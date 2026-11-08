#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <vector>
#include "../generated/PixelCore.hpp"
#include "DensityGraph.hpp"

// Display model only. No image handles, render flags, GPU work or parameter writes.
namespace pmhud {
struct Sample {float x,y;};
struct Swatch {float r,g,b;};
struct Model {
 pm::Parameters parameters{};
 int points=0;
 std::array<Swatch,6> swatches{};
 std::vector<Sample> compression,finalKeep;
 DensityGraph density;
};
inline float compressionOut(const pm::Parameters&p,float s){
 if(s<=0.0f)return 0.0f;
 if(p.pm_threshold==100.0f||p.pm_compression==0.0f)return s;
 const float t=pm::pmc_threshold_raw(pm::pmi_threshold_ui(p.pm_threshold,p.pm_compression),p.pm_softness);
 const auto c=pm::pm_pair_div(pm::pm_pair(s),pm::pm_pair(100.0f));
 return pm::pmvp_round(pm::pm_pair_mul(pm::pm_pair(s),
  pm::pm_continuous_scale_pair(pm::pm_pair(1.0f),c,t,p.pm_compression,p.pm_softness)));
}
inline float finalKeep(const pm::Parameters&p,float x){
 return pm::pmvp_round(pm::pm_pair_mul(pm::pmfd_shadow_keep(pm::pm_pair(x),p.pm_sd_t,p.pm_sd_k),
  pm::pmfd_highlight_keep(pm::pm_pair(x),p.pm_hd_t,p.pm_hd_k)));
}
inline float srgb(float x){return x<=0.0031308f?12.92f*x:1.055f*std::pow(x,1.0f/2.4f)-0.055f;}
inline Swatch directionSwatch(const pm::Parameters&p,int point,int count){
 // Same pair-valued CF2 phase and directions as the core. This is a display
 // direction key at the sRGB gamut boundary, not a prediction of output RGB.
 auto phi=pm::pm_pair_add(pm::pmcf_phase(),pm::pm_pair_mul(pm::pm_pair(p.pm_hue_angle==360?0:p.pm_hue_angle),
  pm::make_float2(1.74532923847436905e-02f,1.35199601514202072e-10f)));
 const auto sector=pm::pm_pair_div(pm::make_float2(6.28318548202514648f,-1.74845553146951715e-07f),pm::pm_pair((float)count));
 phi=pm::pm_pair_add(phi,pm::pm_pair_mul(pm::pm_pair((float)point),sector));
 const auto u=pm::pmcf_unit(phi);
 auto xyz=pm::pmcf_rec_xyz(pm::pmcf_delta_rgb(u.y,u.z));
 xyz.y=pm::pm_pair(0.0f); // core holds Y while moving along these directions
 const double x=(double)xyz.x.x+xyz.x.y,z=(double)xyz.z.x+xyz.z.y;
 double rgb[3]={3.2409699419045226*x-0.4986107602930034*z,
               -0.9692436362808796*x+0.0415550574071756*z,
                0.0556300796969937*x+1.0569715142428786*z};
 const double lo=std::min(rgb[0],std::min(rgb[1],rgb[2]));
 const double hi=std::max(rgb[0],std::max(rgb[1],rgb[2]));
 if(!(hi>lo))return {0,0,0};
 return {srgb((float)((rgb[0]-lo)/(hi-lo))),srgb((float)((rgb[1]-lo)/(hi-lo))),srgb((float)((rgb[2]-lo)/(hi-lo)))};
}
inline Model makeModel(const pm::Parameters&p){
 Model m;m.parameters=p;m.density=makeDensityGraph(p);m.points=pm::pmif_points_from_ui(p.pm_hue_points_index);
 for(int i=0;i<m.points;++i)m.swatches[i]=directionSwatch(p,i,m.points);
 for(int i=0;i<=128;++i){
  const float x=(float)i/128.0f;
  m.compression.push_back({x,compressionOut(p,x*100.0f)/100.0f});
  m.finalKeep.push_back({x,finalKeep(p,x)});
 }
 // Include exact tonal boundaries and both sides of zero-knee discontinuities.
 for(float x:{p.pm_sd_t,std::max(0.0f,p.pm_sd_t-p.pm_sd_k),p.pm_hd_t,std::min(1.0f,p.pm_hd_t+p.pm_hd_k)}){
  if(x<0||x>1)continue;
  m.finalKeep.push_back({x,finalKeep(p,x)});
  if(x>0){float v=std::nextafter(x,0.0f);m.finalKeep.push_back({v,finalKeep(p,v)});}
  if(x<1){float v=std::nextafter(x,1.0f);m.finalKeep.push_back({v,finalKeep(p,v)});}
 }
 std::stable_sort(m.finalKeep.begin(),m.finalKeep.end(),[](Sample a,Sample b){return a.x<b.x;});
 return m;
}
}
