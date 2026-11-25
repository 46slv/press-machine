// Compile the standalone DCTL itself, through the exact user-facing RGB entry.
#include <cmath>
struct float2 { float x,y; };
struct float3 { float x,y,z; };
inline float2 make_float2(float x,float y) { return {x,y}; }
inline float3 make_float3(float x,float y,float z) { return {x,y,z}; }
inline float _fabs(float x) { return std::fabs(x); }
inline float _fmaxf(float a,float b) { return std::fmax(a,b); }
inline float _fminf(float a,float b) { return std::fmin(a,b); }
inline float _sqrtf(float x) { return std::sqrt(x); }
inline float _powf(float x,float y) { return std::pow(x,y); }
inline float _log2f(float x) { return std::log2(x); }
inline float _floorf(float x) { return std::floor(x); }
inline float _fmaf(float a,float b,float c) { return std::fma(a,b,c); }
#define __DEVICE__ inline
#define DCTLUI_SLIDER_FLOAT float
#define DCTLUI_CHECK_BOX int
#define DCTLUI_COMBO_BOX int
#define DEFINE_UI_PARAMS(name,label,type,initial,...) type name=initial;
#include DCTL_FILE
extern "C" __declspec(dllexport) void cpu_transform(const float* rgb,const float* sliders,const int* controls,float* out) {
    pm_threshold=sliders[0]; pm_compression=sliders[1]; pm_softness=sliders[2];
    pm_comp_bypass=controls[0]; pmi_ig=controls[1]; pmi_it=controls[2];
    pmi_og=controls[3]; pmi_ot=controls[4];
    float3 v=transform(controls[5],controls[6],controls[7],controls[8],rgb[0],rgb[1],rgb[2]);
    out[0]=v.x;out[1]=v.y;out[2]=v.z;
}
