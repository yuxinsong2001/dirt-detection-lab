"""Offline tests; no real model, network requests or training."""

import importlib.util
import io
import pickle
import tempfile
import unittest
import zipfile
from collections import OrderedDict
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "inspect_official_checkpoint.py"
SPEC = importlib.util.spec_from_file_location("official_checkpoint", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WouldExecute:
    def __reduce__(self):
        return eval, ("1 / 0",)


class OfficialCheckpointTests(unittest.TestCase):
    def test_external_constructor_is_not_executed(self):
        payload = pickle.dumps({"model": WouldExecute(), "train_args": {"epochs": 2}})
        document = MODULE.MetadataUnpickler(io.BytesIO(payload)).load()
        self.assertIsInstance(document["model"], MODULE.SkippedObject)
        self.assertEqual(document["train_args"]["epochs"], 2)

    def test_metadata_from_synthetic_archive(self):
        document = {"train_args": {"epochs": 2}, "train_results": OrderedDict(epoch=[1, 2]), "train_metrics": {"map": 0.4}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.pt"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("fixture/data.pkl", pickle.dumps(document))
            result = MODULE.checkpoint_metadata(path)
            self.assertEqual(result["train_results"]["epoch"], [1, 2])

    def test_inconsistent_curve_lengths_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.curve_rows({"epoch": [1, 2], "map": [0.5]})

    def test_curve_rows_preserve_values(self):
        columns, rows = MODULE.curve_rows({"epoch": [1, 2], "map": [0.4, 0.5]})
        self.assertEqual(columns, ["epoch", "map"])
        self.assertEqual(rows[1], {"epoch": 2, "map": 0.5})

    def test_unknown_metadata_and_nan_are_rejected(self):
        for value in (MODULE.SkippedObject(), float("nan")):
            with self.assertRaises(ValueError):
                MODULE.json_metadata(value)

    def test_json_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            MODULE.write_json(path, {"value": 1})
            with self.assertRaises(FileExistsError):
                MODULE.write_json(path, {"value": 2})

    def test_checksum_failure_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "wrong.pt"
            path.write_bytes(b"not the official artifact")
            with self.assertRaises(ValueError):
                MODULE.verify_artifact(path)


if __name__ == "__main__":
    unittest.main()
