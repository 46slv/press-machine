"""Offline replay of pinned SatComp near-DI Resolve captures. No live Resolve access."""
import argparse
import csv
import json
from pathlib import Path

from fixtures import N, W, RGBA, bytes_of, sha, f32
from native_checkpoint_metrics import load
from measure import absolute_map


SCALE = 1e-5
STEP = 2e-5
# Input fixture deliberately overwrites x=300,301; neither adjacent nor internal edges score smoothness.
SKIP_STEPS = {299,300,301}
ROWS = ((60,'R'),(180,'G'),(300,'R'))
PINS = {
    'input': ('host-nonlog-r1/near-input/near_di.000000.exr','d3a503185db4a0371954043ecc7011f65de372a1bcbcbc4eed678680822b94b6'),
    'oracle': ('research-blend/near-range-fixture/sat-near-di-oracle.000000.exr','8c1c388af50a5578084a737e8916e7a6636e154dd840921210b70bb772e79ee1'),
    'off': ('host-nonlog-r1/near_di_off_take0/near_di_off_take0_00000000.exr','9692a2a4fdbb274543520d89257f9ae2e4faead56c05908ae45c1a2b08064d61'),
    'resolvefx': ('host-nonlog-r1/near_di_ofx_take1/near_di_ofx_take1_00000000.exr','175b5df1b1316b944f611514ed46ca93ca49ed82249bf30f27bc8c1267dca899'),
}


def want(ok, why):
    if not ok:
        raise ValueError(why)


