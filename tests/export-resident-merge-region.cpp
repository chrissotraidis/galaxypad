// Static, relocatable value-region export. Caller checks FP availability and
// retains the original generated chunk's cycle precharge. No runtime code cache.
#include "Core/PowerPC/JitArm64/Jit.h"
#include "aot-paired-merge.h"
#include "aot-paired-multiply.h"
#include "Common/MsgHandler.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
namespace Common {
bool MsgAlertFmtImpl(bool,MsgType,Log::LogType,const char* file,int line,
                    fmt::string_view,const fmt::format_args&) {
  std::fprintf(stderr,"Resident merge assertion %s:%d\n",file,line);std::abort();
}
}
int main(int argc,char** argv) {
  if(argc<3 || argc>18) return 2;
  const unsigned count=argc-2;
  char* tail=nullptr;
  const unsigned long address=std::strtoul(argv[1],&tail,16);
  if(tail==argv[1] || *tail || (address&3) || address>0x100000000ul-count*4) return 2;
  std::array<u32,16> operations;
  for(unsigned i=0;i<count;++i) {
    const unsigned long word=std::strtoul(argv[i+2],&tail,16);
    if(tail==argv[i+2] || *tail || word>0xfffffffful) return 2;
    const auto decoded=AotDecodePairedMerge(u32(word));
    const bool multiply=(word>>26)==4 && ((word>>1)&31)==25 && !(word&1) && ((word>>11)&31)==0;
    const unsigned op5=(word>>1)&31;
    const bool fma=(word>>26)==4 && op5>=28 && op5<=31 && !(word&1);
    const bool selected=(word>>26)==4 && op5>=12 && op5<=15 && !(word&1) &&
                        (op5>=14 || ((word>>11)&31)==0);
    const bool sum=(word>>26)==4 && (op5==10 || op5==11) && !(word&1);
    const bool scalar=(word>>26)==59 && op5==25 && !(word&1) && ((word>>11)&31)==0;
    if(!decoded && !multiply && !fma && !selected && !sum && !scalar) return 2;
    operations[i]=u32(word);
  }
  using namespace Arm64Gen;using enum ARM64Reg;
  std::puts(".text");
  for(unsigned entry=0;entry<count;++entry) {
    alignas(16) std::array<u8,32768> bytes{};
    JitArm64 emit(bytes.data(),bytes.data()+bytes.size());
    ARM64FloatEmitter fp(&emit);
    emit.STP(IndexType::Pre,X29,X30,SP,-160);emit.MOV(X29,X0);
    for(int r=8;r<16;r+=2) fp.STP(128,IndexType::Signed,
      static_cast<ARM64Reg>(int(Q0)+r),static_cast<ARM64Reg>(int(Q0)+r+1),SP,16+(r-8)*16);
    Arm64FPRCache cache;cache.Init(&emit);cache.Lock(Q24,Q25,Q26,Q27,Q28,Q29,Q30,Q31);
    for(unsigned i=entry;i<count;++i) {
      emit.MOVI2R(W0,u32(address+i*4));
      emit.STR(IndexType::Unsigned,W0,X29,offsetof(CPUState,pc));
      const auto word=operations[i];
      if(const auto op=AotDecodePairedMerge(word)) {
        AotMergePair(emit,cache,op->dest,op->a,op->b,op->lane_a,op->lane_b);
        if(op->record) AotRecordCR1(emit);
      } else {
        const unsigned op5=(word>>1)&31;
        AotMultiplyPair(emit,cache,(word>>21)&31,(word>>16)&31,(word>>6)&31,
                        (op5==25 || op5==12 || op5==13)?-1:int((word>>11)&31),
                        op5==28 || op5==30,op5>=30,(op5>=12 && op5<=15)?int(op5&1):-1,
                        (op5==10 || op5==11)?int(op5&1):-1,(word>>26)==59);
      }
    }
    cache.Flush(FlushMode::All,INVALID_REG);
    for(int r=8;r<16;r+=2) fp.LDP(128,IndexType::Signed,
      static_cast<ARM64Reg>(int(Q0)+r),static_cast<ARM64Reg>(int(Q0)+r+1),SP,16+(r-8)*16);
    emit.LDP(IndexType::Post,X29,X30,SP,160);emit.RET();
    if(emit.HasWriteFailed()) return 1;
    std::printf(".p2align 2\n.globl _galaxypad_resident_merge_%u\n_galaxypad_resident_merge_%u:\n",entry,entry);
    for(ptrdiff_t offset=0;offset<emit.GetCodePtr()-bytes.data();offset+=4) {
      u32 word;std::memcpy(&word,bytes.data()+offset,4);std::printf(" .long 0x%08x\n",word);
    }
  }
}
