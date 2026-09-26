// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <optional>

namespace galaxypad::efb_batch_probe {
enum Counter : unsigned {
  Refreshes, ActiveRefreshes, RefreshCopies, DemandCopies, DirectCopies,
  IntermediateCopies, BlitEncoders, ContiguousPairs, SameResourcePairs,
  MultiCopyRefreshes, MaximumCopies, MaximumRun, Count
};
inline std::atomic<bool> enabled{false};
inline std::array<std::atomic<std::uint64_t>,Count> published{};
inline std::atomic<std::uint64_t> publication{0};
// The recorder lives exclusively on the rendering thread. Only its occasional
// cumulative publication is shared; no allocations, timers, formatting or IO.
struct Recorder {
  std::array<std::uint64_t,Count> totals{};
  bool inRefresh=false,inPopulate=false,intermediate=false;
  std::uint64_t copies=0,run=0,workEpoch=0,lastCopyEpoch=~std::uint64_t(0);
  std::uintptr_t command=0,source=0,destination=0;
};
inline thread_local Recorder recorder;
inline bool Enabled() { return enabled.load(std::memory_order_relaxed); }
inline void Publish() {
  publication.fetch_add(1,std::memory_order_acq_rel);
  for(unsigned i=0;i<Count;++i) published[i].store(recorder.totals[i],std::memory_order_relaxed);
  publication.fetch_add(1,std::memory_order_release);
}
inline std::optional<std::array<std::uint64_t,Count>> Read() {
  for(unsigned attempt=0;attempt<3;++attempt) {
    const auto before=publication.load(std::memory_order_acquire);
    if(before&1) continue;
    std::array<std::uint64_t,Count> result;
    for(unsigned i=0;i<Count;++i) result[i]=published[i].load(std::memory_order_relaxed);
    std::atomic_thread_fence(std::memory_order_acquire);
    if(publication.load(std::memory_order_relaxed)==before) return result;
  }
  return std::nullopt;
}
inline void OtherWork() {
  if(Enabled() && recorder.inRefresh) ++recorder.workEpoch;
}
struct RefreshScope {
  bool active=Enabled();
  RefreshScope() {
    if(!active) return;
    recorder.inRefresh=true;recorder.copies=0;recorder.run=0;
    recorder.lastCopyEpoch=~std::uint64_t(0);++recorder.totals[Refreshes];
  }
  ~RefreshScope() {
    if(!active) return;
    if(recorder.copies) ++recorder.totals[ActiveRefreshes];
    if(recorder.copies>1) ++recorder.totals[MultiCopyRefreshes];
    recorder.totals[MaximumCopies]=std::max(recorder.totals[MaximumCopies],recorder.copies);
    recorder.inRefresh=false;
    // Empty FIFO refresh polling can run millions of times per second. Keep
    // counting it locally, but publish only on each 64th copy-bearing refresh.
    // The copies guard also prevents repeated publication while that active
    // count remains divisible by 64 across subsequent empty calls.
    if(recorder.copies && recorder.totals[ActiveRefreshes]%64==0) Publish();
  }
};
struct PopulateScope {
  bool active=Enabled();
  PopulateScope() {if(active) {recorder.inPopulate=true;recorder.intermediate=false;}}
  void setIntermediate(bool value) {if(active) recorder.intermediate=value;}
  ~PopulateScope() {if(active) recorder.inPopulate=false;}
};
inline void Copy(std::uintptr_t command,std::uintptr_t source,std::uintptr_t destination,
                 bool encoderCreated=true) {
  if(!Enabled()) return;
  auto& r=recorder;
  if(!r.inPopulate) {OtherWork();return;}
  if(encoderCreated) ++r.totals[BlitEncoders];
  ++r.totals[r.intermediate?IntermediateCopies:DirectCopies];
  if(!r.inRefresh) {++r.totals[DemandCopies];return;}
  ++r.totals[RefreshCopies];++r.copies;
  if(r.lastCopyEpoch==r.workEpoch && r.command==command) {
    ++r.totals[ContiguousPairs];++r.run;
    if(r.source==source && r.destination==destination) ++r.totals[SameResourcePairs];
  } else r.run=1;
  r.totals[MaximumRun]=std::max(r.totals[MaximumRun],r.run);
  r.lastCopyEpoch=r.workEpoch;r.command=command;r.source=source;r.destination=destination;
}
} // namespace galaxypad::efb_batch_probe
