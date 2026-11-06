"""Reproduce the pre-repair numeric failure and check final R2 candidate."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import boundary_diagnosis as b
from tools import domain_probe as d
from tools import qualify as q
from tools.build_native import ROOT, EXE, build
from tools.generate_precision_candidate import BASE_COMMIT

def measure():
    baseline_source=subprocess.check_output(['git','-C',str(ROOT),'show',
        BASE_COMMIT+':dctl/PressMachine_R2.dctl'])
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build/boundary_baseline.dctl').write_bytes(baseline_source)
    baseline_harness=subprocess.check_output(['git','-C',str(ROOT),'show',
        BASE_COMMIT+':tests/native_harness.cpp']).decode('utf-8').replace(
        '../dctl/PressMachine_R2.dctl','../build/boundary_baseline.dctl')
    (ROOT/'build/boundary_baseline.cpp').write_text(baseline_harness,encoding='utf-8')
    baseline_exe=ROOT/'build/boundary_baseline.exe'
    compiler={'baseline':build('build/boundary_baseline.cpp',baseline_exe),
              'current':build()}
    d.EXE=baseline_exe
    before=b.focused_numeric()
    d.EXE=EXE
    after=b.focused_numeric()
    planes=b.cancellation_planes()
    seams=b.routing_seams()
    original=q.measure()
    frozen=json.loads((ROOT/'evidence/parity_budget.json').read_text())
    for key,limit in frozen['limits'].items():
        if original[key]>limit: raise AssertionError((key,original[key],limit))
    if [x['id'] for x in original['guard_boundary_crossings']]!=frozen['guard_boundary_ids']:
        raise AssertionError('original guard observations changed')
    if not before['outside_existing_empirical_envelope']:
        raise AssertionError('pre-repair regression was not reproduced')
    if after['outside_existing_empirical_envelope']:
        raise AssertionError(after)
    if planes['outside_existing_empirical_envelope_or_nonfinite'] or seams['outside_existing_empirical_envelope']:
        raise AssertionError((planes,seams))
    return {'status':'R2_NUMERIC_REPAIR_PASS_NOT_HOST_OR_VISUAL_ACCEPTANCE',
        'baseline_commit':BASE_COMMIT,
        'baseline_dctl_sha256':q.sha(ROOT/'build/boundary_baseline.dctl'),
        'current_dctl_sha256':q.sha(ROOT/'dctl/PressMachine_R2.dctl'),
        'unchanged_frozen_budget_sha256':q.sha(ROOT/'evidence/parity_budget.json'),
        'compiler':compiler,'before':before,'after':after,
        'all_LMS_planes':planes,'routing_seams':seams,
        'recorded_cusp_pair':b.recorded_pair(),
        'reference_cusp_convergence':b.convergence(),
        'original_corpus_unchanged_budgets':original,
        'Resolve_GPU':'NOT_RUN','alpha_host':'NOT_RUN',
        'performance_4k':'NOT_RUN','visual_user_acceptance':'NOT_RUN',
        'continuous_domain_proposal':'UNCHANGED_UNAPPROVED',
        'remaining_L_guard_jump':'UNCHANGED_BY_R2_CONTRACT'}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=measure()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('compiler','original_corpus_unchanged_budgets','reference_cusp_convergence')},indent=2))
