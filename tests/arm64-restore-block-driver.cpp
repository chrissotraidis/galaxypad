#include "aot-block-frame.h"
#include <cassert>
#include <cstdio>
#include <vector>
#include <chrono>
PPCMemWriteJournal g_mem_write_journal;
void* g_mem_write_journal_user;
#ifdef AOT_DIRECT_CPU
using Adapter=CPUState;
#else
using Adapter=AotBlockFrame;
#endif
#ifdef AOT_MIXED_BLOCK
constexpr u32 block_start=0x80319ab8;
constexpr unsigned block_count=10;
#else
constexpr u32 block_start=0x80517584;
constexpr unsigned block_count=4;
#endif
extern "C" {
void galaxypad_aot_restore_0(Adapter*);
void galaxypad_aot_restore_1(Adapter*);
void galaxypad_aot_restore_2(Adapter*);
void galaxypad_aot_restore_3(Adapter*);
#ifdef AOT_MIXED_BLOCK
void galaxypad_aot_restore_4(Adapter*);
void galaxypad_aot_restore_5(Adapter*);
void galaxypad_aot_restore_6(Adapter*);
void galaxypad_aot_restore_7(Adapter*);
void galaxypad_aot_restore_8(Adapter*);
void galaxypad_aot_restore_9(Adapter*);
#endif
void galaxypad_aot_restore_load(Adapter* frame,u32 rd,u32 ea,u32 pc) {
#ifdef AOT_DIRECT_CPU
  CPUState* cpu=frame;
#else
  frame->ExportGPRs();
  CPUState* cpu=frame->guest;
#endif
  cpu->pc=pc;
  cpu->gpr[rd]=mem_read32(cpu,ea);
  #ifndef AOT_DIRECT_CPU
  frame->ImportGPRs();
  #endif
}
void galaxypad_aot_restore_store(Adapter* frame,u32 rs,u32 ea,u32 pc) {
#ifdef AOT_DIRECT_CPU
  CPUState* cpu=frame;
#else
  frame->ExportGPRs();CPUState* cpu=frame->guest;
#endif
  cpu->pc=pc;mem_write32(cpu,ea,cpu->gpr[rs]);
#ifndef AOT_DIRECT_CPU
  frame->ImportGPRs();
#endif
}
void galaxypad_aot_restore_return(Adapter* frame) {
#ifdef AOT_DIRECT_CPU
  frame->pc=frame->lr&~3u;
#else
  frame->ExportGPRs();frame->guest->pc=frame->guest->lr&~3u;
#endif
}
}
#include "restore-reference.inc"
static bool dispatch_restore(CPUState* guest) {
  using Block=void(*)(Adapter*);
  const Block blocks[]={galaxypad_aot_restore_0,galaxypad_aot_restore_1,
                        galaxypad_aot_restore_2,galaxypad_aot_restore_3
#ifdef AOT_MIXED_BLOCK
    ,galaxypad_aot_restore_4,galaxypad_aot_restore_5,galaxypad_aot_restore_6,
    galaxypad_aot_restore_7,galaxypad_aot_restore_8,galaxypad_aot_restore_9
#endif
  };
  const u32 offset=guest->pc-block_start;
  if(offset>4*(block_count-1) || (offset&3)) return false;
  const unsigned entry=offset/4;
  // Same suffix charge as the original generated switch, before callbacks.
  guest->downcount-=block_count-entry;
#ifdef AOT_DIRECT_CPU
  blocks[entry](guest);
#else
  AotBlockFrame frame{};frame.guest=guest;frame.ImportGPRs();blocks[entry](&frame);
#endif
  return true;
}
static std::array<u8,256> ram,exram,other;
static std::vector<u64> calls;
static u64 external(CPUState* cpu,u32 address,u8 size) {
  calls.push_back((u64(cpu->pc)<<32)|address);
  assert(size==4);
  // Mutate base, mappings, return state, flags and all registers in the callback.
  for(unsigned r=0;r<32;++r) cpu->gpr[r]^=0x9e3779b9u*(r+1);
  cpu->gpr[11]=0x80000040;
  cpu->ram=other.data();cpu->ram_size=other.size();
  cpu->lr^=0x1003;cpu->exception^=1;cpu->fpscr^=0x12345;
  cpu->downcount-=7;
  return address^0x12345678;
}
static void external_write(CPUState* cpu,u32 address,u64 value,u8 size) {
  calls.push_back(0xffffffffffffffffull);calls.push_back(value);
  external(cpu,address,size);
}
static void journal(u32 offset,u32 size,void* user) {
  calls.push_back(0xfffffffffffffffeull);calls.push_back(offset);
  auto* cpu=static_cast<CPUState*>(user);
  external(cpu,0xfeed0000|size,4);
}
int main(int argc,char**) {
  if(argc>1) {
    // Unsanitized, paired local cost gate, not a full-module/FPS measurement.
    constexpr unsigned iterations=1000000;
    for(unsigned sample=0;sample<8;++sample) for(unsigned order=0;order<2;++order) {
      const bool candidate=(sample+order)%2;
      CPUState cpu{};cpu.ram=ram.data();cpu.ram_size=ram.size();cpu.lr=0x81234567;
      ram.fill(0);g_mem_write_journal=nullptr;
      const auto begin=std::chrono::steady_clock::now();
      for(unsigned i=0;i<iterations;++i) {
        cpu.pc=block_start;cpu.gpr[11]=0x80000040;
        cpu.gpr[3]=0x80000040;cpu.gpr[0]=16;cpu.gpr[4]=32;cpu.gpr[6]=0;
        cpu.downcount=10000;
        if(candidate) {const bool accepted=dispatch_restore(&cpu);assert(accepted);}
        else reference(&cpu);
      }
      const auto elapsed=std::chrono::duration<double,std::nano>(
          std::chrono::steady_clock::now()-begin).count()/iterations;
      std::printf("sample=%u candidate=%u ns_per_block=%.3f checksum=%u\n",
                  sample,unsigned(candidate),elapsed,cpu.gpr[0]^cpu.gpr[29]^cpu.pc);
    }
    return 0;
  }
  for(unsigned i=0;i<256;++i) {ram[i]=i^37;exram[i]=i^91;other[i]=i^191;}
  const u32 regions[]={0x80000000,0xc0000000,0x90000000,0xd0000000,0,0xffffffff,0xcc000000};
  unsigned count=0;
  const auto initial_ram=ram,initial_exram=exram,initial_other=other;
  for(unsigned entry=0;entry<block_count;++entry) for(u32 region:regions)
  for(unsigned offset=0;offset<272;++offset) for(unsigned mode=0;mode<8;++mode) {
    ram=initial_ram;exram=initial_exram;other=initial_other;
    CPUState a{};a.ram=ram.data();a.ram_size=ram.size();
    a.exram=(mode&1)?exram.data():nullptr;a.exram_size=(mode&1)?exram.size():0;
    a.external_read=(mode&2)?external:nullptr;
    a.external_write=(mode&2)?external_write:nullptr;
    for(unsigned r=0;r<32;++r) a.gpr[r]=r*37+offset;
    a.gpr[11]=region+offset;
#ifdef AOT_MIXED_BLOCK
    a.gpr[3]=region+offset;a.gpr[0]=16;a.gpr[4]=32;
#endif
    a.pc=block_start+entry*4;
    a.lr=0x81234567;a.downcount=10000;a.fpscr=0x54321;
    CPUState b=a;
    g_mem_write_journal=(mode&4)?journal:nullptr;g_mem_write_journal_user=&a;
    calls.clear();reference(&a);const auto expected_calls=calls;
    const auto expected_ram=ram,expected_exram=exram,expected_other=other;
    ram=initial_ram;exram=initial_exram;other=initial_other;
    calls.clear();g_mem_write_journal_user=&b;assert(dispatch_restore(&b));
    assert(calls==expected_calls);
    assert(!std::memcmp(&a,&b,sizeof(a)));
    assert(ram==expected_ram && exram==expected_exram && other==expected_other);
    ++count;
  }
  for(u32 pc:{0u,block_start-4,block_start+2,block_start+4*block_count,0xffffffffu}) {
    CPUState state{};state.pc=pc;state.downcount=123;
    const CPUState before=state;
    calls.clear();assert(!dispatch_restore(&state));
    assert(calls.empty() && !std::memcmp(&state,&before,sizeof(state)));
  }
  // Reuse one CPU object's address for both runs: pointer bytes are identical,
  // and reads can observe canonical GPR/PC writes without pointer normalization.
  unsigned aliases=0;
  g_mem_write_journal=nullptr;g_mem_write_journal_user=nullptr;
  for(unsigned entry=0;entry<block_count;++entry)
  for(unsigned window=0;window<2;++window) for(unsigned offset=0;offset<144;++offset) {
    CPUState state{};
    state.ram=window?reinterpret_cast<u8*>(&state.pc):reinterpret_cast<u8*>(state.gpr);
    state.ram_size=window?sizeof(state.pc):sizeof(state.gpr);
    state.pc=block_start+entry*4;state.lr=0x81234567;state.downcount=10000;
    for(unsigned r=0;r<32;++r) state.gpr[r]=r*37;
    state.gpr[11]=0x80000000+offset;
#ifdef AOT_MIXED_BLOCK
    state.gpr[3]=0x80000000+offset;state.gpr[0]=16;state.gpr[4]=32;
#endif
    const CPUState before=state;
    reference(&state);const CPUState expected=state;
    state=before;assert(dispatch_restore(&state));
    assert(!std::memcmp(&state,&expected,sizeof(state)));
    ++aliases;
  }
  std::printf("%u actual-block/suffix complete CPUState and callback-trace comparisons passed\n",count);
  std::printf("%u CPUState RAM alias comparisons passed\n",aliases);
}
