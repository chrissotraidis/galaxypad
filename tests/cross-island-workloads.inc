// Extra full-routine cost checks, injected inside the existing driver main.
// Input-copy and state-reset costs are included equally in both variants.
for(unsigned ni_mode=0;ni_mode<2;++ni_mode)for(unsigned workload=0;workload<4;++workload) {
 u32 inputs[64][6];
 for(unsigned n=0;n<64;++n)for(unsigned lane=0;lane<6;++lane) {
   const u32 fraction=((n*123457u+lane*76543u)&0x7fffffu);
   inputs[n][lane]=((127u+(n+lane)%5u)<<23)|fraction;
   if(workload==1)inputs[n][lane]=((107u+(n+lane)%5u)<<23)|fraction;
   if(workload==2)inputs[n][lane]=((197u+(n+lane)%5u)<<23)|fraction;
 }
 if(workload==3)for(unsigned n=0;n<64;++n) {
   inputs[n][0]=inputs[n][1]=inputs[n][3]=inputs[n][4]=0x3f800000;
   inputs[n][2]=0x33800000;inputs[n][5]=0x3f800001;
 }
 for(unsigned n=0;n<64;++n) {
  for(unsigned lane=0;lane<3;++lane) {
   write_be32(ram+64+lane*4,inputs[n][lane]);
   write_be32(ram+80+lane*4,inputs[n][lane+3]);
  }
  CPUState a=initial,b=initial;a.pc=b.pc=0x804b6cb8;
  a.fpscr=b.fpscr=ni_mode?FPSCR_NI_BIT:0;
  a.downcount=b.downcount=10000;
  memset(ram,0xa5,12);ppc_fpscr_control_updated(&a);feclearexcept(FE_ALL_EXCEPT);
  reference(&a);const int flags=fetestexcept(FE_ALL_EXCEPT);
  unsigned char output[12];memcpy(output,ram,12);
  memset(ram,0xa5,12);ppc_fpscr_control_updated(&b);feclearexcept(FE_ALL_EXCEPT);
  candidate(&b);
  assert(!memcmp(&a,&b,sizeof(a))&&!memcmp(output,ram,12));
  assert(flags==fetestexcept(FE_ALL_EXCEPT));
 }
 printf("ni=%u workload=%u all64 inputs match CPU/output/host flags\n",ni_mode,workload);
 for(unsigned run=0;run<4;++run) {
  const bool is_reference=run==0||run==3;
  void (*volatile fn)(CPUState*)=is_reference?reference:candidate;
  CPUState state=initial;
  state.fpscr=ni_mode?FPSCR_NI_BIT:0;
  ppc_fpscr_control_updated(&state);
  const unsigned repetitions=250000;
  u64 before=instructions();double start=now();
  for(unsigned i=0;i<repetitions;++i) {
   for(unsigned lane=0;lane<3;++lane) {
    write_be32(ram+64+lane*4,inputs[i%64][lane]);
    write_be32(ram+80+lane*4,inputs[i%64][lane+3]);
   }
   state.pc=0x804b6cb8;state.downcount=10000;state.fpscr=ni_mode?FPSCR_NI_BIT:0;fn(&state);
  }
  const double elapsed=now()-start;const u64 after=instructions();
  printf("ni=%u workload=%u %s ns/call=%.3f instructions/call=%.3f\n",ni_mode,workload,
         is_reference?"reference":"candidate",elapsed*1e9/repetitions,
         (double)(after-before)/repetitions);
 }
}
