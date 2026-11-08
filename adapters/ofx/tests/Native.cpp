#include "../generated/PixelCore.hpp"
#include "../generated/ParameterValues.hpp"
#undef PRESSMACHINE_COLOR_ADAPTER_DCTLH
#undef PRESSMACHINE_HUE_LINEAR_PAIR_DCTLH
#undef PRESSMACHINE_HUE_RAY_FORCE_DCTLH
#undef PRESSMACHINE_CF2_PAIR_DCTLH
#pragma once
#ifdef __CUDACC__
#define PM_DEVICE __device__
#define __DEVICE__ __device__
#define DEVICE_IS_CUDA 1
#define _fabs fabsf
#define _fminf fminf
#define _fmaxf fmaxf
#define _floorf floorf
#define _fmaf fmaf
#define _powf powf
#define _sqrtf sqrtf
#define _log2f log2f
#else
#include <cmath>
#define PM_DEVICE inline
#define __DEVICE__ inline
#define _fabs std::fabs
#define _fminf std::fmin
#define _fmaxf std::fmax
#define _floorf std::floor
#define _fmaf std::fma
#define _powf std::pow
#define _sqrtf std::sqrt
#define _log2f std::log2
#endif

#ifndef __CUDACC__
struct float2{float x,y;};struct float3{float x,y,z;}; inline float2 make_float2(float x,float y){return {x,y};} inline float3 make_float3(float x,float y,float z){return {x,y,z};}
#endif
#define PMUI_DCTLUI_SLIDER_FLOAT(name,value) static thread_local float name=value;
#define PMUI_DCTLUI_CHECK_BOX(name,value) static thread_local int name=value;
#define PMUI_DCTLUI_COMBO_BOX(name,value) static thread_local int name=value;
#define DEFINE_UI_PARAMS(name,label,kind,value,...) PMUI_##kind(name,value)
#define DEFINE_UI_TOOLTIP(...)

