#pragma once
#include <windows.h>
#include <GL/gl.h>
#include <cstdio>
#include <limits>
#include "ofxsInteract.h"
#include "../generated/Descriptors.hpp"
#include "../generated/ParameterValues.hpp"
#include "HudModel.hpp"
#include "HudPlacement.hpp"

namespace pmhud {
// A tiny original 5x7 bitmap alphabet. No OS fonts, textures or persistent GL objects.
inline const unsigned char* glyph(char c){
 static const unsigned char data[][7]={
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
 {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
 {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},
 {14,17,17,15,1,1,14},
 {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{15,16,16,16,16,16,15},
 {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
 {15,16,16,19,17,17,15},{17,17,17,31,17,17,17},{14,4,4,4,4,4,14},
 {7,2,2,2,18,18,12},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
 {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
 {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
 {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
 {17,17,17,17,17,10,4},{17,17,17,21,21,27,17},{17,17,10,4,10,17,17},
 {17,17,10,4,4,4,4},{31,1,2,4,8,16,31},
 {0,0,0,31,0,0,0},{0,0,0,0,0,12,12},{0,0,4,0,4,0,0},
 {0,1,2,4,8,16,0},{17,2,4,8,17,0,0},{0,4,4,31,4,4,0},{0,0,0,0,0,0,0},
 {4,4,10,10,17,17,31},{4,4,31,4,4,0,31},{0,0,31,0,31,0,0}};
 if(c>='0'&&c<='9')return data[c-'0'];
 if(c>='A'&&c<='Z')return data[10+c-'A'];
 switch(c){case '-':return data[36];case '.':return data[37];case ':':return data[38];
 case '/':return data[39];case '%':return data[40];case '+':return data[41];case '~':return data[43];case '@':return data[44];case '=':return data[45];default:return data[42];}
}
inline void quad(float x,float y,float w,float h){
 glVertex2f(x,y);glVertex2f(x+w,y);glVertex2f(x+w,y+h);glVertex2f(x,y+h);
}
inline void text(float x,float y,const char*s,float size=1.0f){
 glBegin(GL_QUADS);
 for(;*s;++s,x+=6*size){
  const auto*g=glyph(*s);
  for(int row=0;row<7;++row)for(int col=0;col<5;++col)
   if(g[row]&(1<<(4-col)))quad(x+col*size,y+(6-row)*size,size,size);
 }
 glEnd();
}
inline void label(float x,float y,const char*s){glColor4f(.82f,.87f,.87f,.94f);text(x,y,s);}
inline void formatted(float x,float y,const char*format,double a,double b=0,double c=0){
 char s[96];std::snprintf(s,sizeof s,format,a,b,c);label(x,y,s);
}
struct Rect{double x1,y1,x2,y2;};
inline bool project(double x,double y,const GLdouble*m,const GLdouble*p,int w,int h,double&sx,double&sy){
 double v[4]={x,y,0,1},mv[4]={},clip[4]={};
 for(int i=0;i<4;++i)for(int j=0;j<4;++j)mv[i]+=m[j*4+i]*v[j];
 for(int i=0;i<4;++i)for(int j=0;j<4;++j)clip[i]+=p[j*4+i]*mv[j];
 if(!std::isfinite(clip[3])||std::abs(clip[3])<1e-12)return false;
 sx=(clip[0]/clip[3]+1)*w/2;sy=(clip[1]/clip[3]+1)*h/2;
 return std::isfinite(sx)&&std::isfinite(sy);
}
struct GLState{
 GLint mode;
 GLState(int width,int height){
  glGetIntegerv(GL_MATRIX_MODE,&mode);glPushAttrib(GL_ALL_ATTRIB_BITS);
  glMatrixMode(GL_PROJECTION);glPushMatrix();glLoadIdentity();glOrtho(0,width,0,height,-1,1);
  glMatrixMode(GL_MODELVIEW);glPushMatrix();glLoadIdentity();
  glDisable(GL_DEPTH_TEST);glDisable(GL_LIGHTING);glDisable(GL_CULL_FACE);glDisable(GL_TEXTURE_1D);
  glDisable(GL_TEXTURE_2D);glDisable(GL_ALPHA_TEST);glDisable(GL_STENCIL_TEST);
  glDisable(GL_FOG);glDisable(GL_LINE_STIPPLE);glDisable(GL_POLYGON_STIPPLE);
  glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
  glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
  glLineWidth(1.0f);
 }
 ~GLState(){
  glMatrixMode(GL_MODELVIEW);glPopMatrix();glMatrixMode(GL_PROJECTION);glPopMatrix();
  glPopAttrib();glMatrixMode(mode);
 }
};
inline void panel(float x,float y,const char*title,float height=90){
 glColor4f(.025f,.035f,.04f,.70f);glBegin(GL_QUADS);quad(x,y,176,height);glEnd();
 glColor4f(.23f,.65f,.61f,.58f);glBegin(GL_LINE_LOOP);
 glVertex2f(x,y);glVertex2f(x+176,y);glVertex2f(x+176,y+height);glVertex2f(x,y+height);glEnd();
 label(x+8,y+height-14,title);
}
inline void curve(float x,float y,const std::vector<Sample>&samples,bool diagonal){
 glColor4f(.42f,.49f,.49f,.42f);glBegin(GL_LINES);
 for(int i=0;i<=4;++i){float q=i/4.0f;glVertex2f(x+q*148,y);glVertex2f(x+q*148,y+28);
 glVertex2f(x,y+q*28);glVertex2f(x+148,y+q*28);}glEnd();
 if(diagonal){glColor4f(.7f,.7f,.7f,.35f);glBegin(GL_LINES);glVertex2f(x,y);glVertex2f(x+148,y+28);glEnd();}
 glColor4f(.40f,.94f,.79f,1);glBegin(GL_LINE_STRIP);
 for(auto s:samples)glVertex2f(x+148*std::clamp(s.x,0.0f,1.0f),y+28*std::clamp(s.y,0.0f,1.0f));glEnd();
}
inline void densityLine(float x,float y,float w,float h,const std::vector<DensitySample>&samples,
 bool saturation,float range){
 bool open=false;
 for(auto sample:samples){
  const bool valid=saturation?sample.validSat:sample.validEV;
  if(!valid){if(open){glEnd();open=false;}continue;}
  const float value=saturation?sample.deltaSatPercent:sample.deltaEV;
  // Model range includes all finite samples; never silently clip a measurement.
  if(!std::isfinite(value)||std::abs(value)>range*1.00001f){if(open){glEnd();open=false;}continue;}
  if(!open){glBegin(GL_LINE_STRIP);open=true;}
  glVertex2f(x+w*(sample.inputEV+6)/12,y+h*(.5f+.5f*value/range));
 }
 if(open)glEnd();
}
inline void densityPlot(float x,float y,const DensityGraph&g,bool saturation){
 const float w=132,h=18,range=saturation?g.satRange:g.evRange;
 glColor4f(.42f,.49f,.49f,.42f);glBegin(GL_LINES);
 for(int i=0;i<=2;++i){glVertex2f(x+w*i/2,y);glVertex2f(x+w*i/2,y+h);}
 glVertex2f(x,y+h/2);glVertex2f(x+w,y+h/2);glEnd();
 const float colors[3][3]={{1,.70f,.43f},{1,.30f,.30f},{.32f,.68f,1}};
 for(int i=0;i<3;++i){glColor4f(colors[i][0],colors[i][1],colors[i][2],1);
  densityLine(x,y,w,h,g.curves[i],saturation,range);}
}
inline void densityPanel(float x,float y,const Model&m){
 const auto&p=m.parameters;const auto&g=m.density;
 panel(x,y,p.pm_db?"DENSITY OFF":"DENSITY",104);
 label(x+78,y+90,"REF");
 glColor4f(1,.70f,.43f,1);text(x+108,y+90,"SK");
 glColor4f(1,.30f,.30f,1);text(x+132,y+90,"R");
 glColor4f(.32f,.68f,1,1);text(x+150,y+90,"B");
 formatted(x+8,y+78,"D%.0f C%.0f R%.1f",p.pm_density,p.pm_chroma,p.pm_response);
 label(x+8,y+66,"HUE-LOOK S=C/L 0=.18Y");
 densityPlot(x+36,y+41,g,false);densityPlot(x+36,y+18,g,true);
 label(x+5,y+52,"~EV");label(x+2,y+42,densityRangeLabel(g.evRange).c_str());
 label(x+5,y+29,"~S%");label(x+2,y+19,densityRangeLabel(g.satRange).c_str());
 if(g.validSatCount==0)label(x+66,y+23,"SAT N/A");
 label(x+6,y+6,"EV");label(x+30,y+6,"-6");label(x+99,y+6,"0");label(x+162,y+6,"+6");
}
inline void drawPanels(const Model&m,float l,float b,float r,float t,float scale){
 const auto&p=m.parameters;
 glPushMatrix();glScalef(scale,scale,1);
 l/=scale;b/=scale;r/=scale;t/=scale;
 const float x0=l+10,x1=r-186,y0=b+10,y1=t-100,hy=t-184;
 panel(x0,hy,"HUE",174);
 label(x0+36,hy+160,patternName(p.pm_hue_pattern));
 formatted(x0+8,hy+144,"ANGLE %.1f",p.pm_hue_angle);
 formatted(x0+8,hy+132,"STRENGTH %.1f%%",p.pm_hue_compression);
 formatted(x0+8,hy+120,"BIAS %.0f SPLIT %.0f",p.pm_hue_bias,p.pm_luma_split);
 const float w=m.anchors?(156.0f-(m.anchors-1)*3)/m.anchors:0;
 for(int i=0;i<m.anchors;++i){auto c=m.swatches[i];glColor4f(c.r,c.g,c.b,.98f);
  glBegin(GL_QUADS);quad(x0+9+i*(w+3),hy+98,w,14);glEnd();}
 label(x0+8,hy+86,"0: SKIN / DIRECTION KEY");
 formatted(x0+8,hy+74,"PIV %.2f W %.2f",p.pm_luma_pivot_ev,p.pm_luma_width);
 glColor4f(.40f,.94f,.79f,1);text(x0+8,hy+62,"Q");
 glColor4f(1,.70f,.43f,1);text(x0+26,hy+62,"DRIVE");label(x0+68,hy+62,"-1 TO +1");
 glColor4f(.42f,.49f,.49f,.42f);glBegin(GL_LINES);
 glVertex2f(x0+14,hy+44);glVertex2f(x0+162,hy+44);
 glVertex2f(x0+88,hy+30);glVertex2f(x0+88,hy+58);glEnd();
 for(int i=0;i<2;++i){
  if(i==0)glColor4f(.40f,.94f,.79f,1);else glColor4f(1,.70f,.43f,1);
  glBegin(GL_LINE_STRIP);
  for(auto v:i==0?m.lumaResponse:m.signedDrive)glVertex2f(x0+14+148*v.x,hy+44+14*v.y);
  glEnd();
 }
 label(x0+8,hy+18,"INPUT EV -6 TO +6");
 label(x0+8,hy+6,"DRIVE NOT OUTPUT HUE");
 panel(x1,y1,"COMPRESSION");
 formatted(x1+8,y1+62,"T %.0f  A %.0f  K %.0f",p.pm_threshold,p.pm_compression,p.pm_softness);
 curve(x1+14,y1+18,m.compression,true);
 label(x1+8,y1+6,"S IN 0-100 / S OUT");
 formatted(x1+8,y1+49,"BASE / SKIN %.0f%%",p.pm_sat_skin);
 densityPanel(x0,y0,m);
 panel(x1,y0,"FINAL SAT KEEP");
 formatted(x1+8,y0+62,"SH %.2f  K %.2f",p.pm_sd_t,p.pm_sd_k);
 curve(x1+14,y0+18,m.finalKeep,false);
 formatted(x1+8,y0+49,"HI %.2f  K %.2f",p.pm_hd_t,p.pm_hd_k);
 label(x1+8,y0+6,"DI-Y 0-1 / KEEP 0-100%");
 glPopMatrix();
}
class Overlay:public OFX::OverlayInteract{
 OFX::ImageEffect*effect;
 Parameters handles;
 OFX::BooleanParam*graph;
 OFX::Clip*source;
 ModelCache cache;
public:
 Overlay(OfxInteractHandle h,OFX::ImageEffect*e):OFX::OverlayInteract(h),effect(e),handles(*e){
  graph=e->fetchBooleanParam("pm_graph");source=e->fetchClip(kOfxImageEffectSimpleSourceClipName);
  addParamToSlaveTo(graph);
  handles.forEach([this](auto*param){addParamToSlaveTo(param);});
 }
 bool draw(const OFX::DrawArgs&a) override{
  if(!graph->getValueAtTime(a.time))return false;
  // This interact is registered only as V1 (OpenGL), never as V2 DrawSuite.
  GLint vp[4];GLdouble mv[16],proj[16];glGetIntegerv(GL_VIEWPORT,vp);
  if(vp[2]<400||vp[3]<308)return false;
  glGetDoublev(GL_MODELVIEW_MATRIX,mv);glGetDoublev(GL_PROJECTION_MATRIX,proj);
  Rect visible{0,0,(double)vp[2],(double)vp[3]};
  OfxRectD rod;
  try{rod=source->getRegionOfDefinition(a.time);}
  catch(...){auto p=effect->getProjectOffset(),s=effect->getProjectSize();rod={p.x,p.y,p.x+s.x,p.y+s.y};}
  Rect image{std::numeric_limits<double>::infinity(),std::numeric_limits<double>::infinity(),
   -std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};
  for(int i=0;i<4;++i){
   double x,y;
   if(!project(i&1?rod.x2:rod.x1,i&2?rod.y2:rod.y1,mv,proj,vp[2],vp[3],x,y))return false;
   image.x1=std::min(image.x1,x);image.y1=std::min(image.y1,y);
   image.x2=std::max(image.x2,x);image.y2=std::max(image.y2,y);
  }
  const auto placement=placeHud(vp[2],vp[3],{image.x1,image.y1,image.x2,image.y2});
  if(!placement.visible)return false;
  visible={placement.bounds.x1,placement.bounds.y1,placement.bounds.x2,placement.bounds.y2};
  const float scale=placement.scale;
  std::array<double,kParameterCount> values{};handles.read(a.time,values.data());
  if(cache.update(values)==CacheUpdate::Invalid)return false;
  GLState state(vp[2],vp[3]);drawPanels(cache.get(),(float)visible.x1,(float)visible.y1,(float)visible.x2,(float)visible.y2,scale);
  return true;
 }
 // Pen/key actions deliberately retain the SDK's unconsumed defaults.
};
class Descriptor:public OFX::DefaultEffectOverlayDescriptor<Descriptor,Overlay>{};
inline void describe(OFX::ImageEffectDescriptor&d){
 // Resolve's bundled Support setter currently registers V2. Keep its SDK
 // untouched and explicitly register the stable compatibility/OpenGL V1 API.
 static Descriptor descriptor;
 if(OFX::getImageEffectHostDescription()->supportsOverlays)
  d.getPropertySet().propSetPointer(kOfxImageEffectPluginPropOverlayInteractV1,(void*)descriptor.getMainEntry());
}
}
