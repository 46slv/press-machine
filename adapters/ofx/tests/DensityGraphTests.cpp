#include "../src/DensityGraph.hpp"
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <set>
#include <vector>
using pmhud::DensityGraph;
void require(bool ok,const char*s){if(!ok)throw std::runtime_error(s);}
int validCount(const DensityGraph&g,bool sat){
 int n=0;for(auto c:g.curves)for(auto s:c)if(sat?s.validSat:s.validEV)++n;return n;
}
double difference(const DensityGraph&a,const DensityGraph&b,bool sat,int probe=-1){
 double sum=0;for(int k=0;k<3;++k){if(probe>=0&&k!=probe)continue;
  for(size_t i=0;i<a.curves[k].size();++i){auto x=a.curves[k][i],y=b.curves[k][i];
   require(!(sat?x.validSat!=y.validSat:x.validEV!=y.validEV),"comparison sample validity differs");
   if(sat?x.validSat&&y.validSat:x.validEV&&y.validEV)
    sum+=std::abs((double)(sat?x.deltaSatPercent:x.deltaEV)-(sat?y.deltaSatPercent:y.deltaEV));
  }}return sum;
}
bool flat(const DensityGraph&g){
 if(validCount(g,false)!=99||validCount(g,true)!=99)return false;
 for(auto c:g.curves)for(auto s:c){
  if(s.validEV&&std::abs(s.deltaEV)>1e-5)return false;
  if(s.validSat&&std::abs(s.deltaSatPercent)>1e-4)return false;
 }return true;
}
int main(int argc,char**argv){
 try{
 auto p=pm::defaultParameters();p.pm_density=80;p.pm_chroma=50;
 auto base=pmhud::makeDensityGraph(p);std::vector<std::string> checks;
 auto check=[&](bool ok,const char*name){require(ok,name);checks.push_back(name);};
 check(validCount(base,false)==99&&validCount(base,true)==99,"baseline_all_reference_samples_valid");
 for(float range:{1.5f,3.f,4.5f,10.f,25.f,50.f,100.f,200.f,500.f,1000.f,1e6f,1e12f})
  check(pmhud::densityRangeLabel(range).size()<=5,"range_labels_fit_30_pixel_margin");
 for(int k=0;k<3;++k)for(float e:{-6.f,0.f,6.f}){
  const double y=pmhud::pairDoubleValue(pm::pmvpy_Y(pmhud::referenceInput(k,e)));
  check(std::abs(y/(.18*std::exp2(e))-1)<1e-9,"reference_input_Y_calibration");
 }
 auto q=p;q.pm_density=0;check(flat(pmhud::makeDensityGraph(q)),"density_zero_flattens_both");
 q.pm_chroma=-100;check(flat(pmhud::makeDensityGraph(q)),"chroma_inactive_at_density_zero");
 q=p;q.pm_density=-80;auto negative=pmhud::makeDensityGraph(q);
 check(difference(base,negative,false)>1,"density_sign_changes_EV");
 for(int k=0;k<3;++k)for(int i=0;i<33;++i)
  check(base.curves[k][i].validEV&&negative.curves[k][i].validEV&&base.curves[k][i].deltaEV<=1e-5f&&negative.curves[k][i].deltaEV>=-1e-5f,"density_sign_matches_brightness_direction");
 q=p;q.pm_chroma=-50;auto negC=pmhud::makeDensityGraph(q);
 check(difference(base,negC,true)>.1,"chroma_changes_relative_sat");
 q=p;q.pm_chroma=0;auto zeroC=pmhud::makeDensityGraph(q);double zeroCSat=0;
 for(auto c:zeroC.curves)for(auto v:c){check(v.validSat,"zero_chroma_samples_valid");zeroCSat+=std::abs(v.deltaSatPercent);}
 check(zeroCSat<1e-4,"zero_chroma_preserves_relative_saturation");
 check(difference(base,negC,false)<1e-5,"chroma_preserves_density_Y_law");
 q=p;q.pm_response=1;auto r1=pmhud::makeDensityGraph(q);q.pm_response=4;
 check(difference(r1,pmhud::makeDensityGraph(q),false)>.1,"response_changes_color_weight");
 q=p;q.pm_shadow=100;auto shadow=pmhud::makeDensityGraph(q);
 check(difference(base,shadow,false)>.1&&difference(base,shadow,true)>.1,"shadow_protection_changes_both_curves");
 q.pm_sr=0;auto sr0=pmhud::makeDensityGraph(q);q.pm_sr=100;
 check(difference(sr0,pmhud::makeDensityGraph(q),false)>.1,"shadow_range_changes_curve_with_protect");
 q=p;q.pm_sr=0;auto inactiveSR=pmhud::makeDensityGraph(q);q.pm_sr=100;
 check(difference(inactiveSR,pmhud::makeDensityGraph(q),false)==0,"shadow_range_inactive_when_shadow_zero");
 q=p;q.pm_highlight=100;auto highlight=pmhud::makeDensityGraph(q);
 check(difference(base,highlight,false)>.1,"highlight_protection_changes_curve");
 q.pm_hr=0;auto hr0=pmhud::makeDensityGraph(q);q.pm_hr=100;
 check(difference(hr0,pmhud::makeDensityGraph(q),false)>.1,"highlight_range_changes_curve_with_protect");
 q=p;q.pm_hr=0;auto inactiveHR=pmhud::makeDensityGraph(q);q.pm_hr=100;
 check(difference(inactiveHR,pmhud::makeDensityGraph(q),false)==0,"highlight_range_inactive_when_highlight_zero");
 q=p;q.pm_density_skin=100;auto skin=pmhud::makeDensityGraph(q);
 const auto skinDelta=difference(base,skin,false,0),blueDelta=difference(base,skin,false,2);
 check(skinDelta>.1&&skinDelta>blueDelta*2&&difference(base,skin,true,0)>.01,"skin_protection_distinguishes_skin_from_blue_in_both_metrics");
 q=p;q.pm_db=1;auto bypass=pmhud::makeDensityGraph(q);
 check(flat(bypass),"bypass_flattens_both");
 q.pm_density=-300;q.pm_chroma=-100;q.pm_response=4;q.pm_shadow=100;q.pm_highlight=100;q.pm_density_skin=100;
 check(flat(pmhud::makeDensityGraph(q)),"bypass_dominates_all_density_controls");
 q=p;q.pm_pre=50;check(difference(base,pmhud::makeDensityGraph(q),false)>.01,"pre_saturation_feeds_real_density_response");
 q=p;q.pm_compression=75;q.pm_threshold=50;
 check(difference(base,pmhud::makeDensityGraph(q),false)>.01,"compression_feeds_real_density_response");
 q=p;q.pm_hue_angle=45;q.pm_hue_compression=70;
 check(difference(base,pmhud::makeDensityGraph(q),false)>.01,"hue_feeds_real_density_response");
 q=p;q.pm_sd_t=.4f;q.pm_hd_t=.6f;
 auto final=pmhud::makeDensityGraph(q);
 check(difference(base,final,false)==0&&difference(base,final,true)==0,"final_desat_is_outside_density_measurement");
 q=p;q.pmi_ig=3;q.pmi_it=4;q.pmi_og=2;q.pmi_ot=3;
 auto io=pmhud::makeDensityGraph(q);
 check(difference(base,io,false)==0&&difference(base,io,true)==0,"linear_DWG_references_independent_of_IO_encoding");
 // Exactly neutral Comp input makes the percentage denominator undefined, not zero percent.
 q=p;q.pm_pre=0;
 const auto neutral=pmhud::makeDensityGraph(q);
 check(validCount(neutral,false)==99&&neutral.validSatCount==0,"neutral_ratio_is_omitted_not_zero");
 // Original-input Skin mask must survive upstream color changes unchanged.
 q=p;q.pm_hue_angle=60;q.pm_hue_compression=85;q.pm_density_skin=100;
 for(int pattern=0;pattern<6;++pattern)for(float strength:{0.f,85.f})
 for(float bias:{-70.f,60.f})for(float split:{-200.f,180.f}){
  q.pm_hue_pattern=pattern;q.pm_hue_compression=strength;q.pm_hue_bias=bias;q.pm_luma_split=split;
  q.pm_luma_pivot_ev=2;q.pm_luma_width=.5f;q.pm_compression=70;q.pm_pre=130;q.pm_sat_skin=50;
  auto input=pmhud::referenceInput(0,0);
  auto prep=pm::pmc_prepare_stages(input.x,input.y,input.z,100,q.pm_sat_skin,q.pm_density_skin);
  auto pre=pm::pmvq_presat(input,q.pm_pre,pm::pm_pair(1),0,2,.001f,2);
  auto comp=pm::pmc_comp_stage(pre,pm::pmi_threshold_ui(q.pm_threshold,q.pm_compression),q.pm_compression,q.pm_softness,pm::pm_pair(1));
  auto conditioned=pm::pmcc_mix(input,comp,prep.keep_sat);
  const auto peak=pm::pmv_peak(pm::pmvp_high(input));
  const auto yRef=pm::pm_pair_mul(pm::pmvpy_Y(pm::pmvp_div(input,peak)),pm::pm_pair(peak));
  auto hue=pm::pmvn_hue_curve(conditioned,yRef,q.pm_hue_angle,pattern,strength,bias,split,q.pm_luma_pivot_ev,q.pm_luma_width);
  auto den=pm::pmc_density_stage(hue,q.pm_density,q.pm_chroma,q.pm_response,q.pm_shadow,q.pm_sr,q.pm_highlight,q.pm_hr,pm::pm_pair(1),q.pm_db);
  const auto protectedHue=pm::pmcc_mix(conditioned,hue,prep.keep_density);
  const auto protectedLook=pm::pmcc_mix(conditioned,den,prep.keep_density);
  auto z=pmhud::densityStages(q,input);
  check(pm::pmvp_same(z.hue,protectedHue)&&pm::pmvp_same(z.look,protectedLook),"original_input_Look_protection_matches_both_endpoints");
  auto sample=pmhud::sampleDensity(q,0,0);
  const double expectedEV=std::log2(pmhud::pairDoubleValue(pm::pmvpy_Y(protectedLook))/pmhud::pairDoubleValue(pm::pmvpy_Y(protectedHue)));
  const auto beforeLab=pm::pmvp_lab(protectedHue),afterLab=pm::pmvp_lab(protectedLook);
  const double beforeSat=pmhud::pairDoubleValue(pm::pmvp_chroma(beforeLab))/pmhud::pairDoubleValue(beforeLab.x);
  const double afterSat=pmhud::pairDoubleValue(pm::pmvp_chroma(afterLab))/pmhud::pairDoubleValue(afterLab.x);
  check(sample.validEV&&sample.deltaEV==(float)expectedEV,"Density_only_EV_matches_protected_Hue_to_Look");
  check(sample.validSat&&sample.deltaSatPercent==(float)(100*(afterSat/beforeSat-1)),"Density_only_relative_chroma_matches_protected_Hue_to_Look");
  auto bypassHue=q;bypassHue.pm_db=1;
  check(flat(pmhud::makeDensityGraph(bypassHue)),"Density_bypass_flat_with_active_Pattern_Bias_Split_and_Look_protection");
  bypassHue.pm_db=0;bypassHue.pm_density=0;
  check(flat(pmhud::makeDensityGraph(bypassHue)),"Density_zero_flat_with_active_Pattern_Bias_Split_and_Look_protection");
 }
 q=p;q.pm_hue_bias=40;q.pm_luma_split=180;q.pm_hue_compression=0;
 check(difference(base,pmhud::makeDensityGraph(q),false)>.01,"Bias_Split_feed_density_at_zero_Strength");
 const auto defaultCurve=pmhud::makeDensityGraph(q);q.pm_luma_pivot_ev=3;q.pm_luma_width=.25f;
 check(difference(defaultCurve,pmhud::makeDensityGraph(q),false)>.01,"Pivot_Width_feed_real_density_response");
 // Worst nonzero branches: two plots share 99 full stage evaluations, once per model change.
 q=p;q.pm_density=300;q.pm_chroma=100;q.pm_response=4;q.pm_pre=180;q.pm_hue_compression=80;
 q.pm_hue_bias=80;q.pm_luma_split=-250;q.pm_luma_pivot_ev=-4;q.pm_luma_width=.25f;
 q.pm_compression=90;q.pm_threshold=40;q.pm_shadow=65;q.pm_highlight=70;q.pm_density_skin=60;
 std::vector<double> timings;double checksum=0;
 for(int i=0;i<25;++i){
  q.pm_hue_angle=(float)(i*13);
  const auto start=std::chrono::steady_clock::now();auto g=pmhud::makeDensityGraph(q);
  timings.push_back(std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count());
  checksum+=g.curves[0][16].deltaEV+g.curves[1][16].deltaSatPercent;
  for(auto c:g.curves)for(auto s:c){
   check(!s.validEV||(std::isfinite(s.deltaEV)&&std::abs(s.deltaEV)<=g.evRange),"EV_samples_inside_labeled_range");
   check(!s.validSat||(std::isfinite(s.deltaSatPercent)&&std::abs(s.deltaSatPercent)<=g.satRange),"sat_samples_inside_labeled_range");
  }
 }
 std::sort(timings.begin(),timings.end());
 const std::set<std::string> uniqueChecks(checks.begin(),checks.end());
 if(argc>1){std::ofstream out(argv[1]);require(bool(out),"cannot open Density receipt");out<<"{\"status\":\"PASS\",\"assertions\":"<<checks.size()
 <<",\"probes\":[\"Skin sRGB194/150/130\",\"Red sRGB0.80/0.15/0.10\",\"Blue sRGB0.12/0.25/0.85\"],\"samples_per_probe\":33,\"stage_evaluations_per_rebuild\":99"
 <<",\"worst_setting_median_ms\":"<<timings[12]<<",\"worst_setting_p96_ms\":"<<timings[23]
 <<",\"checksum\":"<<checksum<<",\"skin_EV_difference\":"<<skinDelta<<",\"blue_EV_difference\":"<<blueDelta
 <<",\"host_acceptance\":false,\"checks\":[";
 bool first=true;for(const auto&name:uniqueChecks){if(!first)out<<",";first=false;out<<"\""<<name<<"\"";}out<<"]}\n";}
 std::cout<<"Density graph focused tests PASS: "<<checks.size()<<" assertions; worst-branch median "<<timings[12]<<" ms p96 "<<timings[23]<<" ms\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<"Density graph FAIL: "<<e.what()<<"\n";return 1;}
}
