#!/usr/bin/env python3
"""Verify actual Git submodule pin and cleanliness behavior with local fixtures."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dependency_lock', ROOT / 'scripts/dependency-lock.py')
lock_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lock_module)


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], stderr=subprocess.DEVNULL).decode().strip()


class DependencyLockTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        def repository(name):
            path = self.base / name
            path.mkdir()
            git(path, 'init', '-q')
            git(path, 'config', 'user.name', 'Fixture')
            git(path, 'config', 'user.email', 'fixture@example.invalid')
            (path / 'source.cpp').write_text('int reviewed;\n')
            (path / '.gitignore').write_text('/build/\n')
            git(path, 'add', '.')
            git(path, 'commit', '-qm', 'fixture')
            return path
        def add(parent, child, relative):
            git(parent, '-c', 'protocol.file.allow=always', 'submodule', 'add', str(child), relative)
            git(parent, 'commit', '-qam', 'pin child')
        dol = repository('dol')
        core = repository('core'); add(core, dol, 'DolRecomp')
        modern = repository('modern'); add(modern, core, 'vendor/dolphin')
        self.root = repository('project'); add(self.root, modern, 'ref/ModernGekko')
        git(self.root, '-c', 'protocol.file.allow=always', 'submodule', 'update', '--init', '--recursive')
        revisions = {name: git(path, 'rev-parse', 'HEAD') for name, path in
                     [('modernGekko', modern), ('recompCore', core), ('dolRecomp', dol)]}
        urls = {'modernGekko': str(modern), 'recompCore': str(core), 'dolRecomp': str(dol)}
        self.lock = {'repositories': {name: {'revision': revision, 'url': urls[name]} for name, revision in revisions.items()},
                     'vendorRevisions': {'modernGekkoRecompCoreDolphin': revisions['recompCore']}}
        (self.root / 'config').mkdir()
        self.write_lock()
        self.modern = self.root / 'ref/ModernGekko'
        self.core = self.modern / 'vendor/dolphin'
        self.dol = self.core / 'DolRecomp'

    def write_lock(self):
        (self.root / 'config/dependencies.lock.json').write_text(json.dumps(self.lock))

    def test_clean_pins_and_ignored_build_products(self):
        (self.dol / 'build').mkdir()
        (self.dol / 'build/output.o').write_text('build product')
        before = git(self.root, 'status', '--porcelain')
        lock_module.verify(self.root)
        self.assertEqual(git(self.root, 'status', '--porcelain'), before)

    def test_dirty_source_rejected_without_mutation(self):
        source = self.dol / 'source.cpp'
        source.write_text('int unreviewed;\n')
        with self.assertRaises(ValueError): lock_module.verify(self.root)
        self.assertEqual(source.read_text(), 'int unreviewed;\n')

    def test_nonignored_extra_source_rejected(self):
        (self.modern / 'extra.cpp').write_text('int extra;\n')
        with self.assertRaises(ValueError): lock_module.verify(self.root)

    def test_root_gitlink_mismatch_rejected(self):
        self.lock['repositories']['modernGekko']['revision'] = '1' * 40
        self.write_lock()
        with self.assertRaisesRegex(ValueError, 'parent gitlink'): lock_module.verify(self.root)

    def test_nested_gitlink_mismatch_rejected(self):
        git(self.core, 'update-index', '--cacheinfo', '160000,' + '1' * 40 + ',DolRecomp')
        with self.assertRaises(ValueError): lock_module.verify(self.root)

    def test_head_mismatch_rejected_even_if_lock_and_index_agree(self):
        expected = git(self.modern, 'rev-parse', 'HEAD')
        git(self.modern, 'checkout', '--detach', 'HEAD^')
        self.assertEqual(self.lock['repositories']['modernGekko']['revision'], expected)
        with self.assertRaises(ValueError): lock_module.verify(self.root)

    def test_missing_dependency_rejected(self):
        git(self.root, 'submodule', 'deinit', '-f', 'ref/ModernGekko')
        with self.assertRaises((ValueError, subprocess.CalledProcessError)): lock_module.verify(self.root)

    def test_missing_gitmodules_rejected(self):
        (self.root / '.gitmodules').unlink()
        with self.assertRaisesRegex(ValueError, '.gitmodules is missing'): lock_module.verify(self.root)

    def test_wrong_declared_url_rejected(self):
        git(self.root, 'config', '--file', '.gitmodules', 'submodule.ref/ModernGekko.url', 'https://example.invalid/wrong.git')
        with self.assertRaisesRegex(ValueError, 'URL does not match'): lock_module.verify(self.root)

    def test_wrong_declared_path_rejected(self):
        git(self.root, 'config', '--file', '.gitmodules', 'submodule.ref/ModernGekko.path', 'ref/wrong')
        with self.assertRaisesRegex(ValueError, 'exactly one path'): lock_module.verify(self.root)

    def test_local_mirror_override_is_allowed(self):
        git(self.modern, 'remote', 'set-url', 'origin', str(self.base / 'offline-mirror'))
        lock_module.verify(self.root)


if __name__ == '__main__': unittest.main()