namespace original {
// PRESSMACHINE COMMON COLOR TEST CANDIDATE. NATIVE RESEARCH; HOST/GPU QUALIFICATION PENDING.
// Explicit input primaries + transfer -> linear DWG pair -> shared creative core -> output (default follows input).
// Full: Pre -> Hue -> Comp -> Density -> final tonal desat; Density Bypass affects Density only. Standalone Comp Bypass affects Comp only.
DEFINE_UI_PARAMS(pm_pre, Pre Saturation, DCTLUI_SLIDER_FLOAT, 100.0, 0.0, 200.0, 0.1)
DEFINE_UI_PARAMS(pm_hue_angle, Hue Angle, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 360.0, 0.1)
DEFINE_UI_PARAMS(pm_hue_points_index, Hue Points, DCTLUI_COMBO_BOX, 1, { PMIF_POINTS_1, PMIF_POINTS_2, PMIF_POINTS_3, PMIF_POINTS_4, PMIF_POINTS_6 }, { 1, 2, 3, 4, 6 })
DEFINE_UI_PARAMS(pm_hue_compression, Hue Compression, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_threshold, Threshold, DCTLUI_SLIDER_FLOAT, 80.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_compression, Amount %, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_softness, Knee %, DCTLUI_SLIDER_FLOAT, 20.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_sat_skin, Sat Skin Protect, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_density, Density, DCTLUI_SLIDER_FLOAT, 0.0, -300.0, 300.0, 0.1)
DEFINE_UI_PARAMS(pm_chroma, Density Chroma, DCTLUI_SLIDER_FLOAT, 0.0, -100.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_response, Saturation Response, DCTLUI_SLIDER_FLOAT, 2.0, 1.0, 4.0, 0.01)
DEFINE_UI_PARAMS(pm_shadow, Shadow Protect, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_sr, Shadow Range, DCTLUI_SLIDER_FLOAT, 50.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_highlight, Highlight Protect, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_hr, Highlight Range, DCTLUI_SLIDER_FLOAT, 50.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_density_skin, Density Skin Protect, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 100.0, 0.1)
DEFINE_UI_PARAMS(pm_db, Density Bypass, DCTLUI_CHECK_BOX, 0)
DEFINE_UI_PARAMS(pm_sd_t, Shadow Desat Threshold, DCTLUI_SLIDER_FLOAT, 0.0, 0.0, 1.0, 0.001)
DEFINE_UI_PARAMS(pm_sd_k, Shadow Desat Knee, DCTLUI_SLIDER_FLOAT, 0.18, 0.0, 1.0, 0.001)
DEFINE_UI_PARAMS(pm_hd_t, Highlight Desat Threshold, DCTLUI_SLIDER_FLOAT, 1.0, 0.0, 1.0, 0.001)
DEFINE_UI_PARAMS(pm_hd_k, Highlight Desat Knee, DCTLUI_SLIDER_FLOAT, 0.18, 0.0, 1.0, 0.001)
DEFINE_UI_PARAMS(pmi_ig, Input Primaries, DCTLUI_COMBO_BOX, 0, { PMA_DWG_IN, PMA_AWG3_IN, PMA_AWG4_IN, PMA_AP1_IN }, { DWG D65, ARRI Wide Gamut 3 D65, ARRI Wide Gamut 4 D65, ACES AP1 CAT02 })
DEFINE_UI_PARAMS(pmi_it, Input Transfer, DCTLUI_COMBO_BOX, 0, { PMA_DI_IN, PMA_LOGC3_IN, PMA_LOGC4_IN, PMA_ACESCCT_IN, PMA_LINEAR_IN }, { DaVinci Intermediate, LogC3 EI800 Exposure, LogC4 Scene, ACEScct Reversible, Relative Linear })
DEFINE_UI_PARAMS(pmi_og, Output Primaries, DCTLUI_COMBO_BOX, 0, { PMA_SAME_GAMUT_OUT, PMA_DWG_OUT, PMA_AWG3_OUT, PMA_AWG4_OUT, PMA_AP1_OUT }, { Same as Input, DWG D65, ARRI Wide Gamut 3 D65, ARRI Wide Gamut 4 D65, ACES AP1 CAT02 })
DEFINE_UI_PARAMS(pmi_ot, Output Transfer, DCTLUI_COMBO_BOX, 0, { PMA_SAME_TRANSFER_OUT, PMA_DI_OUT, PMA_LOGC3_OUT, PMA_LOGC4_OUT, PMA_ACESCCT_OUT, PMA_LINEAR_OUT }, { Same as Input, DaVinci Intermediate, LogC3 EI800 Exposure, LogC4 Scene, ACEScct Reversible, Relative Linear })
DEFINE_UI_TOOLTIP(Hue Compression, "CF2 projection changes hue and chroma. Zero is unchanged. One point can strongly tint neutrals; two or more keep the center. Angle zero targets BT2020 red.")
DEFINE_UI_TOOLTIP(Threshold, "Lower 0 to 80 maps linearly to the old 0 to 25. Default 80 preserves the old 25. The upper range covers higher saturation. At 100, Comp is disabled. Image response depends on the shot.")
DEFINE_UI_TOOLTIP(Hue Points, "Choose 1, 2, 3, 4 or 6 equally spaced hue directions. Two is an opposite axis. Old fractional slider settings do not transfer automatically.")
DEFINE_UI_TOOLTIP(Density Bypass, "Checked bypasses Density only. Hue, Comp and final desaturation still run.")

// FULL-FEATURE COMMON LINEAR CORE TEST CANDIDATE. UI/TRANSFORM-FREE.

__DEVICE__ int pm_finite(float x) {
    return x == x && _fabs(x) <= 3.402823466e38f;
}
__DEVICE__ int pm_finite3(float3 v) {
    return pm_finite(v.x) && pm_finite(v.y) && pm_finite(v.z);
}
// Pair arithmetic depends on each binary32 rounding boundary. CUDA may
// contract ordinary expressions (and fast math may approximate division).
// Explicit round-to-nearest intrinsics preserve the error-free compensation steps.
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
__DEVICE__ float pm_decode(float v) {
    return v <= 0.02740668f ? v / 10.44426855f :
        _powf(2.0f, v / 0.07329248f - 7.0f) - 0.0075f;
}
__DEVICE__ float pm_encode(float v) {
    return v <= 0.00262409f ? v * 10.44426855f :
        (_log2f(v + 0.0075f) + 7.0f) * 0.07329248f;
}
__DEVICE__ float pm_cbrt(float x) {
    // A general power on negative LMS is invalid. Preserve the real root sign.
#ifdef DEVICE_IS_CUDA
    return cbrtf(x);
#else
    return x < 0.0f ? -_powf(-x, 1.0f / 3.0f) : _powf(x, 1.0f / 3.0f);
#endif
}
__DEVICE__ float3 pm_dwg_xyz(float3 v) {
    return make_float3(
        0.70062239f*v.x + 0.14877482f*v.y + 0.10105872f*v.z,
        0.27411851f*v.x + 0.87363190f*v.y - 0.14775041f*v.z,
       -0.09896291f*v.x - 0.13789533f*v.y + 1.32591599f*v.z);
}
__DEVICE__ float3 pm_xyz_dwg(float3 v) {
    return make_float3(
        1.51667204f*v.x - 0.28147805f*v.y - 0.14696363f*v.z,
       -0.46491710f*v.x + 1.25142378f*v.y + 0.17488461f*v.z,
        0.06484905f*v.x + 0.10913934f*v.y + 0.76141462f*v.z);
}
__DEVICE__ float3 pm_xyz_lms(float3 v) {
    return make_float3(
        0.8190224379967030f*v.x + 0.3619062600528904f*v.y - 0.1288737815209879f*v.z,
        0.0329836539323885f*v.x + 0.9292868615863434f*v.y + 0.0361446663506424f*v.z,
        0.0481771893596242f*v.x + 0.2642395317527308f*v.y + 0.6335478284694309f*v.z);
}
__DEVICE__ float3 pm_root_lab(float3 v) {
    return make_float3(
        0.2104542683093140f*v.x + 0.7936177747023054f*v.y - 0.0040720430116193f*v.z,
        1.9779985324311684f*v.x - 2.4285922420485799f*v.y + 0.4505937096174110f*v.z,
        0.0259040424655478f*v.x + 0.7827717124575296f*v.y - 0.8086757549230774f*v.z);
}
__DEVICE__ float3 pm_lab_root(float3 v) {
    return make_float3(
        v.x + 0.3963377773761749f*v.y + 0.2158037573099136f*v.z,
        v.x - 0.1055613458156586f*v.y - 0.0638541728258133f*v.z,
        v.x - 0.0894841775298119f*v.y - 1.2914855480194092f*v.z);
}
__DEVICE__ float3 pm_lms_xyz(float3 v) {
    return make_float3(
        1.2268798758459243f*v.x - 0.5578149944602171f*v.y + 0.2813910456659647f*v.z,
       -0.0405757452148008f*v.x + 1.1122868032803170f*v.y - 0.0717110580655164f*v.z,
       -0.0763729366746601f*v.x - 0.4214933324022432f*v.y + 1.5869240198367816f*v.z);
}
__DEVICE__ float pm_transfer(float s, float t, float compression, float softness) {
    if (compression == 0.0f) return s;
#ifdef DEVICE_IS_CUDA
    // This exact published endpoint is zero for every finite positive S.
    // Integer classification avoids fast-math comparisons treating a positive
    // subnormal S as zero and incorrectly returning it unchanged.
    int s_word=__float_as_int(s);
    if ((__float_as_int(t) & 0x7fffffff)==0 && compression==100.0f && s_word>0 && s_word<0x7f800000) return 0.0f;
#endif
    float2 hundred = pm_pair(100.0f);
    float2 a = pm_pair_div(pm_pair(compression),hundred);
    float2 q = pm_pair_div(pm_pair_add(hundred,pm_pair(-compression)),hundred);
    float2 half = pm_pair_mul(pm_pair(t),pm_pair_div(pm_pair(softness),hundred));
    float2 lo = pm_pair_add(pm_pair(t),pm_pair_neg(half));
    float2 hi = pm_pair_add(pm_pair(t),half);
    float2 x = pm_pair_add(pm_pair(s),pm_pair_neg(lo));
    if (x.x < 0.0f || (x.x == 0.0f && x.y <= 0.0f)) return s;
    float2 out;
    float2 upper = pm_pair_add(pm_pair(s),pm_pair_neg(hi));
    if (half.x == 0.0f || upper.x > 0.0f || (upper.x == 0.0f && upper.y >= 0.0f)) {
        float2 d = pm_pair_add(pm_pair(s),pm_pair(-t));
        out = pm_pair_add(pm_pair(t),pm_pair_mul(q,d));
    } else {
        float2 numerator = pm_pair_mul(a,pm_pair_mul(x,x));
        float2 reduction = pm_pair_div(numerator,pm_pair_mul(pm_pair(4.0f),half));
        out = pm_pair_add(pm_pair(s),pm_pair_neg(reduction));
    }
    return pm_rn_add(out.x,out.y);
}
// Precision fallback only: the ordinary binary32 path loses the sign/magnitude
// of nearly cancelling LMS sums. Re-evaluate the SAME DI and published matrices
// in float pairs when an LMS component loses at least eight relative bits.
// No epsilon guard, chroma curve, lightness, hue or output weighting is changed.
__DEVICE__ float2 pm_precise_dot3(float2 x,float2 y,float2 z,
                                  float2 a,float2 b,float2 c) {
    return pm_pair_add(pm_pair_add(pm_pair_mul(a,x),pm_pair_mul(b,y)),pm_pair_mul(c,z));
}
__DEVICE__ float2 pm_precise_decode(float v) {
    if (v <= 0.02740668f) return pm_pair_div(pm_pair(v),make_float2(10.444268226623535f, 3.2337646871383185e-07f));
    float2 exponent = pm_pair_add(pm_pair_div(pm_pair(v),make_float2(0.07329247891902924f, 1.0809707573500305e-09f)),pm_pair(-7.0f));
    // Finite decoded values in the log branch have integer exponent >= -7.
    // Existing fast-path range handling owns unrepresentable large values.
    if (exponent.x > 127.0f) return pm_pair(pm_decode(v));
    float n = _floorf(exponent.x);
    if (exponent.x == n && exponent.y < 0.0f) n -= 1.0f;
    float2 r = pm_pair_add(exponent,pm_pair(-n));
    // Degree-16 Taylor polynomial for 2^r, 0 <= r <= 1. Its analytic
    // truncation bound is 2*ln(2)^17/17! < 1.4e-17 before pair rounding.
    float2 y = make_float2(1.3570247350023161e-16f, 5.9873197698431394e-24f);
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(3.132436682680125e-15f, 2.440830304062437e-23f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(6.77872607221866e-14f, 2.826038934825586e-21f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(1.3691489348516273e-12f, -4.9461213028820005e-20f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(2.567843680745252e-11f, -8.139643343159617e-19f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(4.4455383818586824e-10f, -1.0998787340184869e-17f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(7.054911765891347e-09f, -1.4509021906398983e-16f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(1.0178086284895471e-07f, -2.75655776552303e-15f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(1.3215486660556053e-06f, 1.2958825669712268e-14f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(1.5252733646775596e-05f, 1.5728424693304405e-13f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.0001540352968731895f, 7.060626389110425e-12f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.0013333557872101665f, 2.7432677657257543e-11f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.009618128649890423f, 4.5773804191462375e-10f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.05550410971045494f, -1.0456333576769339e-09f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.24022650718688965f, -2.277889404878053e-10f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(0.6931471824645996f, -1.9046542121259336e-09f));
    y = pm_pair_add(pm_pair_mul(y,r),make_float2(1.0f, 0.0f));
    return pm_pair_add(pm_pair_mul(y,pm_pair(_powf(2.0f,n))),pm_pair_neg(make_float2(0.007499999832361937f, 1.6763807009212428e-10f)));
}
__DEVICE__ float3 pm_precise_lms(float3 encoded) {
    float2 x=pm_precise_decode(encoded.x);
    float2 y=pm_precise_decode(encoded.y);
    float2 z=pm_precise_decode(encoded.z);
    float2 a = pm_precise_dot3(x,y,z,make_float2(0.7006223797798157f, 1.022018469853947e-08f),make_float2(0.14877481758594513f, 2.41405495593483e-09f),make_float2(0.1010587215423584f, -1.5423583521467776e-09f));
    float2 b = pm_precise_dot3(x,y,z,make_float2(0.2741185128688812f, -2.8688811326560426e-09f),make_float2(0.8736318945884705f, 5.411529446774921e-09f),make_float2(-0.14775040745735168f, -2.5426483141188783e-09f));
    float2 c = pm_precise_dot3(x,y,z,make_float2(-0.09896291047334671f, 4.733466951734044e-10f),make_float2(-0.13789533078670502f, 7.867050344501081e-10f),make_float2(1.3259159326553345f, 5.734466412832262e-08f));
    x=a; y=b; z=c;
    a = pm_precise_dot3(x,y,z,make_float2(0.8190224170684814f, 2.0928220934024466e-08f),make_float2(0.3619062602519989f, -1.991085074593002e-10f),make_float2(-0.1288737803697586f, -1.1512293340842916e-09f));
    b = pm_precise_dot3(x,y,z,make_float2(0.032983653247356415f, 6.850320866114146e-10f),make_float2(0.9292868375778198f, 2.4008523169527507e-08f),make_float2(0.036144666373729706f, -2.3087306372238103e-11f));
    c = pm_precise_dot3(x,y,z,make_float2(0.048177190124988556f, -7.653643829819146e-10f),make_float2(0.26423951983451843f, 1.1918212194927946e-08f),make_float2(0.633547842502594f, -1.4033163076021538e-08f));
    return make_float3(pm_rn_add(a.x,a.y),pm_rn_add(b.x,b.y),pm_rn_add(c.x,c.y));
}
__DEVICE__ float3 pm_condition_lms(float3 encoded,float3 lms) {
    float largest = _fmaxf(_fabs(lms.x),_fmaxf(_fabs(lms.y),_fabs(lms.z)));
    float error_region = largest*0.00390625f; // 2^-8, precision routing only.
    if (_fabs(lms.x)<=error_region || _fabs(lms.y)<=error_region || _fabs(lms.z)<=error_region) {
        float3 precise=pm_precise_lms(encoded);
        if (pm_finite3(precise)) return precise;
    }
    return lms;
}

// Keep residuals through the entire ill-conditioned path: prematurely rounding
// Lab, S or the inverse basis can amplify one ulp during HDR cancellation.
__DEVICE__ float2 pm_pair_cbrt(float2 v) {
    // Exact power-of-two range reduction keeps root^3 residuals finite
    // even when a rounded cube-root seed lies just above cbrt(FLT_MAX).
    float factor=1.0f;
    if (_fabs(v.x)>4.0e37f) { v=pm_pair_mul(v,pm_pair(0.125f)); factor=2.0f; }
    float h=pm_cbrt(v.x);
    if (h==0.0f) return pm_pair(h);
    float2 root=pm_pair(h);
    for (int i=0;i<2;i++) {
        float2 square=pm_pair_mul(root,root);
        float2 residual=pm_pair_add(v,pm_pair_neg(pm_pair_mul(square,root)));
        root=pm_pair_add(root,pm_pair_div(residual,pm_pair_mul(pm_pair(3.0f),square)));
    }
    return pm_pair_mul(root,pm_pair(factor));
}
__DEVICE__ float2 pm_pair_sqrt(float2 v) {
    float h=_sqrtf(v.x);
    if (h==0.0f) return pm_pair(h);
    float2 root=pm_pair(h);
    float2 residual=pm_pair_add(v,pm_pair_neg(pm_pair_mul(root,root)));
    return pm_pair_add(root,pm_pair_div(residual,pm_pair_mul(pm_pair(2.0f),root)));
}
__DEVICE__ float2 pm_precise_transfer(float2 s,float t,float compression,float softness) {
    float2 hundred=pm_pair(100.0f);
    float2 a=pm_pair_div(pm_pair(compression),hundred);
    float2 q=pm_pair_div(pm_pair_add(hundred,pm_pair(-compression)),hundred);
    float2 half=pm_pair_mul(pm_pair(t),pm_pair_div(pm_pair(softness),hundred));
    float2 lo=pm_pair_add(pm_pair(t),pm_pair_neg(half));
    float2 hi=pm_pair_add(pm_pair(t),half);
    float2 x=pm_pair_add(s,pm_pair_neg(lo));
    if (x.x<0.0f || (x.x==0.0f && x.y<=0.0f)) return s;
    float2 upper=pm_pair_add(s,pm_pair_neg(hi));
    if (half.x==0.0f || upper.x>0.0f || (upper.x==0.0f && upper.y>=0.0f)) {
        return pm_pair_add(pm_pair(t),pm_pair_mul(q,pm_pair_add(s,pm_pair(-t))));
    }
    float2 numerator=pm_pair_mul(a,pm_pair_mul(x,x));
    float2 denominator=pm_pair_mul(pm_pair(4.0f),half);
    return pm_pair_add(s,pm_pair_neg(pm_pair_div(numerator,denominator)));
}
__DEVICE__ int pm_precision_route(float3 lms) {
    float largest=_fmaxf(_fabs(lms.x),_fmaxf(_fabs(lms.y),_fabs(lms.z)));
    float region=largest*0.00390625f;
    return _fabs(lms.x)<=region || _fabs(lms.y)<=region || _fabs(lms.z)<=region;
}


// PROPOSED domain: S*=100*C/abs(L); L=0 uses its continuous high-S limit.
// Evaluate C_out/C directly so no division by L or S is necessary.
// This replaces R2's L/S identity policy; it is NOT an approved R2 repair.
__DEVICE__ float2 pm_continuous_scale_pair(float2 lightness,float2 chroma,
                                         float t,float compression,float softness) {
    if (lightness.x<0.0f || (lightness.x==0.0f && lightness.y<0.0f)) lightness=pm_pair_neg(lightness);
    float2 hundred=pm_pair(100.0f);
    float2 strength=pm_pair_div(pm_pair(compression),hundred);
    float2 slope=pm_pair_div(pm_pair_add(hundred,pm_pair(-compression)),hundred);
    float2 center=pm_pair_div(pm_pair_mul(pm_pair(t),lightness),hundred);
    float2 half=pm_pair_mul(center,pm_pair_div(pm_pair(softness),hundred));
    float2 lo=pm_pair_add(center,pm_pair_neg(half));
    float2 hi=pm_pair_add(center,half);
    float2 lower=pm_pair_add(chroma,pm_pair_neg(lo));
    if (lower.x<0.0f || (lower.x==0.0f && lower.y<=0.0f)) return pm_pair(1.0f);
    float2 upper=pm_pair_add(chroma,pm_pair_neg(hi));
    float2 out;
    if (half.x==0.0f || upper.x>0.0f || (upper.x==0.0f && upper.y>=0.0f)) {
        out=pm_pair_add(pm_pair_mul(slope,chroma),pm_pair_mul(strength,center));
    } else {
        float2 reduction=pm_pair_div(pm_pair_mul(strength,pm_pair_mul(lower,lower)),
                                    pm_pair_mul(pm_pair(4.0f),half));
        out=pm_pair_add(chroma,pm_pair_neg(reduction));
    }
    return pm_pair_div(out,chroma);
}
__DEVICE__ float3 pm_precise_color(float3 original,float threshold,float compression,float softness) {
    float2 x=pm_precise_decode(original.x);
    float2 y=pm_precise_decode(original.y);
    float2 z=pm_precise_decode(original.z);
    float2 a=pm_precise_dot3(x,y,z,make_float2(0.7006223797798157f, 1.022018469853947e-08f),make_float2(0.14877481758594513f, 2.41405495593483e-09f),make_float2(0.1010587215423584f, -1.5423583521467776e-09f));
    float2 b=pm_precise_dot3(x,y,z,make_float2(0.2741185128688812f, -2.8688811326560426e-09f),make_float2(0.8736318945884705f, 5.411529446774921e-09f),make_float2(-0.14775040745735168f, -2.5426483141188783e-09f));
    float2 c=pm_precise_dot3(x,y,z,make_float2(-0.09896291047334671f, 4.733466951734044e-10f),make_float2(-0.13789533078670502f, 7.867050344501081e-10f),make_float2(1.3259159326553345f, 5.734466412832262e-08f));
    x=a; y=b; z=c;
    a=pm_precise_dot3(x,y,z,make_float2(0.8190224170684814f, 2.0928220934024466e-08f),make_float2(0.3619062602519989f, -1.991085074593002e-10f),make_float2(-0.1288737803697586f, -1.1512293340842916e-09f));
    b=pm_precise_dot3(x,y,z,make_float2(0.032983653247356415f, 6.850320866114146e-10f),make_float2(0.9292868375778198f, 2.4008523169527507e-08f),make_float2(0.036144666373729706f, -2.3087306372238103e-11f));
    c=pm_precise_dot3(x,y,z,make_float2(0.048177190124988556f, -7.653643829819146e-10f),make_float2(0.26423951983451843f, 1.1918212194927946e-08f),make_float2(0.633547842502594f, -1.4033163076021538e-08f));
    a=pm_pair_cbrt(a); b=pm_pair_cbrt(b); c=pm_pair_cbrt(c);
    x=a; y=b; z=c;
    a=pm_precise_dot3(x,y,z,make_float2(0.21045427024364471f, -1.934330695618769e-09f),make_float2(0.7936177849769592f, -1.0274654016484419e-08f),make_float2(-0.004072043113410473f, 1.0179117271302829e-10f));
    b=pm_precise_dot3(x,y,z,make_float2(1.9779984951019287f, 3.732924014343553e-08f),make_float2(-2.4285922050476074f, -3.700097295222804e-08f),make_float2(0.4505937099456787f, -3.282677185634242e-10f));
    c=pm_precise_dot3(x,y,z,make_float2(0.025904042646288872f, -1.8074107488441626e-10f),make_float2(0.7827717065811157f, 5.876414022054632e-09f),make_float2(-0.8086757659912109f, 1.1068133964897697e-08f));

    float3 lab=make_float3(a.x,b.x,c.x);
    float2 chroma=pm_pair_sqrt(pm_pair_add(pm_pair_mul(b,b),pm_pair_mul(c,c)));
    if (!pm_finite3(lab) || !pm_finite(chroma.x) || chroma.x<=1.0e-7f) return original;
    float2 scale=pm_continuous_scale_pair(a,chroma,threshold,compression,softness);
    if (!pm_finite(scale.x) || !pm_finite(scale.y)) return original;
    if (scale.x==1.0f && scale.y==0.0f) return original;
    b=pm_pair_mul(b,scale); c=pm_pair_mul(c,scale);
    x=a; y=b; z=c;
    a=pm_precise_dot3(x,y,z,make_float2(1.0f, 0.0f),make_float2(0.3963377773761749f, -2.6757812162793975e-17f),make_float2(0.21580375730991364f, -3.5253905002695555e-17f));
    b=pm_precise_dot3(x,y,z,make_float2(1.0f, 0.0f),make_float2(-0.10556134581565857f, -3.0664061763373566e-17f),make_float2(-0.0638541728258133f, -6.542968866792397e-18f));
    c=pm_precise_dot3(x,y,z,make_float2(1.0f, 0.0f),make_float2(-0.08948417752981186f, -4.086914118167298e-17f),make_float2(-1.2914855480194092f, -2.031250023911959e-17f));
    a=pm_pair_mul(a,pm_pair_mul(a,a));
    b=pm_pair_mul(b,pm_pair_mul(b,b));
    c=pm_pair_mul(c,pm_pair_mul(c,c));
    x=a; y=b; z=c;
    a=pm_precise_dot3(x,y,z,make_float2(1.2268798351287842f, 4.0717139881962794e-08f),make_float2(-0.5578150153160095f, 2.085579176025476e-08f),make_float2(0.28139105439186096f, -8.725896449846005e-09f));
    b=pm_precise_dot3(x,y,z,make_float2(-0.040575746446847916f, 1.2320471309834602e-09f),make_float2(1.1122868061065674f, -2.826250344867276e-09f),make_float2(-0.07171105593442917f, -2.131087306622703e-09f));
    c=pm_precise_dot3(x,y,z,make_float2(-0.07637293636798859f, -3.0667152151053756e-10f),make_float2(-0.4214933216571808f, -1.0745062617445456e-08f),make_float2(1.5869240760803223f, -5.624353960342887e-08f));
    x=a; y=b; z=c;
    a=pm_precise_dot3(x,y,z,make_float2(1.5166720151901245f, 2.4809875043274587e-08f),make_float2(-0.28147804737091064f, -2.6290893906377732e-09f),make_float2(-0.14696362614631653f, -3.853683594456925e-09f));
    b=pm_precise_dot3(x,y,z,make_float2(-0.4649170935153961f, -6.48460396490691e-09f),make_float2(1.2514238357543945f, -5.575439487870426e-08f),make_float2(0.1748846173286438f, -7.3286439139508275e-09f));
    c=pm_precise_dot3(x,y,z,make_float2(0.06484904885292053f, 1.1470794314405452e-09f),make_float2(0.1091393381357193f, 1.864280729790835e-09f),make_float2(0.761414647102356f, -2.710235591507626e-08f));

    float3 linear=make_float3(pm_rn_add(a.x,a.y),pm_rn_add(b.x,b.y),pm_rn_add(c.x,c.y));
    if (!pm_finite3(linear)) return original;
    float3 encoded=make_float3(pm_encode(linear.x),pm_encode(linear.y),pm_encode(linear.z));
    return pm_finite3(encoded) ? encoded : original;
}
__DEVICE__ int pm_domain(float3 lab, float c, float s) {
    return pm_finite3(lab) && pm_finite(c) && pm_finite(s) &&
        lab.x > 1.0e-6f && c > 1.0e-7f && s > 1.0e-7f;
}

// LUMA-ANCHORED RGB SATURATION REVISION, RESEARCH ONLY.
// The four controls and centered-knee scalar algebra remain. The metric and
// reconstruction change explicitly: linear Rec2020 opponent C / RMS energy.
// No Density, signed cube root, original Oklab L/h invariant or RGB clamp.
__DEVICE__ float3 pm_luma_dwg_rec2020(float3 v) {
    return make_float3(
        1.1303021773140678f*v.x - 0.02039284413095366f*v.y - 0.10990932792933558f*v.z,
       -0.025547057107365524f*v.x + 1.3108493208064071f*v.y - 0.285302265676628f*v.z,
       -0.09259860409296901f*v.x - 0.16465302630512835f*v.y + 1.2572516297342213f*v.z);
}
__DEVICE__ float3 pm_luma_rec2020_dwg(float3 v) {
    return make_float3(
        0.8921121191000202f*v.x + 0.024369174231315953f*v.y + 0.08351870614890726f*v.z,
        0.032616603684044905f*v.x + 0.7861375200421156f*v.y + 0.1812458830002832f*v.z,
        0.06997705207896263f*v.x + 0.10474948976869711f*v.y + 0.8252734555413982f*v.z);
}
__DEVICE__ float3 pm_perceptual_fallback(float3 input_linear,float threshold,float compression,float softness) {
    float3 wide=pm_luma_dwg_rec2020(input_linear);
    if (!pm_finite3(wide)) return input_linear;
    float peak=_fmaxf(_fabs(wide.x),_fmaxf(_fabs(wide.y),_fabs(wide.z)));
    if (peak==0.0f) return input_linear;
    float3 n=make_float3(pm_rn_div(wide.x,peak),pm_rn_div(wide.y,peak),pm_rn_div(wide.z,peak));
    if (!pm_finite3(n)) return input_linear;
    float energy=_sqrtf(0.2627002120112671f*n.x*n.x +
                         0.6779980715188708f*n.y*n.y + 0.05930171646986196f*n.z*n.z);
    float a=0.2070491871195835f*(n.x-n.z)-0.24661455358067144f*(n.y-n.z);
    float b=0.04752151915825072f*(n.x-n.z)+0.11405113589737766f*(n.y-n.z);
    float chroma=_sqrtf(a*a+b*b);
    if (!pm_finite(energy) || !pm_finite(chroma) || energy==0.0f || chroma==0.0f) return input_linear;
    // S=100*C/E; pair arithmetic evaluates the same direct chroma-domain knee.
    float2 pair_scale=pm_continuous_scale_pair(pm_pair(energy),pm_pair(chroma),threshold,compression,softness);
    float scale=pm_rn_add(pair_scale.x,pair_scale.y);
    if (!pm_finite(scale) || scale==1.0f) return input_linear;
    float range=_fmaxf(n.x,_fmaxf(n.y,n.z))-_fminf(n.x,_fminf(n.y,n.z));
    float u=range/energy;
    float visibility=u>=1.0f ? 1.0f : u*u*(3.0f-2.0f*u);
    float luminance=0.2627002120112671f*n.x + 0.6779980715188708f*n.y + 0.05930171646986196f*n.z;
    float negative=0.2627002120112671f*_fmaxf(-n.x,0.0f) +
                   0.6779980715188708f*_fmaxf(-n.y,0.0f) + 0.05930171646986196f*_fmaxf(-n.z,0.0f);
    float anchor=luminance+visibility*negative;
    float d=1.0f-scale;
    float3 delta=make_float3(d*(anchor-n.x)*peak,d*(anchor-n.y)*peak,d*(anchor-n.z)*peak);
    if (!pm_finite3(delta)) return input_linear;
    delta=pm_luma_rec2020_dwg(delta);
    float3 output_linear=make_float3(input_linear.x+delta.x,input_linear.y+delta.y,input_linear.z+delta.z);
    if (!pm_finite3(output_linear)) return input_linear;
    return output_linear;
}
__DEVICE__ float3 pm_perceptual_rec_lms(float3 v) {
    return make_float3(
        0.61675578486544447f*v.x + 0.36019840122646324f*v.y + 0.023045813908092305f*v.z,
        0.26513305939263682f*v.x + 0.63583937206784902f*v.y + 0.099027568539514166f*v.z,
        0.10010262952034829f*v.x + 0.20390652261661441f*v.y + 0.69599084786303733f*v.z);
}
__DEVICE__ float3 pm_perceptual_lms_rec(float3 v) {
    return make_float3(
        2.1399067304346509f*v.x - 1.2463894937606175f*v.y + 0.10648276332596682f*v.z,
         - 0.88473583575776771f*v.x + 2.1632309383612012f*v.y - 0.27849510260343363f*v.z,
         - 0.04857374640044404f*v.x - 0.45450314971409606f*v.y + 1.5030768961145398f*v.z);
}

// CONSTANT-Y RECONSTRUCTION; HUE/S RELAXED ONLY AT POSITIVE-PROXY GAMUT EDGE.
// Positive RGB has LMS safely away from zero after peak normalization.
// For mixed signs, blend toward the bounded RGB-luma extension using P/(P+N).
// Inherited Comp helper: all controls are explicit arguments.
__DEVICE__ float3 pmv_comp(float3 linear,float threshold,float compression,float softness) {
    if (compression==0.0f || !pm_finite3(linear)) return linear;
    if (linear.x==linear.y && linear.y==linear.z) return linear;
    float3 wide=pm_luma_dwg_rec2020(linear);
    if (!pm_finite3(wide)) return linear;
    float peak=_fmaxf(_fabs(wide.x),_fmaxf(_fabs(wide.y),_fabs(wide.z)));
    if (peak==0.0f) return linear;
    float3 n=make_float3(pm_rn_div(wide.x,peak),pm_rn_div(wide.y,peak),pm_rn_div(wide.z,peak));
    if (!pm_finite3(n)) return linear;
    float3 positive=make_float3(_fmaxf(n.x,0.0f),_fmaxf(n.y,0.0f),_fmaxf(n.z,0.0f));
    float3 negative=make_float3(_fminf(n.x,0.0f),_fminf(n.y,0.0f),_fminf(n.z,0.0f));
    float positive_peak=_fmaxf(positive.x,_fmaxf(positive.y,positive.z));
    float3 fallback=linear;
    if (negative.x<0.0f || negative.y<0.0f || negative.z<0.0f)
        fallback=pm_perceptual_fallback(linear,threshold,compression,softness);
    if (positive_peak==0.0f) {
        if (fallback.x==linear.x && fallback.y==linear.y && fallback.z==linear.z) return linear;
        return fallback;
    }
    float P=0.2627002120112671f*positive.x+0.6779980715188708f*positive.y+0.05930171646986196f*positive.z;
    float N=-0.2627002120112671f*negative.x-0.6779980715188708f*negative.y-0.05930171646986196f*negative.z;
    float visibility=P/(P+N);
    float3 unit=make_float3(positive.x/positive_peak,positive.y/positive_peak,positive.z/positive_peak);
    float3 lms=pm_perceptual_rec_lms(unit);
    float3 roots=make_float3(pm_cbrt(lms.x),pm_cbrt(lms.y),pm_cbrt(lms.z));
    float3 lab=pm_root_lab(roots);
    float chroma=_sqrtf(lab.y*lab.y+lab.z*lab.z);
    if (!pm_finite3(lab) || !pm_finite(chroma) || lab.x<=0.0f) return linear;
    float scale=1.0f;
    if (chroma>0.0f) {
        float2 pair_scale=pm_continuous_scale_pair(pm_pair(lab.x),pm_pair(chroma),threshold,compression,softness);
        scale=pm_rn_add(pair_scale.x,pair_scale.y);
    }
    if (!pm_finite(scale)) return linear;
    if (scale==1.0f && fallback.x==linear.x && fallback.y==linear.y && fallback.z==linear.z) return linear;
    float3 proxy=positive;
    if (scale!=1.0f) {
        float3 shape=make_float3(1.0f,lab.y*scale/lab.x,lab.z*scale/lab.x);
        roots=pm_lab_root(shape);
        lms=make_float3(roots.x*roots.x*roots.x,roots.y*roots.y*roots.y,roots.z*roots.z*roots.z);
        float3 shape_rgb=pm_perceptual_lms_rec(lms);
        float shape_Y=0.2627002120112671f*shape_rgb.x+0.6779980715188708f*shape_rgb.y+0.05930171646986196f*shape_rgb.z;
        if (!pm_finite3(shape_rgb) || !pm_finite(shape_Y) || shape_Y<=0.0f) return linear;
        float normalizer=P/shape_Y;
        proxy=make_float3(shape_rgb.x*normalizer,shape_rgb.y*normalizer,shape_rgb.z*normalizer);
        // EXPLICIT POSITIVE-PROXY GAMUT-EDGE RECONSTRUCTION, RESEARCH ONLY.
        // The exact hue/S invariants are relaxed only if this proxy leaves
        // nonnegative Rec2020. Both candidates retain the same positive Y.
        // The original signed residual is added separately below, never clamped.
        if (proxy.x<0.0f || proxy.y<0.0f || proxy.z<0.0f) {
            float gray=(1.0f-scale)*P;
            float3 safe=make_float3(scale*positive.x+gray,scale*positive.y+gray,scale*positive.z+gray);
            float weight=0.0f;
            if (proxy.x<0.0f && safe.x>proxy.x) weight=_fmaxf(weight,-proxy.x/(safe.x-proxy.x));
            if (proxy.y<0.0f && safe.y>proxy.y) weight=_fmaxf(weight,-proxy.y/(safe.y-proxy.y));
            if (proxy.z<0.0f && safe.z>proxy.z) weight=_fmaxf(weight,-proxy.z/(safe.z-proxy.z));
            weight=_fminf(_fmaxf(weight,0.0f),1.0f);
            float keep=1.0f-weight;
            proxy=make_float3(keep*proxy.x+weight*safe.x,keep*proxy.y+weight*safe.y,keep*proxy.z+weight*safe.z);
        }
    }
    float3 branch=make_float3(proxy.x+scale*negative.x,proxy.y+scale*negative.y,proxy.z+scale*negative.z);
    float3 delta=make_float3((branch.x-n.x)*peak,(branch.y-n.y)*peak,(branch.z-n.z)*peak);
    if (!pm_finite3(delta)) return linear;
    delta=pm_luma_rec2020_dwg(delta);
    float3 perceptual=make_float3(linear.x+delta.x,linear.y+delta.y,linear.z+delta.z);
    float3 output_linear=perceptual;
    if (N>0.0f) output_linear=make_float3(fallback.x+visibility*(perceptual.x-fallback.x),
        fallback.y+visibility*(perceptual.y-fallback.y),fallback.z+visibility*(perceptual.z-fallback.z));
    if (!pm_finite3(output_linear)) return linear;
    return output_linear;
}
// Pixel-local linear-DWG stages. No DEFINE_UI_PARAMS variables may be read here.
// PROTOTYPE: chart-calibrated skin hue still needs same-view Host/skin acceptance.
__DEVICE__ float pmv_peak(float3 v) {
    return _fmaxf(_fabs(v.x),_fmaxf(_fabs(v.y),_fabs(v.z)));
}
__DEVICE__ int pmv_same(float3 a,float3 b) {
    return a.x==b.x && a.y==b.y && a.z==b.z;
}
__DEVICE__ float pmv_smooth(float lo,float hi,float x) {
    float u=_fminf(1.0f,_fmaxf(0.0f,(x-lo)/(hi-lo)));
    return u*u*(3.0f-2.0f*u);
}
__DEVICE__ float3 pmv_lab(float3 n) {
    float3 lms=pm_xyz_lms(pm_dwg_xyz(n));
    return pm_root_lab(make_float3(pm_cbrt(lms.x),pm_cbrt(lms.y),pm_cbrt(lms.z)));
}
__DEVICE__ float3 pmv_unlab(float3 lab) {
    float3 roots=pm_lab_root(lab);
    return pm_xyz_dwg(pm_lms_xyz(make_float3(roots.x*roots.x*roots.x,
        roots.y*roots.y*roots.y,roots.z*roots.z*roots.z)));
}
__DEVICE__ float pmv_chroma(float3 lab) {
    // Peak-normalized lab components are small enough for these squares.
    return _sqrtf(lab.y*lab.y+lab.z*lab.z);
}
__DEVICE__ float pmv_response(float l,float c,float power) {
    if (!(l>0.0f) || !(c>0.0f) || !pm_finite(l) || !pm_finite(c)) return 0.0f;
    // q=S/25=4C/L. Form the <=1 ratio in each branch, never huge C/L or q^p.
    float center=0.25f*l;
    if (c<=center) {
        float v=_powf(c/center,power);
        return v/(1.0f+v);
    }
    float v=_powf(center/c,power);
    return 1.0f/(1.0f+v);
}
__DEVICE__ float pmv_tone(float e,float shadow,float sr,float highlight,float hr) {
    // Width4 stops gives |d tonal attenuation / dE|<=0.375.
    // Therefore base Density Eout derivative >=1-1.5*0.375=0.4375.
    float es=-7.0f+0.06f*sr;
    float eh= 7.0f-0.06f*hr;
    float ms=1.0f-pmv_smooth(es-2.0f,es+2.0f,e);
    float mh=pmv_smooth(eh-2.0f,eh+2.0f,e);
    return (1.0f-0.01f*shadow*ms)*(1.0f-0.01f*highlight*mh);
}
// Generated from a fixed D65 sRGB (194,150,130) chart swatch, not scope angle.
// Relative saturation fade is exposure-invariant and has no lightness gate.
__DEVICE__ float pmv_skin(float3 input_linear,float reference_a,float reference_b) {
    if (input_linear.x==input_linear.y && input_linear.y==input_linear.z) return 0.0f;
    float peak=pmv_peak(input_linear);
    if (!pm_finite(peak) || peak==0.0f) return 0.0f;
    float3 n=make_float3(input_linear.x/peak,input_linear.y/peak,input_linear.z/peak);
    float3 lab=pmv_lab(n);
    float c=pmv_chroma(lab);
    if (!pm_finite3(lab) || !(lab.x>0.0f) || !(c>0.0f)) return 0.0f;
    float cosine=(lab.y*reference_a+lab.z*reference_b)/c;
    float mh=pmv_smooth(0.90630778703665f,0.9902680687415704f,cosine);
    // S>=8 is full confidence. Branch before division to avoid overflow.
    float mc=c>=0.08f*lab.x ? 1.0f : pmv_smooth(0.0f,0.08f,c/lab.x);
    return mh*mc;
}
__DEVICE__ float3 pmv_presat(float3 input_linear,float pre,float skin_keep) {
    float gain=1.0f+(0.01f*pre-1.0f)*skin_keep;
    if (gain==1.0f || skin_keep==0.0f) return input_linear;
    if (input_linear.x==input_linear.y && input_linear.y==input_linear.z) return input_linear;
    float peak=pmv_peak(input_linear);
    if (!pm_finite(peak) || peak==0.0f) return input_linear;
    float3 n=make_float3(input_linear.x/peak,input_linear.y/peak,input_linear.z/peak);
    float3 lab=pmv_lab(n);
    if (!pm_finite3(lab) || !(lab.x>0.0f)) return input_linear;
    float3 before=pmv_unlab(lab);
    float3 after=pmv_unlab(make_float3(lab.x,lab.y*gain,lab.z*gain));
    float3 out=make_float3(input_linear.x+(after.x-before.x)*peak,
        input_linear.y+(after.y-before.y)*peak,input_linear.z+(after.z-before.z)*peak);
    return pm_finite3(out) ? out : input_linear;
}
__DEVICE__ float3 pmv_mask_delta(float3 source,float3 processed,float keep) {
    if (keep==0.0f) return source;
    if (keep==1.0f) return processed;
    float protected_part=1.0f-keep;
    float3 out=make_float3(keep*processed.x+protected_part*source.x,
        keep*processed.y+protected_part*source.y,keep*processed.z+protected_part*source.z);
    return pm_finite3(out) ? out : source;
}
__DEVICE__ float3 pmv_density(float3 stage_input,float amount,float chroma,float power,
    float shadow,float sr,float highlight,float hr,float skin_keep,float white_log_offset) {
    if (amount==0.0f || skin_keep==0.0f) return stage_input;
    if (stage_input.x==stage_input.y && stage_input.y==stage_input.z) return stage_input;
    float peak=pmv_peak(stage_input);
    if (!pm_finite(peak) || peak==0.0f) return stage_input;
    float3 n=make_float3(stage_input.x/peak,stage_input.y/peak,stage_input.z/peak);
    float3 lab=pmv_lab(n);
    float c=pmv_chroma(lab);
    if (!pm_finite3(lab) || !(lab.x>0.0f) || !pm_finite(c) || !(c>0.0f)) return stage_input;
    float w=pmv_response(lab.x,c,power);
    float e=3.0f*_log2f(lab.x)+_log2f(peak)+white_log_offset;
    if (!pm_finite(e)) return stage_input;
    float de=-0.015f*amount*w*pmv_tone(e,shadow,sr,highlight,hr)*skin_keep;
    if (!pm_finite(de) || de==0.0f) return stage_input;
    float gain=_powf(2.0f,de);
    float3 base=make_float3(stage_input.x*gain,stage_input.y*gain,stage_input.z*gain);
    if (!pm_finite3(base)) return stage_input;
    if (chroma==0.0f) return base;
    float gc=_powf(2.0f,0.0025f*chroma*_fabs(de));
    if (!pm_finite(gc)) return base;
    float3 before=pmv_unlab(lab);
    float3 after=pmv_unlab(make_float3(lab.x,lab.y*gc,lab.z*gc));
    float3 out=make_float3(base.x+((after.x-before.x)*gain)*peak,
        base.y+((after.y-before.y)*gain)*peak,base.z+((after.z-before.z)*gain)*peak);
    // A bad Chroma reconstruction must not discard valid Density-only output.
    return pm_finite3(out) ? out : base;
}
// EXPERIMENTAL ACCURACY PATH: pair state persists through the new stages.
// Comp snapshots remain binary32 and unchanged. Host struct support is untested.
typedef struct { float2 x; float2 y; float2 z; } pmvp3;
__DEVICE__ pmvp3 pmvp_make(float2 x,float2 y,float2 z) { pmvp3 v; v.x=x; v.y=y; v.z=z; return v; }
__DEVICE__ pmvp3 pmvp_float(float3 v) { return pmvp_make(pm_pair(v.x),pm_pair(v.y),pm_pair(v.z)); }
__DEVICE__ float pmvp_round(float2 x) { return x.y==0.0f ? x.x : pm_rn_add(x.x,x.y); }
__DEVICE__ float3 pmvp_high(pmvp3 v) { return make_float3(pmvp_round(v.x),pmvp_round(v.y),pmvp_round(v.z)); }
__DEVICE__ int pmvp_finite(pmvp3 v) { return pm_finite3(pmvp_high(v)) && pm_finite(v.x.y)&&pm_finite(v.y.y)&&pm_finite(v.z.y); }
__DEVICE__ int pmvp_same(pmvp3 a,pmvp3 b) { return a.x.x==b.x.x&&a.x.y==b.x.y&&a.y.x==b.y.x&&a.y.y==b.y.y&&a.z.x==b.z.x&&a.z.y==b.z.y; }
__DEVICE__ float2 pmvp_sub(float2 a,float2 b) { return pm_pair_add(a,pm_pair_neg(b)); }
__DEVICE__ pmvp3 pmvp_add(pmvp3 a,pmvp3 b) { return pmvp_make(pm_pair_add(a.x,b.x),pm_pair_add(a.y,b.y),pm_pair_add(a.z,b.z)); }
__DEVICE__ pmvp3 pmvp_sub3(pmvp3 a,pmvp3 b) { return pmvp_make(pmvp_sub(a.x,b.x),pmvp_sub(a.y,b.y),pmvp_sub(a.z,b.z)); }
__DEVICE__ pmvp3 pmvp_scale(pmvp3 a,float2 g) { return pmvp_make(pm_pair_mul(a.x,g),pm_pair_mul(a.y,g),pm_pair_mul(a.z,g)); }
__DEVICE__ pmvp3 pmvp_div(pmvp3 a,float k) { return pmvp_make(pm_pair_div(a.x,pm_pair(k)),pm_pair_div(a.y,pm_pair(k)),pm_pair_div(a.z,pm_pair(k))); }
__DEVICE__ int pmvp_positive(float2 x) { return x.x>0.0f || (x.x==0.0f&&x.y>0.0f); }
__DEVICE__ int pmvp_ge(float2 a,float2 b) { float2 d=pmvp_sub(a,b); return d.x>0.0f || (d.x==0.0f&&d.y>=0.0f); }
__DEVICE__ float2 pmvp_abs(float2 x) { return x.x<0.0f || (x.x==0.0f&&x.y<0.0f) ? pm_pair_neg(x) : x; }
__DEVICE__ pmvp3 pmvp_dwg_xyz(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(0.70062237977981567f,1.0220184365472562e-08f),make_float2(0.14877481758594513f,2.4140548726681033e-09f),make_float2(0.1010587215423584f,-1.5423583937801411e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.27411851286888123f,-2.8688812436783451e-09f),make_float2(0.87363189458847046f,5.4115295577972233e-09f),make_float2(-0.14775040745735168f,-2.5426483141188783e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.09896291047334671f,4.7334670905119225e-10f),make_float2(-0.13789533078670502f,7.8670500669453247e-10f),make_float2(1.3259159326553345f,5.7344665460590249e-08f))); }
__DEVICE__ pmvp3 pmvp_xyz_lms(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(0.81902241706848145f,2.0928221600158281e-08f),make_float2(0.3619062602519989f,-1.991085074593002e-10f),make_float2(-0.12887378036975861f,-1.151229306328716e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.032983653247356415f,6.8503208661141457e-10f),make_float2(0.92928683757781982f,2.4008523613616717e-08f),make_float2(0.036144666373729706f,-2.3087302902791151e-11f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.048177190124988556f,-7.6536435522633894e-10f),make_float2(0.26423951983451843f,1.19182123614614e-08f),make_float2(0.63354784250259399f,-1.4033163076021538e-08f))); }
__DEVICE__ pmvp3 pmvp_root_lab(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(0.21045427024364471f,-1.9343307233743445e-09f),make_float2(0.79361778497695923f,-1.0274653794439814e-08f),make_float2(-0.0040720431134104729f,1.0179117271302829e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.9779984951019287f,3.7329239699346317e-08f),make_float2(-2.4285922050476074f,-3.700097250813883e-08f),make_float2(0.45059370994567871f,-3.2826769080784857e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.025904042646288872f,-1.8074107141496931e-10f),make_float2(0.78277170658111572f,5.8764139110323299e-09f),make_float2(-0.80867576599121094f,1.1068133520808487e-08f))); }
__DEVICE__ pmvp3 pmvp_lab_root(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.0f,0.0f),make_float2(0.39633777737617493f,0.0f),make_float2(0.21580375730991364f,-2.7755575615628914e-17f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.0f,0.0f),make_float2(-0.10556134581565857f,-2.7755575615628914e-17f),make_float2(-0.063854172825813293f,0.0f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.0f,0.0f),make_float2(-0.089484177529811859f,-4.163336342344337e-17f),make_float2(-1.2914855480194092f,0.0f))); }
__DEVICE__ pmvp3 pmvp_lms_xyz(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.2268798351287842f,4.0717140104007399e-08f),make_float2(-0.55781501531600952f,2.0855792426388575e-08f),make_float2(0.28139105439186096f,-8.7258962833125508e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.040575746446847916f,1.2320471171056724e-09f),make_float2(1.1122868061065674f,-2.826250344867276e-09f),make_float2(-0.071711055934429169f,-2.1310872372337641e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.076372936367988586f,-3.0667150763274975e-10f),make_float2(-0.42149332165718079f,-1.0745062395400851e-08f),make_float2(1.5869240760803223f,-5.6243540713651896e-08f))); }
__DEVICE__ pmvp3 pmvp_xyz_dwg(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.5166720151901245f,2.4809875487363797e-08f),make_float2(-0.28147804737091064f,-2.629089335126622e-09f),make_float2(-0.14696362614631653f,-3.8536834834346223e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.46491709351539612f,-6.4846039093957586e-09f),make_float2(1.2514238357543945f,-5.5754394434615051e-08f),make_float2(0.1748846173286438f,-7.328643802928525e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.064849048852920532f,1.1470794730739087e-09f),make_float2(0.1091393381357193f,1.8642807020352592e-09f),make_float2(0.76141464710235596f,-2.7102355915076259e-08f))); }

