from pathlib import Path
from PIL import Image
import shutil
import json
import argparse


# ============================================================
# Dataset profiles
#
# The existing small dataset is stored in ./datasets/binary/small.
# This script converts the full raw dataset under ./datasets/images into ./datasets/binary/full.
# After conversion, switch datasets by changing only the data= YAML path in YOLO commands.
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
CFG_ROOT = PROJECT_ROOT / "cfg"

DATASET_PROFILES = {
    "full": {
        "train_val_root": PROJECT_ROOT / "datasets" / "images" / "training",
        "test_root": PROJECT_ROOT / "datasets" / "images" / "test",
        "output_root": PROJECT_ROOT / "datasets" / "binary" / "full",
        "cfg_prefix": "dirt_binary_full",
        "yolo_relative_path": "../datasets/binary/full",
        "test_datasets": {
            "test_real_new": "test_real_new (Test)",
            "blended_test_floor_images": "blended_test_floor_images (TestSynth)",
            "blended_training_floor_images": "blended_training_floor_images (TestSynthTF)",
            "blended_test_floor_images_dirt_only": "blended_test_floor_images_dirt_only",
        },
    },
}

ACTIVE_PROFILE = "full"
TRAIN_VAL_ROOT = DATASET_PROFILES[ACTIVE_PROFILE]["train_val_root"]
RAW_TEST_ROOT = DATASET_PROFILES[ACTIVE_PROFILE]["test_root"]
TEST_DATASETS = DATASET_PROFILES[ACTIVE_PROFILE]["test_datasets"]
binary_ROOT = DATASET_PROFILES[ACTIVE_PROFILE]["output_root"]
CFG_PREFIX = DATASET_PROFILES[ACTIVE_PROFILE]["cfg_prefix"]
YOLO_RELATIVE_PATH = DATASET_PROFILES[ACTIVE_PROFILE]["yolo_relative_path"]

OUT_IMAGES_DIR = binary_ROOT / "images"
OUT_LABELS_DIR = binary_ROOT / "labels"


# ============================================================
# 5. Split names
# ============================================================
TRAIN_SPLIT_NAME = "train"
VAL_SPLIT_NAME = "val"


# ============================================================
# 6. Whether to clear old output results
# Keep this as False for the first run.
# If the dataset has already been generated and you want to regenerate it,
# set this to True.
# ============================================================
CLEAR_OLD_OUTPUT = False


def configure_profile(profile_name, clear_old_output=False):
    """
    Configure all paths from a named dataset profile.
    """
    global ACTIVE_PROFILE
    global TRAIN_VAL_ROOT
    global RAW_TEST_ROOT
    global TEST_DATASETS
    global binary_ROOT
    global CFG_PREFIX
    global YOLO_RELATIVE_PATH
    global OUT_IMAGES_DIR
    global OUT_LABELS_DIR
    global CLEAR_OLD_OUTPUT

    if profile_name not in DATASET_PROFILES:
        available = ", ".join(sorted(DATASET_PROFILES.keys()))
        raise ValueError(f"Unknown dataset profile: {profile_name}. Available profiles: {available}")

    profile = DATASET_PROFILES[profile_name]
    ACTIVE_PROFILE = profile_name
    TRAIN_VAL_ROOT = profile["train_val_root"]
    RAW_TEST_ROOT = profile["test_root"]
    TEST_DATASETS = profile["test_datasets"]
    binary_ROOT = profile["output_root"]
    CFG_PREFIX = profile["cfg_prefix"]
    YOLO_RELATIVE_PATH = profile["yolo_relative_path"]
    OUT_IMAGES_DIR = binary_ROOT / "images"
    OUT_LABELS_DIR = binary_ROOT / "labels"
    CLEAR_OLD_OUTPUT = clear_old_output


def get_split_from_floor_id(floor_id):
    """
    Split train / validation according to the floor ID.

    floor_000000 ~ floor_000015 -> train
    floor_000016 ~ floor_000020 -> val
    """
    if 0 <= floor_id <= 15:
        return TRAIN_SPLIT_NAME
    elif 16 <= floor_id <= 20:
        return VAL_SPLIT_NAME
    else:
        raise ValueError(f"Unknown floor ID: {floor_id}")


