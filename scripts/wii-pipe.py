#!/usr/bin/env python3
"""Configure and drive GalaxyPad's deterministic Wii Pipe controller."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import time
from pathlib import Path


BUTTONS = {
    "A": "A",
    # This pinned Dolphin Pipe backend exposes Button B, but that input does
    # not reach the emulated Wii Remote B bit. Use independent Pipe tokens
    # that were verified at RMGE01's held-A+B title gate.
    "B": "X",
    "C": "B",
    "Z": "Z",
    "PLUS": "START",
    "MINUS": "Y",
    "SPIN": "L",
    "UP": "D_UP",
    "DOWN": "D_DOWN",
    "LEFT": "D_LEFT",
    "RIGHT": "D_RIGHT",
}


WIIMOTE_CONFIG = """[Wiimote1]
Device = Pipe/0/galaxypad
Buttons/A = `Button A`
Buttons/B = `Button X`
Buttons/- = `Button Y`
Buttons/+ = `Button START`
D-Pad/Up = `Button D_UP`
D-Pad/Down = `Button D_DOWN`
D-Pad/Left = `Button D_LEFT`
D-Pad/Right = `Button D_RIGHT`
IR/Up = `Axis C Y -`
IR/Down = `Axis C Y +`
IR/Left = `Axis C X -`
IR/Right = `Axis C X +`
IR/Center = 0.00 0.00
Shake/X = `Button L`
Shake/Y = `Button L`
Shake/Z = `Button L`
Extension = Nunchuk
Nunchuk/Buttons/C = `Button B`
Nunchuk/Buttons/Z = `Button Z`
Nunchuk/Stick/Up = `Axis MAIN Y -`
Nunchuk/Stick/Down = `Axis MAIN Y +`
Nunchuk/Stick/Left = `Axis MAIN X -`
Nunchuk/Stick/Right = `Axis MAIN X +`
Nunchuk/Stick/Calibration = 100 100 100 100 100 100 100 100
Options/Sideways Wiimote = False

[Wiimote2]
[Wiimote3]
[Wiimote4]
"""


def configure(user_dir: Path, force: bool) -> Path:
    config_dir = user_dir / "Config"
    pipes_dir = user_dir / "Pipes"
    config_dir.mkdir(parents=True, exist_ok=True)
    pipes_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "WiimoteNew.ini"
    if config_path.exists() and not force:
        raise RuntimeError(f"refusing to replace existing config: {config_path}")
    temporary = config_path.with_suffix(".ini.tmp")
    temporary.write_text(WIIMOTE_CONFIG, encoding="utf-8")
    os.replace(temporary, config_path)

    pipe_path = pipes_dir / "galaxypad"
    if pipe_path.exists():
        if not stat.S_ISFIFO(pipe_path.stat().st_mode):
            raise RuntimeError(f"existing pipe path is not a FIFO: {pipe_path}")
    else:
        os.mkfifo(pipe_path, 0o600)
    return pipe_path


def normalized_axis(value: object, name: str) -> float:
    number = float(value)
    if not -1.0 <= number <= 1.0:
        raise ValueError(f"{name} must be in [-1, 1]")
    return number


def axis_commands(axis: str, x: object, y: object) -> list[str]:
    nx = normalized_axis(x, "x")
    ny = normalized_axis(y, "y")
    raw_x = 0.5 + nx / 2.0
    raw_y = 0.5 - ny / 2.0
    return [f"SET {axis} {raw_x:.3f} {raw_y:.3f}"]


def encode_step(step: dict) -> tuple[list[str], float, float]:
    action = str(step.get("action", "tap")).lower()
    delay = float(step.get("delay", 0.0))
    hold = 0.0
    if delay < 0:
        raise ValueError("delay must be non-negative")
    if action in {"tap", "press", "release"}:
        semantic = str(step["button"]).upper()
        if semantic not in BUTTONS:
            raise ValueError(f"unsupported button: {semantic}")
        token = BUTTONS[semantic]
        if action == "tap":
            hold = float(step.get("hold", 0.12))
            if hold <= 0:
                raise ValueError("tap hold must be positive")
            return [f"PRESS {token}", f"RELEASE {token}"], delay, hold
        return [f"{action.upper()} {token}"], delay, hold
    if action == "nunchuk":
        return axis_commands("MAIN", step["x"], step["y"]), delay, hold
    if action == "pointer":
        return axis_commands("C", step["x"], step["y"]), delay, hold
    if action == "wait":
        wait = float(step.get("seconds", 1.0))
        if wait < 0:
            raise ValueError("wait must be non-negative")
        return [], delay + wait, hold
    raise ValueError(f"unsupported action: {action}")


def run_sequence(sequence: list[dict], pipe_path: Path | None, dry_run: bool) -> None:
    fd: int | None = None
    if not dry_run:
        fd = os.open(pipe_path, os.O_WRONLY)
    try:
        for step in sequence:
            commands, delay, hold = encode_step(step)
            if not dry_run and delay:
                time.sleep(delay)
            for index, command in enumerate(commands):
                print(command, flush=True)
                if fd is not None:
                    os.write(fd, (command + "\n").encode("ascii"))
                if index == 0 and hold and not dry_run:
                    time.sleep(hold)
    finally:
        if fd is not None:
            os.close(fd)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    configure_parser = commands.add_parser("configure")
    configure_parser.add_argument("--user-dir", type=Path, required=True)
    configure_parser.add_argument("--force", action="store_true")
    run_parser = commands.add_parser("run")
    run_parser.add_argument("--pipe", type=Path)
    run_parser.add_argument("--sequence", type=Path, required=True)
    run_parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        if args.command == "configure":
            print(configure(args.user_dir, args.force))
        else:
            if not args.dry_run and args.pipe is None:
                parser.error("run requires --pipe unless --dry-run is used")
            sequence = json.loads(args.sequence.read_text(encoding="utf-8"))
            if not isinstance(sequence, list) or not all(isinstance(x, dict) for x in sequence):
                raise ValueError("sequence must be a JSON list of objects")
            run_sequence(sequence, args.pipe, args.dry_run)
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"wii-pipe: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
