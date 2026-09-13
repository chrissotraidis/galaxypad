#!/usr/bin/env python3
"""Compare dependency sources with HEAD plus an ordered, reviewed patch stack.

The temporary index never changes the checkout or its real staging area.
The named child submodule is checked separately by bootstrap. Git-ignored
generated/build inputs are outside this source comparison.
"""

import os
from pathlib import Path
import subprocess
import sys
import tempfile


def verify(checkout, child, patches):
    with tempfile.TemporaryDirectory(prefix="galaxypad-dependency-index-") as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}

        def git(*args):
            return subprocess.check_output(
                ["git", "-C", str(checkout), *args], env=env
            )

        git("read-tree", "HEAD")
        for patch in patches:
            git("apply", "--cached", str(Path(patch).resolve()))

        changed = git("diff", "--name-only", "-z", "--ignore-submodules=none")
        untracked = git("ls-files", "--others", "--exclude-standard", "-z")
        unexpected = sorted(
            os.fsdecode(path)
            for path in set((changed + untracked).split(b"\0"))
            if path and os.fsdecode(path) != child
        )
        if unexpected:
            for path in unexpected:
                print(f"unexpected local dependency change: {checkout}/{path}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: verify-dependency-tree.py CHECKOUT CHILD_SUBMODULE [PATCH ...]")
    try:
        sys.exit(verify(sys.argv[1], sys.argv[2], sys.argv[3:]))
    except subprocess.CalledProcessError as error:
        sys.exit(f"could not reconstruct reviewed dependency tree (git exited {error.returncode})")
