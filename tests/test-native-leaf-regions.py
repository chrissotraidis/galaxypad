#!/usr/bin/env python3
"""Structural candidate selection must fail closed on unsupported CFGs."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('leaf', Path(__file__).resolve().parents[1] / 'scripts/audit-native-leaf-regions.py')
leaf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(leaf)


class Regions(unittest.TestCase):
    def run_case(self, body, extra=None):
        code = {0: ('bl', '0x00000100')}
        code.update({0x100 + 4 * i: item for i, item in enumerate(body)})
        code.update(extra or {})
        return leaf.audit(code)

    def test_leaf(self):
        result = self.run_case([('addi', 'r3, r3, 1'), ('blr', '')])
        self.assertEqual(result['candidates'][0]['pcs'], ['00000100', '00000104'])

    def test_conditional_returns(self):
        result = self.run_case([('bc', '12, 2, 0x00000108'), ('blr', ''), ('blr', '')])
        self.assertEqual(len(result['candidates']), 1)

    def test_cycle(self):
        self.assertEqual(self.run_case([('b', '0x00000104'), ('b', '0x00000100')])['rejected'], {'loop': 1})

    def test_missing(self):
        self.assertEqual(self.run_case([('addi', 'r3, r3, 1')])['rejected'], {'missing_instruction': 1})

    def test_nested_call(self):
        result = self.run_case([('bl', '0x00000200'), ('blr', '')], {0x200: ('blr', '')})
        self.assertEqual(result['rejected'], {'nested_call': 1})

    def test_indirect_and_system(self):
        for op in ('bctr', 'bctrl', 'sc', 'rfi', 'unknown'):
            self.assertEqual(self.run_case([(op, '')])['rejected'], {'system_indirect_or_unknown': 1})

    def test_external_interior(self):
        result = self.run_case([('addi', 'r3, r3, 1'), ('blr', '')], {0x200: ('b', '0x00000104')})
        self.assertEqual(result['rejected'], {'external_interior_branch': 1})

    def test_tail_entry(self):
        result = self.run_case([('b', '0x00000200')], {4: ('bl', '0x00000200'), 0x200: ('blr', '')})
        self.assertEqual(result['rejected'], {'another_call_entry': 1})

    def test_cross_chunk_and_fallthrough(self):
        code = {0: ('bl', '0x00000100'), 0x100: ('b', '0x00000200'), 0x200: ('blr', '')}
        self.assertEqual(len(leaf.audit(code)['candidates']), 1)
        code[0x1fc] = ('addi', 'r3, r3, 1')
        self.assertEqual(leaf.audit(code)['rejected'], {'external_interior_fallthrough': 1})

    def test_annotation_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'chunk.c'
            path.write_text('label_00000100:\n // 00000100: blr\n')
            code, _ = leaf.parse_sources([path, path])
            self.assertEqual(code, {0x100: ('blr', '')})
            path.write_text('// 00000100: blr\n')
            with self.assertRaises(ValueError):
                leaf.parse_sources([path])

    def test_closed_calls(self):
        code = {0: ('bl', '0x00000100'), 0x100: ('bl', '0x00000200'),
                0x104: ('blr', ''), 0x200: ('blr', '')}
        candidates = leaf.audit(code, allow_calls=True)['candidates']
        self.assertEqual(len(leaf.closed_calls(candidates)), 2)
        code[0x200] = ('bl', '0x00000100')
        code[0x204] = ('blr', '')
        self.assertEqual(leaf.closed_calls(leaf.audit(code, allow_calls=True)['candidates']), [])
        code[0x200] = ('bctr', '')
        self.assertEqual(leaf.closed_calls(leaf.audit(code, allow_calls=True)['candidates']), [])


if __name__ == '__main__':
    unittest.main()
