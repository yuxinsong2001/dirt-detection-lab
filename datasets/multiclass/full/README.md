# Multiclass Dataset Layout

This directory documents the expected layout of the 10-class DirtNet dataset. The image and label files are intentionally excluded from Git because of their size.

The class mapping is:

| ID | Class |
|---:|---|
| 0 | `dirt` |
| 1 | `business_cards` |
| 2 | `keys` |
| 3 | `other` |
| 4 | `paper_and_notebooks` |
| 5 | `pens` |
| 6 | `rulers` |
| 7 | `scissors` |
| 8 | `tapes` |
| 9 | `usb_sticks` |

Expected local structure:

```text
datasets/multiclass/full/
  images/
    train/
    val/
    test_real_new/
  labels/
    train/
    val/
    test_real_new/
```

The experiment used 860 training images, 296 validation images, and 80 held-out real test images.
