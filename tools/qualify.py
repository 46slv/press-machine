"""Measure first, then check a reviewed frozen parity budget. No host claims."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o
from tools import vectors
from tools.build_native import EXE, ROOT, build

def native(requests):
    lines=[]
    for op,rgb,params in requests:
        t,c,p,b=params
        lines.append(' '.join(map(str,(op,*(o.bits(x) for x in rgb),o.bits(t),o.bits(c),o.bits(p),int(b)))))
    run=subprocess.run([str(EXE)],input='\n'.join(lines)+'\n',capture_output=True,text=True,check=True)
    rows=[tuple(map(int,line.split())) for line in run.stdout.splitlines()]
    if len(rows)!=len(requests): raise AssertionError('native result count mismatch')
    return rows

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def measure():
    scalar=list(vectors.scalar_cases())
    scalar_out=native([('S',(s,0.,0.),(t,c,p,False)) for s,t,c,p in scalar])
    worst_s={'error':0.,'case':None}; worst_s_normal=0.; s_identity=0
    previous={}; mono=[]; boost=[]
    for case,words in zip(scalar,scalar_out):
        s,t,c,p=case; y=o.from_bits(words[0]); expected=o.transfer(*case)
        error=abs(y-expected)
        if error>worst_s['error']: worst_s={'error':error,'case':case,'expected':expected,'actual':y}
        worst_s_normal=max(worst_s_normal,error/max(1.,abs(expected)))
        if c==0 or s<=t*(1-p/100):
            # Mathematical boundary and float arithmetic may differ by a float
            # neighbor. These controls/boundaries are exactly representable here.
            if words[0]!=o.bits(s): raise AssertionError(('scalar identity',case,y))
            s_identity+=1
        key=(t,c,p)
        if y<0 or y>s: boost.append((case,y))
        if key in previous and y<previous[key]: mono.append((case,previous[key],y))
        previous[key]=y
    if boost or mono: raise AssertionError({'native_boost':boost[:3],'native_monotone':mono[:3]})

    pixels=list(vectors.pixels()); stress=list(vectors.finite_stress())
    all_rows=pixels+stress
    out=native([('P',v['rgb'],v['params']) for v in all_rows])
    worst={'error':0.,'id':None}; normalized=0.; compressed=identity=0; failures=[]; boundary=[]
    for v,words in zip(all_rows,out):
        actual=tuple(o.from_bits(w) for w in words)
        if not all(math.isfinite(x) for x in actual): raise AssertionError(('nonfinite_output',v,actual))
        if v['group']=='finite_only': continue
        expected=o.apply(v['rgb'],*v['params'])
        error=max(abs(a-b) for a,b in zip(actual,expected.rgb))
        normal=error/max(1.,*map(abs,expected.rgb))
        normalized=max(normalized,normal)
        if error>worst['error']:
            worst={'error':error,'id':v['id'],'path':expected.path,'expected':expected.rgb,'actual':actual}
        if expected.path=='compressed': compressed+=1
        else:
            if tuple(words)!=tuple(map(o.bits,v['rgb'])):
                measured=native([('M',v['rgb'],v['params'])])[0]
                lab=tuple(o.from_bits(w) for w in measured)
                # Native rounded Lab and double oracle can fall on opposite
                # sides of an epsilon. Pin the guard itself with direct tests;
                # retain these differences in parity maxima and the report.
                native_c=o.f32(math.sqrt(o.f32(o.f32(lab[1]*lab[1])+o.f32(lab[2]*lab[2]))))
                ref_lab=o.encoded_lab(v['rgb']); ref_c=math.hypot(*ref_lab[1:])
                if (expected.path=='domain_identity' and v['id'].startswith('C_guard_') and
                    ref_c<=1e-7 and native_c>o.f32(1e-7)):
                    boundary.append({'id':v['id'],'oracle_c':ref_c,'native_c':native_c,'rgb_error':error})
                else: failures.append({'id':v['id'],'path':expected.path,'error':error})
            else: identity+=1
    if failures: raise AssertionError({'pixel_identity_failures':failures})

    # Direct guard tests pin equality to the actual float32 constants. Adjacent
    # encoded RGB cannot reliably manufacture an exact Lab boundary in float32.
    domains=list(vectors.domain_cases())+[(1e6,1e-4,0.),(float('inf'),.2,0.),(float('nan'),.2,0.)]
    d_out=native([('D',lab,(25.,75.,20.,False)) for lab in domains])
    for lab,word in zip(domains,d_out):
        l,c,_=lab
        expected=int(all(math.isfinite(x) for x in lab) and l>o.f32(1e-6) and c>o.f32(1e-7) and 100*c/l>o.f32(1e-7))
        if o.from_bits(word[0])!=expected: raise AssertionError(('domain',lab,word,expected))
    eps=o.bits(1e-7)
    s_guards=[o.from_bits(eps-1),o.from_bits(eps),o.from_bits(eps+1),float('inf'),float('nan')]
    g_out=native([('G',(.5,.2,0.),(s,75.,20.,False)) for s in s_guards])
    for words,expected in zip(g_out,(0,0,1,0,0)):
        if o.from_bits(words[0])!=expected: raise AssertionError(('direct_s_guard',words,expected))

    # Native DI mappings and signed cube-root anchors complement pixel parity.
    anchors=[-.01,0.,.00262409,.18,1.,10.,40.,100.]
    conversions=native([('E',(o.f32(x),o.f32(o.encode(x)),o.f32(-abs(x))),(25.,75.,20.,False)) for x in anchors])
    conversion_max=0.
    for x,words in zip(anchors,conversions):
        expected=(o.encode(o.f32(x)),o.decode(o.f32(o.encode(x))),math.cbrt(o.f32(-abs(x))))
        actual=tuple(o.from_bits(w) for w in words)
        if not all(math.isfinite(x) for x in actual): raise AssertionError(('conversion',x,actual))
        conversion_max=max(conversion_max,*(abs(a-b)/max(1.,abs(b)) for a,b in zip(actual,expected)))

    # Bypass must copy even non-finite inputs without touching payload/sign bits.
    special=[(o.from_bits(0x7fc12345),-.0,float('inf')),(float('-inf'),1.,-0.)]
    special_out=native([('P',v,(25.,75.,20.,True)) for v in special])
    for v,words in zip(special,special_out):
        if tuple(words)!=tuple(map(o.bits,v)): raise AssertionError('bypass payload changed')

    return {'stage':'NATIVE_MEASURED', 'platform':platform.platform(),'python':platform.python_version(),
            'dctl_sha256':sha(ROOT/'dctl/PressMachine_R2.dctl'),
            'vectors_sha256':sha(ROOT/'fixtures/vectors.jsonl'),
            'counts':{'scalar':len(scalar),'scalar_exact_identity':s_identity,'pixels':len(pixels),
                      'pixel_compressed':compressed,'pixel_exact_identity':identity,'finite_stress':len(stress),
                      'direct_domain':len(domains)+len(s_guards),'conversion_anchors':len(anchors),'bypass_nonfinite':len(special)},
            'scalar_worst':worst_s,'scalar_max_normalized_error':worst_s_normal,
            'rgb_worst':worst,'rgb_max_normalized_error':normalized,
            'conversion_max_normalized_error':conversion_max,
            'identity_failures':0,'guard_boundary_crossings':boundary,
            'native_scalar_boosts':0,'native_scalar_decreases':0,'new_nonfinite_outputs':0,
            'host':'NOT_RUN','visual':'NOT_RUN','alpha_host':'NOT_RUN','performance_4k':'NOT_RUN'}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true')
    parser.add_argument('--skip-build',action='store_true'); args=parser.parse_args()
    compiler=build() if not args.skip_build else {'compiler_output':(ROOT/'build/compiler.txt').read_text(encoding='utf-8')}
    vectors.write()
    report=measure(); report['compiler']=compiler
    if args.check:
        budget=json.loads((ROOT/'evidence/parity_budget.json').read_text())
        for key,limit in budget['limits'].items():
            if report[key]>limit: raise AssertionError((key,report[key],limit))
        if [x['id'] for x in report['guard_boundary_crossings']] != budget['guard_boundary_ids']:
            raise AssertionError('guard-boundary classifications changed; inspect before refreezing')
        report['stage']='PREBUILD_PARITY_PASS'; report['budget_sha256']=sha(ROOT/'evidence/parity_budget.json')
    path=ROOT/'evidence'/('prebuild.json' if args.check else 'measurement.json')
    path.parent.mkdir(exist_ok=True); path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k!='compiler'},indent=2))

if __name__=='__main__': main()
