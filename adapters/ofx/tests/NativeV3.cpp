#include "../generated/PixelCore.hpp"
#include "../generated/ParameterValues.hpp"
#ifdef _WIN32
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif
EXPORT void pm_eval30(const float* x,const double* v,int premult,float* out){pm::pixel(fromValues(v),x,out,premult);}
EXPORT int pm_identity30(const double* v){return pm::identity(fromValues(v));}
static double value(pm::float2 x){return (double)x.x+(double)x.y;}
static pm::float2 pair(double x){float hi=(float)x;return pm::make_float2(hi,(float)(x-(double)hi));}
static void write(pm::pmvp3 x,double* out){out[0]=value(x.x);out[1]=value(x.y);out[2]=value(x.z);}
EXPORT void pm_vnext_scalar(double y,double bias,double split,double u,double* out){
 auto q=pm::pmvn_q_ref(pair(y));out[0]=value(q);out[1]=value(pm::pmvn_drive((float)bias,(float)split,q));out[2]=value(pm::pmvn_F(pair(u)));
}
EXPORT void pm_vnext_target(double a,double b,double y,double angle,int pattern,double* out){
 write(pm::pmvn_target(pair(a),pair(b),pair(y),pm::pmvn_phase((float)angle),pattern),out);
}
EXPORT void pm_vnext_hue(const double* x,double y,double angle,int pattern,double strength,double bias,double split,double* out){
 write(pm::pmvn_hue(pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2])),pair(y),(float)angle,pattern,(float)strength,(float)bias,(float)split),out);
}
EXPORT void pm_vnext_stages30(const double* x,const double* v,double* out){
 auto p=fromValues(v);auto input=pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2]));
 auto z=pm::pmvn_process_makeup(input,p.pm_pre,pm::pmi_threshold_ui(p.pm_threshold,p.pm_compression),p.pm_compression,p.pm_softness,p.pm_density,p.pm_chroma,p.pm_response,p.pm_shadow,p.pm_sr,p.pm_highlight,p.pm_hr,p.pm_sat_skin,p.pm_density_skin,p.pm_db,p.pm_hue_angle,p.pm_hue_pattern,p.pm_hue_compression,p.pm_hue_bias,p.pm_luma_split,p.pm_sd_t,p.pm_sd_k,p.pm_hd_t,p.pm_hd_k,p.pm_luma_pivot_ev,p.pm_luma_width,p.pm_makeup);
 write(z.pre_raw,out);write(z.conditioned,out+3);write(z.hue,out+6);write(z.look,out+9);write(z.final,out+12);
 auto analysis=pm::pmc_prepare_stages(input.x,input.y,input.z,100.0f,p.pm_sat_skin,p.pm_density_skin);
 out[15]=value(analysis.keep_sat);out[16]=value(analysis.keep_density);
}
EXPORT void pm_vnext_legacy_neutral_hue30(const double* x,const double* v,double* out){
 auto p=fromValues(v);auto input=pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2]));
 auto z=pm::pmif_process(input,p.pm_pre,pm::pmi_threshold_ui(p.pm_threshold,p.pm_compression),p.pm_compression,p.pm_softness,p.pm_density,p.pm_chroma,p.pm_response,p.pm_shadow,p.pm_sr,p.pm_highlight,p.pm_hr,0.0f,0.0f,p.pm_db,p.pm_hue_angle,2,0.0f,p.pm_sd_t,p.pm_sd_k,p.pm_hd_t,p.pm_hd_k);
 write(z.final,out);
}
EXPORT void pm_vnext_density30(const double* x,const double* v,double* out){
 auto p=fromValues(v);write(pm::pmc_density_stage(pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2])),p.pm_density,p.pm_chroma,p.pm_response,p.pm_shadow,p.pm_sr,p.pm_highlight,p.pm_hr,pm::pm_pair(1.0f),p.pm_db),out);
}
EXPORT double pm_vnext_y(const double* x){return value(pm::pmvpy_Y(pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2]))));}
#include "../generated/DctlReferenceV3Curve.hpp"
EXPORT void pm_dctl_eval30(const float* x,const double* v,float* out){
 generated_dctl::readValues(v);
 auto z=generated_dctl::transform(1,1,0,0,x[0],x[1],x[2]);
 out[0]=z.x;out[1]=z.y;out[2]=z.z;out[3]=x[3];
}

EXPORT void pm_vnext_curve(double y,double pivot,double width,double* out){
 out[0]=value(pm::pmvn_q_ref(pair(y)));out[1]=value(pm::pmvn_curve_q_ref(pair(y),(float)pivot,(float)width));
}
EXPORT void pm_vnext_hue_curve(const double* x,double y,double angle,int pattern,double strength,double bias,double split,double pivot,double width,double* out){
 write(pm::pmvn_hue_curve(pm::pmvp_make(pair(x[0]),pair(x[1]),pair(x[2])),pair(y),(float)angle,pattern,(float)strength,(float)bias,(float)split,(float)pivot,(float)width),out);
}

// Retain the old diagnostic29-value C entrypoints. New callers use explicit30 names.
static void oldValues(const double*v,double*out){for(int i=0;i<29;i++)out[i]=v[i];out[29]=100.;}
EXPORT void pm_eval(const float*x,const double*v,int m,float*out){double a[30];oldValues(v,a);pm_eval30(x,a,m,out);}
EXPORT int pm_identity(const double*v){double a[30];oldValues(v,a);return pm_identity30(a);}
EXPORT void pm_vnext_stages(const double*x,const double*v,double*out){double a[30];oldValues(v,a);pm_vnext_stages30(x,a,out);}
EXPORT void pm_vnext_legacy_neutral_hue(const double*x,const double*v,double*out){double a[30];oldValues(v,a);pm_vnext_legacy_neutral_hue30(x,a,out);}
EXPORT void pm_vnext_density(const double*x,const double*v,double*out){double a[30];oldValues(v,a);pm_vnext_density30(x,a,out);}
EXPORT void pm_dctl_eval(const float*x,const double*v,float*out){double a[30];oldValues(v,a);pm_dctl_eval30(x,a,out);}

// Direct mask boundary probe: exact DI coordinates avoid inverse-transfer rounding.
EXPORT void pm_final_masks(double level,double st,double sk,double ht,double hk,double* out){
 out[0]=value(pm::pmfd_shadow_keep(pair(level),(float)st,(float)sk));
 out[1]=value(pm::pmfd_highlight_keep(pair(level),(float)ht,(float)hk));
}
