#!/usr/bin/env python3
"""Prepare, then explicitly execute, a private full-core Mixer-layout experiment.

No canonical edits, installs, module builds, or shared archive replacements.
Preparation does not run CMake or compile. Execution requires final copied
Mixer.cpp/Mixer.h/AudioTempo.h and rebuilds a new core graph with a VFS overlay.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT/'generated/build/ios-simulator-core'
HOST = ROOT/'generated/build/ios-simulator-pause-toggle-app'
PACKAGE = ROOT/'generated/ios/iphonesimulator/libs/libGalaxyPadCore.a'
MODULE = ROOT/'generated/build/ios-simulator-pgo-use-20260912/gRMGE01_recomp.dylib'
MIXDIR = ROOT/'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon'
HOST_SHA = 'b3edb1647b350bc35256f8fba8c2e63878b842b7b5111b8df0864c7eb2018d43'
MODULE_SHA = '90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'


def require(ok, reason):
    if not ok:
        raise SystemExit(reason)


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, indent=2)+'\n')


def cache_values():
    return {m[1]:m[2] for line in (CORE/'CMakeCache.txt').read_text().splitlines()
            if (m:=re.match(r'^([A-Za-z_][A-Za-z_0-9]*):[^=]+=(.*)$',line))}


def commands(build, target):
    return [shlex.split(line) for line in subprocess.check_output(
        ['ninja','-C',str(build),'-t','commands',target],text=True).splitlines()]


def mixer_dependents(build):
    deps=[]
    active=None
    proc=subprocess.Popen(['ninja','-C',str(build),'-t','deps'],stdout=subprocess.PIPE,text=True)
    for line in proc.stdout:
        if line and not line[0].isspace():
            active=line.split(': #deps ',1)[0] if ': #deps ' in line else None
        elif active and line.strip()==str(MIXDIR/'Mixer.h'):
            deps.append(active)
    require(proc.wait()==0,'Ninja dependency inventory failed')
    return sorted(set(deps))


def package_archives():
    # Parse the established provision script's two explicit archive lists;
    # do not execute that script, which would overwrite the shared package.
    text=(ROOT/'scripts/provision-ios-simulator-core.sh').read_text()
    groups=re.findall(r'for relative in \\\n(.*?); do\n  libs\+=\("\$(core|external)/\$relative"\)',text,re.S)
    require(len(groups)==2,'Provision archive lists changed; audit before execution')
    result=[CORE/'libmoderngekko.a']
    for body,kind in groups:
        prefix=CORE/'vendor/dolphin'/('Source/Core' if kind=='core' else 'Externals')
        result.extend(prefix/x for x in shlex.split(body.replace('\\\n',' ')))
    require(all(p.is_file() for p in result),'Control package archive missing')
    return result


def logged(argv, cwd, log):
    with log.open('w') as f:
        p=subprocess.Popen(argv,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in p.stdout:
            f.write(line);f.flush();print(line,end='',flush=True)
        require(p.wait()==0,'Command failed: '+str(log))


def verify_control(plan):
    require(sha(HOST/'GalaxyPad.app/GalaxyPad')==HOST_SHA,'Control host changed')
    require(sha(MODULE)==MODULE_SHA,'Control old-PGO module changed')
    for p,digest in plan['control_hashes'].items():
        require(sha(p)==digest,'Control input changed: '+p)
    for row in plan['source_stamps']:
        stat=Path(row['path']).stat()
        require((stat.st_size,stat.st_mtime_ns)==(row['bytes'],row['mtime_ns']),
                'Source changed since preparation: '+row['path'])


def validate_compile_commands(control, actual, newcore, overlay):
    # A source may be compiled by several targets. Preserve its output identity
    # and working directory rather than collapsing the database by source path.
    def index(rows, relocate):
        result={}
        for row in rows:
            move=lambda value: value.replace(str(CORE),str(newcore)) if relocate else value
            command=[move(x) for x in shlex.split(row['command'])]
            require(command.count('-o')==1,'Missing or ambiguous compile output')
            output=command[command.index('-o')+1]
            key=(move(row['directory']),move(row['file']),output)
            require(key not in result,'Repeated compile target identity: '+str(key))
            result[key]=command
        return result
    expected=index(control,True)
    observed=index(actual,False)
    require(expected.keys()==observed.keys(),
            'Core target set changed: missing='+str(sorted(expected.keys()-observed.keys())[:3])+
            ' extra='+str(sorted(observed.keys()-expected.keys())[:3]))
    repeated=0
    sdl=ROOT/'ref/ModernGekko/vendor/dolphin/Externals/SDL/SDL'
    for key,wanted in expected.items():
        command=observed[key][:]
        source=Path(key[1])
        # SDL CMakeLists.txt appends CMAKE_C_FLAGS to CMAKE_OBJC_FLAGS.
        # Both deliberately carry the same overlay; all other arguments must
        # still match exactly, in order, for each target separately.
        count=2 if sdl in source.parents and source.suffix=='.m' else 1
        require(command.count('-ivfsoverlay')==count,'Unexpected VFS overlay count: '+str(key))
        for _ in range(count):
            ix=command.index('-ivfsoverlay')
            require(ix+1<len(command) and command[ix+1]==str(overlay),'Wrong VFS overlay: '+str(key))
            del command[ix:ix+2]
        require(command==wanted,'Unexpected core compiler-policy difference: '+str(key))
        repeated+=count==2
    return {'entries':len(expected),'unique_sources':len({k[1] for k in expected}),
            'sdl_objc_repeated_overlay_entries':repeated}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--mixer-cpp',type=Path)
    p.add_argument('--mixer-h',type=Path)
    p.add_argument('--tempo-header',type=Path)
    p.add_argument('--jobs',type=int,default=4)
    args=p.parse_args();out=args.output.resolve()
    require(ROOT/'generated/build' in out.parents,'Use a new isolated generated/build directory')
    require(out!=CORE and out!=HOST,'Cannot use control directories')
    require(1<=args.jobs<=16,'jobs must be1..16')
    planfile=out/'recipe.json'
    if not args.execute:
        require(not out.exists(),'Output exists; preserve prior recipe')
        require(sha(HOST/'GalaxyPad.app/GalaxyPad')==HOST_SHA,'Control host hash changed')
        require(sha(MODULE)==MODULE_SHA,'Control module hash changed')
        cache=cache_values();rows=json.loads((CORE/'compile_commands.json').read_text())
        hostcmds=commands(HOST,'GalaxyPad.app/GalaxyPad')
        link=hostcmds[-1]
        require(link[:2]==[':','&&'] and link[-2:]==['&&',':'],'Unexpected host link wrappers')
        link=link[2:-2];require(link.count(str(PACKAGE))==1,'Unexpected host core package')
        hdeps=mixer_dependents(HOST);cdeps=mixer_dependents(CORE)
        require(hdeps and cdeps,'Mixer dependency inventory is incomplete')
        host_compile=[]
        for cmd in hostcmds:
            if '-c' not in cmd or '-o' not in cmd:continue
            if cmd[cmd.index('-o')+1] in hdeps:
                host_compile.append(cmd)
        require(len(host_compile)==len(hdeps),'Missing dependent host compiler command')
        archives=package_archives()
        # These keys reproduce the original core setup; all generated compiler
        # commands are checked against control after configuration as well.
        keys=['CMAKE_TOOLCHAIN_FILE','CMAKE_BUILD_TYPE','CMAKE_EXPORT_COMPILE_COMMANDS',
              'USE_SYSTEM_FMT','USE_SYSTEM_LZ4','USE_SYSTEM_ZSTD','ENABLE_QT',
              'ENABLE_TESTS','BUILD_TESTING','MODERNGEKKO_ENABLE_DOLPHIN_TESTS',
              'ENABLE_CUBEB','ENABLE_VULKAN','HAVE_PIPE2']
        configure=['cmake','-S',cache['CMAKE_HOME_DIRECTORY'],'-B',str(out/'core'),'-G','Ninja']
        configure += ['-D'+k+'='+cache[k] for k in keys]
        tracked={CORE/'CMakeCache.txt',CORE/'compile_commands.json',PACKAGE,
                 ROOT/'scripts/provision-ios-simulator-core.sh',
                 ROOT/'scripts/ios-simulator-toolchain.cmake',MIXDIR/'Mixer.cpp',MIXDIR/'Mixer.h'}
        tracked.update(archives)
        for cmd in host_compile:tracked.add(Path(cmd[cmd.index('-c')+1]))
        sourcefiles={Path(r['file']) for r in rows if Path(r['file']).is_file()}
        stamps=[{'path':str(f),'bytes':f.stat().st_size,'mtime_ns':f.stat().st_mtime_ns}
                for f in sorted(sourcefiles)]
        plan={'status':'prepared; no configuration or build executed','core_configure':configure,
              'baseline_host_sha256':HOST_SHA,'unchanged_module_sha256':MODULE_SHA,
              'language_flags':{lang:cache['CMAKE_'+lang+'_FLAGS'] for lang in ['C','CXX','OBJC','OBJCXX']},
              'control_compile_commands':rows,'core_mixer_dependents':cdeps,
              'host_mixer_dependents':hdeps,'host_compile_commands':host_compile,
              'host_link_command':link,'package_archives':[str(x) for x in archives],
              'control_hashes':{str(x):sha(x) for x in sorted(tracked)},'source_stamps':stamps,
              'required_future_inputs':['copied Mixer.cpp','copied Mixer.h','AudioTempo.h'],
              'scope':'New full core graph; overlay in all languages; rebuild host Mixer.h consumers; unchanged old-PGO module'}
        out.mkdir(parents=True);dump(planfile,plan)
        print(f'Prepared {len(rows)} core compile entries; {len(cdeps)} known core Mixer.h dependents; {len(hdeps)} host dependents; {len(archives)} archives.')
        print('No configure/build. Execute after candidate validation with --execute --mixer-cpp PATH --mixer-h PATH --tempo-header PATH.')
        return
    require(planfile.is_file(),'Prepare recipe first')
    require(all(v and v.is_file() for v in [args.mixer_cpp,args.mixer_h,args.tempo_header]),
            'Provide all three final copied source/header inputs')
    plan=json.loads(planfile.read_text());verify_control(plan)
    require(not (out/'core').exists(), 'Core build directory already exists; use a fresh prepared recipe to avoid stale-layout objects')
    inputs=out/'inputs';inputs.mkdir(exist_ok=True)
    mapping=[]
    for supplied,virtual in [(args.mixer_cpp,MIXDIR/'Mixer.cpp'),(args.mixer_h,MIXDIR/'Mixer.h'),
                             (args.tempo_header,MIXDIR/'AudioTempo.h')]:
        target=inputs/virtual.name
        if target.exists():require(sha(target)==sha(supplied),'Previously staged candidate input differs')
        else:shutil.copyfile(supplied,target)
        mapping.append({'type':'file','name':str(virtual),'external-contents':str(target)})
    overlay=out/'overlay.json'
    dump(overlay,{'version':0,'case-sensitive':'true','use-external-names':False,'roots':mapping})
    plan['candidate_input_hashes']={str(inputs/x):sha(inputs/x) for x in ['Mixer.cpp','Mixer.h','AudioTempo.h']}
    dump(planfile,plan)
    newcore=out/'core'
    configure=plan['core_configure'][:]
    for lang,oldflags in plan['language_flags'].items():
        flags=shlex.join(shlex.split(oldflags)+['-ivfsoverlay',str(overlay)])
        configure.append('-DCMAKE_'+lang+'_FLAGS='+flags)
    logged(configure,ROOT,out/'configure.log')
    actual=json.loads((newcore/'compile_commands.json').read_text())
    plan['compiler_validation']=validate_compile_commands(
        plan['control_compile_commands'],actual,newcore,overlay)
    plan['compiler_commands_validated']=True;dump(planfile,plan)
    logged(['cmake','--build',str(newcore),'--target','moderngekko','--parallel',str(args.jobs)],ROOT,out/'core-build.log')
    for dep in plan['core_mixer_dependents']:
        require((newcore/dep).is_file(),'Missing rebuilt Mixer.h dependent: '+dep)
    runtime=newcore/'CMakeFiles/moderngekko.dir/src/runtime/dolphin_runtime.cpp.o'
    logged(['xcrun','vtool','-show-build',str(runtime)],ROOT,out/'runtime-platform.log')
    require('platform IOSSIMULATOR' in (out/'runtime-platform.log').read_text(),'Wrong core platform')
    private=out/'libGalaxyPadCore.a'
    newarchives=[x.replace(str(CORE),str(newcore)) for x in plan['package_archives']]
    require(all(Path(x).is_file() for x in newarchives),'New core archive set incomplete')
    logged(['xcrun','libtool','-static','-o',str(private),*newarchives],ROOT,out/'package.log')
    logged(['xcrun','lipo',str(private),'-verify_arch','arm64'],ROOT,out/'package-architecture.log')
    replacements={};objdir=out/'host-objects';objdir.mkdir(exist_ok=True)
    for cmd in plan['host_compile_commands']:
        command=[x.replace(str(CORE),str(newcore)) for x in cmd]
        oldobject=command[command.index('-o')+1];newobject=objdir/Path(oldobject).name
        for flag in ['-MT','-MF']:
            if flag in command:
                ix=command.index(flag);del command[ix:ix+2]
        if '-MD' in command:command.remove('-MD')
        command[command.index('-o')+1]=str(newobject)
        command+=['-ivfsoverlay',str(overlay)]
        logged(command,HOST,out/(newobject.name+'.log'))
        replacements[oldobject]=str(newobject)
    app=out/'GalaxyPad.app';require(not app.exists(),'Candidate app already exists; preserve it')
    shutil.copytree(HOST/'GalaxyPad.app',app,symlinks=True)
    link=[replacements.get(x,x) for x in plan['host_link_command']]
    link[link.index(str(PACKAGE))]=str(private)
    link[link.index('-o')+1]=str(app/'GalaxyPad')
    link.insert(1,'-Wl,-map,'+str(out/'host-link.map'))
    logged(link,HOST,out/'host-link.log')
    logged(['codesign','--force','--sign','-',str(app)],ROOT,out/'sign.log')
    logged(['codesign','--verify','--deep','--strict',str(app)],ROOT,out/'sign-verify.log')
    verify_control(plan)
    for path,digest in plan['candidate_input_hashes'].items():require(sha(path)==digest,'Frozen candidate input changed')
    plan.update(status='built; not installed or selected',private_core_sha256=sha(private),
                candidate_host_sha256=sha(app/'GalaxyPad'),host_link_command_executed=link)
    dump(planfile,plan);print(plan['candidate_host_sha256'],app)


if __name__=='__main__':main()
