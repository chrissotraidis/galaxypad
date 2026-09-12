#!/usr/bin/env python3
"""Prepare or execute an isolated one-host-TU dual-core + full-v8-audio relink.

Preparation records commands/hashes only; --execute is a separate explicit step.
Never rebuilds/replaces the core, baseline app, old-PGO module, or user data.
"""
import argparse, hashlib, json, shlex, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIO=ROOT/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
BASE=ROOT/'generated/build/ios-simulator-pause-toggle-app'
OLDCORE=ROOT/'generated/build/ios-simulator-core'
SOURCE=ROOT/'generated/dual-core-source-audit-20260912/GalaxyPadCoreHost.mm'
CANONICAL=ROOT/'apple/ios/GalaxyPadCoreHost.mm'
MIX=ROOT/'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon'
MODULE=ROOT/'generated/build/ios-simulator-pgo-use-20260912/gRMGE01_recomp.dylib'
HOST_SHA='b3edb1647b350bc35256f8fba8c2e63878b842b7b5111b8df0864c7eb2018d43'
AUDIO_SHA='bb8b49859d1573122ce5bcb8c001b7bc91f7827c47a838cb66c2c802a8aabba9'
CORE_SHA='457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8'
MODULE_SHA='90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'
MIX_SHAS={'Mixer.cpp':'102a876d8efe784e2c37c4cadae46eadc4479f0776797a8388d16d31215565e1',
 'Mixer.h':'4e14a7db9b84f372b65ac660c8653c1f7207f243d36e2bfe9b84b5ed81ee0c27',
 'AudioTempo.h':'eff12bf32da6aa3fb6ccf073117f1b0001df1c23e3ef3f5baf21bd1036fbba5a'}
def require(ok,message):
 if not ok:raise SystemExit(message)
