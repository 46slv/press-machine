#include "../src/HudModel.hpp"
#include <cassert>
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <random>
#include <stdexcept>
void require(bool ok,const char*why){if(!ok)throw std::runtime_error(why);}
bool near(float a,float b,float eps=2e-5f){return std::abs(a-b)<=eps;}
int main(int argc,char**argv){
 try{
 auto p=pm::defaultParameters();
 auto base=pmhud::makeModel(p);
 require(base.anchors==2,"default directions");
 for(auto s:base.compression)require(near(s.x,s.y),"default comp identity");
 for(auto s:base.finalKeep)require(s.y==1,"default final identity");
 int counts[6]={1,3,2,3,3,4};int tests=0;
 const float offsets[6][4]={{0},{0,30,330},{0,180},{0,150,210},{0,120,240},{0,90,180,270}};
 for(int index=0;index<6;++index)for(float angle:{0.f,17.2f,180.f,359.9f,360.f}){
  p.pm_hue_pattern=index;p.pm_hue_angle=angle;auto m=pmhud::makeModel(p);
  require(m.anchors==counts[index],"pattern count mapping");
  for(int i=0;i<m.anchors;++i){auto c=m.swatches[i];
   auto reference=p;reference.pm_hue_pattern=0;
   reference.pm_hue_angle=std::fmod(angle+offsets[index][i],360.0f);
   const auto expected=pmhud::directionSwatch(reference,0);
   require(near(c.r,expected.r)&&near(c.g,expected.g)&&near(c.b,expected.b),"Pattern anchor swatch oracle");
   require(std::isfinite(c.r)&&std::isfinite(c.g)&&std::isfinite(c.b),"finite swatch");
   require(near(std::min(c.r,std::min(c.g,c.b)),0),"max sat lower");
   require(near(std::max(c.r,std::max(c.g,c.b)),1),"max sat upper");++tests;}
 }
 p=pm::defaultParameters();
 auto zero=pmhud::makeModel(p);p.pm_hue_angle=360;auto wrap=pmhud::makeModel(p);
 require(std::memcmp(zero.swatches.data(),wrap.swatches.data(),sizeof zero.swatches)==0,"zero/360 exact");
 require(zero.swatches[0].r>zero.swatches[0].g&&zero.swatches[0].g>zero.swatches[0].b,"skin zero orange direction");
 // Curve model is the actual original-input luminance Q and signed Drive.
 for(float pivot:{-6.f,0.f,6.f})for(float width:{.25f,1.f,4.f})
 for(float bias:{-100.f,0.f,100.f})for(float split:{-300.f,0.f,300.f}){
  p=pm::defaultParameters();p.pm_luma_pivot_ev=pivot;p.pm_luma_width=width;
  p.pm_hue_bias=bias;p.pm_luma_split=split;auto m=pmhud::makeModel(p);
  require(m.lumaResponse.size()==129&&m.signedDrive.size()==129,"curve bounded sample count");
  for(size_t i=0;i<m.lumaResponse.size();++i){
   auto q=m.lumaResponse[i],drive=m.signedDrive[i];
   const double y=.18*std::exp2(-6.+12.*q.x),sy=std::sqrt(y),root=std::sqrt(.18)*std::exp2(pivot/2.);
   const double raw=(sy-root)/(sy+root),want=raw/(width+(1-width)*std::abs(raw));
   const double wantDrive=std::tanh(std::log(2.)*(bias/100.+split/100.*want));
   require(near(q.y,(float)want,2e-7f)&&near(drive.y,(float)wantDrive,2e-7f),"Q and Drive scalar oracle");
   const auto core=pm::pmvn_curve_q_ref(pmhud::pairDouble(y),pivot,width);
   require(q.y==pm::pmvp_round(core),"Q exact core mapping");
   require(drive.y==pm::pmvp_round(pm::pmvn_drive(bias,split,core)),"Drive exact core mapping");
   require(q.y>=-1&&q.y<=1&&drive.y>=-1&&drive.y<=1,"signed plot bounds");++tests;
  }
 }
 // All 29 values invalidate, including appended Pivot/Width; invalid input
 // does not poison the cached state. Repeated redraws reuse the same model.
 static_assert(kParameterCount==29,"candidate ABI");
 std::array<double,kParameterCount> values{};values[28]=1;
 pmhud::ModelCache cache;
 require(cache.update(values)==pmhud::CacheUpdate::Rebuilt,"initial cache");
 require(cache.update(values)==pmhud::CacheUpdate::Unchanged,"repeat cache");
 for(size_t i=0;i<values.size();++i){
  auto changed=values;changed[i]+=1;
  require(cache.update(changed)==pmhud::CacheUpdate::Rebuilt,"every parameter invalidates cache");
  require(cache.update(changed)==pmhud::CacheUpdate::Unchanged,"unchanged parameter cache");
  require(cache.update(values)==pmhud::CacheUpdate::Rebuilt,"restored value invalidates cache");
  auto invalid=values;invalid[i]=std::numeric_limits<double>::quiet_NaN();
  require(cache.update(invalid)==pmhud::CacheUpdate::Invalid,"NaN cache rejected");
  invalid[i]=std::numeric_limits<double>::infinity();
  require(cache.update(invalid)==pmhud::CacheUpdate::Invalid,"Inf cache rejected");
  require(cache.update(values)==pmhud::CacheUpdate::Unchanged,"bad input leaves cache intact");++tests;
 }
 p=pm::defaultParameters();
 // Independent scalar transfer oracle for the same unprotected base law.
 for(float threshold:{0.f,20.f,80.f,93.f,99.9f,100.f})for(float amount:{0.f,1.f,50.f,100.f})
 for(float knee:{0.f,20.f,100.f})for(float s:{0.f,.01f,1.f,22.f,50.f,100.f}){
  p.pm_threshold=threshold;p.pm_compression=amount;p.pm_softness=knee;
  float expected=threshold==100||amount==0?s:pm::pm_transfer(s,pm::pmc_threshold_raw(pm::pmi_threshold_ui(threshold,amount),knee),amount,knee);
  require(near(pmhud::compressionOut(p,s),expected,4e-5f),"compression oracle");
  require(pmhud::compressionOut(p,s)<=s+4e-5f,"compression never expands");++tests;
 }
 p=pm::defaultParameters();p.pm_sd_t=.7f;p.pm_sd_k=.7f;p.pm_hd_t=.3f;p.pm_hd_k=.7f;
 auto overlap=pmhud::makeModel(p);
 for(auto s:overlap.finalKeep){
  float a=pm::pmvp_round(pm::pmfd_shadow_keep(pm::pm_pair(s.x),p.pm_sd_t,p.pm_sd_k));
  float b=pm::pmvp_round(pm::pmfd_highlight_keep(pm::pm_pair(s.x),p.pm_hd_t,p.pm_hd_k));
  require(near(s.y,a*b),"overlap product");require(s.y>=0&&s.y<=1,"keep range");++tests;
 }
 p.pm_sd_t=.234567f;p.pm_sd_k=0;p.pm_hd_t=.765432f;p.pm_hd_k=0;
 auto step=pmhud::makeModel(p);bool shLo=false,shHi=false,hiLo=false,hiHi=false;
 for(auto s:step.finalKeep){
  if(s.x==p.pm_sd_t&&s.y==1)shHi=true;
  if(s.x==std::nextafter(p.pm_sd_t,0.f)&&s.y==0)shLo=true;
  if(s.x==p.pm_hd_t&&s.y==1)hiLo=true;
  if(s.x==std::nextafter(p.pm_hd_t,1.f)&&s.y==0)hiHi=true;
 }
 require(shLo&&shHi&&hiLo&&hiHi,"step boundaries");
 // Display model must leave all core parameters and pixel results byte-exact.
 p=pm::defaultParameters();p.pm_compression=70;p.pm_density=42;p.pm_hue_compression=30;
 p.pm_sd_t=.22f;p.pm_hd_t=.82f;p.pm_hue_bias=30;p.pm_luma_split=-80;p.pm_luma_pivot_ev=1.5f;p.pm_luma_width=.5f;
 const auto original=p;std::mt19937 rng(911);std::uniform_real_distribution<float>d(-.1f,1.4f);
 for(int i=0;i<1000;++i){
  float in[4]={d(rng),d(rng),d(rng),d(rng)},off[4],on[4];
  pm::pixel(p,in,off,i%2);auto hud=pmhud::makeModel(p);pm::pixel(p,in,on,i%2);
  require(std::memcmp(&p,&original,sizeof p)==0,"model mutates parameters");
  require(std::memcmp(off,on,sizeof off)==0,"model mutates pixel result");++tests;
 }
 const auto start=std::chrono::steady_clock::now();double checksum=0;
 for(int i=0;i<1000;++i){p.pm_hue_angle=i%360;auto m=pmhud::makeModel(p);checksum+=m.finalKeep[64].y+m.swatches[0].r;}
 const double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-start).count()/1000;
 if(argc>1){std::ofstream out(argv[1]);require(bool(out),"cannot open HUD receipt");out<<"{\"status\":\"PASS\",\"assertion_cases\":"<<tests
 <<",\"pixel_model_before_after_cases\":1000,\"mean_model_ms\":"<<ms
 <<",\"model_checksum\":"<<checksum<<",\"host_checkbox_export_test\":false,\"host_viewer_test\":false}\n";}
 std::cout<<"HUD model PASS cases="<<tests<<" mean rebuild ms="<<ms<<"\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<"HUD FAIL: "<<e.what()<<"\n";return 1;}
}
