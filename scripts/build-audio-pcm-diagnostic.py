#!/usr/bin/env python3
"""Build a private combined Simulator host changing only post-mix PCM capture."""
import collections, hashlib, json, shlex, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'generated/build/ios-simulator-dual-core-audio-tempo-20260912'
AUDIO=ROOT/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912'
OUT=ROOT/'generated/build/ios-simulator-audio-pcm-diagnostic-retry-20260912'
SOURCE=ROOT/'generated/experiments/audio-pcm-capture-20260912/CoreAudioSoundStream.cpp'
CANON=ROOT/'ref/ModernGekko/vendor/dolphin/Source/Core/AudioCommon/CoreAudioSoundStream.cpp'
MODULE=ROOT/'generated/build/ios-simulator-pgo-use-20260912/gRMGE01_recomp.dylib'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(v,m):
 if not v: raise SystemExit(m)
def run(cmd,log,cwd=ROOT):
 with (OUT/log).open('w') as f: subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,check=True)
def members(path):
 data=Path(path).read_bytes(); require(data[:8]==b'!<arch>\n','Bad archive'); p=8; rows=[]
 while p<len(data):
  h=data[p:p+60]; size=int(h[48:58]); name=h[:16].decode().strip(); body=data[p+60:p+60+size]
  if name.startswith('#1/'):
   n=int(name[3:]); name=body[:n].rstrip(b'\0').decode(); body=body[n:]
  else: name=name.rstrip('/')
  if not name.startswith('__.SYMDEF'): rows.append((name,hashlib.sha256(body).hexdigest()))
  p+=60+size+(size%2)
 return collections.Counter(rows)
