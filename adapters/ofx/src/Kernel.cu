#include "../generated/PixelCore.hpp"
extern "C" __global__ void PressMachineKernel(
 const char* src,char* dst,long long sp,long long dp,
 int sx1,int sy1,int sx2,int sy2,int dx1,int dy1,
 int rx1,int ry1,int rx2,int ry2,int premult,pm::Parameters p){
 const int x=rx1+blockIdx.x*blockDim.x+threadIdx.x;
 const int y=ry1+blockIdx.y*blockDim.y+threadIdx.y;
 if(x>=rx2||y>=ry2)return;
 float* out=(float*)(dst+(long long)(y-dy1)*dp)+(x-dx1)*4;
 if(x<sx1||x>=sx2||y<sy1||y>=sy2){for(int c=0;c<4;++c)out[c]=0.0f;return;}
 const float* in=(const float*)(src+(long long)(y-sy1)*sp)+(x-sx1)*4;
 pm::pixel(p,in,out,premult);
}
