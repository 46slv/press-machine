// Diagnostic only: no input reads, no blend, and no adjustable state.
extern "C" __global__ void sat19_opaque_8125(char* dst, long long pitch,
    int x0, int y0, int w, int h) {
  const int x=int(blockIdx.x*blockDim.x+threadIdx.x);
  const int y=int(blockIdx.y*blockDim.y+threadIdx.y);
  if (x>=w || y>=h) return;
  float* p=reinterpret_cast<float*>(dst+static_cast<long long>(y+y0)*pitch)+4*(x+x0);
  p[0]=8.125f; p[1]=8.125f; p[2]=0.375f; p[3]=1.0f;
}
