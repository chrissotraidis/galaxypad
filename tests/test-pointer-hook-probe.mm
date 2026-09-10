#import <Foundation/Foundation.h>
#include "../apple/ios/GalaxyPadPointerHooks.h"
#include "moderngekko/mod_loader.hpp"
#include <cassert>
#include <cstring>
int main() {
  @autoreleasepool {
    moderngekko::ModManager manager;
    galaxypad::PointerHookProbe movementProbe;
    assert(!galaxypad::ObservePointerMovement(movementProbe,std::nullopt));
    galaxypad::ProcessedPointer sample{0x80010000,0,0,0,0,false,false};
    assert(galaxypad::ObservePointerMovement(movementProbe,sample));
    assert(!galaxypad::ObservePointerMovement(movementProbe,sample));
    sample.currentValid=true;
    assert(galaxypad::ObservePointerMovement(movementProbe,sample));
    for(unsigned i=0;i<40;i++) {
      sample.currentX+=1;
      assert(galaxypad::ObservePointerMovement(movementProbe,sample)==(i<30));
    }
    assert(movementProbe.movements==32);
    auto sources=std::vector{moderngekko::ModSource::AttachedDescriptor(galaxypad::PointerHookDescriptor())};
    assert(manager.Load(sources,"RMGE01"));
    CPUState state{}; state.pc=0x803fb0ec; state.lr=0x80178eb0;
    state.gpr[1]=0x81700000; state.gpr[3]=0x81144cc8;
    auto original=state;
    assert(!manager.Dispatch(&state,state.pc));
    assert(std::memcmp(&original,&state,sizeof(state))==0);
    state.pc=state.lr; state.gpr[3]=1; original=state;
    assert(!manager.Dispatch(&state,state.pc));
    assert(std::memcmp(&original,&state,sizeof(state))==0);
    assert(galaxypad::pointerHookProbe.hits==1 && galaxypad::pointerHookProbe.depth==0);
    for (unsigned i=0;i<17;++i) galaxypad::PointerQueryEntry(&state);
    assert(galaxypad::pointerHookProbe.invalid);
    manager.Unload(); assert(manager.Load(sources,"RMGE01"));
    assert(!galaxypad::pointerHookProbe.invalid && !galaxypad::pointerHookProbe.depth);
    galaxypad::PointerQueryEntry(&state);
    state.pc=0x80000000;
    galaxypad::PointerQueryReturn(&state);
    assert(galaxypad::pointerHookProbe.invalid);
    galaxypad::pointerHookProbe={};
    state.lr=0x80000000;
    galaxypad::NativePointerQueryObservation(&state,0x803fb0ec);
    assert(!galaxypad::pointerHookProbe.depth);
    state.lr=0x80178ec8;
    galaxypad::NativePointerQueryObservation(&state,0x803fb0ec);
    assert(galaxypad::pointerHookProbe.depth==1);
    state.pc=state.lr; state.gpr[3]=1;
    galaxypad::NativePointerQueryObservation(&state,state.pc);
    assert(!galaxypad::pointerHookProbe.depth && galaxypad::pointerHookProbe.hits==1);
    std::vector<uint8_t> ram(24*1024*1024);
    state.ram=ram.data(); state.gpr[13]=0x80010000;
    auto store=[&](uint32_t address,uint32_t word) {
      auto* p=ram.data()+address-0x80000000;
      for (unsigned i=0;i<4;++i) p[i]=uint8_t(word>>(24-8*i));
    };
    store(state.gpr[13]-14968,0x80020000);
    store(0x80020020,0x80030000); store(0x80030030,0x80040000);
    store(0x80040004,0x80050000);
    store(0x80050004,std::bit_cast<uint32_t>(123.f));
    store(0x80050008,std::bit_cast<uint32_t>(234.f));
    store(0x8005000c,0x01000000);
    for (auto [offset,value]:{std::pair{0xb8u,0.f},{0xbcu,-.2f},{0xc0u,2.f},
                              {0x84u,.03f},{0x88u,.5f}})
      store(0x8061d340+offset,std::bit_cast<uint32_t>(value));
    store(0x8061ef28,1);
    store(0x8061d3e8,std::bit_cast<uint32_t>(.25f));
    galaxypad::pointerHookProbe={};
    original=state;
    galaxypad::NativePointerQueryObservation(&state,0x803fb0ec);
    assert(std::memcmp(&original,&state,sizeof(state))==0);
    assert(galaxypad::pointerHookProbe.frames[0].position);
    assert(galaxypad::pointerHookProbe.frames[0].calibration);
    assert(galaxypad::pointerHookProbe.frames[0].conversion);
    store(0x8061d3e8,0);
    assert(galaxypad::pointerHookProbe.frames[0].conversion->accelerationHorizon[0]==.25f);
    store(0x8061ef28,0);
    assert(galaxypad::pointerHookProbe.frames[0].calibration->filterMode==1);
    store(0x80050004,std::bit_cast<uint32_t>(456.f));
    assert(galaxypad::pointerHookProbe.frames[0].position->pastX==123.f);
    assert(galaxypad::pointerHookProbe.frames[0].position->pastY==234.f);
    assert(galaxypad::pointerHookProbe.frames[0].position->pastValid);
    galaxypad::NativePointerQueryObservation(&state,state.pc);
    assert(!galaxypad::pointerHookProbe.depth);
    state.ram=nullptr;
    puts("Pointer hook probe: pairing, state preservation, bounded stack, reset and native caller filter pass");
  }
}
