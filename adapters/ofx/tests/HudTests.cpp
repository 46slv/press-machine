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
 require(base.points==2,"default directions");
 for(auto s:base.compression)require(near(s.x,s.y),"default comp identity");
 for(auto s:base.finalKeep)require(s.y==1,"default final identity");
 int counts[5]={1,2,3,4,6};int tests=0;
 for(int index=0;index<5;++index)for(float angle:{0.f,17.2f,180.f,359.9f,360.f}){
  p.pm_hue_points_index=index;p.pm_hue_angle=angle;auto m=pmhud::makeModel(p);
  require(m.points==counts[index],"points mapping");
  for(int i=0;i<m.points;++i){auto c=m.swatches[i];
   require(std::isfinite(c.r)&&std::isfinite(c.g)&&std::isfinite(c.b),"finite swatch");
   require(near(std::min(c.r,std::min(c.g,c.b)),0),"max sat lower");
   require(near(std::max(c.r,std::max(c.g,c.b)),1),"max sat upper");++tests;}
 }
 p=pm::defaultParameters();
 auto zero=pmhud::makeModel(p);p.pm_hue_angle=360;auto wrap=pmhud::makeModel(p);
 require(std::memcmp(zero.swatches.data(),wrap.swatches.data(),sizeof zero.swatches)==0,"zero/360 exact");
 require(zero.swatches[0].r>zero.swatches[0].g&&zero.swatches[0].g>zero.swatches[0].b,"skin zero orange direction");
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
 p.pm_sd_t=.22f;p.pm_hd_t=.82f;
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
 if(argc>1){std::ofstream out(argv[1]);out<<"{\"status\":\"PASS\",\"assertion_cases\":"<<tests
 <<",\"pixel_model_before_after_cases\":1000,\"mean_model_ms\":"<<ms
 <<",\"model_checksum\":"<<checksum<<",\"host_checkbox_export_test\":false,\"host_viewer_test\":false}\n";}
 std::cout<<"HUD model PASS cases="<<tests<<" mean rebuild ms="<<ms<<"\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<"HUD FAIL: "<<e.what()<<"\n";return 1;}
}
