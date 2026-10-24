# Training experiment results

The 37 previously flat YOLO experiment directories under runs/detect were grouped here without changing their names or file contents.

- Training results: runs/detect/training/<experiment>/
- Test evaluations: runs/detect/test/
- Video demonstrations: runs/detect/final_demo_outputs/
- Other legacy experiment locations remain unchanged.

Original args.yaml / opt.yaml contain paths used at execution time. Those historical paths have deliberately not been rewritten. Use the current directory when loading a checkpoint; specify project=runs/detect/training for new training runs.

The inventory tool scans recursively, so it still finds all 41 training CSV files across the repository's runs directory. No training or evaluation was rerun.
