"""Native SC09 comparison; the CUDA-only diagnostic is distinct from the production effect."""
import json,sys
from pathlib import Path
from fixtures import RGBA,N,W,bytes_of,sha
from native_checkpoint_metrics import load

P=Path('goal-blend'); H=Path('host-sc09')
PINS={'input':('satblend.000000.exr','9e2e348fcfa7a9a42f04d9e5f010be57a3067d8c8b82594ee9fa6c1a67fd709a'),'off':('off/blend_off00000000.exr','cedc6f82bf84ba6c504ca385f682f6ebd739df4f9a7d94703922b6c913fa4c24'),'direct':('direct/blend_direct00000000.exr','b45b094f067f5f4e0dade04f7dc7ff3ece267682edb571a7c254ad466ebbc39a'),'builtin_fx':('full/blend_full00000000.exr','e8a9bca21bdd38a40a57ade17e61f87d063daf4c3286defbbe1f7bef8a6a6e47')}
CONSTANT=dict(zip(RGBA,(8.125,8.125,.375,1.)))

def data():
    z={}; files={}
    for k,(name,h) in PINS.items():
        p=P/name; assert sha(p)==h; z[k]=load(p); files[k]={'sha256':h,'file':p.as_posix()}
    assert bytes_of(z['input'],RGBA)==bytes_of(z['off'],RGBA)
    assert all(all(v==CONSTANT[c] for v in z['direct'][c]) for c in RGBA)
    assert all(v==1. for v in z['input']['A'])
    print('same-input controls duplicated verified: opaque, OFF bit exact, direct exact',flush=True)
    return z,files

def run(dst, allow_prior=False):
    z,files=data(); label='SatComp SC09 Opaque CUDA 8125'; cap=H/'capture.json'; host=None
    if cap.is_file():
        a=json.loads(cap.read_text(encoding='utf8')); f=Path(a['file']); j=a['job']; q=j['queue']; g=json.loads(Path('native-ofx-sc09/gpu-verification-final.json').read_text(encoding='utf8'))
        assert sha(f)==a['sha256'] and a['completion']=={'JobStatus':'Complete','CompletionPercentage':100} and a['ofx_sha256']==g['ofx_sha256']
        assert j['tools']==['OFX：'+label] and j['source_index']==0 and q['VideoCodec']=='RGB float (ZIP)' and q['MarkIn']==q['MarkOut']==86400 and q['ExportAlpha'] and q.get('AlphaMode')==1 and q.get('OutputFilename')==f.name
        z['native_ofx']=load(f); files['native_ofx']={'sha256':a['sha256'],'file':f.as_posix(),'job':j['job'],'binary':a['ofx_sha256']}
        host=json.loads((H/'cleanup.json').read_text(encoding='utf8')) if (H/'cleanup.json').is_file() else None
    elif not allow_prior: raise RuntimeError('no new qualified native OFX render')
    f={k:{'constant_exact_pixels':sum(all(x[c][i]==CONSTANT[c] for c in RGBA) for i in range(N)),'alpha_word_exact_to_input':bytes_of(x,'A')==bytes_of(z['input'],'A'),'per_channel':{c:{'constant_exact':sum(v==CONSTANT[c] for v in x[c]),'zeros':sum(v==0 for v in x[c]),'sixteens':sum(v==16 for v in x[c]),'max_abs_vs_constant':max(abs(v-CONSTANT[c]) for v in x[c])} for c in RGBA}} for k,x in z.items() if k not in ('input','off')}
    probes={f'{x},{y}':{k:[v[c][y*W+x] for c in RGBA] for k,v in z.items()} for x,y in ((620,45),(620,135),(10,45),(10,135),(320,225))}
    r={'scope':'opaque constant; alpha=0 deliberately excluded; no original-route pass','captures':files,'comparison':f,'probes':probes,'native_live':cap.is_file(),'cleanup':host}
    if 'native_ofx' in z:
        r['native_vs_builtin_rgba_bit_exact']=bytes_of(z['native_ofx'],RGBA)==bytes_of(z['builtin_fx'],RGBA)
        r['native_vs_direct_rgba_bit_exact']=bytes_of(z['native_ofx'],RGBA)==bytes_of(z['direct'],RGBA)
    with dst.open('x',encoding='utf8') as o: json.dump(r,o,indent=2,allow_nan=False)
    print(f)
    return r
if __name__=='__main__': run(Path(sys.argv[1]), sys.argv[2:]==['--prior-only'])
