#pragma once
#include <atomic>
#include "ofxMessage.h"
namespace pmtrace {
inline bool hostLog(OfxMessageSuiteV1* suite,void* handle,const char* text) noexcept {
 if(!suite||!suite->message)return false;
 // Serialize only this plugin's log callbacks without waiting on a renderer.
 static std::atomic_flag busy=ATOMIC_FLAG_INIT;
 if(busy.test_and_set(std::memory_order_acquire))return false;
 struct Release{std::atomic_flag& f;~Release(){f.clear(std::memory_order_release);}} release{busy};
 try {
  // The literal format is required. The installed C++ sendMessage wrapper
  // otherwise forwards the rendered message itself as the printf format.
  return suite->message(handle,kOfxMessageLog,"PressMachineBackendTrace","%s",text)==kOfxStatOK;
 } catch(...){return false;}
}
}
