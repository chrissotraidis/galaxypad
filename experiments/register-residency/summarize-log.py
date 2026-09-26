#!/usr/bin/env python3
"""Summarize GalaxyPad frame/performance windows from a runtime.log after the last runtime start."""
import re, statistics, sys, argparse
p = argparse.ArgumentParser(); p.add_argument('log'); p.add_argument('--start', type=float, default=30); p.add_argument('--end', type=float, default=1e9)
a = p.parse_args()
lines = open(a.log, errors='replace').read().splitlines()
start = max(i for i, l in enumerate(lines) if 'Starting runtime:' in l)
t0 = None; rows = []; cur = None
for l in lines[start:]:
    m = re.search(r'\[GalaxyPad frame window\].* mono=([\d.]+) seconds=([\d.]+).* fps=([\d.]+).*emulation_speed_estimate=([\d.]+) native_menu=(\d) ui_blocked=(\d) pause_requested=(\d)', l)
    if m:
        mono = float(m.group(1)); t0 = t0 if t0 is not None else mono
        cur = {'t': mono - t0, 'fps': float(m.group(3)), 'speed': float(m.group(4)), 'ok': m.group(5) + m.group(6) + m.group(7) == '000'}
        continue
    m = re.search(r'\[GalaxyPad performance\].* process_cpu_percent=([\d.]+).* thermal_state=(\d)', l)
    if m and cur:
        cur['cpu'] = float(m.group(1)); cur['thermal'] = int(m.group(2)); rows.append(cur); cur = None
sel = [r for r in rows if r['ok'] and a.start <= r['t'] <= a.end]
if not sel: sys.exit('no windows')
med = lambda k: round(statistics.median(r[k] for r in sel), 3)
print(f"windows={len(sel)} span={sel[0]['t']:.0f}-{sel[-1]['t']:.0f}s fps_med={med('fps')} fps_min={min(r['fps'] for r in sel):.1f} "
      f"speed_med={med('speed')} cpu_med={med('cpu')} cpu_mean={statistics.mean(r['cpu'] for r in sel):.1f} "
      f"cpu_per_frame_ms={statistics.median(r['cpu'] / r['fps'] * 10 for r in sel):.2f} thermal={sorted(set(r['thermal'] for r in sel))}")