def get_floor_id_from_image_name(img_name):
    """
    Extract the floor ID from the image filename.

    Example:
    floor_000016_img_000054_r0_f0.png

    After splitting:
    ['floor', '000016', 'img', '000054', 'r0', 'f0.png']

    floor_id = 16
    """
    parts = img_name.split("_")

    if len(parts) < 2 or parts[0] != "floor":
        raise ValueError(f"Cannot extract floor ID from image name: {img_name}")

    return int(parts[1])


def original_class_to_binary(class_name):
    """
    Binary class mapping:

    dirt -> 0
    all other classes -> 1
    """
    class_name = class_name.strip().lower()

    if class_name == "dirt":
        return 0
    else:
        return 1


def convert_bbox_to_yolo(xmin, ymin, xmax, ymax, img_w, img_h):
    """
    Original format:
    xmin ymin xmax ymax

    YOLO format:
    x_center y_center width height
    """
    x_center = ((xmin + xmax) / 2.0) / img_w
    y_center = ((ymin + ymax) / 2.0) / img_h
    width = (xmax - xmin) / img_w
    height = (ymax - ymin) / img_h

    return x_center, y_center, width, height


def parse_bbox_line(line):
    """
    Parse one line from a bbox label file.

    Supported training set format:
    floor_000020_img_000012_r0_f0 102 953 368 1023 rulers

    Supported test set format:
    test_floor_000000_img_000000 102 953 368 1023 dirt

    Also compatible with the old space-separated format:
    floor 000020 img 000012 r0 f0 102 953 368 1023 rulers

    Returns:
    img_name, xmin, ymin, xmax, ymax, class_name
    """
    parts = line.strip().split()

    if not parts:
        raise ValueError(f"Empty line: {line}")

    # =====================================================
    # Format 1: common format for training / test sets
    # floor_000020_img_000012_r0_f0 102 953 368 1023 rulers
    # test_floor_000000_img_000000 102 953 368 1023 dirt
    # =====================================================
    if parts[0].startswith("floor_") or parts[0].startswith("test_floor_"):
        if len(parts) < 6:
            raise ValueError(f"Incomplete line format: {line}")

        img_name = parts[0]

        if not img_name.lower().endswith((".png", ".jpg", ".jpeg")):
            img_name = img_name + ".png"

        xmin = float(parts[1])
        ymin = float(parts[2])
        xmax = float(parts[3])
        ymax = float(parts[4])
        class_name = parts[5]

        return img_name, xmin, ymin, xmax, ymax, class_name

    # =====================================================
    # Format 2: old space-separated format
    # floor 000020 img 000012 r0 f0 102 953 368 1023 rulers
    # =====================================================
    if len(parts) >= 11 and parts[0] == "floor" and parts[2] == "img":
        img_name = "_".join(parts[0:6]) + ".png"

        xmin = float(parts[6])
        ymin = float(parts[7])
        xmax = float(parts[8])
        ymax = float(parts[9])
        class_name = parts[10]

        return img_name, xmin, ymin, xmax, ymax, class_name

    raise ValueError(f"Unrecognized line format: {line}")


def clip_bbox(xmin, ymin, xmax, ymax, img_w, img_h):
    """
    Prevent bbox coordinates from exceeding image boundaries.
    """
    xmin = max(0, min(xmin, img_w))
    xmax = max(0, min(xmax, img_w))
    ymin = max(0, min(ymin, img_h))
    ymax = max(0, min(ymax, img_h))

    return xmin, ymin, xmax, ymax


def get_image_files(folder):
    """
    Get image files from a folder.
    """
    image_files = []
    image_files.extend(folder.glob("*.png"))
    image_files.extend(folder.glob("*.jpg"))
    image_files.extend(folder.glob("*.jpeg"))

    return sorted(image_files)


def clear_old_output():
    """
    Optionally clear the old conversion results of the current DATASET_VERSION.
    """
    if not CLEAR_OLD_OUTPUT:
        return

    if binary_ROOT.exists():
        shutil.rmtree(binary_ROOT)
        print(f"Old output directory has been removed: {binary_ROOT}")


