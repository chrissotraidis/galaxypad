#!/usr/bin/env python3
"""Exercise dependency verification with real Git repositories, without downloads."""

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dependency_tree", ROOT / "scripts/verify-dependency-tree.py")
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class DependencyTreeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / "repository"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.file = self.repo / "source with spaces.txt"
        self.file.write_text("original\n" + "unchanged\n" * 20)
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.file.write_text(self.file.read_text().replace("original", "reviewed", 1))
        self.patch = self.base / "reviewed.patch"
        self.patch.write_bytes(self.git("diff", "--binary"))

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args])

    def check(self, patches=None):
        return verifier.verify(self.repo, "", patches or [self.patch])

    def test_reviewed_tree_passes_without_changing_index(self):
        before = (self.repo / ".git/index").read_bytes()
        self.assertEqual(self.check(), 0)
        self.assertEqual((self.repo / ".git/index").read_bytes(), before)

    def test_unrelated_edit_inside_reviewed_file_is_rejected_and_preserved(self):
        self.file.write_text(self.file.read_text() + "unreviewed build flag\n")
        before = self.file.read_bytes()
        self.assertEqual(self.check(), 1)
        self.assertEqual(self.file.read_bytes(), before)

    def test_untracked_file_is_rejected(self):
        (self.repo / "unexpected.txt").write_text("unreviewed\n")
        self.assertEqual(self.check(), 1)

    def test_mode_change_is_rejected(self):
        self.git("config", "core.fileMode", "true")
        self.file.chmod(0o755)
        self.assertEqual(self.check(), 1)

    def test_overlapping_patches_and_new_file_are_accepted(self):
        self.git("add", ".")
        self.file.write_text(self.file.read_text().replace("reviewed", "second review", 1))
        new_file = self.repo / "new header.h"
        new_file.write_text("// reviewed addition\n")
        self.git("add", "-N", str(new_file))
        second = self.base / "second.patch"
        second.write_bytes(self.git("diff", "--binary"))
        self.assertEqual(self.check([self.patch, second]), 0)

    def test_existing_worktree_checkout_is_accepted(self):
        worktree = self.base / "worktree"
        revision = self.git("rev-parse", "HEAD").decode().strip()
        self.git("worktree", "add", "--detach", str(worktree), revision)
        self.git("remote", "add", "origin", "https://example.invalid/dependency.git")
        bootstrap = (ROOT / "scripts/bootstrap-dependencies.sh").read_text()
        function = bootstrap.split("ensure_checkout() {", 1)[1].split("\nrequire_clean()", 1)[0]
        result = subprocess.run(
            ["bash", "-euc", "ensure_checkout() {" + function + '\nensure_checkout "$1" "$2" "$3"',
             "fixture", "https://example.invalid/dependency.git", str(worktree), revision],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
