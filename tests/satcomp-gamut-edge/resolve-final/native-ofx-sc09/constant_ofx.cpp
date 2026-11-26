// SatComp separate-ID OpenFX diagnostic. Deliberately CUDA-only and opaque.
#include <windows.h>
#include <cstdint>
#include <cstring>
#include <initializer_list>
#include "ofxImageEffect.h"
#include "ofxGPURender.h"
#include "constant_ptx.hpp"

namespace {
constexpr char kIdentity[]="org.satcomp.diagnostic.opaquefloat8125.r1";
constexpr char kLabel[]="SatComp SC09 Opaque CUDA 8125";
OfxHost* host=nullptr;
const OfxPropertySuiteV1* props=nullptr;
const OfxImageEffectSuiteV1* images=nullptr;
using Handle=void*;

struct Driver {
  HMODULE dll=LoadLibraryExW(L"nvcuda.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);
  int (WINAPI *ctx)(Handle*)=get<decltype(ctx)>("cuCtxGetCurrent");
  int (WINAPI *load)(Handle*,const void*)=get<decltype(load)>("cuModuleLoadData");
  int (WINAPI *find)(Handle*,Handle,const char*)=get<decltype(find)>("cuModuleGetFunction");
  int (WINAPI *launch)(Handle,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,Handle,void**,void**)=get<decltype(launch)>("cuLaunchKernel");
  int (WINAPI *sync)(Handle)=get<decltype(sync)>("cuStreamSynchronize");
  int (WINAPI *unload)(Handle)=get<decltype(unload)>("cuModuleUnload");
  template<class T> T get(const char* name) {return dll?reinterpret_cast<T>(GetProcAddress(dll,name)):nullptr;}
  bool ok() const {return ctx&&load&&find&&launch&&sync&&unload;}
};
int fill(void* out, long long pitch, int x, int y, int w, int h, Handle stream) {
  // Bounded renderer: rejects unexpected, negative, or overflowing extents.
  if (!out || pitch<=0 || x<0 || y<0 || w<=0 || h<=0 || x>16384 || y>16384 || w>16384 || h>16384 || pitch%4 || pitch<16LL*(x+w)) return 1;
  static Driver d;
  Handle context=nullptr,m=nullptr,f=nullptr;
  if (!d.ok() || d.ctx(&context) || !context || d.load(&m,kPtx)) return 2;
  int error=d.find(&f,m,"sat19_opaque_8125");
  if (!error) {
    void* args[]={&out,&pitch,&x,&y,&w,&h};
    error=d.launch(f,(w+15)/16,(h+7)/8,1,16,8,1,0,stream,args,nullptr);
    if (!error) error=d.sync(stream);
  }
  const int unload=d.unload(m);
  return error?error:unload;
}

OfxStatus describe(OfxImageEffectHandle effect) {
  OfxPropertySetHandle p=nullptr;
  if (images->getPropertySet(effect,&p)) return kOfxStatFailed;
  if (props->propSetString(p,kOfxPropLabel,0,kLabel) ||
      props->propSetString(p,kOfxImageEffectPluginPropGrouping,0,"SatComp Diagnostics") ||
      props->propSetString(p,kOfxImageEffectPropSupportedContexts,0,kOfxImageEffectContextFilter) ||
      props->propSetString(p,kOfxImageEffectPropSupportedPixelDepths,0,kOfxBitDepthFloat) ||
      props->propSetString(p,kOfxImageEffectPropCudaRenderSupported,0,"true")) return kOfxStatFailed;
  props->propSetInt(p,kOfxImageEffectPropSupportsTiles,0,0);
  props->propSetInt(p,kOfxImageEffectPropTemporalClipAccess,0,0);
  props->propSetString(p,kOfxImageEffectPluginRenderThreadSafety,0,kOfxImageEffectRenderInstanceSafe);
  // OFX GPU extension: when streams are not negotiated, complete the CUDA
  // work before returning. Don't misinterpret missing GetPointer as a stream.
  if (props->propSetString(p,kOfxImageEffectPropCudaStreamSupported,0,"false")) return kOfxStatFailed;
  return kOfxStatOK;
}
OfxStatus context(OfxImageEffectHandle effect) {
  for (const char* name : {kOfxImageEffectSimpleSourceClipName,kOfxImageEffectOutputClipName}) {
    OfxPropertySetHandle p=nullptr;
    if (images->clipDefine(effect,name,&p) || props->propSetString(p,kOfxImageEffectPropSupportedComponents,0,kOfxImageComponentRGBA)) return kOfxStatFailed;
    props->propSetInt(p,kOfxImageClipPropOptional,0,0);
    props->propSetInt(p,kOfxImageEffectPropSupportsTiles,0,0);
  }
  return kOfxStatOK;
}
struct Image { OfxPropertySetHandle h=nullptr; ~Image(){if(h) images->clipReleaseImage(h);} };
OfxStatus render(OfxImageEffectHandle effect, OfxPropertySetHandle in) {
  int cuda=0,r[4]={},b[4]={},pitch=0; double time=0;
  if (!in || props->propGetInt(in,kOfxImageEffectPropCudaEnabled,0,&cuda) || cuda!=1) return kOfxStatErrUnsupported;
  if (props->propGetDouble(in,kOfxPropTime,0,&time) || props->propGetIntN(in,kOfxImageEffectPropRenderWindow,4,r)) return kOfxStatFailed;
  OfxImageClipHandle output=nullptr; Image im;
  if (images->clipGetHandle(effect,kOfxImageEffectOutputClipName,&output,nullptr) || images->clipGetImage(output,time,nullptr,&im.h) || !im.h) return kOfxStatFailed;
  void* dst=nullptr; char *depth=nullptr,*components=nullptr;
  if (props->propGetString(im.h,kOfxImageEffectPropPixelDepth,0,&depth) || !depth || std::strcmp(depth,kOfxBitDepthFloat) ||
      props->propGetString(im.h,kOfxImageEffectPropComponents,0,&components) || !components || std::strcmp(components,kOfxImageComponentRGBA) ||
      props->propGetInt(im.h,kOfxImagePropRowBytes,0,&pitch) || props->propGetIntN(im.h,kOfxImagePropBounds,4,b) || props->propGetPointer(im.h,kOfxImagePropData,0,&dst)) return kOfxStatFailed;
  if (r[0]<b[0] || r[1]<b[1] || r[2]>b[2] || r[3]>b[3]) return kOfxStatFailed;
  const int64_t x=int64_t(r[0])-b[0],y=int64_t(r[1])-b[1],w=int64_t(r[2])-r[0],h=int64_t(r[3])-r[1];
  if (x>16384 || y>16384 || w>16384 || h>16384 || w<0 || h<0) return kOfxStatFailed;
  if (!w || !h) return kOfxStatOK;
  return fill(dst,pitch,int(x),int(y),int(w),int(h),nullptr)==0?kOfxStatOK:kOfxStatFailed;
}
void setHost(OfxHost* p) {host=p;}
OfxStatus entry(const char* a,const void* h,OfxPropertySetHandle in,OfxPropertySetHandle) {
  if (!a) return kOfxStatErrValue;
  if (!std::strcmp(a,kOfxActionLoad)) {
    if (!host || !host->fetchSuite) return kOfxStatErrMissingHostFeature;
    props=static_cast<const OfxPropertySuiteV1*>(host->fetchSuite(host->host,kOfxPropertySuite,1));
    images=static_cast<const OfxImageEffectSuiteV1*>(host->fetchSuite(host->host,kOfxImageEffectSuite,1));
    return props&&images?kOfxStatOK:kOfxStatErrMissingHostFeature;
  }
  if (!std::strcmp(a,kOfxActionUnload)) {props=nullptr; images=nullptr; return kOfxStatOK;}
  if (!props||!images) return kOfxStatErrMissingHostFeature;
  auto effect=reinterpret_cast<OfxImageEffectHandle>(const_cast<void*>(h));
  if (!std::strcmp(a,kOfxActionDescribe)) return describe(effect);
  if (!std::strcmp(a,kOfxImageEffectActionDescribeInContext)) return context(effect);
  if (!std::strcmp(a,kOfxImageEffectActionRender)) return render(effect,in);
  if (!std::strcmp(a,kOfxActionCreateInstance)||!std::strcmp(a,kOfxActionDestroyInstance)) return kOfxStatOK;
  return kOfxStatReplyDefault;
}
OfxPlugin plugin={kOfxImageEffectPluginApi,1,kIdentity,1,0,setHost,entry};
}
extern "C" __declspec(dllexport) int OfxGetNumberOfPlugins(){return 1;}
extern "C" __declspec(dllexport) OfxPlugin* OfxGetPlugin(int i){return i==0?&plugin:nullptr;}
#ifdef SAT19_STANDALONE_TEST
extern "C" __declspec(dllexport) int Sat19TestGpuFill(void* dst,long long pitch,int x,int y,int w,int h){return fill(dst,pitch,x,y,w,h,nullptr);}
#endif
