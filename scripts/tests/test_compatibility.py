"""Safe tests for relocated utilities; never convert data or render reports."""

import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CompatibilityTests(unittest.TestCase):
    def test_old_and_new_help_entrypoints(self):
        for old, new in (
            ("dataset_convert_to_yolo_binary.py", "scripts/dataset_convert_to_yolo_binary.py"),
            ("tools/configure_dataset.py", "scripts/configure_dataset.py"),
            ("tools/visualize_multiclass_labels.py", "scripts/visualize_multiclass_labels.py"),
        ):
            for entry in (old, new):
                with self.subTest(entry=entry):
                    result = subprocess.run(
                        [sys.executable, "-B", str(ROOT / entry), "--help"],
                        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("--help", result.stdout)

    def test_converter_import_preserves_dataset_root(self):
        for entry in ("dataset_convert_to_yolo_binary.py", "scripts/dataset_convert_to_yolo_binary.py"):
            namespace = runpy.run_path(str(ROOT / entry), run_name="compatibility_probe")
            self.assertEqual(namespace["PROJECT_ROOT"], ROOT)
            self.assertEqual(namespace["CFG_ROOT"], ROOT / "cfg")

    def test_config_wrapper_preserves_function_and_no_overwrite(self):
        namespace = runpy.run_path(str(ROOT / "tools/configure_dataset.py"), run_name="compatibility_probe")
        self.assertEqual(namespace["ROOT"], ROOT)
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "images/train").mkdir(parents=True)
            source = base / "source.yaml"
            source.write_text("path: unused\ntrain: images/train\nnames: {0: dirt}\n", encoding="utf-8")
            output = base / "local.yaml"
            configure = namespace["configure_dataset"]
            self.assertEqual(configure(source, base, output), output)
            self.assertTrue(output.exists())
            with self.assertRaises(ValueError):
                configure(source, base, output)


if __name__ == "__main__":
    unittest.main()
