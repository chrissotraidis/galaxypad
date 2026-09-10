"""Private whole-entry normal-MEM1 candidate; never changes generated product code."""
import re

def build(body):
    assert body.count('goto return_dispatch_804B60A0;') == 1
    fast = body.replace('goto return_dispatch_804B60A0;', 'return;')
    fast, count = re.subn(r'    if \(!ppc_fp_available_inline\(ctx, 0x[0-9A-F]+u\)\) return;\n', '', fast)
    entries = re.findall(r'^label_([0-9A-F]{8}):', body, re.M)
    assert (entries[0],len(entries)) in {('804B64A4',41),('804B6BCC',17),('804B6CB8',15)}
    assert count == len(entries)-1
    assert not re.search(r'ctx->gpr\[\d+\]\s*=',body)
    # Literal effective addresses remain in their original order. Only memory
    # acquisition and quantization checks become the whole-entry guard.
    pattern = r'ppc_psq_(load|store)_inline\(ctx, (\d+)u, ea, (true|false), 0u, false, 0x[0-9A-F]+u\);'
    accesses=[]
    for block in re.split(r'(?=^label_)',fast,flags=re.M):
        ea=re.search(r'u32 ea = ctx->gpr\[(\d+)\] \+ \(u32\)\(s32\)\((-?\d+)\);',block)
        if not ea:continue
        paired=re.search(pattern,block)
        assert paired or 'mem_read32(ctx, ea)' in block
        width=8 if paired and paired[3]=='false' else 4
        accesses.append((block,int(ea[1]),int(ea[2]),width,paired))
    spans={}
    for _,base,offset,width,_ in accesses:
        lo,hi=spans.get(base,(offset,offset+width))
        spans[base]=(min(lo,offset),max(hi,offset+width))
    assert len(spans)==3
    names=dict(zip(sorted(spans),('input','output','constant')))
    def replace(m,pointer):
        kind, register, one = m.groups()
        if kind == 'load':
            return (f'ctx->fpr[{register}]=f64_value(convert_to_double(read_be32({pointer})));\n'
                    f'        ctx->ps1[{register}]='+('1.0;' if one=='true' else
                    f'f64_value(convert_to_double(read_be32({pointer}+4)));'))
        result = f'clear_matching_reservation(ctx,ea);\n        write_be32({pointer},convert_to_single_ftz(f64_bits(ctx->fpr[{register}])));'
        if one == 'false':
            result += f'\n        clear_matching_reservation(ctx,ea+4);\n        write_be32({pointer}+4,convert_to_single_ftz(f64_bits(ctx->ps1[{register}])));'
        return result
    for block,base,offset,width,paired in accesses:
        pointer=f'{names[base]}+{offset-spans[base][0]}'
        replacement=(re.sub(pattern,lambda m:replace(m,pointer),block) if paired else
                     block.replace('mem_read32(ctx, ea)',f'read_be32({pointer})'))
        assert fast.count(block)==1
        fast=fast.replace(block,replacement,1)
    assert not re.search(r'\b(?:mem_read|mem_write|ppc_psq_)\w*\(',fast)
    guard = r'''
static bool wide_mem1(CPUState* ctx,u32 address,u32 size,u8** result) {
    const u32 offset=(address&~0x40000000u)-0x80000000u;
    if(!ctx->ram || ctx->ram_size<size || ctx->ram_size>0x10000000u ||
       ctx->exram_size>0x10000000u || (ctx->exram && ctx->exram_size<4) ||
       offset>ctx->ram_size-size) return false;
    const uintptr_t base=(uintptr_t)ctx->ram, state=(uintptr_t)ctx;
    if(base>UINTPTR_MAX-offset) return false;
    const uintptr_t start=base+offset;
    if(start>UINTPTR_MAX-size || state>UINTPTR_MAX-sizeof(*ctx)) return false;
    if(start<state+sizeof(*ctx) && state<start+size) return false;
    *result=(u8*)start;return true;
}
static bool wide_eligible(CPUState* ctx,u8** input,u8** output,u8** constant) {
    return ctx->pc==0x804B64A4u && (ctx->msr&PPC_MSR_FP) && !ctx->exception &&
       (ctx->hid2&PPC_HID2_LSQE) && !(ctx->gqr[0]&0x00070007u) &&
       !g_mem_write_journal &&
       wide_mem1(ctx,ctx->gpr[4],16,input) &&
       wide_mem1(ctx,ctx->gpr[3],48,output) &&
       wide_mem1(ctx,ctx->gpr[2]+9392u,4,constant);
}
'''
    guard=guard.replace('ctx->pc==0x804B64A4u',f'ctx->pc==0x{entries[0]}u')
    checks=' &&\n       '.join(f'wide_mem1(ctx,ctx->gpr[{base}]+{lo}u,{hi-lo},{names[base]})'
        for base,(lo,hi) in sorted(spans.items()))
    guard=guard[:guard.index('       wide_mem1(ctx,ctx->gpr[4]')]+ '       '+checks+';\n}\n'
    return guard+'\nstatic __attribute__((noinline)) void wide_fast(CPUState* ctx,u8* input,u8* output,u8* constant) {\n'+fast+'\n}\n'
