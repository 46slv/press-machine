"""Focused RED/GREEN gates using the compiled standalone transform and independent oracle."""
from itertools import product
import math
import re
import struct
from statistics import median
import sys
from harness import BASE,CAND,load,f32,inp32,same,maxerr
from reference import D,matrix,mv,decode,encode,convert

lane=sys.argv[1]
run=load(lane)
passed=0; failures=[]
def check(label,cond,detail=''):
    global passed
    if cond: passed+=1
    else: failures.append((label,detail))

def close(a,b,rel=3e-7,absolute=3e-7):
    return all(math.isfinite(x) and abs(x-float(y))<=absolute+rel*abs(float(y)) for x,y in zip(a,b))

text=BASE.read_text()
subject=BASE if lane=='baseline' else CAND
check('all eight exact UI lines',re.findall(r'^DEFINE_UI_PARAMS.*',subject.read_text(),re.M)==re.findall(r'^DEFINE_UI_PARAMS.*',text,re.M) and len(re.findall(r'^DEFINE_UI_PARAMS.*',text,re.M))==8)

# Separate mathematical, binary32-interface, and implementation error.
extreme=inp32((-2,.1,4))
lin=tuple(decode(x,2) for x in extreme)
mapped=mv(matrix(3,0),lin)
exact_back=tuple(encode(v,2) for v in mv(matrix(0,3),mapped))
ramp=inp32(mapped)
out=run(extreme,ig=3,it=2,og=0,ot=4,bypass=1)
back=run(out,ig=0,it=4,og=3,ot=2,bypass=1)
back_ideal=inp32(convert(ramp,0,4,3,2))
# Independent Decimal evaluation of the *declared* reverse table isolates
# arithmetic from the slight difference vs the chromaticity-derived table.
rows=text.split('float2 pma_from_dwg_channel',1)[1].split('if(gamut==3){',1)[1].split('    }',1)[0].splitlines()
coeffs=tuple(tuple(D(f32(hi))+D(f32(lo)) for hi,lo in re.findall(r'make_float2\(([-+.0-9e]+)f, ([-+.0-9e]+)f\)',r)) for r in rows if 'dot3' in r)
back_declared=inp32(tuple(encode(x,2) for x in mv(coeffs,tuple(map(D,out)))))
ulp=(2**28,2**29,2**32)
print('AP1 input binary32',extreme,'decoded',tuple(map(float,lin)))
print('ideal no intermediate quantization',tuple(map(float,exact_back)))
print('DWG linear exact',tuple(map(float,mapped)),'rounded',ramp,'compiled',out,'ULP',ulp)
print('ideal reverse rounded DWG',back_ideal,'pinned reverse rounded DWG',back_declared,'compiled',back)
print('inverse channel condition',tuple(float(sum(abs(m*x) for m,x in zip(row,mapped))/abs(lin[i])) for i,row in enumerate(matrix(0,3))))
# Witness distinct source triples collapsing to exactly the same rounded DWG.
collisions=[]
for source in [(-3,.2,4),(-1,.05,4),(0,0,4),(.3,.5,4)]:
    if same(inp32(convert(inp32(source),3,2,0,4)),ramp): collisions.append(source)
print('indistinguishable encoded triples at ideal DWG float32 boundary',collisions)
check('forward matches independent rounded DWG',same(out,ramp))
check('high precision roundtrip recovers input without float32 boundary',same(inp32(exact_back),extreme))
check('actual float32 collision witness',bool(collisions))
check('compiled reverse compares to pinned coefficient oracle',close(back,back_declared,rel=2e-7,absolute=2e-7),back)

# Independent same-gamut cases: direct transfer needs no gamut roundtrip.
for ig,ot,controls in product(range(1,4),(0,4),({'bypass':1,'amount':100},{'amount':0},{'amount':100,'threshold':100})):
    actual=run(extreme,ig=ig,it=2,ot=ot,**controls)
    target=inp32(convert(extreme,ig,2,ig,ot))
    check('same-gamut extreme transfer-only',close(actual,target,rel=1e-6,absolute=5e-8),(ig,ot,controls,actual,target))
    if ot==4:
        inverse=run(actual,ig=ig,it=4,ot=2,**controls)
        check('same-gamut LogC4 via own linear roundtrip',close(inverse,extreme,absolute=2e-7),(ig,controls,inverse))
for it,ot,lim in [(2,4,8.7186901),(1,4,10.0943115)]:
    for frac in (.911,.95,.99,.99999):
        code=inp32((lim*frac,-2,1.3))
        target=inp32(convert(code,3,it,3,ot))
        actual=run(code,ig=3,it=it,ot=ot,bypass=1)
        check('finite decoded range including canceled/signed neighbors',close(actual,target,rel=3e-6,absolute=3e-7),(it,code,actual,target))
for ot in (1,2):
    for top in (1e35,1.6e35,1e36,1e37,8e37,2e38,3.4e38):
        lin32=inp32((top,-.05,2.5))
        target=inp32(convert(lin32,0,4,0,ot))
        actual=run(lin32,ot=ot,bypass=1)
        check('finite encoded range without intermediate overflow',close(actual,target,rel=3e-7,absolute=2e-7),(ot,lin32,actual,target))

# Adjacent binary32 values on either side of the new range-route cutovers and
# the actual decoded representability boundary. Do not round above-cap inputs down.
def neighbors(x,steps=4):
    center=struct.unpack('<I',struct.pack('<f',x))[0]
    return [struct.unpack('<f',struct.pack('<I',j))[0] for j in range(center-steps,center+steps+1)]

