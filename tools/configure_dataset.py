"""Generate a machine-local YOLO dataset YAML without changing the shared config."""
import argparse
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def configure_dataset(config: Path, dataset: Path, output: Path) -> Path:
    config = config.expanduser().resolve()
    dataset = dataset.expanduser().resolve()
    output = output.expanduser().resolve()
    if output == config or output.exists():
        raise ValueError(f"Refusing to overwrite an existing configuration: {output}")
    document = yaml.safe_load(config.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Dataset configuration must be a YAML mapping")
    if not dataset.is_dir():
        raise FileNotFoundError(f"Dataset directory not found: {dataset}")
    for split in ("train", "val", "test"):
        value = document.get(split)
        if value is None:
            continue
        if not isinstance(value, str) or Path(value).is_absolute():
            raise ValueError(f"Expected a relative path for split {split}")
        target = (dataset / value).resolve()
        if not target.is_relative_to(dataset) or not target.exists():
            raise ValueError(f"Missing or out-of-root split {split}: {target}")
    document["path"] = dataset.as_posix()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        yaml.safe_dump(document, stream, allow_unicode=True, sort_keys=False)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    destination = args.output or ROOT / "cfg" / "local" / args.config.name
    print(configure_dataset(args.config, args.dataset, destination))