def main():
 require(not OUT.exists(),'Preserve existing diagnostic build')
 plan=json.loads((BASE/'recipe.json').read_text())
 expected={BASE/'GalaxyPad.app/GalaxyPad':'ef9898603ebf4eddf7fb01f6406f862aa20e03ad808025cf48078b50bcc69953',AUDIO/'libGalaxyPadCore.a':'457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8',MODULE:'90e24dfb4e96597686b8fccf09bb55efdcbd7d059dd3ff710a9f32fab26f353f'}
 for p,h in expected.items(): require(sha(p)==h,'Changed baseline '+str(p))
 canonical_sha=sha(CANON)
 OUT.mkdir(); (OUT/'inputs').mkdir(); (OUT/'host-objects').mkdir()
 shutil.copyfile(SOURCE,OUT/'inputs/CoreAudioSoundStream.cpp')
 shutil.copyfile(ROOT/'experiments/audio-pcm-capture/DiagnosticPcmCapture.h',OUT/'inputs/DiagnosticPcmCapture.h')
 overlay=json.loads((AUDIO/'overlay.json').read_text())
 for row in overlay['roots']:
  p=Path(row['external-contents']); require(sha(p)==plan['frozen_audio_input_hashes'][p.name],'Changed v8 input')
  shutil.copyfile(p,OUT/'inputs'/p.name); row['external-contents']=str(OUT/'inputs'/p.name)
 overlay['roots'].append({'type':'file','name':str(CANON),'external-contents':str(OUT/'inputs/CoreAudioSoundStream.cpp')})
 (OUT/'overlay.json').write_text(json.dumps(overlay,indent=2)+'\n')
 rows=json.loads((AUDIO/'core/compile_commands.json').read_text())
 row=next(r for r in rows if r['file']==str(CANON)); cmd=shlex.split(row['command'])
 obj=OUT/'CoreAudioSoundStream.cpp.o'
 cmd[cmd.index('-o')+1]=str(obj); cmd[cmd.index('-ivfsoverlay')+1]=str(OUT/'overlay.json')
 cmd+=['-DGALAXYPAD_DIAGNOSTIC_PCM_CAPTURE=1','-I'+str(OUT/'inputs'),'-MD','-MF',str(obj)+'.d']
 run(cmd,'compile.log',Path(row['directory']))
 deps=Path(str(obj)+'.d').read_text()
 for name in ['Mixer.h','AudioTempo.h','DiagnosticPcmCapture.h']: require(name in deps,'Missing ABI dependency '+name)
 private=OUT/'libGalaxyPadCore.a'; shutil.copyfile(AUDIO/'libGalaxyPadCore.a',private)
 before=members(private); before_core=[x for x in before if x[0]=='CoreAudioSoundStream.cpp.o']
 require(len(before_core)==1 and before[before_core[0]]==1,'Ambiguous original capture object')
 run(['xcrun','ar','-d',str(private),'CoreAudioSoundStream.cpp.o'],'archive-delete.log')
 run(['xcrun','ar','-r',str(private),str(obj)],'archive-add.log')
 run(['xcrun','ranlib',str(private)],'archive-index.log')
 after=members(private); after_core=[x for x in after if x[0]=='CoreAudioSoundStream.cpp.o']
 require(len(after_core)==1 and after[after_core[0]]==1,'Ambiguous replacement object')
 before.pop(before_core[0]); after.pop(after_core[0]); require(before==after,'Other archive member changed')
 link=plan['link'][:]; hashes={}
 for i,x in enumerate(link):
  if x.endswith('.o'):
   target=OUT/'host-objects'/Path(x).name; require(not target.exists(),'Object collision')
   shutil.copyfile(x,target); hashes[str(target)]=sha(x); link[i]=str(target)
  elif x==str(AUDIO/'libGalaxyPadCore.a'): link[i]=str(private)
  elif x.startswith('-Wl,-map,'): link[i]='-Wl,-map,'+str(OUT/'host-link.map')
 link[link.index('-o')+1]=str(OUT/'GalaxyPad.app/GalaxyPad')
 shutil.copytree(BASE/'GalaxyPad.app',OUT/'GalaxyPad.app',symlinks=True)
 run(link,'link.log',Path(plan['cwd']))
 table=(OUT/'host-link.map').read_text(errors='replace').split('# Sections:')[0]
 for name in ['Mixer.cpp.o','CoreAudioSoundStream.cpp.o']:
  owners=[x for x in table.splitlines() if name in x]
  require(len(owners)==1 and str(private) in owners[0],'Wrong archive owner '+name)
 owners=[x for x in table.splitlines() if 'GalaxyPadCoreHost.mm.o' in x]
 require(len(owners)==1 and str(OUT/'host-objects/GalaxyPadCoreHost.mm.o') in owners[0],'Wrong CoreHost owner')
 run(['xcrun','vtool','-show-build',str(OUT/'GalaxyPad.app/GalaxyPad')],'platform.log')
 require('platform IOSSIMULATOR' in (OUT/'platform.log').read_text(),'Not Simulator')
 run(['codesign','--force','--sign','-',str(OUT/'GalaxyPad.app')],'sign.log')
 run(['codesign','--verify','--deep','--strict',str(OUT/'GalaxyPad.app')],'sign-verify.log')
 for p,h in expected.items(): require(sha(p)==h,'Baseline mutated')
 require(sha(CANON)==canonical_sha,'Canonical source mutated')
 require(all(sha(p)==h for p,h in hashes.items()),'Host object changed')
 record={'status':'built, signed, not installed or run','diagnostic_only':True,'capture_env':'GALAXYPAD_AUDIO_PCM_PATH','capture_limit_seconds':120,'flush':'Stop Game destroys stream; after RemoteIO stop/uninitialize','capture_scope':'Only GalaxyPad final Mixer 48k stereo S16 before RemoteIO output volume, no microphone or other apps','compile':cmd,'link':link,'baseline_hashes':{str(p):h for p,h in expected.items()},'candidate_host_sha256':sha(OUT/'GalaxyPad.app/GalaxyPad'),'candidate_archive_sha256':sha(private),'replaced_object_sha256':sha(obj),'other_archive_members_byte_identical':sum(before.values()),'host_object_hashes':hashes,'input_hashes':{p.name:sha(p) for p in (OUT/'inputs').iterdir()},'limitations':['Not hardware loopback or subjective sound acceptance','Captures first 120 seconds of rendered frames, including startup/route','Explicit pause wall-time gaps are not inserted','Stop Game required to flush; process kill loses capture','Do not use this instrumented app for FPS acceptance']}
 (OUT/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 print(record['candidate_host_sha256'],OUT/'GalaxyPad.app')
if __name__=='__main__':main()
