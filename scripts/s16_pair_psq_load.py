"""Offline four-byte mapped signed16 pair, original helper on every fallback."""
from s16_psq_load import HELPER as PER_LANE_HELPER, transform as per_lane_transform

HELPER = r'''
static inline bool galaxy_s16_pair_load(CPUState* cpu,u8 frD,u32 ea,bool w,
                                       u8 gqr_index,bool indexed,u32 cia) {
 const u32 gqr=cpu->gqr[gqr_index&7u];
 if(!w && (gqr&0x3f070000u)==0x00070000u &&
    (indexed||(cpu->hid2&PPC_HID2_LSQE)) &&
    cpu->ram_size>=4u && cpu->ram_size<=0x10000000u &&
    (!cpu->exram || (cpu->exram_size>=4u && cpu->exram_size<=0x10000000u))) {
  u8* pair=get_ram_ptr(cpu,ea,4u,NULL);
  if(pair) {
   cpu->fpr[frD]=(f64)(s16)read_be16(pair);
   cpu->ps1[frD]=(f64)(s16)read_be16(pair+2u);
   return true;
  }
 }
 return ppc_psq_load_inline(cpu,frD,ea,w,gqr_index,indexed,cia);
}
'''

def transform(source, coverage=False):
    changed = per_lane_transform(source)
    assert changed.count(PER_LANE_HELPER) == 1
    helper = HELPER
    if coverage:
        helper = ('#include <assert.h>\n#include <stdio.h>\nstatic unsigned long pair_hits;\n'
                  '__attribute__((destructor)) static void pair_coverage(void) {\n'
                  'assert(pair_hits);fprintf(stderr,"pair_hits=%lu\\n",pair_hits);\n}\n'
                  + helper.replace('   cpu->fpr[frD]=', '   ++pair_hits; cpu->fpr[frD]='))
    return changed.replace(PER_LANE_HELPER, helper).replace(
        'galaxy_s16_load(', 'galaxy_s16_pair_load(')
