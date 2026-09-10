#!/usr/bin/env python3
"""Measure a fixed diagnostic window after the R85 trigger's first A press."""
import argparse
import csv
import json
import math


def measure(path):
    with open(path, newline="") as source:
        rows = list(csv.DictReader(source))
    press = next(r for r in rows if r["event"] == "input_sample" and int(r["value"]) != 0)
    start = int(press["steady_ns"]) + 20_000_000_000
    end = start + 60_000_000_000
    if int(rows[-1]["steady_ns"]) < end:
        raise ValueError("Trace ends before the complete 60-second window")
    result = {"path": path, "start_ns": start, "end_ns": end, "events": {}}
    for event in ("vi_end_field", "frame_begin", "present_done", "dma_enqueue"):
        times = sorted(int(r["steady_ns"]) for r in rows
                       if r["event"] == event and start <= int(r["steady_ns"]) < end)
        if len(times) < 2:
            raise ValueError(f"Insufficient {event} events")
        gaps = sorted((b - a) / 1e6 for a, b in zip(times, times[1:]))
        result["events"][event] = {
            "count": len(times), "hz": len(times) / 60,
            "p95_ms": gaps[math.ceil(len(gaps) * .95) - 1],
            "p99_ms": gaps[math.ceil(len(gaps) * .99) - 1],
            "gaps_ge_20ms": sum(g >= 20 for g in gaps),
        }
    result["dma_khz"] = result["events"]["dma_enqueue"]["count"] * 128 / 60 / 1000
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces", nargs="+")
    args = parser.parse_args()
    print(json.dumps([measure(path) for path in args.traces], indent=2))
