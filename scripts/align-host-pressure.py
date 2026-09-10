"""Bracket VI hitches with host snapshots. Brackets are wider than the hitch."""
import argparse
import csv
import json

COUNTERS=('cpu_user_ticks','cpu_system_ticks','cpu_idle_ticks','cpu_nice_ticks',
          'pageins','pageouts','swapins','swapouts','compressions','decompressions')


def bracket(rows,start,end):
    if end<=start:raise ValueError('Nonpositive interval')
    before=[r for r in rows if r['end_ns']<=start]
    after=[r for r in rows if r['start_ns']>=end]
    if not before or not after:return dict(covered=False)
    a,b=before[-1],after[0]
    result=dict(covered=True,snapshot_freshness='unknown_kernel_cache',start_ns=a['start_ns'],end_ns=b['end_ns'],
                bracket_ms=(b['end_ns']-a['start_ns'])/1e6)
    if not a['valid'] or not b['valid']:
        return dict(result,valid=False)
    delta={k:b[k]-a[k] if b[k]>=a[k] else None for k in COUNTERS}
    ticks=[delta[k] for k in COUNTERS[:4]]
    total=sum(ticks) if all(v is not None for v in ticks) else None
    return dict(result,valid=True,deltas=delta,
                aggregate_idle_percent=100*delta['cpu_idle_ticks']/total if total else None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('host');parser.add_argument('aligned_states')
    args=parser.parse_args()
    with open(args.host) as source:
        rows=[]
        for r in csv.DictReader(source):
            row={k:int(r[k]) for k in ('start_ns','end_ns','valid')}
            if row['valid'] not in (0,1) or row['end_ns']<row['start_ns']:
                raise ValueError('Invalid host query')
            if rows and row['start_ns']<rows[-1]['end_ns']:
                raise ValueError('Overlapping/unordered host queries')
            row.update({k:int(r[k]) if row['valid'] else None for k in COUNTERS})
            rows.append(row)
    with open(args.aligned_states) as source:intervals=json.load(source)['longest']
    print(json.dumps(dict(note='Host statistics may be kernel-cached: query timestamps are not counter refresh times. Deltas cannot exclude short pressure bursts. Aggregate CPU counters cannot resolve per-core scheduling.',
                          intervals=[dict(vi_start_ns=i['start_ns'],vi_end_ns=i['end_ns'],
                                          wall_ms=i['wall_ms'],host=bracket(rows,i['start_ns'],i['end_ns']))
                                     for i in intervals]),indent=2))


if __name__=='__main__':main()
