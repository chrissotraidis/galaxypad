#!/usr/bin/env python3
"""Isolated 119-site decoder experiment; reuses accepted unchanged objects.

Never runs Ninja builds, edits vendor sources, or changes module selection.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', ROOT/'scripts/audit-fprf-regions.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def extract(text, signature):
    start = text.index(signature)
    brace = text.index('{', start)
    end, depth = brace + 1, 1
    while depth:
        depth += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[start:end]

def main():
    accepted = Path((ROOT/'generated/modules/RMGE01/active-module.txt').read_text().strip())
    expected = '9098890e25b36e802ab5f793c9ad7800f991190f41e972996937343d84ecc9de'
    assert sha(accepted) == expected
    generated = (accepted.parent/'dolrecomp-output').resolve()
    build = generated.parent/'module-build'
    assert sha(build/'gRMGE01_recomp.dylib') == expected
    experiment = ROOT/'generated/fprf-r167'
    experiment.mkdir(exist_ok=True)
    output = experiment/'gRMGE01_recomp.dylib'
    assert not output.exists(), 'Do not overwrite an existing candidate'
    chunk = generated/'RMGE01_generated/chunks/chunk_1102_text1_804520A0.c'
    core = ROOT/'ref/ModernGekko/vendor/dolphin/GXRuntime/src/core'
    floats = core/'cpu_interpreter_float.c'
    assert sha(chunk) == '2dc3b915db7bd33c84a0481499fefd0ee91a201bc20cb6540248caf06729d539'
    assert sha(floats) == '3026eb10f63667a85dccb6e1fc7df1d2c299058cd636cae6b2c0ca7b02a4806c'
    profile = ROOT/'generated/pgo/rmge01.profdata'
    assert sha(profile) == 'f39a3cedeb6c49f35c411356893c619dc347eb1b0bb5986687f25cf81e7d460d'
    original = chunk.read_text()
    eligible = audit.regions(original)
    assert len(eligible) == 119
    changed = original
    for address in eligible:
        start = changed.index(f'label_{address:08X}:\n')
        end = changed.index('\nlabel_', start)
        body, count = re.subn(r'ppc_ps_(add|sub|mul|madd)_op\(', r'galaxypad_deferred_\1(', changed[start:end])
        assert count == 1
        changed = changed[:start]+body+changed[end:]
    assert sum(changed.count('galaxypad_deferred_'+op+'(') for op in ('add','sub','mul','madd')) == 119
    assert re.sub(r'galaxypad_deferred_(add|sub|mul|madd)\(', r'ppc_ps_\1_op(', changed) == original
    declarations, helpers = [], []
    for op in ('add', 'sub', 'mul', 'madd'):
        signature = 'void ppc_ps_'+op+'_op('
        body = extract(floats.read_text(), signature)
        write = '    set_fprf(cpu, classify_f32(ps0));'
        assert body.count(write) == 1
        helper = body.replace(signature, 'void galaxypad_deferred_'+op+'(').replace(write, '')
        helpers.append(helper)
        declarations.append(helper.split('{', 1)[0].strip()+';')
    include = '#include "../RMGE01.h"'
    assert changed.count(include) == 1
    changed = changed.replace(include, '#include "'+str(generated/'RMGE01_generated/RMGE01.h')+'"\n'+'\n'.join(declarations))
    new_chunk = experiment/chunk.name
    new_float = experiment/floats.name
    new_chunk.write_text(changed)
    new_float.write_text(floats.read_text()+'\n'+'\n'.join(helpers)+'\n')

    # Read the actual accepted build graph, not reconstructed optimization flags.
    graph = (build/'build.ninja').read_text()
    blocks = re.findall(r'^build ([^\n]+)\n((?:  [^\n]*\n)*)', graph, re.M)
    parsed = []
    for header, variables in blocks:
        target, rule_inputs = header.split(': ', 1)
        rule, _, inputs = rule_inputs.partition(' ')
        fields = dict(re.findall(r'^  (\w+) = (.*)$', variables, re.M))
        parsed.append((target, rule, inputs, fields))
    replacements, commands = {}, []
    for source, candidate in ((chunk, new_chunk), (floats, new_float)):
        matches = [row for row in parsed if row[1].startswith('C_COMPILER_')
                   and row[2].split(' || ')[0] == str(source)]
        assert len(matches) == 1, str(source)
        target, _, _, fields = matches[0]
        flags = shlex.split(fields['DEFINES']+' '+fields['INCLUDES']+' '+fields['FLAGS'])
        assert '-O2' == [flag for flag in flags if re.fullmatch('-O[0-3sz]', flag)][-1]
        assert '-ffp-contract=off' in flags and '-fno-fast-math' in flags and '-flto=thin' in flags
        obj = experiment/(candidate.name+'.o')
        command = ['/usr/bin/clang',*flags,'-I',str(core),'-c',str(candidate),'-o',str(obj)]
        commands.append(command)
        replacements[target] = str(obj)
    links = [row for row in parsed if row[0] == 'gRMGE01_recomp.dylib']
    assert len(links) == 1
    _, _, inputs, fields = links[0]
    objects = shlex.split(inputs.split(' | ')[0])
    assert len(objects) == 1329, len(objects)  # 1322 chunks + 7 runtime/export units.
    assert sum('/chunks/chunk_' in obj for obj in objects) == 1322
    identities = {}
    for obj in objects:
        path = build/obj
        assert path.is_file() and path.stat().st_mtime_ns <= (build/'gRMGE01_recomp.dylib').stat().st_mtime_ns
        identities[obj] = sha(path)
    assert set(replacements).issubset(objects)
    response = experiment/'objects.rsp'
    response.write_text('\n'.join(shlex.quote(replacements.get(obj, str(build/obj))) for obj in objects)+'\n'+fields['LINK_LIBRARIES']+'\n')
    assert fields['PRE_LINK'] == fields['POST_BUILD'] == ':'
    link = ['/usr/bin/clang',*shlex.split(fields['LANGUAGE_COMPILE_FLAGS']+' '+fields['ARCH_FLAGS']+' '+fields['LINK_FLAGS']),
            '-o',str(output),fields['SONAME_FLAG'],fields['INSTALLNAME_DIR']+fields['SONAME'],'@'+str(response)]
    commands.append(link)
    (experiment/'build-provenance.json').write_text(json.dumps({
        'accepted_sha256':expected,'selected':False,'sites':eligible,
        'chunk_sha256':sha(new_chunk),'float_sha256':sha(new_float),
        'accepted_objects_sha256':identities,'commands':commands},indent=2)+'\n')
    manifest = (accepted.parent/'manifest.txt').read_text().replace('module_sources_fnv1a=', 'reference_module_sources_fnv1a=')
    (experiment/'manifest.txt').write_text(manifest+'experiment=fprf-r167\nselected=false\nsource_overlay=build-provenance.json\n')
    reference_link = experiment/'dolrecomp-output'
    if not reference_link.exists(): reference_link.symlink_to(generated, target_is_directory=True)
    assert reference_link.resolve() == generated
    for command in commands:
        print('Compile '+Path(command[-3]).name if '-c' in command else 'Link candidate (unchanged objects reused)', flush=True)
        subprocess.run(command,cwd=build,check=True)
    assert sha(accepted) == expected
    subprocess.run([str(ROOT/'scripts/audit-module.sh'),str(output)],check=True)
    print('Candidate only: '+str(output)+' SHA256='+sha(output),flush=True)

if __name__ == '__main__':
    main()
