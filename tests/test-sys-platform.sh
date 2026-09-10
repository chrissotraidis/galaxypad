#!/usr/bin/env bash
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
python3 - "$root" <<'PY'
import pathlib
import subprocess
import sys

source = (pathlib.Path(sys.argv[1]) / "ref/ModernGekko/vendor/dolphin/Source/Core/Common/FileUtil.cpp").read_text()
body = source.split("static std::string CreateSysDirectoryPath()", 1)[1]
selector = body[body.index("#if"):].split("\n#if defined(__APPLE__)\n", 1)[0]

def resolve(flags, code=selector):
    return subprocess.check_output(
        ["clang", "-E", "-P", "-x", "c", "-undef", *flags, "-"],
        input=code + "\nSYSDATA_DIR\n", text=True).strip()

cases = [
    (["-D__APPLE__", "-DTARGET_OS_IPHONE=0", "-DLINUX_LOCAL_DEV"], '"Contents/Resources/Sys"'),
    (["-D__APPLE__", "-DTARGET_OS_IPHONE=0"], '"Contents/Resources/Sys"'),
    (["-D__APPLE__", "-DTARGET_OS_IPHONE=1", "-DLINUX_LOCAL_DEV"], '"Sys"'),
    (["-DLINUX_LOCAL_DEV"], '"Sys"'),
    (["-D_WIN32"], '"Sys"'),
]
for flags, expected in cases:
    actual = resolve(flags)
    assert actual == expected, (flags, actual, expected)
# Prove coverage of the actual desktop-build regression, not just ordinary macOS.
old = selector.replace('(defined(LINUX_LOCAL_DEV) && !defined(__APPLE__))', 'defined(LINUX_LOCAL_DEV)')
assert resolve(cases[0][0], old) == '"Sys"'
print("Sys platform selection tests passed")
PY
