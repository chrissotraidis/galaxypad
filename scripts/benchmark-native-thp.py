#!/usr/bin/env python3
"""Private, bounded native THP throughput probe; no game integration or pixel oracle."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--ffmpeg", required=True, type=Path)
parser.add_argument("--movie", required=True, type=Path)
parser.add_argument("--frames", type=int, default=600)
parser.add_argument("--runs", type=int, default=3)
args = parser.parse_args()
if not 1 <= args.frames <= 6000 or not 1 <= args.runs <= 5:
    parser.error("frames must be 1..6000 and runs 1..5")
binary, movie = args.ffmpeg.resolve(strict=True), args.movie.resolve(strict=True)
for run in range(args.runs):
    command = [str(binary), "-nostdin", "-hide_banner", "-nostats", "-benchmark",
               "-xerror", "-threads", "1", "-i", str(movie), "-map", "0:v:0",
               "-an", "-sn", "-dn", "-filter_threads", "1", "-frames:v",
               str(args.frames), "-fps_mode", "passthrough", "-f", "null", "-"]
    start = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    wall = time.monotonic() - start
    frames = re.findall(r"frame=\s*(\d+)", result.stderr)
    timing = re.search(r"utime=([\d.]+)s stime=([\d.]+)s rtime=([\d.]+)s", result.stderr)
    if result.returncode or not frames or not timing:
        raise SystemExit(result.stderr or "Missing FFmpeg benchmark result")
    count = int(frames[-1])
    if count != args.frames:
        raise SystemExit(f"Expected {args.frames} decoded frames, got {count}")
    user, system, realtime = map(float, timing.groups())
    print(json.dumps({"run": run + 1, "frames": count, "wall_seconds": wall,
                      "fps_wall": count / wall, "ms_per_frame_wall": wall * 1000 / count,
                      "cpu_seconds": user + system, "ffmpeg_realtime_seconds": realtime,
                      "scope": "native software video decode to null; no audio, upload or parity proof"}),
          flush=True)
    print(result.stderr, flush=True)
