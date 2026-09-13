#!/usr/bin/env python3
"""Exercise the public-content gate in a repository without build inputs."""
from pathlib import Path
import shutil
import subprocess
import tempfile

source = Path(__file__).resolve().parents[1] / "scripts/check-public-content.sh"
with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    (root / "scripts").mkdir()
    shutil.copyfile(source, root / "scripts/check-public-content.sh")
    subprocess.run(["git", "init", "-q", str(root)], check=True)

    def check():
        return subprocess.run(["bash", "scripts/check-public-content.sh"], cwd=root,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT).returncode

    (root / ".env.example").write_text("EXAMPLE=value\n")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    assert check() == 0, "clean source and example environment must pass"
    for name in ("disc.RvZ", "disc.gcm", "GameData.bin", "identity.cer", ".env.local",
                 "generated/module.c", "save/progress.bin", "credential.txt"):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("-----BEGIN " + "PRIVATE KEY-----" if name == "credential.txt" else "fixture")
        subprocess.run(["git", "add", "-f", name], cwd=root, check=True)
        assert check() != 0, f"accepted prohibited fixture: {name}"
        subprocess.run(["git", "rm", "-q", "-f", name], cwd=root, check=True)
    assert check() == 0
print("Public content positive and negative fixtures passed")
