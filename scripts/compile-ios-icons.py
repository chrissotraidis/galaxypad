#!/usr/bin/env python3
"""Compile project-owned icons and merge only Apple's icon metadata into the bundle."""
import argparse
import pathlib
import plistlib
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("--bundle", type=pathlib.Path, required=True)
parser.add_argument("--sdk", choices=("iphoneos", "iphonesimulator"), required=True)
args = parser.parse_args()
root = pathlib.Path(__file__).resolve().parents[1]
info_path = args.bundle / "Info.plist"
with info_path.open("rb") as stream:
    info = plistlib.load(stream)
with tempfile.TemporaryDirectory(prefix="galaxypad-icons-") as temporary:
    partial = pathlib.Path(temporary) / "icons.plist"
    subprocess.run([
        "xcrun", "--sdk", args.sdk, "actool",
        str(root / "apple/ios/Assets.xcassets"),
        "--compile", str(args.bundle), "--platform", args.sdk,
        "--minimum-deployment-target", "16.0", "--target-device", "iphone",
        "--target-device", "ipad", "--app-icon", "AppIcon",
        "--output-partial-info-plist", str(partial),
        "--warnings", "--errors",
    ], check=True)
    with partial.open("rb") as stream:
        metadata = plistlib.load(stream)
    for key in ("CFBundleIcons", "CFBundleIcons~ipad"):
        if key not in metadata:
            raise SystemExit(f"actool did not produce {key}")
        info[key] = metadata[key]
with info_path.open("wb") as stream:
    plistlib.dump(info, stream)
