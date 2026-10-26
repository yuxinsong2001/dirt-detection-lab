import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools/compare_official_configs.py"
SPEC = importlib.util.spec_from_file_location("compare_official_configs", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ConfigComparisonTests(unittest.TestCase):
    def test_null_is_not_a_missing_field(self):
        rows = {row["field"]: row for row in MODULE.compare_dicts({"a": None}, {"b": None})}
        self.assertEqual(rows["a"]["status"], "missing_s")
        self.assertEqual(rows["a"]["YOLO26n"], "null")
        self.assertEqual(rows["b"]["status"], "missing_n")

    def test_types_are_not_silently_coerced(self):
        row = MODULE.compare_dicts({"x": True}, {"x": 1})[0]
        self.assertEqual(row["status"], "different")

    def test_same_and_different_values(self):
        rows = {row["field"]: row for row in MODULE.compare_dicts({"batch": 128, "epochs": 245}, {"batch": 128, "epochs": 70})}
        self.assertEqual(rows["batch"]["status"], "same")
        self.assertEqual(rows["epochs"]["status"], "different")

    def test_existing_output_is_rejected_before_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError):
                MODULE.run(Path("missing-n"), Path("missing-s"), Path(directory))


if __name__ == "__main__":
    unittest.main()
