#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <string>
#include <limits>
#include <vector>
#include "../generated/PixelCore.hpp"
namespace pmhud {
struct DensitySample {
 float inputEV=0,deltaEV=0,deltaSatPercent=0;
 bool validEV=false,validSat=false;
};
struct DensityGraph {
 std::array<std::vector<DensitySample>,3> curves;
 float evRange=1.5f,satRange=10.0f;
 int validSatCount=0;
};
inline pm::float2 pairDouble(double v){
 const float hi=(float)v;return pm::make_float2(hi,(float)(v-(double)hi));
}
inline double pairDoubleValue(pm::float2 v){return (double)v.x+(double)v.y;}
inline double displayDecode(double v){return v<=.04045?v/12.92:std::pow((v+.055)/1.055,2.4);}
inline pm::pmvp3 referenceInput(int index,float ev){
 // Fixed D65 sRGB reference colors, decoded then converted to scene-linear DWG.
 // Skin is the existing chart reference. Red/Blue are synthetic comparison colors.
 static const double colors[3][3]={{194.0/255,150.0/255,130.0/255},{.80,.15,.10},{.12,.25,.85}};
 const double rr=displayDecode(colors[index][0]),gg=displayDecode(colors[index][1]),bb=displayDecode(colors[index][2]);
 const auto xyz=pm::pmvp_make(
  pairDouble(.4123907992659595*rr+.3575843393838780*gg+.1804807884018343*bb),
  pairDouble(.2126390058715104*rr+.7151686787677560*gg+.0721923153607337*bb),
  pairDouble(.0193308187155919*rr+.1191947797946260*gg+.9505321522496606*bb));
 const auto dwg=pm::pmcf_xyz_dwg(xyz);
 const auto y=pm::pmvpy_Y(dwg);
 return pm::pmvp_scale(dwg,pm::pm_pair_div(pairDouble(.18*std::exp2((double)ev)),y));
}
inline pm::pmvn_stages densityStages(const pm::Parameters&p,pm::pmvp3 input){
 // Whole upstream path preserves the Skin mask made from original input.
 // Input/output encoding settings are inapplicable to already-linear DWG probes.
 return pm::pmvn_process_makeup(input,p.pm_pre,pm::pmi_threshold_ui(p.pm_threshold,p.pm_compression),
  p.pm_compression,p.pm_softness,p.pm_density,p.pm_chroma,p.pm_response,p.pm_shadow,p.pm_sr,
  p.pm_highlight,p.pm_hr,p.pm_sat_skin,p.pm_density_skin,p.pm_db,
  p.pm_hue_angle,p.pm_hue_pattern,p.pm_hue_compression,p.pm_hue_bias,p.pm_luma_split,
  p.pm_sd_t,p.pm_sd_k,p.pm_hd_t,p.pm_hd_k,p.pm_luma_pivot_ev,p.pm_luma_width,p.pm_makeup);
}
inline DensitySample sampleDensity(const pm::Parameters&p,int probe,float ev){
 DensitySample s;s.inputEV=ev;
 const auto z=densityStages(p,referenceInput(probe,ev));
 // Both endpoints use the same Look protection from the original input.
 // conditioned -> look would include Hue, so it is not a Density-only measure.
 if(!pm::pmvp_finite(z.hue)||!pm::pmvp_finite(z.look))return s;
 const double y0=pairDoubleValue(pm::pmvpy_Y(z.hue)),y1=pairDoubleValue(pm::pmvpy_Y(z.look));
 if(y0>0&&y1>0){
  const double delta=std::log2(y1/y0);
  if(std::isfinite(delta)&&std::abs(delta)<=std::numeric_limits<float>::max()){s.deltaEV=(float)delta;s.validEV=true;}
 }
 const auto lab0=pm::pmvp_lab(z.hue),lab1=pm::pmvp_lab(z.look);
 const double l0=pairDoubleValue(lab0.x),l1=pairDoubleValue(lab1.x);
 const double c0=pairDoubleValue(pm::pmvp_chroma(lab0)),c1=pairDoubleValue(pm::pmvp_chroma(lab1));
 if(l0>0&&l1>0&&std::isfinite(l0)&&std::isfinite(l1)&&std::isfinite(c0)&&std::isfinite(c1)){
  const double sat0=c0/l0,sat1=c1/l1;
  // A neutral/near-neutral protected Hue result has no stable percentage denominator.
  if(sat0>1e-5&&sat1>=0){
   const double delta=100.0*(sat1/sat0-1);
   if(std::isfinite(delta)&&std::abs(delta)<=std::numeric_limits<float>::max()){s.deltaSatPercent=(float)delta;s.validSat=true;}
  }
 }
 return s;
}
inline float plotRange(float maximum,float minimum){
 if(maximum<=minimum)return minimum;
 const float nice[]={1.5f,3,4.5f,10,25,50,100,200,500,1000};
 for(float v:nice)if(v>=minimum&&v>=maximum)return v;
 return std::pow(10.0f,std::ceil(std::log10(maximum)));
}
inline std::string densityRangeLabel(float range){
 char text[24];
 if(range>=1000)std::snprintf(text,sizeof text,"@1E%.0f",std::round(std::log10(range)));
 else if(range<10)std::snprintf(text,sizeof text,"@%.1f",range);
 else std::snprintf(text,sizeof text,"@%.0f",range);
 return text;
}
inline DensityGraph makeDensityGraph(const pm::Parameters&p){
 DensityGraph g;float evMax=0,satMax=0;
 // Each stage evaluation supplies BOTH plots. No image access or per-frame readback.
 for(int probe=0;probe<3;++probe)for(int i=0;i<=32;++i){
  auto s=sampleDensity(p,probe,-6.0f+12.0f*i/32.0f);
  g.curves[probe].push_back(s);
  if(s.validEV)evMax=std::max(evMax,std::abs(s.deltaEV));
  if(s.validSat){satMax=std::max(satMax,std::abs(s.deltaSatPercent));++g.validSatCount;}
 }
 g.evRange=plotRange(evMax,1.5f);g.satRange=plotRange(satMax,10.0f);
 return g;
}
}
