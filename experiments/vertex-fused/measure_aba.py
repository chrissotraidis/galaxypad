import argparse,os,pathlib,subprocess,time,json
parser=argparse.ArgumentParser();parser.add_argument('--experiment',type=pathlib.Path,required=True);parser.add_argument('--simulator',required=True);args=parser.parse_args();e=args.experiment.resolve();udid=args.simulator;r=pathlib.Path(__file__).resolve().parents[2]
assert not any((e/name).exists() for name in ['A1','B','A2']), 'Preserve existing measurement directories'
for name,app in [('A1',r/'generated/build/ios-simulator-settings-perf6-20260913/GalaxyPad.app'),('B',e/'GalaxyPad.app'),('A2',r/'generated/build/ios-simulator-settings-perf6-20260913/GalaxyPad.app')]:
 out=e/name;env=dict(os.environ,GALAXYPAD_SIMULATOR_UDID=udid,GALAXYPAD_SIMULATOR_INPUT=str(e/'input.json'),GALAXYPAD_SIMULATOR_FRAME_LOGGING='YES',GALAXYPAD_SIMULATOR_STOP_AFTER_SCENE='YES',GALAXYPAD_SIMULATOR_STDERR=str(e/(name+'-stderr.log')))
 env.pop('SIMCTL_CHILD_GALAXYPAD_VERTEX_FORMAT_LOG',None)
 print('BEGIN',name,flush=True);subprocess.run([str(r/'scripts/galaxypad-unattended-simulator-loop.sh'),str(app),str(out)],env=env,check=True)
 with (out/'window.log').open('w') as log:
  proc=subprocess.Popen(['xcrun','simctl','spawn',udid,'log','stream','--style','compact','--level','debug','--predicate','process == "GalaxyPad"'],stdout=log,stderr=log)
  time.sleep(45);proc.terminate();proc.wait()
 subprocess.run(['xcrun','simctl','io',udid,'screenshot',str(out/'end.png')],check=True)
 subprocess.run(['xcrun','simctl','terminate',udid,'org.galaxypad.GalaxyPad'],check=True)
 print('END',name,flush=True)
