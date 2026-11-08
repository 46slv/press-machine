#pragma once
#include <atomic>
namespace pmtrace {
// Nonblocking, bounded attempts. Completed/exhausted calls do no sink work.
class Gate {
 inline static std::atomic_flag sharedSink=ATOMIC_FLAG_INIT;
 std::atomic<unsigned> state{0}; // idle, in-flight, complete, exhausted
 unsigned attempts=0; // accessed only by the successful CAS owner
public:
 template<class Sink> bool emit(Sink&& sink) noexcept {
  if(state.load(std::memory_order_acquire)!=0)return false;
  unsigned expected=0;
  if(!state.compare_exchange_strong(expected,1,std::memory_order_acquire))return false;
  // Contention is deferred, not a failed attempt. Do no sink work or
  // budget accounting while another backend owns the shared logger.
  if(sharedSink.test_and_set(std::memory_order_acquire)){
   state.store(0,std::memory_order_release);return false;
  }
  struct Release{std::atomic_flag& f;~Release(){f.clear(std::memory_order_release);}} release{sharedSink};
  bool success=false;
  try{success=sink();}catch(...){}
  ++attempts;
  state.store(success?2:(attempts<3?0:3),std::memory_order_release);
  return success;
 }
};
}
