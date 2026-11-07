"""Actual-source CUDA regression under four optimizer modes; not host QA."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from reference import oracle as o
from tools import cuda_probe as p
from tools import scalar_measure as sm
from tools.cuda_vectors import extra_pixels

SCALAR_KERNEL=r'''
extern "C" __global__ void pm_scalar(const float* input,float* output,int count) {
 int i=blockIdx.x*blockDim.x+threadIdx.x;
 if(i>=count)return;
 output[3*i]=pm_transfer(input[4*i],input[4*i+1],input[4*i+2],input[4*i+3]);
 output[3*i+1]=0.f; output[3*i+2]=0.f;
}
'''


def pixel_result(actual,expected):
    finite=np.all(np.isfinite(actual),axis=1)
    error=np.max(np.abs(actual.astype(float)-expected),axis=1)/np.maximum(1,np.max(np.abs(expected),axis=1))
    worst=int(np.argmax(error))
    return {'count':len(actual),'nonfinite':int(np.sum(~finite)),
            'outside':int(np.sum(error>2**-13)),'max_normalized_error':float(error[worst]),
            'worst_index':worst,'worst_actual':actual[worst].tolist(),'worst_expected':expected[worst].tolist()}

def scalar_result(actual,cases):
    data=np.asarray([case for _,case in cases],dtype=np.float32)
    expected=np.array([o.transfer(*case) for _,case in cases],dtype=float)
    groups=np.array([group for group,_ in cases])
    error=np.abs(actual.astype(float)-expected)/np.maximum(1,np.abs(expected))
    zero=data[:,2]==0
    decreases=np.flatnonzero((groups[1:]==groups[:-1])&(actual[1:]<actual[:-1]))+1
    examples=[{'previous':cases[i-1], 'current':cases[i],
               'actual':[float(actual[i-1]),float(actual[i])]} for i in decreases[:8]]
    return {'decrease_examples':examples,'count':len(actual),'nonfinite':int(np.sum(~np.isfinite(actual))),
            'outside':int(np.sum(error>2**-23)),'max_normalized_error':float(np.max(error)),
            'boost':int(np.sum(actual>data[:,0])),'negative':int(np.sum(actual<0)),
            'local_decreases':int(np.sum((groups[1:]==groups[:-1])&(actual[1:]<actual[:-1]))),
            'C0_identity_failures':int(np.sum(actual[zero].view('u4')!=data[zero,0].copy().view('u4')))}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    (p.ROOT/'build').mkdir(exist_ok=True)
    source=(p.ROOT/'dctl/PressMachine_R2.dctl').read_text()
    extras=np.array(extra_pixels(),dtype=np.float32)
    expected=np.array([o.apply(tuple(map(float,rgb)),25.,75.,20.).rgb for rgb in extras],dtype=float)
    cases=list(sm.expanded_cases(sm.expanded_states()))+[(g+20000,c) for g,c in sm.tail_cases()]
    scalars=np.array([case for _,case in cases],dtype=np.float32)
    with gzip.open(p.ROOT/'evidence/cuda-rounding-20261107/host-numeric-fixture.json.gz','rt') as f:
        fixture=json.load(f)
    host_input=np.array([r['rgba'][:3] for r in fixture['records']],dtype=np.float32)
    special=np.array([[o.from_bits(0x7fc12345),-0.,float('inf')],
                      [float('-inf'),1.,-0.]],dtype=np.float32)
    identity=np.concatenate((host_input,extras,special))
    cuda=p.Cuda()
    report={'scope':'Standalone same-GPU actual-source stress, NOT Resolve qualification',
            'source_sha256':p.sha(p.ROOT/'dctl/PressMachine_R2.dctl'),
            'device':cuda.info,'extra_seed':120220261110,
            'extra_inputs_sha256_le_f32':hashlib.sha256(extras.tobytes()).hexdigest(),
            'scalar_inputs_sha256_le_f32':hashlib.sha256(scalars.tobytes()).hexdigest(),'modes':{}}
    try:
        for name,options in (('fmad_true',['--fmad=true']),('fmad_false',['--fmad=false']),
                             ('fast_math',['--use_fast_math']),('fast_no_fmad',['--use_fast_math','--fmad=false'])):
            ptx,opts=cuda.compile(p.PRELUDE+source+p.KERNEL+SCALAR_KERNEL,options,'stress-'+name)
            pixels=pixel_result(cuda.run(ptx,extras),expected)
            scalar=scalar_result(cuda.run(ptx,scalars,kernel='pm_scalar')[:,0],cases)
            # T's exact zero bits must not confuse positive subnormal T with zero.
            endpoint_cases=np.array([(o.from_bits(i),o.from_bits(16),100.,soft)
                                     for soft in (0.,100.) for i in range(1,9)],dtype=np.float32)
            endpoint=cuda.run(ptx,endpoint_cases,kernel='pm_scalar')[:,0]
            threshold_check={'count':len(endpoint),'identity_word_failures':int(np.sum(
                endpoint.view('u4')!=endpoint_cases[:,0].copy().view('u4')))}
            report['modes'][name]={'options':opts,'pixels':pixels,'scalar':scalar,
                                  'subnormal_T_identity':threshold_check}
            print(name,json.dumps({'pixels':pixels,'scalar':scalar}),flush=True)
        report['identity']={}
        for name,prelude in (('C0',p.PRELUDE.replace('pm_compression=75.f','pm_compression=0.f')),
                             ('bypass',p.PRELUDE.replace('pm_bypass=0.f','pm_bypass=1.f'))):
            ptx,_=cuda.compile(prelude+source+p.KERNEL,['--use_fast_math'],'identity-'+name)
            actual=cuda.run(ptx,identity)
            report['identity'][name]={'count':len(identity),'word_failures':int(np.sum(actual.view('u4')!=identity.view('u4')))}
    finally:cuda.close()
    report['owned_context_destroyed']=True
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    failed=any(v['pixels']['nonfinite'] or v['pixels']['outside'] or
               any(v['scalar'][k] for k in ('nonfinite','outside','boost','negative','local_decreases','C0_identity_failures'))
               for v in report['modes'].values()) or any(
                   v['subnormal_T_identity']['identity_word_failures'] for v in report['modes'].values()) or any(v['word_failures'] for v in report['identity'].values())
    print('FAILED' if failed else 'PASS',flush=True)
    raise SystemExit(int(failed))

if __name__=='__main__':main()
