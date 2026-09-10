// SPDX-License-Identifier: GPL-3.0-or-later
// Exact RMGE01 rev0 context observation; not target readiness or tap permission.
#pragma once
#include <cstdint>
#include <bit>
#include <cmath>
#include <initializer_list>
#include <optional>
#include <array>

namespace galaxypad {
template<class Read32>
std::optional<uint32_t> ReadPointerWord(uint32_t base, uint32_t offset, Read32 read32) {
  uint64_t address=uint64_t(base)+offset;
  const bool mapped=(address>=0x80000000ull && address+4<=0x81800000ull) ||
                    (address>=0x90000000ull && address+4<=0x94000000ull);
  if (!mapped || (address&3)) return std::nullopt;
  return read32(static_cast<uint32_t>(address));
}
struct PointerContext {
  uint32_t controller=0; // identity used to invalidate observations on replacement
  uint32_t mode=0;
};

struct ProcessedPointer {
  uint32_t controller;
  float pastX, pastY, currentX, currentY;
  bool pastValid, currentValid;
};
struct PointerCalibration {
  float centerX, centerY, scale, playRadius, sensitivity;
  uint32_t filterMode;
};
// Raw finite inputs to the audited regular-point conversion, not a tracking
// validity assertion. Names follow the reference SDK; offsets are USA retail.
struct PointerConversionInputs {
  std::array<float,2> direction, referenceHorizon, accelerationHorizon;
  std::array<float,2> firstPoint, secondPoint, filteredPosition;
};
template<class Read32>
std::optional<PointerConversionInputs> ReadPointerConversionInputs(Read32 read32) {
  PointerConversionInputs result{};
  auto pair=[&](uint32_t offset,std::array<float,2>& out) {
    for (unsigned i=0;i<2;++i) {
      auto word=ReadPointerWord(0x8061d340,offset+4*i,read32);
      if (!word) return false;
      out[i]=std::bit_cast<float>(*word);
      if (!std::isfinite(out[i])) return false;
    }
    return true;
  };
  if (!pair(0x1b54,result.direction) || !pair(0xb0,result.referenceHorizon) ||
      !pair(0xa8,result.accelerationHorizon) || !pair(0xf4,result.firstPoint) ||
      !pair(0x100,result.secondPoint) || !pair(0x20,result.filteredPosition))
    return std::nullopt;
  return result;
}
// P1 inside_kpads in the exact USA DOL, verified through setter instructions.
// Read only on CPU thread after exact-DOL gating; this is not portable SDK layout.
template<class Read32>
std::optional<PointerCalibration> ReadPointerCalibration(Read32 read32) {
  auto value=[&](uint32_t offset)->std::optional<float> {
    auto word=ReadPointerWord(0x8061d340,offset,read32);
    if (!word) return std::nullopt;
    float f=std::bit_cast<float>(*word);
    return std::isfinite(f)?std::optional(f):std::nullopt;
  };
  auto x=value(0xb8),y=value(0xbc),scale=value(0xc0),radius=value(0x84),sensitivity=value(0x88);
  // Retail filter loads this word at 8044FB88; only modes 0 and 1 are audited.
  auto mode=ReadPointerWord(0x8061d340,0x1be8,read32);
  if (!x || !y || !scale || !radius || !sensitivity || *scale<=0 || *radius<0 ||
      *sensitivity<0 || !mode || *mode>1) return std::nullopt;
  return PointerCalibration{*x,*y,*scale,*radius,*sensitivity,*mode};
}
// Exact USA P1 director chain, observed on the CPU thread. These are guest
// screen coordinates, not normalized host coordinates or an input epoch.
template<class Read32>
std::optional<ProcessedPointer> ReadProcessedPointer(uint32_t r13, Read32 read32) {
  if (r13<14968) return std::nullopt;
  auto object=ReadPointerWord(r13-14968,0,read32);
  for (uint32_t offset:{0x20u,0x30u,4u}) {
    if (!object || !*object) return std::nullopt;
    object=ReadPointerWord(*object,offset,read32);
  }
  if (!object || !*object) return std::nullopt;
  auto channel=ReadPointerWord(*object,0,read32);
  auto px=ReadPointerWord(*object,4,read32), py=ReadPointerWord(*object,8,read32);
  auto pv=ReadPointerWord(*object,0xc,read32);
  auto cx=ReadPointerWord(*object,0x18,read32), cy=ReadPointerWord(*object,0x1c,read32);
  auto cv=ReadPointerWord(*object,0x20,read32);
  if (!channel || *channel!=0 || !px || !py || !pv || !cx || !cy || !cv ||
      (*pv>>24)>1 || (*cv>>24)>1) return std::nullopt;
  ProcessedPointer result{*object,std::bit_cast<float>(*px),std::bit_cast<float>(*py),
    std::bit_cast<float>(*cx),std::bit_cast<float>(*cy),bool(*pv>>24),bool(*cv>>24)};
  if (!std::isfinite(result.pastX) || !std::isfinite(result.pastY) ||
      !std::isfinite(result.currentX) || !std::isfinite(result.currentY)) return std::nullopt;
  return result;
}

// Caller must establish the supported DOL identity and run on the CPU thread.
// read32 returns a big-endian guest word or nullopt, never dereferences unchecked
// host pointers. Return unknown during startup, transitions or invalid chains.
template<class Read32>
std::optional<PointerContext> ReadPointerContext(uint32_t r13, Read32 read32) {
  auto read=[&](uint32_t base, uint32_t offset) -> std::optional<uint32_t> {
    return ReadPointerWord(base,offset,read32);
  };
  if (r13<14968) return std::nullopt;
  auto object=read(r13-14968,0);
  for (uint32_t offset:{12u,4u,8u}) {
    if (!object || !*object) return std::nullopt;
    object=read(*object,offset);
  }
  if (!object || !*object) return std::nullopt;
  auto mode=read(*object,0xd0);
  if (!mode || *mode>=26) return std::nullopt;
  return PointerContext{*object,*mode};
}

struct FilePointerTarget {
  uint32_t selector=0, item=0;
  bool pointing=false, invalid=false;
};
struct ActorPointerState {
  uint32_t spine=0, current=0, pending=0;
};
// Observe both states: getCurrentNerve prefers pending during a transition.
// A consumer must not treat the old current state as stable when pending!=0.
template<class Read32>
std::optional<ActorPointerState> ReadActorPointerState(uint32_t actor, Read32 read32) {
  auto spine=ReadPointerWord(actor,0x50,read32);
  if (!spine || !*spine) return std::nullopt;
  auto current=ReadPointerWord(*spine,4,read32);
  auto pending=ReadPointerWord(*spine,8,read32);
  if (!current || !*current || !pending) return std::nullopt;
  // Nerve objects contain a mapped vtable word; only validate readability here.
  if (!ReadPointerWord(*current,0,read32) ||
      (*pending && !ReadPointerWord(*pending,0,read32))) return std::nullopt;
  return ActorPointerState{*spine,*current,*pending};
}
// Diagnostic observation only. A cached hovered item is NOT tap authorization.
template<class Read32>
std::optional<FilePointerTarget> ReadFilePointerTarget(PointerContext context, Read32 read32) {
  if (context.mode!=5) return std::nullopt;
  auto read=[&](uint32_t base,uint32_t offset) { return ReadPointerWord(base,offset,read32); };
  uint32_t selector=0;
  for (uint32_t i=0;i<16;++i) {
    auto request=read(context.controller,0x0c+4*i);
    if (!request || !*request) return std::nullopt;
    auto owner=read(*request,0), mode=read(*request,4);
    if (!owner || !mode) return std::nullopt;
    if (*mode!=5 || !*owner) continue;
    if (selector && selector!=*owner) return std::nullopt;
    selector=*owner;
  }
  if (!selector) return std::nullopt;
  auto item=read(selector,0xbc);
  if (!item) return std::nullopt;
  if (!*item) return FilePointerTarget{selector,0,false,false};
  auto flags=read(*item,0x144);
  if (!flags) return std::nullopt;
  auto pointing=*flags>>24, invalid=(*flags>>16)&255;
  if (pointing>1 || invalid>1) return std::nullopt;
  return FilePointerTarget{selector,*item,pointing==1,invalid==1};
}
} // namespace galaxypad
