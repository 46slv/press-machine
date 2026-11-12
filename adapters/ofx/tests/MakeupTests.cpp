#include "../src/HudModel.hpp"
#include <iostream>
#include <limits>
#include <stdexcept>
using namespace pm;
void check(bool q,const char*s){if(!q)throw std::runtime_error(s);}
double value(float2 x){return pmhud::pairDoubleValue(x);}double error(pmvp3 a,pmvp3 b){return std::max(std::abs(value(pmvp_sub(a.x,b.x))),std::max(std::abs(value(pmvp_sub(a.y,b.y))),std::abs(value(pmvp_sub(a.z,b.z)))));}
pmvp3 pre(pmvp3 x,float v){return pmif_neutral(x)?x:pmvq_presat(x,v,pm_pair(1),0,2,.001f,2);}
pmvp3 raw(pmvp3 input,const Parameters&p){auto a=pre(input,p.pm_pre);auto b=pmif_neutral(a)?a:pmc_comp_stage(a,pmi_threshold_ui(p.pm_threshold,p.pm_compression),p.pm_compression,p.pm_softness,pm_pair(1));return pre(b,p.pm_makeup);}
int main(){try{int cases=0;auto p=defaultParameters();check(p.pm_makeup==100,"default100");p.pm_makeup=150;check(!identity(p),"identity must see Makeup");
for(int probe=0;probe<3;probe++)for(float ev:{-6.f,0.f,6.f})for(float makeup:{0.f,50.f,100.f,150.f,200.f})for(float skin:{0.f,50.f,100.f}){
 auto input=pmhud::referenceInput(probe,ev);p=defaultParameters();p.pm_pre=150;p.pm_compression=80;p.pm_threshold=40;p.pm_makeup=makeup;p.pm_sat_skin=skin;
 auto z=pmhud::densityStages(p,input);auto analysis=pmc_prepare_stages(input.x,input.y,input.z,100,skin,0);auto expected=pmcc_mix(input,raw(input,p),analysis.keep_sat);check(error(z.conditioned,expected)<1e-12*std::max(1.,std::abs(value(pmvpy_Y(input)))),"independent raw block then single mask");cases++;
}
p=defaultParameters();p.pm_pre=150;p.pm_compression=80;p.pm_threshold=40;p.pm_makeup=150;p.pm_sat_skin=50;auto x=pmhud::referenceInput(0,0);auto analysis=pmc_prepare_stages(x.x,x.y,x.z,100,50,0);check(value(analysis.keep_sat)<1,"skin fixture eligible");auto z=pmhud::densityStages(p,x);auto pa=pmvq_presat(x,150,analysis.keep_sat,0,2,.001f,2);auto ca=pmc_comp_stage(pa,pmi_threshold_ui(40,80),80,20,analysis.keep_sat);auto wrong=pmvq_presat(ca,150,analysis.keep_sat,0,2,.001f,2);double separation=error(z.conditioned,wrong);check(separation>1e-8,"negative oracle rejects per-stage protection");
p.pm_makeup=100;auto neutral=pmhud::densityStages(p,x).conditioned;for(float m:{-1.f,201.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){p.pm_makeup=m;check(error(neutral,pmhud::densityStages(p,x).conditioned)==0,"invalid Makeup no-op block continues");}
for(float m:{0.f,50.f,100.f,150.f,200.f})for(double a:{0.,.001,.18,1.,16.,-.1}){p=defaultParameters();p.pm_makeup=m;p.pm_pre=150;p.pm_compression=80;auto q=pmhud::pairDouble(a);auto gray=pmvp_make(q,q,q);check(pmvp_same(pmhud::densityStages(p,gray).final,gray),"gray identity with neutral Hue");cases++;}
p=defaultParameters();auto g=pmhud::makeModel(p);p.pm_makeup=150;auto h=pmhud::makeModel(p);check(g.neutralHue.samples[20].strength==h.neutralHue.samples[20].strength,"Hue-only neutral graph excludes Makeup");check(g.density.curves[0][10].deltaEV==0&&h.density.curves[0][10].deltaEV==0,"Density0 graph0 with Makeup active");
std::cout<<"PASS Makeup cases="<<cases<<"; single-vs-perstage protection separation="<<separation<<";identity/invalid/gray/Hue-only/Density0 gates\n";return 0;}catch(std::exception&e){std::cerr<<e.what();return 1;}}
