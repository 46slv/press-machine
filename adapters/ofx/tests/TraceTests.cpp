#include <atomic>
#include <thread>
#include <vector>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <cstdarg>
#include <cstring>
#include <iterator>
#include "../src/TraceGate.hpp"
#include "../src/TraceHost.hpp"
#include "../src/TraceFile.hpp"
static void require(bool v,const char* why){if(!v)throw std::runtime_error(why);}
static int reply=kOfxStatOK;
static unsigned hostCalls=0;
static std::string hostText,hostFormat;
static std::atomic<bool> blockHost{false},hostEntered{false},releaseHost{false};
static OfxStatus message(void*,const char* type,const char* id,const char* format,...){
 require(std::strcmp(type,kOfxMessageLog)==0,"Wrong message type");
 require(std::strcmp(id,"PressMachineBackendTrace")==0,"Wrong log ID");
 hostFormat=format;
 if(blockHost.load()){hostEntered.store(true);while(!releaseHost.load())std::this_thread::yield();}
 char data[512];va_list args;va_start(args,format);std::vsnprintf(data,sizeof(data),format,args);va_end(args);
 hostText=data;++hostCalls;return reply;
}
int main(int argc,char** argv){
 try{
  require(argc==2,"Need owned workspace fixture directory");
  unsigned checks=0;
  {
   pmtrace::Gate gate;unsigned calls=0;
   for(int i=0;i<100;++i)gate.emit([&](){++calls;return true;});
   require(calls==1,"Successful gate did repeated sink work");++checks;
  }
  {
   pmtrace::Gate gate;unsigned calls=0;
   for(int i=0;i<100;++i)gate.emit([&](){++calls;return false;});
   require(calls==3,"Failure budget not bounded");++checks;
  }
  {
   pmtrace::Gate gate;unsigned calls=0;
   for(int i=0;i<100;++i)gate.emit([&](){++calls;throw std::runtime_error("mock");return false;});
   require(calls==3,"Exception stranded gate or escaped budget");++checks;
  }
  {
   pmtrace::Gate gate;unsigned calls=0;
   for(int i=0;i<100;++i)gate.emit([&](){return ++calls==3;});
   require(calls==3,"Retry did not become complete");++checks;
  }
  {
   pmtrace::Gate gate;std::atomic<unsigned> calls{0};std::vector<std::thread> threads;
   for(int i=0;i<16;++i)threads.emplace_back([&](){for(int j=0;j<100;++j)gate.emit([&](){++calls;return true;});});
   for(auto& thread:threads)thread.join();
   require(calls==1,"Concurrent calls duplicated successful sink");++checks;
  }
  {
   pmtrace::Gate cpu,cuda;unsigned a=0,b=0;
   cpu.emit([&](){++a;return true;});cuda.emit([&](){++b;return true;});
   require(a==1&&b==1,"Backend budgets not independent");++checks;
  }
  OfxMessageSuiteV1 suite{message};
  require(!pmtrace::hostLog(nullptr,nullptr,"x"),"Null suite accepted");++checks;
  OfxMessageSuiteV1 empty{};
  require(!pmtrace::hostLog(&empty,nullptr,"x"),"Missing callback accepted");++checks;
  reply=kOfxStatOK;
  require(pmtrace::hostLog(&suite,nullptr,"percent %s %n literal"),"Successful Host log rejected");
  require(hostFormat=="%s"&&hostText=="percent %s %n literal","Unsafe Host printf forwarding");++checks;
  reply=kOfxStatReplyDefault;
  require(!pmtrace::hostLog(&suite,nullptr,"not accepted"),"Non-OK Host status accepted");++checks;
  {
   pmtrace::Gate cpu,cuda;unsigned cudaCalls=0;std::atomic<bool> cpuSuccess{false};
   reply=kOfxStatOK;blockHost=true;hostEntered=false;releaseHost=false;
   std::thread first([&](){cpuSuccess=cpu.emit([&](){return pmtrace::hostLog(&suite,nullptr,"blocked CPU");});});
   for(unsigned i=0;i<100000&&!hostEntered.load();++i)std::this_thread::yield();
   const bool entered=hostEntered.load();
   for(int i=0;i<100;++i)cuda.emit([&](){++cudaCalls;return pmtrace::hostLog(&suite,nullptr,"deferred CUDA");});
   const unsigned during=cudaCalls;
   releaseHost=true;first.join();blockHost=false;
   require(entered&&cpuSuccess,"Blocked Host test failed to enter callback");
   require(during==0,"Busy Host consumed other backend sink work");
   require(cuda.emit([&](){++cudaCalls;return pmtrace::hostLog(&suite,nullptr,"CUDA after release");}),"Deferred backend exhausted its retry budget");
   require(cudaCalls==1,"Deferred backend call count wrong");++checks;
  }
  const auto root=std::filesystem::absolute(argv[1])/(std::to_wstring(GetCurrentProcessId())+L"-"+std::to_wstring(GetTickCount64()));
  std::filesystem::create_directories(root);
  const auto good=root/L"append";
  const std::string one="trace-one\r\n",two="trace-two\r\n";
  const auto a=pmtrace::writeFile(good.wstring(),one.data(),(DWORD)one.size());
  require(a.ok,"Real file write/flush/close failed");
  const auto b=pmtrace::writeFile(good.wstring(),two.data(),(DWORD)two.size());
  require(b.ok,"Append failed");
  std::ifstream in(good/L"OFXv2-hud-density-test.log",std::ios::binary);
  const std::string content((std::istreambuf_iterator<char>(in)),{});
  require(content==one+two,"Append bytes differed");++checks;
  {
   const auto concurrent=root/L"concurrent";
   std::vector<std::thread> threads;std::atomic<unsigned> succeeded{0};
   for(int i=0;i<16;++i)threads.emplace_back([&,i](){
    const std::string row="row-"+std::to_string(i)+"\r\n";
    if(pmtrace::writeFile(concurrent.wstring(),row.data(),(DWORD)row.size()).ok)++succeeded;
   });
   for(auto& thread:threads)thread.join();
   require(succeeded==16,"Concurrent append failed");
   std::ifstream appended(concurrent/L"OFXv2-hud-density-test.log",std::ios::binary);
   const std::string rows((std::istreambuf_iterator<char>(appended)),{});
   for(int i=0;i<16;++i){
    const auto row="row-"+std::to_string(i)+"\r\n";
    const auto first=rows.find(row);
    require(first!=std::string::npos&&rows.find(row,first+row.size())==std::string::npos,"Concurrent rows lost or duplicated");
   }
   ++checks;
  }
  const auto bad=pmtrace::writeFile((root/L"missing-parent"/L"child").wstring(),one.data(),(DWORD)one.size());
  require(!bad.ok&&bad.stage==pmtrace::FileStage::directory&&bad.error!=0,"Missing parent failure was hidden");++checks;
  const auto blocked=root/L"blocked";
  std::filesystem::create_directories(blocked/L"OFXv2-hud-density-test.log");
  const auto denied=pmtrace::writeFile(blocked.wstring(),one.data(),(DWORD)one.size());
  require(!denied.ok&&denied.stage==pmtrace::FileStage::open&&denied.error!=0,"File-open failure was hidden");++checks;
  std::cout<<"{\"status\":\"PASS\",\"checks\":"<<checks<<",\"owned_fixture_only\":true,\"Host_or_GPU_used\":false}"<<std::endl;
  return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<std::endl;return 1;}
}
