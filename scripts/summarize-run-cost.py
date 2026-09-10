#!/usr/bin/env python3
"""Sparse CPU-thread branch attribution. Estimates are not game FPS or speedups."""
import argparse
import json
import math
from pathlib import Path
import re


def summarize(log, run=None):
    if run is not None:
        boundaries = list(re.finditer(r'\[galaxypad-run-cost\] capture-start pc=', log))
        if not 1 <= run <= len(boundaries):
            raise ValueError('Selected Run does not exist')
        start = boundaries[run - 1].start()
        end = boundaries[run].start() if run < len(boundaries) else len(log)
        log = log[start:end]
    starts = re.findall(r'\[galaxypad-run-cost\] capture-start pc=([0-9a-f]{8})', log)
    reports = re.findall(r'\[galaxypad-run-cost\] cpu_ns=(\d+) clock_errors=(\d+) inclusion=(\d+)', log)
    lanes = re.findall(r'\[galaxypad-run-cost-lane\] lane=(\d+) spans=(\d+) selected=(\d+) '
                       r'completed=(\d+) ns=(\d+) squared_ns=(\d+) maximum_ns=(\d+)', log)
    if len(starts) != 1 or len(reports) != 1 or len(lanes) != 2:
        raise ValueError('Require one activated complete Run report and exactly two lanes')
    cpu_ns, errors, inclusion = map(int, reports[0])
    if cpu_ns <= 0 or errors or inclusion != 256:
        raise ValueError('Invalid clock, denominator or unsupported inclusion rate')
    result = []
    seen = set()
    for raw in lanes:
        lane, spans, selected, completed, ns, squares, maximum = map(int, raw)
        if lane not in (0, 1) or lane in seen or completed != selected or selected > spans:
            raise ValueError('Inconsistent lane/sample counts')
        seen.add(lane)
        if (not selected and (ns or squares or maximum)) or maximum > ns:
            raise ValueError('Inconsistent empty sample or maximum')
        if selected and (ns > selected * maximum or squares > ns * maximum * (1 + 1e-12)
                         or squares * selected < ns * ns * (1 - 1e-12)):
            raise ValueError('Inconsistent sample moments')
        estimate = ns * inclusion
        # Bernoulli-inclusion total estimator and estimated variance. The fixed
        # PRNG and workload correlations weaken nominal confidence coverage.
        se = math.sqrt((1 - 1 / inclusion) * inclusion**2 * squares)
        result.append(dict(lane=('native' if lane == 0 else 'non_native_routing'),
            spans=spans, selected=selected, sampled_cpu_ns=ns, maximum_sample_ns=maximum,
            estimated_cpu_ns=estimate, estimated_cpu_fraction=estimate/cpu_ns,
            approximate_95_halfwidth_fraction=(1.96*se/cpu_ns if selected else None),
            ratio_estimate_fraction=(spans * ns / selected / cpu_ns if selected else None),
            enough_samples_for_screening=selected >= 30))
    return dict(cpu_ns=cpu_ns, capture_pc=starts[0], selected_run=run, lanes=result,
        caveat='Inclusive native/non-native branches; outer routing/timing is unassigned. '
               'Pseudo-random sparse estimates include clock/diagnostic overhead. Nominal '
               'intervals assume independent inclusion, not proven PRNG/workload independence. '
               'Do not force fractions to sum to one, subtract assumed overhead or infer FPS.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--run', type=int, help='Explicit one-based Run selection; never merge pauses')
    args = parser.parse_args()
    print(json.dumps(summarize(args.log.read_text(), args.run), indent=2))
