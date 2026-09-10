// Included only by the private full-chunk --cross-island driver.
#include <assert.h>
#include <fenv.h>
#include <stdio.h>
static unsigned char cross_other[256];
static u64 cross_trace;
static unsigned cross_callbacks;
static void cross_observe(CPUState* cpu,u32 address,u64 value) {
  cross_trace=(cross_trace*0x100000001b3ull)^address^value^cpu->pc^
              f64_bits(cpu->fpr[8])^cpu->fpscr;
  ++cross_callbacks;
  cpu->fpr[0]=f64_value(0x3ff0000000000000ull);
  cpu->ps1[3]=f64_value(0x4000000000000000ull);
  cpu->gpr[3]=0x80000040;cpu->gpr[4]=0x80000050;
  cpu->ram=cross_other;cpu->ram_size=sizeof(cross_other);
  cpu->fpscr^=0x10000;cpu->downcount-=3;
}
static u64 cross_read(CPUState* cpu,u32 address,u8 size) {
  assert(size==4);cross_observe(cpu,address,0);
  return 0x3f800000u|((address&255)<<12);
}
static void cross_write(CPUState* cpu,u32 address,u64 value,u8 size) {
  assert(size==4);cross_observe(cpu,address,value);
}
static void cross_journal(u32 offset,u32 size,void* user) {
  cross_observe((CPUState*)user,offset,size);
}
static void cross_context_checks(void* left,void* right) {
  typedef void (*SetJournal)(PPCMemWriteJournal,void*);
  SetJournal set_left=(SetJournal)dlsym(left,"probe_set_journal");
  SetJournal set_right=(SetJournal)dlsym(right,"probe_set_journal");
  assert(set_left&&set_right);
  unsigned count=0,observed=0;
  unsigned char ram[256],before_ram[256],before_other[256];
  for(unsigned i=0;i<256;i+=4) {
    write_be32(before_ram+i,0x3f800000u+(i<<15));
    write_be32(before_other+i,0x40000000u+(i<<14));
  }
  for(unsigned entry=0;entry<15;++entry)for(unsigned mode=0;mode<8;++mode)
  for(unsigned offset=0;offset<=96;offset+=4)for(unsigned rn=0;rn<4;++rn) {
    CPUState state={0};
    state.ram=(mode&1)?(u8*)state.fpr:ram;state.ram_size=256;
    state.msr=0x2000;state.hid2=PPC_HID2_LSQE|PPC_HID2_PSE;
    state.lr=0x81234564;state.downcount=10000;state.pc=0x804b6cb8+4*entry;
    state.fpscr=rn;state.gpr[3]=(mode&2)?0xcc000040:0x80000040;
    state.gpr[4]=(mode&2)?0xcc000050:0x80000050;
    state.gpr[5]=(mode&2)?0xcc000000:0x80000000+offset;
    state.external_read=cross_read;state.external_write=cross_write;
    for(unsigned r=0;r<32;++r) {
      state.fpr[r]=f64_value(0x3ff0000000000000ull+((u64)r<<32));
      state.ps1[r]=f64_value(0x4000000000000000ull+((u64)r<<32));
    }
    // Run both variants at the same CPUState address: no pointer normalization.
    const CPUState before=state;
    memcpy(ram,before_ram,256);memcpy(cross_other,before_other,256);
    set_left((mode&4)?cross_journal:NULL,&state);
    cross_trace=0;cross_callbacks=0;ppc_fpscr_control_updated(&state);feclearexcept(FE_ALL_EXCEPT);
    reference(&state);const CPUState expected=state;
    const u64 expected_trace=cross_trace;const unsigned expected_calls=cross_callbacks;
    const int expected_flags=fetestexcept(FE_ALL_EXCEPT);
    unsigned char expected_ram[256],expected_other[256];
    memcpy(expected_ram,ram,256);memcpy(expected_other,cross_other,256);
    state=before;memcpy(ram,before_ram,256);memcpy(cross_other,before_other,256);
    set_right((mode&4)?cross_journal:NULL,&state);
    cross_trace=0;cross_callbacks=0;ppc_fpscr_control_updated(&state);feclearexcept(FE_ALL_EXCEPT);
    candidate(&state);
    assert(!memcmp(&state,&expected,sizeof(state)));
    assert(!memcmp(ram,expected_ram,256)&&!memcmp(cross_other,expected_other,256));
    assert(cross_trace==expected_trace&&cross_callbacks==expected_calls);
    assert(fetestexcept(FE_ALL_EXCEPT)==expected_flags);
    observed+=cross_callbacks;++count;
  }
  set_left(NULL,NULL);set_right(NULL,NULL);
  assert(observed>0);
  printf("%u full-context callback/journal/alias/suffix comparisons pass; %u observed callbacks\n",count,observed);
}
