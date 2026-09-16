#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('regions', Path(__file__).resolve().parents[1] / 'scripts/analyze-region-feasibility.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Regions(unittest.TestCase):
    def fixture(self, ops):
        return '\n'.join(f'label_{0x1000 + 4*i:08X}:\n // {0x1000 + 4*i:08X}: {op}' for i, op in enumerate(ops))

    def test_memory_is_only_hypothetically_transparent(self):
        records = m.parse(self.fixture(['ps_mul', 'psq_st', 'ps_add', 'blr']))
        self.assertEqual([s['fp'] for s in m.windows(records, False)], [1, 1])
        self.assertEqual([s['fp'] for s in m.windows(records, True)], [2])

    def test_unknown_control_and_status_are_barriers(self):
        for op in ['mffs', 'mtfsf', 'bl', 'bc', 'rfi', 'sc', 'mystery', 'lwarx', 'stwcx.']:
            self.assertEqual(m.classify(op), 'barrier')
            spans = m.windows(m.parse(self.fixture(['fadd', op, 'fmul'])), True)
            self.assertEqual([s['fp'] for s in spans], [1, 1])

    def test_integer_gap_and_record_form(self):
        spans = m.windows(m.parse(self.fixture(['ps_mul.', 'addi', 'ps_add'])), False)
        self.assertEqual((spans[0]['fp'], spans[0]['instructions']), (2, 3))

    def test_address_gap(self):
        records = [(0x1000, 'fadd', 'fp'), (0x1008, 'fmul', 'fp')]
        self.assertEqual(len(m.windows(records, True)), 2)

    def test_malformed_annotations(self):
        with self.assertRaises(ValueError):
            m.parse('// 00001000: fadd')
        with self.assertRaises(ValueError):
            m.parse(self.fixture(['fadd']) + '\n' + self.fixture(['fmul']))
        self.assertEqual(len(m.parse(self.fixture(['fadd']) + '\n' + self.fixture(['fadd']))), 1)

if __name__ == '__main__':
    unittest.main()
