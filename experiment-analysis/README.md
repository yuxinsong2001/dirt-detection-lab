# Experiment Analysis

This module inventories existing experiment records without training or running models.
Code, tests and generated reports remain together in this module.

- tools/inventory_experiments.py: recursively inspect saved CSV files and matching configurations.
- tests/test_inventory_experiments.py: six offline unit tests.
- reports/inventory: original and post-reorganization inventory snapshots.
- local-work-notes: local-only personal explanations, excluded from Git.

From the repository root:

```powershell
python -B experiment-analysis/tools/inventory_experiments.py
python -B -m unittest discover -s experiment-analysis/tests -p test_inventory_experiments.py -v
```

JSON snapshots record source paths at capture time. The tool reports byte-identical
copies rather than deleting them. File counts do not equal independent experiment counts.
