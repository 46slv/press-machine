"""Offline comparison for two extreme same-gamut transfer diagnoses."""
from array import array
from pathlib import Path
import json,sys
from fixtures import RGBA,W,N,bytes_of,encode,f32,sha
from native_checkpoint_metrics import load
from measure_nonlog_r1_native import verified
from measure_di_r2 import samples, SKIP_STEPS
H=Path('host-sc02'); R=Path('host-control-inputs/range3.000000.exr')

def run(out):
    rec=json.loads((H/'receipt.json').read_text(encoding='utf8')) if (H/'receipt.json').exists() else {'captures':{}}
    x=load(R); src=load(Path('host-control-off-raw/range3/range3_off00000000.exr')); assert bytes_of(x,RGBA)==bytes_of(src,RGBA)
    outdata={}
    for name,tr,trial in [('LogC3',1,1),('DIExtreme',0,4)]:
        fx,observed=verified('range3','ofx',trial); q=rec['captures'].get(name)
        oracle={c:array('f',(f32(encode(v,tr)) for v in x[c])) for c in 'RGB'}; oracle['A']=x['A']
        group={'resolvefx':observed}; report={'settings':fx, 'routes':{}}
        if q:
            f=Path(q['file']); assert q['completion']=={'JobStatus':'Complete','CompletionPercentage':100} and sha(f)==q['sha256'] and q['job']['mode']==name
            group['direct']=load(f); report['direct_receipt']=q
        for link,px in group.items():
            a={c:samples(px[c],oracle[c],range(N)) for c in 'RGB'}; s={c:max(abs((px[c][i+1]-px[c][i])-(oracle[c][i+1]-oracle[c][i])) for i in range(180*W,181*W-1)) for c in 'RGB'}
            aa=bytes_of(px,'A')==bytes_of(x,'A'); i=180*W+600
            report['routes'][link]={'RGB':a,'step':s,'A_word_exact':aa,'pass':aa and all(w['over_scaled']==0 and w['unexpected_zero']==0 for w in a.values()) and max(s.values())<=2e-5,'R_at_600_180':{'expected':oracle['R'][i],'observed':px['R'][i],'input':x['R'][i]}}
        if 'direct' in group:
            raw=group['direct']; report['conditional_model_from_native_direct']={c:sum(o==f32(i+f32(z-i)) for i,z,o in zip(x[c],raw[c],observed[c],strict=True)) for c in 'RGB'}
        outdata[name]=report
    data={'scope':'fixed exact candidate; opaque, extreme source; not original product acceptance','source_sha256':sha(R),'off_rgba_exact':True,'native_capture_count':len(rec['captures']),'host_flags':{k:rec[k] for k in ('lease_readback','removed','error','cleanup_error') if k in rec},'cases':outdata}
    with out.open('x',encoding='utf8') as f:json.dump(data,f,indent=2,allow_nan=False)
    for k,v in outdata.items():print(k,[(n,z['pass'],z['R_at_600_180'],z['RGB']['R']['unexpected_zero']) for n,z in v['routes'].items()],v.get('conditional_model_from_native_direct'))
    return data
if __name__=='__main__':run(Path(sys.argv[1]))