def sha(path):
 with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def logged(cmd,cwd,path):
 with path.open('w') as f:subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--execute',action='store_true');args=p.parse_args();out=args.output.resolve()
 require(ROOT/'generated/build' in out.parents and out not in [AUDIO,BASE,OLDCORE],'Use a new isolated generated/build directory')
 planfile=out/'recipe.json'
 if not args.execute:
  require(not out.exists(),'Output exists; preserve earlier recipe')
  audio=json.loads((AUDIO/'recipe.json').read_text())
  require(audio['candidate_host_sha256']==AUDIO_SHA and audio['private_core_sha256']==CORE_SHA,'Unexpected audio build manifest')
  require(len(audio['core_mixer_dependents'])==18 and len(audio['host_compile_commands'])==1,'Unexpected layout consumer inventory')
  controlhashes={str(BASE/'GalaxyPad.app/GalaxyPad'):HOST_SHA,str(AUDIO/'GalaxyPad.app/GalaxyPad'):AUDIO_SHA,str(MODULE):MODULE_SHA}
  for path,expected in controlhashes.items():require(sha(path)==expected,'Changed baseline: '+path)
  for name,expected in MIX_SHAS.items():require(sha(AUDIO/'inputs'/name)==expected,'Frozen v8 source changed: '+name)
  dual=SOURCE.read_text();normal=CANONICAL.read_text()
  addition='#if TARGET_OS_SIMULATOR\n          Config::SetCurrent(Config::MAIN_CPU_THREAD, true);\n#endif\n'
  require(dual.count(addition)==1 and dual.replace(addition,'')==normal,'Copied host differs beyond session-only dual-core override')
  compile=[x.replace(str(OLDCORE),str(AUDIO/'core')) for x in audio['host_compile_commands'][0]]
  for flag in ['-MF','-MT']:
   if flag in compile:
    i=compile.index(flag);del compile[i:i+2]
  if '-MD' in compile:compile.remove('-MD')
  compile[compile.index('-o')+1]=str(out/'GalaxyPadCoreHost.mm.o')
  compile+=['-MD','-MF',str(out/'GalaxyPadCoreHost.mm.o.d'),'-ivfsoverlay',str(out/'overlay.json')]
  link=audio['host_link_command_executed'][:]
  oldobj=str(AUDIO/'host-objects/GalaxyPadCoreHost.mm.o')
  require(link.count(oldobj)==1 and link.count(str(AUDIO/'libGalaxyPadCore.a'))==1,'Unexpected audio host link owners')
  require(not any(x.endswith('libGalaxyPadCore.a') and x!=str(AUDIO/'libGalaxyPadCore.a') for x in link),'Stale core archive in link')
  snapshots={}
  for i,x in enumerate(link):
   if x.endswith('.o'):
    original=Path(x) if Path(x).is_absolute() else BASE/x
    if x==oldobj:link[i]=str(out/'GalaxyPadCoreHost.mm.o')
    else:
     target=out/'host-objects'/Path(x).name
     require(str(target) not in snapshots,'Object basename collision')
     snapshots[str(target)]={'source':str(original),'sha256':sha(original)};link[i]=str(target)
  link=[x for x in link if not x.startswith('-Wl,-map,')]
  link.insert(1,'-Wl,-map,'+str(out/'host-link.map'));link[link.index('-o')+1]=str(out/'GalaxyPad.app/GalaxyPad')
  plan={'status':'prepared; no compilation/link/signing executed','cwd':str(BASE),'compile':compile,'link':link,
   'normal_host_sha256':HOST_SHA,'audio_host_sha256':AUDIO_SHA,'private_core_sha256':CORE_SHA,'old_module_sha256':MODULE_SHA,
   'control_hashes':controlhashes,'frozen_audio_input_hashes':MIX_SHAS,'dual_source_sha256':sha(SOURCE),
   'core_archive':str(AUDIO/'libGalaxyPadCore.a'),'core_archive_stamp':[ (AUDIO/'libGalaxyPadCore.a').stat().st_size,(AUDIO/'libGalaxyPadCore.a').stat().st_mtime_ns],
   'source':str(SOURCE),'host_object_snapshots':snapshots,'full_audio_core_manifest_sha256':sha(AUDIO/'recipe.json'),
   'scope':'Recompile CoreHost only against frozen v8 Mixer/Tempo VFS and rebuilt core include paths; reuse full v8 aggregate and byte-identical other host objects; Simulator session CPU_THREAD override only'}
  out.mkdir(parents=True);write(planfile,plan)
  (out/'README.md').write_text('Prepared only. Execute after standalone v8 runtime acceptance and resource release:\n\n```sh\npython3 scripts/prepare-dual-core-audio-tempo-host.py --output '+str(out.relative_to(ROOT))+' --execute\n```\n\nThe script checks normal/audio host, old module, full v8 archive and source identity; snapshots other audio host objects; recompiles CoreHost with matching v8 headers; links/signs a separate app. It audits dependency paths, unique link-map object ownership and Simulator platform. No full core/module rebuild, app install, Simulator operation or data mutation.\n')
  print('Prepared only:',out);return
 require(planfile.is_file(),'Prepare first');plan=json.loads(planfile.read_text())
 require(not (out/'GalaxyPad.app').exists(),'Candidate already exists; preserve it')
 def verify():
  for path,digest in plan['control_hashes'].items():require(sha(path)==digest,'Control changed: '+path)
  require(sha(AUDIO/'libGalaxyPadCore.a')==CORE_SHA,'Full audio core changed')
  require(sha(SOURCE)==plan['dual_source_sha256'],'Copied dual host changed')
  require(sha(AUDIO/'recipe.json')==plan['full_audio_core_manifest_sha256'],'Audio core provenance changed')
  for name,digest in MIX_SHAS.items():require(sha(AUDIO/'inputs'/name)==digest,'Frozen v8 input changed')
 verify()
 inputs=out/'inputs';inputs.mkdir();shutil.copyfile(SOURCE,inputs/'GalaxyPadCoreHost.mm')
 mappings=[{'type':'file','name':str(CANONICAL),'external-contents':str(inputs/'GalaxyPadCoreHost.mm')}]
 for name in MIX_SHAS:
  shutil.copyfile(AUDIO/'inputs'/name,inputs/name)
  mappings.append({'type':'file','name':str(MIX/name),'external-contents':str(inputs/name)})
 write(out/'overlay.json',{'version':0,'use-external-names':False,'roots':mappings})
 (out/'host-objects').mkdir()
 for target,row in plan['host_object_snapshots'].items():
  require(sha(row['source'])==row['sha256'],'Other host object changed: '+row['source']);shutil.copyfile(row['source'],target)
  require(sha(target)==row['sha256'],'Host object snapshot differs')
 logged(plan['compile'],BASE,out/'compile.log')
 deps=(out/'GalaxyPadCoreHost.mm.o.d').read_text()
 for path in [CANONICAL,MIX/'Mixer.h',MIX/'AudioTempo.h']:require(str(path) in deps,'Missing matching-layout dependency: '+str(path))
 require(str(OLDCORE) not in ' '.join(plan['compile']),'Stale control core include path')
 shutil.copytree(AUDIO/'GalaxyPad.app',out/'GalaxyPad.app',symlinks=True)
 logged(plan['link'],BASE,out/'link.log')
 linkmap=(out/'host-link.map').read_text(errors='replace');table=linkmap.split('# Sections:',1)[0]
 rows=[x for x in table.splitlines() if 'GalaxyPadCoreHost.mm.o' in x]
 require(len(rows)==1 and str(out/'GalaxyPadCoreHost.mm.o') in rows[0],'Wrong/stale CoreHost allocation owner')
 mixrows=[x for x in table.splitlines() if 'Mixer.cpp.o' in x]
 require(len(mixrows)==1 and str(AUDIO/'libGalaxyPadCore.a') in mixrows[0],'Wrong Mixer implementation owner')
 logged(['xcrun','vtool','-show-build',str(out/'GalaxyPad.app/GalaxyPad')],ROOT,out/'platform.log')
 require('platform IOSSIMULATOR' in (out/'platform.log').read_text(),'Wrong platform')
 logged(['codesign','--force','--sign','-',str(out/'GalaxyPad.app')],ROOT,out/'sign.log')
 logged(['codesign','--verify','--deep','--strict',str(out/'GalaxyPad.app')],ROOT,out/'sign-verify.log')
 verify();plan.update(status='built and signed; not installed or selected',candidate_host_sha256=sha(out/'GalaxyPad.app/GalaxyPad'),host_object_sha256=sha(out/'GalaxyPadCoreHost.mm.o'))
 write(planfile,plan);print(plan['candidate_host_sha256'],out/'GalaxyPad.app')
if __name__=='__main__':main()
