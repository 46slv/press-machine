#pragma once
#include <algorithm>
#include <cmath>
namespace pmhud {
struct PlacementRect{double x1,y1,x2,y2;};
struct Placement{PlacementRect bounds;float scale;bool visible;};
inline Placement placeHud(int w,int h,PlacementRect image){
 PlacementRect viewport{0,0,(double)w,(double)h};
 if(w<400||h<308)return {viewport,0,false};
 PlacementRect clipped{std::max(0.,image.x1),std::max(0.,image.y1),std::min((double)w,image.x2),std::min((double)h,image.y2)};
 auto fits=[](PlacementRect b){return std::isfinite(b.x1)&&std::isfinite(b.y1)&&std::isfinite(b.x2)&&std::isfinite(b.y2)&&b.x2-b.x1>=510&&b.y2-b.y1>=393;};
 // The HUD is viewer UI, not rendered pixels. Zooming the image out must not
 // silently remove it; use the viewport when the visible image cannot fit it.
 PlacementRect b=fits(clipped)?clipped:viewport;
 double width=b.x2-b.x1,height=b.y2-b.y1;
 // Owner-selected 1.5x for ALL four panels/text, not viewer image zoom.
 // 400x308 logical envelope includes tall Hue174 + Density104 and margins.
 // Keep the desired 1.5x where it fits; bound it only to avoid clipping/overlap.
 float scale=(float)std::min(1.5*std::clamp(width/1280.,.85,1.25),std::min(width/400.,height/308.));
 return {b,scale,scale>=.7f};
}
}
