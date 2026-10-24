# Official YOLO26n saved training records — release v8.4.0

This directory contains metadata extracted from a newly downloaded official
Ultralytics asset, not from the user's local training runs. No training, prediction,
dataset validation or tensor reconstruction was performed.

## Files

| File | Meaning |
|---|---|
| source.json | Publisher, official URL, release asset ID, size, SHA-256 and download timestamp |
| training_config.json | All 113 saved training arguments, retaining original names and values |
| epoch_metrics.csv | 245 rows (epochs 1–245), 19 columns of saved training/validation records |
| saved_metrics.json | Eleven metrics saved in the published checkpoint; not automatically the final curve row |
| checkpoint_metadata.json | Original training code revision, timestamp, library version and checkpoint metadata |
| inspection_summary.json | Counts and column names from the extraction |

## Verified source

- [Official release](https://github.com/ultralytics/assets/releases/tag/v8.4.0)
- [Official asset](https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt)
- [Publisher description of embedded records](https://docs.ultralytics.com/guides/yolo26-training-recipe/#viewing-the-training-curves)
- Asset ID: 340096055; size: 5,544,453 bytes.
- SHA-256: 9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef.
- The downloaded file matched the digest returned by GitHub's official release API.

This verifies correspondence to the pinned published asset, not independent
reproduction of its metrics or a cryptographic signature of the research claims.
The binary is local and ignored under experiment-analysis/data/external/ultralytics/v8.4.0/.

## Interpretation boundaries

- Task is detect. The saved data value is the author's COCO YAML path, not a path
  that should exist on this machine. No COCO images were downloaded.
- The published asset is yolo26n.pt. The training argument model is
  yolo26n-objv1-150.pt, the starting checkpoint for this stage, not the output filename.
- Recorded settings include 245 epochs, image size 640, batch 128 and MuSGD.
  These are historical values, not commands to reproduce on the user's hardware.
- This checkpoint contains the COCO-stage curve, not all Objects365 pretraining
  history. Downloading one stage does not create a complete two-stage experiment.
- Saved metrics and the last curve row are different records. For example, saved
  mAP50-95(B) is 0.40116 whereas the final curve row contains 0.40111. Preserve both.
- The checkpoint's epoch value is -1. Do not interpret this as "zero training" or
  use it to replace the observed 245 curve rows; it is retained as checkpoint metadata.
- The recorded library version is 8.3.222 on the exp-main branch at commit
  cb13d5f9cfbd6f299da3620c625f81d721dc2849. Release v8.4.0 is the asset release tag,
  not a claim that training used library version 8.4.0.
- Loss names and fitness are retained without assuming their formulas match every
  other YOLO version. Verify the producing code before cross-version interpretation.
- One official run is not a controlled hyperparameter sweep. Other official model
  sizes may use different recipes and budgets; no causal parameter conclusions yet.

## Reading method

The tool reads ZIP-contained data.pkl with a constrained metadata unpickler. All
model/tensor globals are replaced by inert placeholders; tensor storage is not
read. Only selected plain metadata are exported. This avoids torch.load and model
imports, but is not advertised as a general-purpose sandbox for untrusted pickle.
Inputs are restricted to one reviewed, checksum-pinned official asset. Unknown
objects in selected metadata cause an error instead of being silently stringified.

Existing artifact or output destinations are refused. Partial downloads are retained
for inspection on failure rather than silently overwritten or deleted.
