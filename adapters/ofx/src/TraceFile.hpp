#pragma once
#include <windows.h>
#include <shlobj.h>
#include <string>
namespace pmtrace {
enum class FileStage{success,path,directory,open,write,flush,close,exception};
struct FileResult {
 bool ok=false;
 FileStage stage=FileStage::path;
 DWORD error=ERROR_PATH_NOT_FOUND;
 HRESULT folderHR=E_UNEXPECTED;
 unsigned pathKind=0; // 0 unavailable, 1 KnownFolder, 2 environment fallback
};
inline const char* stageName(FileStage s){
 switch(s){
 case FileStage::success:return "success";case FileStage::path:return "path";
 case FileStage::directory:return "directory";case FileStage::open:return "open";
 case FileStage::write:return "write";case FileStage::flush:return "flush";
 case FileStage::close:return "close";default:return "exception";
 }
}
inline FileResult writeFile(const std::wstring& directory,const char* text,DWORD count){
 FileResult result;
 if(!CreateDirectoryW(directory.c_str(),nullptr)){
  const DWORD error=GetLastError();
  const DWORD attributes=GetFileAttributesW(directory.c_str());
  if(error!=ERROR_ALREADY_EXISTS||attributes==INVALID_FILE_ATTRIBUTES||!(attributes&FILE_ATTRIBUTE_DIRECTORY)){
   result.stage=FileStage::directory;result.error=error;return result;
  }
 }
 const std::wstring path=directory+L"\\OFXv2-test.log";
 HANDLE file=CreateFileW(path.c_str(),GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,
                         nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
 if(file==INVALID_HANDLE_VALUE){result.stage=FileStage::open;result.error=GetLastError();return result;}
 DWORD written=0;
 OVERLAPPED append{};append.Offset=MAXDWORD;append.OffsetHigh=MAXDWORD;
 // The handle is synchronous; MAXDWORD offsets atomically append to EOF.
 const BOOL wrote=WriteFile(file,text,count,&written,&append);
 if(!wrote||written!=count){
  result.stage=FileStage::write;result.error=wrote?ERROR_WRITE_FAULT:GetLastError();
 }else if(!FlushFileBuffers(file)){
  result.stage=FileStage::flush;result.error=GetLastError();
 }else{
  result.ok=true;result.stage=FileStage::success;result.error=ERROR_SUCCESS;
 }
 if(!CloseHandle(file)&&result.ok){result.ok=false;result.stage=FileStage::close;result.error=GetLastError();}
 return result;
}
inline FileResult localFile(const char* text,DWORD count){
 std::wstring directory;
 PWSTR folder=nullptr;
 const HRESULT hr=SHGetKnownFolderPath(FOLDERID_LocalAppData,KF_FLAG_DEFAULT,nullptr,&folder);
 struct FreeFolder{PWSTR p;~FreeFolder(){if(p)CoTaskMemFree(p);}} release{folder};
 unsigned kind=0;
 if(SUCCEEDED(hr)&&folder&&*folder){directory=folder;kind=1;}
 else {
  const DWORD length=GetEnvironmentVariableW(L"LOCALAPPDATA",nullptr,0);
  if(!length||length>32768){
   FileResult result;result.folderHR=hr;result.error=length?ERROR_BUFFER_OVERFLOW:GetLastError();return result;
  }
  std::wstring environment(length,L'\0');
  const DWORD copied=GetEnvironmentVariableW(L"LOCALAPPDATA",&environment[0],length);
  if(!copied||copied>=length){
   FileResult result;result.folderHR=hr;result.error=copied?ERROR_BUFFER_OVERFLOW:GetLastError();return result;
  }
  environment.resize(copied);directory=environment;kind=2;
 }
 auto result=writeFile(directory+L"\\PressMachine",text,count);
 result.folderHR=hr;result.pathKind=kind;return result;
}
}