largest=f32(3.402823466e38)
for t,limit,enc_cut,dec_cut in [
    (1,encode(D(largest),1),1e37,encode((D(2)**127-D('.052272'))/D('5.555556'),1)),
    (2,encode(D(largest),2),1e35,encode((D(2)**127-64)/D('2231.82630906768837803320561941251596'),2)),
]:
    enc_err=[]; dec_err=[]; valid=[]; invalid=[]
    for x in neighbors(enc_cut)+[largest]:
        actual=run((x,.13,-.06),ot=t,bypass=1)[0]
        wanted=encode(D(x),t)
        enc_err.append(abs(actual-float(wanted)))
        check('adjacent encode route and FLT_MAX',enc_err[-1]<3e-6,(t,x,actual,wanted))
    for x in neighbors(dec_cut)+neighbors(limit):
        rgb=inp32((x,.13,-.06))
        actual=run(rgb,it=t,ot=4,bypass=1)
        wanted=convert(rgb,0,t,0,4)
        if wanted[0]<=D(largest):
            dec_err.append(abs(actual[0]-float(wanted[0]))/float(wanted[0]));valid.append(x)
            check('adjacent decode route/boundary below FLT_MAX',close(actual,wanted,rel=3e-6),(t,x,actual,wanted))
        else:
            invalid.append(x)
            check('adjacent decode exceeds FLT_MAX, not clipped',same(actual,rgb),(t,x,actual,wanted))
    print('limit seam curve',t,'cutover encode/decode',enc_cut,float(dec_cut),'highest viable code sampled',max(valid),'first overflow sample',min(invalid),'encode max abs',max(enc_err),'decode max relative',max(dec_err))

# The nearest ACEScct float32 code to the mathematical ceiling can itself
# decode above 65504. Report/preserve the strict reversible linear cap.
aces=[]
for x in neighbors(encode(D(65504),3),2):
    rgb=inp32((x,.3,.2)); decoded=decode(x,3); actual=run(rgb,it=3,ot=4,bypass=1)
    accepted=decoded<=D(65504)
    check('ACEScct adjacent code uses existing reversible cap',close(actual,convert(rgb,0,3,0,4),rel=3e-6) if accepted else same(actual,rgb),(x,decoded,actual))
    aces.append((x,round(float(decoded),6),accepted))
print('ACEScct encoded/decoded/accepted around cap',aces)

# Supported vs unsupported, using explicit expected legacy behavior (not a CST).
for rgb,ig,it,og,ot in [
    ((8.75,.1,.2),3,2,0,4),((10.1,-2.,.1),0,1,0,4),
    ((2.,.3,.1),3,3,0,4),((65536.,.3,2.),0,4,0,3),
    ((-1e38,.3,.2),0,4,0,2),((float('inf'),.1,.3),0,4,1,2),
    ((3.4e38,-3.4e38,3.4e38),3,4,1,4)]:
    check('legacy unsupported original (not requested output encoding)',same(run(rgb,ig=ig,it=it,og=og,ot=ot,bypass=1),inp32(rgb)),(rgb,it,og,ot,run(rgb,ig=ig,it=it,og=og,ot=ot,bypass=1)))

for rgb in [(.18,.32,.1),(-.07,.001,1.3),(.24,.11,2.0)]:
    errs=[]; bounds=[]
    for ig,it,og,ot in product(range(4),range(5),range(4),range(5)):
        if (ig,it)==(og,ot) or (it==3 and max(rgb)>1.46799): continue
        wanted=convert(inp32(rgb),ig,it,og,ot)
        if ot==3 and max(wanted)>D('1.4679963'): continue
        actual=run(rgb,ig=ig,it=it,og=og,ot=ot,bypass=1)
        errs.append(maxerr(actual,wanted))
        bounds.extend(abs(a-float(b))/max(1,abs(float(b))) for a,b in zip(actual,wanted))
        check('ordinary/signed/HDR independent conversion',close(actual,wanted,rel=4e-6,absolute=2e-6),(rgb,ig,it,og,ot,actual,wanted))
    print('conversion corpus',rgb,'cases',len(errs),'abs max/median',max(errs),median(errs),'max scaled abs',max(bounds))

legacy=load('baseline')
for ig,it,rgb in product(range(4),range(5),[(.76,.23,.19),(-.07,.001,1.3),(.2,.2,.2)]):
    for amount in (0,25,50,100):
        opts=dict(ig=ig,it=it,amount=amount,threshold=25,knee=20)
        check('ordinary same-profile controls bit-identical to baseline',same(run(rgb,**opts),legacy(rgb,**opts)),(ig,it,rgb,amount))
for rgb,ig,it,og,ot in [((.6,.4,.2),2,1,2,4),((.70,.3,.2),3,2,0,0)]:
    without=run(rgb,ig=ig,it=it,og=og,ot=ot,bypass=1)
    bad=run(rgb,ig=ig,it=it,og=og,ot=ot,amount=60,threshold=-1)
    check('invalid Comp controls do not disable a valid profile conversion',same(bad,without) and not same(bad,inp32(rgb)),(rgb,ig,it,og,ot,bad,without))

print('PASS',passed,'FAIL',len(failures))
for label,detail in failures[:45]: print('FAIL',label,detail)
sys.exit(bool(failures))
