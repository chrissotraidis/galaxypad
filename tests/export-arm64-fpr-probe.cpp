#include "Core/PowerPC/JitArm64/Jit.h"
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "Common/MsgHandler.h"
#include <array>
#include <cstdio>
#include <cstring>
#ifdef AOT_PAIRED_MERGES
#include "aot-paired-merge.h"
#endif
namespace Common {
bool MsgAlertFmtImpl(bool, MsgType, Log::LogType, const char* file, int line,
                    fmt::string_view, const fmt::format_args&) {
  std::fprintf(stderr,"FPR emitter assertion %s:%d\n",file,line);std::abort();
}
}
int main() {
#ifdef AOT_PAIRED_MERGES
  for(unsigned selector=0;selector<4;++selector)
    for(unsigned d=0;d<32;++d)for(unsigned a=0;a<32;++a)for(unsigned b=0;b<32;++b) {
      const u32 word=(4u<<26)|(d<<21)|(a<<16)|(b<<11)|((528+32*selector)<<1);
      const auto decoded=AotDecodePairedMerge(word);
      assert(decoded && decoded->dest==d && decoded->a==a && decoded->b==b &&
             decoded->lane_a==(selector>>1) && decoded->lane_b==(selector&1) && !decoded->record);
      const auto recorded=AotDecodePairedMerge(word|1);
      assert(recorded && recorded->record && recorded->dest==d && recorded->a==a &&
             recorded->b==b && recorded->lane_a==(selector>>1) && recorded->lane_b==(selector&1));
      assert(!AotDecodePairedMerge(word^(1u<<26)));
      assert(!AotDecodePairedMerge(word^2));
    }
#endif
  using namespace Arm64Gen;using enum ARM64Reg;
  alignas(16) std::array<u8,32768> bytes{};
  JitArm64 emit(bytes.data(),bytes.data()+bytes.size());
  ptrdiff_t merge_checkpoint=-1;
  ARM64FloatEmitter fp(&emit);
  emit.STP(IndexType::Pre,X29,X30,SP,-144);emit.MOV(X29,X0);
  for(int r=8;r<16;r+=2) fp.STP(128,IndexType::Signed,
    static_cast<ARM64Reg>(int(Q0)+r),static_cast<ARM64Reg>(int(Q0)+r+1),SP,16+(r-8)*16);
  Arm64FPRCache cache;cache.Init(&emit);cache.Lock(Q31);
#ifdef AOT_PAIRED_MERGES
  cache.Lock(Q30);
#endif
  auto pair=[&](unsigned d,unsigned s) {
    auto source=cache.R(s,RegType::Register);
    fp.MOV(cache.RW(d,RegType::Register),source);
  };
  auto lower=[&](unsigned d,unsigned s,RegType type) {
    auto source=cache.R(s,RegType::LowerPair);
    fp.MOV(cache.RW(d,type),source);
  };
  pair(3,1);lower(3,2,RegType::LowerPair); // Preserve dirty upper from f1.
  pair(4,3);lower(5,4,RegType::Duplicated);
  // Force spills with more guest registers than available host registers.
  for(unsigned r=6;r<32;++r) pair(r,r-1);
  cache.Flush(FlushMode::All,INVALID_REG);
  emit.MOV(X0,X29);
  const auto callback=emit.GetCodePtr()-bytes.data();
  auto branch=emit.BL();emit.SetJumpTarget(branch);
  lower(0,1,RegType::LowerPair);pair(2,0); // Callback changes must reload both lanes.
#ifdef AOT_EXACT_FP
  auto packed=[&](unsigned d,RegType type) {
    auto source=cache.R(20,RegType::LowerPair);
    fp.MOV(cache.RW(d,type),source);
  };
  packed(10,RegType::Single);pair(11,10);
  packed(12,RegType::LowerPairSingle);pair(13,12);
  packed(14,RegType::DuplicatedSingle);pair(15,14);
  packed(16,RegType::Single);lower(16,2,RegType::LowerPair);
#endif
#ifdef AOT_PAIRED_MERGES
  // Four lane selectors and all destination indices, with disjoint, d=a,
  // d=b and a=b=d operands under sustained cache pressure.
  for(unsigned record=0;record<2;++record)for(unsigned selector=0;selector<4;++selector) {
    for(unsigned d=0;d<32;++d) {
      const unsigned a=(d%4==1 || d%4==3)?d:(d+1)%32;
      const unsigned b=(d%4==2 || d%4==3)?d:(d+7)%32;
      const auto op=AotDecodePairedMerge((4u<<26)|(d<<21)|(a<<16)|(b<<11)|
                                       ((528+32*selector)<<1)|record);
      assert(op);
      AotMergePair(emit,cache,op->dest,op->a,op->b,op->lane_a,op->lane_b);
      if(op->record) AotRecordCR1(emit);
    }
    if(selector==1) cache.Flush(FlushMode::All,INVALID_REG);
    if(record==0 && selector==3) {
      cache.Flush(FlushMode::All,INVALID_REG);emit.MOV(X0,X29);
      merge_checkpoint=emit.GetCodePtr()-bytes.data();
      auto checkpoint_branch=emit.BL();emit.SetJumpTarget(checkpoint_branch);
    }
  }
#endif
  cache.Flush(FlushMode::All,INVALID_REG);
  for(int r=8;r<16;r+=2) fp.LDP(128,IndexType::Signed,
    static_cast<ARM64Reg>(int(Q0)+r),static_cast<ARM64Reg>(int(Q0)+r+1),SP,16+(r-8)*16);
  emit.LDP(IndexType::Post,X29,X30,SP,144);emit.RET();
  if(emit.HasWriteFailed()) return 1;
  std::puts(".text\n.p2align 2\n.globl _galaxypad_aot_fpr_probe\n_galaxypad_aot_fpr_probe:");
  for(ptrdiff_t offset=0;offset<emit.GetCodePtr()-bytes.data();offset+=4) {
    if(offset==callback) std::puts("  bl _galaxypad_aot_fpr_callback");
    else if(offset==merge_checkpoint) std::puts("  bl _galaxypad_aot_merge_checkpoint");
    else {u32 word;std::memcpy(&word,bytes.data()+offset,4);std::printf("  .long 0x%08x\n",word);}
  }
}
