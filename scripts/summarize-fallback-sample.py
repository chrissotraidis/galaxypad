#!/usr/bin/env python3
"""CPU-thread wall-stack attribution; NOT running CPU time or vector provenance."""
import argparse
from collections import Counter
import json
import re
from pathlib import Path


def summarize(text):
    lines = text.split('Call graph:', 1)[1].splitlines()
    active = False
    roots = []
    stack = []
    total = None
    for line in lines:
        thread = re.match(r'^    (\d+) Thread_.*', line)
        if thread:
            if active:
                break
            active = line.endswith(': CPU thread') or line.endswith(': CPU-GPU thread')
            if active:
                total = int(thread[1])
            continue
        if not active:
            continue
        match = re.match(r'^([ +!:|`]*)(\d+) (.+?)  \(in ', line)
        if not match:
            if line.strip():
                raise ValueError('Unrecognized CPU call-tree line: ' + line)
            continue
        node = dict(depth=len(match[1]), count=int(match[2]), name=match[3], children=[])
        while stack and stack[-1]['depth'] >= node['depth']:
            stack.pop()
        (stack[-1]['children'] if stack else roots).append(node)
        stack.append(node)
    if total is None or sum(n['count'] for n in roots) != total:
        raise ValueError('Missing CPU thread or root sample conservation failure')
    leaves, groups = Counter(), Counter()

    def visit(node, interpreter=False):
        interpreter |= node['name'].startswith('Interpreter::')
        own = node['count'] - sum(c['count'] for c in node['children'])
        if own < 0:
            raise ValueError('Child samples exceed parent')
        leaves[node['name']] += own
        if interpreter:
            group = 'interpreter_stack'
        elif any(w in node['name'] for w in ('__psynch_cvwait', 'semaphore_wait',
                                             'mach_msg', '__ulock_wait', 'nanosleep')):
            group = 'recognized_wait'
        elif node['name'].startswith(('PowerPC::MMU::', 'PowerPC::InstructionCache::', 'HLE::')):
            group = 'shared_mmu_icache_hle_unattributed'
        else:
            group = 'other'
        groups[group] += own
        for child in node['children']:
            visit(child, interpreter)
    for root in roots:
        visit(root)
    assert sum(groups.values()) == sum(leaves.values()) == total
    # Symbol buckets use SELF counts only. Inlined helpers stay attributed to
    # their containing symbol; they cannot be recovered from collapsed offsets.
    symbols = Counter()
    chunks = []
    for name, count in leaves.items():
        if not count:
            continue
        if re.fullmatch(r'func_[0-9A-Fa-f]{8}', name):
            bucket = 'generated_chunks_including_inlined_work'
            chunks.append(dict(name=name, samples=count))
        elif name == 'chassis_dispatch':
            bucket = 'module_dispatch_symbol'
        elif name == 'StaticRecompCore::Run()':
            bucket = 'host_run_symbol'
        elif name.startswith(('moderngekko::ModManager::', 'StaticRecompCore::IsHostCallAddress(',
                              'StaticRecompCore::HookHostCall(')):
            bucket = 'hook_routing_symbols'
        elif name.startswith('ppc_'):
            bucket = 'out_of_line_ppc_helpers'
        else:
            bucket = 'remaining_symbols'
        symbols[bucket] += count
    assert sum(symbols.values()) == total
    chunks.sort(key=lambda row: (-row['samples'], row['name']))
    return dict(samples=total, groups=dict(groups), symbol_self_buckets=dict(symbols),
                generated_chunks=chunks,
                self_samples=[dict(name=n, samples=c) for n,c in leaves.most_common() if c],
                caveat='Wall-stack samples, not CPU-time percentages. Incomplete/tail-call '
                       'unwinds can hide interpreter ancestry; shared helpers remain unassigned. '
                       'No vector-PC provenance; no exhaustive fallback cost bound.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sample', type=Path)
    parser.add_argument('--output', type=Path, help='Write a new report; refuses overwrite')
    args = parser.parse_args()
    result = json.dumps(summarize(args.sample.read_text()), indent=2) + '\n'
    if args.output:
        with args.output.open('x') as output:
            output.write(result)
    else:
        print(result, end='')
