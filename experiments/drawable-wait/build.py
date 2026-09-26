#!/usr/bin/env python3
"""Prepare/build isolated opt-in timing; never install or launch."""
import argparse,hashlib,json,shlex,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parents[2];src=Path(__file__).resolve().parent
out=root/'generated/experiments/drawable-wait-20260913';out.mkdir(parents=True,exist_ok=True)
base=root/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
host=root/'generated/build/ios-simulator-settings-perf13-final-20260913'
hostrecipe=json.loads((host/'recipe.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
core=base/'libGalaxyPadCore.a';assert digest(core)==hostrecipe['core_sha256']
header=out/'DrawableWaitProbe.h';shutil.copyfile(src/header.name,header)
shutil.copyfile(src/'test.cpp',out/'test.cpp')
paths=[root/'ref/ModernGekko/vendor/dolphin/Source/Core/VideoBackends/Metal/MTLGfx.mm',root/'apple/ios/GalaxyPadCoreHost.mm']
texts=[p.read_text() for p in paths]
def replace(index,old,new):
 assert texts[index].count(old)==1,(index,old);texts[index]=texts[index].replace(old,new)
replace(0,'    m_drawable = MRCRetain([m_layer nextDrawable]);','''    m_drawable = MRCRetain(galaxypad::drawable_wait::Measure(
      [] { return static_cast<std::uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count()); },
      [] { return galaxypad::drawable_wait::State{g_state_tracker->HasUnflushedData(),
                                                g_state_tracker->GPUBusy()}; },
      [&] { return [m_layer nextDrawable]; }));''')
replace(1,'  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];','''  const bool drawableWaitProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevDrawableWaitProbe"];
  galaxypad::drawable_wait::enabled.store(drawableWaitProbe,std::memory_order_relaxed);
  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];''')
# Names are generated once at preparation; runtime formatting occurs only on CPU-side new publications.
names=['calls','totalNs','maxNs','nil','pendingAfter','busyAfter','busyToIdle','busyToIdleNs','pendingChanged']
names += ['hist'+str(i) for i in range(8)]
names += [kind+str(i) for kind in ['stateCount','stateNs','stateMax'] for i in range(4)]
fmt='drawable_wait_probe record=%u field=%u '+' '.join(n+'=%llu' for n in names)
values=',\n                '.join('(unsigned long long)c['+str(i)+']' for i in range(len(names)))
replace(1,'          // Read presenter geometry on its rendering thread, not from UIKit.','''#if TARGET_OS_SIMULATOR
          auto drawableWaitHook=GetVideoEvents().vi_end_field_event.Register(
            [drawableWaitProbe,fields=0u,records=0u,last=std::uint64_t(0)]() mutable {
              if(!drawableWaitProbe || ++fields%120 || records>=128 || !Core::IsCPUThread()) return;
              auto snapshot=galaxypad::drawable_wait::Read();
              if(!snapshot || (*snapshot)[0]==last) return;
              last=(*snapshot)[0];++records;const auto& c=*snapshot;
              GalaxyPadLogPerformanceWindow(@[[NSString stringWithFormat:
                @"'''+fmt+'''",records,fields,
                '''+values+''']]);
            });
#endif
          // Read presenter geometry on its rendering thread, not from UIKit.''')
overlay={'version':0,'use-external-names':False,'roots':[]}
for p,t in zip(paths,texts):
 shutil.copyfile(p,out/(p.name+'.original'))
 target=out/p.name;target.write_text('#include "'+str(header)+'"\n#include <chrono>\n'+t)
 overlay['roots'].append({'type':'file','name':str(p),'external-contents':str(target)})
(out/'overlay.json').write_text(json.dumps(overlay,indent=2)+'\n')
db=json.loads((base/'core/compile_commands.json').read_text());commands=[]
for p in paths:
 if p.name=='GalaxyPadCoreHost.mm':
  cmd=next(c.copy() for c in hostrecipe['compile_commands'] if str(p) in c);cwd=str(root)
 else:
  item=next(c for c in db if c['file']==str(p));cmd=shlex.split(item['command']);cwd=item['directory']
 cmd[cmd.index('-o')+1]=str(out/(p.name+'.o'));cmd+=['-ivfsoverlay',str(out/'overlay.json')]
 commands.append({'argv':cmd,'directory':cwd})
link=hostrecipe['link'].copy()
for i,v in enumerate(link):
 if v.endswith('/objects/GalaxyPadCoreHost.mm.o'):link[i]=str(out/'GalaxyPadCoreHost.mm.o')
 elif v.endswith('/libGalaxyPadCore.a'):link[i]=str(out/'libGalaxyPadCore.a')
 elif v.startswith('-Wl,-map,'):link[i]='-Wl,-map,'+str(out/'host-link.map')
link[link.index('-o')+1]=str(out/'GalaxyPad.app/GalaxyPad')
j={'status':'prepared','core_sha256':digest(core),'original_core':str(core),'source_hashes':{str(p):digest(p) for p in paths},'prepared_hashes':{str(out/n):digest(out/n) for n in ['MTLGfx.mm','GalaxyPadCoreHost.mm','DrawableWaitProbe.h','test.cpp']},'compile_commands':commands,'link':link}
(out/'recipe.json').write_text(json.dumps(j,indent=2)+'\n')
if not args.build:print(out);raise SystemExit
subprocess.run(['xcrun','clang++','-std=c++23','-fsanitize=address,undefined',str(out/'test.cpp'),'-o',str(out/'test')],check=True)
subprocess.run([str(out/'test')],check=True)
for i,c in enumerate(commands):
 with (out/f'compile-{i}.log').open('w') as log:subprocess.run(c['argv'],cwd=c['directory'],stdout=log,stderr=subprocess.STDOUT,check=True)
original=subprocess.check_output(['ar','-t',str(core)],text=True);assert original.splitlines().count('MTLGfx.mm.o')==1
shutil.copyfile(core,out/'libGalaxyPadCore.a')
subprocess.run(['ar','-r',str(out/'libGalaxyPadCore.a'),str(out/'MTLGfx.mm.o')],check=True)
subprocess.run(['ranlib',str(out/'libGalaxyPadCore.a')],check=True)
assert subprocess.check_output(['ar','-t',str(out/'libGalaxyPadCore.a')],text=True)==original
shutil.copytree(host/'GalaxyPad.app',out/'GalaxyPad.app',dirs_exist_ok=True)
with (out/'link.log').open('w') as log:subprocess.run(link,stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['codesign','--force','--sign','-',str(out/'GalaxyPad.app')],check=True)
subprocess.run(['codesign','--verify','--strict',str(out/'GalaxyPad.app')],check=True)
j.update(status='ASan UBSan contracts; isolated compile/link/sign/strict verify passed; no runtime launch',candidate_host_sha256=digest(out/'GalaxyPad.app/GalaxyPad'),candidate_core_sha256=digest(out/'libGalaxyPadCore.a'))
(out/'recipe.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2)[-500:])
