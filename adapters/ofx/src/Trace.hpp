#pragma once
#include <windows.h>
#include <atomic>
#include <string>
#include <cstdio>
// Development-only: one line per backend/process, outside timed steady-state.
// This proves which render entry was used, not GPU pixel correctness.
inline void traceBackend(bool cuda,void* stream,int sourcePitch,int targetPitch){
 static std::atomic<bool> cpuSeen{false},cudaSeen{false};
 if((cuda?cudaSeen:cpuSeen).exchange(true))return;
 wchar_t base[32768];DWORD n=GetEnvironmentVariableW(L"LOCALAPPDATA",base,32000);
 if(!n||n>=32000)return;
 std::wstring directory=std::wstring(base)+L"\\PressMachine";
 CreateDirectoryW(directory.c_str(),nullptr);
 std::wstring path=directory+L"\\OFXv2-test.log";
 HANDLE file=CreateFileW(path.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(file==INVALID_HANDLE_VALUE)return;
 SYSTEMTIME t;GetSystemTime(&t);char line[256];
 int count=std::snprintf(line,sizeof(line),"%04u-%02u-%02uT%02u:%02u:%02uZ pid=%lu backend=%s stream=%s srcRowBytes=%d dstRowBytes=%d\r\n",
  t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,GetCurrentProcessId(),cuda?"CUDA":"CPU",stream?"Host":"default/none",sourcePitch,targetPitch);
 DWORD written;if(count>0)WriteFile(file,line,(DWORD)count,&written,nullptr);CloseHandle(file);
}
