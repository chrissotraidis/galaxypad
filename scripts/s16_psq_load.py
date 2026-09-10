"""Offline exact signed16/scale-zero paired load specialization."""
import hashlib
import re
HELPER = r'''
static inline bool galaxy_s16_load(CPUState* cpu,u8 frD,u32 ea,bool w,
                                  u8 gqr_index,bool indexed,u32 cia) {
 const u32 gqr=cpu->gqr[gqr_index&7u];
 if((gqr&0x3f070000u)==0x00070000u &&
    (indexed||(cpu->hid2&PPC_HID2_LSQE))) {
  cpu->fpr[frD]=(f64)(s16)mem_read16(cpu,ea);
  cpu->ps1[frD]=w?1.0:(f64)(s16)mem_read16(cpu,ea+2u);
  return true;
 }
 return ppc_psq_load_inline(cpu,frD,ea,w,gqr_index,indexed,cia);
}
'''

def transform(source,coverage=False):
    if hashlib.sha256(source.encode()).hexdigest()!='98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991':
        raise ValueError('Unexpected extracted kernel identity')
    changed,count=re.subn(r'ppc_psq_load_inline(?=\(ctx, \d+u, ea, false, 5u, false, 0x[0-9A-F]+u\))',
                          'galaxy_s16_load',source)
    assert count==16
    helper=HELPER
    if coverage:
        helper=('#include <assert.h>\n#include <stdio.h>\nstatic unsigned long s16_hits;\n'
                '__attribute__((destructor)) static void s16_coverage(void) {\n'
                'assert(s16_hits);fprintf(stderr,"s16_hits=%lu\\n",s16_hits);\n}\n'
                +helper.replace('  cpu->fpr[frD]=','  ++s16_hits; cpu->fpr[frD]='))
    marker='static __attribute__((noinline, flatten)) bool thp_kernel_0('
    assert changed.count(marker)==1
    return changed.replace(marker,helper+'\n'+marker,1)
