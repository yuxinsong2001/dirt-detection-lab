# Local dataset paths

Shared YAML files keep repository defaults. Generate ignored, machine-local
configurations when your data are stored elsewhere. Run from the repository root
with the project virtual environment active. PyYAML is explicitly listed in requirements.txt.

```powershell
python scripts/configure_dataset.py --config cfg/dirt_binary_trainval.yaml --dataset D:/DirtNet_Project/data
python scripts/configure_dataset.py --config cfg/dirt_multiclass_trainval.yaml --dataset D:/DirtNet_Project/data/multiclass
python scripts/configure_dataset.py --config cfg/dirt_multiclass_test_real_new.yaml --dataset D:/DirtNet_Project/data/multiclass
```

Use the printed file as the `data=` argument in your existing YOLO commands,
for example `data=cfg/local/dirt_multiclass_trainval.yaml`. No training is started
by the configuration tool. Class names and split definitions remain unchanged.
Split paths must exist inside the selected dataset directory. Existing output
files are never overwritten; use a different `--output` filename to regenerate.
Relative CLI paths are resolved against the current working directory.

The visualization tool keeps its original default and accepts explicit paths:

```powershell
python scripts/visualize_multiclass_labels.py --dataset D:/DirtNet_Project/data/multiclass --output reports/figures/multiclass_label_qa_local
```

Optional: `--splits val` processes only validation labels. Visualization output
uses the named destination and can replace same-named preview images there.
Do not use held-out real test results to select hyperparameters and then describe
that same split as an untouched final benchmark.
