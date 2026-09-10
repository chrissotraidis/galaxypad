"""Offline exact zero-column shortcut; retain original arithmetic and loop exit."""
import hashlib

SOURCE_SHA = '98d98621d4f744ea76977a63e44f3e2e3e731f50051e4a3a800a772e05a68991'
HELPER = r'''
static inline bool galaxy_zero_disjoint(const void* p, size_t n, const void* q, size_t m) {
    uintptr_t a=(uintptr_t)p,b=(uintptr_t)q;
    return a>=b ? a-b>=m : b-a>=n;
}
static inline bool galaxy_zero_column(CPUState* cpu) {
    if (cpu->exception || !(cpu->msr & PPC_MSR_FP) ||
        !(cpu->hid2 & PPC_HID2_LSQE) || cpu->gqr[5]!=0x00070007u ||
        (cpu->gqr[0] & 0x00070007u) || g_mem_write_journal ||
        !cpu->ram || cpu->ram_size<32u || cpu->ram_size>0x10000000u ||
        (cpu->exram && (cpu->exram_size<32u || cpu->exram_size>0x10000000u)) ||
        cpu->downcount<INT64_MIN+22) return false;
    u8* coefficients=get_ram_ptr(cpu,cpu->gpr[3],16,NULL);
    u8* quant=get_ram_ptr(cpu,cpu->gpr[5],8,NULL);
    u32 ea=cpu->gpr[10]+8u;
    u8* output=get_ram_ptr(cpu,ea,32,NULL);
    if (!coefficients || !quant || !output ||
        !galaxy_zero_disjoint(coefficients,16,cpu,sizeof(*cpu)) ||
        !galaxy_zero_disjoint(quant,8,cpu,sizeof(*cpu)) ||
        !galaxy_zero_disjoint(output,32,cpu,sizeof(*cpu)) ||
        !galaxy_zero_disjoint(output,32,&g_mem_write_journal,sizeof(g_mem_write_journal))) return false;
    if (read_be64(coefficients) || read_be64(coefficients+8)) return false;
    // All original reads precede the first output store. Preserve even unusual
    // quant values through the exact paired multiply and its FPSCR handling.
    cpu->fpr[10]=0.0;cpu->ps1[10]=0.0;
    cpu->fpr[11]=f64_value(convert_to_double(read_be32(quant)));
    cpu->ps1[11]=f64_value(convert_to_double(read_be32(quant+4)));
    cpu->gpr[0]=0;cpu->gpr[8]=0;cpu->pc=0x80452760u;cpu->downcount-=8;
    ppc_ps_mul_op(cpu,10,10,11);
    cpu->gpr[6]=0;cpu->gpr[7]=0;
    cpu->fpr[0]=cpu->fpr[10];cpu->ps1[0]=cpu->fpr[10];
    const u32 value=convert_to_single_ftz(f64_bits(cpu->fpr[0]));
    for(u32 offset=0;offset<32u;offset+=4u) {
        clear_matching_reservation(cpu,ea+offset);
        write_be32(output+offset,value);
    }
    cpu->cr=(cpu->cr&0x0fffffffu)|((2u|((cpu->xer>>31)&1u))<<28);
    cpu->gpr[10]+=32u;cpu->gpr[3]+=16u;cpu->gpr[5]+=32u;
    cpu->pc=0x80452798u;cpu->downcount-=14;
    return true;
}
'''


def get_helper(nonzero_dc=False, kernel=0):
    if kernel not in (0,1):
        raise ValueError('Unknown kernel')
    if kernel==1:
        return get_helper(nonzero_dc).replace('galaxy_zero_', 'galaxy_second_').replace(
            '0x80452760u','0x80452BECu').replace('0x80452798u','0x80452C24u')
    if not nonzero_dc:
        return HELPER
    # Only the first signed16 coefficient is allowed nonzero. Its dequantization
    # at the guarded scale0 is exact; the original paired multiply stays intact.
    return HELPER.replace(
        'if (read_be64(coefficients) || read_be64(coefficients+8)) return false;',
        'if ((read_be64(coefficients) & 0x0000ffffffffffffull) || read_be64(coefficients+8)) return false;'
    ).replace('cpu->fpr[10]=0.0;cpu->ps1[10]=0.0;',
              'cpu->fpr[10]=(f64)(s16)read_be16(coefficients);cpu->ps1[10]=0.0;')


def transform(source, nonzero_dc=False, both_kernels=False):
    if both_kernels and not nonzero_dc:
        raise ValueError('Both-kernel experiment requires signed DC mode')
    if hashlib.sha256(source.encode()).hexdigest()!=SOURCE_SHA:
        raise ValueError('Unexpected extracted kernel identity')
    signature='static __attribute__((noinline, flatten)) bool thp_kernel_0('
    label='\nlabel_80452750:\n'
    assert source.count(label)==2
    changed=source.replace(label,label+'    if (galaxy_zero_column(ctx)) goto label_804527A4;\n',1)
    helpers=get_helper(nonzero_dc)
    if both_kernels:
        second='\nlabel_80452BDC:\n'
        assert changed.count(second)==2
        changed=changed.replace(second,second+'    if (galaxy_second_column(ctx)) goto label_80452C30;\n',1)
        helpers+='\n'+get_helper(nonzero_dc,kernel=1)
    return changed.replace(signature,helpers+'\n'+signature,1)
