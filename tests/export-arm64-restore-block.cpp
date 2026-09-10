// Private integer block decoder; unsupported instructions reject before export.
#include "Core/PowerPC/JitArm64/Jit.h"
#include "Core/PowerPC/JitArm64/JitArm64_RegCache.h"
#include "Common/MsgHandler.h"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <utility>
namespace Common {
bool MsgAlertFmtImpl(bool, MsgType, Log::LogType, const char* file, int line,
                     fmt::string_view, const fmt::format_args&) {
  std::fprintf(stderr,"Emitter assertion %s:%d\n",file,line);std::abort();
}
}
int main(int argc,char** argv) {
  if(argc<4 || argc>19) return 2;
  unsigned long start=std::strtoul(argv[1],nullptr,16);
  std::vector<u32> words(argc-2);
  for(unsigned i=0;i<words.size();++i) words[i]=std::strtoul(argv[i+2],nullptr,16);
  if(start>0x100000000ull-words.size()*4 || (start&3) || words.back()!=0x4e800020) return 2;
  for(unsigned i=0;i+1<words.size();++i) {
    const u32 opcode=words[i]>>26;
    if(opcode!=32 && opcode!=36 && opcode!=14 &&
       !(opcode==31 && ((words[i]>>1)&1023)==266 && !(words[i]&1))) return 2;
  }
  using namespace Arm64Gen;using enum ARM64Reg;
  std::puts(".text");
  for(unsigned entry=0;entry<words.size();++entry) {
    alignas(16) std::array<u8,4096> bytes{};
    JitArm64 emit(bytes.data(),bytes.data()+bytes.size());
    std::vector<std::pair<size_t,const char*>> relocations;
    auto call=[&](const char* name) {
      relocations.emplace_back(emit.GetCodePtr()-bytes.data(),name);
      auto branch=emit.BL();emit.SetJumpTarget(branch);
    };
    emit.STP(IndexType::Pre,X29,X30,SP,-96);
    for(int r=19;r<=27;r+=2) emit.STP(IndexType::Signed,
      static_cast<ARM64Reg>(static_cast<int>(X0)+r),
      static_cast<ARM64Reg>(static_cast<int>(X0)+r+1),SP,16+(r-19)*8);
    emit.MOV(X29,X0);
    Arm64GPRCache cache;cache.Init(&emit);
    cache.Lock(W0,W1,W2,W3);
#ifdef AOT_FAST_LOAD
    cache.Lock(W9,W10,W11,W12,W13);
#endif
    for(unsigned i=entry;i+1<words.size();++i) {
      const u32 word=words[i],rd=(word>>21)&31,ra=(word>>16)&31;
      const s32 displacement=static_cast<s16>(word);
      const u32 opcode=word>>26;
      if(opcode==14) {
        if(ra==0) {
          cache.BindToRegister(rd,false);emit.MOVI2R(cache.R(rd),static_cast<u32>(displacement));
        } else {
          const auto source=cache.R(ra);
          cache.BindToRegister(rd,false);
          auto scratch=cache.GetScopedReg();
          if(displacement<0) emit.SUBI2R(cache.R(rd),source,-displacement,scratch);
          else emit.ADDI2R(cache.R(rd),source,displacement,scratch);
        }
        continue;
      }
      if(opcode==31) {
        const auto left=cache.R(ra),right=cache.R((word>>11)&31);
        cache.BindToRegister(rd,false);emit.ADD(cache.R(rd),left,right);continue;
      }
      if(ra) emit.MOV(W2,cache.R(ra));else emit.MOVI2R(W2,0);
      cache.Flush(FlushMode::All,INVALID_REG);
      auto scratch=cache.GetScopedReg();
      if(displacement<0) emit.SUBI2R(W2,W2,static_cast<u32>(-displacement),scratch);
      else emit.ADDI2R(W2,W2,static_cast<u32>(displacement),scratch);
      emit.MOV(X0,X29);emit.MOVI2R(W1,rd);emit.MOVI2R(W3,start+i*4);
#ifdef AOT_FAST_LOAD
      if(opcode==32) {
        // All dirty guest registers have been flushed before mapping/read.
        // PC must be visible even when RAM aliases CPUState bytes.
        emit.STR(IndexType::Unsigned,W3,X29,offsetof(CPUState,pc));
        emit.AND(W9,W2,LogicalImm(0xbfffffffu,GPRSize::B32));
        emit.LDR(IndexType::Unsigned,X11,X29,offsetof(CPUState,exram));
        auto no_exram=emit.CBZ(X11);
        emit.MOVI2R(W13,0x90000000u);emit.SUB(W10,W9,W13);
        emit.LDR(IndexType::Unsigned,W12,X29,offsetof(CPUState,exram_size));
        emit.SUB(W12,W12,4u);emit.CMP(W10,W12);
        auto exram_hit=emit.B(CCFlags::CC_LS);
        emit.SetJumpTarget(no_exram);
        emit.MOVI2R(W13,0x80000000u);emit.SUB(W10,W9,W13);
        emit.LDR(IndexType::Unsigned,W12,X29,offsetof(CPUState,ram_size));
        emit.SUB(W12,W12,4u);emit.CMP(W10,W12);
        auto miss=emit.B(CCFlags::CC_HI);
        emit.LDR(IndexType::Unsigned,X11,X29,offsetof(CPUState,ram));
        auto no_ram=emit.CBZ(X11);
        emit.SetJumpTarget(exram_hit);
        emit.ADD(X11,X11,X10);
        emit.LDR(IndexType::Unsigned,W12,X11,0);
        emit.REV32(W12,W12);
        emit.STR(IndexType::Unsigned,W12,X29,offsetof(CPUState,gpr)+rd*sizeof(u32));
        auto done=emit.B();
        emit.SetJumpTarget(miss);emit.SetJumpTarget(no_ram);
        call("_galaxypad_aot_restore_load");
        emit.SetJumpTarget(done);
        continue;
      }
#endif
      call(opcode==32?"_galaxypad_aot_restore_load":"_galaxypad_aot_restore_store");
    }
    cache.Flush(FlushMode::All,INVALID_REG);
    emit.MOV(X0,X29);call("_galaxypad_aot_restore_return");
    for(int r=19;r<=27;r+=2) emit.LDP(IndexType::Signed,
      static_cast<ARM64Reg>(static_cast<int>(X0)+r),
      static_cast<ARM64Reg>(static_cast<int>(X0)+r+1),SP,16+(r-19)*8);
    emit.LDP(IndexType::Post,X29,X30,SP,96);emit.RET();
    if(emit.HasWriteFailed()) return 1;
    std::printf(".p2align 2\n.globl _galaxypad_aot_restore_%u\n_galaxypad_aot_restore_%u:\n",entry,entry);
    for(size_t offset=0;offset<static_cast<size_t>(emit.GetCodePtr()-bytes.data());offset+=4) {
      const char* symbol=nullptr;
      for(auto relocation:relocations) if(relocation.first==offset) symbol=relocation.second;
      if(symbol) std::printf("  bl %s\n",symbol);
      else {u32 word;std::memcpy(&word,bytes.data()+offset,4);std::printf("  .long 0x%08x\n",word);}
    }
  }
}
