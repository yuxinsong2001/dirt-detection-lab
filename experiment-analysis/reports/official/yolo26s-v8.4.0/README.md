# Official YOLO26s saved training records — release v8.4.0

Newly downloaded from the official Ultralytics release, not copied from personal
training outputs. No training, prediction or dataset evaluation was executed.

## Source and files

- [Official release](https://github.com/ultralytics/assets/releases/tag/v8.4.0)
- [Official asset](https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26s.pt)
- Asset ID 340096060; 20,422,725 bytes.
- SHA-256: 646f8bc3fe0a656803d95c294f7852321748cb29d13466a1af8862e2db384a1b.
- Downloaded bytes matched the pinned digest and GitHub release API metadata.

| File | Meaning |
|---|---|
| source.json | Exact URL, release metadata, checksum and retrieval timestamp |
| training_config.json | 113 saved settings, original types and values |
| epoch_metrics.csv | 70 recorded epochs, 19 columns |
| saved_metrics.json | Eleven saved checkpoint metrics, separate from the final curve row |
| checkpoint_metadata.json | Producing code revision, date, library version and checkpoint metadata |
| inspection_summary.json | Extraction counts and fields |

The binary stays ignored under experiment-analysis/data/external/ultralytics/v8.4.0/.
The reader only processes saved plain metadata; model/tensor globals are replaced
by inert placeholders and tensor storage is not read. It is not a general pickle sandbox.

## Interpretation

This is a detect run with recorded image size 640, batch 128, MuSGD and 70 epochs.
The model argument yolo26s-objv1-150.pt is the starting checkpoint, not this release
filename. The COCO-stage record does not contain the entire prior Objects365 history.

Saved library version is 8.3.222; the producing Git commit is
557e95b99c24c5b0d4eb5973d5d54a20a799566a. It differs from the N checkpoint's code
revision even though the library version string matches. Historical data paths
and device indices are preserved, not treated as current local paths or hardware names.
The checkpoint epoch marker -1 is not a replacement for the 70 observed curve rows.

[N/S configuration comparison](../comparison-n-s-v8.4.0/README.md) documents differences
without ranking accuracy or asserting causal effects.
