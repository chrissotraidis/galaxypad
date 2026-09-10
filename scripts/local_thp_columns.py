"""Offline first-pass local-state experiment; never changes a selected module."""
import hashlib

SOURCE_SHA='98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'


def candidate_source(source):
    if hashlib.sha256(source.encode()).hexdigest()!=SOURCE_SHA:
        raise ValueError('Unexpected extracted kernel identity')
    body='\nlabel_80452750:\n'+source.split('\nlabel_80452750:\n',1)[1].split('\nlabel_80452970:\n',1)[0]
    return r'''
static bool galaxy_columns_disjoint(const void* p,size_t n,const void* q,size_t m) {
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)q;
 return a>=b?a-b>=m:b-a>=n;
}
static __attribute__((always_inline)) inline bool galaxy_columns_body(CPUState* ctx) {
BODY
label_80452970: ctx->pc=0x80452970u; return true;
}
static bool galaxy_try_local_columns(CPUState* cpu,bool* completed) {
 if(cpu->pc!=0x80452750u||cpu->ctr!=8||cpu->exception||!(cpu->msr&PPC_MSR_FP)||
    !(cpu->hid2&PPC_HID2_LSQE)||cpu->gqr[5]!=0x00070007u||
    (cpu->gqr[0]&0x00070007u)||g_mem_write_journal||
    cpu->downcount<INT64_MIN+4096||!cpu->ram||cpu->ram_size<264||cpu->ram_size>0x10000000u||
    (cpu->exram&&(cpu->exram_size<264||cpu->exram_size>0x10000000u))) return false;
 u8* pointers[]={get_ram_ptr(cpu,cpu->gpr[3],144,NULL),
                 get_ram_ptr(cpu,cpu->gpr[5],264,NULL),
                 get_ram_ptr(cpu,cpu->gpr[10]+8u,256,NULL)};
 const size_t sizes[]={144,264,256};
 for(unsigned i=0;i<3;i++) {
  if(!pointers[i]||!galaxy_columns_disjoint(pointers[i],sizes[i],cpu,sizeof(*cpu))||
     !galaxy_columns_disjoint(pointers[i],sizes[i],&g_mem_write_journal,sizeof(g_mem_write_journal))) return false;
  for(unsigned j=0;j<i;j++)if(!galaxy_columns_disjoint(pointers[i],sizes[i],pointers[j],sizes[j]))return false;
 }
 CPUState local=*cpu;
 bool done=galaxy_columns_body(&local);
 *cpu=local;
 *completed=done;
 return true;
}
'''.replace('BODY',body)


def transform(source, coverage=False):
    helper=candidate_source(source)
    if coverage:
        helper=('#include <assert.h>\n#include <stdio.h>\nstatic unsigned long local_column_hits;\n'
                '__attribute__((destructor)) static void local_column_coverage(void) {\n'
                'assert(local_column_hits);fprintf(stderr,"local_column_hits=%lu\\n",local_column_hits);\n}\n'
                +helper.replace('CPUState local=*cpu;', '++local_column_hits; CPUState local=*cpu;'))
    marker='static __attribute__((noinline, flatten)) bool thp_kernel_0('
    entry='\nlabel_80452750:\n    ctx->pc = 0x80452750u;\n'
    # The outer dispatcher repeats this PC label; target only the charged body.
    charged_entry=entry+'    ctx->downcount -= 8;\n'
    assert source.count(marker)==1 and source.count(charged_entry)==1
    dispatch=('    { bool completed=false;\n'
              '      if(galaxy_try_local_columns(ctx,&completed)) {\n'
              '        if(!completed)return false;\n'
              '        goto label_80452970;\n      }\n    }\n')
    # Patch the original phase only, never the helper copy inserted afterward.
    changed=source.replace(charged_entry,entry+dispatch+'    ctx->downcount -= 8;\n',1)
    return changed.replace(marker,helper+'\n'+marker,1)
