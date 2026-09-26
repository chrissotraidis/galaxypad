#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <optional>
#include <time.h>
namespace galaxypad::precision_timing {
enum Counter : unsigned {Calls,Late,Positive,RequestedNs,WallNs,CpuNs,SpinNs,
  OvershootNs,MaxOvershootNs,CpuValid,HistBegin,Count=HistBegin+8};
using Counters=std::array<std::uint64_t,Count>;
inline std::atomic<bool> enabled{false};
struct Lane {std::array<std::atomic<std::uint64_t>,Count> values{};std::atomic<std::uint64_t> sequence{0};};
inline std::array<Lane,2> lanes{};
// Only CoreTiming's CPU and video branches assign these lanes; unrelated timer users are ignored.
inline thread_local int lane=-1;
inline thread_local Counters totals{};
inline thread_local std::uint64_t lastPublication=0;
inline thread_local unsigned publications=0;
struct Scope {int previous;explicit Scope(int value):previous(lane){lane=value;}~Scope(){lane=previous;}};
inline void Record(Counters& c,std::uint64_t start,std::uint64_t target,std::uint64_t end,
                   std::uint64_t spin,std::uint64_t cpu,bool valid) {
  ++c[Calls];c[Late]+=target<=start;c[Positive]+=target>start;
  c[RequestedNs]+=target>start?target-start:0;c[WallNs]+=end-start;
  c[CpuNs]+=valid?cpu:0;c[CpuValid]+=valid;c[SpinNs]+=end-spin;
  // Late arrivals cannot establish wakeup overshoot. Keep them in Late only.
  const auto over=target>start&&end>target?end-target:0;
  c[OvershootNs]+=over;c[MaxOvershootNs]=std::max(c[MaxOvershootNs],over);
  constexpr std::array<std::uint64_t,7> edges={10000,50000,100000,250000,500000,1000000,5000000};
  unsigned i=0;while(i<edges.size()&&over>=edges[i])++i;if(target>start)++c[HistBegin+i];
}
inline std::optional<Counters> Read(unsigned index) {
  auto& l=lanes[index];
  for(unsigned attempt=0;attempt<3;++attempt){const auto before=l.sequence.load();
    if(!before||(before&1))continue;Counters result;
    for(unsigned i=0;i<Count;++i)result[i]=l.values[i].load();
    if(l.sequence.load()==before)return result;
  }return std::nullopt;
}
inline std::uint64_t Wall(){return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count();}
inline std::optional<std::uint64_t> Cpu(){timespec t{};if(clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t))return std::nullopt;return std::uint64_t(t.tv_sec)*1000000000+t.tv_nsec;}
struct Measurement {
  bool active;std::uint64_t start=0,target=0,spin=0;std::optional<std::uint64_t> cpu;
  template<class Time> explicit Measurement(Time deadline):active(enabled.load(std::memory_order_relaxed)&&lane>=0){
    if(!active)return;target=std::chrono::duration_cast<std::chrono::nanoseconds>(deadline.time_since_epoch()).count();
    cpu=Cpu();start=Wall();spin=start;
  }
  void Spin(){if(active)spin=Wall();}
  ~Measurement(){if(!active)return;const auto end=Wall();const auto endCpu=Cpu();
    const bool valid=cpu&&endCpu&&*endCpu>=*cpu;
    Record(totals,start,target,end,spin,valid?*endCpu-*cpu:0,valid);
    // Bounded publication; no allocation or IO in timing paths.
    if(end-lastPublication>=1000000000&&publications<512){lastPublication=end;++publications;
      auto& l=lanes[lane];l.sequence.fetch_add(1);
      for(unsigned i=0;i<Count;++i)l.values[i].store(totals[i]);l.sequence.fetch_add(1);}
  }
};
}
