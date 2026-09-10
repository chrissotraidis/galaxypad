#!/usr/bin/env python3
"""Icon packaging preserves non-icon settings and rejects incomplete metadata."""
import pathlib
import plistlib
import runpy
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/compile-ios-icons.py"


class IconPackagingTests(unittest.TestCase):
    def test_merge_is_repeatable_and_preserves_app_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            info = pathlib.Path(directory) / "Info.plist"
            original = {"CFBundleIdentifier": "org.galaxypad.GalaxyPad",
                        "UIDeviceFamily": [1, 2], "UIRequiresFullScreen": True}
            info.write_bytes(plistlib.dumps(original))
            metadata = {"CFBundleIcons": {"CFBundlePrimaryIcon": {"CFBundleIconName": "AppIcon"}},
                        "CFBundleIcons~ipad": {"CFBundlePrimaryIcon": {"CFBundleIconName": "AppIcon"}},
                        "CFBundleIdentifier": "must-not-overwrite"}

            def actool(command, **kwargs):
                output = pathlib.Path(command[command.index("--output-partial-info-plist") + 1])
                output.write_bytes(plistlib.dumps(metadata))

            for sdk in ("iphonesimulator", "iphoneos"):
                with patch("sys.argv", [str(SCRIPT), "--bundle", directory, "--sdk", sdk]), \
                     patch("subprocess.run", side_effect=actool):
                    runpy.run_path(str(SCRIPT), run_name="__main__")
                result = plistlib.loads(info.read_bytes())
                self.assertEqual({key: result[key] for key in original}, original)
                self.assertEqual(result["CFBundleIcons"], metadata["CFBundleIcons"])
            before = info.read_bytes()
            del metadata["CFBundleIcons~ipad"]
            with patch("sys.argv", [str(SCRIPT), "--bundle", directory, "--sdk", "iphoneos"]), \
                 patch("subprocess.run", side_effect=actool), self.assertRaises(SystemExit):
                runpy.run_path(str(SCRIPT), run_name="__main__")
            self.assertEqual(info.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
