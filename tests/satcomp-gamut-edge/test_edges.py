"""Isolated blurred ramps. Run the actual standalone transform, not a spatial model of it."""
import csv
from itertools import product
from math import erf,sqrt,isfinite
from functools import lru_cache
from harness import OUT,load,inp32,maxerr,same
from reference import D,decode,encode,BASES

base=load('baseline'); cand=load('candidate')
counts=[0,0]
def check(label,v):
    counts[not v]+=1
    if not v: print('FAIL',label)

def blend(dark,fg,a): return tuple(b+(f-b)*a for b,f in zip(dark,fg))
def rec(a,fn): return tuple(fn(v) for v in a)
def y(a,ig): return sum(float(w)*v for w,v in zip(BASES[ig][1],a))
def peak_diff(seq): return max((maxerr(a,b) for a,b in zip(seq,seq[1:])),default=0)
def curv(seq): return max((max(abs(x-2*y+z) for x,y,z in zip(a,b,c)) for a,b,c in zip(seq,seq[1:],seq[2:])),default=0)

@lru_cache(None)
def code(rgb,t): return inp32(rec(rgb,lambda v:encode(D(v),t)))
def to_lin(rgb,t): return rec(rgb,lambda v:float(decode(v,t)))

def alpha(x,center,sigma):
    z=(x-center)/(sigma*sqrt(2))
    return 0. if z< -5 else 1. if z>5 else .5*(1+erf(z))

blurs={
    'neutral':((.002,)*3,(.8,)*3),
    'chromatic_nearly_neutral':((.005,.0057,.0053),(.36,.41,.34)),
    'saturated_to_desaturated':((.19,.18,.17),(1.2,.031,.012)),
    'saturated_blue_to_black':((0.,0.,0.),(.014,.023,2.4)),
    'warm_to_dark_color':((.0006,.003,.007),(1.4,.055,.021)),
    'signed_to_dark_color':((-.005,.002,.003),(1.2,-.09,.24)),
}
controls=[('bypass',100,1),('amount0',0,0),('amount25',25,0),('amount50',50,0),('amount100',100,0)]
profile=[('DWG-linear',0,4,None,None),('AP1-logc4',3,2,None,None),('AP1-logc4-to-linear',3,2,3,4)]
n=129
print('Blur fixtures: Gaussian-CDF stationary 2 frames and translation 8 frames with 0.375px/frame; sigma=2.8 px. Same-profile, plus explicit output transfer.')
with (OUT/'edge-metrics.csv').open('w',newline='',encoding='utf8') as fh:
    writer=csv.writer(fh)
    writer.writerow('profile fixture motion control delta_from_bypass max_candidate_minus_base max_spatial_first max_spatial_second max_temporal_first max_temporal_second max_linear_y_overshoot'.split())
    for (name,(bg,fg)),(pr,ig,it,og,ot) in product(blurs.items(),profile):
        reference_a={}; still_frames={}
        for motion,frames in [('stationary',2),('moving',8)]:
            for tag,amount,bypass in controls:
                observed=[]; diffs=[]; edits=[]; luma=[]
                for k in range(frames):
                    center=64.+(.375*k if motion=='moving' else 0.)
                    row=[]
                    for x in range(n):
                        a=alpha(x,center,2.8)
                        rgb=code(blend(bg,fg,a),it)
                        opts=dict(ig=ig,it=it,og=og,ot=ot,threshold=25,knee=20,amount=amount,bypass=bypass)
                        p=cand(rgb,xy=(n,32,x,15),**opts)
                        b=base(rgb,xy=(n,32,x,15),**opts)
                        row.append(p); diffs.append(maxerr(p,b))
                        if x in (0,59,64,67,128) and k in (0,frames-1):
                            q=cand(rgb,xy=(1920,1080,881,634),**opts)
                            check('same source RGB is independent of coordinates/dimensions',same(p,q))
                        if tag=='bypass': reference_a[motion,k,x]=p
                        else: edits.append(maxerr(p,reference_a[motion,k,x]))
                        if ot is None and tag in ('bypass','amount0'):
                            check('same-profile bypass/amount0 exact',same(p,rgb))
                        if tag=='amount0': check('bypass equals amount0 on same gradient',same(p,reference_a[motion,k,x]))
                        if name=='neutral' and ot is None: check('neutral remains exact across controls',same(p,rgb))
                    observed.append(row)
                    check('flat tails remain flat',same(row[0],row[15]) and same(row[-1],row[-16]))
                    xy=[y(to_lin(p,it if ot is None else ot),ig if og is None else og) for p in row]
                    lo=min(xy[0],xy[-1]); hi=max(xy[0],xy[-1]); luma.extend(max(0,v-hi,lo-v) for v in xy)
                diff=max(diffs); edit=max(edits,default=0.)
                check('ordinary blur candidate unchanged within 2e-6',diff<=2e-6 and isfinite(edit))
                if motion=='stationary':
                    check('stationary frames bit-identical',all(same(a,b) for a,b in zip(*observed)))
                    still_frames[tag]=observed[0]
                else: check('motion frame zero matches stationary',all(same(a,b) for a,b in zip(observed[0],still_frames[tag])))
                writer.writerow((pr,name,motion,tag,edit,diff,max(map(peak_diff,observed)),max(map(curv,observed)),max(map(peak_diff,zip(*observed))),max(map(curv,zip(*observed))),max(luma)))
                if motion=='moving' and tag in ('bypass','amount100'):
                    print(pr,name,tag,'edit %.6g | candidate-base %.3g | spatial curvature %.6g | temporal curvature %.6g | Y overshoot %.6g' % (edit,diff,max(map(curv,observed)),max(map(curv,zip(*observed))),max(luma)))

