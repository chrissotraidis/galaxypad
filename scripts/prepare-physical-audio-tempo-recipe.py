#!/usr/bin/env python3
"""Prepare an isolated physical v8 audio + dual-core build. Never signs or deploys.

Default preparation is read/copy only. --execute is a separate explicit action;
it builds a fresh core graph and all host objects using physical control policy.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shlex
import shutil

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('core_recipe',ROOT/'scripts/prepare-audio-tempo-core-host.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.CORE=ROOT/'generated/build/ios-device-core'
m.HOST=ROOT/'generated/build/ios-device-app'
m.PACKAGE=ROOT/'generated/ios/iphoneos/libs/libGalaxyPadCore.a'
CONTROL_APP=ROOT/'generated/device-stage.JOtjGn/GalaxyPad.app'
m.MODULE=CONTROL_APP/'Frameworks/gRMGE01_recomp.dylib'
m.HOST_SHA='f6396bcdb26a2e6ac23525cfa19b13fa9dbca56ce5ef7ae7e8b0edda737e006c'
m.MODULE_SHA='919b2382ebf37007bf86865f1d2f46ca048bec61b45574797483684a039a047b'
V8=ROOT/'generated/experiments/audio-tempo-integration-v8-20260912'
V8_SHA={'Mixer.cpp':'102a876d8efe784e2c37c4cadae46eadc4479f0776797a8388d16d31215565e1',
'Mixer.h':'4e14a7db9b84f372b65ac660c8653c1f7207f243d36e2bfe9b84b5ed81ee0c27',
'AudioTempo.h':'eff12bf32da6aa3fb6ccf073117f1b0001df1c23e3ef3f5baf21bd1036fbba5a'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--execute',action='store_true')
    p.add_argument('--jobs',type=int,default=4)
    a=p.parse_args();out=a.output.resolve();core=out/'core';planfile=out/'recipe.json'
    m.require(ROOT/'generated/build' in out.parents and out not in [m.CORE,m.HOST],'Use a fresh isolated build directory')
    m.require(1<=a.jobs<=16,'Invalid jobs')
    if not a.execute:
        m.require(not out.exists(),'Preserve existing recipe; use a fresh directory')
        m.require(m.sha(m.HOST/'GalaxyPad.app/GalaxyPad')==m.HOST_SHA,'Physical unsigned control host changed')
        m.require(m.sha(m.MODULE)==m.MODULE_SHA,'Physical signed control module changed')
        for name,digest in V8_SHA.items():m.require(m.sha(V8/name)==digest,'Final v8 source changed: '+name)
        runtime=(ROOT/'ref/ModernGekko/src/runtime/dolphin_runtime.cpp').read_text()
        m.require('Config::SetBase(Config::MAIN_AUDIO_BUFFER_SIZE, 120);' in runtime,'Audio reserve changed')
        host=ROOT/'apple/ios/GalaxyPadCoreHost.mm';hosttext=host.read_text()
        needle='          Config::SetBaseOrCurrent(Config::MAIN_AUDIO_MUTED, initialMute);'
        m.require(hosttext.count(needle)==1 and 'MAIN_CPU_THREAD' not in hosttext,'Audit current host dual-core policy first')
        hosttext=hosttext.replace(needle,needle+'\n          Config::SetCurrent(Config::MAIN_CPU_THREAD, true);')
        mainfile=ROOT/'apple/ios/main.mm';maintext=mainfile.read_text()
        m.require('point at Back and press A to return to gameplay' in maintext,'Latest reviewed main.mm help is missing')
        cmds=m.commands(m.HOST,'GalaxyPad.app/GalaxyPad')
        compilecmds=[c for c in cmds if '-c' in c and '-o' in c]
        m.require(len(compilecmds)==13,'Host source target set changed')
        link=cmds[-1]
        m.require(link[:2]==[':','&&'] and link[-2:]==['&&',':'],'Unexpected link wrapper')
        link=link[2:-2];m.require(link.count(str(m.PACKAGE))==1,'Wrong physical core package')
        rows=json.loads((m.CORE/'compile_commands.json').read_text());cache=m.cache_values()
        m.require(cache['CMAKE_TOOLCHAIN_FILE']==str(ROOT/'scripts/ios-device-toolchain.cmake'),'Wrong core toolchain')
        keys=['CMAKE_TOOLCHAIN_FILE','CMAKE_BUILD_TYPE','CMAKE_EXPORT_COMPILE_COMMANDS','USE_SYSTEM_FMT','USE_SYSTEM_LZ4','USE_SYSTEM_ZSTD','ENABLE_QT','ENABLE_TESTS','BUILD_TESTING','MODERNGEKKO_ENABLE_DOLPHIN_TESTS','ENABLE_CUBEB','ENABLE_VULKAN','HAVE_PIPE2']
        configure=['cmake','-S',cache['CMAKE_HOME_DIRECTORY'],'-B',str(core),'-G','Ninja']+['-D'+k+'='+cache[k] for k in keys]
        archives=m.package_archives();cdeps=m.mixer_dependents(m.CORE)
        m.require(cdeps,'Physical Mixer dependency inventory missing')
        tracked={m.CORE/'CMakeCache.txt',m.CORE/'compile_commands.json',m.PACKAGE,CONTROL_APP/'GalaxyPad',ROOT/'scripts/ios-device-toolchain.cmake',ROOT/'scripts/provision-ios-simulator-core.sh',Path(__file__).resolve(),ROOT/'scripts/prepare-audio-tempo-core-host.py'}|set(archives)
        hostfiles={Path(c[c.index('-c')+1]) for c in compilecmds};tracked|=hostfiles
        sourcefiles={Path(r['file']) for r in rows if Path(r['file']).is_file()}|hostfiles
        out.mkdir(parents=True);inputs=out/'inputs';inputs.mkdir();mapping=[]
        for name in V8_SHA:
            shutil.copyfile(V8/name,inputs/name)
            mapping.append({'type':'file','name':str(m.MIXDIR/name),'external-contents':str(inputs/name)})
        for name,text,virtual in [('GalaxyPadCoreHost.mm',hosttext,host),('main.mm',maintext,mainfile)]:
            (inputs/name).write_text(text)
            mapping.append({'type':'file','name':str(virtual),'external-contents':str(inputs/name)})
        overlay=out/'overlay.json';m.dump(overlay,{'version':0,'case-sensitive':'true','use-external-names':False,'roots':mapping})
        for lang in ['C','CXX','OBJC','OBJCXX']:
            configure.append('-DCMAKE_'+lang+'_FLAGS='+shlex.join(shlex.split(cache['CMAKE_'+lang+'_FLAGS'])+['-ivfsoverlay',str(overlay)]))
        plan={'status':'prepared; no configure/build/sign/install','core_configure':configure,'control_compile_commands':rows,'host_compile_commands':compilecmds,'host_link_command':link,'core_mixer_dependents':cdeps,'package_archives':[str(x) for x in archives],'control_hashes':{str(x):m.sha(x) for x in sorted(tracked)},'source_stamps':[{'path':str(f),'bytes':f.stat().st_size,'mtime_ns':f.stat().st_mtime_ns} for f in sorted(sourcefiles)],'candidate_input_hashes':{str(x):m.sha(x) for x in sorted(inputs.iterdir())},'module_sha256':m.MODULE_SHA,'scope':'Physical full core + all13 host TUs; exact v8 audio, session-only dual core on both Apple targets, latest main.mm pause help;120ms and4:3 default retained. No signing/deployment.'}
        m.dump(planfile,plan)
        print(f'Prepared {len(rows)} physical core entries, {len(cdeps)} Mixer consumers, all{len(compilecmds)} host objects. No configure/build/sign/install.')
        return
    m.require(planfile.is_file(),'Prepare first');plan=json.loads(planfile.read_text());m.verify_control(plan)
    for path,digest in plan['candidate_input_hashes'].items():m.require(m.sha(path)==digest,'Frozen input changed: '+path)
    m.require(not core.exists(),'Use a fresh recipe; never reuse a stale Mixer-layout build')
    m.logged(plan['core_configure'],ROOT,out/'configure.log')
    plan['compiler_validation']=m.validate_compile_commands(plan['control_compile_commands'],json.loads((core/'compile_commands.json').read_text()),core,out/'overlay.json');m.dump(planfile,plan)
    m.logged(['cmake','--build',str(core),'--target','moderngekko','--parallel',str(a.jobs)],ROOT,out/'core-build.log')
    actualdeps=m.mixer_dependents(core)
    m.require(set(plan['core_mixer_dependents'])<=set(actualdeps),'Missing rebuilt physical Mixer dependency')
    for dep in plan['core_mixer_dependents']:
        m.require((core/dep).is_file(),'Missing object: '+dep)
    m.logged(['xcrun','vtool','-show-build',str(core/'CMakeFiles/moderngekko.dir/src/runtime/dolphin_runtime.cpp.o')],ROOT,out/'core-platform.log')
    m.require('platform IOS\n' in (out/'core-platform.log').read_text(),'Wrong physical core platform')
    package=out/'libGalaxyPadCore.a';archives=[x.replace(str(m.CORE),str(core)) for x in plan['package_archives']]
    m.require(all(Path(x).is_file() for x in archives),'Missing rebuilt archive')
    m.logged(['xcrun','libtool','-static','-o',str(package),*archives],ROOT,out/'package.log')
    objects=out/'host-objects';objects.mkdir();replacements={}
    for index,original in enumerate(plan['host_compile_commands']):
        cmd=[x.replace(str(m.CORE),str(core)) for x in original];old=cmd[cmd.index('-o')+1];obj=objects/(str(index)+'-'+Path(old).name)
        for flag in ['-MT','-MF']:
            if flag in cmd:i=cmd.index(flag);del cmd[i:i+2]
        if '-MD' in cmd:cmd.remove('-MD')
        cmd[cmd.index('-o')+1]=str(obj);cmd+=['-ivfsoverlay',str(out/'overlay.json')]
        m.logged(cmd,m.HOST,out/(obj.name+'.log'));replacements[old]=str(obj)
    app=out/'GalaxyPad.app';shutil.copytree(m.HOST/'GalaxyPad.app',app,symlinks=True)
    # Remove only copied old resource seal. Signing is deliberately outside this recipe.
    if (app/'_CodeSignature').exists():shutil.rmtree(app/'_CodeSignature')
    link=[replacements.get(x,x) for x in plan['host_link_command']];link[link.index(str(m.PACKAGE))]=str(package);link[link.index('-o')+1]=str(app/'GalaxyPad');link.insert(1,'-Wl,-map,'+str(out/'host-link.map'))
    m.logged(link,m.HOST,out/'host-link.log')
    (app/'Frameworks').mkdir(exist_ok=True);shutil.copyfile(m.MODULE,app/'Frameworks/gRMGE01_recomp.dylib')
    m.require(m.sha(app/'Frameworks/gRMGE01_recomp.dylib')==m.MODULE_SHA,'Physical module changed')
    m.logged(['xcrun','vtool','-show-build',str(app/'GalaxyPad')],ROOT,out/'host-platform.log')
    m.require('platform IOS\n' in (out/'host-platform.log').read_text(),'Wrong physical host platform')
    m.logged(['xcrun','lipo',str(app/'GalaxyPad'),'-verify_arch','arm64'],ROOT,out/'host-architecture.log')
    m.verify_control(plan)
    for path,digest in plan['candidate_input_hashes'].items():m.require(m.sha(path)==digest,'Frozen input changed: '+path)
    plan.update(status='built unsigned; not signed, installed or selected',host_sha256=m.sha(app/'GalaxyPad'),private_core_sha256=m.sha(package),rebuilt_host_objects=replacements,host_link_command_executed=link);m.dump(planfile,plan)
    print(plan['host_sha256'],app)

if __name__=='__main__':main()
