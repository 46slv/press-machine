#include <windows.h>
#include <map>
#include <mutex>
#include <stdexcept>
#include "../../vnext/generated/PixelCore.hpp"
#include <vector>
using Handle=void*;using Status=int;
class VNextDriver{public:HMODULE dll;Status (__stdcall *ctx)(Handle*);Status (__stdcall *contextId)(Handle,unsigned long long*);Status (__stdcall *load)(Handle*,const void*);Status (__stdcall *function)(Handle*,Handle,const char*);Status (__stdcall *streamSync)(Handle);Status (__stdcall *launch)(Handle,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,unsigned,Handle,void**,void**);
 VNextDriver(){dll=LoadLibraryExW(L"nvcuda.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);if(!dll)throw std::runtime_error("NVIDIA driver unavailable");
  ctx=(decltype(ctx))GetProcAddress(dll,"cuCtxGetCurrent");contextId=(decltype(contextId))GetProcAddress(dll,"cuCtxGetId");load=(decltype(load))GetProcAddress(dll,"cuModuleLoadData");function=(decltype(function))GetProcAddress(dll,"cuModuleGetFunction");launch=(decltype(launch))GetProcAddress(dll,"cuLaunchKernel");streamSync=(decltype(streamSync))GetProcAddress(dll,"cuStreamSynchronize");
  if(!ctx||!contextId||!load||!function||!launch||!streamSync)throw std::runtime_error("CUDA driver entry point unavailable");}};
void runCudaVNext(void*stream,const void*src,void*dst,long long sp,long long dp,int sx1,int sy1,int sx2,int sy2,int dx1,int dy1,int rx1,int ry1,int rx2,int ry2,int premult,const pm::Parameters&params){
 static VNextDriver driver;static std::mutex mutex;static std::map<std::pair<Handle,unsigned long long>,Handle>functions;Handle context=nullptr,fun=nullptr;if(driver.ctx(&context)||!context)throw std::runtime_error("No current Host CUDA context");
 {unsigned long long id=0;if(driver.contextId(context,&id))throw std::runtime_error("CUDA context ID query failed");const auto key=std::make_pair(context,id);std::lock_guard<std::mutex>lock(mutex);auto i=functions.find(key);
  if(i==functions.end()){Handle module=nullptr;HMODULE self=nullptr;static const int anchor=0;if(!GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,(LPCWSTR)&anchor,&self))throw std::runtime_error("Plugin module unavailable");
   auto resource=FindResourceW(self,MAKEINTRESOURCEW(201),MAKEINTRESOURCEW(10));if(!resource)throw std::runtime_error("Embedded CUDA PTX missing");const DWORD size=SizeofResource(self,resource);const char*data=(const char*)LockResource(LoadResource(self,resource));std::vector<char>ptx(data,data+size);ptx.push_back(0);
   if(driver.load(&module,ptx.data())||driver.function(&fun,module,"PressMachineVNextKernel"))throw std::runtime_error("CUDA module load failed");functions[key]=fun;}else fun=i->second;}
 if(rx2<=rx1||ry2<=ry1)return;pm::Parameters p=params;void*args[]={&src,&dst,&sp,&dp,&sx1,&sy1,&sx2,&sy2,&dx1,&dy1,&rx1,&ry1,&rx2,&ry2,&premult,&p};
 if(driver.launch(fun,(rx2-rx1+15)/16,(ry2-ry1+7)/8,1,16,8,1,0,stream,args,nullptr))throw std::runtime_error("CUDA kernel enqueue failed");if(!stream&&driver.streamSync(nullptr))throw std::runtime_error("CUDA default stream completion failed");
}
