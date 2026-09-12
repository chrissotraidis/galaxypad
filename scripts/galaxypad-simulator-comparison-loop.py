#!/usr/bin/env python3
"""Repeat launch -> visual scene check -> unsampled capture for each A/B candidate.

This retains sparse HUD readings, not continuous frame-tail/audio acceptance.
Reuses the target Simulator and never changes the physical app. Run diagnostics
separately. The caller checks screenshots, changes one candidate, then repeats.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = 'org.galaxypad.GalaxyPad'
DEFAULT_SIM = '94BACEE0-DE7F-4D31-8097-4F3F0B02C7D1'

def run(*args):
    return subprocess.check_output(args, text=True)

def digest(path):
    with open(path, 'rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()

def target_simulator(sim):
    devices = json.loads(run('xcrun', 'simctl', 'list', 'devices', 'booted', '--json'))
    booted = [d['udid'] for group in devices['devices'].values() for d in group if d['state']=='Booted']
    if sim not in booted:
        raise SystemExit('Boot the target Simulator before using this comparison loop.')
    return devices

def check_module(module):
    if '__llvm_profile' in run('xcrun', 'nm', '-a', str(module)):
        raise SystemExit('Instrumented profile module is forbidden in the comparison lane.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    launch = sub.add_parser('launch')
    launch.add_argument('app', type=Path)
    launch.add_argument('module', type=Path)
    launch.add_argument('output', type=Path)
    launch.add_argument('--simulator', default=DEFAULT_SIM)
    capture = sub.add_parser('capture')
    capture.add_argument('output', type=Path)
    scene_gate = capture.add_mutually_exclusive_group(required=True)
    scene_gate.add_argument('--scene-verified', action='store_true',
                            help='Caller has visually checked the current Observatory scene.')
    scene_gate.add_argument('--provisional', action='store_true',
                            help='Capture immediately after routing; all saved frames require visual review before comparison.')
    capture.add_argument('--seconds', type=int, choices=(30,60,120,240), default=60)
    args = parser.parse_args()
    output = args.output.resolve()
    if args.action == 'launch':
        inventory = target_simulator(args.simulator)
        app, module = args.app.resolve(), args.module.resolve()
        check_module(module)
        if output.exists():
            raise SystemExit('Use a fresh evidence directory; existing runs are immutable.')
        output.mkdir(parents=True)
        manifest = {'simulator':args.simulator, 'app':str(app), 'module':str(module),
                    'host_sha256':digest(app/'GalaxyPad'), 'module_sha256':digest(module),
                    'booted_simulators':inventory,
                    'scene':'121-star Observatory central map platform',
                    'logging':False, 'sampling':False, 'render_scale':1, 'aspect_mode':0}
        (output/'comparison.json').write_text(json.dumps(manifest, indent=2)+'\n')
        env = dict(os.environ, GALAXYPAD_SIMULATOR_UDID=args.simulator,
                   GALAXYPAD_SIMULATOR_MODULE=str(module),
                   GALAXYPAD_SIMULATOR_STOP_AFTER_SCENE='YES',
                   GALAXYPAD_SIMULATOR_FRAME_LOGGING='NO',
                   GALAXYPAD_SIMULATOR_EFB_TRACE='', GALAXYPAD_SIMULATOR_PHASE_TRACE='',
                   GALAXYPAD_SIMULATOR_LLVM_PROFILE_FILE='', GALAXYPAD_SIMULATOR_SYSTEM_TRACE='')
        with (output/'route.log').open('w') as log:
            subprocess.run(['bash',str(ROOT/'scripts/galaxypad-unattended-simulator-loop.sh'),
                            str(app),str(output)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        print(f'Inspect {output}/scene.png. Repair navigation if needed; then capture --scene-verified.')
        return
    scene = output/'scene.png'
    if not scene.exists() or time.time()-scene.stat().st_mtime > 120:
        raise SystemExit('Scene verification is stale. Take a current scene.png and visually verify gameplay before capture.')
    manifest = json.loads((output/'comparison.json').read_text())
    sim = manifest['simulator']
    inventory = target_simulator(sim)
    module = Path(manifest['module'])
    check_module(module)
    assert digest(module)==manifest['module_sha256'], 'Module changed after launch'
    pid = int((output/'pid.txt').read_text())
    command = run('ps','-p',str(pid),'-o','args=')
    startup=(output/'console.log').read_text()
    assert 'Starting runtime: render_scale=1 aspect_ratio_mode=0' in startup, 'Unverified render/aspect settings'
    assert str(module) in command and '-GalaxyPadLogFrameRateWindows NO' in command, 'Wrong running candidate'
    installed = Path(run('xcrun','simctl','get_app_container',sim,BUNDLE,'app').strip())
    assert digest(installed/'GalaxyPad')==manifest['host_sha256'], 'Installed host differs'
    samples = output/'observation.json'
    assert not samples.exists(), 'Capture already exists'
    (output/'booted-before.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (output/'host-before.txt').write_text(run('ps','-axo','pid,pcpu,rss,stat,command'))
    (output/'thermal-before.txt').write_text(run('pmset','-g','therm'))
    observations=[]
    start=time.monotonic()
    for offset in range(0,args.seconds+1,10):
        time.sleep(max(0,start+offset-time.monotonic()))
        entry={'elapsed':time.monotonic()-start,'utc_epoch':time.time(),
               'process':run('ps','-p',str(pid),'-o','pid,pcpu,rss,time,stat').strip()}
        subprocess.run(['xcrun','simctl','io',sim,'screenshot',str(output/f'window-{offset:03d}.png')],check=True)
        entry['screenshot_end_elapsed']=time.monotonic()-start
        observations.append(entry)
    samples.write_text(json.dumps({'samples':observations,'requires_visual_review':args.provisional,'limits':'Sparse HUD only; no continuous frame tail, speed or timed audio proof.'},indent=2)+'\n')
    (output/'booted-after.json').write_text(json.dumps(target_simulator(sim),indent=2)+'\n')
    (output/'host-after.txt').write_text(run('ps','-axo','pid,pcpu,rss,stat,command'))
    (output/'thermal-after.txt').write_text(run('pmset','-g','therm'))
    print(f'Capture retained in {output}; compare matched control and candidate, then record accept/reject before repeating.')

if __name__=='__main__':
    main()
