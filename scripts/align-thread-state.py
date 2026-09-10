"""Align snapshot queries to VI intervals; never interpolate state durations."""
import argparse
import collections
import csv
import json


def observe(rows, start, end):
    if end <= start:
        raise ValueError('Nonpositive interval')
    inside = [r for r in rows if start <= r['start_ns'] and r['end_ns'] <= end]
    valid = [r for r in inside if r['valid']]
    counts = collections.Counter(str(r['run_state']) for r in valid)
    priorities = collections.Counter(str(r['priority']) for r in valid if r.get('priority') is not None)
    scheduling = {key:dict(collections.Counter(str(r[key]) for r in valid if r.get(key) is not None))
                  for key in ('policy','base_priority','max_priority')}
    # Distance between snapshots, including boundaries: not continuous coverage.
    points = [start] + [r['start_ns'] for r in valid] + [end]
    return dict(samples=len(inside), invalid=len(inside)-len(valid), states=dict(counts),
                priorities=dict(priorities), priority_unknown=sum(r.get('priority') is None for r in valid),
                scheduling=scheduling,
                max_snapshot_gap_ms=max(b-a for a,b in zip(points,points[1:]))/1e6,
                max_query_ms=max((r['end_ns']-r['start_ns'] for r in inside),default=0)/1e6,
                boundary_overlaps=sum(r['start_ns'] < end and r['end_ns'] > start and
                                      not(start <= r['start_ns'] and r['end_ns'] <= end) for r in rows))


def read_states(path):
    with open(path) as source:
        raw=list(csv.DictReader(line for line in source if not line.startswith('#')))
    rows=[]
    for r in raw:
        row={k:int(r[k]) for k in ('start_ns','end_ns','valid')}
        if row['valid'] not in (0,1) or row['end_ns'] < row['start_ns']:
            raise ValueError('Malformed query')
        row['run_state']=int(r['run_state']) if row['valid'] else None
        row['priority']=int(r['priority']) if row['valid'] and r.get('priority') else None
        for key in ('policy','base_priority','max_priority'):
            row[key]=int(r[key]) if row['valid'] and r.get(key) else None
        if rows and row['start_ns'] < rows[-1]['end_ns']:
            raise ValueError('Unordered/overlapping queries')
        rows.append(row)
    if not rows:
        raise ValueError('Empty state capture')
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('states');parser.add_argument('vi')
    parser.add_argument('--start-ns',type=int,required=True)
    parser.add_argument('--end-ns',type=int,required=True)
    args=parser.parse_args()
    rows=read_states(args.states)
    with open(args.vi) as source:
        ticks=[int(r['wall_ns']) for r in csv.DictReader(l for l in source if not l.startswith('#'))]
    if any(b<=a for a,b in zip(ticks,ticks[1:])):
        raise ValueError('Unordered VI timestamps')
    if not ticks or ticks[0]>args.start_ns or ticks[-1]<args.end_ns:
        raise ValueError('VI capture does not cover window')
    intervals=[(a,b) for a,b in zip(ticks,ticks[1:]) if args.start_ns<=a and b<=args.end_ns]
    longest=sorted(intervals,key=lambda pair:pair[1]-pair[0],reverse=True)[:10]
    gaps=[dict(start_ns=a['end_ns'],end_ns=b['start_ns'],gap_ms=(b['start_ns']-a['end_ns'])/1e6)
          for a,b in zip(rows,rows[1:]) if a['valid'] and b['valid'] and
          args.start_ns<=a['end_ns'] and b['start_ns']<=args.end_ns]
    print(json.dumps(dict(note='Snapshots only. State1 running/runnable; state3 waiting. Priority is pth_curpri, not QoS or App Nap evidence. No duration inference.',
                          window=observe(rows,args.start_ns,args.end_ns),
                          largest_inter_query_gaps=sorted(gaps,key=lambda g:g['gap_ms'],reverse=True)[:10],
                          longest=[dict(start_ns=a,end_ns=b,wall_ms=(b-a)/1e6,
                                        **observe(rows,a,b)) for a,b in longest]),indent=2))


if __name__=='__main__':main()
