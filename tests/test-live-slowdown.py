import importlib.util
from pathlib import Path
import unittest
from datetime import datetime

spec = importlib.util.spec_from_file_location('capture', Path(__file__).resolve().parents[1] /
                                             'scripts/capture-live-slowdown.py')
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class CaptureTests(unittest.TestCase):
    def test_optional_cadence_estimates(self):
        start = datetime(2026, 9, 8, 12).timestamp()
        line = ('2026-09-08 12:00:06.000 GalaxyPad [GalaxyPad frame window] '
                'seconds=5 presented=150 min_observed_fps=20.0')
        old = capture.frame_summary(line, start, start+7)['windows'][0]
        self.assertIsNone(old['vi_rate_estimate'])
        new = capture.frame_summary(line + ' vi_rate_estimate=60.0 emulation_speed_estimate=1.0',
                                    start, start+7)['windows'][0]
        self.assertEqual(new['vi_rate_estimate'], 60)
        self.assertEqual(new['emulation_speed_estimate'], 1)

    def test_vm(self):
        self.assertEqual(capture.vm_counters('Swapins: 12.\nSwapouts: 5.\n'),
                         {'Swapins': 12, 'Swapouts': 5})

    def test_weighted_and_boundaries(self):
        lines = '\n'.join(f'2026-09-08 12:00:{second:02d}.000 GalaxyPad [GalaxyPad frame window] '
                          f'seconds={duration} presented={count} min_observed_fps=20.0'
                          for second, duration, count in [(3, 5, 150), (8, 5, 150),
                                                          (14, 6, 120), (20, 6, 360)])
        start = datetime(2026, 9, 8, 12).timestamp()
        result = capture.frame_summary(lines, start, start + 15)
        self.assertEqual(len(result['windows']), 2)
        self.assertAlmostEqual(result['weighted_presented_fps'], 270 / 11)
        self.assertIsNone(capture.frame_summary('', start, start + 15)['weighted_presented_fps'])


if __name__ == '__main__':
    unittest.main()
