"""Isolated single-object experiments from the verified accepted graph; never selects them.

First relink unchanged objects and require the accepted binary hash. Only then
compile the changed chunk and link the candidate. All writes stay in generated.
"""
import hashlib
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess

from zero_dc_column import transform

ROOT=Path(__file__).resolve().parents[1]
ACCEPTED_SHA='1180447313459c4c153ca74e5215811e88a9b69a00d15feff940f062148fc631'
CHUNK_SHA='fa455a7ae795c5428ce66c56d745416d2c5d9815ac32db14da571428b3661bae'
PROFILE_SHA='f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_graph(graph):
    rows=[]
    for header,variables in re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)',graph,re.M):
        target,rest=header.split(': ',1)
        rule,_,inputs=rest.partition(' ')
        rows.append((target,rule,inputs,dict(re.findall(r'^  (\w+) = (.*)$',variables,re.M))))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--huffman-no-profile', action='store_true',
                        help='Compile unchanged chunk1103 without its saved PGO flag; reuse verified control')
    parser.add_argument('--outline-add-nan', action='store_true',
                        help='Outline only ni_add NaN handling in the float TU; reuse verified control')
    parser.add_argument('--s16-load', action='store_true',
                        help='Specialize16 coefficient-load calls only; reuse verified control')
    parser.add_argument('--s16-pair', action='store_true',
                        help='Checked four-byte coefficient pairs on the accepted store-scale baseline')
    parser.add_argument('--two-range', action='store_true',
                        help='Specialize only module-export lookup; reuse verified control')
    parser.add_argument('--dead-pc', action='store_true',
                        help='Avoid95 unobserved PC stores on the current two-range baseline')
    parser.add_argument('--psq-scale', action='store_true',
                        help='Exact quantized-store power-of-two factor on current baseline')
    args=parser.parse_args()
    assert sum((args.huffman_no_profile,args.outline_add_nan,args.s16_load,args.s16_pair,args.two_range,args.dead_pc,args.psq_scale))<=1
    accepted_digest = ('c0021b9f2fad3acc3746b6a582b46935e2f7b60bc38434ad7d485564957c7939' if args.s16_pair else
                       '5499889a558e44197bb740b3b3c5cc96187bcd80e3a8df097b814cb2703692e1'
                       if args.dead_pc or args.psq_scale else ACCEPTED_SHA)
    marker=ROOT/'generated/modules/RMGE01/active-module.txt'
    marker_bytes=marker.read_bytes()
    accepted=Path(marker_bytes.decode().strip())
    assert accepted.is_absolute() and sha(accepted)==accepted_digest
    build=accepted.parent/'module-build'
    assert sha(build/'gRMGE01_recomp.dylib')==accepted_digest
    generated=accepted.parent/'dolrecomp-output/RMGE01_generated'
    expected_header = ('da2def2ce566f57929afe0a8a2f7de5539b17624eb37452d6928790ac6999336'
                       if args.dead_pc or args.psq_scale or args.s16_pair else '2cf2a7c3752cd6ab93f7c41140aaa2f3c1ae477cca6587925d6a5b51c3d683b9')
    assert sha(generated/'RMGE01.h')==expected_header
    if args.psq_scale:
        from psq_scale import transform as specialize_scale
        chunk=ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu.c'
        changed=specialize_scale(chunk.read_text())
    elif args.two_range:
        from two_range_lookup import transform as specialize_lookup
        chunk=ROOT/'ref/ModernGekko/vendor/dolphin/module-template/module_export.c'
        assert sha(chunk)=='1e3efee3cf6384a245da1f03a4163098fcb68e7acf615fa86f566d34fc7efd41'
        changed=specialize_lookup((generated/'RMGE01.h').read_text())
    elif args.outline_add_nan:
        from outline_add_nan import transform as outline_nan
        chunk=ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core/cpu_interpreter_float.c'
        changed=outline_nan(chunk.read_text())
        # Preserve quote-include resolution when relocating the private TU.
        include='#include "cpu_interpreter_private.h"'
        assert changed.count(include)==1
        changed=changed.replace(include,'#include "'+str(chunk.parent/'cpu_interpreter_private.h')+'"',1)
    elif args.huffman_no_profile:
        chunk=generated/'chunks/chunk_1103_text1_804530A0.c'
        assert sha(chunk)=='e6aa915816ee2a89534f75c4d59dd0c145f7a5d0162c3e1a15b2ebe33b996dcc'
    else:
        chunk=generated/'chunks/chunk_1102_text1_804520A0.c'
        assert sha(chunk)==CHUNK_SHA
        fixture=ROOT/'generated/thp-kernels-r198-exits/candidate.c'
        normalize=lambda text: re.sub(r'(?m)^#include ".*RMGE01.h"$', '#include "../RMGE01.h"',text)
        assert normalize(fixture.read_text())==chunk.read_text()
        if args.s16_pair:
            from s16_pair_psq_load import transform as specialize_pair
            changed=normalize(specialize_pair(fixture.read_text()))
        elif args.dead_pc:
            from thp_dead_pc import transform as specialize_pc
            changed=normalize(specialize_pc(fixture.read_text()))
        elif args.s16_load:
            from s16_psq_load import transform as specialize_s16
            changed=normalize(specialize_s16(fixture.read_text()))
        else:
            changed=normalize(transform(fixture.read_text(),nonzero_dc=True,both_kernels=True))
        changed=changed.replace('#include "../RMGE01.h"', '#include "'+str(generated/'RMGE01.h')+'"',1)
    profile=ROOT/'generated/pgo/rmge01.profdata'
    assert sha(profile)==PROFILE_SHA
    core=ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime'
    if args.s16_pair:
        assert sha(core/'src/core/cpu.c')=='05e221c01bead6801c51217f84398bd10f22e1b810f6d06977e04d8a801436ea'
    assert sha(core/'include/core/cpu.h')=='7fc1448116c581afc53f2c41c6e3b3d11b3a580c5e71147cb52fca493e0d4657'
    assert sha(core/'src/core/cpu_interpreter_float.c')=='554149a2e7d08783402af38e5a2b898aff476370b0e3a6af0ed4bd411aab934f'
    graph=build/'build.ninja'
    rows=parse_graph(graph.read_text())
    matches=[r for r in rows if r[1].startswith('C_COMPILER_') and r[2].split(' || ')[0]==str(chunk)]
    assert len(matches)==1
    target,_,_,compile_fields=matches[0]
    flags=shlex.split(' '.join(compile_fields[x] for x in ('DEFINES','INCLUDES','FLAGS')))
    assert [x for x in flags if re.fullmatch('-O[0-3sz]',x)][-1]=='-O2'
    assert all(x in flags for x in ('-flto=thin','-ffp-contract=off','-fno-fast-math','-mmacosx-version-min=14.0'))
    assert '-fprofile-instr-use='+str(profile) in flags
    original_flags=list(flags)
    if args.huffman_no_profile:
        flags.remove('-fprofile-instr-use='+str(profile))
        assert len(flags)==len(original_flags)-1
    links=[r for r in rows if r[0]=='gRMGE01_recomp.dylib']
    assert len(links)==1
    _,_,inputs,link_fields=links[0]
    objects=shlex.split(inputs.split(' | ')[0])
    assert len(objects)==1329 and sum('/chunks/chunk_' in x for x in objects)==1322
    assert objects.count(target)==1
    assert link_fields['PRE_LINK']==link_fields['POST_BUILD']==':'
    identities={obj:sha(build/obj) for obj in objects}
    # A fresh directory prevents accidental overwrite or reuse of partial output.
    experiment_name=('s16-pair-r408' if args.s16_pair else 'psq-scale-r381' if args.psq_scale else 'dead-pc-r376' if args.dead_pc else 'two-range-r358' if args.two_range else 's16-load-r346' if args.s16_load else 'add-nan-r334' if args.outline_add_nan else
                     'huffman-no-profile-r324' if args.huffman_no_profile else 'dc-column-r316')
    experiment=ROOT/'generated'/experiment_name
    experiment.mkdir(exist_ok=False)
    control=experiment/'control';control.mkdir()
    candidate=experiment/'candidate';candidate.mkdir()
    if args.two_range:
        (candidate/'RMGE01.h').write_text(changed)
        (candidate/'generated.h').write_text('#include "RMGE01.h"\n')
        flags.insert(0,'-I'+str(candidate))
        assert flags[1:]==original_flags
        new_chunk=chunk  # Keep original source path for static-function PGO names.
    elif args.huffman_no_profile:
        new_chunk=chunk  # Compile the original, unchanged file at its original path.
    else:
        new_chunk=candidate/chunk.name;new_chunk.write_text(changed)
    new_object=candidate/(chunk.name+'.o')
    compiler='/usr/bin/clang'
    version=subprocess.check_output([compiler,'--version'],text=True)
    assert version.splitlines()[0]=='Apple clang version 21.0.0 (clang-2100.1.1.101)'
    def link_command(directory,replacement=None):
        response=directory/'objects.rsp'
        response.write_text('\n'.join(shlex.quote(str(replacement if replacement and obj==target else build/obj))
                                      for obj in objects)+'\n'+link_fields['LINK_LIBRARIES']+'\n')
        return [compiler,*shlex.split(' '.join(link_fields[x] for x in ('LANGUAGE_COMPILE_FLAGS','ARCH_FLAGS','LINK_FLAGS'))),
                '-o',str(directory/'gRMGE01_recomp.dylib'),link_fields['SONAME_FLAG'],
                link_fields['INSTALLNAME_DIR']+link_fields['SONAME'],'@'+str(response)]
    control_link=link_command(control)
    compile_command=[compiler,*flags,'-c',str(new_chunk),'-o',str(new_object)]
    candidate_link=link_command(candidate,new_object)
    provenance={'selected':False,'accepted_sha256':accepted_digest,'graph_sha256':sha(graph),
                'generated_header_sha256':sha(generated/'RMGE01.h'),
                'profile_sha256':PROFILE_SHA,'source_sha256':sha(new_chunk),'compiler':version,
                'objects_sha256':identities,'commands':[control_link,compile_command,candidate_link],
                'original_compile_flags':original_flags,'candidate_compile_flags':flags,
                'policy':('s16-pair-mapping-experimental' if args.s16_pair else 'psq-store-scale-experimental' if args.psq_scale else 'dead-pc-stores-experimental' if args.dead_pc else 'two-range-dispatch-experimental' if args.two_range else 's16-coefficient-load-experimental' if args.s16_load else 'ni-add-nan-outline-experimental' if args.outline_add_nan else
                          'huffman-chunk-no-profile' if args.huffman_no_profile else 'signed-dc-columns-2-experimental')}
    record=experiment/'build-provenance.json'
    if args.two_range:
        provenance['candidate_header_sha256']=sha(candidate/'RMGE01.h')
    record.write_text(json.dumps(provenance,indent=2)+'\n')
    print('Relink unchanged control; candidate gated on exact accepted hash',flush=True)
    if args.huffman_no_profile or args.outline_add_nan or args.s16_load or args.two_range or args.psq_scale:
        previous=ROOT/('generated/dead-pc-r376' if args.psq_scale else 'generated/dc-column-r316')
        prior=json.loads((previous/'build-provenance.json').read_text())
        assert prior['graph_sha256']==sha(graph) and prior['objects_sha256']==identities
        assert prior['compiler']==version and prior['accepted_sha256']==accepted_digest
        cached=previous/'control/gRMGE01_recomp.dylib'
        assert prior['control_sha256']==sha(cached)==accepted_digest
        assert [x.replace(str(previous/'control'),str(control)) for x in prior['commands'][0]]==control_link
        assert (previous/'control/objects.rsp').read_bytes()==(control/'objects.rsp').read_bytes()
        (control/'gRMGE01_recomp.dylib').symlink_to(cached)
        provenance['control_reused_from']=str(cached)
        print('Reused byte-identical control after verifying compiler, graph, all objects, link command and response',flush=True)
    else:
        subprocess.run(control_link,cwd=build,check=True)
    provenance['control_sha256']=sha(control/'gRMGE01_recomp.dylib')
    record.write_text(json.dumps(provenance,indent=2)+'\n')
    assert provenance['control_sha256']==accepted_digest,'Unchanged relink differs; candidate not built'
    print('Control is byte-identical. Compile one changed chunk, then link candidate',flush=True)
    subprocess.run(compile_command,cwd=build,check=True)
    subprocess.run(candidate_link,cwd=build,check=True)
    assert marker.read_bytes()==marker_bytes and sha(accepted)==accepted_digest
    assert all(sha(build/obj)==digest for obj,digest in identities.items())
    manifest=(accepted.parent/'manifest.txt').read_text()
    if not args.huffman_no_profile:
        manifest=manifest.replace('module_sources_fnv1a=','reference_module_sources_fnv1a=')
    (candidate/'manifest.txt').write_text(manifest+'experiment='+experiment_name+'\nselected=false\nbuild_provenance=../build-provenance.json\n')
    (candidate/'dolrecomp-output').symlink_to(accepted.parent/'dolrecomp-output',target_is_directory=True)
    output=candidate/'gRMGE01_recomp.dylib'
    subprocess.run([str(ROOT/'scripts/audit-module.sh'),str(output)],check=True)
    provenance['candidate_sha256']=sha(output)
    record.write_text(json.dumps(provenance,indent=2)+'\n')
    print('Unselected candidate SHA256='+provenance['candidate_sha256'],flush=True)


if __name__=='__main__':
    main()
