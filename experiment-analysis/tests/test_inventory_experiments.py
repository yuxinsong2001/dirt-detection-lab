"""Small synthetic fixtures verify software behavior, not model performance."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "inventory_experiments.py"
SPEC = importlib.util.spec_from_file_location("inventory_experiments", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "runs").mkdir()

    def add_csv(self, name, content):
        path = self.root / "runs" / name / "results.csv"
        path.parent.mkdir()
        path.write_text(content, encoding="utf-8")
        return path

    def test_duplicates_are_reported_without_deleting_inputs(self):
        content = "epoch,metrics/mAP50(B)\n1,0.5\n"
        first = self.add_csv("first", content)
        self.add_csv("copy", content)
        before = first.read_bytes()
        report = MODULE.inventory(self.root)
        self.assertEqual(report["summary"]["training_csv_files"], 2)
        self.assertEqual(report["summary"]["distinct_csv_byte_contents"], 1)
        self.assertEqual(len(report["byte_identical_groups"]), 1)
        self.assertEqual(first.read_bytes(), before)

    def test_legacy_alias_and_config(self):
        path = self.add_csv("legacy", "epoch, metrics/mAP_0.5\n0,0.7\n")
        (path.parent / "opt.yaml").write_text("epochs: 1\n", encoding="utf-8")
        record = MODULE.inventory(self.root)["training_records"][0]
        self.assertEqual(record["metric_columns"]["map50"], "metrics/mAP_0.5")
        self.assertIn("opt.yaml", record["config_files"])
        self.assertIn("single_row_review_purpose", record["issues"])

    def test_empty_csv_is_flagged(self):
        self.add_csv("empty", "")
        issues = MODULE.inventory(self.root)["training_records"][0]["issues"]
        self.assertIn("missing_header", issues)
        self.assertIn("no_data_rows", issues)

    def test_inconsistent_width_is_flagged(self):
        self.add_csv("broken", "epoch,metric\n1,0.5,unexpected\n")
        issues = MODULE.inventory(self.root)["training_records"][0]["issues"]
        self.assertIn("inconsistent_row_width", issues)

    def test_missing_runs_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.inventory(self.root / "missing")

    def test_other_csv_is_separate(self):
        (self.root / "runs" / "test_summary.csv").write_text("metric\n0.5\n", encoding="utf-8")
        report = MODULE.inventory(self.root)
        self.assertEqual(report["summary"]["training_csv_files"], 0)
        self.assertEqual(report["summary"]["other_csv_files"], 1)


if __name__ == "__main__":
    unittest.main()
