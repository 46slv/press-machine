#pragma once
#include "DensityGraph.hpp"
namespace pmhud {
struct NeutralHueSample {float x=0,strength=0;std::array<float,3> direction{},preview{};bool displayClipped=false;};
struct NeutralHueGraph {std::vector<NeutralHueSample> samples;float range=1;bool displayClipped=false;};
inline std::array<double,3> neutralSrgb(double x,double y,double z){return {3.2409699419045226*x-1.537383177570094*y-.4986107602930034*z,-.9692436362808796*x+1.8759675015077202*y+.0415550574071756*z,.0556300796969937*x-.2039769588889765*y+1.0569715142428786*z};}
inline float neutralEncode(double x){return (float)(x<=.0031308?12.92*x:1.055*std::pow(x,1./2.4)-.055);}
inline NeutralHueSample sampleNeutralHue(const pm::Parameters&p,float x){
 NeutralHueSample s;s.x=x;const double Y=.18*std::exp2(-6.+12.*x);
 const auto input=pm::pmvp_make(pairDouble(Y),pairDouble(Y),pairDouble(Y));
 const auto before=pm::pmvp_dwg_xyz(input);
 const auto out=pm::pmvn_hue_curve(input,pm::pmvpy_Y(input),p.pm_hue_angle,p.pm_hue_pattern,p.pm_hue_compression,p.pm_hue_bias,p.pm_luma_split,p.pm_luma_pivot_ev,p.pm_luma_width);
 const auto xyz=pm::pmvp_dwg_xyz(out);
 const auto delta=pm::pmvp_make(pm::pmvp_sub(xyz.x,before.x),pm::pmvp_sub(xyz.y,before.y),pm::pmvp_sub(xyz.z,before.z));
 const auto ab=pm::pmcf_xy(pm::pmcf_xyz_rec(delta));
 s.strength=(float)(std::hypot(pairDoubleValue(ab.y),pairDoubleValue(ab.z))/pairDoubleValue(pm::pmvpy_Y(input)));
 auto rgb=neutralSrgb(pairDoubleValue(delta.x)/Y,0,pairDoubleValue(delta.z)/Y);
 const double lo=*std::min_element(rgb.begin(),rgb.end()),hi=*std::max_element(rgb.begin(),rgb.end());
 for(int i=0;i<3;i++)s.direction[i]=s.strength>1e-10f&&hi>lo?neutralEncode((rgb[i]-lo)/(hi-lo)):.7f;
 rgb=neutralSrgb(.18*pairDoubleValue(xyz.x)/Y,.18*pairDoubleValue(xyz.y)/Y,.18*pairDoubleValue(xyz.z)/Y);
 for(int i=0;i<3;i++){s.displayClipped|=rgb[i]<0||rgb[i]>1;s.preview[i]=neutralEncode(std::clamp(rgb[i],0.,1.));}
 return s;
}
inline NeutralHueGraph makeNeutralHueGraph(const pm::Parameters&p){
 NeutralHueGraph g;float maximum=0;
 for(int i=0;i<=128;i++){auto s=sampleNeutralHue(p,i/128.f);g.samples.push_back(s);maximum=std::max(maximum,s.strength);g.displayClipped|=s.displayClipped;}
 for(float r:{1.f,2.f,5.f,10.f,25.f,50.f,100.f})if(maximum<=r){g.range=r;return g;}
 g.range=std::pow(10.f,std::ceil(std::log10(maximum)));return g;
}
}
