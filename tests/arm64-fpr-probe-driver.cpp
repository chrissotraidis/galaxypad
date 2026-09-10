#include "core/cpu.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <random>
extern "C" void galaxypad_aot_fpr_probe(CPUState*);
static CPUState callback_state;
static bool candidate_call;
#ifdef AOT_PAIRED_MERGES
static CPUState merge_checkpoint;
static unsigned checkpoint_calls;
extern "C" void galaxypad_aot_merge_checkpoint(CPUState* cpu) {
  assert(candidate_call && checkpoint_calls++==0);
  assert(!std::memcmp(cpu,&merge_checkpoint,sizeof(*cpu)));
}
#endif
extern "C" void galaxypad_aot_fpr_callback(CPUState* cpu) {
  if(candidate_call) assert(!std::memcmp(cpu,&callback_state,sizeof(*cpu)));
  else callback_state=*cpu;
  // Bitwise mutations include NaNs, signed zero and non-FP fields.
  for(unsigned r=0;r<32;++r) {
    u64 bits;std::memcpy(&bits,&cpu->fpr[r],8);bits^=0x9e3779b97f4a7c15ull*(r+1);
    std::memcpy(&cpu->fpr[r],&bits,8);
    std::memcpy(&bits,&cpu->ps1[r],8);bits^=0xd1b54a32d192ed03ull*(r+1);
    std::memcpy(&cpu->ps1[r],&bits,8);
  }
  cpu->fpscr^=0x12345678;cpu->pc^=0x1000;cpu->gpr[7]^=123;
}
int main() {
  std::mt19937_64 random(800);
  for(unsigned iteration=0;iteration<100000;++iteration) {
    CPUState a{};
    for(unsigned r=0;r<32;++r) {
      auto x=random(),y=random();std::memcpy(&a.fpr[r],&x,8);std::memcpy(&a.ps1[r],&y,8);
      a.gpr[r]=random();
    }
    if(iteration<65536) {
      // Every exponent/sign with eight mantissa edges, each under16 FPCR modes.
      const u32 mantissas[]={0,1,0x3fffff,0x400000,0x7ffffe,0x7fffff,0x200001,0x400001};
      const unsigned pattern=iteration/16;
      const u32 low=((pattern>>11)<<31)|(((pattern>>3)&255)<<23)|mantissas[pattern&7];
      const u32 high=(low^0x807fffffu);
      // f2 propagates through the copy chain to f20 before the callback XOR.
      const u64 input=(u64(low)|(u64(high)<<32))^(0x9e3779b97f4a7c15ull*21);
      std::memcpy(&a.fpr[2],&input,8);
    }
    a.fpscr=(random()&0x0fffffffu)|((iteration&15)<<28);
    a.cr=random();a.xer=random();a.pc=random();CPUState b=a;
    // Use byte moves only: preserving signaling-NaN payloads is part of this gate.
    auto pair=[&](unsigned d,unsigned s) {
      std::memmove(&a.fpr[d],&a.fpr[s],8);std::memmove(&a.ps1[d],&a.ps1[s],8);
    };
    pair(3,1);std::memcpy(&a.fpr[3],&a.fpr[2],8);pair(4,3);
    std::memcpy(&a.fpr[5],&a.fpr[4],8);std::memcpy(&a.ps1[5],&a.fpr[4],8);
    for(unsigned r=6;r<32;++r) pair(r,r-1);
    candidate_call=false;galaxypad_aot_fpr_callback(&a);
    std::memcpy(&a.fpr[0],&a.fpr[1],8);pair(2,0);
#ifdef AOT_EXACT_FP
    u64 packed;std::memcpy(&packed,&a.fpr[20],8);
    const u64 low=convert_to_double(u32(packed)),high=convert_to_double(u32(packed>>32));
    std::memcpy(&a.fpr[10],&low,8);std::memcpy(&a.ps1[10],&high,8);pair(11,10);
    std::memcpy(&a.fpr[12],&low,8);pair(13,12);
    std::memcpy(&a.fpr[14],&low,8);std::memcpy(&a.ps1[14],&low,8);pair(15,14);
    std::memcpy(&a.fpr[16],&a.fpr[2],8);std::memcpy(&a.ps1[16],&high,8);
#endif
#ifdef AOT_PAIRED_MERGES
    for(unsigned record=0;record<2;++record)for(unsigned selector=0;selector<4;++selector) {
      for(unsigned d=0;d<32;++d) {
        const unsigned ra=(d%4==1 || d%4==3)?d:(d+1)%32;
        const unsigned rb=(d%4==2 || d%4==3)?d:(d+7)%32;
        u64 low,high;
        std::memcpy(&low,(selector>>1)?&a.ps1[ra]:&a.fpr[ra],8);
        std::memcpy(&high,(selector&1)?&a.ps1[rb]:&a.fpr[rb],8);
        std::memcpy(&a.fpr[d],&low,8);
        std::memcpy(&a.ps1[d],&high,8);
        if(record) a.cr=(a.cr&0xf0ffffffu)|((a.fpscr>>4)&0x0f000000u);
      }
      if(record==0 && selector==3) merge_checkpoint=a;
    }
    checkpoint_calls=0;
#endif
    candidate_call=true;
    const u64 flags=iteration&0x9fu;
    u64 saved_flags,after_flags,saved_mode,after_mode;
    asm volatile("mrs %0, fpcr" : "=r"(saved_mode));
    const u64 mode=(saved_mode&~((3ull<<22)|(1ull<<24)|(1ull<<25))) |
                    (u64(iteration&3)<<22) | (u64((iteration>>2)&1)<<24) |
                    (u64((iteration>>3)&1)<<25);
    asm volatile("msr fpcr, %0" : : "r"(mode));
    asm volatile("mrs %0, fpsr" : "=r"(saved_flags));
    asm volatile("msr fpsr, %0" : : "r"(flags));
    galaxypad_aot_fpr_probe(&b);
#ifdef AOT_PAIRED_MERGES
    assert(checkpoint_calls==1);
#endif
    asm volatile("mrs %0, fpsr" : "=r"(after_flags));
    asm volatile("mrs %0, fpcr" : "=r"(after_mode));
    asm volatile("msr fpsr, %0" : : "r"(saved_flags));
    asm volatile("msr fpcr, %0" : : "r"(saved_mode));
    assert(after_flags==flags && after_mode==mode);
    assert(!std::memcmp(&a,&b,sizeof(a)));
  }
  std::puts("100000 full CPUState split-lane/spill/callback-entry/final-state and host FPSR/FPCR comparisons passed; includes65536 exponent/sign/mantissa-edge by host-mode cases");
}
