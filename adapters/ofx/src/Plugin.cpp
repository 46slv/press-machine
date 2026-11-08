#include <memory>
#include <algorithm>
#include <string>
#include "ofxsImageEffect.h"
#include "ofxsProcessing.h"
#include "../generated/PixelCore.hpp"
#include "../generated/ParameterValues.hpp"
#include "../generated/Descriptors.hpp"
#include "Trace.hpp"
void runCuda(void*,const void*,void*,long long,long long,int,int,int,int,int,int,int,int,int,int,int,const pm::Parameters&);
class Processor:public OFX::ImageProcessor{
 OFX::Image* src=nullptr;
 pm::Parameters p{};
 int premult=0;
public:
 Processor(OFX::ImageEffect&e):OFX::ImageProcessor(e){}
 void setup(OFX::Image*s,const pm::Parameters&params,int mult){src=s;p=params;premult=mult;}
 void processImagesCUDA() override{
  const auto s=src->getBounds(),d=_dstImg->getBounds(),r=_renderWindow;
  runCuda(_pCudaStream,src->getPixelData(),_dstImg->getPixelData(),src->getRowBytes(),_dstImg->getRowBytes(),
   s.x1,s.y1,s.x2,s.y2,d.x1,d.y1,r.x1,r.y1,r.x2,r.y2,premult,p);
  traceBackend(_effect,true,_pCudaStream,src->getRowBytes(),_dstImg->getRowBytes());
 }
 void multiThreadProcessImages(OfxRectI r) override{
  traceBackend(_effect,false,nullptr,src->getRowBytes(),_dstImg->getRowBytes());
  for(int y=r.y1;y<r.y2;++y){
   if(_effect.abort())return;
   for(int x=r.x1;x<r.x2;++x){
    auto* out=(float*)_dstImg->getPixelAddress(x,y);
    if(!out)continue;
    const auto* in=(const float*)src->getPixelAddress(x,y);
    if(in)pm::pixel(p,in,out,premult);
    else for(int c=0;c<4;++c)out[c]=0.0f;
   }
  }
 }
};
class PressMachine:public OFX::ImageEffect{
 OFX::Clip *source,*output;
 Parameters handles;
 pm::Parameters values(double time){
  double v[25];handles.read(time,v);return fromValues(v);
 }
public:
 PressMachine(OfxImageEffectHandle h):OFX::ImageEffect(h),handles(*this){
  source=fetchClip(kOfxImageEffectSimpleSourceClipName);output=fetchClip(kOfxImageEffectOutputClipName);
 }
 bool isIdentity(const OFX::IsIdentityArguments&a,OFX::Clip*&clip,double&time) override{
  if(pm::identity(values(a.time))){clip=source;time=a.time;return true;}return false;
 }
 void render(const OFX::RenderArguments&a) override{
  std::unique_ptr<OFX::Image> dst(output->fetchImage(a.time)),src(source->fetchImage(a.time));
  if(!dst||!src)OFX::throwSuiteStatusException(kOfxStatFailed);
  if(src->getPixelDepth()!=OFX::eBitDepthFloat||dst->getPixelDepth()!=OFX::eBitDepthFloat||
   src->getPixelComponents()!=OFX::ePixelComponentRGBA||dst->getPixelComponents()!=OFX::ePixelComponentRGBA)
    OFX::throwSuiteStatusException(kOfxStatErrUnsupported);
  const auto d=dst->getBounds();
  OfxRectI r{std::max(a.renderWindow.x1,d.x1),std::max(a.renderWindow.y1,d.y1),
             std::min(a.renderWindow.x2,d.x2),std::min(a.renderWindow.y2,d.y2)};
  if(r.x2<=r.x1||r.y2<=r.y1)return;
  Processor processor(*this);processor.setDstImg(dst.get());
  processor.setup(src.get(),values(a.time),src->getPreMultiplication()==OFX::eImagePreMultiplied);
  processor.setGPURenderArgs(a);processor.setRenderWindow(r);processor.process();
 }
};
mDeclarePluginFactory(PressMachineFactory,{}, {});
void PressMachineFactory::describe(OFX::ImageEffectDescriptor&d){
 d.setLabels("Press Machine v2.0","Press Machine v2.0","Press Machine v2.0");
 d.setPluginGrouping("Press Machine");
 d.setPluginDescription("Press Machine v2.0. Skin-reference angle zero. Legacy red-zero angles require conversion; no automatic state migration. Input color settings must match the node's actual input.");
 d.addSupportedContext(OFX::eContextFilter);d.addSupportedContext(OFX::eContextGeneral);
 d.addSupportedBitDepth(OFX::eBitDepthFloat);d.setSingleInstance(false);d.setHostFrameThreading(false);
 d.setRenderThreadSafety(OFX::eRenderFullySafe);d.setSupportsTiles(true);d.setSupportsMultiResolution(true);
 d.setTemporalClipAccess(false);d.setSupportsMultipleClipPARs(false);d.setRenderTwiceAlways(false);
 d.setSupportsCudaRender(true);d.setSupportsCudaStream(true);d.setSupportsOpenCLRender(false);
 d.setNoSpatialAwareness(true);
}
void PressMachineFactory::describeInContext(OFX::ImageEffectDescriptor&d,OFX::ContextEnum){
 auto* s=d.defineClip(kOfxImageEffectSimpleSourceClipName);s->addSupportedComponent(OFX::ePixelComponentRGBA);
 s->setTemporalClipAccess(false);s->setSupportsTiles(true);s->setIsMask(false);
 auto* o=d.defineClip(kOfxImageEffectOutputClipName);o->addSupportedComponent(OFX::ePixelComponentRGBA);o->setSupportsTiles(true);
 defineParameters(d);
}
OFX::ImageEffect* PressMachineFactory::createInstance(OfxImageEffectHandle h,OFX::ContextEnum){return new PressMachine(h);}
void OFX::Plugin::getPluginIDs(OFX::PluginFactoryArray&a){static PressMachineFactory factory("com.46slv.PressMachine.v2.skinaxis",2,0);a.push_back(&factory);}
