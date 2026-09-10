#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('audio_summary',
    Path(__file__).resolve().parents[1] / 'scripts/summarize-audio-window.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(time, count, available=1):
    values = dict.fromkeys(module.COUNTERS, count)
    values.update(mono_before=time, mono_after=time + .001,
                  output_counters_available=available)
    return '[GalaxyPad audio counters] ' + ' '.join(f'{k}={v}' for k, v in values.items())


class SummaryTests(unittest.TestCase):
    def test_delta_and_brackets(self):
        result = module.summarize('\n'.join([row(5, 0), row(10, 100),
                                            row(15, 240100), row(20, 0)]), 9, 16)
        self.assertEqual(result['delta']['output_frames'], 240000)
        low, high = result['output_frames_per_second_bounds']
        self.assertLess(low, 48000)
        self.assertGreater(high, 48000)

    def test_reject_reset_gap_unavailable_and_insufficient(self):
        for text in [row(10, 100) + '\n' + row(15, 0),
                     row(10, 0) + '\n' + row(20, 100),
                     row(10, 0, 0) + '\n' + row(15, 100),
                     row(10, 0)]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                module.summarize(text, 0, 30)


if __name__ == '__main__':
    unittest.main()
