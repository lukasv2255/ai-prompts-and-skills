from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        return int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use WIDTHxHEIGHT, for example 1080x1350") from exc


def is_dark_column(image: Image.Image, x: int) -> bool:
    column = image.crop((x, 0, x + 1, image.height)).convert("L")
    stat = ImageStat.Stat(column)
    return stat.mean[0] < 238


def find_column_groups(image: Image.Image, expected: int) -> list[tuple[int, int]]:
    dark = [is_dark_column(image, x) for x in range(image.width)]

    groups: list[tuple[int, int]] = []
    start: int | None = None
    for index, active in enumerate(dark):
        if active and start is None:
            start = index
        elif not active and start is not None:
            if index - start > image.width * 0.05:
                groups.append((start, index))
            start = None

    if start is not None and image.width - start > image.width * 0.05:
        groups.append((start, image.width))

    if len(groups) == expected:
        return groups

    # Fallback: crop the non-white content area and split it evenly.
    background = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    bbox = ImageChops.difference(image, background).getbbox() or (0, 0, image.width, image.height)
    left, _, right, _ = bbox
    panel_width = (right - left) / expected
    return [
        (round(left + i * panel_width), round(left + (i + 1) * panel_width))
        for i in range(expected)
    ]


def content_y_bounds(image: Image.Image) -> tuple[int, int]:
    background = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    bbox = ImageChops.difference(image, background).getbbox()
    if bbox is None:
        return 0, image.height
    return bbox[1], bbox[3]


def fit_without_distortion(crop: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Fit a slide crop into the target canvas without stretching faces or text."""
    target_w, target_h = size
    crop_ratio = crop.width / crop.height
    target_ratio = target_w / target_h

    # Build a soft full-canvas background from the same slide, then place the
    # untouched-ratio crop on top. This avoids the "squeezed carousel" effect.
    if crop_ratio < target_ratio:
        bg_scale = target_w / crop.width
    else:
        bg_scale = target_h / crop.height
    bg_size = (round(crop.width * bg_scale), round(crop.height * bg_scale))
    background = crop.resize(bg_size, Image.Resampling.LANCZOS)
    bg_left = max((background.width - target_w) // 2, 0)
    bg_top = max((background.height - target_h) // 2, 0)
    background = background.crop((bg_left, bg_top, bg_left + target_w, bg_top + target_h))
    background = background.filter(ImageFilter.GaussianBlur(radius=24))

    fit_scale = min(target_w / crop.width, target_h / crop.height)
    fit_size = (round(crop.width * fit_scale), round(crop.height * fit_scale))
    foreground = crop.resize(fit_size, Image.Resampling.LANCZOS)
    x = (target_w - fit_size[0]) // 2
    y = (target_h - fit_size[1]) // 2
    background.paste(foreground, (x, y))
    return background


def split_strip(input_path: Path, out_dir: Path, slides: int, resize: tuple[int, int]) -> dict:
    image = Image.open(input_path).convert("RGB")
    out_dir.mkdir(parents=True, exist_ok=True)

    y1, y2 = content_y_bounds(image)
    groups = find_column_groups(image, slides)
    outputs = []

    for index, (x1, x2) in enumerate(groups, start=1):
        crop = image.crop((x1, y1, x2, y2))
        crop = fit_without_distortion(crop, resize)
        out_path = out_dir / f"{index:02d}.png"
        crop.save(out_path)
        outputs.append({"index": index, "file": out_path.name, "source_crop": [x1, y1, x2, y2]})

    sheet_width = resize[0] * len(outputs)
    sheet = Image.new("RGB", (sheet_width, resize[1]), "white")
    for index, item in enumerate(outputs):
        slide = Image.open(out_dir / item["file"]).convert("RGB")
        sheet.paste(slide, (index * resize[0], 0))
    sheet_path = out_dir / "contact-sheet.png"
    sheet.save(sheet_path)

    manifest = {
        "input": str(input_path),
        "slides": slides,
        "resize": list(resize),
        "fit_mode": "preserve_aspect_with_blurred_background",
        "outputs": outputs,
        "contact_sheet": sheet_path.name,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Split a horizontal IG carousel concept strip into individual slides.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--slides", type=int, default=5)
    parser.add_argument("--resize", type=parse_size, default=(1080, 1350))
    args = parser.parse_args()

    manifest = split_strip(args.input, args.out_dir, args.slides, args.resize)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
