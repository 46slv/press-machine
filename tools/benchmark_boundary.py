"""A bounded CPU comparison, not GPU/4K or playback evidence."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.build_native import ROOT,build
from tools.generate_precision_candidate import BASE_COMMIT
from tools.qualify import sha

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
#define _floorf std::floor
#define _fmaxf std::fmax
namespace baseline {
#include "@BASE@"
}
namespace repaired {
#include "@CURRENT@"
}
static float3 inputs[256];
static volatile float sink=0;
template<typename F>double bench(F fn){
 auto start=std::chrono::steady_clock::now();float acc=0;
 for(int i=0;i<1000000;i++){const auto v=inputs[i%256];auto o=fn(1,1,0,0,v.x,v.y,v.z);acc+=o.x+o.y+o.z;}
 sink=acc;return std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count();
}
int main(){
 baseline::pm_compression=repaired::pm_compression=75.f;
 for(int i=0;i<256;i++){float u=(float)i/255.f;inputs[i]=make_float3(baseline::pm_encode(.18f*(1-u)),baseline::pm_encode(.18f*(1-u)),baseline::pm_encode(.18f*(1-u)+u));}
 for(int r=0;r<5;r++){
   double b,n;
   if(r%2==0){b=bench(baseline::transform);n=bench(repaired::transform);}
   else{n=bench(repaired::transform);b=bench(baseline::transform);}
   printf("%d %.6f %.6f\n",r,b,n);
 }
}
'''
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    baseline=ROOT/'build/boundary_baseline.dctl'
    baseline.write_bytes(subprocess.check_output(['git','-C',str(ROOT),'show',BASE_COMMIT+':dctl/PressMachine_R2.dctl']))
    source=CPP.replace('@BASE@',baseline.as_posix()).replace('@CURRENT@',(ROOT/'dctl/PressMachine_R2.dctl').as_posix())
    (ROOT/'build/benchmark_boundary.cpp').write_text(source,encoding='utf-8')
    exe=ROOT/'build/benchmark_boundary.exe'
    compiler=build('build/benchmark_boundary.cpp',exe)
    rows=[list(map(float,line.split())) for line in subprocess.check_output([str(exe)],text=True).splitlines()]
    medians={name:statistics.median(row[i] for row in rows) for i,name in enumerate(('baseline','repaired'),1)}
    result={'scope':'CPU only; one million samples, fixed 256-point DWG blue ramp, T25/C75/P20; five alternating-order runs. No Resolve/GPU/4K/playback claim.',
        'source_hashes':{'baseline':sha(baseline),'repaired':sha(ROOT/'dctl/PressMachine_R2.dctl')},
        'compiler':compiler,'milliseconds':rows,'median_milliseconds':medians,
        'repaired_to_baseline_ratio':medians['repaired']/medians['baseline']}
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='compiler'},indent=2))
