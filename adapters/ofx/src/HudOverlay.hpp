#pragma once
#include <windows.h>
#include <GL/gl.h>
#include <cstdio>
#include <limits>
#include "ofxsInteract.h"
#include "../generated/Descriptors.hpp"
#include "../generated/ParameterValues.hpp"
#include "HudModel.hpp"

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
 {0,1,2,4,8,16,0},{17,2,4,8,17,0,0},{0,4,4,31,4,4,0},{0,0,0,0,0,0,0}};
 if(c>='0'&&c<='9')return data[c-'0'];
 if(c>='A'&&c<='Z')return data[10+c-'A'];
 switch(c){case '-':return data[36];case '.':return data[37];case ':':return data[38];
 case '/':return data[39];case '%':return data[40];case '+':return data[41];default:return data[42];}
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
inline void panel(float x,float y,const char*title){
 glColor4f(.025f,.035f,.04f,.70f);glBegin(GL_QUADS);quad(x,y,176,90);glEnd();
 glColor4f(.23f,.65f,.61f,.58f);glBegin(GL_LINE_LOOP);
 glVertex2f(x,y);glVertex2f(x+176,y);glVertex2f(x+176,y+90);glVertex2f(x,y+90);glEnd();
 label(x+8,y+76,title);
}
inline void curve(float x,float y,const std::vector<Sample>&samples,bool diagonal){
 glColor4f(.42f,.49f,.49f,.42f);glBegin(GL_LINES);
 for(int i=0;i<=4;++i){float q=i/4.0f;glVertex2f(x+q*148,y);glVertex2f(x+q*148,y+28);
 glVertex2f(x,y+q*28);glVertex2f(x+148,y+q*28);}glEnd();
 if(diagonal){glColor4f(.7f,.7f,.7f,.35f);glBegin(GL_LINES);glVertex2f(x,y);glVertex2f(x+148,y+28);glEnd();}
 glColor4f(.40f,.94f,.79f,1);glBegin(GL_LINE_STRIP);
 for(auto s:samples)glVertex2f(x+148*std::clamp(s.x,0.0f,1.0f),y+28*std::clamp(s.y,0.0f,1.0f));glEnd();
}
inline void drawPanels(const Model&m,float l,float b,float r,float t,float scale){
 const auto&p=m.parameters;
 glPushMatrix();glScalef(scale,scale,1);
 l/=scale;b/=scale;r/=scale;t/=scale;
 const float x0=l+10,x1=r-186,y0=b+10,y1=t-100;
 panel(x0,y1,"HUE");
 formatted(x0+8,y1+62,"ANGLE %.1f   N %.0f",p.pm_hue_angle,m.points);
 formatted(x0+8,y1+50,"COMP %.1f%%",p.pm_hue_compression);
 const float w=m.points?(156.0f-(m.points-1)*3)/m.points:0;
 for(int i=0;i<m.points;++i){auto c=m.swatches[i];glColor4f(c.r,c.g,c.b,.98f);
  glBegin(GL_QUADS);quad(x0+9+i*(w+3),y1+24,w,17);glEnd();}
 label(x0+8,y1+10,"0: SKIN / DIRECTION KEY");
 panel(x1,y1,"COMPRESSION");
 formatted(x1+8,y1+62,"T %.0f  A %.0f  K %.0f",p.pm_threshold,p.pm_compression,p.pm_softness);
 curve(x1+14,y1+18,m.compression,true);
 label(x1+8,y1+6,"S IN 0-100 / S OUT");
 formatted(x1+8,y1+49,"BASE / SKIN %.0f%%",p.pm_sat_skin);
 panel(x0,y0,"DENSITY");
 formatted(x0+8,y0+62,"D %.1f   C %.1f",p.pm_density,p.pm_chroma);
 formatted(x0+8,y0+50,"RESPONSE %.2f",p.pm_response);
 formatted(x0+8,y0+38,"SH %.0f / %.0f",p.pm_shadow,p.pm_sr);
 formatted(x0+8,y0+26,"HI %.0f / %.0f",p.pm_highlight,p.pm_hr);
 formatted(x0+8,y0+14,"SKIN %.0f%%",p.pm_density_skin);
 label(x0+100,y0+14,p.pm_db?"BYPASS":"ACTIVE");
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
 std::array<double,25> previous{};
 bool cached=false;
 Model model;
public:
 Overlay(OfxInteractHandle h,OFX::ImageEffect*e):OFX::OverlayInteract(h),effect(e),handles(*e){
  graph=e->fetchBooleanParam("pm_graph");source=e->fetchClip(kOfxImageEffectSimpleSourceClipName);
  addParamToSlaveTo(graph);
#define PM_HUD_SLAVE(id) addParamToSlaveTo(handles.id);
  PM_HUD_SLAVE(pmi_ig) PM_HUD_SLAVE(pmi_it) PM_HUD_SLAVE(pmi_og) PM_HUD_SLAVE(pmi_ot)
  PM_HUD_SLAVE(pm_pre) PM_HUD_SLAVE(pm_hue_angle) PM_HUD_SLAVE(pm_hue_points_index)
  PM_HUD_SLAVE(pm_hue_compression) PM_HUD_SLAVE(pm_threshold) PM_HUD_SLAVE(pm_compression)
  PM_HUD_SLAVE(pm_softness) PM_HUD_SLAVE(pm_sat_skin) PM_HUD_SLAVE(pm_density)
  PM_HUD_SLAVE(pm_chroma) PM_HUD_SLAVE(pm_response) PM_HUD_SLAVE(pm_shadow)
  PM_HUD_SLAVE(pm_sr) PM_HUD_SLAVE(pm_highlight) PM_HUD_SLAVE(pm_hr)
  PM_HUD_SLAVE(pm_density_skin) PM_HUD_SLAVE(pm_db) PM_HUD_SLAVE(pm_sd_t)
  PM_HUD_SLAVE(pm_sd_k) PM_HUD_SLAVE(pm_hd_t) PM_HUD_SLAVE(pm_hd_k)
#undef PM_HUD_SLAVE
 }
 bool draw(const OFX::DrawArgs&a) override{
  if(!graph->getValueAtTime(a.time))return false;
  // This interact is registered only as V1 (OpenGL), never as V2 DrawSuite.
  GLint vp[4];GLdouble mv[16],proj[16];glGetIntegerv(GL_VIEWPORT,vp);
  if(vp[2]<400||vp[3]<230)return false;
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
  visible={std::max(visible.x1,image.x1),std::max(visible.y1,image.y1),
   std::min(visible.x2,image.x2),std::min(visible.y2,image.y2)};
  const double width=visible.x2-visible.x1,height=visible.y2-visible.y1;
  const float scale=(float)std::min(std::clamp(width/1280.0,.85,1.25),std::min(width/400.0,height/230.0));
  if(width<340||height<200||scale<.7f)return false;
  std::array<double,25> values{};handles.read(a.time,values.data());
  for(double v:values)if(!std::isfinite(v))return false;
  if(!cached||values!=previous){model=makeModel(fromValues(values.data()));previous=values;cached=true;}
  GLState state(vp[2],vp[3]);drawPanels(model,(float)visible.x1,(float)visible.y1,(float)visible.x2,(float)visible.y2,scale);
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