def samples(v,q,idx):
    delta=[abs(v[i]-q[i]) for i in idx]
    scaled=[d/max(1,abs(q[i])) for d,i in zip(delta,idx,strict=True)]
    n=max(range(len(idx)),key=scaled.__getitem__); i=idx[n]
    return {'n':len(idx),'max_abs':max(delta),'max_scaled':scaled[n],'over_scaled':sum(d>SCALE for d in scaled),'unexpected_zero':sum(v[i]==0 and q[i]!=0 for i in idx),'worst':{'x':i%W,'y':i//W,'actual':v[i],'reference':q[i]}}


def details(a,b,src):
    d={'full_frame':{ch:samples(a[ch],b[ch],range(N)) for ch in 'RGB'},'rows':{},'alpha_word_exact':bytes_of(a,'A')==bytes_of(src,'A')}
    for y,ch in ROWS:
        k=range(y*W,(y+1)*W); x=a[ch]; q=b[ch]; s=src[ch]
        vals=samples(x,q,k)
        st=sorted(((abs((x[i+1]-x[i])-(q[i+1]-q[i])),i%W) for i in k[:-1] if i%W not in SKIP_STEPS),reverse=True)
        vals.update({'step_max':st[0][0],'step_over':sum(v>STEP for v,_ in st),'step_pairs':len(st),'step_worst_left_x':st[0][1], 'input_at_worst':s[y*W+vals['worst']['x']]})
        d['rows'][f'{ch}@{y}']=vals
    return d


def gate(d):
    return (d['alpha_word_exact'] and all(x['over_scaled']==x['unexpected_zero']==0 for x in d['full_frame'].values()) and all(x['step_over']==0 for x in d['rows'].values()))


def read_native(p):
    r=json.loads(p.read_text(encoding='utf8'))
    want(r.get('gpu_backend')=='CUDA' and r.get('lease_readback')=='FREE' and r.get('staged_removed') and 'error' not in r and 'cleanup_error' not in r,'incomplete host verification')
    want(set(r['captures'])=={'direct','reopen'},'missing native direct/reopen capture')
    want(r['admission']['resolvefx']['id']=='06d12afb-b233-4711-8b62-35fa62b8730e','wrong paired FX timeline')
    want(r['checkpoint']['after_reopen']['id']==r['apply']['direct']['id'],'checkpoint identity mismatch')
    want(sha(Path(r['drp']['path']))==r['drp']['sha256'],'changed DRP')
    for k,d in r['captures'].items():
        want(d['readback']=={'JobStatus':'Complete','CompletionPercentage':100} and d['job']['direct']==r['apply']['direct'] and d['job']['resolvefx']==r['admission']['resolvefx'],'paired job wrong clip/graph')
        want(Path(d['path']).name==d['job']['queue']['OutputFilename'] and d['job']['queue']['JobId']==d['job']['job'],'unbound render job')
    return r


def prior_job(name):
    def result(file):
        a=json.loads(file.read_text(encoding='utf8').splitlines()[-1])['mcp_result']
        want(not a.get('isError'),f'failed R1 MCP envelope: {file}')
        return json.loads(a['content'][0]['text'])['result']
    root=Path('evidence'); fx=name=='resolvefx'; take='ofx-take1' if fx else 'off-take0'
    slug='nonlog-r1-near-di-'+take
    d=result(root/(slug+'-mcp.jsonl')); q=d['queue']; filename,digest=PINS[name]
    want(d['blocked'] is None and d['clip_start']==d['source_index']==0 and d['alpha_mode']=='Straight' and d['source_path'].replace('\\','/').lower().endswith('/host-nonlog-r1/near-input/near_di.[000000-000001].exr'),'R1 source mismatch')
    want(d['project_id']=='e17e7e45-1a29-4bed-9ecb-54f6a5f05c39' and (not fx or d['timeline']=='06d12afb-b233-4711-8b62-35fa62b8730e') and not d['lut'] and (d['tools']==['OFX：DCTL'] if fx else not d['tools']),'R1 graph mismatch')
    expected={'OutputFilename':Path(filename).name,'JobId':d['job'],'MarkIn':86400,'MarkOut':86400,'FormatWidth':640,'FormatHeight':360,'FrameRate':'24','VideoCodec':'RGB float (ZIP)','ExportAlpha':True,'AlphaMode':1,'PixelAspectRatio':1.0,'RenderMode':'Individual clips'}
    want(all(q.get(k)==v for k,v in expected.items()),'R1 render settings mismatch')
    want(any(any(j['id']==d['job'] and j['status']=={'JobStatus':'Complete','CompletionPercentage':100} for j in result(z)['jobs']) for z in root.glob(slug+'-verify*-mcp.jsonl')),'R1 complete job missing')
    ctl=None
    if fx:
        u=root/'nonlog-r1-near-di-1-settings-ui.json'; els=json.loads(u.read_text(encoding='utf8'))['elements']
        frame=lambda e:e.get('frame') or {}
        combos={frame(e).get('y'):e.get('value') for e in els if e.get('role')=='ComboBox' and frame(e).get('x',0)>3500 and 90<=frame(e).get('y',0)<=360}
        sliders={frame(e).get('y'):e.get('label') for e in els if e.get('role')=='Text' and e.get('label') and frame(e).get('x')==3700 and frame(e).get('y') in (156,181,206)}
        bypass=[e.get('selected') for e in els if e.get('label')=='Comp Bypass' and e.get('role')=='CheckBox']
        blend=[e.get('label') for e in els if e.get('role')=='Text' and frame(e).get('y')==390 and frame(e).get('x') in (3487,3700) and e.get('label')]
        want(combos=={131:'PR19_769a014c_CANDIDATE',256:'DWG D65',281:'Relative Linear',306:'Same as Input',331:'DaVinci Intermediate'} and sliders=={156:'25.0',181:'100.0',206:'20.0'} and bypass==[True] and blend==['1.000'],'R1 transform/sliders mismatch')
        ctl={'source_ui':u.as_posix(),'sha256':sha(u),'controls':combos,'sliders':sliders,'comp_bypass':True,'global_blend':1.0}
    want(sha(Path(filename))==digest,'R1 EXR changed')
    return {'path':filename,'sha256':digest,'job':d['job'],'timeline':d['timeline'],'source_index':0,'alpha_mode':'Straight','settings':ctl}


def calc(out, receipt):
    picks=dict(PINS); host={}
    fx=prior_job('resolvefx'); off=prior_job('off')
    if receipt:
        host=read_native(receipt)
        for k,c in host['captures'].items(): picks[k]=(c['path'],c['sha256'])
    for kind,(filename,digest) in picks.items():
        want(sha(Path(filename))==digest, f'{kind} SHA mismatch')
    a={k:load(Path(p)) for k,(p,_) in picks.items()}
    src=a['input']; ref=a['oracle']; fxarr=a['resolvefx']; offarr=a['off']
    want(bytes_of(src,RGBA)==bytes_of(offarr,RGBA),'OFF differs from input')
    want(bytes_of(src,'A')==bytes_of(ref,'A') and all(v==1 for v in src['A']),'not the pinned opaque alpha trial')
    d={'scope':'SatComp PR19 769a014c near-DI only; no product or native-OFX claim', 'scale_limit':SCALE,'smooth_step_limit':STEP,'excluded_left_x':sorted(SKIP_STEPS),'bit_exact_off_input':True,'resolvefx_r1':fx,'off_r1':off,'files':picks,'verified_native_direct':bool(receipt),'reports':{},'conditional_model':{}}
    for name,x in [('resolvefx',fxarr),*((k,a[k]) for k in ('direct','reopen') if k in a)]:
        r=d['reports'][name]=details(x,ref,src); r['gate_pass']=gate(r)
    if host:
        want(host['restore']['blocked'] is None and not host['restore']['direct_after']['lut'] and host['final_queue_count']==host['admission']['jobs_before']+2,'scratch restore not confirmed')
        d.update({'capture_jobs':{k:p['job']['job'] for k,p in host['captures'].items()},'drp':host['drp'],'direct_reopen_rgba_bit_exact':bytes_of(a['direct'],RGBA)==bytes_of(a['reopen'],RGBA),'resolvefx_vs_direct':details(fxarr,a['direct'],src)})
        d['full_frame_conditional_model_from_direct']={}
        for ch in 'RGB':
            x, z, y=offarr[ch], a['direct'][ch], fxarr[ch]
            diff=[abs(o-f32(v+f32(t-v))) for v,t,o in zip(x,z,y,strict=True)]
            d['full_frame_conditional_model_from_direct'][ch]={'count':len(diff),'exact':diff.count(0.0),'max_abs_residual':max(diff)}
    out.mkdir(exist_ok=False)
    with (out/'centerlines.csv').open('x',encoding='utf-8',newline='') as f:
        wr=csv.writer(f); names=['off','oracle','resolvefx']+(['direct','reopen'] if host else [])
        wr.writerow(['y','x','channel',*names,'abs_fx_vs_off_cross_units','abs_fx_vs_oracle',*(['abs_direct_vs_oracle','abs_fx_vs_direct'] if host else []),'conditional_model_from_oracle','conditional_model_from_direct'])
        for y,ch in ROWS:
            counts={'oracle_exact':0,'direct_exact':0 if host else None,'count':W,'oracle_mismatch_first16':[],'direct_mismatch_first16':[] if host else None}
            for x in range(W):
                i=y*W+x; v=offarr[ch][i]; fxv=fxarr[ch][i]; q=ref[ch][i]
                model=f32(v+f32(q-v)); dm=None
                if fxv==model: counts['oracle_exact']+=1
                elif len(counts['oracle_mismatch_first16'])<16: counts['oracle_mismatch_first16'].append(x)
                if host:
                    dv=a['direct'][ch][i]; dm=f32(v+f32(dv-v))
                    if fxv==dm: counts['direct_exact']+=1
                    elif len(counts['direct_mismatch_first16'])<16: counts['direct_mismatch_first16'].append(x)
                wr.writerow([y,x,ch,*[a[k][ch][i] for k in names],abs(fxv-v),abs(fxv-q),*([abs(dv-q),abs(fxv-dv)] if host else []),model,dm])
            d['conditional_model'][f'{ch}@{y}']=counts
    pairs={'resolvefx_vs_oracle':(fxarr,ref),'resolvefx_vs_off_cross_units':(fxarr,offarr)}
    if host: pairs.update({'direct_vs_oracle':(a['direct'],ref),'direct_vs_off_cross_units':(a['direct'],offarr),'resolvefx_vs_direct':(fxarr,a['direct'])})
    maps={}
    for label,(x,y) in pairs.items():
        p=out/(label+'.f64.gz'); absolute_map(p,x,y); maps[p.name]=sha(p)
    d['abs_maps']={'format':'unscaled |a-b|, planar RGBA 640x360 little-endian float64 gzip; cross_units is numeric only, not a visual or quality delta','files':maps}
    d['centerlines_sha256']=sha(out/'centerlines.csv')
    with (out/'metrics.json').open('x',encoding='utf-8') as f: json.dump(d,f,indent=2,allow_nan=False); f.write('\n')
    print(json.dumps({'reports':{k:(v['gate_pass'],v['alpha_word_exact'],{r:{j:c[j] for j in ('max_scaled','over_scaled','step_max','unexpected_zero')} for r,c in v['rows'].items()}) for k,v in d['reports'].items()},'reopen_exact':d.get('direct_reopen_rgba_bit_exact'),'model':d['conditional_model']},indent=2))
    return d


if __name__=='__main__':
    if not __debug__: raise SystemExit('Do not disable the dependency assertions.')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    g=p.add_mutually_exclusive_group(required=True); g.add_argument('--receipt',type=Path); g.add_argument('--prior-only',action='store_true')
    args=p.parse_args(); calc(args.output,args.receipt)
