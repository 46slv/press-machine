"""SC11 numerical replay. Compare actual two-layer Resolve RGB with positive/negative controls."""
from collections import Counter
from pathlib import Path
import sys,json
from fixtures import N,W,RGBA,sha,bytes_of,f32
from native_checkpoint_metrics import load
from measure_sc34 import need,delta

RECEIPT=Path('host-sc11/receipt.json'); REF=Path('reference-pack'); PLANES=('premult','straight')

def run(out):
    r=json.loads(RECEIPT.read_text(encoding='utf8')); a=r['captures']
    need(set(a)==set(PLANES) and r['lease_readback']=='FREE' and not {'error','cleanup_error'}&r.keys(),'missing complete SC11 capture')
    need(sha(REF/'manifest.json')=='67b3631408c111ac88bec601be71f28f47c486841dbab582a6fd5831055e2caa','fixture manifest changed'); m=json.loads((REF/'manifest.json').read_text(encoding='utf8'))['files']
    def source(kind):
        p=REF/f'{kind}.000001.exr'; need(sha(p)==m[p.name]['sha256'],'unmatched source'); return load(p)
    linear=source('linear_comp'); wrong=source('log_comp_bad'); i=135*W+327; rgb={}; loaded={}
    mids={'premult':'466e64d5-57cc-4be3-a273-176cb6793118','straight':'1a1fa68a-6c3e-46bc-b898-de3c28c2a6ae'}
    for k in PLANES:
        c=a[k]; f=Path(c['file']); j=c['job']; q=j['queue']; t,b=j['tracks']
        need(c['completion']=={'JobStatus':'Complete','CompletionPercentage':100} and sha(f)==c['sha256'],'unmatched delivery')
        need(q['RenderMode']=='Single clip' and q['MarkIn']==q['MarkOut']==86400 and q['VideoCodec']=='RGB float (ZIP)' and q['OutputFilename']==f.name and q['ExportAlpha'] and q['TimelineName']=='SAT19_SC11_'+k,'wrong delivery route')
        need(t['index']==1 and b['index']==2 and b['media_id']==mids[k] and all(x['composite']=='Normal' and x['opacity']==100 and x['source_index']==1 and x['effects']==[] for x in (t,b)),'unqualified track stack')
        z=load(f); loaded[k]=z
        x=rgb[k]={'vs_linear_max_abs':delta(z,linear),'vs_log_max_abs':delta(z,wrong),'center':{c:z[c][i] for c in RGBA},'alpha_bit_exact':bytes_of(z,'A')==bytes_of(linear,'A')}
        x['rgb_linear_gate_pass']=max(x['vs_linear_max_abs'][c] for c in 'RGB')<=2e-6 and abs(z['R'][i]-wrong['R'][i])>=.1
        x['exact_rgba_gate_pass']=x['rgb_linear_gate_pass'] and x['alpha_bit_exact']
        x['alpha_output_histogram']=[{'value':v,'pixels':n} for v,n in sorted(Counter(z['A']).items())]
        fg=source(k)
        x['alpha_reference_source_over_matches']=sum(v==f32(a0+f32(1-a0)) for v,a0 in zip(z['A'],fg['A'],strict=True))
    d={'scope':'two real timeline tracks using Normal, no effects, unmanaged DWG-linear test only','receipt_sha256':sha(RECEIPT),'probe':[327,135],'linear_R':linear['R'][i],'known_wrong_log_R':wrong['R'][i],'results':rgb,'premult_vs_straight_max_abs':delta(loaded['premult'],loaded['straight']),'alpha_words_equal_between_modes':bytes_of(loaded['premult'],'A')==bytes_of(loaded['straight'],'A'),'rgba_words_equal':bytes_of(loaded['premult'],RGBA)==bytes_of(loaded['straight'],RGBA)}
    with out.open('x',encoding='utf8') as f: json.dump(d,f,indent=2,allow_nan=False)
    print(json.dumps(d,indent=2)); return d

if __name__=='__main__': run(Path(sys.argv[1]))
