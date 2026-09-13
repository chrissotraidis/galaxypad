import argparse,pathlib,json,shutil,subprocess,hashlib
parser=argparse.ArgumentParser();parser.add_argument('--experiment',type=pathlib.Path,required=True);e=parser.parse_args().experiment.resolve();r=pathlib.Path(__file__).resolve().parents[2];base=r/'generated/build/ios-simulator-audio-tempo-isolated-retry-20260912/libGalaxyPadCore.a';h=r/'generated/build/ios-simulator-settings-perf6-20260913'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base)=='457f4dba560eab8aeb899406340852244ef8bb1554b987e2bf1f26883ed94cb8'
shutil.copyfile(e/'candidate.o',e/'VertexLoader.cpp.o');shutil.copyfile(base,e/'libGalaxyPadCore.a');subprocess.run(['xcrun','ar','-r',str(e/'libGalaxyPadCore.a'),str(e/'VertexLoader.cpp.o')],check=True)
shutil.copytree(h/'GalaxyPad.app',e/'GalaxyPad.app',dirs_exist_ok=True)
link=json.loads((h/'recipe.json').read_text())['link'];link=[str(e/'libGalaxyPadCore.a') if v==str(base) else v for v in link];link[link.index('-o')+1]=str(e/'GalaxyPad.app/GalaxyPad');link=[('-Wl,-map,'+str(e/'host-link.map')) if v.startswith('-Wl,-map,') else v for v in link];subprocess.run(link,check=True);subprocess.run(['codesign','--force','--sign','-',str(e/'GalaxyPad.app')],check=True)
(e/'receipt.json').write_text(json.dumps({'base_sha':sha(base),'core_sha':sha(e/'libGalaxyPadCore.a'),'source_sha':sha(e/'VertexLoader.cpp'),'host_sha':sha(e/'GalaxyPad.app/GalaxyPad'),'link':link},indent=2))