__DEVICE__ pmvp3 pmvp_lab(pmvp3 v) {
    v=pmvp_xyz_lms(pmvp_dwg_xyz(v));
    v=pmvp_make(pm_pair_cbrt(v.x),pm_pair_cbrt(v.y),pm_pair_cbrt(v.z));
    return pmvp_root_lab(v);
}
__DEVICE__ pmvp3 pmvp_unlab(pmvp3 v) {
    v=pmvp_lab_root(v);
    v=pmvp_make(pm_pair_mul(v.x,pm_pair_mul(v.x,v.x)),pm_pair_mul(v.y,pm_pair_mul(v.y,v.y)),pm_pair_mul(v.z,pm_pair_mul(v.z,v.z)));
    return pmvp_xyz_dwg(pmvp_lms_xyz(v));
}
__DEVICE__ float2 pmvp_exp2(float2 exponent) {
    if (!pm_finite(exponent.x)||!pm_finite(exponent.y)) return pm_pair(_powf(2.0f,exponent.x));
    if (exponent.x < -150.0f) return pm_pair(0.0f);
    if (exponent.x > 127.0f) return pm_pair(_powf(2.0f,exponent.x));
    float n=_floorf(exponent.x);
    if (exponent.x==n && exponent.y<0.0f) n-=1.0f;
    float2 r=pmvp_sub(exponent,pm_pair(n));
    float2 y=make_float2(1.3570247350023161e-16f,5.9873197944950427e-24f);
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(3.1324366826801248e-15f,2.4408302251763465e-23f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(6.7787260722186604e-14f,2.8260388212296155e-21f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.3691489348516273e-12f,-4.9461214846355531e-20f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(2.567843680745252e-11f,-8.1396432462243887e-19f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(4.4455383818586824e-10f,-1.0998787236787292e-17f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(7.0549117658913474e-09f,-1.4509022650861534e-16f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.0178086284895471e-07f,-2.7565577522881403e-15f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.3215486660556053e-06f,1.2958825246195795e-14f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.5252733646775596e-05f,1.5728424185084636e-13f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.00015403529687318951f,7.0606265517407507e-12f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.0013333557872101665f,2.7432677657257543e-11f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.0096181286498904228f,4.5773805405768808e-10f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.055504109710454941f,-1.0456333646158278e-09f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.24022650718688965f,-2.277889543655931e-10f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.69314718246459961f,-1.904654323148236e-09f));
    y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.0f,0.0f));
    return pm_pair_mul(y,pm_pair(_powf(2.0f,n)));
}
__DEVICE__ float2 pmvp_log2(float2 x) {
    float y=_log2f(x.x);
    if (!pm_finite(y)) return pm_pair(y);
    float2 base=pmvp_exp2(pm_pair(y));
    float2 r=pm_pair_div(pmvp_sub(x,base),base);
    float2 rr=pm_pair_mul(r,r);
    float2 ln=pm_pair_add(pmvp_sub(r,pm_pair_mul(rr,pm_pair(0.5f))),pm_pair_mul(pm_pair_mul(rr,r),make_float2(0.3333333432674408f,-9.9341074810688212e-09f)));
    return pm_pair_add(pm_pair(y),pm_pair_mul(ln,make_float2(1.4426950216293335f,1.9259629890910901e-08f)));
}
__DEVICE__ float2 pmvp_pow_small(float2 q,float p) {
    if (!pmvp_positive(q)) return pm_pair(0.0f);
    return pmvp_exp2(pm_pair_mul(pmvp_log2(q),pm_pair(p)));
}
__DEVICE__ float2 pmvp_chroma(pmvp3 lab) { return pm_pair_sqrt(pm_pair_add(pm_pair_mul(lab.y,lab.y),pm_pair_mul(lab.z,lab.z))); }
__DEVICE__ float2 pmvp_smooth(float2 lo,float2 hi,float2 x) {
    if (pmvp_ge(lo,x)) return pm_pair(0.0f);
    if (pmvp_ge(x,hi)) return pm_pair(1.0f);
    float2 u=pm_pair_div(pmvp_sub(x,lo),pmvp_sub(hi,lo));
    return pm_pair_mul(pm_pair_mul(u,u),pmvp_sub(pm_pair(3.0f),pm_pair_mul(pm_pair(2.0f),u)));
}
__DEVICE__ float2 pmvp_response(float2 l,float2 c,float p) {
    float2 center=pm_pair_mul(l,pm_pair(0.25f));
    if (pmvp_ge(center,c)) {
        float2 v=pmvp_pow_small(pm_pair_div(c,center),p);
        return pm_pair_div(v,pm_pair_add(pm_pair(1.0f),v));
    }
    float2 v=pmvp_pow_small(pm_pair_div(center,c),p);
    return pm_pair_div(pm_pair(1.0f),pm_pair_add(pm_pair(1.0f),v));
}
__DEVICE__ float2 pmvp_tone(float2 e,float shadow,float sr,float highlight,float hr) {
    float2 es=pm_pair_add(pm_pair(-7.0f),pm_pair_mul(pm_pair(sr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
    float2 eh=pmvp_sub(pm_pair(7.0f),pm_pair_mul(pm_pair(hr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
    float2 ms=pmvp_sub(pm_pair(1.0f),pmvp_smooth(pmvp_sub(es,pm_pair(2.0f)),pm_pair_add(es,pm_pair(2.0f)),e));
    float2 mh=pmvp_smooth(pmvp_sub(eh,pm_pair(2.0f)),pm_pair_add(eh,pm_pair(2.0f)),e);
    return pm_pair_mul(pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(shadow),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),ms)),
        pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(highlight),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),mh)));
}
__DEVICE__ float2 pmvp_skin(pmvp3 input) {
    float3 high=pmvp_high(input);float peak=pmv_peak(high);
    if (peak==0.0f || (high.x==high.y&&high.y==high.z)) return pm_pair(0.0f);
    pmvp3 lab=pmvp_lab(pmvp_div(input,peak));float2 c=pmvp_chroma(lab);
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)||!pmvp_positive(c)) return pm_pair(0.0f);
    float2 cosine=pm_pair_div(pm_pair_add(pm_pair_mul(lab.y,make_float2(0.69936877489089966f,7.3722203897119698e-09f)),pm_pair_mul(lab.z,make_float2(0.71476101875305176f,-5.269663372331479e-09f))),c);
    float2 hue=pmvp_smooth(make_float2(0.90630781650543213f,-2.9468782192232368e-08f),make_float2(0.9902680516242981f,1.7117272266276018e-08f),cosine);
    float2 s=pm_pair_div(c,lab.x);
    float2 conf=pmvp_smooth(pm_pair(0.0f),make_float2(0.079999998211860657f,1.7881393449270533e-09f),s);
    return pm_pair_mul(hue,conf);
}
__DEVICE__ pmvp3 pmvp_presat(pmvp3 input,float pre,float2 keep) {
    if (pre==100.0f) return input;
    float2 gain=pm_pair_add(pm_pair(1.0f),pm_pair_mul(pmvp_sub(pm_pair_mul(pm_pair(pre),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),pm_pair(1.0f)),keep));
    if ((gain.x==1.0f&&gain.y==0.0f)||!pmvp_positive(keep)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 lab=pmvp_lab(pmvp_div(input,peak));
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)) return input;
    pmvp3 changed=pmvp_make(lab.x,pm_pair_mul(lab.y,gain),pm_pair_mul(lab.z,gain));
    pmvp3 delta=pmvp_sub3(pmvp_unlab(changed),pmvp_unlab(lab));
    pmvp3 out=pmvp_add(input,pmvp_scale(delta,pm_pair(peak)));
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmvp_comp(pmvp3 input,float threshold,float compression,float softness,float2 keep) {
    if (compression==0.0f||!pmvp_positive(keep)) return input;
    float3 high=pmvp_high(input);float3 processed=pmv_comp(high,threshold,compression,softness);
    if (pmv_same(high,processed)) return input;
    pmvp3 out=pmvp_add(pmvp_scale(pmvp_float(processed),keep),pmvp_scale(input,pmvp_sub(pm_pair(1.0f),keep)));
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmvp_density(pmvp3 input,float amount,float chroma,float power,float shadow,float sr,float highlight,float hr,float2 keep) {
    if (amount==0.0f||!pmvp_positive(keep)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 lab=pmvp_lab(pmvp_div(input,peak));float2 c=pmvp_chroma(lab);
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)||!pmvp_positive(c)) return input;
    float2 e=pm_pair_add(pm_pair_add(pm_pair_mul(pm_pair(3.0f),pmvp_log2(lab.x)),pmvp_log2(pm_pair(peak))),make_float2(2.4739310741424561f,1.1334516436534159e-07f));
    float2 de=pm_pair_mul(pm_pair_mul(pm_pair(amount),make_float2(-0.014999999664723873f,-3.3527612630646075e-10f)),pm_pair_mul(pm_pair_mul(pmvp_response(lab.x,c,power),pmvp_tone(e,shadow,sr,highlight,hr)),keep));
    if (!pm_finite(de.x)||!pm_finite(de.y)||(de.x==0.0f&&de.y==0.0f)) return input;
    float2 gain=pmvp_exp2(de);pmvp3 base=pmvp_scale(input,gain);
    if (!pmvp_finite(base)) return input;
    if (chroma==0.0f) return base;
    float2 cg=pmvp_exp2(pm_pair_mul(pm_pair_mul(pm_pair(chroma),make_float2(0.0024999999441206455f,5.5879354528970415e-11f)),pmvp_abs(de)));
    pmvp3 changed=pmvp_make(lab.x,pm_pair_mul(lab.y,cg),pm_pair_mul(lab.z,cg));
    pmvp3 delta=pmvp_sub3(pmvp_unlab(changed),pmvp_unlab(lab));
    pmvp3 out=pmvp_add(base,pmvp_scale(delta,pm_pair_mul(gain,pm_pair(peak))));
    return pmvp_finite(out)?out:base;
}
__DEVICE__ float pmvp_encode(float2 x) {
    float2 encoded;
    if (pmvp_ge(make_float2(0.0026240900624543428f,-6.2454342912576788e-11f),x)) encoded=pm_pair_mul(x,make_float2(10.444268226623535f,3.2337646516111818e-07f));
    else encoded=pm_pair_mul(pm_pair_add(pmvp_log2(pm_pair_add(x,make_float2(0.0074999998323619366f,1.6763806315323038e-10f))),pm_pair(7.0f)),make_float2(0.073292478919029236f,1.0809707573500305e-09f));
    return pm_rn_add(encoded.x,encoded.y);
}
__DEVICE__ float3 pmvp_encode3(pmvp3 v) { return make_float3(pmvp_encode(v.x),pmvp_encode(v.y),pmvp_encode(v.z)); }

