#!/usr/bin/env python3
import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location(
    "result", pathlib.Path(__file__).with_name("check-mobile-ui-result.py"))
result = importlib.util.module_from_spec(spec)
spec.loader.exec_module(result)


class ResultTests(unittest.TestCase):
    def test_false_launcher_success(self):
        self.assertFalse(result.passed("FAIL: default A leaves the observed Gateway inventory HUD clear\norg.galaxypad.overlay-tests: 95041\n"))

    def test_incomplete_or_ambiguous(self):
        for output in ("", "org.galaxypad.overlay-tests: 1", "crashed",
                       "GALAXYPAD_UI_TEST_PASS\n" * 2,
                       "FAIL: spacing\nGALAXYPAD_UI_TEST_PASS\n"):
            self.assertFalse(result.passed(output))

    def test_completed(self):
        self.assertTrue(result.passed("system warning\nGALAXYPAD_UI_TEST_PASS\norg.galaxypad.overlay-tests: 2\n"))


if __name__ == "__main__":
    unittest.main()
