"""Bounded standalone CUDA execution of the actual DCTL, never Resolve QA.

Uses the already-installed, signed Resolve NVRTC and NVIDIA driver. No install,
GPU setting change, GUI, rendering, network, or other process termination.
"""
import argparse
import ctypes as c
import hashlib
import gzip
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
RESOLVE=Path('C:/Program Files/Blackmagic Design/DaVinci Resolve')
PRELUDE=r'''
struct pm_vec2 { float x,y; };
struct pm_vec3 { float x,y,z; };
#define float2 pm_vec2
#define float3 pm_vec3
#define make_float2 pm_make_float2
#define make_float3 pm_make_float3
__device__ pm_vec2 make_float2(float x,float y){pm_vec2 v={x,y};return v;}
__device__ pm_vec3 make_float3(float x,float y,float z){pm_vec3 v={x,y,z};return v;}
#define __DEVICE__ __device__ __forceinline__
#define DEVICE_IS_CUDA 1
#define DEFINE_UI_PARAMS(...)
__device__ float pm_threshold=25.f;
__device__ float pm_compression=75.f;
__device__ float pm_softness=20.f;
__device__ float pm_bypass=0.f;
#define _fabs fabsf
#define _powf powf
#define _sqrtf sqrtf
#define _log2f log2f
#define _fmaf fmaf
#define _floorf floorf
#define _fmaxf fmaxf
'''
KERNEL=r'''
extern "C" __global__ void pm_run(const float* input,float* output,int count){
 int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i>=count)return;
 pm_vec3 out=transform(1,1,0,0,input[3*i],input[3*i+1],input[3*i+2]);
 output[3*i]=out.x;output[3*i+1]=out.y;output[3*i+2]=out.z;
}
extern "C" __global__ void pm_stages(const float* input,float* output,int count){
 int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i>=count)return;
 pm_vec3 v=make_float3(input[3*i],input[3*i+1],input[3*i+2]);
 pm_vec2 x=pm_precise_decode(v.x),y=pm_precise_decode(v.y),z=pm_precise_decode(v.z);
 pm_vec3 linear=make_float3(pm_decode(v.x),pm_decode(v.y),pm_decode(v.z));
 pm_vec3 fast=pm_xyz_lms(pm_dwg_xyz(linear));
 pm_vec3 precise=pm_precise_lms(v);
 pm_vec3 lms=pm_condition_lms(v,fast);
 pm_vec3 lab=pm_root_lab(make_float3(pm_cbrt(lms.x),pm_cbrt(lms.y),pm_cbrt(lms.z)));
 float chroma=_sqrtf(lab.y*lab.y+lab.z*lab.z);
 float sat=100.f*(chroma/lab.x);
 float out_sat=pm_transfer(sat,25.f,75.f,20.f);
 float values[18]={x.x,x.y,y.x,y.y,z.x,z.y,fast.x,fast.y,fast.z,
 precise.x,precise.y,precise.z,lab.x,lab.y,lab.z,sat,out_sat,out_sat/sat};
 for(int k=0;k<18;k++)output[18*i+k]=values[k];
}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Cuda:
    def __init__(self):
        self.cookie=os.add_dll_directory(str(RESOLVE))
        self.builtins=c.CDLL(str(RESOLVE/'nvrtc-builtins64_128.dll'))
        self.nv=c.CDLL(str(RESOLVE/'nvrtc64_120_0.dll'))
        self.driver=c.WinDLL('nvcuda.dll')
        def bind(lib,name,args):
            fn=getattr(lib,name);fn.argtypes=args;fn.restype=c.c_int
            return fn
        p=c.c_void_p; u=c.c_uint; ip=c.POINTER(c.c_int)
        self.init=bind(self.driver,'cuInit',[u])
        self.device_count=bind(self.driver,'cuDeviceGetCount',[ip])
        self.device_get=bind(self.driver,'cuDeviceGet',[ip,c.c_int])
        self.device_name=bind(self.driver,'cuDeviceGetName',[c.c_char_p,c.c_int,c.c_int])
        self.attribute=bind(self.driver,'cuDeviceGetAttribute',[ip,c.c_int,c.c_int])
        self.driver_version=bind(self.driver,'cuDriverGetVersion',[ip])
        self.ctx_create=bind(self.driver,'cuCtxCreate_v2',[c.POINTER(p),u,c.c_int])
        self.ctx_destroy=bind(self.driver,'cuCtxDestroy_v2',[p])
        self.module_load=bind(self.driver,'cuModuleLoadData',[c.POINTER(p),p])
        self.module_unload=bind(self.driver,'cuModuleUnload',[p])
        self.function=bind(self.driver,'cuModuleGetFunction',[c.POINTER(p),p,c.c_char_p])
        self.alloc=bind(self.driver,'cuMemAlloc_v2',[c.POINTER(c.c_uint64),c.c_size_t])
        self.free=bind(self.driver,'cuMemFree_v2',[c.c_uint64])
        self.htod=bind(self.driver,'cuMemcpyHtoD_v2',[c.c_uint64,p,c.c_size_t])
        self.dtoh=bind(self.driver,'cuMemcpyDtoH_v2',[p,c.c_uint64,c.c_size_t])
        self.launch=bind(self.driver,'cuLaunchKernel',[p,u,u,u,u,u,u,u,p,c.POINTER(p),c.POINTER(p)])
        self.synchronize=bind(self.driver,'cuCtxSynchronize',[])
        self.create_program=bind(self.nv,'nvrtcCreateProgram',[c.POINTER(p),c.c_char_p,c.c_char_p,c.c_int,p,p])
        self.compile_program=bind(self.nv,'nvrtcCompileProgram',[p,c.c_int,c.POINTER(c.c_char_p)])
        self.log_size=bind(self.nv,'nvrtcGetProgramLogSize',[p,c.POINTER(c.c_size_t)])
        self.log_get=bind(self.nv,'nvrtcGetProgramLog',[p,p])
        self.ptx_size=bind(self.nv,'nvrtcGetPTXSize',[p,c.POINTER(c.c_size_t)])
        self.ptx_get=bind(self.nv,'nvrtcGetPTX',[p,p])
        self.destroy_program=bind(self.nv,'nvrtcDestroyProgram',[c.POINTER(p)])
        self.nv_version=bind(self.nv,'nvrtcVersion',[ip,ip])
        self.check(self.init(0),'cuInit')
        n=c.c_int();self.check(self.device_count(c.byref(n)),'cuDeviceGetCount')
        targets=[]
        for i in range(n.value):
            device=c.c_int();self.check(self.device_get(c.byref(device),i),'cuDeviceGet')
            name=c.create_string_buffer(256)
            self.check(self.device_name(name,256,device),'cuDeviceGetName')
            if name.value.decode()=='NVIDIA GeForce RTX 3070 Ti':
                targets.append((i,device.value,name.value.decode()))
        if len(targets)!=1:
            raise RuntimeError(('exact compute target not unique',targets))
        self.index,self.device,self.name=targets[0]
        self.ctx=p()
        self.check(self.ctx_create(c.byref(self.ctx),0,self.device),'cuCtxCreate')
        major=c.c_int();minor=c.c_int();driver=c.c_int();nvmajor=c.c_int();nvminor=c.c_int()
        self.check(self.attribute(c.byref(major),75,self.device),'major')
        self.check(self.attribute(c.byref(minor),76,self.device),'minor')
        self.check(self.driver_version(c.byref(driver)),'driver version')
        self.check(self.nv_version(c.byref(nvmajor),c.byref(nvminor)),'NVRTC version')
        self.info={'device_index':self.index,'name':self.name,
                   'compute_capability':[major.value,minor.value],
                   'driver_API_version':driver.value,'nvrtc_version':[nvmajor.value,nvminor.value],
                   'nvrtc_path':str(RESOLVE/'nvrtc64_120_0.dll'),
                   'nvrtc_sha256':sha(RESOLVE/'nvrtc64_120_0.dll')}
        self.arch=f'compute_{major.value}{minor.value}'

    def check(self,code,where):
        if code!=0:raise RuntimeError((where,code))

    def compile(self,source,options,name):
        program=c.c_void_p()
        self.check(self.create_program(c.byref(program),source.encode(),b'actual_dctl.cu',0,None,None),'nvrtcCreateProgram')
        try:
            opts=['--gpu-architecture='+self.arch,'--std=c++17',*options]
            array_opts=(c.c_char_p*len(opts))(*(x.encode() for x in opts))
            code=self.compile_program(program,len(opts),array_opts)
            size=c.c_size_t();self.check(self.log_size(program,c.byref(size)),'nvrtc log size')
            log=c.create_string_buffer(size.value)
            self.check(self.log_get(program,log),'nvrtc log')
            (ROOT/'build'/f'cuda-{name}.log').write_text(log.value.decode(errors='replace'),encoding='utf-8')
            if code:raise RuntimeError(('nvrtcCompileProgram',code,log.value.decode(errors='replace')[:2000]))
            self.check(self.ptx_size(program,c.byref(size)),'nvrtc ptx size')
            ptx=c.create_string_buffer(size.value);self.check(self.ptx_get(program,ptx),'nvrtc ptx')
            (ROOT/'build'/f'cuda-{name}.ptx').write_bytes(ptx.value)
            return ptx.value,opts
        finally:
            self.check(self.destroy_program(c.byref(program)),'nvrtcDestroyProgram')

    def run(self,ptx,inputs,kernel='pm_run',stride=3):
        data=np.asarray(inputs,dtype=np.float32,order='C')
        output=np.empty((len(data),stride),dtype=np.float32)
        di=c.c_uint64();do=c.c_uint64();module=c.c_void_p();loaded=False
        try:
            self.check(self.alloc(c.byref(di),data.nbytes),'cuMemAlloc input')
            self.check(self.alloc(c.byref(do),output.nbytes),'cuMemAlloc output')
            self.check(self.htod(di,data.ctypes.data,data.nbytes),'cuMemcpyHtoD')
            ptxbuf=c.create_string_buffer(ptx)
            self.check(self.module_load(c.byref(module),ptxbuf),'cuModuleLoadData');loaded=True
            fn=c.c_void_p();self.check(self.function(c.byref(fn),module,kernel.encode()),'cuModuleGetFunction')
            count=c.c_int(len(data))
            args=(c.c_void_p*3)(c.addressof(di),c.addressof(do),c.addressof(count))
            self.check(self.launch(fn,(len(data)+127)//128,1,1,128,1,1,0,None,args,None),'cuLaunchKernel')
            self.check(self.synchronize(),'cuCtxSynchronize')
            self.check(self.dtoh(output.ctypes.data,do,output.nbytes),'cuMemcpyDtoH')
            return output
        finally:
            if loaded:self.check(self.module_unload(module),'cuModuleUnload')
            if di.value:self.check(self.free(di),'cuMemFree input')
            if do.value:self.check(self.free(do),'cuMemFree output')

    def close(self):
        self.check(self.ctx_destroy(self.ctx),'cuCtxDestroy')
        self.cookie.close()


def host_pixels(host,manifest):
    path=next((host/'numeric-c75').glob('*.exr'))
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-frames:v','1',
        '-f','rawvideo','-pix_fmt','gbrapf32le','pipe:1'],check=True,stdout=subprocess.PIPE).stdout
    pixels=np.frombuffer(raw,dtype='<f4').reshape(4,manifest['height'],manifest['width'])
    return np.array([[pixels[2,r['y'],r['x']],pixels[0,r['y'],r['x']],pixels[1,r['y'],r['x']]]
                     for r in manifest['records']],dtype=np.float32)


def analyze(actual,expected,records,host):
    error=np.max(np.abs(actual.astype(float)-expected),axis=1)/np.maximum(1,np.max(np.abs(expected),axis=1))
    result={'nonfinite':int(np.sum(~np.isfinite(actual))),'max_normalized_error':float(np.max(error)),
            'outside_envelope':int(np.sum(error>2**-13)),
            'host_matching_channel_words':int(np.sum(actual.view('u4')==host.view('u4'))),
            'host_total_channel_words':int(actual.size),
            'max_absolute_difference_from_host':float(np.max(np.abs(actual.astype(float)-host.astype(float)))),
            'regression_actual':actual[0].tolist(),'groups':{}}
    for group in sorted({r['group'] for r in records}):
        ix=[i for i,r in enumerate(records) if r['group']==group]
        worst=max(ix,key=lambda i:error[i])
        result['groups'][group]={'count':len(ix),'outside':int(np.sum(error[ix]>2**-13)),
            'max_error':float(error[worst]),'worst_index':worst,'actual':actual[worst].tolist()}
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--host',type=Path)
    parser.add_argument('--fixture',type=Path,default=ROOT/'evidence/cuda-rounding-20261107/host-numeric-fixture.json.gz')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source',type=Path,default=ROOT/'dctl/PressMachine_R2.dctl')
    args=parser.parse_args()
    (ROOT/'build').mkdir(exist_ok=True)
    if args.host:
        manifest=json.loads((args.host/'numeric_manifest.json').read_text())
        records=manifest['records']
        host=host_pixels(args.host,manifest)
        manifest_hash=sha(args.host/'numeric_manifest.json')
    else:
        with gzip.open(args.fixture,'rt',encoding='utf-8') as file:
            manifest=json.load(file)
        records=manifest['records']
        host=np.array([r['old_host_rgb'] for r in records],dtype=np.float32)
        manifest_hash=manifest['original_manifest_sha256']
    inputs=np.array([r['rgba'][:3] for r in records],dtype=np.float32)
    expected=np.array([r['expected_c75']['rgb'] for r in records],dtype=float)
    source=PRELUDE+'\n'+args.source.read_text(encoding='utf-8')+'\n'+KERNEL
    cuda=Cuda()
    try:
        report={'scope':'Standalone CUDA actual-source probe, NOT Resolve qualification',
                'device':cuda.info,'dctl_sha256':sha(args.source),
                'manifest_sha256':manifest_hash,
                'count':len(records),'modes':{}}
        for name,options in (('fmad_true',['--fmad=true']),('fmad_false',['--fmad=false']),
                             ('fast_math',['--use_fast_math']),('fast_no_fmad',['--use_fast_math','--fmad=false'])):
            ptx,opts=cuda.compile(source,options,name)
            actual=cuda.run(ptx,inputs)
            result=analyze(actual,expected,records,host)
            result['options']=opts;result['ptx_sha256']=hashlib.sha256(ptx).hexdigest()
            selected=sorted({0,*[g['worst_index'] for g in result['groups'].values()]})
            stage=cuda.run(ptx,inputs[selected],kernel='pm_stages',stride=18)
            result['diagnostic_stage_order']='decode hi/lo R/G/B; fast LMS; precise LMS; Lab; S; outS; scale'
            result['diagnostic_stages']={str(i):row.tolist() for i,row in zip(selected,stage)}
            report['modes'][name]=result
            print(name,result['outside_envelope'],result['max_normalized_error'],
                  result['host_matching_channel_words'],'/',result['host_total_channel_words'],flush=True)
    finally:
        cuda.close()
    report['owned_context_destroyed']=True
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'device':report['device'],'source':report['dctl_sha256'],
                      'output':str(args.output),'context_destroyed':True},indent=2))


if __name__=='__main__':
    main()
