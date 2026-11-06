"""Bounded CPU microbenchmark, never a Resolve/GPU/4K performance result."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.build_native import ROOT,build

CPP=r'''
#include <cmath>
#include <chrono>
#include <cstdio>
struct float2 { float x,y; };
struct float3 { float x,y,z; };
static float2 make_float2(float x,float y){return{x,y};}
static float3 make_float3(float x,float y,float z){return{x,y,z};}
#define __DEVICE__ static
#define DEFINE_UI_PARAMS(name,label,kind,value,...) static float name=value;
#define _fabs std::fabs
#define _powf std::pow
#define _sqrtf std::sqrt
#define _log2f std::log2
#define _fmaf std::fma
namespace baseline {
#include "@BASE@"
}
namespace stable {
#include "@STABLE@"
}
namespace proposed {
#include "@PROPOSAL@"
}
static float3 inputs[256];
static volatile float sink=0;
template<typename F>double bench(F fn){
 auto start=std::chrono::steady_clock::now();float acc=0;
 for(int i=0;i<1000000;i++){const auto v=inputs[i%256];auto o=fn(1,1,0,0,v.x,v.y,v.z);acc+=o.x+o.y+o.z;}
 sink=acc;return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
}
int main(){
 baseline::pm_compression=stable::pm_compression=proposed::pm_compression=75.f;
 for(int i=0;i<256;i++){float s=(float)i/255.f;inputs[i]=make_float3(baseline::pm_encode(.01f+.19f*s),baseline::pm_encode(.01f+.29f*s),baseline::pm_encode(.9f));}
 for(int r=0;r<5;r++){
   double b,s,p;
   if(r%2==0){b=bench(baseline::transform);s=bench(stable::transform);p=bench(proposed::transform);}
   else{p=bench(proposed::transform);s=bench(stable::transform);b=bench(baseline::transform);}
   printf("%d %.6f %.6f %.6f\n",r,b,s,p);
 }
}
'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    baseline=ROOT/'build/benchmark_baseline.dctl';baseline.parent.mkdir(exist_ok=True)
    baseline.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show','37e0c2ed447e1218dae94ccd6ac7c4aef28eab72:dctl/PressMachine_R2.dctl']))
    source=CPP.replace('@BASE@',baseline.as_posix()).replace('@STABLE@',(ROOT/'dctl/PressMachine_R2.dctl').as_posix()).replace('@PROPOSAL@',(ROOT/'prototypes/PressMachine_ContinuousDomain.dctl').as_posix())
    (ROOT/'build/benchmark.cpp').write_text(source,encoding='utf-8')
    exe=ROOT/'build'/('benchmark_native.exe' if sys.platform=='win32' else 'benchmark_native')
    compiler=build('build/benchmark.cpp',exe)
    rows=[list(map(float,line.split())) for line in subprocess.check_output([str(exe)],text=True).splitlines()]
    medians={name:statistics.median(row[i] for row in rows) for i,name in enumerate(('baseline','r2_stable','continuous'),1)}
    result={'scope':'CPU microbenchmark only; 1,000,000 samples per run, 256 fixed DWG blue-biased inputs, T25/C75/P20. Five runs alternate order. Revision processes negative-L samples that baseline bypasses. No Resolve/GPU/4K/playback claim.',
            'compiler':compiler,'milliseconds':rows,'median_milliseconds':medians,
            'median_ratio_to_baseline':{name:value/medians['baseline'] for name,value in medians.items()}}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