# True alpha omitted in the RGB ABI. Simulate two node orderings and a known
# bad encoded-space composite; all pixel data passed to the same DCTL entry.
fg=(1.4,.045,.021); blacks=[('black',(0.,)*3),('colored-dark',(.004,.012,.03))]
for name,bg in blacks:
    for t in (4,2):
        for tag,amount,bypass in controls:
            opts=dict(ig=0,it=t,threshold=0,knee=20,amount=amount,bypass=bypass)
            pf=to_lin(cand(code(fg,t),**opts),t)
            pb=to_lin(cand(code(bg,t),**opts),t)
            comm=[]; wrong=[]; upstream=[]
            for i in range(129):
                a=alpha(i,64,3)
                good=code(blend(bg,fg,a),t)
                # Blend already log-encoded RGB vs blend in linear and then encode.
                bad=inp32(blend(code(bg,t),code(fg,t),a))
                after=to_lin(cand(good,**opts),t)
                before=blend(pb,pf,a)
                comm.append(maxerr(after,before))
                wrong.append(maxerr(after,to_lin(cand(bad,**opts),t)))
                upstream.append(maxerr(to_lin(good,t),to_lin(bad,t)))
            if bypass or not amount:
                check('bypassed alpha commutator is just float quantization',max(comm)<2e-6)
                check('bypass cannot repair upstream encoded blending',abs(max(wrong)-max(upstream))<1e-10)
            print('alpha',name,'transfer',t,tag,'process/compose commutator %.7g | encoded-vs-linear after Comp %.7g | upstream alone %.7g' % (max(comm),max(wrong),max(upstream)))

# A numeric bright-edge discontinuity *was* reproduced: an invalid intermediate
# switched the whole RGB tuple to input Linear mid ramp. Test same candidate as above.
for curve,level in [(2,4e35),(1,1.5e38)]:
    band=[inp32(blend((-.03,.01,.001),(level,.12,.3),alpha(x,64.,12))) for x in range(n)]
    known=[code(v,curve) for v in band]
    before=[base(v,it=4,ot=curve,bypass=1) for v in band]
    after=[cand(v,it=4,ot=curve,bypass=1) for v in band]
    delta_before=max(maxerr(a,b) for a,b in zip(before,known))
    delta_after=max(maxerr(a,b) for a,b in zip(after,known))
    check('HDR fixture reproduces baseline output-domain switch',delta_before>1e32)
    check('HDR blur remains in requested log profile',delta_after<3e-6 and peak_diff(after)<2)
    print('numeric HDR edge transfer',curve,'max ref error before/after',delta_before,delta_after,'max neighbor difference before/after',peak_diff(before),peak_diff(after))

print('EDGE PASS',counts[0],'FAIL',counts[1]); raise SystemExit(bool(counts[1]))
