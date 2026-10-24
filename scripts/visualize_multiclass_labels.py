import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "multiclass" / "small"
OUTPUT = ROOT / "reports" / "figures" / "multiclass_label_qa"
NAMES = [
    "dirt",
    "business_cards",
    "keys",
    "other",
    "paper_and_notebooks",
    "pens",
    "rulers",
    "scissors",
    "tapes",
    "usb_sticks",
]
COLORS = [
    "#ff5d73",
    "#55d6be",
    "#ffd166",
    "#9b8cff",
    "#5aa9ff",
    "#ff9f43",
    "#6ee7ff",
    "#f78fb3",
    "#a3e635",
    "#c084fc",
]


def read_labels(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        class_id, x, y, width, height = line.split()
        rows.append((int(class_id), float(x), float(y), float(width), float(height)))
    return rows


def select_diverse_samples(split: str, count: int = 6, dataset: Path = DATASET):
    label_dir = dataset / "labels" / split
    if not label_dir.is_dir():
        raise FileNotFoundError(f"Label directory not found: {label_dir}")
    candidates = []
    for label_path in sorted(label_dir.glob("*.txt")):
        labels = read_labels(label_path)
        classes = {row[0] for row in labels}
        candidates.append((label_path, labels, classes))

    if not candidates:
        raise ValueError(f"No label files found in {label_dir}")
    selected = []
    covered = set()
    remaining = candidates.copy()
    while remaining and len(selected) < count:
        best = max(
            remaining,
            key=lambda item: (len(item[2] - covered), len(item[2]), len(item[1])),
        )
        selected.append(best)
        covered.update(best[2])
        remaining.remove(best)
    return selected


def make_sheet(split: str, dataset: Path = DATASET, output: Path = OUTPUT):
    tile_width, tile_height = 480, 384
    header_height, footer_height = 38, 80
    columns, rows = 3, 2
    sheet = Image.new(
        "RGB",
        (columns * tile_width, header_height + rows * tile_height + footer_height),
        "#080d13",
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    draw.text((16, 12), f"DirtNet multiclass label QA - {split}", fill="#e6edf3", font=font)

    for index, (label_path, labels, _) in enumerate(select_diverse_samples(split, dataset=dataset)):
        image_path = dataset / "images" / split / f"{label_path.stem}.png"
        image = Image.open(image_path).convert("RGB")
        source_width, source_height = image.size
        image = image.resize((tile_width, tile_height))
        tile_draw = ImageDraw.Draw(image)

        for class_id, x, y, width, height in labels:
            x1 = (x - width / 2) * tile_width
            y1 = (y - height / 2) * tile_height
            x2 = (x + width / 2) * tile_width
            y2 = (y + height / 2) * tile_height
            color = COLORS[class_id]
            tile_draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
            text = f"{class_id}:{NAMES[class_id]}"
            text_y = max(0, y1 - 12)
            tile_draw.rectangle((x1, text_y, x1 + 6 * len(text) + 4, text_y + 12), fill="#000000bb")
            tile_draw.text((x1 + 2, text_y + 1), text, fill=color, font=font)

        tile_draw.rectangle((0, 0, tile_width, 15), fill="#000000cc")
        tile_draw.text(
            (4, 2),
            f"{label_path.stem} | {source_width}x{source_height}",
            fill="white",
            font=font,
        )
        column, row = index % columns, index // columns
        sheet.paste(image, (column * tile_width, header_height + row * tile_height))

    legend_y = header_height + rows * tile_height + 12
    for class_id, name in enumerate(NAMES):
        column, row = class_id % 5, class_id // 5
        x = 14 + column * 286
        y = legend_y + row * 26
        draw.rectangle((x, y, x + 14, y + 14), fill=COLORS[class_id])
        draw.text((x + 20, y + 1), f"{class_id}: {name}", fill="#e6edf3", font=font)

    output.mkdir(parents=True, exist_ok=True)
    output_path = output / f"{split}_samples.jpg"
    sheet.save(output_path, quality=92)
    print(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize multiclass YOLO labels.")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--splits", nargs="+", default=["train", "val", "test_real_new"])
    args = parser.parse_args()
    for split_name in args.splits:
        make_sheet(split_name, args.dataset.expanduser().resolve(), args.output.expanduser().resolve())
