#include "../src/HudPlacement.hpp"
#include <limits>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <array>
void check(bool q,const char*m){if(!q)throw std::runtime_error(m);}
struct R{double l,b,r,t;};
int main(int argc,char**argv){using namespace pmhud;try{int count=0;auto full=placeHud(1280,720,{0,0,1280,720});check(full.visible&&std::abs(full.scale-1.5)<1e-6,"full1.5");
auto small=placeHud(400,308,{0,0,400,308});check(small.visible&&small.scale==1,"small fit limit");check(!placeHud(399,720,{0,0,399,720}).visible,"minw");check(!placeHud(1280,307,{0,0,1280,307}).visible,"minh");
for(int w=400;w<=2000;w+=37)for(int h=308;h<=1200;h+=31)for(int mode=0;mode<4;mode++){
 PlacementRect image=mode==0?PlacementRect{0,0,(double)w,(double)h}:mode==1?PlacementRect{w*.45,h*.45,w*.55,h*.55}:mode==2?PlacementRect{-50,-50,w+50.,h+50.}:PlacementRect{2000,2000,2100,2100};auto p=placeHud(w,h,image);check(p.visible,"visible");double s=p.scale,l=p.bounds.x1/s,b=p.bounds.y1/s,r=p.bounds.x2/s,t=p.bounds.y2/s;
 std::array<R,4> boxes={R{l+10,t-184,l+186,t-10},R{r-186,t-100,r-10,t-10},R{l+10,b+10,l+186,b+114},R{r-186,b+10,r-10,b+100}};
 for(auto q:boxes)check(q.l>=l&&q.r<=r&&q.b>=b&&q.t<=t,"contained");for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)check(!(boxes[i].l<boxes[j].r&&boxes[j].l<boxes[i].r&&boxes[i].b<boxes[j].t&&boxes[j].b<boxes[i].t),"no overlap");count++;}
double n=std::numeric_limits<double>::quiet_NaN();check(placeHud(1280,720,{n,n,n,n}).visible,"invalid image fallback");if(argc>1){std::ofstream out(argv[1]);out<<"{\"status\":\"PASS\",\"geometry_cases\":"<<count<<",\"all_panels_desired_scale\":1.5,\"minimum_fit_scale\":1.0,\"Host_verified\":false}\n";}
std::cout<<"PASS geometry cases="<<count<<" all4panels containment/no overlap;1280scale1.5;400x308fit1.0\n";return 0;}catch(std::exception&e){std::cerr<<e.what();return 1;}}
