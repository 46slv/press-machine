#include "../../vnext/generated/PixelCore.hpp"
#include "../../vnext/generated/ParameterValues.hpp"
#ifdef _WIN32
#define PMVN_EXPORT __declspec(dllexport)
#else
#define PMVN_EXPORT __attribute__((visibility("default")))
#endif
extern "C" {
PMVN_EXPORT void pm_vnext_eval(const float*in,const double*values,int premult,float*out){pm::pixel(fromValues(values),in,out,premult);}
PMVN_EXPORT int pm_vnext_identity(const double*values){return pm::identity(fromValues(values))?1:0;}
PMVN_EXPORT float pm_vnext_skin_mask(const float*rgb){pm::pmvp3 x=pm::pmvp_make(pm::pm_pair(rgb[0]),pm::pm_pair(rgb[1]),pm::pm_pair(rgb[2]));return pm::pmvp_round(pm::pmvn_skin_mask(x));}
PMVN_EXPORT void pm_vnext_stages(const float*rgb,const double*values,float*out){
 auto p=fromValues(values);pm::pmvp3 x=pm::pmvp_make(pm::pm_pair(rgb[0]),pm::pm_pair(rgb[1]),pm::pm_pair(rgb[2]));
 auto z=pm::pmvn_process(x,p.pm_pre,pm::pmi_threshold_ui(p.pm_threshold,p.pm_compression),p.pm_compression,p.pm_softness,p.pm_sat_skin,p.pm_hue_angle,p.pm_hue_pattern,p.pm_hue_compression,p.pm_hue_bias,p.pm_luma_split,p.pm_density,p.pm_chroma,p.pm_response,p.pm_shadow,p.pm_sr,p.pm_highlight,p.pm_hr,p.pm_density_skin,p.pm_db,p.pm_sd_t,p.pm_sd_k,p.pm_hd_t,p.pm_hd_k);
 pm::pmvp3 s[7]={z.pre_raw,z.comp_raw,z.conditioned,z.hue,z.density_raw,z.look,z.final};for(int i=0;i<7;i++){auto h=pm::pmvp_high(s[i]);out[3*i]=h.x;out[3*i+1]=h.y;out[3*i+2]=h.z;}
}}
