"""Bounded scalar requalification, separate from the historical frozen corpus.

Uses the actual DCTL executable and unchanged independent double oracle.
Reports measurements before any envelope decision; adopts no expanded budget.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o
from tools import qualify
from tools.build_native import ROOT, EXE, build

SEED=120220261106


def expanded_states():
    rng=random.Random(SEED)
    states=[tuple(o.f32(rng.randrange(0,n)/10) for n in (2001,1001,1001))
            for _ in range(12000)]
    states.extend(tuple(map(o.f32,state)) for state in
                  itertools.product((0.,.1,.2,199.9,200.),(0.,.1,99.9,100.),(0.,.1,99.9,100.)))
    return states


def points(t,c,p):
    # Match pm_transfer's native float32 boundary operation order. No knee
    # output formula is reproduced here; outputs come only from actual DCTL.
    fraction=o.f32(p/100.)
    lo=o.f32(t*o.f32(1.-fraction))
    hi=o.f32(t*o.f32(1.+fraction))
    words={o.bits(0.),o.bits(500.)}
    for x in (lo,t,hi):
        center=o.bits(x)
        words.update(max(0,center+offset) for offset in range(-5,6))
    return [o.from_bits(word) for word in sorted(words)]


def expanded_cases(states):
    for group,(t,c,p) in enumerate(states):
        for s in points(t,c,p):
            yield group,(s,t,c,p)


def tail_cases():
    groups=itertools.product((0.,.1,.8,1.,25.,134.5,199.9,200.),range(1001),(0.,20.,59.5,100.))
    levels=tuple(map(o.f32,(500.,1000.,1e4,1e7,1e10,1e20,1e30,o.F32_MAX)))
    for group,(t,c,p) in enumerate(groups):
        t,c,p=map(o.f32,(t,c/10.,p))
        for s in levels:
            yield group,(s,t,c,p)


def case_record(case,actual,expected):
    return {'s_t_c_p':case,'input_words':list(map(o.bits,case)),
            'actual':actual,'oracle':expected}


def regression():
    case=tuple(map(o.f32,(500.,.8,99.7,59.5)))
    s,t,c,p=case
    actual=o.from_bits(qualify.native([('S',(s,0.,0.),(t,c,p,False))])[0][0])
    expected=o.transfer(*case)
    # For this positive high-tail case, 100-c is exact by Sterbenz (c~100).
    # q division, s-t, product and final addition each round once: gamma_4.
    # The independent double oracle's cancellation is covered conservatively
    # by 8 double ULPs at S. This bound is case-specific, not a parity budget.
    unit=2.**-24
    gamma4=4*unit/(1-4*unit)
    bound=gamma4*abs(expected)+8*math.ulp(s)
    return {**case_record(case,actual,expected),'absolute_error':abs(actual-expected),
            'case_absolute_bound':bound,'gamma4':gamma4,'double_reference_allowance':8*math.ulp(s),
            'bound_scope':'This positive near-limiter tail point only; no global budget change',
            'historical_native':2.2976105213165283,
            'historical_absolute_error':abs(2.2976105213165283-expected)}


def measure(cases):
    report={'samples':0,'groups':0,'nonfinite':0,'boosts':0,'negatives':0,
            'compression_zero_cases':0,'compression_zero_identity_failures':0,
            'ordered_sample_comparisons':0,'local_decreases':0,'maximum_drop':0.,
            'max_absolute_error':0.,'max_normalized_error':0.,'worst_absolute':None,
            'worst_normalized':None,'worst_drop':None,'decrease_examples':[]}
    digest=hashlib.sha256(); previous=None; previous_group=None
    iterator=iter(cases)
    while chunk:=list(itertools.islice(iterator,4096)):
        requests=[('S',(s,0.,0.),(t,c,p,False)) for _,(s,t,c,p) in chunk]
        outputs=qualify.native(requests)
        for (group,case),words in zip(chunk,outputs):
            s,t,c,p=case; y=o.from_bits(words[0]); expected=o.transfer(*case)
            report['samples']+=1
            digest.update(struct.pack('<5I',group,*map(o.bits,case)))
            if group!=previous_group:
                previous=None; report['groups']+=1
            if c==0:
                report['compression_zero_cases']+=1
                report['compression_zero_identity_failures']+=int(words[0]!=o.bits(s))
            if not math.isfinite(y):
                report['nonfinite']+=1
            else:
                report['boosts']+=int(y>s); report['negatives']+=int(y<0)
                error=abs(y-expected); normalized=error/max(1.,abs(expected))
                item=case_record(case,y,expected)
                if error>report['max_absolute_error']:
                    report['max_absolute_error']=error; report['worst_absolute']=item
                if normalized>report['max_normalized_error']:
                    report['max_normalized_error']=normalized; report['worst_normalized']=item
                if previous is not None:
                    report['ordered_sample_comparisons']+=1
                    if y<previous['actual']:
                        report['local_decreases']+=1
                        drop=previous['actual']-y
                        event={'previous':previous,'current':item,'drop':drop,
                               'input_ulp_distance':o.bits(s)-previous['input_words'][0]}
                        if len(report['decrease_examples'])<5: report['decrease_examples'].append(event)
                        if drop>report['maximum_drop']:
                            report['maximum_drop']=drop; report['worst_drop']=event
                previous=item
            previous_group=group
    report['ordered_cases_sha256_le_group_s_t_c_p_u32']=digest.hexdigest()
    report['measurement_status']='MEASURED; no expanded parity envelope adopted'
    report['normalization']='abs(native-oracle)/max(1,abs(oracle))'
    report['strict_adjacent_float_monotonicity']='NOT_ESTABLISHED'
    return report


def original_corpus(compiler):
    report=qualify.measure()
    budget=json.loads((ROOT/'evidence/parity_budget.json').read_text())
    for key,limit in budget['limits'].items():
        if report[key]>limit: raise AssertionError((key,report[key],limit))
    if [x['id'] for x in report['guard_boundary_crossings']]!=budget['guard_boundary_ids']:
        raise AssertionError('guard boundary classifications changed')
    report.update(stage='ORIGINAL_CORPUS_FROZEN_BUDGET_PASS',compiler=compiler,
                  budget_sha256=qualify.sha(ROOT/'evidence/parity_budget.json'))
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    states=expanded_states()
    assert len(states)==12080
    assert sum(len(points(*state)) for state in states)==421486
    args.output_dir.mkdir(parents=True,exist_ok=False)
    compiler=build()
    if compiler['command'][0]=='cmd.exe':
        compiler['compile_script']=(ROOT/'build/compile.cmd').read_text(encoding='utf-8')
    metadata={'recorded_utc':datetime.now(timezone.utc).isoformat(),
              'platform':platform.platform(),'python':platform.python_version(),'compiler':compiler,
              'base_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
              'source_revision':'Uncommitted working source at measurement; identified by SHA256; final commit in delivery',
              'dctl_sha256':qualify.sha(ROOT/'dctl/PressMachine_R2.dctl'),
              'oracle_sha256':qualify.sha(ROOT/'reference/oracle.py'),
              'harness_sha256':qualify.sha(ROOT/'tests/native_harness.cpp'),
              'build_script_sha256':qualify.sha(ROOT/'tools/build_native.py'),
              'generator_sha256':qualify.sha(Path(__file__)),
              'executable_sha256':qualify.sha(EXE)}
    def write(name,value):
        (args.output_dir/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    write('metadata.json',metadata)
    controls='\n'.join(json.dumps({'group':i,'t_c_p':state,'words':list(map(o.bits,state))})
                       for i,state in enumerate(states))+'\n'
    (args.output_dir/'expanded_controls.jsonl').write_text(controls,encoding='utf-8',newline='\n')
    original=original_corpus(compiler); write('original_corpus.json',original)
    point=regression(); write('regression.json',point)
    assert point['absolute_error']<=point['case_absolute_bound']
    expanded=measure(expanded_cases(states))
    expanded.update(corpus={'seed':SEED,'random_states':12000,'edge_states':80,
                           'controls_file':'expanded_controls.jsonl','state_word_sha256':hashlib.sha256(controls.encode()).hexdigest(),
                           'random_grid':'randrange(0,2001)/10 for T; randrange(0,1001)/10 for C/P; round each to float32',
                           'edge_grid':'T=(0,.1,.2,199.9,200), C/P=(0,.1,99.9,100)',
                           'sampling':'Native float32 lo/hi order; 0,500 and +/-5 bit neighbors of lo,T,hi; clip negative bit indices at zero, deduplicate/sort per state'},
                    **metadata)
    write('expanded_scalar.json',expanded)
    assert expanded['samples']==421486
    print(json.dumps({k:expanded[k] for k in ('samples','max_normalized_error','local_decreases','maximum_drop','boosts','negatives','nonfinite')}),flush=True)
    tail=measure(tail_cases())
    tail.update(corpus={'t':[0,.1,.8,1,25,134.5,199.9,200],'c':'All 1001 tenths, 0..100',
                        'p':[0,20,59.5,100],'s':[500,1000,1e4,1e7,1e10,1e20,1e30,o.F32_MAX],
                        'rounding':'Each input rounded to float32; no state/sample deduplication'},**metadata)
    write('high_tail_scalar.json',tail)
    assert tail['samples']==256256
    print(json.dumps({k:tail[k] for k in ('samples','max_normalized_error','local_decreases','boosts','negatives','nonfinite','compression_zero_identity_failures')}),flush=True)
    for report in (expanded,tail):
        assert all(report[key]==0 for key in ('nonfinite','boosts','negatives','compression_zero_identity_failures'))
    write('summary.json',{'original_corpus':original['stage'],'regression':'PASS_CASE_ROUNDING_BOUND',
                         'expanded':'MEASURED_NOT_UNIVERSAL_BUDGET','high_tail':'MEASURED_NOT_UNIVERSAL_BUDGET',
                         'original_budget_unchanged':True,'host':'NOT_RUN','gpu':'NOT_RUN','visual':'NOT_RUN'})


if __name__=='__main__':
    main()
