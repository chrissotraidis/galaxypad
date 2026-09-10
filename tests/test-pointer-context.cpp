// SPDX-License-Identifier: GPL-3.0-or-later
#include "../apple/shared/GalaxyPadPointerContext.h"
#include <cassert>
#include <map>
#include <cstdio>
int main() {
  constexpr uint32_t r13=0x80010000;
  std::map<uint32_t,uint32_t> memory={{r13-14968,0x80020000},
    {0x8002000c,0x90001000},{0x90001004,0x80030000},
    {0x80030008,0x90002000},{0x900020d0,5}};
  auto read=[&](uint32_t address)->std::optional<uint32_t> {
    auto found=memory.find(address);
    return found==memory.end()?std::nullopt:std::optional(found->second);
  };
  auto context=galaxypad::ReadPointerContext(r13,read);
  assert(!galaxypad::ReadPointerConversionInputs(read));
  for (uint32_t offset:{0x1b54u,0xb0u,0xa8u,0xf4u,0x100u,0x20u}) {
    memory[0x8061d340+offset]=std::bit_cast<uint32_t>(1.f);
    memory[0x8061d344+offset]=std::bit_cast<uint32_t>(.25f);
  }
  auto conversion=galaxypad::ReadPointerConversionInputs(read);
  assert(conversion && conversion->direction[0]==1 && conversion->direction[1]==.25f &&
    conversion->referenceHorizon[0]==1 && conversion->accelerationHorizon[1]==.25f &&
    conversion->firstPoint[0]==1 && conversion->secondPoint[1]==.25f &&
    conversion->filteredPosition[0]==1);
  for (uint32_t offset:{0x1b54u,0xb0u,0xa8u,0xf4u,0x100u,0x20u}) {
    for (uint32_t invalid:{0x7fc00000u,0x7f800000u,0xff800000u}) {
      memory[0x8061d340+offset]=invalid;
      assert(!galaxypad::ReadPointerConversionInputs(read));
    }
    memory.erase(0x8061d340+offset);
    assert(!galaxypad::ReadPointerConversionInputs(read));
    memory[0x8061d340+offset]=std::bit_cast<uint32_t>(1.f);
  }
  assert(!galaxypad::ReadPointerCalibration(read));
  for (auto [offset,value]:{std::pair{0xb8u,0.f},{0xbcu,-.1f},{0xc0u,2.f},
                            {0x84u,.03f},{0x88u,.5f}})
    memory[0x8061d340+offset]=std::bit_cast<uint32_t>(value);
  assert(!galaxypad::ReadPointerCalibration(read)); // Missing mode is unknown.
  memory[0x8061ef28]=0;
  auto calibration=galaxypad::ReadPointerCalibration(read);
  assert(calibration && calibration->centerX==0 && calibration->centerY==-.1f &&
         calibration->scale==2 && calibration->playRadius==.03f && calibration->sensitivity==.5f &&
         calibration->filterMode==0);
  memory[0x8061ef28]=1;
  assert(galaxypad::ReadPointerCalibration(read)->filterMode==1);
  for (uint32_t invalid:{2u,0xffffffffu}) {
    memory[0x8061ef28]=invalid;
    assert(!galaxypad::ReadPointerCalibration(read));
  }
  memory[0x8061ef28]=0;
  for (uint32_t invalid:{0u,0xbf800000u,0x7fc00000u,0x7f800000u}) {
    memory[0x8061d400]=invalid;
    assert(!galaxypad::ReadPointerCalibration(read));
  }
  memory[0x80020020]=0x90005000;
  memory[0x90005030]=0x90006000;
  memory[0x90006004]=0x90007000;
  memory[0x90007000]=0;
  for (auto [offset,value]:{std::pair{4u,120.f},{8u,220.f},{0x18u,320.f},{0x1cu,420.f}})
    memory[0x90007000+offset]=std::bit_cast<uint32_t>(value);
  memory[0x9000700c]=0x01010000; memory[0x90007020]=0;
  auto processed=galaxypad::ReadProcessedPointer(r13,read);
  assert(processed && processed->controller==0x90007000 && processed->pastX==120.f &&
         processed->pastY==220.f && processed->currentX==320.f && processed->currentY==420.f &&
         processed->pastValid && !processed->currentValid);
  for (uint32_t invalid:{1u,0xffffffffu}) {
    memory[0x90007000]=invalid;
    assert(!galaxypad::ReadProcessedPointer(r13,read));
  }
  memory[0x90007000]=0;
  memory[0x9000700c]=0x02000000;
  assert(!galaxypad::ReadProcessedPointer(r13,read));
  memory[0x9000700c]=0;
  for (uint32_t invalid:{0x7fc00000u,0x7f800000u,0xff800000u}) {
    memory[0x90007004]=invalid;
    assert(!galaxypad::ReadProcessedPointer(r13,read));
  }
  memory[0x90007004]=0;
  assert(galaxypad::ReadProcessedPointer(r13,read));
  for (uint32_t invalid:{0u,0x80000001u,0x817ffffcu,0x94000000u,0xfffffffcu}) {
    memory[0x90006004]=invalid;
    assert(!galaxypad::ReadProcessedPointer(r13,read));
  }
  memory[0x90006004]=0x90007000;
  memory.erase(0x9000701c);
  assert(!galaxypad::ReadProcessedPointer(r13,read));
  assert(!galaxypad::ReadProcessedPointer(0,read));
  assert(context && context->controller==0x90002000 && context->mode==5);
  for (uint32_t invalid:{0u,0x80000001u,0x817ffffcu,0x94000000u,0xfffffffcu}) {
    memory[0x80030008]=invalid;
    assert(!galaxypad::ReadPointerContext(r13,read));
  }
  memory[0x80030008]=0x90002000;
  for (uint32_t invalid:{26u,0xffffffffu}) {
    memory[0x900020d0]=invalid;
    assert(!galaxypad::ReadPointerContext(r13,read));
  }
  assert(!galaxypad::ReadPointerContext(0,read));
  memory[0x900020d0]=25;
  context=galaxypad::ReadPointerContext(r13,read);
  assert(context && context->mode==25);
  for (uint32_t i=0;i<16;++i) {
    uint32_t request=0x90003000+i*8;
    memory[0x9000200c+i*4]=request;
    memory[request]=0; memory[request+4]=0xffffffffu;
  }
  memory[0x90003000]=0x80040000; memory[0x90003004]=5;
  memory[0x800400bc]=0x80050000;
  memory[0x80050144]=0x01000000;
  memory[0x80040050]=0x90004000;
  memory[0x90004004]=0x806a0114; memory[0x90004008]=0;
  memory[0x806a0114]=0x80500000; memory[0x806a0144]=0x80500100;
  auto state=galaxypad::ReadActorPointerState(0x80040000,read);
  assert(state && state->spine==0x90004000 && state->current==0x806a0114 && !state->pending);
  memory[0x90004008]=0x806a0144;
  state=galaxypad::ReadActorPointerState(0x80040000,read);
  assert(state && state->current==0x806a0114 && state->pending==0x806a0144);
  memory[0x90004008]=0xffffffff;
  assert(!galaxypad::ReadActorPointerState(0x80040000,read));
  memory[0x90004008]=0; memory[0x90004004]=0;
  assert(!galaxypad::ReadActorPointerState(0x80040000,read));
  memory.erase(0x80040050);
  assert(!galaxypad::ReadActorPointerState(0x80040000,read));
  auto target=galaxypad::ReadFilePointerTarget({0x90002000,5},read);
  assert(target && target->selector==0x80040000 && target->item==0x80050000 &&
         target->pointing && !target->invalid);
  memory[0x80050144]=0x01010000;
  assert(galaxypad::ReadFilePointerTarget({0x90002000,5},read)->invalid);
  memory[0x800400bc]=0;
  assert(galaxypad::ReadFilePointerTarget({0x90002000,5},read)->item==0);
  memory[0x90003008]=0x80060000; memory[0x9000300c]=5;
  assert(!galaxypad::ReadFilePointerTarget({0x90002000,5},read)); // ambiguous owners
  assert(!galaxypad::ReadFilePointerTarget({0x90002000,25},read)); // not file select
  memory.erase(0x90001004);
  assert(!galaxypad::ReadPointerContext(r13,read));
  puts("Pointer context and file target: bounds, modes, hover flags and ambiguous owners pass");
}
