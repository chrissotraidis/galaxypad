import importlib.util
import pathlib
import plistlib
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', pathlib.Path(__file__).parents[1] / 'scripts/ipad-install-assistant.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.app = pathlib.Path(self.temp.name) / 'GalaxyPad.app'
        (self.app / 'Frameworks').mkdir(parents=True)
        (self.app / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': 'org.galaxypad.GalaxyPad'}))
        (self.app / 'GalaxyPad').touch()
        (self.app / 'Frameworks/gRMGE01_recomp.dylib').touch()

    def test_device_validation_without_install(self):
        with patch.object(installer, 'run', side_effect=['arm64', ' platform IOS', 'arm64', ' platform IOS']) as command:
            self.assertEqual(installer.validate(self.app), self.app)
            self.assertEqual(command.call_count, 4)

    def test_simulator_rejected(self):
        with patch.object(installer, 'run', side_effect=['arm64', ' platform IOSSIMULATOR']):
            with self.assertRaisesRegex(ValueError, 'not an iOS device'):
                installer.validate(self.app)

    def test_unsigned_rejected_for_install(self):
        with patch.object(installer, 'run', side_effect=['arm64', ' platform IOS', 'arm64', ' platform IOS']):
            with self.assertRaisesRegex(ValueError, 'No provisioning profile'):
                installer.validate(self.app, signed=True)

    def test_wrong_bundle_and_symlink_rejected(self):
        (self.app / 'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': 'other'}))
        with self.assertRaisesRegex(ValueError, 'Bundle identifier'):
            installer.validate(self.app)
        link = self.app.parent / 'Alias.app'
        link.symlink_to(self.app)
        with self.assertRaises(ValueError):
            installer.validate(link)


if __name__ == '__main__':
    unittest.main()
