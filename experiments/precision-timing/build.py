#!/usr/bin/env python3
"""Prepare/build isolated opt-in timing; never install or launch."""
import argparse,hashlib,json,shlex,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parents[2];src=Path(__file__).resolve().parent
prior=root/'generated/experiments/precision-timing-20260913'
out=root/'generated/experiments/precision-timing-v2-20260914';out.mkdir(parents=True,exist_ok=True)
base=root/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
host=root/'generated/build/ios-simulator-settings-perf13-final-20260913'
hostrecipe=json.loads((host/'recipe.json').read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
core=base/'libGalaxyPadCore.a';assert digest(core)==hostrecipe['core_sha256']
header=out/'PrecisionTimingProbe.h';shutil.copyfile(src/header.name,header)
shutil.copyfile(src/'test.cpp',out/'test.cpp')
paths=[root/'ref/ModernGekko/vendor/dolphin/Source/Core/Common/Timer.cpp',root/'ref/ModernGekko/vendor/dolphin/Source/Core/Core/CoreTiming.cpp',root/'apple/ios/GalaxyPadCoreHost.mm']
texts=[p.read_text() for p in paths]
def replace(index,old,new):
 assert texts[index].count(old)==1,(index,old);texts[index]=texts[index].replace(old,new)
replace(0,'void PrecisionTimer::SleepUntil(Clock::time_point target)\n{','void PrecisionTimer::SleepUntil(Clock::time_point target)\n{\n  galaxypad::precision_timing::Measurement measurement(target);')
replace(0,'  // Spin for the remaining time.','  measurement.Spin();\n  // Spin for the remaining time.')
replace(1,'    const TimePoint time = Clock::now();','    galaxypad::precision_timing::Scope probeScope(0);\n    const TimePoint time = Clock::now();')
replace(1,'    if (use_precision_timer)\n      m_precision_gpu_timer.SleepUntil(time_point);','    galaxypad::precision_timing::Scope probeScope(1);\n    if (use_precision_timer)\n      m_precision_gpu_timer.SleepUntil(time_point);')
replace(2,'  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];','''  const bool precisionTimingProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPrecisionTimingProbe"];
  const bool disablePrecisionTiming=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevDisablePrecisionTiming"];
  galaxypad::precision_timing::enabled.store(precisionTimingProbe,std::memory_order_relaxed);
  const bool pointerProbe=[NSUserDefaults.standardUserDefaults boolForKey:@"GalaxyPadDevPointerContext"];''')
# Startup configuration is set before Runtime::Run and affects both timer paths.
replace(2,'          Config::SetCurrent(Config::MAIN_CPU_THREAD, true);','''          Config::SetCurrent(Config::MAIN_CPU_THREAD, true);
          if(disablePrecisionTiming) Config::SetCurrent(Config::MAIN_PRECISION_FRAME_TIMING,false);
          GalaxyPadLog(@"precision_timing configuration probe=%d disable=%d active=%d",precisionTimingProbe,disablePrecisionTiming,Config::Get(Config::MAIN_PRECISION_FRAME_TIMING));''')
names=['calls','late','positive','requestedNs','wallNs','cpuNs','spinNs','overshootNs','maxOvershootNs','cpuValid']+['hist'+str(i) for i in range(8)]
fmt='precision_timing_probe record=%u field=%u lane=%u '+' '.join(n+'=%llu' for n in names)
values=',\n                '.join('(unsigned long long)c['+str(i)+']' for i in range(len(names)))
replace(2,'          // Read presenter geometry on its rendering thread, not from UIKit.','''          auto precisionTimingHook=GetVideoEvents().vi_end_field_event.Register(
            [precisionTimingProbe,fields=0u,records=0u,last=std::array<std::uint64_t,2>{}]() mutable {
              if(!precisionTimingProbe || ++fields%120 || records>=1024 || !Core::IsCPUThread()) return;
              NSMutableArray<NSString *> *lines=[NSMutableArray arrayWithCapacity:2];
              for(unsigned lane=0;lane<2;++lane){auto snapshot=galaxypad::precision_timing::Read(lane);
              if(!snapshot || (*snapshot)[0]==last[lane]) continue;
              last[lane]=(*snapshot)[0];++records;const auto& c=*snapshot;
              [lines addObject:[NSString stringWithFormat:
                @"'''+fmt+'''",records,fields,lane,
                '''+values+''']];}
              if(lines.count) GalaxyPadLogPerformanceWindow(lines);
            });
          // Read presenter geometry on its rendering thread, not from UIKit.''')
# Source contract: both lane records share exactly one single-flight writer call.
hook=texts[2].split('auto precisionTimingHook=',1)[1].split('// Read presenter geometry',1)[0]
assert hook.count('GalaxyPadLogPerformanceWindow(')==1
assert hook.index('[lines addObject:')<hook.index('if(lines.count) GalaxyPadLogPerformanceWindow(lines);')
assert 'arrayWithCapacity:2' in hook
# The existing void API cannot acknowledge acceptance; it may drop a complete batch,
# but v2 never deliberately races two lane writes against each other.
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
j={'status':'prepared','core_sha256':digest(core),'original_core':str(core),'source_hashes':{str(p):digest(p) for p in paths},'prepared_hashes':{str(out/n):digest(out/n) for n in ['Timer.cpp','CoreTiming.cpp','GalaxyPadCoreHost.mm','PrecisionTimingProbe.h','test.cpp']},'compile_commands':commands,'link':link}
(out/'recipe.json').write_text(json.dumps(j,indent=2)+'\n')
if not args.build:print(out);raise SystemExit
subprocess.run(['xcrun','clang++','-std=c++23','-fsanitize=address,undefined',str(out/'test.cpp'),'-o',str(out/'test')],check=True)
subprocess.run([str(out/'test')],check=True)
prior_recipe=json.loads((prior/'recipe.json').read_text())
assert digest(prior/'libGalaxyPadCore.a')==prior_recipe['candidate_core_sha256']
assert digest(header)==digest(prior/'PrecisionTimingProbe.h')
for name in ['Timer.cpp','CoreTiming.cpp']:
 assert (out/name).read_text().split('\n',1)[1]==(prior/name).read_text().split('\n',1)[1]
 shutil.copyfile(prior/(name+'.o'),out/(name+'.o'))
shutil.copyfile(prior/'libGalaxyPadCore.a',out/'libGalaxyPadCore.a')
c=commands[2]
with (out/'compile-host.log').open('w') as log:subprocess.run(c['argv'],cwd=c['directory'],stdout=log,stderr=subprocess.STDOUT,check=True)
j['compile_commands']=commands[2:]
j['reused_core']=str(prior/'libGalaxyPadCore.a')
j['reused_objects']={name:digest(out/name) for name in ['Timer.cpp.o','CoreTiming.cpp.o']}
shutil.copytree(host/'GalaxyPad.app',out/'GalaxyPad.app',dirs_exist_ok=True)
with (out/'link.log').open('w') as log:subprocess.run(link,stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run(['codesign','--force','--sign','-',str(out/'GalaxyPad.app')],check=True)
subprocess.run(['codesign','--verify','--strict',str(out/'GalaxyPad.app')],check=True)
j.update(status='ASan UBSan contracts; isolated compile/link/sign/strict verify passed; no runtime launch',candidate_host_sha256=digest(out/'GalaxyPad.app/GalaxyPad'),candidate_core_sha256=digest(out/'libGalaxyPadCore.a'))
(out/'recipe.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps(j,indent=2)[-500:])
