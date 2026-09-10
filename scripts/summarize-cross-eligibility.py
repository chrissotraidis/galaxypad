#!/usr/bin/env python3
"""Summarize private cross-island counters; never infer FPS or scene CPU share."""
import argparse
import hashlib
import json
from pathlib import Path
import re

def summarize(text,start_line=1,end_line=None):
    lines=text.splitlines()
    if start_line<1 or (end_line is not None and end_line<start_line):
        raise ValueError('Invalid inclusive line window')
    text='\n'.join(lines[start_line-1:end_line])
    matches=re.findall(r'\[cross-island-(r804|r807)\] calls=(\d+) fast=(\d+) mode=(\d+) range=(\d+) ties=(\d+)',text)
    if len({m[0] for m in matches})>1:raise ValueError('Mixed diagnostic versions')
    rows=[tuple(map(int,m[1:])) for m in matches]
    if len(rows)<2:raise ValueError('Need two complete counter observations')
    for row in rows:
        if row[0]!=sum(row[1:]):raise ValueError('Outcome totals do not equal calls')
    for before,after in zip(rows,rows[1:]):
        if any(b<a for a,b in zip(before,after)):raise ValueError('Counters reset or decreased')
    delta=[b-a for a,b in zip(rows[0],rows[-1])]
    if not delta[0]:raise ValueError('No calls between observations')
    return dict(diagnostic=matches[0][0],line_window=[start_line,min(end_line or len(lines),len(lines))],
                observations=len(rows),first=rows[0],last=rows[-1],
                delta=dict(zip(['calls','fast','mode','range','ties'],delta)),
                fast_fraction=delta[1]/delta[0],
                caveat='Counter window only; no FPS, time interval or CPU-share inference')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('log',type=Path)
    parser.add_argument('--start-line',type=int,default=1)
    parser.add_argument('--end-line',type=int)
    args=parser.parse_args();raw=args.log.read_bytes()
    result=summarize(raw.decode(),args.start_line,args.end_line);result['log_sha256']=hashlib.sha256(raw).hexdigest()
    print(json.dumps(result,indent=2))
