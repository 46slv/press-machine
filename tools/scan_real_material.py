"""Offline full-pixel source-model comparison; requires existing NumPy/FFmpeg.

Does not certify the files' colour metadata or any Resolve/GPU output.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o

SOURCE_XYZ=np.array(((.4123907992659595,.35758433938387796,.1804807884018343),
                     (.21263900587151036,.7151686787677559,.07219231536073371),
                     (.01933081871559185,.11919477979462599,.9505321522496607)))


def encode(x):
    with np.errstate(invalid='ignore'):
        return np.where(x<=.00262409,x*10.44426855,(np.log2(x+.0075)+7)*.07329248)


def transform(lab,continuous):
    c=np.hypot(lab[:,1],lab[:,2]);l=np.abs(lab[:,0])
    eligible=(c>1e-7)&(continuous|(lab[:,0]>1e-6))
    with np.errstate(divide='ignore',invalid='ignore'):
        s=100*c/l
        out_s=np.where(s<=20,s,np.where(s<30,s-.75*(s-20)**2/20,25+.25*(s-25)))
        scale=np.where(l==0,.25,out_s/s)
    scale=np.where(eligible,scale,1.)
    out=lab.copy();out[:,1:]*=scale[:,None]
    root=out@np.array(o.LAB_ROOT).T
    linear=(root**3)@np.array(o.LMS_XYZ).T@np.array(o.XYZ_DWG).T
    return encode(linear),eligible,scale


def measure(source,ffmpeg):
    raw=subprocess.check_output([ffmpeg,'-v','error','-i',str(source),'-frames:v','1','-f','rawvideo','-pix_fmt','gbrpf32le','-'])
    frame=np.frombuffer(raw,dtype='<f4').reshape(3,2160,4096)
    rgb=np.stack((frame[2].ravel(),frame[0].ravel(),frame[1].ravel()),axis=1)
    result={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pixels':len(rgb),
            'source_rgb_min':float(rgb.min()),'source_rgb_max':float(rgb.max()),'negative_rgb_pixels':int(np.any(rgb<0,axis=1).sum()),
            'L_guard_nonblack':0,'negative_lms_nonblack':0,'min_L_nonblack':float('inf'),'positive_domain_max_model_difference':0.,
            'new_domain_max_encoded_difference_from_r2':0.,'changed_pixels_above_1e_4_encoded':0,'new_nonfinite':0}
    for i in range(0,len(rgb),100000):
        chunk=rgb[i:i+100000].astype('float64');nonblack=np.any(chunk!=0,axis=1)
        xyz=chunk@SOURCE_XYZ.T;lms=xyz@np.array(o.XYZ_LMS).T;lab=np.cbrt(lms)@np.array(o.ROOT_LAB).T
        guard=(lab[:,0]<=1e-6)&nonblack
        result['L_guard_nonblack']+=int(guard.sum());result['negative_lms_nonblack']+=int((np.any(lms<0,axis=1)&nonblack).sum())
        result['min_L_nonblack']=min(result['min_L_nonblack'],float(lab[nonblack,0].min()))
        a,eligible,scale=transform(lab,False);b,_,new_scale=transform(lab,True)
        original=encode(xyz@np.array(o.XYZ_DWG).T)
        a=np.where((eligible&(scale!=1))[:,None],a,original)
        b=np.where((new_scale!=1)[:,None],b,original)
        delta=np.max(np.abs(a-b),axis=1)
        positive=lab[:,0]>1e-6
        result['positive_domain_max_model_difference']=max(result['positive_domain_max_model_difference'],float(delta[positive].max(initial=0)))
        result['new_domain_max_encoded_difference_from_r2']=max(result['new_domain_max_encoded_difference_from_r2'],float(delta[guard].max(initial=0)))
        result['changed_pixels_above_1e_4_encoded']+=int((delta>1e-4).sum())
        result['new_nonfinite']+=int((~np.all(np.isfinite(b),axis=1)).sum())
    result['L_guard_percentage']=100*result['L_guard_nonblack']/result['pixels']
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--ffmpeg',required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result={'scope':'Offline double source-model, T25/C75/P20. Assumed scene-linear Rec.709 per existing source documentation; no new embedded metadata confirmation or Resolve execution.',
            'sources':[measure(args.root/(name+'.exr'),args.ffmpeg) for name in ('05_3a_01105','06_1b_00245')]}
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
