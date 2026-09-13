// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <atomic>
namespace galaxypad::efb_direct_batch {
inline std::atomic<bool> enabled{false};
struct Context { bool refresh=false,populate=false,intermediate=false; };
inline thread_local Context context;
void EndMetalBatch();
bool HasMetalBatch();
inline bool Eligible() {return context.refresh && context.populate && !context.intermediate;}
// This scope is deliberately placed AFTER RefreshPeekCache's early return.
// It adds no work to the millions of empty FIFO polling calls.
struct RefreshScope {
  bool active=enabled.load(std::memory_order_relaxed);
  RefreshScope() {if(active) context.refresh=true;}
  ~RefreshScope() {if(active) {EndMetalBatch();context.refresh=false;}}
};
struct PopulateScope {
  bool active=context.refresh;
  PopulateScope() {if(active) {context.populate=true;context.intermediate=false;}}
  void setIntermediate(bool value) {if(active) context.intermediate=value;}
  ~PopulateScope() {if(active) context.populate=false;}
};
} // namespace galaxypad::efb_direct_batch
