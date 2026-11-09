#include "../generated/PixelCore.hpp"
#include <cassert>
#include <cmath>
#include <iostream>
int main(){
 using namespace pm;
 auto p=defaultParameters();
 assert(identity(p));
 auto q0=pmvn_q_ref(pm_pair(0.0f));assert(std::fabs(pmvp_round(q0)+1.0f)<1e-6f);
 auto q18=pmvn_q_ref(pm_pair(0.18f));assert(std::fabs(pmvp_round(q18))<2e-6f);
 auto w=pmvn_drive_weight(100.0f,300.0f,pm_pair(1.0f));
 assert(std::fabs(pmvp_round(w)-255.0f/257.0f)<2e-6f);
 assert(std::fabs(pmvp_round(pmvn_pattern_F(pm_pair(0.0f))))<1e-7f);
 assert(std::fabs(pmvp_round(pmvn_pattern_F(pm_pair(1.0f)))-1.0f)<1e-6f);
 float in[4]={0.04f,0.04f,0.04f,1.0f},out[4]{};
 p.pm_luma_split=300.0f;p.pm_hue_angle=35.0f;p.pm_hue_pattern=2;
 pixel(p,in,out,0);
 assert(std::isfinite(out[0])&&std::isfinite(out[1])&&std::isfinite(out[2]));
 assert(out[0]!=in[0]||out[1]!=in[1]||out[2]!=in[2]);
 assert(out[3]==1.0f);
 p=defaultParameters();p.pm_pre=130.0f;p.pm_compression=50.0f;p.pm_hue_compression=70.0f;p.pm_hue_pattern=3;p.pm_hue_bias=25.0f;p.pm_luma_split=120.0f;p.pm_density=80.0f;
 float c[4]={0.7f,0.12f,-0.03f,0.5f};pixel(p,c,out,0);
 assert(std::isfinite(out[0])&&std::isfinite(out[1])&&std::isfinite(out[2])&&out[3]==0.5f);
 p.pm_db=1;pixel(p,c,out,0);assert(std::isfinite(out[0]));
 std::cout<<"vNext core smoke PASS\n";
}