// EXPLICIT Y-HELD / CHROMA-HEADROOM COMPARISON POLICY. NOT ADOPTED.
typedef struct { float2 a; float2 b; float2 c; float2 d; } pmvpy_poly;
typedef struct { float2 lower; float2 upper; } pmvpy_interval;
__DEVICE__ float2 pmvpy_Y(pmvp3 rgb) { return pm_precise_dot3(rgb.x,rgb.y,rgb.z,make_float2(0.27411851286888123f,-2.8688812436783451e-09f),make_float2(0.87363189458847046f,5.4115295577972233e-09f),make_float2(-0.14775040745735168f,-2.5426483141188783e-09f)); }
__DEVICE__ float2 pmvpy_eval(pmvpy_poly p,float x) {
    float2 g=pm_pair(x);
    return pm_pair_add(pm_pair_mul(pm_pair_add(pm_pair_mul(pm_pair_add(pm_pair_mul(p.d,g),p.c),g),p.b),g),p.a);
}
__DEVICE__ float2 pmvpy_eval_pair(pmvpy_poly p,float2 g) {
    return pm_pair_add(pm_pair_mul(pm_pair_add(pm_pair_mul(pm_pair_add(pm_pair_mul(p.d,g),p.c),g),p.b),g),p.a);
}
__DEVICE__ pmvpy_poly pmvpy_polynomial(pmvp3 lab,float2 yi) {
    pmvp3 v=pmvp_lab_root(pmvp_make(pm_pair(0.0f),lab.y,lab.z));
    float2 l2=pm_pair_mul(lab.x,lab.x),l3=pm_pair_mul(l2,lab.x);
    float2 sum1=pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.040575750172138214f,4.1709611459106455e-10f),make_float2(1.1122868061065674f,8.5370064351053543e-09f),make_float2(-0.071711055934429169f,-2.8343738328606705e-09f));
    float2 sum2=pm_precise_dot3(pm_pair_mul(v.x,v.x),pm_pair_mul(v.y,v.y),pm_pair_mul(v.z,v.z),make_float2(-0.040575750172138214f,4.1709611459106455e-10f),make_float2(1.1122868061065674f,8.5370064351053543e-09f),make_float2(-0.071711055934429169f,-2.8343738328606705e-09f));
    float2 sum3=pm_precise_dot3(pm_pair_mul(v.x,pm_pair_mul(v.x,v.x)),pm_pair_mul(v.y,pm_pair_mul(v.y,v.y)),pm_pair_mul(v.z,pm_pair_mul(v.z,v.z)),make_float2(-0.040575750172138214f,4.1709611459106455e-10f),make_float2(1.1122868061065674f,8.5370064351053543e-09f),make_float2(-0.071711055934429169f,-2.8343738328606705e-09f));
    pmvpy_poly p;
    p.a=pmvp_sub(pm_pair_mul(l3,make_float2(1.0f,6.1197287237746423e-09f)),pm_pair_mul(yi,pm_pair(0.25f)));
    p.b=pm_pair_mul(pm_pair_mul(pm_pair(3.0f),l2),sum1);
    p.c=pm_pair_mul(pm_pair_mul(pm_pair(3.0f),lab.x),sum2);
    p.d=sum3;return p;
}
// Return the two real derivative critical points where present. A negative
// sentinel is ignored. Stable quadratic evaluation avoids one lost root.
__DEVICE__ float2 pmvpy_critical(pmvpy_poly p) {
    float2 a=pm_pair_mul(pm_pair(3.0f),p.d),b=pm_pair_mul(pm_pair(2.0f),p.c),c=p.b;
    if (a.x==0.0f&&a.y==0.0f) {
        if (b.x==0.0f&&b.y==0.0f) return make_float2(-1.0f,-1.0f);
        return make_float2(pmvp_round(pm_pair_div(pm_pair_neg(c),b)),-1.0f);
    }
    float2 disc=pmvp_sub(pm_pair_mul(b,b),pm_pair_mul(pm_pair(4.0f),pm_pair_mul(a,c)));
    if (!pmvp_ge(disc,pm_pair(0.0f))) return make_float2(-1.0f,-1.0f);
    float2 root=pm_pair_sqrt(disc);
    float2 q=pm_pair_mul(pm_pair(-0.5f),pm_pair_add(b,pmvp_ge(b,pm_pair(0.0f))?root:pm_pair_neg(root)));
    if (q.x==0.0f&&q.y==0.0f) return make_float2(pmvp_round(pm_pair_div(pm_pair_neg(b),pm_pair_mul(pm_pair(2.0f),a))),-1.0f);
    float x=pmvp_round(pm_pair_div(q,a)),y=pmvp_round(pm_pair_div(c,q));
    return make_float2(_fminf(x,y),_fmaxf(x,y));
}
// Bracket safe -> unsafe inside one monotone polynomial segment. Returning
// the safe representable side also gives a numerical positivity margin.
__DEVICE__ float2 pmvpy_boundary(pmvpy_poly p,float from,float to) {
    float2 safe=pm_pair(from),unsafe=pm_pair(to);
    for (int i=0;i<80;i++) {
        float2 middle=pm_pair_mul(pm_pair_add(safe,unsafe),pm_pair(0.5f));
        if ((middle.x==safe.x&&middle.y==safe.y)||(middle.x==unsafe.x&&middle.y==unsafe.y)) break;
        if (pmvp_positive(pmvpy_eval_pair(p,middle))) safe=middle;else unsafe=middle;
    }
    return safe;
}
__DEVICE__ pmvpy_interval pmvpy_bounds(pmvpy_poly p) {
    float2 critical=pmvpy_critical(p);
    float points[4];int n=0;
    points[n++]=0.0f;
    if (critical.x>0.0f&&critical.x<1000000.0f&&pm_finite(critical.x)) points[n++]=critical.x;
    if (critical.y>0.0f&&critical.y<1000000.0f&&pm_finite(critical.y)&&critical.y!=critical.x) points[n++]=critical.y;
    points[n++]=1000000.0f;
    pmvpy_interval bounds;bounds.lower=pm_pair(0.0f);bounds.upper=pm_pair(1000000.0f);
    float from=1.0f;
    for (int i=n-1;i>=0;i--) {
        float to=points[i];if (to>=1.0f) continue;
        if (!pmvp_positive(pmvpy_eval(p,to))) { bounds.lower=pmvpy_boundary(p,from,to);break; }
        from=to;
    }
    from=1.0f;
    for (int i=0;i<n;i++) {
        float to=points[i];if (to<=1.0f) continue;
        if (!pmvp_positive(pmvpy_eval(p,to))) { bounds.upper=pmvpy_boundary(p,from,to);break; }
        from=to;
    }
    return bounds;
}
__DEVICE__ float2 pmvpy_tanh_positive(float2 x) {
    float2 exp=pmvp_exp2(pm_pair_mul(x,make_float2(-2.885390043258667f,-3.8519259781821802e-08f)));
    return pm_pair_div(pmvp_sub(pm_pair(1.0f),exp),pm_pair_add(pm_pair(1.0f),exp));
}
__DEVICE__ pmvp3 pmvpy_shape(pmvp3 input,float2 requested) {
    if (requested.x==1.0f&&requested.y==0.0f) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(input,peak);float2 yi=pmvpy_Y(n);pmvp3 lab=pmvp_lab(n);
    if (!pmvp_positive(yi)||!pmvp_positive(lab.x)||!pmvp_finite(lab)||!pmvp_positive(pmvp_chroma(lab))) return input;
    pmvpy_poly p=pmvpy_polynomial(lab,yi);pmvpy_interval bounds=pmvpy_bounds(p);float2 gain=requested;
    if (pmvp_ge(requested,pm_pair(1.0f))&&!pmvp_ge(bounds.upper,pm_pair(1000000.0f))) {
        float2 h=pmvp_sub(bounds.upper,pm_pair(1.0f));if (!pmvp_positive(h)) return input;
        float2 u=pm_pair_div(pmvp_sub(requested,pm_pair(1.0f)),h);
        gain=pm_pair_add(pm_pair(1.0f),pm_pair_mul(h,pmvpy_tanh_positive(u)));
    } else if (!pmvp_ge(requested,pm_pair(1.0f))&&pmvp_positive(bounds.lower)) {
        float2 h=pmvp_sub(pm_pair(1.0f),bounds.lower);if (!pmvp_positive(h)) return input;
        float2 u=pm_pair_div(pmvp_sub(pm_pair(1.0f),requested),h);
        gain=pmvp_sub(pm_pair(1.0f),pm_pair_mul(h,pmvpy_tanh_positive(u)));
    }
    pmvp3 z=pmvp_unlab(pmvp_make(lab.x,pm_pair_mul(lab.y,gain),pm_pair_mul(lab.z,gain)));
    float2 yz=pmvpy_Y(z);
    // Same 1e-10 relative reconstruction allowance as the independent CPU
    // candidate. Without it, an accurately solved saturated boundary can
    // falsely bypass due to a final paired-matrix rounding residual.
    if (!pmvp_positive(yz)||!pmvp_ge(yz,pm_pair_mul(yi,make_float2(0.25f,-2.5000002068509275e-11f)))) return input;
    pmvp3 out=pmvp_scale(z,pm_pair_mul(pm_pair_div(yi,yz),pm_pair(peak)));
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmvpy_presat(pmvp3 input,float pre,float2 keep) {
    if (pre==100.0f||!pmvp_positive(keep)) return input;
    float2 gain=pm_pair_add(pm_pair(1.0f),pm_pair_mul(pmvp_sub(pm_pair_div(pm_pair(pre),pm_pair(100.0f)),pm_pair(1.0f)),keep));
    return pmvpy_shape(input,gain);
}
__DEVICE__ float2 pmvpy_tone(float2 e,float shadow,float sr,float highlight,float hr) {
    float2 es=pm_pair_add(pm_pair(-7.0f),pm_pair_mul(pm_pair(sr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
    float2 eh=pmvp_sub(pm_pair(7.0f),pm_pair_mul(pm_pair(hr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
    float2 ms=pmvp_sub(pm_pair(1.0f),pmvp_smooth(pmvp_sub(es,pm_pair(4.0f)),pm_pair_add(es,pm_pair(4.0f)),e));
    float2 mh=pmvp_smooth(pmvp_sub(eh,pm_pair(4.0f)),pm_pair_add(eh,pm_pair(4.0f)),e);
    return pm_pair_mul(pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(shadow),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),ms)),
        pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(highlight),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),mh)));
}
__DEVICE__ pmvp3 pmvpy_density(pmvp3 input,float amount,float chroma,float power,float shadow,float sr,float highlight,float hr,float2 keep) {
    if (amount==0.0f||!pmvp_positive(keep)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(input,peak);pmvp3 lab=pmvp_lab(n);float2 c=pmvp_chroma(lab);
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)||!pmvp_positive(c)||!pmvp_positive(pmvpy_Y(n))) return input;
    float2 e=pm_pair_add(pm_pair_add(pm_pair_mul(pm_pair(3.0f),pmvp_log2(lab.x)),pmvp_log2(pm_pair(peak))),make_float2(2.4739310741424561f,1.1334516436534159e-07f));
    float2 de=pm_pair_mul(pm_pair_mul(pm_pair(amount),make_float2(-0.014999999664723873f,-3.3527612630646075e-10f)),pm_pair_mul(pm_pair_mul(pmvp_response(lab.x,c,power),pmvpy_tone(e,shadow,sr,highlight,hr)),keep));
    if (!pm_finite(de.x)||!pm_finite(de.y)||(de.x==0.0f&&de.y==0.0f)) return input;
    float2 cg=pmvp_exp2(pm_pair_mul(pm_pair_mul(pm_pair(chroma),make_float2(0.0024999999441206455f,5.5879354528970415e-11f)),pmvp_abs(de)));
    pmvp3 shape=chroma==0.0f ? input : pmvpy_shape(input,cg);
    pmvp3 out=pmvp_scale(shape,pmvp_exp2(de));
    return pmvp_finite(out)?out:input;
}
// FIXED-Q COMPARISON ONLY. No clipping, no product/Host qualification.
typedef struct {
    pmvp3 lab; pmvpy_poly p; float2 yi; float2 dp; float2 chroma;
    float2 lo; float2 hi; float2 prelo; float2 prehi; float2 lms_confidence; int status;
} pmvq_state;
__DEVICE__ float2 pmvq_lms_confidence_from(pmvp3 lms) {
    float2 a=pmvp_abs(lms.x),b=pmvp_abs(lms.y),c=pmvp_abs(lms.z);
    float2 low=pmvp_ge(a,b)?b:a;low=pmvp_ge(low,c)?c:low;
    float2 high=pmvp_ge(a,b)?a:b;high=pmvp_ge(high,c)?high:c;
    if (!pmvp_positive(high)) return pm_pair(0.0f);
    return pmvp_smooth(pm_pair(0.0f),make_float2(0.0010000000474974513f,-4.7497451284572723e-11f),pm_pair_div(low,high));
}
__DEVICE__ float2 pmvq_lms_confidence(pmvp3 n) {
    return pmvq_lms_confidence_from(pmvp_xyz_lms(pmvp_dwg_xyz(n)));
}
__DEVICE__ pmvpy_interval pmvq_bounds(pmvpy_poly p) {
    float2 critical=pmvpy_critical(p);float points[4];int n=0;
    points[n++]=0.0f;
    if (critical.x>0.0f&&critical.x<64.0f&&pm_finite(critical.x)) points[n++]=critical.x;
    if (critical.y>0.0f&&critical.y<64.0f&&pm_finite(critical.y)&&critical.y!=critical.x) points[n++]=critical.y;
    points[n++]=64.0f;
    pmvpy_interval result;result.lower=pm_pair(0.0f);result.upper=pm_pair(64.0f);
    float from=1.0f;
    for (int i=n-1;i>=0;i--) {
        float to=points[i];if (to>=1.0f) continue;
        if (!pmvp_positive(pmvpy_eval(p,to))) {result.lower=pmvpy_boundary(p,from,to);break;}
        from=to;
    }
    from=1.0f;
    for (int i=0;i<n;i++) {
        float to=points[i];if (to<=1.0f) continue;
        if (!pmvp_positive(pmvpy_eval(p,to))) {result.upper=pmvpy_boundary(p,from,to);break;}
        from=to;
    }
    return result;
}
__DEVICE__ pmvpy_poly pmvq_negpoly(pmvpy_poly p) {
    p.a=pm_pair_neg(p.a);p.b=pm_pair_neg(p.b);p.c=pm_pair_neg(p.c);p.d=pm_pair_neg(p.d);return p;
}
__DEVICE__ pmvpy_interval pmvq_virtual_roots(pmvpy_poly p) {
    pmvpy_interval r;r.lower=pm_pair(-1.0f);r.upper=pm_pair(-1.0f);
    float2 a=p.c,b=p.b,c=p.a;
    if (a.x==0.0f&&a.y==0.0f) {
        if (b.x!=0.0f||b.y!=0.0f) r.lower=pm_pair_div(pm_pair_neg(c),b);
        return r;
    }
    float2 disc=pmvp_sub(pm_pair_mul(b,b),pm_pair_mul(pm_pair(4.0f),pm_pair_mul(a,c)));
    if (!pmvp_ge(disc,pm_pair(0.0f))) {
        r.lower=pm_pair_div(pm_pair_neg(b),pm_pair_mul(pm_pair(2.0f),a));r.upper=r.lower;return r;
    }
    float2 root=pm_pair_sqrt(disc);
    float2 q=pm_pair_mul(pm_pair(-0.5f),pm_pair_add(b,pmvp_ge(b,pm_pair(0.0f))?root:pm_pair_neg(root)));
    if (q.x==0.0f&&q.y==0.0f) {r.lower=pm_pair_div(pm_pair_neg(b),pm_pair_mul(pm_pair(2.0f),a));r.upper=r.lower;return r;}
    float2 x=pm_pair_div(q,a),y=pm_pair_div(c,q);
    r.lower=pmvp_ge(y,x)?x:y;r.upper=pmvp_ge(y,x)?y:x;return r;
}
__DEVICE__ pmvpy_interval pmvq_add_boundary(pmvpy_interval interval,float2 root) {
    if (!pm_finite(root.x)||!pm_finite(root.y)||!pmvp_ge(root,pm_pair(0.0f))||!pmvp_ge(pm_pair(64.0f),root)) return interval;
    float2 delta=pmvp_sub(root,pm_pair(1.0f));
    if (pmvp_ge(make_float2(1.000000013351432e-10f,-1.3351431923585892e-18f),pmvp_abs(delta))) {interval.lower=pm_pair(1.0f);interval.upper=pm_pair(1.0f);return interval;}
    if (pmvp_positive(delta)) {if (pmvp_ge(interval.upper,root)) interval.upper=root;}
    else if (pmvp_ge(root,interval.lower)) interval.lower=root;
    return interval;
}
// Share identical LMS work; neutral Chroma needs no polynomial geometry.
__DEVICE__ pmvq_state pmvq_prepare_base(pmvp3 n) {
    pmvq_state z;z.status=0;
    pmvp3 xyz=pmvp_dwg_xyz(n);z.yi=xyz.y;
    pmvp3 lms=pmvp_xyz_lms(xyz);
    z.lms_confidence=pmvq_lms_confidence_from(lms);
    z.lab=pmvp_root_lab(pmvp_make(pm_pair_cbrt(lms.x),pm_pair_cbrt(lms.y),pm_pair_cbrt(lms.z)));
    z.chroma=pm_pair(0.0f);
    if (!pmvp_positive(z.lab.x)||!pmvp_finite(z.lab)) return z;
    z.chroma=pmvp_chroma(z.lab);
    if (!pmvp_positive(z.yi)||!pmvp_positive(z.chroma)) return z;
    z.status=1;return z;
}
__DEVICE__ pmvq_state pmvq_prepare_geometry(pmvq_state z,int continued,int density_shape) {
    if (z.status==0) return z;
    z.p=pmvpy_polynomial(z.lab,z.yi);
    z.p.a=pm_pair_add(z.p.a,pm_pair_mul(z.yi,pm_pair(0.25f)));
    float2 sum=pm_pair_add(pm_pair_add(z.p.a,z.p.b),pm_pair_add(z.p.c,z.p.d));
    // Delta reconstruction makes the original sample the exact g=1 anchor.
    z.p.a=pm_pair_add(z.p.a,pmvp_sub(z.yi,sum));
    z.dp=pm_pair_add(z.p.b,pm_pair_add(pm_pair_mul(pm_pair(2.0f),z.p.c),pm_pair_mul(pm_pair(3.0f),z.p.d)));
    pmvpy_poly floor=z.p;floor.a=pmvp_sub(floor.a,pm_pair_mul(z.yi,pm_pair(0.25f)));
    pmvpy_poly der;der.a=z.p.b;der.b=pm_pair_mul(pm_pair(2.0f),z.p.c);der.c=pm_pair_mul(pm_pair(3.0f),z.p.d);der.d=pm_pair(0.0f);
    pmvpy_interval pb=pmvq_bounds(floor);
    if (continued) {
        pmvpy_interval roots=pmvq_virtual_roots(der);
        pb=pmvq_add_boundary(pb,roots.lower);pb=pmvq_add_boundary(pb,roots.upper);
    }
    z.prelo=pb.lower;z.prehi=pb.upper;z.lo=pb.lower;z.hi=pb.upper;z.status=1;
    // PreSat does not consume the following Density-only bounds/feasibility.
    if (!density_shape) return z;
    pmvpy_poly N;N.a=pm_pair_mul(pm_pair(3.0f),z.p.a);N.b=pm_pair_mul(pm_pair(2.0f),z.p.b);N.c=z.p.c;N.d=pm_pair(0.0f);
    float2 N1=pmvpy_eval(N,1.0f);float2 tolerance=pm_pair_mul(z.yi,make_float2(9.999999960041972e-13f,3.9958027796366288e-21f));
    if (!pmvp_positive(pmvp_sub(pmvp_abs(z.dp),tolerance))||!pmvp_positive(pmvp_sub(N1,tolerance))) return z;
    if (continued) {
        pmvpy_interval nb=pmvq_virtual_roots(N);
        pb=pmvq_add_boundary(pb,nb.lower);pb=pmvq_add_boundary(pb,nb.upper);z.lo=pb.lower;z.hi=pb.upper;
    } else {
        if (!pmvp_positive(z.dp)) der=pmvq_negpoly(der);
        pmvpy_interval nb=pmvq_bounds(N),db=pmvq_bounds(der);
        if (pmvp_ge(nb.lower,z.lo)) z.lo=nb.lower;
        if (pmvp_ge(db.lower,z.lo)) z.lo=db.lower;
        if (pmvp_ge(z.hi,nb.upper)) z.hi=nb.upper;
        if (pmvp_ge(z.hi,db.upper)) z.hi=db.upper;
    }
    if (!pmvp_positive(pmvp_sub(pmvp_sub(pm_pair(1.0f),z.lo),make_float2(1.000000013351432e-10f,-1.3351431923585892e-18f)))||
        !pmvp_positive(pmvp_sub(pmvp_sub(z.hi,pm_pair(1.0f)),make_float2(1.000000013351432e-10f,-1.3351431923585892e-18f)))) return z;
    z.status=2;return z;
}
__DEVICE__ pmvq_state pmvq_prepare(pmvp3 n,int continued) {
    return pmvq_prepare_geometry(pmvq_prepare_base(n),continued,1);
}
// Only skip legacy zero-times-intermediate expressions where their values
// are bounded. Unusual accepted pairs keep the original geometry/q path.
__DEVICE__ int pmvq_neutral_fast_safe(pmvp3 n,pmvq_state st) {
    return st.yi.x>=1.0e-12f&&_fabs(n.x.x)<=2.0f&&_fabs(n.y.x)<=2.0f&&_fabs(n.z.x)<=2.0f&&
        _fabs(n.x.y)<=0.00001f&&_fabs(n.y.y)<=0.00001f&&_fabs(n.z.y)<=0.00001f&&
        _fabs(st.lab.x.x)<=16.0f&&_fabs(st.lab.y.x)<=16.0f&&_fabs(st.lab.z.x)<=16.0f&&
        _fabs(st.lab.x.y)<=0.00001f&&_fabs(st.lab.y.y)<=0.00001f&&_fabs(st.lab.z.y)<=0.00001f;
}
// Reconstruction delta is evaluated directly rather than subtracting two
// nearly equal inverse transforms. This also supports tiny control changes.
__DEVICE__ float2 pmvq_cube_delta(float2 root,float2 u,float2 t) {
    float2 v=pm_pair_mul(u,t);
    float2 b=pm_pair_add(pm_pair_mul(pm_pair(3.0f),pm_pair_mul(root,root)),
        pm_pair_mul(v,pm_pair_add(pm_pair_mul(pm_pair(3.0f),root),v)));
    return pm_pair_mul(v,b);
}
__DEVICE__ pmvp3 pmvq_delta(pmvp3 lab,float2 t) {
    pmvp3 root=pmvp_lab_root(lab),u=pmvp_lab_root(pmvp_make(pm_pair(0.0f),lab.y,lab.z));
    pmvp3 cubes=pmvp_make(pmvq_cube_delta(root.x,u.x,t),pmvq_cube_delta(root.y,u.y,t),pmvq_cube_delta(root.z,u.z,t));
    return pmvp_xyz_dwg(pmvp_lms_xyz(cubes));
}
__DEVICE__ float2 pmvq_deltaY(pmvq_state st,float2 t) {
    float2 quadratic=pm_pair_add(st.p.c,pm_pair_mul(pm_pair(3.0f),st.p.d));
    return pm_pair_mul(t,pm_pair_add(st.dp,pm_pair_mul(t,pm_pair_add(quadratic,pm_pair_mul(t,st.p.d)))));
}
__DEVICE__ float2 pmvq_expm1(float2 log2e) {
    if (pmvp_ge(pm_pair(0.25f),pmvp_abs(log2e))) {
        float2 r=pm_pair_mul(log2e,make_float2(0.69314718246459961f,-1.904654323148236e-09f));
        float2 y=make_float2(2.0876755879584152e-09f,1.1082839478332097e-16f);
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(2.5052107943679403e-08f,4.4176231769972645e-16f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(2.755731998149713e-07f,-7.5751124208094317e-15f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(2.7557318844628753e-06f,3.7935713937038186e-14f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(2.4801587642286904e-05f,-3.406996025904184e-13f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.00019841270113829523f,-2.7255968207233472e-12f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.0013888889225199819f,-3.3631092919220174e-11f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.0083333337679505348f,-4.3461720160287154e-10f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.041666667908430099f,-1.2417634351336027e-09f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.1666666716337204f,-4.9670537405344106e-09f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(0.5f,0.0f));
        y=pm_pair_add(pm_pair_mul(y,r),make_float2(1.0f,0.0f));

        return pm_pair_mul(r,y);
    }
    return pmvp_sub(pmvp_exp2(log2e),pm_pair(1.0f));
}
__DEVICE__ float2 pmvq_tanh(float2 positive) {
    float2 em1=pmvq_expm1(pm_pair_mul(positive,make_float2(-2.885390043258667f,-3.8519259781821802e-08f)));
    return pm_pair_div(pm_pair_neg(em1),pm_pair_add(pm_pair(2.0f),em1));
}
__DEVICE__ float2 pmvq_domain(pmvq_state st,float y_width,int conditioned) {
    if (st.status==0) return pm_pair(0.0f);
    float2 confidence=pm_pair_mul(pmvp_smooth(pm_pair(0.0f),pm_pair(y_width),st.yi),
        pmvp_smooth(pm_pair(0.0f),pm_pair(0.1f),st.lab.x));
    return conditioned>1?pm_pair_mul(confidence,st.lms_confidence):confidence;
}
__DEVICE__ float2 pmvq_q_condition(pmvq_state st) {
    float2 n1=pm_pair_add(pm_pair_mul(pm_pair(3.0f),st.p.a),pm_pair_add(pm_pair_mul(pm_pair(2.0f),st.p.b),st.p.c));
    return pm_pair_mul(pmvp_smooth(pm_pair(0.0f),pm_pair(0.02f),pm_pair_div(pmvp_abs(st.dp),st.yi)),
        pmvp_smooth(pm_pair(0.0f),pm_pair(0.1f),pm_pair_div(n1,pm_pair_mul(pm_pair(3.0f),st.yi))));
}
__DEVICE__ float2 pmvq_boundary_fade(float2 lo,float2 hi) {
    float2 a=pmvp_sub(pm_pair(1.0f),lo),b=pmvp_sub(hi,pm_pair(1.0f));
    return pmvp_smooth(pm_pair(0.0f),pm_pair(0.1f),pmvp_ge(a,b)?b:a);
}
__DEVICE__ float2 pmvq_knee(float2 distance,float2 headroom) {
    if (!pmvp_positive(headroom)) return pm_pair(0.0f);
    float2 half=pm_pair_mul(headroom,pm_pair(0.5f));
    if (pmvp_ge(half,distance)) return distance;
    return pm_pair_add(half,pm_pair_mul(half,pmvq_tanh(pmvp_sub(pm_pair_div(distance,half),pm_pair(1.0f)))));
}
__DEVICE__ float2 pmvq_continued_gain(float2 request,float2 lo,float2 hi) {
    if (!pmvp_ge(request,pm_pair(1.0f))) {
        if (!pmvp_ge(request,pm_pair(0.0f))) request=pm_pair(0.0f);
        return pm_pair_add(lo,pm_pair_mul(pmvp_sub(pm_pair(1.0f),lo),request));
    }
    return pm_pair_add(pm_pair(1.0f),pmvq_knee(pmvp_sub(request,pm_pair(1.0f)),pmvp_sub(hi,pm_pair(1.0f))));
}
__DEVICE__ float2 pmvq_soft_gain(float2 request,float2 lo,float2 hi) {
    if (pmvp_ge(request,pm_pair(1.0f))) {
        float2 h=pmvp_sub(hi,pm_pair(1.0f));
        if (!pmvp_positive(h)) return pm_pair(1.0f);
        return pm_pair_add(pm_pair(1.0f),pm_pair_mul(h,pmvq_tanh(pm_pair_div(pmvp_sub(request,pm_pair(1.0f)),h))));
    }
    if (!pmvp_positive(lo)) return pmvp_ge(request,pm_pair(0.0f))?request:pm_pair(0.0f);
    float2 h=pmvp_sub(pm_pair(1.0f),lo);
    if (!pmvp_positive(h)) return pm_pair(1.0f);
    return pmvp_sub(pm_pair(1.0f),pm_pair_mul(h,pmvq_tanh(pm_pair_div(pmvp_sub(pm_pair(1.0f),request),h))));
}
__DEVICE__ float2 pmvq_full_gain(float2 request,float2 lo,float2 hi) {
    if (pmvp_ge(request,pm_pair(1.0f))) return pmvq_soft_gain(request,lo,hi);
    float2 h=pmvp_sub(pm_pair(1.0f),lo);
    if (!pmvp_positive(h)) return pm_pair(1.0f);
    return pmvp_sub(pm_pair(1.0f),pm_pair_mul(h,pmvq_tanh(pm_pair_div(pmvp_sub(pm_pair(1.0f),request),h))));
}
__DEVICE__ pmvp3 pmvq_presat_ready(pmvp3 input,pmvp3 n,float peak,pmvq_state st,float pre,float2 keep,int held,int conditioned,float y_width,int mode) {
    if (pre==100.0f||!pmvp_positive(keep)) return input;
    st=pmvq_prepare_geometry(st,mode==2,0);if (st.status==0) return input;
    float2 request=pm_pair_add(pm_pair(1.0f),pm_pair_mul(pmvp_sub(pm_pair_div(pm_pair(pre),pm_pair(100.0f)),pm_pair(1.0f)),keep));
    if (conditioned) request=pm_pair_add(pm_pair(1.0f),pm_pair_mul(pmvp_sub(request,pm_pair(1.0f)),pmvq_domain(st,y_width,conditioned)));
    if (mode==2) request=pm_pair_add(pm_pair(1.0f),pm_pair_mul(pmvp_sub(request,pm_pair(1.0f)),pmvq_boundary_fade(st.prelo,st.prehi)));
    float2 gain=mode==2?pmvq_continued_gain(request,st.prelo,st.prehi):pmvq_soft_gain(request,st.prelo,st.prehi);
    pmvp3 z=pmvp_add(n,pmvq_delta(st.lab,pmvp_sub(gain,pm_pair(1.0f))));
    float2 yz=pmvpy_Y(z);
    if (!pmvp_positive(yz)||!pmvp_ge(yz,pm_pair_mul(st.yi,make_float2(0.25f,-2.4999999292951713e-10f)))) return input;
    pmvp3 out=pmvp_scale(z,held?pm_pair_mul(pm_pair(peak),pm_pair_div(st.yi,yz)):pm_pair(peak));
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmvq_presat(pmvp3 input,float pre,float2 keep,int held,int conditioned,float y_width,int mode) {
    if (pre==100.0f||!pmvp_positive(keep)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(input,peak);
    return pmvq_presat_ready(input,n,peak,pmvq_prepare_base(n),pre,keep,held,conditioned,y_width,mode);
}
__DEVICE__ float2 pmvq_skin_lab(pmvp3 lab,float2 c) {
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)||!pmvp_positive(c)) return pm_pair(0.0f);
    float2 cosine=pm_pair_div(pm_pair_add(pm_pair_mul(lab.y,make_float2(0.69936877489089966f,7.3722203897119698e-09f)),pm_pair_mul(lab.z,make_float2(0.71476101875305176f,-5.269663372331479e-09f))),c);
    float2 hue=pmvp_smooth(make_float2(0.90630781650543213f,-2.9468782192232368e-08f),make_float2(0.9902680516242981f,1.7117272266276018e-08f),cosine);
    float2 s=pm_pair_div(c,lab.x);
    return pm_pair_mul(hue,pmvp_smooth(pm_pair(0.0f),make_float2(0.079999998211860657f,1.7881393449270533e-09f),s));
}
typedef struct {pmvp3 presat;float2 keep_sat;float2 keep_density;} pmvq_input_result;
__DEVICE__ pmvq_input_result pmvq_input_stages(pmvp3 input,float peak,float pre,float sat_skin,float density_skin) {
    pmvq_input_result result;result.keep_sat=pm_pair(1.0f);result.keep_density=pm_pair(1.0f);result.presat=input;
    if (sat_skin==0.0f&&density_skin==0.0f) {
        result.presat=pmvq_presat(input,pre,result.keep_sat,0,2,0.001f,2);return result;
    }
    pmvp3 n=pmvp_div(input,peak);pmvq_state base=pmvq_prepare_base(n);
    float3 high=pmvp_high(input);float2 color_mask=pm_pair(0.0f);
    // This is the original encoded-source color mask, not a post-stage mask.
    // Skin eligibility does not require positive Y; stage eligibility still does.
    if (!(high.x==high.y&&high.y==high.z)) color_mask=pmvq_skin_lab(base.lab,base.chroma);
    float2 mask=pm_pair_mul(color_mask,base.lms_confidence);
    // A stage's exact zero protection must remain unprotected independently,
    // including exceptional mask values affecting only the other stage.
    if (sat_skin!=0.0f) result.keep_sat=pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_div(pm_pair(sat_skin),pm_pair(100.0f)),mask));
    if (density_skin!=0.0f) result.keep_density=pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_div(pm_pair(density_skin),pm_pair(100.0f)),mask));
    result.presat=pmvq_presat_ready(input,n,peak,base,pre,result.keep_sat,0,2,0.001f,2);
    return result;
}
__DEVICE__ float2 pmvq_response(float2 l,float2 c,float p) {
    if (p!=1.0f&&p!=2.0f&&p!=3.0f&&p!=4.0f) return pmvp_response(l,c,p);
    float2 center=pm_pair_mul(l,pm_pair(0.25f));int low=pmvp_ge(center,c);
    float2 q=low?pm_pair_div(c,center):pm_pair_div(center,c),v=pm_pair(0.0f);
    if (pmvp_positive(q)) {
        if (!pm_finite(q.x)||!pm_finite(q.y)||q.x<=0.0f||_fabs(q.y)>_fabs(q.x)*0.00001f||!pmvp_ge(pm_pair(1.0f),q)) return pmvp_response(l,c,p);
        if (p==1.0f) v=q;
        else {float2 square=pm_pair_mul(q,q);v=p==2.0f?square:(p==3.0f?pm_pair_mul(square,q):pm_pair_mul(square,square));}
    }
    return low?pm_pair_div(v,pm_pair_add(pm_pair(1.0f),v)):pm_pair_div(pm_pair(1.0f),pm_pair_add(pm_pair(1.0f),v));
}
__DEVICE__ float2 pmvq_amax(pmvq_state st,float power,float2 keep,int conditioned,float y_width) {
    if (st.status==0||!pmvp_positive(keep)) return pm_pair(0.0f);
    // The fixed calibration envelope is the full +/-300 UI range. Dividing
    // actual amount by300 below retains the previous exposure effect per100.
    float2 a=pm_pair_mul(pm_pair(4.5f),pm_pair_mul(pmvq_response(st.lab.x,st.chroma,power),keep));
    return conditioned?pm_pair_mul(a,pmvq_domain(st,y_width,conditioned)):a;
}
__DEVICE__ float2 pmvq_coefficient(pmvq_state st,float chroma,float2 amax,int mode) {
    if (st.status!=2||chroma==0.0f||!pmvp_positive(amax)) return pm_pair(0.0f);
    if (mode==0) {
        float2 bound=chroma>0.0f?st.hi:st.lo;
        float2 ratio=pm_pair_div(pmvpy_eval_pair(st.p,bound),st.yi);
        if (!pmvp_ge(ratio,pm_pair(0.25f))) ratio=pm_pair(0.25f);
        float2 capacity=pm_pair_div(pmvp_abs(pmvp_log2(ratio)),amax);
        float2 magnitude=pm_pair_mul(pm_pair_div(pm_pair_mul(pm_pair(0.5f),capacity),pm_pair_add(pm_pair(0.5f),capacity)),pm_pair_div(pm_pair(_fabs(chroma)),pm_pair(100.0f)));
        return (pmvp_positive(st.dp)==(chroma>0.0f))?magnitude:pm_pair_neg(magnitude);
    }
    // Optional calibration: match a full-dose relative-C request before the
    // q cap. It is still fixed across actual Density and exposure.
    float2 request=pm_pair_add(pm_pair(1.0f),pmvq_expm1(pm_pair_mul(pm_pair_mul(pm_pair(chroma),make_float2(0.0024999999441206455f,5.5879354528970415e-11f)),amax)));
    float2 full=mode==2?pmvq_continued_gain(request,st.lo,st.hi):pmvq_full_gain(request,st.lo,st.hi);
    float2 ratio=pm_pair_add(pm_pair(1.0f),pm_pair_div(pmvq_deltaY(st,pmvp_sub(full,pm_pair(1.0f))),st.yi));
    if (!pmvp_positive(ratio)) return pm_pair(0.0f);
    float2 raw=pm_pair_div(pmvp_log2(ratio),amax);
    float2 q=pm_pair_mul(pm_pair(0.5f),pmvq_tanh(pm_pair_mul(pm_pair(2.0f),pmvp_abs(raw))));
    return pmvp_positive(raw)?q:pm_pair_neg(q);
}
__DEVICE__ float2 pmvq_invert(pmvq_state st,float2 target,int positive_chroma) {
    if (target.x==0.0f&&target.y==0.0f) return pm_pair(0.0f);
    float2 left=positive_chroma?pm_pair(0.0f):pmvp_sub(st.lo,pm_pair(1.0f));
    float2 right=positive_chroma?pmvp_sub(st.hi,pm_pair(1.0f)):pm_pair(0.0f);
    for (int i=0;i<80;i++) {
        float2 middle=pm_pair_mul(pm_pair_add(left,right),pm_pair(0.5f));
        if ((middle.x==left.x&&middle.y==left.y)||(middle.x==right.x&&middle.y==right.y)) break;
        float2 difference=pmvp_sub(pmvq_deltaY(st,middle),target);
        if ((!pmvp_ge(difference,pm_pair(0.0f)))==pmvp_positive(st.dp)) left=middle;else right=middle;
    }
    return pm_pair_mul(pm_pair_add(left,right),pm_pair(0.5f));
}
__DEVICE__ float2 pmvq_tone(float2 e,float shadow,float sr,float highlight,float hr,int skip_zero) {
    float2 s=pm_pair(1.0f),h=pm_pair(1.0f);
    if (shadow!=0.0f||!skip_zero) {
        float2 es=pm_pair_add(pm_pair(-7.0f),pm_pair_mul(pm_pair(sr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
        float2 ms=pmvp_sub(pm_pair(1.0f),pmvp_smooth(pmvp_sub(es,pm_pair(6.0f)),pm_pair_add(es,pm_pair(6.0f)),e));
        s=pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(shadow),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),ms));
    }
    if (highlight!=0.0f||!skip_zero) {
        float2 eh=pmvp_sub(pm_pair(7.0f),pm_pair_mul(pm_pair(hr),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
        float2 mh=pmvp_smooth(pmvp_sub(eh,pm_pair(6.0f)),pm_pair_add(eh,pm_pair(6.0f)),e);
        h=pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_mul(pm_pair(highlight),make_float2(0.0099999997764825821f,2.2351741811588166e-10f)),mh));
    }
    return pm_pair_mul(s,h);
}
// Highlight protection follows actual post-Comp linear Y, not a claim
// to detect sensor/display clipping. Twelve stops preserve Y and L order
// at the full +/-300 Density dose with fixed-q Chroma compensation.
__DEVICE__ float2 pmvq_highlight_keep(float2 normalized_y,float peak,float highlight,float range) {
    if (highlight==0.0f) return pm_pair(1.0f);
    float2 ey=pm_pair_add(pm_pair_add(pmvp_log2(normalized_y),pmvp_log2(pm_pair(peak))),make_float2(2.4739310741424561f,1.1418995615741778e-07f));
    if (!pm_finite(ey.x)||!pm_finite(ey.y)) return pm_pair(0.0f);
    float2 full=pmvp_sub(pm_pair(8.0f),pm_pair_mul(pm_pair(range),make_float2(0.059999998658895493f,1.341104505225843e-09f)));
    if (highlight==100.0f&&pmvp_ge(ey,full)) return pm_pair(0.0f);
    float2 mask=pmvp_smooth(pmvp_sub(full,pm_pair(12.0f)),full,ey);
    if (mask.x==0.0f&&mask.y==0.0f) return pm_pair(1.0f);
    return pmvp_sub(pm_pair(1.0f),pm_pair_mul(pm_pair_div(pm_pair(highlight),pm_pair(100.0f)),mask));
}
__DEVICE__ pmvp3 pmvq_density(pmvp3 input,float amount,float chroma,float power,float shadow,float sr,float highlight,float hr,float2 keep,int mode,int conditioned,float y_width) {
    if (amount==0.0f||!pmvp_positive(keep)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(input,peak);pmvq_state st=pmvq_prepare_base(n);if (st.status==0) return input;
    float2 amax=pmvq_amax(st,power,keep,conditioned,y_width);
    if (!pmvp_positive(amax)) return input;
    float2 tone=pm_pair(1.0f);
    int finite_exposure=st.lab.x.x>=1.0e-12f&&st.lab.x.x<=16.0f&&
        peak>=7.5231638452626401e-37f&&peak<=1.3292279957849159e36f&&
        _fabs(st.lab.x.y)<=st.lab.x.x*0.00001f;
    if (highlight==0.0f) {
        // Keep the original zero-highlight branch and exceptional behavior.
        if (shadow!=0.0f||highlight!=0.0f||!finite_exposure) {
            float2 e=pm_pair_add(pm_pair_add(pm_pair_mul(pm_pair(3.0f),pmvp_log2(st.lab.x)),pmvp_log2(pm_pair(peak))),make_float2(2.4739310741424561f,1.1334516436534159e-07f));
            tone=pmvq_tone(e,shadow,sr,highlight,hr,finite_exposure&&pm_finite(e.x)&&pm_finite(e.y));
        }
    } else {
        tone=pmvq_highlight_keep(st.yi,peak,highlight,hr);
        // Exact full protection stops the complete Density/Chroma stage.
        if (!pmvp_positive(tone)) return input;
        if (shadow!=0.0f||!finite_exposure) {
            float2 e=pm_pair_add(pm_pair_add(pm_pair_mul(pm_pair(3.0f),pmvp_log2(st.lab.x)),pmvp_log2(pm_pair(peak))),make_float2(2.4739310741424561f,1.1334516436534159e-07f));
            tone=pm_pair_mul(tone,pmvq_tone(e,shadow,sr,0.0f,hr,finite_exposure&&pm_finite(e.x)&&pm_finite(e.y)));
        }
    }
    float2 de=pm_pair_mul(pm_pair_mul(pm_pair_div(pm_pair(-amount),pm_pair(300.0f)),amax),tone);
    if (!pm_finite(de.x)||!pm_finite(de.y)||(de.x==0.0f&&de.y==0.0f)) return input;
    float2 q=pm_pair(0.0f);
    float2 t=pm_pair(0.0f);
    int neutral_fast=chroma==0.0f&&pmvq_neutral_fast_safe(n,st);
    if (!neutral_fast) {
        st=pmvq_prepare_geometry(st,mode==2,1);
        // Preserve the nominal100 Chroma response instead of weakening it
        // when the Density range expands. Strong doses can reach the existing
        // connected shape boundary; the monotone solver then stays there.
        q=pmvq_coefficient(st,chroma,pm_pair_div(amax,pm_pair(3.0f)),mode);
        if (conditioned) q=pm_pair_mul(q,pmvq_q_condition(st));
        if (mode==2) q=pm_pair_mul(q,pmvq_boundary_fade(st.lo,st.hi));
        float2 target=pm_pair_mul(st.yi,pmvq_expm1(pm_pair_mul(q,pmvp_abs(de))));
        t=pmvq_invert(st,target,chroma>0.0f);
    }
    pmvp3 shape=pmvp_add(n,pmvq_delta(st.lab,t));
    float2 ys=pmvpy_Y(shape);
    if (!pmvp_positive(ys)) return pmvp_scale(input,pmvp_exp2(de));
    pmvp3 out=pmvp_scale(shape,pm_pair_mul(pm_pair(peak),pm_pair_mul(pmvp_exp2(de),pm_pair_div(st.yi,ys))));
    return pmvp_finite(out)?out:input;
}
// PRECISION REVISION ONLY: immutable centered knee and signed/proxy policy.
__DEVICE__ float2 pmcc_max(float2 a,float2 b) {return pmvp_ge(a,b)?a:b;}
__DEVICE__ float2 pmcc_min(float2 a,float2 b) {return pmvp_ge(a,b)?b:a;}
__DEVICE__ float2 pmcc_Y(pmvp3 v) {return pm_precise_dot3(v.x,v.y,v.z,make_float2(0.26270020008087158f,1.1930395504844427e-08f),make_float2(0.67799806594848633f,5.5703844870080843e-09f),make_float2(0.059301715344190598f,1.1256713616791814e-09f));}
__DEVICE__ pmvp3 pmcc_mix(pmvp3 source,pmvp3 processed,float2 keep) {
    if (keep.x==0.0f&&keep.y==0.0f) return source;
    if (keep.x==1.0f&&keep.y==0.0f) return processed;
    pmvp3 out=pmvp_add(pmvp_scale(source,pmvp_sub(pm_pair(1.0f),keep)),pmvp_scale(processed,keep));
    return pmvp_finite(out)?out:source;
}
__DEVICE__ pmvp3 pmcc_dwg_rec(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.1303021907806396f,-1.3466571857634335e-08f),make_float2(-0.020392844453454018f,3.2250035628123008e-10f),make_float2(-0.10990932583808899f,-2.0912465925615464e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.025547057390213013f,2.8284748848639296e-10f),make_float2(1.3108493089675903f,1.1838816815767927e-08f),make_float2(-0.28530225157737732f,-1.4099250655874584e-08f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.092598602175712585f,-1.9172564230673927e-09f),make_float2(-0.16465303301811218f,6.7129838354773597e-09f),make_float2(1.2572516202926636f,9.4415577578388366e-09f))); }
__DEVICE__ pmvp3 pmcc_rec_dwg(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(0.892112135887146f,-1.6787125800554747e-08f),make_float2(0.024369174614548683f,-3.8323273027218718e-10f),make_float2(0.083518706262111664f,-1.1320440418405298e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.032616604119539261f,-4.3549435585488183e-10f),make_float2(0.78613752126693726f,-1.2248216885168972e-09f),make_float2(0.18124587833881378f,4.6614694049207372e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.069977052509784698f,-4.3082207246136761e-10f),make_float2(0.10474949330091476f,-3.5322176572538666e-09f),make_float2(0.82527345418930054f,1.3520976560599252e-09f))); }
__DEVICE__ pmvp3 pmcc_rec_lms(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(0.61675578355789185f,1.3075526217320999e-09f),make_float2(0.36019840836524963f,-7.1387863953553676e-09f),make_float2(0.023045813664793968f,2.4329833633873754e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.26513305306434631f,6.3282905027328695e-09f),make_float2(0.63583934307098389f,2.8996865131247773e-08f),make_float2(0.099027566611766815f,1.9277473506384979e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.10010263323783875f,-3.7174904543579856e-09f),make_float2(0.20390652120113373f,1.415480677113834e-09f),make_float2(0.69599086046218872f,-1.2599151388847929e-08f))); }
__DEVICE__ pmvp3 pmcc_lms_rec(pmvp3 v) { return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(2.139906644821167f,8.5613483857827077e-08f),make_float2(-1.2463895082473755f,1.4486758015408441e-08f),make_float2(0.10648276656866074f,-3.2426939189367232e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.8847358226776123f,-1.3080155403244476e-08f),make_float2(2.1632308959960938f,4.2365107422170922e-08f),make_float2(-0.27849510312080383f,5.1737020223541208e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-0.048573747277259827f,8.7681578664344784e-10f),make_float2(-0.45450314879417419f,-9.1992186090905648e-10f),make_float2(1.5030769109725952f,-1.4858055452648955e-08f))); }

