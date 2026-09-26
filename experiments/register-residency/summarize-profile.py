#!/usr/bin/env python3
"""Summarize an exported Instruments time-profile table (xctrace export XML).

Resolves xctrace's id/ref compression, then reports per-thread weight, core types
for the busiest thread, and leaf-function/category attribution for a chosen thread.
"""
import argparse, collections, re, xml.etree.ElementTree as ET

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('xml'); p.add_argument('--thread', default='CPU thread'); p.add_argument('--top', type=int, default=30)
p.add_argument('--from-s', type=float, default=0); p.add_argument('--to-s', type=float, default=1e12)
p.add_argument('--addr-hist', help='Leaf function name whose sample offsets (from its binary load address) to histogram')
a = p.parse_args()
root = ET.parse(a.xml).getroot()
ids = {}
def resolve(e):
    if e is None: return None
    if 'ref' in e.attrib: return ids[e.attrib['ref']]
    if 'id' in e.attrib: ids[e.attrib['id']] = e
    for c in e: resolve(c)
    return e
threads = collections.Counter(); cores = collections.Counter(); leaf = collections.Counter(); cat = collections.Counter()
inclusive = collections.Counter(); total = 0
addr_hist = collections.Counter()
def category(name, binary):
    if binary == 'gRMGE01_recomp.dylib':
        if name.startswith('func_') or name.startswith('loop_'): return 'translated game code'
        return 'module runtime helpers'
    if 'StaticRecompCore::Run' in name: return 'dispatch loop (Run)'
    if 'MMU' in name or 'Memory' in name: return 'MMU / memory'
    if 'CoreTiming' in name: return 'CoreTiming'
    if name.startswith('StaticRecompCore'): return 'StaticRecomp runtime'
    return binary or '?'
for row in root.iter('row'):
    fields = {c.tag: resolve(c) for c in row}
    th = fields.get('thread'); w = fields.get('weight'); st = fields.get('tagged-backtrace') or fields.get('backtrace')
    state = fields.get('thread-state')
    if th is None or w is None: continue
    t = fields.get('sample-time')
    if t is not None and not (a.from_s <= int(t.text) / 1e9 <= a.to_s): continue
    tname = th.attrib.get('fmt', '?'); weight = int(w.text) / 1e6
    if state is not None and state.attrib.get('fmt') != 'Running': continue
    threads[re.sub(r' \(0x[0-9a-f]+\).*', '', tname)] += weight
    if a.thread not in tname or st is None: continue
    frames = [resolve(f) for f in st if f.tag == 'frame']
    if not frames: continue
    total += weight
    core = fields.get('core'); cores[re.sub(r'CPU \d+ ', '', core.attrib.get('fmt', '?')) if core is not None else '?'] += weight
    f0 = frames[0]; b = resolve(f0.find('binary')); bname = b.attrib.get('name') if b is not None else None
    name = f0.attrib.get('name') or f0.attrib.get('addr') or '?'
    leaf[(name, bname)] += weight; cat[category(name, bname)] += weight
    if a.addr_hist and name == a.addr_hist:
        addr_hist[int(f0.attrib['addr'], 16) - int(b.attrib['load-addr'], 16)] += weight
    for f in {fr.attrib.get('name') for fr in frames}:
        inclusive[f] += weight
print('Running ms by thread:'); [print(f'  {v:9.1f}  {k}') for k, v in threads.most_common(8)]
print(f'\n{a.thread}: {total:.1f} ms running; core types:', dict(cores))
print('\nLeaf categories:'); [print(f'  {v/total*100:5.1f}%  {k}') for k, v in cat.most_common()]
print(f'\nTop {a.top} leaf functions:'); [print(f'  {v/total*100:5.1f}%  {n}  [{b}]') for (n, b), v in leaf.most_common(a.top)]
print('\nSelected inclusive:'); [print(f'  {inclusive[k]/total*100:5.1f}%  {k}') for k in sorted(inclusive, key=lambda k: -inclusive[k])
                                 if k and any(s in k for s in ('MMU', 'CoreTiming', 'Hook', 'Video', 'Fifo', 'DSP', 'Audio', 'EFB'))][:15]
if addr_hist:
    n = sum(addr_hist.values())
    print(f'\n{a.addr_hist}: {n:.0f} ms of leaf samples; hottest binary offsets (sample address - load address):')
    for off, v in addr_hist.most_common(40):
        print(f'  {v/n*100:5.1f}%  {off:#x}')
