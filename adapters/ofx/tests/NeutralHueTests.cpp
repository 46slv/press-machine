#include "../src/HudModel.hpp"
#include <iostream>
#include <stdexcept>
void check(bool x,const char*m){if(!x)throw std::runtime_error(m);}
int main(){try{int count=0;auto p=pm::defaultParameters();auto base=pmhud::makeModel(p);
check(base.neutralHue.samples.size()==129,"count");for(auto s:base.neutralHue.samples)check(s.strength==0,"neutral zero");
for(int pattern=0;pattern<6;pattern++)for(float a:{0.f,45.f,180.f,360.f})for(float bias:{-100.f,0.f,100.f})for(float split:{-300.f,0.f,300.f}){
p=pm::defaultParameters();p.pm_hue_pattern=pattern;p.pm_hue_angle=a;p.pm_hue_bias=bias;p.pm_luma_split=split;p.pm_hue_compression=50;auto g=pmhud::makeNeutralHueGraph(p);
check(g.samples.size()==129,"count129");for(auto s:g.samples){check(std::isfinite(s.strength)&&s.strength>=0&&s.strength<=g.range,"unclipped range");for(int i=0;i<3;i++)check(std::isfinite(s.direction[i])&&s.direction[i]>=0&&s.direction[i]<=1.000001&&s.preview[i]>=0&&s.preview[i]<=1.000001,"display colors");++count;}}
p=pm::defaultParameters();p.pm_hue_compression=50;p.pm_hue_bias=50;auto m=pmhud::makeModel(p);check(m.anchors==2,"keep swatches");auto mono=p;mono.pm_hue_pattern=0;auto z=pmhud::sampleNeutralHue(mono,.5f);check(std::abs(z.strength-.532418156012)<1e-6,"independent neutral CSV mono oracle");
p.pm_hue_compression=0;p.pm_hue_bias=0;p.pm_luma_split=100;z=pmhud::sampleNeutralHue(p,.5f);check(z.strength==0,"pivot neutral");auto left=pmhud::sampleNeutralHue(p,0),right=pmhud::sampleNeutralHue(p,1);check(left.direction[2]>left.direction[0]&&right.direction[0]>right.direction[2],"opposite hue directions");
p.pm_hue_pattern=5;p.pm_hue_angle=45;p.pm_hue_compression=50;p.pm_hue_bias=-25;z=pmhud::sampleNeutralHue(p,.5f);check(std::abs(z.strength-1.30337038688)<1e-6,"independent neutral CSV tetrad oracle");check(pmhud::makeNeutralHueGraph(p).displayClipped,"display clipping signaled");
auto unchanged=z;p.pm_density=300;p.pm_compression=80;p.pm_density_skin=100;p.pm_sat_skin=100;auto irrelevant=pmhud::sampleNeutralHue(p,.5f);check(unchanged.strength==irrelevant.strength&&unchanged.preview==irrelevant.preview,"Hue only scope");
std::cout<<"PASS samples="<<count<<" +neutral/oracle/display/unused-stage gates\n";return 0;}catch(std::exception&e){std::cerr<<e.what();return 1;}}
