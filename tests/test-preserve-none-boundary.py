#!/usr/bin/env python3
"""Stress the optional calling convention across a real dylib boundary.

Uses the production CPUState/descriptor headers. This is an ABI test, not guest
execution or a throughput benchmark. The actual generated chunk is exercised
separately by test-preserve-none-experiment.py.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
runtime = root/'ref/ModernGekko/vendor/dolphin/GXRuntime/include'
abi = root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/PowerPC/StaticRecomp'
shared = r'''
#include "StaticRecompABI.h"
#if !defined(__aarch64__) || !defined(__clang__) || !__has_attribute(preserve_none)
#error "requires AArch64 Clang preserve_none"
#endif
typedef __attribute__((preserve_none)) int (*PreserveNoneDispatchV1)(CPUState*, u32);
#define FAST_SYMBOL "galaxypad_dispatch_preserve_none_v1"
'''
library = r'''
#include "shared.h"
static inline __attribute__((always_inline)) int exercise(CPUState* cpu, u32 address)
{
    cpu->pc = address;
    cpu->gpr[3] += address;
    cpu->downcount -= 7;
    if (cpu->external_write)
        cpu->external_write(cpu, address, cpu->gpr[3], 4);
    // Legal clobbers for preserve_none. The normal ABI entry must preserve
    // these registers, while the optional entry's caller must handle them.
    __asm__ volatile(
        "mov x19, #19\n mov x20, #20\n mov x21, #21\n mov x22, #22\n"
        "mov x23, #23\n mov x24, #24\n mov x25, #25\n mov x26, #26\n"
        "mov x27, #27\n mov x28, #28\n"
        "movi v8.16b, #0\n movi v9.16b, #0\n movi v10.16b, #0\n movi v11.16b, #0\n"
        "movi v12.16b, #0\n movi v13.16b, #0\n movi v14.16b, #0\n movi v15.16b, #0\n"
        ::: "x19","x20","x21","x22","x23","x24","x25","x26","x27","x28",
            "v8","v9","v10","v11","v12","v13","v14","v15");
    return (address & 1) == 0;
}
static int normal_dispatch(CPUState* cpu, u32 address) { return exercise(cpu,address); }
__attribute__((visibility("default"),preserve_none)) int
galaxypad_dispatch_preserve_none_v1(CPUState* cpu, u32 address) { return exercise(cpu,address); }
static const StaticRecompModuleDesc descriptor = {
    .abi_version=STATICRECOMP_ABI_VERSION, .cpu_abi_version=GXRUNTIME_CPU_ABI_VERSION,
    .cpu_state_size=sizeof(CPUState), .game_id="TEST", .dispatch=normal_dispatch
};
__attribute__((visibility("default"))) const StaticRecompModuleDesc*
staticrecomp_get_module(void) { return &descriptor; }
'''
host = r'''
#include "shared.h"
#include <cassert>
#include <cstring>
#include <cstdio>
#include <dlfcn.h>
struct Trace { u64 hash=0; u32 count=0; };
extern "C" void callback(CPUState* c, u32 address, u64 value, u8 width) {
    auto* t=static_cast<Trace*>(c->external_user_data);
    t->hash=t->hash*131+address+value+width+c->pc+c->downcount;
    ++t->count;
    c->gpr[29]^=static_cast<u32>(value);
    c->reserve_valid=!c->reserve_valid;
}
static u32 seed=0x17123;
static u32 random32() { seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed; }
int main(int argc, char** argv) {
    assert(argc==2);
    void* handle=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
    if(!handle) { std::fprintf(stderr,"%s\n",dlerror());return 1; }
    auto get=reinterpret_cast<StaticRecompGetModuleFn>(dlsym(handle,STATICRECOMP_GET_MODULE_SYMBOL));
    assert(get);
    const auto* descriptor=get();
    assert(descriptor->abi_version==STATICRECOMP_ABI_VERSION);
    assert(descriptor->cpu_abi_version==GXRUNTIME_CPU_ABI_VERSION);
    assert(descriptor->cpu_state_size==sizeof(CPUState));
    const auto fast=reinterpret_cast<PreserveNoneDispatchV1>(dlsym(handle,FAST_SYMBOL));
    const auto missing=reinterpret_cast<PreserveNoneDispatchV1>(dlsym(handle,"galaxypad_absent_test_symbol"));
    assert(fast && !missing);
    for(u32 i=0;i<50000;++i) {
        CPUState a={},b;
        for(auto& v:a.gpr)v=random32();
        for(auto& v:a.fpr) {u64 bits=(u64(random32())<<32)|random32();std::memcpy(&v,&bits,8);}
        a.downcount=static_cast<int>(random32()%1000)-500;
        a.cr=random32();a.xer=random32();a.reserve_valid=i&1;
        a.external_write=i%3?callback:nullptr;
        Trace x,y;a.external_user_data=&x;b=a;b.external_user_data=&y;
        const u32 address=random32();
        const int expected=descriptor->dispatch(&a,address);
        const auto selected=i&1?fast:missing;
        const int result=selected?selected(&b,address):descriptor->dispatch(&b,address);
        assert(result==expected && x.count==y.count && x.hash==y.hash);
        b.external_user_data=a.external_user_data;
        assert(std::memcmp(&a,&b,sizeof(a))==0);
    }
    dlclose(handle);
    std::puts("50000 dynamic ABI cases pass: normal fallback, optional symbol, integer/FP clobbers, callbacks");
}
'''

with tempfile.TemporaryDirectory(prefix='galaxypad-preserve-none-boundary-') as temporary:
    output=Path(temporary)
    (output/'shared.h').write_text(shared)
    (output/'library.c').write_text(library)
    (output/'host.cpp').write_text(host)
    includes=['-I'+str(runtime),'-I'+str(abi),'-I'+str(output)]
    checks=['-Werror=attributes','-Werror=incompatible-function-pointer-types']
    for name,flags in [('optimized',['-O2']),('ubsan',['-O1','-fsanitize=undefined'])]:
        dylib=output/(name+'.dylib');binary=output/(name+'-host')
        subprocess.run(['clang',*includes,*checks,*flags,'-std=gnu11','-dynamiclib',
                        str(output/'library.c'),'-o',str(dylib)],check=True)
        subprocess.run(['clang++',*includes,*checks,*flags,'-std=c++23',
                        str(output/'host.cpp'),'-o',str(binary)],check=True)
        subprocess.run([str(binary),str(dylib)],check=True,timeout=30)
    for sdk,target in [('iphonesimulator','arm64-apple-ios16.0-simulator'),
                       ('iphoneos','arm64-apple-ios16.0')]:
        sdkpath=subprocess.check_output(['xcrun','--sdk',sdk,'--show-sdk-path'],text=True).strip()
        for language,source in [('clang','library.c'),('clang++','host.cpp')]:
            subprocess.run([language,*includes,*checks,'-O2','-target',target,
                            '-isysroot',sdkpath,'-std='+('gnu11' if language=='clang' else 'c++23'),
                            '-c',str(output/source),'-o',str(output/(sdk+'-'+source+'.o'))],check=True)
print('Optional preserve_none dynamic boundary and both Apple target object compilations pass')