def prepare_output_folders():
    """
    Create output folders.
    """
    split_names = [TRAIN_SPLIT_NAME, VAL_SPLIT_NAME] + list(TEST_DATASETS.keys())

    for split in split_names:
        (OUT_IMAGES_DIR / split).mkdir(parents=True, exist_ok=True)
        (OUT_LABELS_DIR / split).mkdir(parents=True, exist_ok=True)


def convert_train_val_flat_folder():
    """
    Convert the training + validation dataset.

    This function is designed for the current dataset structure:

    floors_1156/
    ├── bbox_labels.txt
    ├── floor_000000_img_000000_r0_f0.png
    ├── floor_000000_img_000001_r0_f0.png
    ├── ...
    └── floor_000020_img_000061_r0_f0.png

    Note:
    train / val is determined by the floor ID in the image filename.
    """
    if not TRAIN_VAL_ROOT.exists():
        raise FileNotFoundError(f"Training / validation dataset path does not exist: {TRAIN_VAL_ROOT}")

    label_file = TRAIN_VAL_ROOT / "bbox_labels.txt"

    if not label_file.exists():
        raise FileNotFoundError(f"bbox_labels.txt was not found: {label_file}")

    print(f"Converting training / validation dataset: {TRAIN_VAL_ROOT}")

    labels_by_image = {}
    image_size_cache = {}

    stats = {
        "train_images": 0,
        "train_boxes": 0,
        "val_images": 0,
        "val_boxes": 0,
    }

    with open(label_file, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                img_name, xmin, ymin, xmax, ymax, class_name = parse_bbox_line(line)
            except Exception as e:
                print(f"Warning: failed to parse line {line_number}: {line}")
                print(f"Reason: {e}")
                continue

            img_path = TRAIN_VAL_ROOT / img_name

            if not img_path.exists():
                print(f"Warning: image not found: {img_path}")
                continue

            try:
                floor_id = get_floor_id_from_image_name(img_name)
                split = get_split_from_floor_id(floor_id)
            except Exception as e:
                print(f"Warning: failed to determine train/val split, skipped: {img_name}")
                print(f"Reason: {e}")
                continue

            if img_name not in image_size_cache:
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
                image_size_cache[img_name] = (img_w, img_h)
            else:
                img_w, img_h = image_size_cache[img_name]

            xmin, ymin, xmax, ymax = clip_bbox(xmin, ymin, xmax, ymax, img_w, img_h)

            if xmax <= xmin or ymax <= ymin:
                print(f"Warning: invalid bbox width or height, skipped: {line}")
                continue

            class_id = original_class_to_binary(class_name)

            x_center, y_center, width, height = convert_bbox_to_yolo(
                xmin, ymin, xmax, ymax, img_w, img_h
            )

            if not (
                0 <= x_center <= 1
                and 0 <= y_center <= 1
                and 0 < width <= 1
                and 0 < height <= 1
            ):
                print(f"Warning: YOLO coordinates out of range, skipped: {line}")
                continue

            yolo_line = (
                f"{class_id} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{width:.6f} "
                f"{height:.6f}"
            )

            if img_name not in labels_by_image:
                labels_by_image[img_name] = {
                    "split": split,
                    "labels": [],
                }

            labels_by_image[img_name]["labels"].append(yolo_line)

            if split == TRAIN_SPLIT_NAME:
                stats["train_boxes"] += 1
            elif split == VAL_SPLIT_NAME:
                stats["val_boxes"] += 1

    image_files = get_image_files(TRAIN_VAL_ROOT)

    for img_path in image_files:
        img_name = img_path.name
        stem = img_path.stem

        try:
            floor_id = get_floor_id_from_image_name(img_name)
            split = get_split_from_floor_id(floor_id)
        except Exception as e:
            print(f"Warning: failed to determine train/val split for image, skipped: {img_name}")
            print(f"Reason: {e}")
            continue

        dst_img_path = OUT_IMAGES_DIR / split / img_name
        dst_label_path = OUT_LABELS_DIR / split / f"{stem}.txt"

        shutil.copy2(img_path, dst_img_path)

        label_info = labels_by_image.get(img_name)
        label_lines = label_info["labels"] if label_info else []

        with open(dst_label_path, "w", encoding="utf-8") as f:
            for yolo_line in label_lines:
                f.write(yolo_line + "\n")

        if split == TRAIN_SPLIT_NAME:
            stats["train_images"] += 1
        elif split == VAL_SPLIT_NAME:
            stats["val_images"] += 1

    return stats


def convert_one_fixed_split_folder(src_dir, split):
    """
    Convert a folder with a fixed split.

    Used for the test set:
    test_real_new (Test)/
    ├── bbox_labels_testset.txt
    ├── test_floor_000000_img_000000.png
    └── ...

    All images are placed into the same split, for example test_real_new.
    """

    # The label filename may be different between training and test sets.
    label_candidates = [
        src_dir / "bbox_labels.txt",
        src_dir / "bbox_labels_testset.txt",
    ]

    label_file = None

    for candidate in label_candidates:
        if candidate.exists():
            label_file = candidate
            break

    if label_file is None:
        print(f"Warning: neither bbox_labels.txt nor bbox_labels_testset.txt was found in {src_dir}, skipped.")
        return 0, 0

    print(f"Converting test set: {src_dir.name} -> {split}")
    print(f"Using label file: {label_file.name}")

    labels_by_image = {}
    image_size_cache = {}

    bbox_count = 0

    with open(label_file, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                img_name, xmin, ymin, xmax, ymax, class_name = parse_bbox_line(line)
            except Exception as e:
                print(f"Warning: failed to parse line {line_number}: {line}")
                print(f"Reason: {e}")
                continue

            img_path = src_dir / img_name

            if not img_path.exists():
                print(f"Warning: image not found: {img_path}")
                continue

            if img_name not in image_size_cache:
                with Image.open(img_path) as img:
                    img_w, img_h = img.size
                image_size_cache[img_name] = (img_w, img_h)
            else:
                img_w, img_h = image_size_cache[img_name]

            xmin, ymin, xmax, ymax = clip_bbox(xmin, ymin, xmax, ymax, img_w, img_h)

            if xmax <= xmin or ymax <= ymin:
                print(f"Warning: invalid bbox width or height, skipped: {line}")
                continue

            class_id = original_class_to_binary(class_name)

            x_center, y_center, width, height = convert_bbox_to_yolo(
                xmin, ymin, xmax, ymax, img_w, img_h
            )

            if not (
                0 <= x_center <= 1
                and 0 <= y_center <= 1
                and 0 < width <= 1
                and 0 < height <= 1
            ):
                print(f"Warning: YOLO coordinates out of range, skipped: {line}")
                continue

            yolo_line = (
                f"{class_id} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{width:.6f} "
                f"{height:.6f}"
            )

            if img_name not in labels_by_image:
                labels_by_image[img_name] = []

            labels_by_image[img_name].append(yolo_line)
            bbox_count += 1

    image_files = get_image_files(src_dir)

    image_count = 0

    for img_path in image_files:
        img_name = img_path.name
        stem = img_path.stem

        dst_img_path = OUT_IMAGES_DIR / split / img_name
        dst_label_path = OUT_LABELS_DIR / split / f"{stem}.txt"

        shutil.copy2(img_path, dst_img_path)

        label_lines = labels_by_image.get(img_name, [])

        with open(dst_label_path, "w", encoding="utf-8") as f:
            for yolo_line in label_lines:
                f.write(yolo_line + "\n")

        image_count += 1

    return image_count, bbox_count


def convert_test_sets():
    """
    Convert all test datasets.
    """
    test_stats = {}

    for split_name, raw_folder_name in TEST_DATASETS.items():
        test_root = RAW_TEST_ROOT / raw_folder_name

        if not test_root.exists():
            print(f"Warning: test dataset path does not exist, skipped: {test_root}")
            test_stats[split_name] = {
                "images": 0,
                "boxes": 0,
            }
            continue

        image_count, bbox_count = convert_one_fixed_split_folder(test_root, split_name)

        test_stats[split_name] = {
            "images": image_count,
            "boxes": bbox_count,
        }

    return test_stats


def build_yaml_text(path_value, test_split=None):
    """
    Build a YOLO dataset yaml text block.
    """
    quoted_root = json.dumps(path_value, ensure_ascii=False)
    lines = [
        f"path: {quoted_root}",
        "",
        f"train: images/{TRAIN_SPLIT_NAME}",
        f"val: images/{VAL_SPLIT_NAME}",
    ]

    if test_split is not None:
        lines.append(f"test: images/{test_split}")

    lines.extend([
        "",
        "nc: 2",
        "names:",
        "  0: dirt",
        "  1: object",
        "",
    ])
    return "\n".join(lines)


def write_yaml_files():
    """
    Write YOLO yaml files both beside the converted dataset and under ./cfg.
    """
    CFG_ROOT.mkdir(parents=True, exist_ok=True)

    dataset_trainval_yaml = binary_ROOT / "dirt_binary_trainval.yaml"
    dataset_trainval_yaml.write_text(
        build_yaml_text(binary_ROOT.as_posix()),
        encoding="utf-8",
    )
    print(f"Training yaml has been generated: {dataset_trainval_yaml}")

    cfg_trainval_yaml = CFG_ROOT / f"{CFG_PREFIX}_trainval.yaml"
    cfg_trainval_yaml.write_text(
        build_yaml_text(YOLO_RELATIVE_PATH),
        encoding="utf-8",
    )
    print(f"Training cfg yaml has been generated: {cfg_trainval_yaml}")

    for split_name in TEST_DATASETS.keys():
        dataset_test_yaml = binary_ROOT / f"dirt_binary_{split_name}.yaml"
        dataset_test_yaml.write_text(
            build_yaml_text(binary_ROOT.as_posix(), split_name),
            encoding="utf-8",
        )
        print(f"Test yaml has been generated: {dataset_test_yaml}")

        cfg_test_yaml = CFG_ROOT / f"{CFG_PREFIX}_{split_name}.yaml"
        cfg_test_yaml.write_text(
            build_yaml_text(YOLO_RELATIVE_PATH, split_name),
            encoding="utf-8",
        )
        print(f"Test cfg yaml has been generated: {cfg_test_yaml}")


def parse_args():
    parser = argparse.ArgumentParser(description="Convert Dirt Detection labels to YOLO binary format.")
    parser.add_argument(
        "--profile",
        default=ACTIVE_PROFILE,
        choices=sorted(DATASET_PROFILES.keys()),
        help="Dataset profile to convert.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Remove the converted output folder for this profile before regenerating it.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    configure_profile(args.profile, args.clear)

    print("Start converting Dirt Detection binary YOLO dataset")
    print("=" * 80)
    print(f"Current dataset profile: {ACTIVE_PROFILE}")
    print(f"Training / validation dataset path: {TRAIN_VAL_ROOT}")
    print(f"Test dataset root path: {RAW_TEST_ROOT}")
    print(f"Output root directory: {binary_ROOT}")
    print(f"Generated cfg prefix: {CFG_PREFIX}")
    print("=" * 80)

    clear_old_output()
    prepare_output_folders()

    train_val_stats = convert_train_val_flat_folder()
    test_stats = convert_test_sets()

    write_yaml_files()

    print("=" * 80)
    print("Conversion completed!")
    print()
    print("Training / validation statistics:")
    print(f"train image count: {train_val_stats['train_images']}")
    print(f"train bbox count: {train_val_stats['train_boxes']}")
    print(f"val image count: {train_val_stats['val_images']}")
    print(f"val bbox count: {train_val_stats['val_boxes']}")

    print()
    print("Test set statistics:")
    for split_name, stats in test_stats.items():
        print(f"{split_name} image count: {stats['images']}")
        print(f"{split_name} bbox count: {stats['boxes']}")

    print()
    print("Output paths:")
    print(f"Image output folder: {OUT_IMAGES_DIR}")
    print(f"Label output folder: {OUT_LABELS_DIR}")

    print()
    print("Class definition:")
    print("0 = dirt")
    print("1 = object")

    print()
    print("Next checks:")
    print("1. The first column of txt files in labels/train should only contain 0 or 1")
    print("2. images/train and labels/train should have matching filenames")
    print("3. images/val and labels/val should have matching filenames")
    print("4. images/test_real_new and labels/test_real_new should have matching filenames")
    print(f"5. Use cfg/{CFG_PREFIX}_trainval.yaml for full-dataset training")
    print("6. Keep using cfg/dirt_binary_trainval.yaml for the existing small dataset under datasets/binary/small")


if __name__ == "__main__":
    main()