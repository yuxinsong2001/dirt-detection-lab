import copy
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "tools/build_performance_summary.py"
SPEC = importlib.util.spec_from_file_location("performance_summary", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PerformanceSummaryTests(unittest.TestCase):
    def setUp(self):
        self.source = MODULE.read_json(MODULE.SOURCE)

    def test_separate_sources_and_units(self):
        n, s = MODULE.build_rows(self.source, MODULE.OFFICIAL)
        self.assertEqual(n["map50_95_standard_pct"], 40.9)
        self.assertEqual(n["map50_95_e2e_pct"], 40.1)
        self.assertAlmostEqual(n["checkpoint_saved_map50_95_pct"], 40.116)
        self.assertEqual(s["checkpoint_coco_epochs"], 70)
        self.assertIsNone(n["cpu_hardware"])
        self.assertIn("not_verified", n["checkpoint_saved_head"])

    def test_mixed_protocol_rejected(self):
        self.source["image_size_px"] = 1280
        with self.assertRaises(ValueError):
            MODULE.build_rows(self.source, MODULE.OFFICIAL)

    def test_duplicate_models_rejected(self):
        self.source["models"][1] = copy.deepcopy(self.source["models"][0])
        with self.assertRaises(ValueError):
            MODULE.build_rows(self.source, MODULE.OFFICIAL)

    def test_invalid_numeric_values_rejected(self):
        for value in (float("nan"), -1, True):
            source = copy.deepcopy(self.source)
            source["models"][0]["t4_tensorrt10_ms"] = value
            with self.assertRaises(ValueError):
                MODULE.build_rows(source, MODULE.OFFICIAL)

    def test_generate_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary"
            MODULE.run(output=output)
            with (output / "performance_summary.csv").open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["cpu_hardware"], "")
            self.assertEqual(rows[1]["map50_95_e2e_pct"], "47.8")
            self.assertIn("7.7个百分点", (output / "README.md").read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                MODULE.run(output=output)


if __name__ == "__main__":
    unittest.main()
