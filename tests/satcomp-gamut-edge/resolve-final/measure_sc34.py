"""SC-03/04 frame-1 attribution. ZIP float EXR readback only, no Resolve calls."""
from array import array
from functools import lru_cache
from pathlib import Path
import argparse,csv,json
from fixtures import RGBA,W,N,sha,bytes_of,f32,convert
from native_checkpoint_metrics import load

CASES=('premult','straight','linear_comp','log_comp_bad'); R=Path('reference-pack'); H=Path('host-sc34')
THRESH=2e-6
EXPECTED={f'{c}_{v}_{t}' for c in CASES for v,t in (('off','base'),('base','old'),('base','new'),('base','reopen'))}|{f'{c}_cross_{t}' for c in ('straight','premult') for t in ('new','reopen')}


def need(v, message):
    if not v: raise ValueError(message)


def delta(a,b,indices=range(N)):
    return {c:max((abs(a[c][i]-b[c][i]) for i in indices),default=0.) for c in RGBA}


def rgb(a,i): return [a[c][i] for c in 'RGB']

@lru_cache(65536)
def ap1di(a): return tuple(f32(v) for v in convert(a,0,4,3,0))


def check_ui(conf,case,var,tag):
    p=Path(conf['ui']); need(sha(p)==conf['ui_sha256'],'inspector receipt SHA mismatch')
    es=json.loads(p.read_text(encoding='utf8'))['elements']; f=lambda e:e.get('frame') or {}
    vals={f(x).get('y'):x.get('value') for x in es if x.get('role')=='ComboBox' and f(x).get('x',0)>3500 and 90<=f(x).get('y',0)<=360}
    ss={f(x).get('y'):x.get('label') for x in es if x.get('role')=='Text' and f(x).get('x',0)==3700 and f(x).get('y') in (156,181,206) and x.get('label')}
    bx=[x.get('selected') for x in es if x.get('role')=='CheckBox' and x.get('label')=='Comp Bypass']
    blend=[x.get('label') for x in es if x.get('role')=='Text' and f(x).get('y')==390 and f(x).get('x') in (3487,3700) and x.get('label')]
    cross=var=='cross'; label='PR19_769a014c_'+('OLD' if tag=='old' else 'CANDIDATE')
    need(vals=={131:label,256:'DWG D65',281:'Relative Linear',306:'ACES AP1 CAT02' if cross else 'Same as Input',331:'DaVinci Intermediate' if cross else 'Same as Input'} and ss=={156:'25.0',181:'100.0',206:'20.0'} and bx==[cross] and blend==['1.000'],f'mismatched exact settings: {case}/{var}/{tag}')


