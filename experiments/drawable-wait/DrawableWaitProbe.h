#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <optional>
namespace galaxypad::drawable_wait {
enum Counter : unsigned { Calls, TotalNs, MaxNs, Nil, PendingAfter, BusyAfter,
  BusyToIdle, BusyToIdleNs, PendingChanged, HistBegin, HistEnd=HistBegin+8,
  StateCount=HistEnd, StateNs=StateCount+4, StateMax=StateNs+4, Count=StateMax+4 };
using Counters=std::array<std::uint64_t,Count>;
inline std::atomic<bool> enabled{false};
inline std::array<std::atomic<std::uint64_t>,Count> published{};
inline std::atomic<std::uint64_t> sequence{0};
inline thread_local Counters totals{};
inline thread_local unsigned publications=0;
struct State {bool pending,busy;};
inline void Record(std::uint64_t ns,bool nil,State before,State after) {
  ++totals[Calls];totals[TotalNs]+=ns;totals[MaxNs]=std::max(totals[MaxNs],ns);
  totals[Nil]+=nil;totals[PendingAfter]+=after.pending;totals[BusyAfter]+=after.busy;
  if(before.busy&&!after.busy){++totals[BusyToIdle];totals[BusyToIdleNs]+=ns;}
  totals[PendingChanged]+=before.pending!=after.pending;
  constexpr std::array<std::uint64_t,7> edges={10000,50000,100000,500000,1000000,5000000,16000000};
  unsigned bucket=0;while(bucket<edges.size()&&ns>=edges[bucket])++bucket;
  ++totals[HistBegin+bucket];
  const unsigned state=2*before.pending+before.busy;
  ++totals[StateCount+state];totals[StateNs+state]+=ns;
  totals[StateMax+state]=std::max(totals[StateMax+state],ns);
  // At most 128 publications, once per 120 acquisitions. No per-call IO.
  if(totals[Calls]%120==0&&publications<128){
    ++publications;sequence.fetch_add(1);
    for(unsigned i=0;i<Count;++i)published[i].store(totals[i]);
    sequence.fetch_add(1);
  }
}
inline std::optional<Counters> Read() {
  for(unsigned attempt=0;attempt<3;++attempt){
    const auto before=sequence.load();if(!before||(before&1))continue;
    Counters result;for(unsigned i=0;i<Count;++i)result[i]=published[i].load();
    if(sequence.load()==before)return result;
  }
  return std::nullopt;
}
template<class Clock,class Inspect,class Acquire>
auto Measure(Clock clock,Inspect inspect,Acquire acquire) {
  if(!enabled.load(std::memory_order_relaxed))return acquire();
  const State before=inspect();const auto start=clock();
  auto drawable=acquire();const auto end=clock();const State after=inspect();
  Record(end-start,!drawable,before,after);return drawable;
}
}
