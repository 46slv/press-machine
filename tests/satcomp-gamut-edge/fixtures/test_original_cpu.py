"""Offline CPU qualification of the included pinned DCTL, not a Python transform."""
import ctypes as C
import hashlib
import itertools
import math
import os
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / 'PressMachine_Comp_Color_Normalized_TEST.dctl'
PIN = 'db784f2fd24c7e34df9a33f56e1f93ba202df3fccbd924c17a0c92f5b092bb75'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == PIN, 'Pinned source changed'
if sys.platform == 'win32':
    os.add_dll_directory(r'C:\msys64\mingw64\bin')
lib = C.CDLL(str(ROOT / 'cpu_transform.dll'))
lib.cpu_transform.argtypes = [C.POINTER(C.c_float), C.POINTER(C.c_float), C.POINTER(C.c_int), C.POINTER(C.c_float)]

UI = [
    ('pm_threshold', 'Threshold', 'DCTLUI_SLIDER_FLOAT', 25., 0., 100., .1),
    ('pm_compression', 'Amount %', 'DCTLUI_SLIDER_FLOAT', 0., 0., 100., .1),
    ('pm_softness', 'Knee %', 'DCTLUI_SLIDER_FLOAT', 20., 0., 100., .1),
    ('pm_comp_bypass', 'Comp Bypass', 'DCTLUI_CHECK_BOX', 0),
    ('pmi_ig', 'Input Primaries', 'DCTLUI_COMBO_BOX', 0, ['PMA_DWG_IN', 'PMA_AWG3_IN', 'PMA_AWG4_IN', 'PMA_AP1_IN'], ['DWG D65', 'ARRI Wide Gamut 3 D65', 'ARRI Wide Gamut 4 D65', 'ACES AP1 CAT02']),
    ('pmi_it', 'Input Transfer', 'DCTLUI_COMBO_BOX', 0, ['PMA_DI_IN', 'PMA_LOGC3_IN', 'PMA_LOGC4_IN', 'PMA_ACESCCT_IN', 'PMA_LINEAR_IN'], ['DaVinci Intermediate', 'LogC3 EI800 Exposure', 'LogC4 Scene', 'ACEScct Reversible', 'Relative Linear']),
    ('pmi_og', 'Output Primaries', 'DCTLUI_COMBO_BOX', 0, ['PMA_SAME_GAMUT_OUT', 'PMA_DWG_OUT', 'PMA_AWG3_OUT', 'PMA_AWG4_OUT', 'PMA_AP1_OUT'], ['Same as Input', 'DWG D65', 'ARRI Wide Gamut 3 D65', 'ARRI Wide Gamut 4 D65', 'ACES AP1 CAT02']),
    ('pmi_ot', 'Output Transfer', 'DCTLUI_COMBO_BOX', 0, ['PMA_SAME_TRANSFER_OUT', 'PMA_DI_OUT', 'PMA_LOGC3_OUT', 'PMA_LOGC4_OUT', 'PMA_ACESCCT_OUT', 'PMA_LINEAR_OUT'], ['Same as Input', 'DaVinci Intermediate', 'LogC3 EI800 Exposure', 'LogC4 Scene', 'ACEScct Reversible', 'Relative Linear']),
]

def bits(x): return struct.pack('<f', x)
def same(a,b): return all(bits(x)==bits(y) or (math.isnan(x) and math.isnan(y)) for x,y in zip(a,b))
def delta(a,b): return max(abs(x-y) for x,y in zip(a,b))
def run(rgb, threshold=25, amount=0, knee=20, bypass=0, ig=0, it=0, og=0, ot=0):
    inp=(C.c_float*3)(*rgb); sliders=(C.c_float*3)(threshold,amount,knee)
    controls=(C.c_int*5)(bypass,ig,it,og,ot); out=(C.c_float*3)()
    lib.cpu_transform(inp,sliders,controls,out)
    return tuple(out)

counts = {'pass': 0, 'fail': 0}
failures=[]
def check(label, condition, detail=''):
    key='pass' if condition else 'fail'; counts[key]+=1
    if not condition: failures.append((label,detail))

