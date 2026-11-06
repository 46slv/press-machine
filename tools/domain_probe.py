"""Offline-only diagnosis and isolated continuous-domain comparison. No host use."""
import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o
from reference import continuous_oracle as co
from tools import qualify, vectors
from tools.build_native import ROOT, EXE, build

DOMAIN_EXE=ROOT/'build'/('domain_native.exe' if sys.platform=='win32' else 'domain_native')


def native(requests, executable=DOMAIN_EXE):
    lines=[' '.join(map(str,(op,*(o.bits(x) for x in rgb),o.bits(t),o.bits(c),o.bits(p),int(b))))
           for op,rgb,(t,c,p,b) in requests]
    run=subprocess.run([str(executable)],input='\n'.join(lines)+'\n',capture_output=True,text=True,check=True)
    rows=[tuple(map(int,line.split())) for line in run.stdout.splitlines()]
    if len(rows)!=len(requests): raise AssertionError('native result count mismatch')
    return [tuple(map(o.from_bits,row)) for row in rows]


def build_both():
    return {'r2':build(),'continuous':build('tests/domain_harness.cpp',DOMAIN_EXE)}


def direct_scale_cases():
    rng=random.Random(120220261107)
    for i in range(12000):
        l=o.f32(rng.uniform(-2,2)); c=o.f32(10**rng.uniform(-6,1))
        t,comp,p=(o.f32(rng.randrange(n)/10) for n in (2001,1001,1001))
        yield l,c,t,comp,p
    for l,c,t,comp,p in itertools.product((-.1,-1e-6,0.,1e-6,.1),(.001,.8,10.),(0.,25.,200.),(0.,50.,75.,100.),(0.,20.,100.)):
        yield tuple(map(o.f32,(l,c,t,comp,p)))


def direct_report():
    cases=list(direct_scale_cases())
    actual=native([('Q',(l,c,0.),(t,comp,p,False)) for l,c,t,comp,p in cases])
    worst=0.; failures=0
    for case,rgb in zip(cases,actual):
        l,c,t,comp,p=case; scale=rgb[0]; expected=co.chroma_out(l,c,t,comp,p)/c
        worst=max(worst,abs(scale-expected))
        failures+=int(not math.isfinite(scale) or not 0<=scale<=1)
    return {'cases':len(cases),'scale_max_absolute_error':worst,'nonfinite_negative_or_boost':failures}


def blue_ramps():
    report=[]
    for peak,comp in itertools.product((.01,.1,1.,4.),(50.,75.,100.)):
        linear=[(peak*.18*(1-i/1023),peak*.18*(1-i/1023),peak*(.18*(1-i/1023)+i/1023)) for i in range(1024)]
        encoded=[tuple(map(o.f32,map(o.encode,rgb))) for rgb in linear]
        requests=[('P',rgb,(25.,comp,20.,False)) for rgb in encoded]
        before=[tuple(map(o.decode,rgb)) for rgb in native(requests,EXE)]
        after=[tuple(map(o.decode,rgb)) for rgb in native(requests)]
        expected=[co.apply(rgb,25.,comp,20.).rgb for rgb in encoded]
        def adjacent(rows):
            pairs=[max(abs(a-b) for a,b in zip(rows[i],rows[i+1])) for i in range(1023)]
            i=max(range(1023),key=pairs.__getitem__)
            return {'max_channel_delta':pairs[i],'left_offset':i,'left_rgb':rows[i],'right_rgb':rows[i+1]}
        parity=max(max(abs(a-b) for a,b in zip(actual,ref)) for actual,ref in zip(native(requests),expected))
        report.append({'peak':peak,'compression':comp,'r2':adjacent(before),'proposal':adjacent(after),
                       'proposal_max_encoded_oracle_error':parity,
                       'recorded_host_pair_offsets':[689,690],
                       'recorded_host_pair_L':[o.linear_lab(linear[i])[0] for i in (689,690)],
                       'proposal_pair_blue_delta':after[690][2]-after[689][2]})
    return report


def measure():
    original=qualify.measure()
    budget=json.loads((ROOT/'evidence/parity_budget.json').read_text())
    for key,limit in budget['limits'].items():
        if original[key]>limit: raise AssertionError((key,original[key],limit))
    pixels=list(vectors.pixels())
    requests=[('P',v['rgb'],v['params']) for v in pixels]
    old=native(requests,EXE);new=native(requests)
    positive=0; positive_error=0.; guarded_changed=0; worst_oracle=0.; exact=0
    for v,a,b in zip(pixels,old,new):
        try: lab=o.encoded_lab(v['rgb'])
        except (ValueError,OverflowError): lab=(float('nan'),0.,0.)
        if lab[0]>1e-6:
            positive+=1;positive_error=max(positive_error,max(abs(x-y) for x,y in zip(a,b)))
        elif a!=b:guarded_changed+=1
        ref=co.apply(v['rgb'],*v['params'])
        worst_oracle=max(worst_oracle,max(abs(x-y) for x,y in zip(b,ref.rgb))/max(1.,*map(abs,ref.rgb)))
        if ref.path not in ('compressed',) and tuple(map(o.bits,b))==tuple(map(o.bits,v['rgb'])):exact+=1
    stress=list(vectors.finite_stress())
    outputs=native([('P',v['rgb'],v['params']) for v in stress])
    finite_fail=sum(not all(math.isfinite(x) for x in rgb) for rgb in outputs)
    result={'status':'ISOLATED_PROPOSAL_NOT_PRODUCT_ACCEPTANCE',
            'base_commit':'37e0c2ed447e1218dae94ccd6ac7c4aef28eab72',
            'source_hashes':{str(p.relative_to(ROOT)):qualify.sha(p) for p in
                             (ROOT/'dctl/PressMachine_R2.dctl',ROOT/'prototypes/PressMachine_ContinuousDomain.dctl',ROOT/'reference/continuous_oracle.py')},
            'original_r2_frozen_budget':'PASS','proposal_pixel_vectors':len(pixels),
            'positive_L_vectors':positive,'positive_L_max_encoded_difference_from_r2':positive_error,
            'guarded_vectors_intentionally_changed':guarded_changed,
            'proposal_max_normalized_oracle_error':worst_oracle,'proposal_exact_identity_vectors':exact,
            'finite_stress_cases':len(stress),'finite_stress_failures':finite_fail,
            'direct_chroma_scale':direct_report(),'blue_ramps':blue_ramps(),
            'resolve_gpu':'NOT_RUN','performance_4k':'NOT_RUN','user_visual_acceptance':'NOT_RUN'}
    if finite_fail or result['direct_chroma_scale']['nonfinite_negative_or_boost']:
        raise AssertionError(result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();metadata=build_both();result=measure();result['compiler']=metadata
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('compiler','blue_ramps')},indent=2))
    for row in result['blue_ramps']:
        print('blue',row['peak'],row['compression'],row['r2']['max_channel_delta'],row['proposal']['max_channel_delta'])

if __name__=='__main__':main()
