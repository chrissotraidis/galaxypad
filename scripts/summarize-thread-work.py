#!/usr/bin/env python3
"""Summarize private self-thread work; require matching VI and complete coverage."""
import argparse
import csv
import json
import re

COUNTERS=('instructions','cycles','user_mach','system_mach')

def summarize(rows, stamps, metadata, vi_dropped, start, end, capacity=None):
    levels=metadata['levels']; numerator=metadata['numerator']; denominator=metadata['denominator']
    if not 1 <= levels <= 8 or numerator<=0 or denominator<=0 or metadata['config_error']:
        raise ValueError('Unavailable counter provider/topology/timebase')
    if start<0 or end<=start or not stamps or any(b<=a for a,b in zip(stamps,stamps[1:])):
        raise ValueError('Invalid window or VI sequence')
    groups=[]
    for raw in rows:
        r={k:int(v) for k,v in raw.items()}
        if any(v<0 for v in r.values()): raise ValueError('Negative counter/status')
        if not groups or r['vi_ns']!=groups[-1][0]['vi_ns']: groups.append([])
        groups[-1].append(r)
    if [g[0]['vi_ns'] for g in groups]!=stamps:
        raise ValueError('Sidecar does not exactly match retained VI samples')
    for g in groups:
        if [r['level'] for r in g]!=list(range(levels)):
            raise ValueError('Missing/duplicate/reordered level')
        for r in g:
            if any(r[k]!=g[0][k] for k in ('before_ns','after_ns','error')):
                raise ValueError('Inconsistent query group')
    for drops in (metadata['dropped'],vi_dropped):
        if drops<0 or (drops and (capacity is None or capacity<=0 or len(stamps)!=capacity)):
            raise ValueError('Unverified dropped prefix')
    if stamps[0]>start or stamps[-1]<end:
        raise ValueError('Incomplete requested coverage')
    selected=[g for g in groups if start<=g[0]['vi_ns']<end]
    if len(selected)<2: raise ValueError('Too few complete samples')
    for i,g in enumerate(selected):
        a=g[0]
        if a['error'] or not a['vi_ns']<=a['before_ns']<=a['after_ns']:
            raise ValueError('Failed/invalid counter query')
        if i:
            previous=selected[i-1]
            if previous[0]['after_ns']>=a['before_ns']:
                raise ValueError('Overlapping query brackets')
            if any(r[k]<p[k] for r,p in zip(g,previous) for k in COUNTERS):
                raise ValueError('Counter reset inside selected window')
    # Validate before trimming the final boundary; never hide an invalid interior
    # query merely because its corrupt after timestamp lies past the window.
    selected=[g for g in selected if g[0]['after_ns']<=end]
    if len(selected)<2: raise ValueError('Too few complete query brackets')
    first,last=selected[0],selected[-1]
    a,b=first[0],last[0]
    minimum=sum(a['after_ns']<=t<b['before_ns'] for t in stamps)
    maximum=sum(a['before_ns']<=t<b['after_ns'] for t in stamps)
    if minimum<=0: raise ValueError('Empty guaranteed interval')
    result=[]
    for i,(p,q) in enumerate(zip(first,last)):
        delta={k:q[k]-p[k] for k in COUNTERS}
        cpu_ns=(delta['user_mach']+delta['system_mach'])*numerator/denominator
        result.append(dict(level=i,deltas=delta,cpu_ns=cpu_ns))
    cpu_ns=sum(r['cpu_ns'] for r in result)
    totals={k:sum(r['deltas'][k] for r in result) for k in COUNTERS}
    if cpu_ns<=0 or totals['instructions']<=0 or totals['cycles']<=0:
        raise ValueError('Unavailable thread work')
    for r in result: r['cpu_time_share']=r['cpu_ns']/cpu_ns
    return dict(scope='Calling CPU thread including host work; VI is not presentation',
        requested_window_ns=[start,end],selected_query_bounds_ns=[a['before_ns'],a['after_ns'],b['before_ns'],b['after_ns']],
        vi_count_range=[minimum,maximum],selected_samples=len(selected),
        omitted_boundary_ns=[a['before_ns']-start,end-b['after_ns']],
        thread_cpu_ns=cpu_ns,levels=result,totals=totals,
        per_vi_ranges={**{k:[totals[k]/maximum,totals[k]/minimum] for k in ('instructions','cycles')},
                       'cpu_ms':[cpu_ns/maximum/1e6,cpu_ns/minimum/1e6]},
        recording=dict(sidecar_dropped=metadata['dropped'],vi_dropped=vi_dropped,
                       verified_prefix_capacity=capacity,retained_tail_margin_ns=stamps[-1]-end))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sidecar'); parser.add_argument('vi')
    parser.add_argument('--start-ns',type=int,required=True); parser.add_argument('--end-ns',type=int,required=True)
    parser.add_argument('--verified-prefix-capacity',type=int)
    args=parser.parse_args()
    with open(args.sidecar) as stream:
        match=re.fullmatch(r'# dropped=(\d+) levels=(\d+) timebase=(\d+)/(\d+) config_error=(\d+)\n',stream.readline())
        if not match: raise ValueError('Unknown sidecar metadata')
        metadata=dict(zip(('dropped','levels','numerator','denominator','config_error'),map(int,match.groups())))
        rows=list(csv.DictReader(stream))
    with open(args.vi) as stream:
        match=re.fullmatch(r'# dropped=(\d+)\n',stream.readline())
        if not match: raise ValueError('Unknown VI metadata')
        vi_dropped=int(match[1]); stamps=[int(r['wall_ns']) for r in csv.DictReader(stream)]
    print(json.dumps(summarize(rows,stamps,metadata,vi_dropped,args.start_ns,args.end_ns,
                               args.verified_prefix_capacity),indent=2))
