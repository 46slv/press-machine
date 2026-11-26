"""Local replay: actual fixed Color vs prior configured ResolveFX on the same alpha inputs."""
import json,sys
from pathlib import Path
from fixtures import W,RGBA,bytes_of,sha,f32
from native_checkpoint_metrics import load
from measure_sc34 import ap1di,check_ui,need

OLD=Path('host-sc34/receipt-scan.json'); NEW=Path('host-sc10/receipt.json')

def run(dst):
    b=json.loads(OLD.read_text(encoding='utf8')); d=json.loads(NEW.read_text(encoding='utf8'))
    need(d['lease_readback']=='FREE' and d['staged_absent'] and not {'error','cleanup_error'}&d.keys(),'unqualified SC10 scope')
    def read(a):
        p=Path(a['file']); need(sha(p)==a['sha256'],'wrong EXR file'); return load(p)
    z={}; receipts={}; bit={}
    for k,am in (('straight',1),('premult',0)):
        old=b['captures'][k+'_cross_new']; raw=b['captures'][k+'_off_base']; check_ui(old['settings_ui'],k,'cross','new')
        new=d['captures'][k]; j=new['job']; q=j['queue']
        need(j['media_id']==old['job']['media_id']==raw['job']['media_id'] and j['source_index']==old['job']['source_index']==raw['job']['source_index']==1 and q['AlphaMode']==am and q['ExportAlpha'] and q['MarkIn']==q['MarkOut']==86400 and q['OutputFilename']==Path(new['file']).name and q['VideoCodec']=='RGB float (ZIP)' and j['lut']=='ZZ_S19_769a014c_AlphaAP1DI_r1.dctl' and new['completion']=={'JobStatus':'Complete','CompletionPercentage':100},'unmatched capture')
        a,x,y=map(read,(raw,old,new)); z[k]=(a,x,y)
        need(bytes_of(a,'A')==bytes_of(x,'A')==bytes_of(y,'A'),'alpha did not survive unchanged')
        bit[k]={'whole_frame_rgba_words_equal':bytes_of(x,RGBA)==bytes_of(y,RGBA),'alpha_words_exact':True,'rgb_max_abs_vs_fx':{c:max(abs(v-w) for v,w in zip(x[c],y[c],strict=True)) for c in 'RGB'}}
        receipts[k]=[raw['sha256'],old['sha256'],new['sha256']]
    a,_,_=z['premult']; A=a['A']; s=z['straight'][0]; need(bytes_of(a,'A')==bytes_of(s,'A'),'source alpha mismatch')
    row=range(135*W,136*W); sets={'zero':[i for i in row if A[i]==0],'tiny_below_1e-7':[i for i in row if 0<A[i]<1e-7],'tiny_from_1e-7':[i for i in row if 1e-7<=A[i]<.01],'partial_ge_.01':[i for i in row if .01<=A[i]<1],'opaque':[i for i in row if A[i]==1]}
    result={'scope':'Same input and export as SC34, frame 1; fixed direct only. Host internal position and exact alpha cutoff not inferred.','receipt_sha256':[sha(OLD),sha(NEW)],'exr_sha256_off_fx_direct':receipts,'full_frame':bit,'center_row':{}}
    for index,name in ((1,'ResolveFX'),(2,'Direct')):
        x,y=z['straight'][index],z['premult'][index]; why=result['center_row'][name]={}
        for k,idx in sets.items():
            need(idx,'empty alpha band'); b=why[k]={'n':len(idx),'A_range':[min(A[i] for i in idx),max(A[i] for i in idx)]}
            b['straight_max_abs_RGB']=max(abs(x[c][i]) for i in idx for c in 'RGB'); b['premult_max_abs_RGB']=max(abs(y[c][i]) for i in idx for c in 'RGB')
            if k=='zero': continue
            b['unassociated_residual_normal']=max(abs(y[c][i]-f32(A[i]*x[c][i]))/A[i] for i in idx for c in 'RGB')
            b['unassociated_residual_grade_associated_then_multiply']=max(abs(y[c][i]-f32(A[i]*t))/A[i] for i in idx for c,t in zip('RGB',ap1di(tuple(a[c][i] for c in 'RGB')),strict=True))
    with dst.open('x',encoding='utf8') as f: json.dump(result,f,allow_nan=False,indent=2)
    print(json.dumps(result['full_frame'])); print(json.dumps(result['center_row'],indent=2)); return result

if __name__=='__main__': run(Path(sys.argv[1]))
