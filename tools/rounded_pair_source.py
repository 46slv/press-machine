"""CUDA RN and portable strict-mode compensated pair source."""
RN_PAIR_SOURCE = r'''
// Pair arithmetic depends on each binary32 rounding boundary. CUDA may
// contract ordinary expressions (and fast math may approximate division).
// Explicit round-to-nearest intrinsics preserve the error-free transforms.
__DEVICE__ float pm_rn_add(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fadd_rn(a,b);
#else
    volatile float result=a+b; return result;
#endif
}
__DEVICE__ float pm_rn_sub(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fsub_rn(a,b);
#else
    volatile float result=a-b; return result;
#endif
}
__DEVICE__ float pm_rn_mul(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fmul_rn(a,b);
#else
    volatile float result=a*b; return result;
#endif
}
__DEVICE__ float pm_rn_div(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fdiv_rn(a,b);
#else
    volatile float result=a/b; return result;
#endif
}
__DEVICE__ float pm_rn_fma(float a,float b,float c) {
#ifdef DEVICE_IS_CUDA
    return __fmaf_rn(a,b,c);
#else
    return _fmaf(a,b,c);
#endif
}
__DEVICE__ float2 pm_pair(float x) { return make_float2(x, 0.0f); }
__DEVICE__ float2 pm_pair_add(float2 a, float2 b) {
    float s = pm_rn_add(a.x,b.x);
    float v = pm_rn_sub(s,a.x);
    float e = pm_rn_add(pm_rn_add(pm_rn_add(pm_rn_sub(a.x,pm_rn_sub(s,v)),pm_rn_sub(b.x,v)),a.y),b.y);
    float h = pm_rn_add(s,e);
    return make_float2(h,pm_rn_sub(e,pm_rn_sub(h,s)));
}
__DEVICE__ float2 pm_pair_neg(float2 a) { return make_float2(-a.x,-a.y); }
__DEVICE__ float2 pm_pair_mul(float2 a, float2 b) {
    float p = pm_rn_mul(a.x,b.x);
    float e = pm_rn_add(pm_rn_add(pm_rn_add(pm_rn_fma(a.x,b.x,-p),pm_rn_mul(a.x,b.y)),pm_rn_mul(a.y,b.x)),pm_rn_mul(a.y,b.y));
    float h = pm_rn_add(p,e);
    return make_float2(h,pm_rn_sub(e,pm_rn_sub(h,p)));
}
__DEVICE__ float2 pm_pair_div(float2 a, float2 b) {
    float q = pm_rn_div(a.x,b.x);
    float2 r = pm_pair_add(a,pm_pair_neg(pm_pair_mul(b,pm_pair(q))));
    return pm_pair_add(pm_pair(q),pm_pair(pm_rn_div(pm_rn_add(r.x,r.y),b.x)));
}
'''