text=SOURCE.read_text(encoding='utf-8')
lines=re.findall(r'^DEFINE_UI_PARAMS\((.*)\)$',text,re.M)
check('UI count',len(lines)==8,str(len(lines)))
for spec,line in zip(UI,lines):
    parts=[p.strip() for p in line.split(',',4)]
    check('UI '+spec[0],parts[:4]==[spec[0],spec[1],spec[2],str(spec[3]) if isinstance(spec[3],int) else f'{spec[3]:.1f}'],str(parts[:4]))
    if spec[2]=='DCTLUI_SLIDER_FLOAT':
        check('range/step '+spec[0],parts[4]==f'{spec[4]:.1f}, {spec[5]:.1f}, {spec[6]:.1f}',parts[4])
    if spec[2]=='DCTLUI_COMBO_BOX':
        groups=re.findall(r'\{([^}]*)\}',line)
        actual=[s.strip() for s in groups[0].split(',')] if groups else []
        labels=[s.strip() for s in groups[1].split(',')] if len(groups)==2 else []
        check('options '+spec[0],actual==spec[4],str(actual))
        check('option labels '+spec[0],labels==spec[5],str(labels))

chromatic=(.68,.31,.12)
neutral=[(0.,0.,0.),(.18,.18,.18),(-.2,-.2,-.2),(2.,2.,2.)]
for rgb in neutral:
    for it in range(5):
        for ig in range(4):
            out=run(rgb,amount=100,ig=ig,it=it)
            check('neutral same-profile exact',same(out,rgb),f'{rgb} {ig} {it}: {out}')

# All input 4x5 profiles, all output 5x6 selectors. Every explicit selector
# is checked against the equivalent resolved selector, including conversion.
profile_pairs=0; same_max=0.; conversion_count=0
for ig,it,og,ot in itertools.product(range(4),range(5),range(5),range(6)):
    args=dict(ig=ig,it=it,og=og,ot=ot,bypass=1,amount=100)
    out=run(chromatic,**args)
    explicit=run(chromatic,ig=ig,it=it,og=(ig+1 if og==0 else og),ot=(it+1 if ot==0 else ot),bypass=1,amount=100)
    profile_pairs+=1
    check('same-as-input selector',same(out,explicit),f'{args}: {out} vs {explicit}')
    if og in (0,ig+1) and ot in (0,it+1):
        same_max=max(same_max,delta(out,chromatic))
        check('matching profile bypass identity',same(out,chromatic),f'{args}: {out}')
    if og not in (0,ig+1) or ot not in (0,it+1):
        conversion_count+=not same(out,chromatic)
    check('profile output finite',all(map(math.isfinite,out)),f'{args}: {out}')

# Bypass is Comp-only: same profile exact, different profile still converts.
for rgb in [chromatic,(-.12,.33,1.5),(1.4,.25,.04),(4.,1.,.2)]:
    for ig,it in itertools.product(range(4),range(5)):
        off=run(rgb,ig=ig,it=it,bypass=1,amount=100,threshold=0,knee=100)
        zero=run(rgb,ig=ig,it=it,amount=0)
        check('bypass isolation same',same(off,zero) and same(off,rgb),f'{rgb} {ig} {it}: {off} {zero}')
        converted=run(rgb,ig=ig,it=it,og=2 if ig!=1 else 3,ot=5,bypass=1,amount=100)
        converted_zero=run(rgb,ig=ig,it=it,og=2 if ig!=1 else 3,ot=5,amount=0)
        check('bypass leaves conversion',same(converted,converted_zero),f'{rgb} {ig} {it}: {converted} {converted_zero}')

