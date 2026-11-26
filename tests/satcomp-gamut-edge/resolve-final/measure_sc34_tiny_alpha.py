"""Measure the near-zero association knee separately, without an absolute RGB floor."""
from pathlib import Path
from math import isfinite
import csv,json,sys
from fixtures import RGBA,W,f32,sha,bytes_of
from native_checkpoint_metrics import load
from measure_sc34 import ap1di

R=Path('host-sc34/receipt-scan.json')
def measure(out):
    r=json.loads(R.read_text(encoding='utf8'))
    def pull(k):
        a=r['captures'][k]; p=Path(a['file']); assert sha(p)==a['sha256']; return load(p)
    off=pull('premult_off_base'); st=pull('straight_cross_new'); pm=pull('premult_cross_new'); s0=pull('straight_base_new'); p0=pull('premult_base_new'); old=pull('premult_base_old')
    assert bytes_of(off,'A')==bytes_of(st,'A')==bytes_of(pm,'A')==bytes_of(p0,'A') and bytes_of(p0,RGBA)==bytes_of(old,RGBA)
    observed=[]; threshold=1e-7
    for i in range(135*W,136*W):
        a=off['A'][i]
        if not 0<a<.01: continue
        native=[pm[c][i] for c in 'RGB']; inp=[off[c][i] for c in 'RGB']; graded_raw=ap1di(tuple(inp)); right=[f32(st[c][i]*a) for c in 'RGB']; multiply_raw=[f32(v*a) for v in graded_raw]
        def ratio(q): return max(abs(p-q0)/a for p,q0 in zip(native,q,strict=True))
        observed.append({'x':i%W,'A':a,'native':native,'offRGB':inp,'straight_then_premult':right,'transform_associated_then_premult_again':multiply_raw,'normal_unassociated_residual':ratio(right),'associated_twice_unassociated_residual':ratio(multiply_raw),'native_base_R_div_A':p0['R'][i]/a,'straight_base_R':s0['R'][i]})
    below=[d for d in observed if d['A']<threshold]; above=[d for d in observed if d['A']>=threshold]
    assert below and above
    bounds={'max_alpha_below':max(q['A'] for q in below),'min_alpha_above':min(q['A'] for q in above)}
    res={'scope':'different association behaviors around near-zero alpha in an existing end-to-end capture. No exact cutoff or internal ownership claimed. A=0 excluded.', 'threshold_candidate_for_classification':threshold,'observed_bracket':bounds,'rows':{},'evidence_sha256':sha(R)}
    for n,x in [('below',below),('above',above)]:
        res['rows'][n]={'n':len(x),'worst_unassociated_residual_straight_then_A':max(d['normal_unassociated_residual'] for d in x),'worst_unassociated_residual_transform_associated_then_A':max(d['associated_twice_unassociated_residual'] for d in x),'closest_to_knee':max(x,key=lambda d:d['A']) if n=='below' else min(x,key=lambda d:d['A'])}
    assert res['rows']['below']['worst_unassociated_residual_transform_associated_then_A']<2e-6 and res['rows']['above']['worst_unassociated_residual_straight_then_A']<2e-6
    out.mkdir(exist_ok=False)
    with (out/'metrics.json').open('x',encoding='utf8') as f: json.dump(res,f,indent=2,allow_nan=False)
    with (out/'samples.csv').open('x',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(observed[0])); w.writeheader(); w.writerows(observed)
    print(json.dumps(res,indent=2)); return res
if __name__=='__main__': measure(Path(sys.argv[1]))