def run(out):
    mp=R/'manifest.json'; need(sha(mp)=='67b3631408c111ac88bec601be71f28f47c486841dbab582a6fd5831055e2caa','fixture manifest changed')
    m=json.loads(mp.read_text(encoding='utf8'))['files']
    for c in CASES:
        p=R/f'{c}.000001.exr'; need(sha(p)==m[p.name]['sha256'],'source fixture changed: '+c)
    s={c:load(R/f'{c}.000001.exr') for c in CASES}
    need(bytes_of(s['premult'],'A')==bytes_of(s['straight'],'A'),'association stimuli have unequal coverage')
    probes=(243,308,315,320,327,334,346,420); y=135; i=y*W+327
    st=s['straight']; pm=s['premult']; rows=range(y*W,(y+1)*W)
    sep={c:0. for c in 'RGB'}; h0={}; h1={}
    for j in rows:
        a=st['A'][j]; h0[j]=[f32(a*v) for v in ap1di(tuple(rgb(st,j)))]; h1[j]=ap1di(tuple(rgb(pm,j)))
        if 0<a<1:
            for c,z,v in zip('RGB',h0[j],h1[j],strict=True): sep[c]=max(sep[c],abs(v-z))
    need(max(sep.values())>100*THRESH,'alpha contrast insufficient')
    r={'scope':'synthetic frame1, individual EXR primitive; not product or in-host two-layer Alpha Over', 'gates':{'normal_abs':THRESH,'nonvacuous_chromatic_change':1e-3,'alpha':'bit exact'},'offline':{'input_sha256':{c:sha(R/f'{c}.000001.exr') for c in CASES},'association_model_separation_partial':sep,'composite_R_before_any_effect':{c:s[c]['R'][i] for c in ('linear_comp','log_comp_bad')}},'native':{}}
    host={}; cap={}; receipt=next((p for p in (H/'receipt-scan.json',H/'receipt-resume.json',H/'receipt.json') if p.is_file()),H/'receipt.json')
    if receipt.is_file():
        info=json.loads(receipt.read_text(encoding='utf8')); r['host']= {k:info[k] for k in ('source_index','lease_readback','completed_queue','removed','error','cleanup_error','drp_sha256') if k in info}
        for k,p in info['captures'].items():
            c,v,tag=k.rsplit('_',2); j=p['job']; f=Path(p['file']); q=j['queue']; conf=p['settings_ui']
            need(c in s and v in ('off','base','cross') and j['source_index']==1 and j['data_level']=='Full' and q['MarkIn']==q['MarkOut']==86400 and q['VideoCodec']=='RGB float (ZIP)' and q['AlphaMode']==(0 if c=='premult' else 1) and q['OutputFilename']==f.name and sha(f)==p['sha256'],'wrong native source/EXR/job')
            need((conf is None and v=='off') or (conf['timeline']==j['timeline'] and sha(Path(conf['ui']))==conf['ui_sha256']),'no correlated FX inspector')
            need(k in EXPECTED,'unexpected capture')
            if v!='off': check_ui(conf,c,v,tag)
            z=load(f); host[k]=z; cap[k]={'job':j['job'],'timeline':j['timeline'],'media_id':j['media_id'],'file':p['file'],'sha256':p['sha256']}; n=r['native'][k]={**cap[k],'alpha_word_exact':bytes_of(z,'A')==bytes_of(s[c],'A'),'at_center':rgb(z,i),'alpha_at_center':z['A'][i]}
            if v=='off': n['off_source_rgba_exact']=bytes_of(z,RGBA)==bytes_of(s[c],RGBA)
            if v=='base':
                n['rgb_max_vs_off']=max(v for c,v in delta(z,s[c]).items() if c!='A')
                n['center_delta_R_vs_off']=abs(z['R'][i]-s[c]['R'][i]); n['protected_alpha_buckets']={nm:sum(t(a) for a in z['A']) for nm,t in [('zero',lambda a:a==0),('partial',lambda a:0<a<1),('opaque',lambda a:a==1)]}
        r['rgb_old_new']={}
        r['reopen']={}
        for c in CASES:
            old,new,rep=(host.get(f'{c}_base_{k}') for k in ('old','new','reopen'))
            if old and new:
                d=delta(old,new); r['rgb_old_new'][c]={'max_abs':d,'rgba_bit_exact':bytes_of(old,RGBA)==bytes_of(new,RGBA),'within_tolerance':max(d.values())<=THRESH}
            if new and rep:r['reopen'][c+'_base']=bytes_of(new,RGBA)==bytes_of(rep,RGBA)
            new,rep=(host.get(f'{c}_cross_{k}') for k in ('new','reopen'))
            if new and rep:r['reopen'][c+'_cross']=bytes_of(new,RGBA)==bytes_of(rep,RGBA)
        if all(f'{c}_base_new' in host for c in ('linear_comp','log_comp_bad')):
            r['composite_R_after_candidate']={c:host[f'{c}_base_new']['R'][i] for c in ('linear_comp','log_comp_bad')}
        a,b=host.get('straight_cross_new'),host.get('premult_cross_new')
        if a and b:
            idx=[i for i in rows if 0<st['A'][i]<1]; hidden=[i for i in rows if st['A'][i]==0]
            prim=[i for i in idx if st['A'][i]>=.01]; tiny=[i for i in idx if st['A'][i]<.01]
            r['association_cross']={
                'premult_vs_actual_straight_times_alpha_partial_max':{c:max(abs(b[c][i]-f32(a[c][i]*st['A'][i])) for i in idx) for c in 'RGB'},
                'premult_vs_analytic_straight_times_alpha_partial_max':{c:max(abs(b[c][i]-h0[i][k]) for i in idx) for k,c in enumerate('RGB')},
                'premult_vs_transform_associated_first_partial_max':{c:max(abs(b[c][i]-h1[i][k]) for i in idx) for k,c in enumerate('RGB')},
                'straight_vs_analytic_nonzero_A_max':{c:max(abs(a[c][i]-ap1di(tuple(rgb(st,i)))[k]) for i in rows if st['A'][i]>0) for k,c in enumerate('RGB')},
                'alpha_zero_centerline_separate':{'n':len(hidden),'straight_RGB_max_magnitude':max(abs(a[c][i]) for i in hidden for c in 'RGB'),'premult_RGB_max_magnitude':max(abs(b[c][i]) for i in hidden for c in 'RGB')},
                'primary_alpha_001_to_1':{'n':len(prim),'max_residual':max(abs(b[c][i]-h0[i][k]) for i in prim for k,c in enumerate('RGB')),'wrong_order_max_residual':max(abs(b[c][i]-h1[i][k]) for i in prim for k,c in enumerate('RGB'))},
                'near_zero_separate':{'n':len(tiny),'max_associated_residual':max(abs(b[c][i]-h0[i][k]) for i in tiny for k,c in enumerate('RGB')),'max_rgb_error_after_dividing_by_alpha':max(abs(b[c][i]-h0[i][k])/st['A'][i] for i in tiny for k,c in enumerate('RGB'))},
            }
    complete=set(host)==EXPECTED and r.get('host',{}).get('lease_readback')=='FREE' and 'error' not in r.get('host',{}) and 'cleanup_error' not in r.get('host',{})
    checks={'off_words':all(r['native'].get(c+'_off_base',{}).get('off_source_rgba_exact') for c in CASES),'alpha_words':bool(host) and all(x['alpha_word_exact'] for x in r['native'].values()),'old_new':bool(r.get('rgb_old_new')) and len(r['rgb_old_new'])==4 and all(x['within_tolerance'] for x in r['rgb_old_new'].values()),'nonvacuous':all(r['native'].get(f'{c}_base_{t}',{}).get('center_delta_R_vs_off',0)>=1e-3 for c in CASES for t in ('old','new')),'reopen':len(r.get('reopen',{}))==6 and all(r['reopen'].values())}
    ap=r.get('association_cross',{}).get('primary_alpha_001_to_1'); checks['association_primary']=bool(ap and ap['max_residual']<=THRESH and ap['wrong_order_max_residual']>=100*THRESH)
    r['checks']=checks
    r['coverage']={'native_expected':len(EXPECTED),'native_captured':len(host),'normal_fixture_repeated':False,'strictly_complete':complete,'scoped_numerical_pass':complete and all(checks.values())}
    out.mkdir(exist_ok=False)
    with (out/'row135.csv').open('x',encoding='utf8',newline='') as f:
        w=csv.writer(f); w.writerow(['x','inputA','inputPixelClass',*[f'{c}_{k}' for c in s for k in RGBA],*[f'{c}_{k}' for c in host for k in RGBA],'model_straight_times_A_R','model_associated_first_R'])
        for j in rows:
            a=st['A'][j]; w.writerow([j%W,a,'zero' if a==0 else 'opaque' if a==1 else 'partial',*[z[k][j] for z in s.values() for k in RGBA],*[z[k][j] for z in host.values() for k in RGBA],h0[j][0],h1[j][0]])
    with (out/'metrics.json').open('x',encoding='utf8') as f:json.dump(r,f,indent=2,allow_nan=False)
    print(json.dumps({k:r[k] for k in ('coverage','offline','rgb_old_new','reopen','association_cross','composite_R_after_candidate') if k in r},indent=2),flush=True)
    return r

if __name__=='__main__':
    a=argparse.ArgumentParser(); a.add_argument('output',type=Path); run(a.parse_args().output)
