"""Fetch one pinned official artifact and export saved metadata; never run a model.

The metadata reader substitutes inert placeholders for model/tensor globals. It
does not call torch.load, import Ultralytics, reconstruct tensors or run inference.
This is a narrowly scoped reader for checksum-verified official checkpoint metadata,
not a general-purpose or adversarially hardened pickle sandbox.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import pickle
import urllib.request
import zipfile
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
RELEASE = "v8.4.0"
ASSET = "yolo26n.pt"
EXPECTED_SIZE = 5544453
EXPECTED_SHA256 = "9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef"
RELEASE_API = f"https://api.github.com/repos/ultralytics/assets/releases/tags/{RELEASE}"
DOWNLOAD_URL = f"https://github.com/ultralytics/assets/releases/download/{RELEASE}/{ASSET}"
DOC_URL = "https://docs.ultralytics.com/guides/yolo26-training-recipe/"


class SkippedObject:
    """Inert substitute for all model classes and tensor rebuilding functions."""

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        pass

    def __setstate__(self, state):
        # Model state is deliberately discarded, not applied to a real object.
        pass


class MetadataUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) == ("collections", "OrderedDict"):
            return OrderedDict
        return SkippedObject

    def persistent_load(self, pid):
        # Tensor storage is never read from the archive.
        return SkippedObject()


def json_metadata(value):
    """Accept only plain JSON-compatible metadata; never stringify unknown objects."""
    if value is None or type(value) in (str, bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Non-finite number in selected metadata")
        return value
    if isinstance(value, (dict, OrderedDict)):
        if not all(type(key) is str for key in value):
            raise ValueError("Selected metadata has non-string dictionary keys")
        return {key: json_metadata(item) for key, item in value.items()}
    if type(value) in (list, tuple):
        return [json_metadata(item) for item in value]
    raise ValueError(f"Unsupported selected metadata type: {type(value).__name__}")


def checkpoint_metadata(path):
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.endswith("/data.pkl")]
        if len(names) != 1:
            raise ValueError("Expected exactly one checkpoint data.pkl")
        if archive.getinfo(names[0]).file_size > 16 * 1024 * 1024:
            raise ValueError("Checkpoint metadata exceeds the reader limit")
        document = MetadataUnpickler(io.BytesIO(archive.read(names[0]))).load()
    if not isinstance(document, dict):
        raise ValueError("Expected a checkpoint dictionary")
    required = ("train_args", "train_results", "train_metrics")
    missing = [key for key in required if key not in document]
    if missing:
        raise ValueError("Missing metadata: " + ", ".join(missing))
    return {key: json_metadata(document[key]) for key in (
        "train_args", "train_results", "train_metrics", "git", "date", "version", "epoch", "license"
    ) if key in document}


def curve_rows(curves):
    """Accept a column-oriented saved table without guessing field meanings."""
    if not isinstance(curves, dict) or not curves:
        raise ValueError("Expected a non-empty column-oriented train_results table")
    if not all(isinstance(values, list) for values in curves.values()):
        raise ValueError("Every train_results column must contain a list")
    lengths = {len(values) for values in curves.values()}
    if len(lengths) != 1 or lengths == {0}:
        raise ValueError("Empty or inconsistent train_results column lengths")
    columns = list(curves)
    return columns, [dict(zip(columns, values)) for values in zip(*(curves[key] for key in columns))]


def request_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "dirt-detection-lab-official-source-audit"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def verify_artifact(path):
    if path.stat().st_size != EXPECTED_SIZE:
        raise ValueError("Artifact size differs from pinned official asset")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Artifact SHA-256 differs from pinned official asset")
    return digest


def download_artifact(destination, release):
    assets = [item for item in release["assets"] if item["name"] == ASSET]
    if len(assets) != 1 or release["tag_name"] != RELEASE:
        raise ValueError("Official release asset not uniquely identified")
    asset = assets[0]
    if (asset["size"] != EXPECTED_SIZE or asset.get("digest") != "sha256:" + EXPECTED_SHA256
            or asset["browser_download_url"] != DOWNLOAD_URL):
        raise ValueError("Release metadata no longer matches pinned values; review before proceeding")
    if destination.exists():
        raise FileExistsError("Refusing to reuse a previous local checkpoint for this first acquisition")
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(".pt.download")
    request = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "dirt-detection-lab-official-source-audit"})
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("xb") as output:
        total = 0
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > EXPECTED_SIZE:
                raise ValueError("Download exceeds expected size; partial retained for inspection")
            output.write(chunk)
    verify_artifact(partial)
    partial.rename(destination)
    return asset


def write_json(path, document):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def run(output_dir, artifact):
    if output_dir.exists():
        raise FileExistsError("Output directory already exists; choose a new destination")
    if artifact.exists() or artifact.with_suffix(".pt.download").exists():
        raise FileExistsError("Acquisition destination already exists; no files overwritten")
    release = request_json(RELEASE_API)
    asset = download_artifact(artifact, release)
    metadata = checkpoint_metadata(artifact)
    columns, rows = curve_rows(metadata["train_results"])
    output_dir.mkdir(parents=True)
    provenance = {
        "publisher": "Ultralytics",
        "repository": "https://github.com/ultralytics/assets",
        "release_tag": RELEASE,
        "release_url": release["html_url"],
        "release_api": RELEASE_API,
        "release_published_at": release["published_at"],
        "asset_name": ASSET,
        "asset_id": asset["id"],
        "asset_updated_at": asset["updated_at"],
        "download_url": DOWNLOAD_URL,
        "size_bytes": artifact.stat().st_size,
        "sha256": verify_artifact(artifact),
        "checksum_matches_official_digest": True,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "documentation_url": DOC_URL,
        "checkpoint_version": metadata.get("version"),
        "checkpoint_git": metadata.get("git"),
        "scope": "One publisher-provided checkpoint; not a controlled parameter sweep",
        "operations_performed": ["download", "checksum verification", "saved metadata extraction"],
        "operations_not_performed": ["training", "inference", "validation", "tensor reconstruction"],
    }
    write_json(output_dir / "source.json", provenance)
    write_json(output_dir / "training_config.json", metadata["train_args"])
    write_json(output_dir / "saved_metrics.json", metadata["train_metrics"])
    write_json(output_dir / "checkpoint_metadata.json", {
        key: value for key, value in metadata.items() if key not in ("train_args", "train_metrics", "train_results")
    })
    with (output_dir / "epoch_metrics.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "asset": ASSET,
        "release": RELEASE,
        "training_config_fields": len(metadata["train_args"]),
        "saved_metric_fields": len(metadata["train_metrics"]),
        "curve_rows": len(rows),
        "curve_columns": columns,
        "saved_checkpoint_epoch": metadata.get("epoch"),
        "note": "Preserved publisher values; best checkpoint and final curve row are not assumed identical",
    }
    write_json(output_dir / "inspection_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=MODULE_ROOT / "reports" / "official" / "yolo26n-v8.4.0")
    parser.add_argument("--artifact", type=Path, default=MODULE_ROOT / "data" / "external" / "ultralytics" / RELEASE / ASSET)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.output.resolve(), args.artifact.resolve()), indent=2, ensure_ascii=False))
    except (OSError, ValueError, KeyError, pickle.UnpicklingError, zipfile.BadZipFile) as exc:
        parser.exit(1, f"Official checkpoint inspection failed: {exc}\n")


if __name__ == "__main__":
    main()