base=run(chromatic)
check('default Amount zero',same(base,chromatic),str(base))
active=run(chromatic,amount=100,threshold=0)
check('Amount active',not same(active,chromatic),str(active))
check('Amount zero regardless other controls',same(run(chromatic,amount=0,threshold=0,knee=100),chromatic))
check('Threshold 100 no-op',same(run(chromatic,amount=100,threshold=100,knee=100),chromatic))
check('Bypass active no-op',same(run(chromatic,amount=100,threshold=0,bypass=1),chromatic))
thresholds=[run(chromatic,amount=100,threshold=t,knee=20) for t in (0,25,50,75,100)]
check('Threshold response',len(set(map(str,thresholds)))>=3,str(thresholds))
knees=[run(chromatic,amount=100,threshold=25,knee=k) for k in (0,20,50,100)]
check('Knee response',len(set(map(str,knees)))>=2,str(knees))
amounts=[run(chromatic,amount=a,threshold=0) for a in (0,25,50,75,100)]
check('Amount response',len(set(map(str,amounts)))==5,str(amounts))

for rgb in [(float('nan'),.2,.4),(float('inf'),.2,.4),(-float('inf'),.2,.4)]:
    for it in range(5):
        check('nonfinite untouched',same(run(rgb,amount=100,it=it,og=2,ot=5),rgb),f'{rgb} {it}')
for kwargs in [dict(ig=-1),dict(ig=4),dict(it=-1),dict(it=5),dict(og=-1),dict(og=5),dict(ot=-1),dict(ot=6)]:
    check('invalid profile untouched',same(run(chromatic,amount=100,**kwargs),chromatic),str(kwargs))
for bad in [(-1,25,20),(101,25,20),(25,-1,20),(25,101,20),(25,50,-1),(25,50,101)]:
    result=run(chromatic,threshold=bad[0],amount=bad[1],knee=bad[2])
    check('invalid control untouched',same(result,chromatic),f'{bad}: {result}')
for rgb,it in [((2.,.3,.1),3),((1e10,.2,.3),3),((1e30,.2,.3),0),((1e30,.2,.3),2)]:
    result=run(rgb,it=it,amount=100,og=2,ot=5)
    check('invalid encoded/domain untouched',same(result,rgb),f'{rgb} it={it}: {result}')

# Measured numeric identity and roundtrip, not an assumed tolerance.
roundtrip=[]; roundtrip_cases=[]; ordinary_roundtrip=[]; negatives=[]; hdr=[]
for rgb in [(-.3,.2,1.3),(-2.,.1,4.),(.18,.32,.1),(1.5,.8,.2),(4.,1.,.2)]:
    for ig,it in itertools.product(range(4),range(5)):
        to=run(rgb,ig=ig,it=it,og=1,ot=5,bypass=1)
        back=run(to,ig=0,it=4,og=ig+1,ot=it+1,bypass=1)
        if all(map(math.isfinite,back)):
            roundtrip.append(delta(rgb,back))
            roundtrip_cases.append((delta(rgb,back), rgb, ig, it, to, back))
            if rgb == (.18,.32,.1): ordinary_roundtrip.append(delta(rgb,back))
        processed=run(rgb,ig=ig,it=it,amount=100,threshold=0)
        check('processed finite or input preserved',all(map(math.isfinite,processed)),f'{rgb} {ig} {it}: {processed}')
        (negatives if min(rgb)<0 else hdr).append(delta(rgb,processed))

print('source_sha256',hashlib.sha256(SOURCE.read_bytes()).hexdigest())
print('compiled transform profile_cases',profile_pairs,'converted_nonidentity',conversion_count,'of',profile_pairs-80)
print('bypass identity max_abs',same_max)
print('roundtrip finite',len(roundtrip),'max_abs',max(roundtrip),'median_abs',sorted(roundtrip)[len(roundtrip)//2])
print('roundtrip worst',max(roundtrip_cases))
print('roundtrip ordinary finite',len(ordinary_roundtrip),'max_abs',max(ordinary_roundtrip),'median_abs',sorted(ordinary_roundtrip)[len(ordinary_roundtrip)//2])
print('creative signed max_abs',max(negatives),'nonzero',sum(x>0 for x in negatives),'of',len(negatives))
print('creative HDR max_abs',max(hdr),'nonzero',sum(x>0 for x in hdr),'of',len(hdr))
print('control response threshold',thresholds,'knee',knees,'amount',amounts)
print('PASS',counts['pass'],'FAIL',counts['fail'])
for name,detail in failures[:30]: print('FAILURE',name,detail)
sys.exit(bool(failures))
