#pragma once
#include <cstdio>
#include "ofxsImageEffect.h"
#include "TraceGate.hpp"
#include "TraceHost.hpp"
#include "TraceFile.hpp"
// This matches the installed, source-linked Resolve OFX Support Library.
// It is not an extra suite fetch or a dependency on the optional V2 suite.
namespace OFX {namespace Private {extern OfxMessageSuiteV1* gMessageSuite;}}
inline void traceBackend(OFX::ImageEffect& effect,bool cuda,void* stream,int sourcePitch,int targetPitch) noexcept {
 static pmtrace::Gate cpuGate,cudaGate;
 auto& gate=cuda?cudaGate:cpuGate;
 gate.emit([&](){
  SYSTEMTIME t;GetSystemTime(&t);char line[384];
  const int count=std::snprintf(line,sizeof(line),
   "PressMachineBackendTrace revision=2 variant=SkinAxisHUDDensity plugin=com.46slv.PressMachine.v2.skinaxis.hud.density %04u-%02u-%02uT%02u:%02u:%02uZ pid=%lu backend=%s stream=%s event=%s srcRowBytes=%d dstRowBytes=%d\r\n",
   (unsigned)t.wYear,(unsigned)t.wMonth,(unsigned)t.wDay,(unsigned)t.wHour,(unsigned)t.wMinute,(unsigned)t.wSecond,
   GetCurrentProcessId(),cuda?"CUDA":"CPU",stream?"Host":"default/none",cuda?"enqueue-success":"cpu-dispatch",sourcePitch,targetPitch);
  if(count<=0||count>=(int)sizeof(line))return false;
  pmtrace::FileResult file;
  try{file=pmtrace::localFile(line,(DWORD)count);}
  catch(...){file.stage=pmtrace::FileStage::exception;file.error=ERROR_UNHANDLED_EXCEPTION;}
  char hostLine[640];
  const int hostCount=std::snprintf(hostLine,sizeof(hostLine),
   "%.*s file_stage=%s file_error=%lu folder_hr=0x%08lx path_kind=%s",
   count>1?count-2:count,line,pmtrace::stageName(file.stage),file.error,(unsigned long)file.folderHR,
   file.pathKind==1?"KnownFolder":file.pathKind==2?"environment":"unavailable");
  const bool host=hostCount>0&&hostCount<(int)sizeof(hostLine)&&
   pmtrace::hostLog(OFX::Private::gMessageSuite,effect.getHandle(),hostLine);
  return file.ok||host;
 });
}
// A CUDA trace proves successful enqueue, not completed pixels.
// Each backend has at most three attempts, then no formatting/path/I/O.
// Logging failures and exceptions never change rendering outcomes.
