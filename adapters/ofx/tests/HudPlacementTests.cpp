#include "../src/HudPlacement.hpp"
#include <cassert>
#include <limits>
#include <fstream>
#include <iostream>
int main(int argc,char**argv){using namespace pmhud;
 auto full=placeHud(1280,720,{0,0,1280,720});assert(full.visible&&full.bounds.x2==1280);
 auto zoom=placeHud(1280,720,{590,310,690,410});assert(zoom.visible&&zoom.bounds.x1==0&&zoom.bounds.x2==1280);
 auto portrait=placeHud(650,560,{200,0,450,560});assert(portrait.visible&&portrait.bounds.x1==0);
 auto crop=placeHud(1280,720,{-100,-100,1800,900});assert(crop.visible&&crop.bounds.x1==0&&crop.bounds.y2==720);
 auto off=placeHud(1280,720,{2000,2000,2100,2100});assert(off.visible&&off.bounds.x1==0);
 assert(!placeHud(399,720,{0,0,399,720}).visible);
 assert(!placeHud(1280,307,{0,0,1280,307}).visible);
 double n=std::numeric_limits<double>::quiet_NaN();auto invalid=placeHud(1280,720,{n,n,n,n});assert(invalid.visible);
 if(argc>1){std::ofstream out(argv[1]);out<<"{\"status\":\"PASS\",\"cases\":8,\"Host_verified\":false}\n";}
 std::cout<<"HUD placement PASS: 8 cases; Host not tested\n";
}
