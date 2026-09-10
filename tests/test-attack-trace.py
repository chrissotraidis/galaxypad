import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "attack", Path(__file__).resolve().parents[1] / "scripts/measure-attack-trace.py")
attack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attack)


class AttackTraceTest(unittest.TestCase):
    def test_boundaries_and_incomplete_window(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.csv"
            rows = ["ordinal,steady_ns,event,value", "0,0,input_sample,1"]
            for event in ("vi_end_field", "frame_begin", "present_done", "dma_enqueue"):
                for stamp in (19_999_999_999, 20_000_000_000, 20_010_000_000, 80_000_000_000):
                    rows.append(f"1,{stamp},{event},0")
            path.write_text("\n".join(rows) + "\n")
            result = attack.measure(str(path))
            self.assertEqual(result["events"]["frame_begin"]["count"], 2)
            self.assertEqual(result["events"]["frame_begin"]["p99_ms"], 10)
            self.assertAlmostEqual(result["dma_khz"], 256 / 60000)
            path.write_text("\n".join(r for r in rows if ",80000000000," not in r) + "\n")
            with self.assertRaisesRegex(ValueError, "complete"):
                attack.measure(str(path))


if __name__ == "__main__":
    unittest.main()