__DEVICE__ pmvp3 pmcc_fallback(pmvp3 input,pmvp3 n,float peak,float threshold,float amount,float softness) {
    float2 energy=pm_pair_sqrt(pmcc_Y(pmvp_make(pm_pair_mul(n.x,n.x),pm_pair_mul(n.y,n.y),pm_pair_mul(n.z,n.z))));
    float2 dx=pmvp_sub(n.x,n.z),dy=pmvp_sub(n.y,n.z);
    float2 a=pm_pair_add(pm_pair_mul(dx,make_float2(0.20704919099807739f,-3.8784938871661012e-09f)),pm_pair_mul(dy,make_float2(-0.24661456048488617f,6.9042147277098564e-09f)));
    float2 b=pm_pair_add(pm_pair_mul(dx,make_float2(0.047521520406007767f,-1.2477570435209806e-09f)),pm_pair_mul(dy,make_float2(0.11405113339424133f,2.5031363232175252e-09f)));
    float2 c=pm_pair_sqrt(pm_pair_add(pm_pair_mul(a,a),pm_pair_mul(b,b)));
    if (!pmvp_positive(energy)||!pmvp_positive(c)||!pm_finite(energy.x)||!pm_finite(c.x)) return input;
    float2 scale=pm_continuous_scale_pair(energy,c,threshold,amount,softness);
    if (!pm_finite(scale.x)||!pm_finite(scale.y)||(scale.x==1.0f&&scale.y==0.0f)) return input;
    float2 range=pmvp_sub(pmcc_max(n.x,pmcc_max(n.y,n.z)),pmcc_min(n.x,pmcc_min(n.y,n.z)));
    float2 u=pm_pair_div(range,energy);
    float2 visibility=pmvp_ge(u,pm_pair(1.0f))?pm_pair(1.0f):pm_pair_mul(pm_pair_mul(u,u),pmvp_sub(pm_pair(3.0f),pm_pair_mul(pm_pair(2.0f),u)));
    float2 luminance=pmcc_Y(n);
    pmvp3 negative=pmvp_make(pmcc_max(pm_pair_neg(n.x),pm_pair(0.0f)),pmcc_max(pm_pair_neg(n.y),pm_pair(0.0f)),pmcc_max(pm_pair_neg(n.z),pm_pair(0.0f)));
    float2 anchor=pm_pair_add(luminance,pm_pair_mul(visibility,pmcc_Y(negative)));
    float2 d=pm_pair_mul(pmvp_sub(pm_pair(1.0f),scale),pm_pair(peak));
    pmvp3 delta=pmvp_scale(pmvp_make(pmvp_sub(anchor,n.x),pmvp_sub(anchor,n.y),pmvp_sub(anchor,n.z)),d);
    pmvp3 out=pmvp_add(input,pmcc_rec_dwg(delta));
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmcc_process(pmvp3 input,float threshold,float amount,float softness,int positive_edge) {
    if (amount==0.0f||!pmvp_finite(input)) return input;
    if (input.x.x==input.y.x&&input.x.y==input.y.y&&input.y.x==input.z.x&&input.y.y==input.z.y) return input;
    pmvp3 wide=pmcc_dwg_rec(input);
    if (!pmvp_finite(wide)) return input;
    float peak=pmv_peak(pmvp_high(wide));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(wide,peak);
    pmvp3 positive=pmvp_make(pmcc_max(n.x,pm_pair(0.0f)),pmcc_max(n.y,pm_pair(0.0f)),pmcc_max(n.z,pm_pair(0.0f)));
    pmvp3 negative=pmvp_make(pmcc_min(n.x,pm_pair(0.0f)),pmcc_min(n.y,pm_pair(0.0f)),pmcc_min(n.z,pm_pair(0.0f)));
    float2 positive_peak=pmcc_max(positive.x,pmcc_max(positive.y,positive.z));
    float2 P=pmcc_Y(positive),N=pm_pair_neg(pmcc_Y(negative));
    pmvp3 fallback=input;
    if (pmvp_positive(N)) fallback=pmcc_fallback(input,n,peak,threshold,amount,softness);
    if (!pmvp_positive(positive_peak)) return fallback;
    pmvp3 unit=pmvp_make(pm_pair_div(positive.x,positive_peak),pm_pair_div(positive.y,positive_peak),pm_pair_div(positive.z,positive_peak));
    pmvp3 lms=pmcc_rec_lms(unit);
    pmvp3 lab=pmvp_root_lab(pmvp_make(pm_pair_cbrt(lms.x),pm_pair_cbrt(lms.y),pm_pair_cbrt(lms.z)));
    float2 c=pmvp_chroma(lab);
    if (!pmvp_finite(lab)||!pmvp_positive(lab.x)||!pm_finite(c.x)) return input;
    float2 scale=pm_pair(1.0f);
    if (pmvp_positive(c)) scale=pm_continuous_scale_pair(lab.x,c,threshold,amount,softness);
    if (!pm_finite(scale.x)||!pm_finite(scale.y)) return input;
    if (scale.x==1.0f&&scale.y==0.0f&&pmvp_same(input,fallback)) return input;
    pmvp3 proxy=positive;
    if (!(scale.x==1.0f&&scale.y==0.0f)) {
        pmvp3 shape=pmvp_make(pm_pair(1.0f),pm_pair_div(pm_pair_mul(lab.y,scale),lab.x),pm_pair_div(pm_pair_mul(lab.z,scale),lab.x));
        pmvp3 roots=pmvp_lab_root(shape);
        pmvp3 cube=pmvp_make(pm_pair_mul(roots.x,pm_pair_mul(roots.x,roots.x)),pm_pair_mul(roots.y,pm_pair_mul(roots.y,roots.y)),pm_pair_mul(roots.z,pm_pair_mul(roots.z,roots.z)));
        pmvp3 rgb=pmcc_lms_rec(cube);float2 shapeY=pmcc_Y(rgb);
        if (!pmvp_finite(rgb)||!pmvp_positive(shapeY)) return input;
        proxy=pmvp_scale(rgb,pm_pair_div(P,shapeY));
        if (positive_edge&&(!pmvp_ge(proxy.x,pm_pair(0.0f))||!pmvp_ge(proxy.y,pm_pair(0.0f))||!pmvp_ge(proxy.z,pm_pair(0.0f)))) {
            float2 gray=pm_pair_mul(pmvp_sub(pm_pair(1.0f),scale),P);
            pmvp3 safe=pmvp_add(pmvp_scale(positive,scale),pmvp_make(gray,gray,gray));
            float2 w=pm_pair(0.0f);
            if (!pmvp_ge(proxy.x,pm_pair(0.0f))&&pmvp_positive(pmvp_sub(safe.x,proxy.x))) w=pmcc_max(w,pm_pair_div(pm_pair_neg(proxy.x),pmvp_sub(safe.x,proxy.x)));
            if (!pmvp_ge(proxy.y,pm_pair(0.0f))&&pmvp_positive(pmvp_sub(safe.y,proxy.y))) w=pmcc_max(w,pm_pair_div(pm_pair_neg(proxy.y),pmvp_sub(safe.y,proxy.y)));
            if (!pmvp_ge(proxy.z,pm_pair(0.0f))&&pmvp_positive(pmvp_sub(safe.z,proxy.z))) w=pmcc_max(w,pm_pair_div(pm_pair_neg(proxy.z),pmvp_sub(safe.z,proxy.z)));
            w=pmcc_max(pm_pair(0.0f),pmcc_min(pm_pair(1.0f),w));
            proxy=pmcc_mix(proxy,safe,w);
        }
    }
    pmvp3 branch=pmvp_add(proxy,pmvp_scale(negative,scale));
    pmvp3 delta=pmvp_scale(pmvp_sub3(branch,n),pm_pair(peak));
    pmvp3 perceptual=pmvp_add(input,pmcc_rec_dwg(delta));
    if (!pmvp_finite(perceptual)) return input;
    pmvp3 out=pmvp_positive(N)?pmcc_mix(fallback,perceptual,pm_pair_div(P,pm_pair_add(P,N))):perceptual;
    return pmvp_finite(out)?out:input;
}
__DEVICE__ pmvp3 pmcc_process_masked(pmvp3 input,float threshold,float amount,float softness,float2 keep,int positive_edge) {
    if (amount==0.0f||!pmvp_positive(keep)) return input;
    pmvp3 processed=pmcc_process(input,threshold,amount,softness,positive_edge);
    if (pmvp_same(input,processed)) return input;
    return pmcc_mix(input,processed,keep);
}

// All RGB fields are scene-linear DWG float-pairs. Input/output transfer and
// primaries conversion, UI scope, encoded identity and alpha belong outside.
typedef struct {
    float2 r;float2 g;float2 b;
    float2 pre_r;float2 pre_g;float2 pre_b;
    float2 comp_r;float2 comp_g;float2 comp_b;
    int changed;int pre_changed;int comp_changed;
} pmc_core_result;
// Threshold is a practical 0..100 control, not vectorscope radius or raw S.
// Invert the existing knee so the reference target retention is linear in UI.
// Caller handles exact UI100 as a Comp-only no-op, including Knee100.
__DEVICE__ float pmc_threshold_raw(float threshold,float softness) {
    float2 u=pm_pair_div(pm_pair(threshold),pm_pair(100.0f));
    float2 k=pm_pair_div(pm_pair(softness),pm_pair(100.0f));
    float2 reference=make_float2(90.403160095214844f,-3.2403075653772979e-06f);
    if (pmvp_ge(pm_pair(1.0f),pm_pair_mul(u,pm_pair_add(pm_pair(1.0f),k)))) return pmvp_round(pm_pair_mul(reference,u));
    float2 a=pmvp_sub(pm_pair(1.0f),k),kr=pm_pair_mul(k,pmvp_sub(pm_pair(1.0f),u));
    float2 denominator=pm_pair_add(a,pm_pair_add(pm_pair_mul(pm_pair(2.0f),kr),
        pm_pair_mul(pm_pair(2.0f),pm_pair_sqrt(pm_pair_mul(kr,pm_pair_add(a,kr))))));
    return pmvp_round(pm_pair_div(reference,denominator));
}
__DEVICE__ pmc_core_result pmc_process_core(float2 r,float2 g,float2 b,
    float pre,float threshold,float compression,float softness,
    float density,float chroma,float response,float shadow,float sr,
    float highlight,float hr,float sat_skin,float density_skin,int density_bypass) {
    pmvp3 input=pmvp_make(r,g,b);pmc_core_result result;
    result.r=r;result.g=g;result.b=b;
    result.pre_r=r;result.pre_g=g;result.pre_b=b;
    result.comp_r=r;result.comp_g=g;result.comp_b=b;
    result.changed=0;result.pre_changed=0;result.comp_changed=0;
    if (!pmvp_finite(input)) return result;
    if (r.x==g.x&&r.y==g.y&&g.x==b.x&&g.y==b.y) return result;
    if (pre==100.0f&&(compression==0.0f||threshold==100.0f)&&(density==0.0f||density_bypass)) return result;
    if (!pm_finite(pre)||pre<0.0f||pre>200.0f ||
        !pm_finite(compression)||compression<0.0f||compression>100.0f ||
        !pm_finite(threshold)||threshold<0.0f||threshold>100.0f ||
        !pm_finite(softness)||softness<0.0f||softness>100.0f ||
        !pm_finite(density)||_fabs(density)>300.0f ||
        !pm_finite(chroma)||_fabs(chroma)>100.0f ||
        !pm_finite(response)||response<1.0f||response>4.0f ||
        !pm_finite(shadow)||shadow<0.0f||shadow>100.0f ||
        !pm_finite(sr)||sr<0.0f||sr>100.0f ||
        !pm_finite(highlight)||highlight<0.0f||highlight>100.0f ||
        !pm_finite(hr)||hr<0.0f||hr>100.0f ||
        !pm_finite(sat_skin)||sat_skin<0.0f||sat_skin>100.0f ||
        !pm_finite(density_skin)||density_skin<0.0f||density_skin>100.0f) return result;
    float peak=pmv_peak(pmvp_high(input));
    if (peak==0.0f) return result;
    pmvq_input_result prepared=pmvq_input_stages(input,peak,pre,sat_skin,density_skin);
    pmvp3 presat=prepared.presat;
    pmvp3 comp=threshold==100.0f?presat:pmcc_process_masked(presat,pmc_threshold_raw(threshold,softness),compression,softness,prepared.keep_sat,1);
    pmvp3 final=comp;
    if (!density_bypass) final=pmvq_density(comp,density,chroma,response,shadow,sr,highlight,hr,prepared.keep_density,2,2,0.001f);
    result.r=final.x;result.g=final.y;result.b=final.z;
    result.pre_r=presat.x;result.pre_g=presat.y;result.pre_b=presat.z;
    result.comp_r=comp.x;result.comp_g=comp.y;result.comp_b=comp.z;
    result.changed=!pmvp_same(final,input);
    result.pre_changed=!pmvp_same(presat,input);result.comp_changed=!pmvp_same(comp,input);
    return result;
}

__DEVICE__ int pmc_controls_valid(float pre,float threshold,float compression,float softness,
    float density,float chroma,float response,float shadow,float sr,float highlight,float hr,float sat_skin,float density_skin) {
    return !(!pm_finite(pre)||pre<0.0f||pre>200.0f ||
        !pm_finite(compression)||compression<0.0f||compression>100.0f ||
        !pm_finite(threshold)||threshold<0.0f||threshold>100.0f ||
        !pm_finite(softness)||softness<0.0f||softness>100.0f ||
        !pm_finite(density)||_fabs(density)>300.0f ||
        !pm_finite(chroma)||_fabs(chroma)>100.0f ||
        !pm_finite(response)||response<1.0f||response>4.0f ||
        !pm_finite(shadow)||shadow<0.0f||shadow>100.0f ||
        !pm_finite(sr)||sr<0.0f||sr>100.0f ||
        !pm_finite(highlight)||highlight<0.0f||highlight>100.0f ||
        !pm_finite(hr)||hr<0.0f||hr>100.0f ||
        !pm_finite(sat_skin)||sat_skin<0.0f||sat_skin>100.0f ||
        !pm_finite(density_skin)||density_skin<0.0f||density_skin>100.0f);
}

// Public stage seams for an independent Hue module. Original skin is analyzed
// once from the unmodified common input, before PreSat/Hue/Comp/Density.
__DEVICE__ pmvq_input_result pmc_prepare_stages(float2 r,float2 g,float2 b,float pre,float sat_skin,float density_skin) {
    pmvp3 input=pmvp_make(r,g,b);pmvq_input_result out;
    out.presat=input;out.keep_sat=pm_pair(1.0f);out.keep_density=pm_pair(1.0f);
    if (!pmvp_finite(input)||!pm_finite(pre)||pre<0.0f||pre>200.0f||
        !pm_finite(sat_skin)||sat_skin<0.0f||sat_skin>100.0f||
        !pm_finite(density_skin)||density_skin<0.0f||density_skin>100.0f) return out;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return out;
    return pmvq_input_stages(input,peak,pre,sat_skin,density_skin);
}
__DEVICE__ pmvp3 pmc_comp_stage(pmvp3 input,float threshold,float compression,float softness,float2 keep_sat) {
    if (!pm_finite(threshold)||threshold<0.0f||threshold>100.0f||
        !pm_finite(compression)||compression<0.0f||compression>100.0f||
        !pm_finite(softness)||softness<0.0f||softness>100.0f||threshold==100.0f) return input;
    return pmcc_process_masked(input,pmc_threshold_raw(threshold,softness),compression,softness,keep_sat,1);
}
__DEVICE__ pmvp3 pmc_density_stage(pmvp3 input,float density,float chroma,float response,float shadow,float sr,float highlight,float hr,float2 keep_density,int density_bypass) {
    if (density_bypass||!pmvp_finite(input)||
        !pm_finite(density)||_fabs(density)>300.0f||!pm_finite(chroma)||_fabs(chroma)>100.0f||
        !pm_finite(response)||response<1.0f||response>4.0f||
        !pm_finite(shadow)||shadow<0.0f||shadow>100.0f||!pm_finite(sr)||sr<0.0f||sr>100.0f||
        !pm_finite(highlight)||highlight<0.0f||highlight>100.0f||!pm_finite(hr)||hr<0.0f||hr>100.0f) return input;
    return pmvq_density(input,density,chroma,response,shadow,sr,highlight,hr,keep_density,2,2,0.001f);
}
// Final tonal desaturation: common linear DWG, after all creative operations.
// Threshold coordinates are DI(Y), not display IRE. No skin/tone protection.
__DEVICE__ int pmfd_control(float x) {return pm_finite(x)&&x>=0.0f&&x<=1.0f;}
__DEVICE__ float2 pmfd_level(float2 y) {
    if (pmvp_ge(make_float2(0.0026240900624543428f,-6.2454342912576788e-11f),y))
        return pm_pair_mul(y,make_float2(10.444268226623535f,3.2337646516111818e-07f));
    return pm_pair_mul(pm_pair_add(pmvp_log2(pm_pair_add(y,make_float2(0.0074999998323619366f,1.6763806315323038e-10f))),pm_pair(7.0f)),make_float2(0.073292478919029236f,1.0809707573500305e-09f));
}
__DEVICE__ float2 pmfd_shadow_keep(float2 level,float threshold,float knee) {
    if (threshold==0.0f||pmvp_ge(level,pm_pair(threshold))) return pm_pair(1.0f);
    float2 lower=pmcc_max(pm_pair(0.0f),pmvp_sub(pm_pair(threshold),pm_pair(knee)));
    if (knee==0.0f||pmvp_ge(lower,level)) return pm_pair(0.0f);
    return pmvp_smooth(lower,pm_pair(threshold),level);
}
__DEVICE__ float2 pmfd_highlight_keep(float2 level,float threshold,float knee) {
    if (threshold==1.0f||pmvp_ge(pm_pair(threshold),level)) return pm_pair(1.0f);
    float2 upper=pmcc_min(pm_pair(1.0f),pm_pair_add(pm_pair(threshold),pm_pair(knee)));
    if (knee==0.0f||pmvp_ge(level,upper)) return pm_pair(0.0f);
    return pmvp_sub(pm_pair(1.0f),pmvp_smooth(pm_pair(threshold),upper,level));
}
__DEVICE__ pmvp3 pmc_final_desat(float2 r,float2 g,float2 b,float shadow_t,float shadow_k,float highlight_t,float highlight_k) {
    pmvp3 input=pmvp_make(r,g,b);
    if (shadow_t==0.0f&&highlight_t==1.0f) return input;
    if (!pmvp_finite(input)||pmvp_same(input,pmvp_make(r,r,r))) return input;
    if (!pmfd_control(shadow_t)||!pmfd_control(shadow_k)||!pmfd_control(highlight_t)||!pmfd_control(highlight_k)) return input;
    float peak=pmv_peak(pmvp_high(input));if (peak==0.0f) return input;
    pmvp3 n=pmvp_div(input,peak);
    float2 yn=pmvpy_Y(n),y=pm_pair_mul(yn,pm_pair(peak));
    if (!pm_finite(y.x)||!pm_finite(y.y)) return input;
    // A finite non-positive Y is below every active shadow threshold. Avoid
    // overflowing the DI linear toe for huge negative values.
    if (pmvp_ge(pm_pair(0.0f),y)) return shadow_t>0.0f?pmvp_make(y,y,y):input;
    float2 level=pmfd_level(y);
    if (!pm_finite(level.x)||!pm_finite(level.y)) return input;
    float2 keep=pm_pair_mul(pmfd_shadow_keep(level,shadow_t,shadow_k),pmfd_highlight_keep(level,highlight_t,highlight_k));
    if (keep.x==1.0f&&keep.y==0.0f) return input;
    if (keep.x==0.0f&&keep.y==0.0f) return pmvp_make(y,y,y);
    float2 neutral=pm_pair_mul(pmvp_sub(pm_pair(1.0f),keep),yn);
    pmvp3 out=pmvp_scale(pmvp_add(pmvp_make(neutral,neutral,neutral),pmvp_scale(n,keep)),pm_pair(peak));
    return pmvp_finite(out)?out:input;
}

// PRESSMACHINE COLOR ADAPTER MODULE. ISOLATED RESEARCH; HOST/GPU UNQUALIFIED.
// Pure source primaries/transfer <-> scene-linear DWG float-pair conversion.
// Same data conversion library for full-feature and standalone creative cores.
// Helpers are namespaced pma_; UI and no-change/Bypass policy belong to caller.
#ifndef PRESSMACHINE_COLOR_ADAPTER_DCTLH
#define PRESSMACHINE_COLOR_ADAPTER_DCTLH
#define PMA_GAMUT_COUNT 4
#define PMA_TRANSFER_COUNT 5
#define PMA_LOGC4_A 2231.8263090676883f
#define PMA_LOGC4_B 0.90713587487781033f
#define PMA_LOGC4_C 0.092864125122189639f
#define PMA_LOGC4_S 0.1135972086105891f
#define PMA_LOGC4_T -0.018056996119911309f
#define PMA_ACESCCT_MAX_LINEAR 65504.0f
#define PMA_ACESCCT_MAX_ENCODED 1.4679963120447153f
__DEVICE__ int pma_finite(float x) {
    return x == x && _fabs(x) <= 3.402823466e38f;
}

__DEVICE__ int pma_finite3(float3 v) {
    return pma_finite(v.x) && pma_finite(v.y) && pma_finite(v.z);
}
// Pair arithmetic depends on each binary32 rounding boundary. CUDA may
// contract ordinary expressions (and fast math may approximate division).
// Explicit round-to-nearest intrinsics preserve the error-free compensation steps.

__DEVICE__ float pma_rn_add(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fadd_rn(a,b);
#else
    volatile float result=a+b; return result;
#endif
}

__DEVICE__ float pma_rn_sub(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fsub_rn(a,b);
#else
    volatile float result=a-b; return result;
#endif
}

__DEVICE__ float pma_rn_mul(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fmul_rn(a,b);
#else
    volatile float result=a*b; return result;
#endif
}

__DEVICE__ float pma_rn_div(float a,float b) {
#ifdef DEVICE_IS_CUDA
    return __fdiv_rn(a,b);
#else
    volatile float result=a/b; return result;
#endif
}

__DEVICE__ float pma_rn_fma(float a,float b,float c) {
#ifdef DEVICE_IS_CUDA
    return __fmaf_rn(a,b,c);
#else
    return _fmaf(a,b,c);
#endif
}

__DEVICE__ float2 pma_pair(float x) { return make_float2(x, 0.0f); }

__DEVICE__ float2 pma_pair_add(float2 a, float2 b) {
    float s = pma_rn_add(a.x,b.x);
    float v = pma_rn_sub(s,a.x);
    float e = pma_rn_add(pma_rn_add(pma_rn_add(pma_rn_sub(a.x,pma_rn_sub(s,v)),pma_rn_sub(b.x,v)),a.y),b.y);
    float h = pma_rn_add(s,e);
    return make_float2(h,pma_rn_sub(e,pma_rn_sub(h,s)));
}

__DEVICE__ float2 pma_pair_neg(float2 a) { return make_float2(-a.x,-a.y); }

__DEVICE__ float2 pma_pair_mul(float2 a, float2 b) {
    float p = pma_rn_mul(a.x,b.x);
    float e = pma_rn_add(pma_rn_add(pma_rn_add(pma_rn_fma(a.x,b.x,-p),pma_rn_mul(a.x,b.y)),pma_rn_mul(a.y,b.x)),pma_rn_mul(a.y,b.y));
    float h = pma_rn_add(p,e);
    return make_float2(h,pma_rn_sub(e,pma_rn_sub(h,p)));
}

__DEVICE__ float2 pma_pair_div(float2 a, float2 b) {
    float q = pma_rn_div(a.x,b.x);
    float2 r = pma_pair_add(a,pma_pair_neg(pma_pair_mul(b,pma_pair(q))));
    return pma_pair_add(pma_pair(q),pma_pair(pma_rn_div(pma_rn_add(r.x,r.y),b.x)));
}

__DEVICE__ float pma_decode(float v) {
    return v <= 0.02740668f ? v / 10.44426855f :
        _powf(2.0f, v / 0.07329248f - 7.0f) - 0.0075f;
}

__DEVICE__ float pma_encode(float v) {
    return v <= 0.00262409f ? v * 10.44426855f :
        (_log2f(v + 0.0075f) + 7.0f) * 0.07329248f;
}

__DEVICE__ float2 pma_precise_dot3(float2 x,float2 y,float2 z,
                                  float2 a,float2 b,float2 c) {
    return pma_pair_add(pma_pair_add(pma_pair_mul(a,x),pma_pair_mul(b,y)),pma_pair_mul(c,z));
}

__DEVICE__ float2 pma_precise_decode(float v) {
    if (v <= 0.02740668f) return pma_pair_div(pma_pair(v),make_float2(10.444268226623535f, 3.2337646871383185e-07f));
    float2 exponent = pma_pair_add(pma_pair_div(pma_pair(v),make_float2(0.07329247891902924f, 1.0809707573500305e-09f)),pma_pair(-7.0f));
    // Finite decoded values in the log branch have integer exponent >= -7.
    // Existing fast-path range handling owns unrepresentable large values.
    if (exponent.x > 127.0f) return pma_pair(pma_decode(v));
    float n = _floorf(exponent.x);
    if (exponent.x == n && exponent.y < 0.0f) n -= 1.0f;
    float2 r = pma_pair_add(exponent,pma_pair(-n));
    // Degree-16 Taylor polynomial for 2^r, 0 <= r <= 1. Its analytic
    // truncation bound is 2*ln(2)^17/17! < 1.4e-17 before pair rounding.
    float2 y = make_float2(1.3570247350023161e-16f, 5.9873197698431394e-24f);
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(3.132436682680125e-15f, 2.440830304062437e-23f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(6.77872607221866e-14f, 2.826038934825586e-21f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.3691489348516273e-12f, -4.9461213028820005e-20f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(2.567843680745252e-11f, -8.139643343159617e-19f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(4.4455383818586824e-10f, -1.0998787340184869e-17f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(7.054911765891347e-09f, -1.4509021906398983e-16f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.0178086284895471e-07f, -2.75655776552303e-15f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.3215486660556053e-06f, 1.2958825669712268e-14f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.5252733646775596e-05f, 1.5728424693304405e-13f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.0001540352968731895f, 7.060626389110425e-12f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.0013333557872101665f, 2.7432677657257543e-11f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.009618128649890423f, 4.5773804191462375e-10f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.05550410971045494f, -1.0456333576769339e-09f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.24022650718688965f, -2.277889404878053e-10f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.6931471824645996f, -1.9046542121259336e-09f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.0f, 0.0f));
    return pma_pair_add(pma_pair_mul(y,pma_pair(_powf(2.0f,n))),pma_pair_neg(make_float2(0.007499999832361937f, 1.6763807009212428e-10f)));
}

__DEVICE__ float2 pma_pair_exp2(float2 exponent) {
    float n = _floorf(exponent.x);
    if (exponent.x == n && exponent.y < 0.0f) n -= 1.0f;
    float2 r = pma_pair_add(exponent,pma_pair(-n));
    // Degree-16 Taylor polynomial for 2^r, 0 <= r <= 1. Its analytic
    // truncation bound is 2*ln(2)^17/17! < 1.4e-17 before pair rounding.
    float2 y = make_float2(1.3570247350023161e-16f, 5.9873197698431394e-24f);
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(3.132436682680125e-15f, 2.440830304062437e-23f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(6.77872607221866e-14f, 2.826038934825586e-21f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.3691489348516273e-12f, -4.9461213028820005e-20f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(2.567843680745252e-11f, -8.139643343159617e-19f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(4.4455383818586824e-10f, -1.0998787340184869e-17f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(7.054911765891347e-09f, -1.4509021906398983e-16f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.0178086284895471e-07f, -2.75655776552303e-15f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.3215486660556053e-06f, 1.2958825669712268e-14f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.5252733646775596e-05f, 1.5728424693304405e-13f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.0001540352968731895f, 7.060626389110425e-12f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.0013333557872101665f, 2.7432677657257543e-11f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.009618128649890423f, 4.5773804191462375e-10f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.05550410971045494f, -1.0456333576769339e-09f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.24022650718688965f, -2.277889404878053e-10f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(0.6931471824645996f, -1.9046542121259336e-09f));
    y = pma_pair_add(pma_pair_mul(y,r),make_float2(1.0f, 0.0f));
    return pma_pair_mul(y,pma_pair(_powf(2.0f,n)));
}

__DEVICE__ float2 pma_decode_channel(float v,int curve) {
    if (curve==0) return pma_precise_decode(v);
    if (curve==1) {
        if (v<=5.367655f*.010591f+.092809f) return pma_pair_div(pma_pair_add(pma_pair(v),pma_pair_neg(make_float2(0.092808999121189117f, 8.7881091292985047e-10f))),make_float2(5.3676548004150391f, 1.9958496011440729e-07f));
        float2 argument=pma_pair_mul(pma_pair_div(pma_pair_add(pma_pair(v),pma_pair_neg(make_float2(0.38553699851036072f, 1.4896393008001496e-09f))),make_float2(0.24718999862670898f, 1.3732910364439022e-09f)),make_float2(3.3219280242919922f, 7.0595369550119358e-08f));
        return pma_pair_div(pma_pair_add(pma_pair_exp2(argument),pma_pair_neg(make_float2(0.052271999418735504f, 5.8126448099216077e-10f))),make_float2(5.5555558204650879f, 1.7953490782929293e-07f));
    }
    if (curve==2) {
        if(v<0) return pma_pair_add(pma_pair_mul(pma_pair(v),make_float2(0.11359720677137375f, 1.8392153355861751e-09f)),make_float2(-0.018056996166706085f, 4.6794776387137915e-11f));
        float2 argument=pma_pair_add(pma_pair_mul(pma_pair_div(pma_pair_add(pma_pair(v),pma_pair_neg(make_float2(0.092864125967025757f, -8.4483608997487636e-10f))),make_float2(0.90713590383529663f, -2.8957487074876553e-08f)),pma_pair(14.0f)),pma_pair(6.0f));
        return pma_pair_div(pma_pair_add(pma_pair_exp2(argument),pma_pair(-64.0f)),make_float2(2231.826416015625f, -0.00010694793309085071f));
    }
    if(curve==3) {
        if(v<=.155251141552511f) return pma_pair_div(pma_pair_add(pma_pair(v),pma_pair_neg(make_float2(0.072905533015727997f, 1.180107456200119e-09f))),make_float2(10.540237426757812f, 3.1489668117501424e-07f));
        return pma_pair_exp2(pma_pair_add(pma_pair_mul(pma_pair(v),make_float2(17.520000457763672f, -4.5776366164318461e-07f)),pma_pair_neg(make_float2(9.7200002670288086f, -2.6702880973061838e-07f))));
    }
    return pma_pair(v);
}

__DEVICE__ float pma_encode_raw(float x, int curve) {
    if (curve == 0) return pma_encode(x);
    if (curve == 1) {
        return x <= 0.010591f ? 5.367655f*x+0.092809f :
            0.247190f*(_log2f(5.555556f*x+0.052272f)*0.301029995663981195f)+0.385537f;
    }
    if (curve == 2) {
        return x < PMA_LOGC4_T ? (x-PMA_LOGC4_T)/PMA_LOGC4_S :
            (_log2f(PMA_LOGC4_A*x+64.0f)-6.0f)/14.0f*PMA_LOGC4_B+PMA_LOGC4_C;
    }
    if (curve == 3) {
        return x <= 0.0078125f ? 10.5402377416545f*x+0.0729055341958355f :
            (_log2f(x)+9.72f)/17.52f;
    }
    return x;
}

__DEVICE__ float2 pma_to_dwg_channel(float2 r,float2 g,float2 b,int gamut,int axis) {
    if(gamut==0)return axis==0?r:(axis==1?g:b);
    if(gamut==1){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(0.88505852222442627f, -2.6090580362847504e-08f),make_float2(0.10359375923871994f, -2.4355044647705881e-09f),make_float2(0.01134774275124073f, -2.7162425086935116e-10f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(0.069226622581481934f, 7.1832900738755256e-10f),make_float2(0.91943150758743286f, 6.9110814848727387e-09f),make_float2(0.011341863311827183f, 3.9346656488525866e-10f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(0.075368478894233704f, 6.5197500176417122e-11f),make_float2(0.052795965224504471f, 1.1672210975532948e-09f),make_float2(0.87183552980422974f, 2.5231999600805466e-08f));
    }
    if(gamut==2){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(0.99739593267440796f, 1.0492574809006783e-08f),make_float2(-0.0231650210916996f, -2.9240670995633877e-10f),make_float2(0.025769073516130447f, 1.1767115060123956e-10f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(-0.009183080866932869f, -4.4421283318385463e-10f),make_float2(0.91763204336166382f, -1.0192937160979909e-08f),make_float2(0.091551050543785095f, -8.9774643274864729e-10f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(0.073487989604473114f, 3.3234182073016427e-10f),make_float2(0.09370480477809906f, -3.6873533115766577e-09f),make_float2(0.83280718326568604f, 2.6094140181953662e-08f));
    }
    if(gamut==3){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(0.91485494375228882f, 2.0290430668978843e-08f),make_float2(0.0028445599600672722f, -5.7727718438815856e-11f),make_float2(0.082300469279289246f, 2.192329651151681e-09f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(0.031184511259198189f, 3.8516545508571198e-10f),make_float2(0.78331631422042847f, -8.4815265921633909e-09f),make_float2(0.18549919128417969f, -7.1638255327854949e-09f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(0.067400179803371429f, 2.528846909655158e-09f),make_float2(0.085586093366146088f, -2.5182433915915681e-09f),make_float2(0.84701371192932129f, 1.5277944243052843e-08f));
    }
    return pma_pair(0.0f);
}
__DEVICE__ float2 pma_from_dwg_channel(float2 r,float2 g,float2 b,int gamut,int axis) {
    if(gamut==0)return axis==0?r:(axis==1?g:b);
    if(gamut==1){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(1.1409879922866821f, 8.8314298096747734e-09f),make_float2(-0.12779955565929413f, 2.2449295755677667e-09f),make_float2(-0.013188442215323448f, -6.1637542292380942e-11f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(-0.084754809737205505f, 2.5450033191987131e-09f),make_float2(1.0979348421096802f, 3.1120954702146264e-08f),make_float2(-0.013180067762732506f, -3.0992905464266585e-10f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(-0.093503661453723907f, -1.860155918187445e-09f),make_float2(-0.055439896881580353f, -1.6585109952060861e-09f),make_float2(1.1489435434341431f, 1.7629545823183435e-08f));
    }
    if(gamut==2){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(1.0054028034210205f, 5.1725336902563868e-08f),make_float2(0.0288817398250103f, -3.3337085869611371e-10f),make_float2(-0.034284591674804688f, 1.6147450043746403e-09f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(0.01912744902074337f, -3.9758540903989115e-10f),make_float2(1.1026830673217773f, 1.5850037726750088e-08f),make_float2(-0.12181053310632706f, -2.1180622533645277e-10f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(-0.090870216488838196f, 3.2876101840884076e-09f),make_float2(-0.12661893665790558f, 4.0037053672392631e-09f),make_float2(1.2174891233444214f, 2.1813267636616729e-08f));
    }
    if(gamut==3){
        if(axis==0)return pma_precise_dot3(r,g,b,make_float2(1.1008081436157227f, -1.6732849772438385e-08f),make_float2(0.0078776273876428604f, -3.392565672832859e-10f),make_float2(-0.10868574678897858f, -2.0666635069943595e-09f));
        if(axis==1)return pma_precise_dot3(r,g,b,make_float2(-0.023646220564842224f, -3.4342955562705058e-11f),make_float2(1.307750940322876f, 5.7631741157138094e-08f),make_float2(-0.28410476446151733f, -1.4858594354905108e-08f));
        if(axis==2)return pma_precise_dot3(r,g,b,make_float2(-0.085206270217895508f, -4.2690301294001642e-10f),make_float2(-0.13276791572570801f, -2.4372845963682721e-09f),make_float2(1.2179741859436035f, 2.2014654543767165e-09f));
    }
    return pma_pair(0.0f);
}

// No UI, transform, creative stages, or Bypass semantics live in this library.
__DEVICE__ int pma_profile_valid(int gamut,int transfer){
    return gamut>=0&&gamut<PMA_GAMUT_COUNT&&transfer>=0&&transfer<PMA_TRANSFER_COUNT;
}
__DEVICE__ int pma_profiles_same(int ig,int it,int og,int ot){return ig==og&&it==ot;}
__DEVICE__ int pma_encoded_domain_valid(float3 v,int transfer){
    return pma_finite3(v)&&(transfer!=3||(v.x<=PMA_ACESCCT_MAX_ENCODED&&v.y<=PMA_ACESCCT_MAX_ENCODED&&v.z<=PMA_ACESCCT_MAX_ENCODED));
}
__DEVICE__ int pma_linear_domain_valid(float2 v,int transfer){
    if(!pma_finite(v.x)||!pma_finite(v.y)||!pma_finite(pma_rn_add(v.x,v.y)))return 0;
    return transfer!=3||v.x<PMA_ACESCCT_MAX_LINEAR||(v.x==PMA_ACESCCT_MAX_LINEAR&&v.y<=0.0f);
}
__DEVICE__ float pma_encode_channel(float2 linear,int transfer){
    return pma_encode_raw(pma_rn_add(linear.x,linear.y),transfer);
}

#endif

// PressMachine Hue v0.3: luma-preserving shared linear-opponent redesign.
// Integral sector warp retained from standalone v0.2 SHA9d591f7; angle space changed.
// No UI, transform, transfer or primaries conversion. Scene-linear DWG pair.
// Original Oklab low-chroma eligibility is held; keep_sat attenuates angular delta once.
// Hue uses the existing shared Comp linear-opponent a/b coordinates. Linear DWG Y is preserved; Oklab L/C is not a promised invariant.
// Integral warp parameters, half-width .18, minimum slope .02 are retained.
#ifndef PRESSMACHINE_HUE_LINEAR_PAIR_DCTLH
#define PRESSMACHINE_HUE_LINEAR_PAIR_DCTLH
__DEVICE__ float2 pmah_pi(){return make_float2(3.14159274101257324e+00f,-8.74227765734758577e-08f);}
__DEVICE__ float2 pmah_tau(){return make_float2(6.28318548202514648e+00f,-1.74845553146951715e-07f);}
__DEVICE__ float2 pmah_clamp01(float2 x){return !pmvp_positive(x)?pm_pair(0.0f):(pmvp_ge(x,pm_pair(1.0f))?pm_pair(1.0f):x);}
__DEVICE__ float2 pmah_wrap(float2 x){
 float k=_floorf(pmvp_round(pm_pair_div(pm_pair_add(x,pmah_pi()),pmah_tau())));
 float2 z=pmvp_sub(x,pm_pair_mul(pm_pair(k),pmah_tau()));
 if(pmvp_ge(z,pmah_pi()))z=pmvp_sub(z,pmah_tau());
 if(!pmvp_ge(z,pm_pair_neg(pmah_pi())))z=pm_pair_add(z,pmah_tau());return z;
}
// atan2 range-reduced to |t|<=tan(pi/8). Pair polynomial avoids float-angle
// errors becoming large encoded residuals when HDR RGB channels cancel.
__DEVICE__ float2 pmah_atan2(float2 y,float2 x){
 float2 ax=pmvp_abs(x),ay=pmvp_abs(y);int swap=pmvp_ge(ay,ax);
 float2 hi=swap?ay:ax,lo=swap?ax:ay;if(!pmvp_positive(hi))return pm_pair(0.0f);
 float2 q=pm_pair_div(lo,hi);int reduce=pmvp_ge(q,make_float2(4.14213567972183228e-01f,-5.59908830410904557e-09f));
 float2 t=reduce?pm_pair_div(pmvp_sub(q,pm_pair(1.0f)),pm_pair_add(q,pm_pair(1.0f))):q;
 float2 t2=pm_pair_mul(t,t),v=make_float2(3.99999991059303284e-02f,8.94069651646844932e-10f);
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-4.34782616794109344e-02f,8.09845746019277613e-10f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(4.76190485060214996e-02f,-8.86973883229558169e-10f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-5.26315793395042419e-02f,3.92135823812367335e-10f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(5.88235296308994293e-02f,-2.19134724255276581e-10f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-6.66666701436042786e-02f,3.47693762670076012e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(7.69230797886848450e-02f,-2.86560797313484272e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-9.09090936183929443e-02f,2.70930211598852111e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(1.11111111938953400e-01f,-8.27842294714997706e-10f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-1.42857149243354797e-01f,6.38621200366173980e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(2.00000002980232239e-01f,-2.98023228317845224e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(-3.33333343267440796e-01f,9.93410775862457740e-09f));
 v=pm_pair_add(pm_pair_mul(v,t2),make_float2(1.00000000000000000e+00f,0.00000000000000000e+00f));
 float2 a=pm_pair_mul(t,v);if(reduce)a=pm_pair_add(make_float2(7.85398185253143311e-01f,-2.18556941433689644e-08f),a);
 if(swap)a=pmvp_sub(make_float2(1.57079637050628662e+00f,-4.37113882867379289e-08f),a);if(!pmvp_ge(x,pm_pair(0.0f)))a=pmvp_sub(pmah_pi(),a);
 return !pmvp_ge(y,pm_pair(0.0f))?pm_pair_neg(a):a;
}
__DEVICE__ float2 pmah_integral(float2 u,float2 a,float2 b){
 if(pmvp_ge(a,u))return pm_pair(0.0f);
 float2 d=pmvp_sub(b,a);if(!pmvp_positive(d))return pmvp_sub(u,a);
 if(pmvp_ge(u,b))return pm_pair_add(pm_pair_mul(pm_pair(.5f),d),pmvp_sub(u,b));
 float2 t=pm_pair_div(pmvp_sub(u,a),d),t2=pm_pair_mul(t,t),t3=pm_pair_mul(t2,t);
 return pm_pair_mul(d,pmvp_sub(t3,pm_pair_mul(pm_pair(.5f),pm_pair_mul(t3,t))));
}
__DEVICE__ float2 pmah_warp_u(float2 u,float2 c,float2 pivot){
 if(!pmvp_positive(c)||!pmvp_positive(u)||pmvp_ge(u,pm_pair(1.0f)))return u;
 float2 a=pmah_clamp01(pmvp_sub(pivot,make_float2(1.80000007152557373e-01f,-7.15255721317475945e-09f))),b=pmah_clamp01(pm_pair_add(pivot,make_float2(1.80000007152557373e-01f,-7.15255721317475945e-09f)));
 float2 m=make_float2(1.99999995529651642e-02f,4.47034825823422466e-10f),w=pmvp_sub(pm_pair(1.0f),m);
 float2 full=pmah_clamp01(pm_pair_div(pm_pair_add(pm_pair_mul(m,u),pm_pair_mul(w,pmah_integral(u,a,b))),pm_pair_add(m,pm_pair_mul(w,pmah_integral(pm_pair(1.0f),a,b)))));
 // Compression is the fraction of the full angular move, so 25/50/75 percent
 // gives 25/50/75 percent of the same pixel's full move at fixed Pivot.
 return pmah_clamp01(pm_pair_add(u,pm_pair_mul(c,pmvp_sub(full,u))));
}
__DEVICE__ float2 pmah_hue_delta(float2 h,float angle,int points,float c,float pivot){
 float2 spacing=pm_pair_div(pmah_tau(),pm_pair((float)points)),half=pm_pair_mul(pm_pair(.5f),spacing);
 float2 base=angle==360.0f?pm_pair(0.0f):pm_pair_mul(pm_pair(angle),make_float2(1.74532923847436905e-02f,1.35199601514202072e-10f));
 float2 rel=pmah_wrap(pmvp_sub(h,base)),q=pm_pair_div(rel,spacing);
 float nearest=pmvp_positive(q)?_floorf(pmvp_round(pm_pair_add(q,pm_pair(.5f)))):-_floorf(pmvp_round(pm_pair_add(pm_pair_neg(q),pm_pair(.5f))));
 float2 anchor=pm_pair_add(base,pm_pair_mul(pm_pair(nearest),spacing));
 float2 d=pmah_wrap(pmvp_sub(h,anchor));if(pmvp_positive(pmvp_sub(d,half)))d=pmvp_sub(d,spacing);
 if(pmvp_positive(pmvp_sub(pm_pair_neg(half),d)))d=pm_pair_add(d,spacing);
 float2 u=pmah_clamp01(pm_pair_div(pmvp_abs(d),half));
 float2 warped=pmah_warp_u(u,pm_pair_div(pm_pair(c),pm_pair(100.0f)),pm_pair_div(pm_pair(pivot),pm_pair(100.0f)));
 float2 target=pm_pair_mul(half,warped);if(!pmvp_ge(d,pm_pair(0.0f)))target=pm_pair_neg(target);
 return pmvp_sub(target,d);
}
__DEVICE__ float2 pmah_prepare(pmvp3 original){
 if(!pmvp_finite(original))return pm_pair(0.0f);
 if(original.x.x==original.y.x&&original.x.y==original.y.y&&original.x.x==original.z.x&&original.x.y==original.z.y)return pm_pair(0.0f);
 float peak=pmv_peak(pmvp_high(original));if(peak==0.0f)return pm_pair(0.0f);
 pmvp3 lab=pmvp_lab(pmvp_div(original,peak));if(!pmvp_finite(lab))return pm_pair(0.0f);
 float2 scale=pm_pair_cbrt(pm_pair(peak)),c=pm_pair_mul(pmvp_chroma(lab),scale),l=pm_pair_mul(pmvp_abs(lab.x),scale);
 if(pmvp_ge(make_float2(1.00000001168609742e-07f,-1.16860974683322431e-15f),c))return pm_pair(0.0f);
 float2 denom=pmvp_ge(l,make_float2(9.99999997475242708e-07f,2.52475724686976061e-15f))?l:make_float2(9.99999997475242708e-07f,2.52475724686976061e-15f);
 return pmvp_smooth(make_float2(2.00000009499490261e-03f,-9.49949008344219692e-11f),make_float2(1.99999995529651642e-02f,4.47034825823422466e-10f),pm_pair_div(c,denom));
}
__DEVICE__ float2 pmah_sin(float2 angle){
 // Range reduction keeps |angle/4|<=pi/4. Degree17/16 truncation is below
 // pair rounding; double twice. This is not a lower-precision Hue option.
 float2 x=pm_pair_mul(angle,pm_pair(.25f)),z=pm_pair_mul(x,x),s=make_float2(2.81145735896637036e-15f,-1.04620847397636578e-22f),c=make_float2(4.77947725613294544e-14f,7.62544404448642983e-22f);
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(-7.64716360981271270e-13f,-1.22007104711782877e-20f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(1.60590443720742826e-10f,-5.35252651156272563e-18f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(-2.50521079436794025e-08f,-4.41762304464836646e-16f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(2.75573188446287531e-06f,3.79357122429722915e-14f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(-1.98412701138295233e-04f,2.72559687493345582e-12f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(8.33333376795053482e-03f,-4.34617203337595015e-10f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(-1.66666671633720398e-01f,4.96705387931228870e-09f));
 s=pm_pair_add(pm_pair_mul(s,z),make_float2(1.00000000000000000e+00f,0.00000000000000000e+00f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(-1.14707453605089604e-11f,-2.37220768923123805e-19f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(2.08767558795841524e-09f,1.10828398092043424e-16f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(-2.75573199814971304e-07f,7.57511220905119492e-15f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(2.48015876422869042e-05f,-3.40699609366681977e-13f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(-1.38888892251998186e-03f,3.36310944371032150e-11f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(4.16666679084300995e-02f,-1.24176346982807218e-09f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(-5.00000000000000000e-01f,0.00000000000000000e+00f));
 c=pm_pair_add(pm_pair_mul(c,z),make_float2(1.00000000000000000e+00f,0.00000000000000000e+00f));
 s=pm_pair_mul(x,s);
 for(int i=0;i<2;i++){float2 ns=pm_pair_mul(pm_pair(2.0f),pm_pair_mul(s,c));c=pmvp_sub(pm_pair_mul(c,c),pm_pair_mul(s,s));s=ns;}
 return s;
}
__DEVICE__ float2 pmah_cube_delta(float2 root,float2 d){
 return pm_pair_mul(d,pm_pair_add(pm_pair_mul(pm_pair(3.0f),pm_pair_mul(root,root)),pm_pair_add(pm_pair_mul(pm_pair(3.0f),pm_pair_mul(root,d)),pm_pair_mul(d,d))));
}
__DEVICE__ int pmah_controls_valid(float angle,int points,float c,float pivot){
 return pm_finite(angle)&&angle>=0.0f&&angle<=360.0f&&points>=1&&points<=6&&pm_finite(c)&&c>=0.0f&&c<=100.0f&&pm_finite(pivot)&&pivot>=0.0f&&pivot<=100.0f;
}
__DEVICE__ pmvp3 pmah_dwg_rec(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.13030219078063965e+00f,-1.34665718576343352e-08f),make_float2(-2.03928444534540176e-02f,3.22500359750677035e-10f),make_float2(-1.09909325838088989e-01f,-2.09124650929481959e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-2.55470573902130127e-02f,2.82847495425286866e-10f),make_float2(1.31084930896759033e+00f,1.18388170378125324e-08f),make_float2(-2.85302251577377319e-01f,-1.40992506558745845e-08f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-9.25986021757125854e-02f,-1.91725635367845371e-09f),make_float2(-1.64653033018112183e-01f,6.71298394649966212e-09f),make_float2(1.25725162029266357e+00f,9.44155775783883655e-09f)));}
__DEVICE__ pmvp3 pmah_rec_dwg_delta(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(8.92112135887145996e-01f,-1.22515713130155746e-08f),make_float2(2.43691708892583847e-02f,-5.21347964799190322e-10f),make_float2(8.35186988115310669e-02f,2.60166221899282846e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(3.26166003942489624e-02f,1.26596755301022768e-09f),make_float2(7.86137521266937256e-01f,-5.50762369044832667e-09f),make_float2(1.81245878338813782e-01f,5.74527581065353843e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(6.99770525097846985e-02f,-3.02064595558704241e-09f),make_float2(1.04749493300914764e-01f,8.38598801511380998e-10f),make_float2(8.25273454189300537e-01f,2.56943355481098479e-09f)));}
__DEVICE__ pmvp3 pmah_opponent(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(2.62700200080871582e-01f,1.19303953383109729e-08f),make_float2(6.77998065948486328e-01f,5.57038459803038677e-09f),make_float2(5.93017153441905975e-02f,1.12567133392360574e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(2.07049190998077393e-01f,-3.87849397043282806e-09f),make_float2(-2.46614560484886169e-01f,6.90421453342082714e-09f),make_float2(3.95653657615184784e-02f,6.99569457918158832e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(4.75215204060077667e-02f,-1.24775700882651108e-09f),make_float2(1.14051133394241333e-01f,2.50313636485088864e-09f),make_float2(-1.61572650074958801e-01f,-4.98066965448629162e-09f)));}
__DEVICE__ pmvp3 pmah_opponent_delta(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.00000000000000000e+00f,2.22044604925031308e-16f),make_float2(3.29174137115478516e+00f,-8.70019007948030776e-08f),make_float2(1.17309868335723877e+00f,-1.38626674583974818e-08f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.00000000000000000e+00f,2.22044604925031308e-16f),make_float2(-1.28102314472198486e+00f,1.12422311460136370e-08f),make_float2(5.33355511724948883e-02f,8.46733627657414445e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.00000000000000000e+00f,2.22044604925031308e-16f),make_float2(6.39118254184722900e-02f,-1.90392568377717453e-09f),make_float2(-5.80648756027221680e+00f,1.41416691690210428e-07f)));}
__DEVICE__ pmvp3 pmah_process(pmvp3 input,float2 validity,float2 keep_sat,float angle,int points,float c,float pivot){
 if(c==0.0f||!pmah_controls_valid(angle,points,c,pivot)||!pmvp_finite(input)||!pmvp_positive(validity)||!pmvp_positive(keep_sat))return input;
 float peak=pmv_peak(pmvp_high(input));if(peak==0.0f)return input;
 pmvp3 n=pmvp_div(input,peak),opp=pmah_opponent(pmah_dwg_rec(n));
 if(!pmvp_finite(opp)||!pmvp_positive(pmvp_chroma(opp)))return input;
 float2 delta=pm_pair_mul(pmah_hue_delta(pmah_atan2(opp.z,opp.y),angle,points,c,pivot),pm_pair_mul(pmah_clamp01(validity),pmah_clamp01(keep_sat)));
 if(!pmvp_positive(pmvp_abs(delta)))return input;
 float2 sn=pmah_sin(delta),sh=pmah_sin(pm_pair_mul(delta,pm_pair(.5f))),cm1=pm_pair_mul(pm_pair(-2.0f),pm_pair_mul(sh,sh));
 float2 da=pmvp_sub(pm_pair_mul(opp.y,cm1),pm_pair_mul(opp.z,sn)),db=pm_pair_add(pm_pair_mul(opp.y,sn),pm_pair_mul(opp.z,cm1));
 pmvp3 recdelta=pmah_opponent_delta(pmvp_make(pm_pair(0.0f),da,db));
 pmvp3 dwgdelta=pmah_rec_dwg_delta(recdelta);
 // Project the delta onto the actual published common-DWG zero-Y plane.
 // This removes inverse/white coefficient residuals rather than scaling RGB
 // by a potentially zero/negative output Y. No input/output RGB clipping.
 float2 dy=pmvpy_Y(dwgdelta);dwgdelta=pmvp_sub3(dwgdelta,pmvp_make(dy,dy,dy));
 pmvp3 out=pmvp_add(input,pmvp_scale(dwgdelta,pm_pair(peak)));
 return pmvp_finite(out)?out:input;
}
#endif

// HUE-RAY FORCE CANDIDATE. No fixed target saturation radius.
// Each ray supplies projected attraction plus a small directional bias.
// Bias is a normalized force scale, not a target point location.
// Amount scales the input-evaluated force once; Transition smooths the 90-degree crossing.
#ifndef PRESSMACHINE_HUE_RAY_FORCE_DCTLH
#define PRESSMACHINE_HUE_RAY_FORCE_DCTLH
__DEVICE__ float2 pmhr_step_c(int n){
 if(n==1)return make_float2(1.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==2)return make_float2(-1.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==3)return make_float2(-5.00000000000000000e-01f,2.22044604925031308e-16f);
 if(n==4)return make_float2(0.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==5)return make_float2(3.09017002582550049e-01f,-8.20760259756525556e-09f);
 if(n==6)return make_float2(5.00000000000000000e-01f,1.11022302462515654e-16f);
 return pm_pair(1);
}
__DEVICE__ float2 pmhr_step_s(int n){
 if(n==1)return make_float2(-0.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==2)return make_float2(0.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==3)return make_float2(8.66025388240814209e-01f,1.55436250537377418e-08f);
 if(n==4)return make_float2(1.00000000000000000e+00f,0.00000000000000000e+00f);
 if(n==5)return make_float2(9.51056540012359619e-01f,-2.37172059769363841e-08f);
 if(n==6)return make_float2(8.66025388240814209e-01f,1.55436250537377418e-08f);
 return pm_pair(0);
}


__DEVICE__ float2 pmhr_positive(float2 x,float2 width){
 if(!pmvp_positive(width))return pmvp_positive(x)?x:pm_pair(0);
 if(pmvp_ge(x,width))return x;if(pmvp_ge(pm_pair_neg(width),x))return pm_pair(0);
 float2 u=pm_pair_add(x,width);return pm_pair_div(pm_pair_mul(u,u),pm_pair_mul(pm_pair(4),width));
}
__DEVICE__ pmvp3 pmhr_force(float2 a,float2 b,float angle,int points,float transition){
 pmvp3 force=pmvp_make(pm_pair(0),pm_pair(0),pm_pair(0));
 if(!pmah_controls_valid(angle,points,100,transition)||!pm_finite(a.x)||!pm_finite(a.y)||!pm_finite(b.x)||!pm_finite(b.y))return force;
 if(points>1&&!pmvp_positive(pmvp_abs(a))&&!pmvp_positive(pmvp_abs(b)))return force;
 float2 bias=pm_pair_div(pm_pair(8),pm_pair(100)),width=pm_pair_mul(bias,pm_pair_div(pm_pair(transition),pm_pair(100)));
 float2 h=angle==360?pm_pair(0):pmah_wrap(pm_pair_mul(pm_pair(angle),make_float2(1.74532923847436905e-02f,1.35199601514202072e-10f)));
 float2 qs=pmah_sin(h),hs=pmah_sin(pm_pair_mul(h,pm_pair(.5f))),qc=pmvp_sub(pm_pair(1),pm_pair_mul(pm_pair(2),pm_pair_mul(hs,hs)));
 float2 total=pm_pair(0),fa=pm_pair(0),fb=pm_pair(0),sc=pmhr_step_c(points),ss=pmhr_step_s(points);
 for(int k=0;k<points;k++){
  float2 along=pm_pair_add(pm_pair_mul(a,qc),pm_pair_mul(b,qs)),radial=pm_pair_add(pmhr_positive(along,width),bias);
  float2 va=pmvp_sub(pm_pair_mul(radial,qc),a),vb=pmvp_sub(pm_pair_mul(radial,qs),b);
  if(points==1)return pmvp_make(pm_pair(0),va,vb);
  float2 d2=pm_pair_add(pm_pair_mul(va,va),pm_pair_mul(vb,vb));if(!pmvp_positive(d2))return force;
  float2 w=pm_pair_div(pm_pair(1),d2);total=pm_pair_add(total,w);fa=pm_pair_add(fa,pm_pair_mul(w,va));fb=pm_pair_add(fb,pm_pair_mul(w,vb));
  float2 nc=pmvp_sub(pm_pair_mul(qc,sc),pm_pair_mul(qs,ss));qs=pm_pair_add(pm_pair_mul(qs,sc),pm_pair_mul(qc,ss));qc=nc;
 }
 if(!pmvp_positive(total))return force;return pmvp_make(pm_pair(0),pm_pair_div(fa,total),pm_pair_div(fb,total));
}
__DEVICE__ pmvp3 pmhr_process(pmvp3 input,float2 validity,float2 keep,float angle,int points,float amount,float transition){
 if(amount==0||!pmah_controls_valid(angle,points,amount,transition)||!pmvp_finite(input)||!pmvp_positive(keep))return input;
 if(points>1&&!pmvp_positive(validity))return input;
 int neutral=input.x.x==input.y.x&&input.x.y==input.y.y&&input.x.x==input.z.x&&input.x.y==input.z.y;
 if(points>1&&neutral)return input;float peak=pmv_peak(pmvp_high(input));if(peak==0)return input;
 pmvp3 rec=pmah_dwg_rec(pmvp_div(input,peak));float2 energy=pm_pair_sqrt(pmcc_Y(pmvp_make(pm_pair_mul(rec.x,rec.x),pm_pair_mul(rec.y,rec.y),pm_pair_mul(rec.z,rec.z))));
 if(!pmvp_positive(energy)||!pm_finite(energy.x)||!pm_finite(energy.y))return input;
 pmvp3 opp=pmah_opponent(rec);if(!pmvp_finite(opp))return input;
 float2 a=neutral?pm_pair(0):pm_pair_div(opp.y,energy),b=neutral?pm_pair(0):pm_pair_div(opp.z,energy);
 pmvp3 f=pmhr_force(a,b,angle,points,transition);
 float2 t=pm_pair_mul(pm_pair_div(pm_pair(amount),pm_pair(100)),pmah_clamp01(keep));if(points>1)t=pm_pair_mul(t,pmah_clamp01(validity));
 float2 da=pm_pair_mul(pm_pair_mul(t,energy),f.y),db=pm_pair_mul(pm_pair_mul(t,energy),f.z);
 if(!pmvp_positive(pmvp_abs(da))&&!pmvp_positive(pmvp_abs(db)))return input;
 pmvp3 delta=pmah_rec_dwg_delta(pmah_opponent_delta(pmvp_make(pm_pair(0),da,db)));float2 dy=pmvpy_Y(delta);delta=pmvp_sub3(delta,pmvp_make(dy,dy,dy));
 pmvp3 output=pmvp_add(input,pmvp_scale(delta,pm_pair(peak)));return pmvp_finite(output)?output:input;
}
#endif

// CF-2 comparison candidate, exact equation provenance: upstream_cf2/reference.py SHA948a6164.
// UI-free. Common linear DWG pair bridge -> XYZ D65 -> linear BT.2020 chroma plane.
// No old low-chroma eligibility. Original SatSkin keep scales this stage delta once.
#ifndef PRESSMACHINE_CF2_PAIR_DCTLH
#define PRESSMACHINE_CF2_PAIR_DCTLH
__DEVICE__ pmvp3 pmcf_xyz_rec(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.71665120124816895e+00f,-1.32769013561073734e-08f),make_float2(-3.55670779943466187e-01f,-3.83292597661011314e-09f),make_float2(-2.53366291522979736e-01f,1.01493196069668556e-08f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-6.66684329509735107e-01f,-2.23227534235093117e-08f),make_float2(1.61648118495941162e+00f,5.16755278567870846e-08f),make_float2(1.57685466110706329e-02f,-7.97159505072642105e-10f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(1.76398567855358124e-02f,6.59775123423855803e-10f),make_float2(-4.27706129848957062e-02f,-2.72912942245184809e-10f),make_float2(9.42103147506713867e-01f,-2.62712394061281884e-08f)));}
__DEVICE__ pmvp3 pmcf_rec_xyz(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(6.36958062648773193e-01f,-1.43474814251476346e-08f),make_float2(1.44616901874542236e-01f,1.71166614215678692e-09f),make_float2(1.68880969285964966e-01f,5.87820725428400692e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(2.62700200080871582e-01f,1.19303953383109729e-08f),make_float2(6.77998065948486328e-01f,5.57038459803038677e-09f),make_float2(5.93017153441905975e-02f,1.12567133392360574e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(0.00000000000000000e+00f,0.00000000000000000e+00f),make_float2(2.80726924538612366e-02f,5.95226257171788120e-10f),make_float2(1.06098508834838867e+00f,-3.06375973480044195e-08f)));}
__DEVICE__ pmvp3 pmcf_xyz_dwg(pmvp3 v){return pmvp_make(pm_precise_dot3(v.x,v.y,v.z,make_float2(1.51667201519012451e+00f,3.50879751920274430e-08f),make_float2(-2.81478047370910645e-01f,-1.02848272121036644e-08f),make_float2(-1.46963641047477722e-01f,5.37586997140238054e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(-4.64917093515396118e-01f,-7.08441616481536585e-09f),make_float2(1.25142371654510498e+00f,5.72052876179895975e-08f),make_float2(1.74884617328643799e-01f,-5.86235016086789074e-09f)),pm_precise_dot3(v.x,v.y,v.z,make_float2(6.48490414023399353e-02f,1.25935450956404793e-09f),make_float2(1.09139345586299896e-01f,2.34810149102315791e-09f),make_float2(7.61414647102355957e-01f,-2.52304044323636845e-08f)));}
__DEVICE__ float2 pmcf_kr(){return make_float2(2.62700200080871582e-01f,1.19303953383109729e-08f);}
__DEVICE__ float2 pmcf_kg(){return make_float2(6.77998065948486328e-01f,5.57038459803038677e-09f);}
__DEVICE__ float2 pmcf_kb(){return make_float2(5.93017153441905975e-02f,1.12567133392360574e-09f);}
__DEVICE__ float2 pmcf_phase(){return make_float2(2.72323161363601685e-01f,6.31167917930497424e-09f);}

__DEVICE__ pmvp3 pmcf_unit(float2 h){
 h=pmah_wrap(h);float2 si=pmah_sin(h),hs=pmah_sin(pm_pair_mul(h,pm_pair(.5f)));
 return pmvp_make(pm_pair(0),pmvp_sub(pm_pair(1),pm_pair_mul(pm_pair(2),pm_pair_mul(hs,hs))),si);
}
__DEVICE__ float2 pmcf_dot(float2 a,float2 b,pmvp3 u){return pm_pair_add(pm_pair_mul(a,u.y),pm_pair_mul(b,u.z));}
__DEVICE__ pmvp3 pmcf_delta_rgb(float2 a,float2 b){
 float2 dr=pm_pair_mul(pm_pair_mul(pm_pair(2),pmvp_sub(pm_pair(1),pmcf_kr())),a);
 float2 db=pm_pair_neg(pm_pair_mul(pm_pair_mul(pm_pair(2),pmvp_sub(pm_pair(1),pmcf_kb())),b));
 float2 dg=pm_pair_neg(pm_pair_div(pm_pair_add(pm_pair_mul(pmcf_kr(),dr),pm_pair_mul(pmcf_kb(),db)),pmcf_kg()));
 return pmvp_make(dr,dg,db);
}
__DEVICE__ pmvp3 pmcf_xy(pmvp3 rgb){
 float2 rg=pmvp_sub(rgb.x,rgb.y),bg=pmvp_sub(rgb.z,rgb.y),rm=pmvp_sub(pm_pair(1),pmcf_kr()),bm=pmvp_sub(pm_pair(1),pmcf_kb());
 float2 a=pm_pair_div(pmvp_sub(pm_pair_mul(rm,rg),pm_pair_mul(pmcf_kb(),bg)),pm_pair_mul(pm_pair(2),rm));
 float2 b=pm_pair_neg(pm_pair_div(pmvp_sub(pm_pair_mul(bm,bg),pm_pair_mul(pmcf_kr(),rg)),pm_pair_mul(pm_pair(2),bm)));
 return pmvp_make(pm_pair(0),a,b);
}
__DEVICE__ pmvp3 pmcf_endpoint(float2 a,float2 b,float2 Y,float angle,int points){
 float2 phi=pmah_wrap(pm_pair_add(pmcf_phase(),pm_pair_mul(pm_pair(angle==360?0:angle),make_float2(1.74532923847436905e-02f,1.35199601514202072e-10f))));
 pmvp3 u=pmcf_unit(phi);float2 floor=pm_pair(0);
 if(points==1&&pmvp_positive(Y)){
  pmvp3 d=pmcf_delta_rgb(u.y,u.z);float2 low=pmvp_ge(d.x,d.y)?d.y:d.x;low=pmvp_ge(low,d.z)?d.z:low;
  float2 denom=pm_pair_neg(low);if(!pmvp_positive(denom))return pmvp_make(pm_pair(0),a,b);floor=pm_pair_div(Y,denom);
 }
 float scale=_fmaxf(_fmaxf(pmvp_round(pmvp_abs(a)),pmvp_round(pmvp_abs(b))),pmvp_round(floor));
 if(scale==0)return pmvp_make(pm_pair(0),pm_pair(0),pm_pair(0));
 if(!pm_finite(scale))return pmvp_make(pm_pair(0),a,b);
 float2 va=pm_pair_div(a,pm_pair(scale)),vb=pm_pair_div(b,pm_pair(scale));
 if(points<=2){
  float2 along=pmcf_dot(va,vb,u);if(points==1){float2 f=pm_pair_div(floor,pm_pair(scale));along=pmvp_ge(along,f)?along:f;}
  return pmvp_make(pm_pair(0),pm_pair_mul(pm_pair_mul(along,u.y),pm_pair(scale)),pm_pair_mul(pm_pair_mul(along,u.z),pm_pair(scale)));
 }
 float2 h=pmah_wrap(pmvp_sub(pmah_atan2(vb,va),phi));if(!pmvp_ge(h,pm_pair(0)))h=pm_pair_add(h,pmah_tau());
 float2 sector=pm_pair_div(pmah_tau(),pm_pair((float)points)),q=pm_pair_div(h,sector);
 int j=(int)_floorf(q.x);if(!pmvp_ge(q,pm_pair((float)j)))j--;if(pmvp_ge(q,pm_pair((float)(j+1))))j++;
 if(j<0)j=0;if(j>=points)j=points-1;
 float2 t=pmah_clamp01(pmvp_sub(q,pm_pair((float)j))),w=pm_pair_mul(pm_pair_mul(t,t),pmvp_sub(pm_pair(3),pm_pair_mul(pm_pair(2),t)));
 pmvp3 ul=pmcf_unit(pm_pair_add(phi,pm_pair_mul(pm_pair((float)j),sector))),ur=pmcf_unit(pm_pair_add(phi,pm_pair_mul(pm_pair((float)(j+1)),sector)));
 float2 dl=pmcf_dot(va,vb,ul),dr=pmcf_dot(va,vb,ur);if(!pmvp_positive(dl))dl=pm_pair(0);if(!pmvp_positive(dr))dr=pm_pair(0);
 float2 left=pmvp_sub(pm_pair(1),w);
 float2 ta=pm_pair_add(pm_pair_mul(left,pm_pair_mul(dl,ul.y)),pm_pair_mul(w,pm_pair_mul(dr,ur.y)));
 float2 tb=pm_pair_add(pm_pair_mul(left,pm_pair_mul(dl,ul.z)),pm_pair_mul(w,pm_pair_mul(dr,ur.z)));
 return pmvp_make(pm_pair(0),pm_pair_mul(ta,pm_pair(scale)),pm_pair_mul(tb,pm_pair(scale)));
}
__DEVICE__ pmvp3 pmcf_process(pmvp3 input,float2 keep,float angle,int points,float amount){
 if(amount==0||!pmah_controls_valid(angle,points,amount,50.0f)||!pmvp_finite(input)||!pmvp_positive(keep))return input;
 int neutral=input.x.x==input.y.x&&input.x.y==input.y.y&&input.x.x==input.z.x&&input.x.y==input.z.y;
 if(points>=2&&neutral)return input;float peak=pmv_peak(pmvp_high(input));if(peak==0)return input;
 pmvp3 xyz=pmvp_dwg_xyz(pmvp_div(input,peak)),rec=pmcf_xyz_rec(xyz),xy=pmcf_xy(rec);
 // The adapter's canonical relative-white gray is exact by contract despite published matrix rounding.
 if(neutral)xy.y=xy.z=pm_pair(0);
 pmvp3 target=pmcf_endpoint(xy.y,xy.z,xyz.y,angle,points);float2 t=pm_pair_mul(pm_pair_div(pm_pair(amount),pm_pair(100)),pmah_clamp01(keep));
 float2 da=pm_pair_mul(t,pmvp_sub(target.y,xy.y)),db=pm_pair_mul(t,pmvp_sub(target.z,xy.z));
 if(!pmvp_positive(pmvp_abs(da))&&!pmvp_positive(pmvp_abs(db)))return input;
 pmvp3 dxyz=pmcf_rec_xyz(pmcf_delta_rgb(da,db));dxyz.y=pm_pair(0);
 pmvp3 delta=pmcf_xyz_dwg(dxyz);pmvp3 out=pmvp_add(input,pmvp_scale(delta,pm_pair(peak)));
 return pmvp_finite(out)?out:input;
}
#endif

__DEVICE__ int pmif_points_from_ui(int index){
 if(index==0)return 1;if(index==1)return 2;if(index==2)return 3;if(index==3)return 4;if(index==4)return 6;return 0;
}

// Public Threshold lower80 maps linearly to old normalized0..25.
// Upper20 uses a monotonic C1 Hermite join; creative core is unchanged.
__DEVICE__ float pmi_threshold_ui(float threshold,float amount){
 if(!pm_finite(threshold)||threshold<=0.0f||threshold>=100.0f||amount==0.0f)return threshold;
 if(threshold<=80.0f)return pm_rn_mul(threshold,0.3125f);
 float2 v=pm_pair_div(pmvp_sub(pm_pair(threshold),pm_pair(80.0f)),pm_pair(20.0f));
 float2 blend=pm_pair_mul(pm_pair_mul(v,v),pmvp_sub(pm_pair(3.0f),pm_pair_mul(pm_pair(2.0f),v)));
 return pmvp_round(pm_pair_add(pm_pair(25.0f),pm_pair_add(pm_pair_mul(pm_pair(6.25f),v),pm_pair_mul(pm_pair(68.75f),blend))));
}
__DEVICE__ pmc_core_result pmi_identity(float2 r,float2 g,float2 b){
    pmc_core_result result;result.r=result.pre_r=result.comp_r=r;result.g=result.pre_g=result.comp_g=g;result.b=result.pre_b=result.comp_b=b;result.changed=result.pre_changed=result.comp_changed=0;return result;
}
typedef struct { float3 rgb;int valid; } pmi_encoded_result;
__DEVICE__ pmi_encoded_result pmi_encode_output(float2 r,float2 g,float2 b,int og,int ot) {
    pmi_encoded_result result;result.rgb=make_float3(0.0f,0.0f,0.0f);result.valid=0;
    if(!pma_linear_domain_valid(r,4)||!pma_linear_domain_valid(g,4)||!pma_linear_domain_valid(b,4))return result;
    float2 tr=pma_from_dwg_channel(r,g,b,og,0),tg=pma_from_dwg_channel(r,g,b,og,1),tb=pma_from_dwg_channel(r,g,b,og,2);
    if(!pma_linear_domain_valid(tr,ot)||!pma_linear_domain_valid(tg,ot)||!pma_linear_domain_valid(tb,ot))return result;
    result.rgb=make_float3(pma_encode_channel(tr,ot),pma_encode_channel(tg,ot),pma_encode_channel(tb,ot));
    result.valid=pma_encoded_domain_valid(result.rgb,ot);return result;
}
__DEVICE__ float3 pmi_finish(float3 original,float2 r,float2 g,float2 b,pmc_core_result core,int ig,int it,int og,int ot) {
    int same=pma_profiles_same(ig,it,og,ot);
    if(!core.changed&&same)return original;
    pmi_encoded_result output=pmi_encode_output(core.r,core.g,core.b,og,ot);
    if(output.valid)return output.rgb;
    if(!core.comp_changed&&same)return original;
    output=pmi_encode_output(core.comp_r,core.comp_g,core.comp_b,og,ot);
    if(output.valid)return output.rgb;
    if(!core.pre_changed&&same)return original;
    output=pmi_encode_output(core.pre_r,core.pre_g,core.pre_b,og,ot);
    if(output.valid)return output.rgb;
    if(same)return original;
    output=pmi_encode_output(r,g,b,og,ot);
    return output.valid?output.rgb:original;
}

__DEVICE__ int pmif_ui_integer(float value,int low,int high){
 if(!pm_finite(value)||value<(float)low||value>(float)high)return low-1;
 return (int)_floorf(value+0.5f);
}

typedef struct {pmvp3 pre;pmvp3 hue;pmvp3 comp;pmvp3 density;pmvp3 final;} pmif_stages;
__DEVICE__ pmif_stages pmif_process(pmvp3 input,
 float pre,float threshold,float compression,float softness,float density,float chroma,float response,float shadow,float sr,float highlight,float hr,float sat_skin,float density_skin,int db,
 float angle,int points,float hc,float st,float sk,float ht,float hk){
 pmif_stages z;z.pre=z.hue=z.comp=z.density=z.final=input;
 if(db<0||db>1||!pmvp_finite(input)||!pmc_controls_valid(pre,threshold,compression,softness,density,chroma,response,shadow,sr,highlight,hr,sat_skin,density_skin)||!pmah_controls_valid(angle,points,hc,50.0f)||!pmfd_control(st)||!pmfd_control(sk)||!pmfd_control(ht)||!pmfd_control(hk))return z;
 if(hc==0.0f){
  pmc_core_result c=pmc_process_core(input.x,input.y,input.z,pre,threshold,compression,softness,density,chroma,response,shadow,sr,highlight,hr,sat_skin,density_skin,db);
  z.pre=pmvp_make(c.pre_r,c.pre_g,c.pre_b);z.hue=z.pre;z.comp=pmvp_make(c.comp_r,c.comp_g,c.comp_b);z.density=pmvp_make(c.r,c.g,c.b);
 }else{
  pmvq_input_result p=pmc_prepare_stages(input.x,input.y,input.z,pre,sat_skin,density_skin);z.pre=p.presat;
  z.hue=pmcf_process(z.pre,p.keep_sat,angle,points,hc);
  z.comp=pmc_comp_stage(z.hue,threshold,compression,softness,p.keep_sat);
  z.density=pmc_density_stage(z.comp,density,chroma,response,shadow,sr,highlight,hr,p.keep_density,db);
 }
 z.final=pmc_final_desat(z.density.x,z.density.y,z.density.z,st,sk,ht,hk);return z;
}
__DEVICE__ int pmif_neutral(pmvp3 x){return x.x.x==x.y.x&&x.x.y==x.y.y&&x.x.x==x.z.x&&x.x.y==x.z.y;}
__DEVICE__ pmi_encoded_result pmif_encode_final_neutral(pmvp3 final,int ot){
 // A final-desat endpoint is relative normalized white in every supported
 // output primaries. Preserve that semantic exactly here only. The general
 // adapter matrices/pure conversions are unchanged.
 pmi_encoded_result o;o.valid=0;o.rgb=make_float3(0.0f,0.0f,0.0f);
 if(!pma_linear_domain_valid(final.x,ot))return o;
 float e=pma_encode_channel(final.x,ot);o.rgb=make_float3(e,e,e);o.valid=pma_encoded_domain_valid(o.rgb,ot);return o;
}
__DEVICE__ float3 pmif_finish(float3 original,pmvp3 input,pmif_stages z,int ig,int it,int og,int ot){
 int same=pma_profiles_same(ig,it,og,ot);
 for(int i=0;i<6;i++){
  pmvp3 stage=i==0?z.final:(i==1?z.density:(i==2?z.comp:(i==3?z.hue:(i==4?z.pre:input))));
  if(same&&pmvp_same(stage,input))return original;
  int neutral_endpoint=i==0&&!pmvp_same(z.final,z.density)&&pmif_neutral(z.final);
  pmi_encoded_result o=neutral_endpoint?pmif_encode_final_neutral(stage,ot):pmi_encode_output(stage.x,stage.y,stage.z,og,ot);
  if(o.valid)return o.rgb;
 }
 return original;
}

__DEVICE__ float3 transform(int p_Width,int p_Height,int p_X,int p_Y,float p_R,float p_G,float p_B) {
 float3 original=make_float3(p_R,p_G,p_B);int ig=pmi_ig,it=pmi_it;
 int og=pmi_og==0?ig:pmi_og-1,ot=pmi_ot==0?it:pmi_ot-1;
 if(!pma_profile_valid(ig,it)||!pma_profile_valid(og,ot)||!pma_encoded_domain_valid(original,it))return original;
 float2 sr=pma_decode_channel(p_R,it),sg=pma_decode_channel(p_G,it),sb=pma_decode_channel(p_B,it);
 if(!pma_linear_domain_valid(sr,it)||!pma_linear_domain_valid(sg,it)||!pma_linear_domain_valid(sb,it))return original;
 pmvp3 input=pmvp_make(pma_to_dwg_channel(sr,sg,sb,ig,0),pma_to_dwg_channel(sr,sg,sb,ig,1),pma_to_dwg_channel(sr,sg,sb,ig,2));
 int points=pmif_points_from_ui(pm_hue_points_index),db=pmif_ui_integer(pm_db,0,1);
 pmif_stages z;
 if(p_R==p_G&&p_G==p_B&&!(points==1&&pm_hue_compression>0.0f))z.pre=z.hue=z.comp=z.density=z.final=input;
 else z=pmif_process(input,pm_pre,pmi_threshold_ui(pm_threshold,pm_compression),pm_compression,pm_softness,pm_density,pm_chroma,pm_response,pm_shadow,pm_sr,pm_highlight,pm_hr,pm_sat_skin,pm_density_skin,db,
  pm_hue_angle,points,pm_hue_compression,pm_sd_t,pm_sd_k,pm_hd_t,pm_hd_k);
 return pmif_finish(original,input,z,ig,it,og,ot);
}

}
#ifdef _WIN32
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif
EXPORT void pm_eval(const float*x,const double*v,int premult,float*out){pm::pixel(fromValues(v),x,out,premult);}
EXPORT int pm_identity(const double*v){return pm::identity(fromValues(v));}
EXPORT void pm_baseline(const float*x,const double*v,float*out){original::pmi_ig=(int)v[0];original::pmi_it=(int)v[1];original::pmi_og=(int)v[2];original::pmi_ot=(int)v[3];original::pm_pre=(float)v[4];original::pm_hue_angle=(float)v[5];original::pm_hue_points_index=(int)v[6];original::pm_hue_compression=(float)v[7];original::pm_threshold=(float)v[8];original::pm_compression=(float)v[9];original::pm_softness=(float)v[10];original::pm_sat_skin=(float)v[11];original::pm_density=(float)v[12];original::pm_chroma=(float)v[13];original::pm_response=(float)v[14];original::pm_shadow=(float)v[15];original::pm_sr=(float)v[16];original::pm_highlight=(float)v[17];original::pm_hr=(float)v[18];original::pm_density_skin=(float)v[19];original::pm_db=(int)v[20];original::pm_sd_t=(float)v[21];original::pm_sd_k=(float)v[22];original::pm_hd_t=(float)v[23];original::pm_hd_k=(float)v[24];auto z=original::transform(1,1,0,0,x[0],x[1],x[2]);out[0]=z.x;out[1]=z.y;out[2]=z.z;out[3]=x[3];}
