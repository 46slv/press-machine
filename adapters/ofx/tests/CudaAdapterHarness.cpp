#include "../generated/ParameterValues.hpp"
#include <stdexcept>
void runCuda(void*,const void*,void*,long long,long long,int,int,int,int,int,int,int,int,int,int,int,const pm::Parameters&);
extern "C" __declspec(dllexport) int pm_cuda_adapter(
 void* stream,const void* src,void* dst,long long sp,long long dp,
 int sx1,int sy1,int sx2,int sy2,int dx1,int dy1,
 int rx1,int ry1,int rx2,int ry2,int premult,const double*values){
 try{runCuda(stream,src,dst,sp,dp,sx1,sy1,sx2,sy2,dx1,dy1,rx1,ry1,rx2,ry2,premult,fromValues(values));return 0;}
 catch(const std::exception&){return 1;}
}
