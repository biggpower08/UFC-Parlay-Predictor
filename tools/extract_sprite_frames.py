r"""Extract transparent sprite frames from FightScope source sprite sheets.

Requires Pillow:
    C:\venvs\mma-ai\Scripts\python.exe -m pip install pillow

Run from repo root:
    C:\venvs\mma-ai\Scripts\python.exe tools\extract_sprite_frames.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from collections import deque
from typing import Any

try:
    from PIL import Image, ImageChops
except ModuleNotFoundError as exc:  # pragma: no cover - local setup guard
    raise SystemExit(
        "Pillow is required. Install with: "
        r"C:\venvs\mma-ai\Scripts\python.exe -m pip install pillow"
    ) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
SPRITE_ROOT = REPO_ROOT / "app" / "frontend" / "public" / "sprites"
CONFIG_PATH = SPRITE_ROOT / "sprite-extract-map.json"
FRAMES_ROOT = SPRITE_ROOT / "frames"
MANIFEST_PATH = SPRITE_ROOT / "sprite-actions.json"
REPORT_PATH = SPRITE_ROOT / "extraction-report.json"


def corner_background_color(image: Image.Image) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    samples = [
        rgb.getpixel((0, 0)),
        rgb.getpixel((width - 1, 0)),
        rgb.getpixel((0, height - 1)),
        rgb.getpixel((width - 1, height - 1)),
    ]
    return tuple(sum(pixel[channel] for pixel in samples) // len(samples) for channel in range(3))


def make_background_transparent(image: Image.Image, tolerance: int = 28) -> Image.Image:
    rgba = image.convert("RGBA")
    bg = corner_background_color(rgba)
    pixels = rgba.load()
    width, height = rgba.size
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    def is_background(red: int, green: int, blue: int) -> bool:
        distance = max(abs(red - bg[0]), abs(green - bg[1]), abs(blue - bg[2]))
        brightness = max(red, green, blue)
        color_spread = max(red, green, blue) - min(red, green, blue)
        is_light_sheet_background = brightness > 220 and color_spread < 34
        is_dark_sheet_background = brightness < 42 and color_spread < 26
        return distance <= tolerance or is_light_sheet_background or is_dark_sheet_background

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or x < 0 or y < 0 or x >= width or y >= height:
            continue
        visited.add((x, y))
        red, green, blue, alpha = pixels[x, y]
        if not alpha or not is_background(red, green, blue):
            continue
        pixels[x, y] = (red, green, blue, 0)
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return rgba


def trim_transparent_bounds(image: Image.Image) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def auto_detect_frame_crops(source: Image.Image, move: dict[str, Any]) -> list[dict[str, Any]]:
    panel = move["autoPanel"]
    tolerance = int(panel.get("tolerance", 34))
    expected = int(panel.get("expectedFrames", 1))
    padding = int(panel.get("padding", 8))
    if panel.get("strategy") == "orderedGrid":
        segment_width = panel["w"] / expected
        overlap = int(panel.get("overlap", 22))
        frames = []
        for index in range(expected):
            left = max(0, round(segment_width * index) - overlap)
            right = min(panel["w"], round(segment_width * (index + 1)) + overlap)
            frames.append(
                {
                    "x": panel["x"] + left,
                    "y": panel["y"],
                    "w": max(1, right - left),
                    "h": panel["h"],
                    "tolerance": tolerance,
                }
            )
        return frames
    min_gap = int(panel.get("minGap", 14))
    rect = (panel["x"], panel["y"], panel["x"] + panel["w"], panel["y"] + panel["h"])
    crop = source.crop(rect)
    transparent = make_background_transparent(crop, tolerance)
    alpha = transparent.getchannel("A")
    width, height = alpha.size
    pixels = alpha.load()
    active_columns = []
    for x in range(width):
        active = 0
        for y in range(height):
            if pixels[x, y] > 0:
                active += 1
        active_columns.append(active > 2)

    runs: list[list[int]] = []
    start = None
    for x, is_active in enumerate(active_columns):
        if is_active and start is None:
            start = x
        elif not is_active and start is not None:
            if x - start > 3:
                runs.append([start, x - 1])
            start = None
    if start is not None and width - start > 3:
        runs.append([start, width - 1])

    merged: list[list[int]] = []
    for run in runs:
        if merged and run[0] - merged[-1][1] <= min_gap:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    runs = merged

    while len(runs) > expected:
        gaps = [(runs[index + 1][0] - runs[index][1], index) for index in range(len(runs) - 1)]
        _, merge_index = min(gaps, key=lambda item: item[0])
        runs[merge_index][1] = runs[merge_index + 1][1]
        del runs[merge_index + 1]

    if not runs:
        runs = [[0, width - 1]]
    if len(runs) < expected:
        segment_width = width / expected
        runs = [[round(segment_width * index), round(segment_width * (index + 1)) - 1] for index in range(expected)]

    frames = []
    for left, right in runs:
        top = height
        bottom = 0
        for x in range(max(0, left), min(width, right + 1)):
            for y in range(height):
                if pixels[x, y] > 0:
                    top = min(top, y)
                    bottom = max(bottom, y)
        if top > bottom:
            top, bottom = 0, height - 1
        frame_left = max(0, left - padding)
        frame_right = min(width - 1, right + padding)
        frame_top = max(0, top - padding)
        frame_bottom = min(height - 1, bottom + padding)
        frames.append(
            {
                "x": panel["x"] + frame_left,
                "y": panel["y"] + frame_top,
                "w": max(1, frame_right - frame_left + 1),
                "h": max(1, frame_bottom - frame_top + 1),
                "tolerance": tolerance,
            }
        )
    return frames


def export_frame(source: Image.Image, crop: dict[str, Any], output_path: Path) -> dict[str, Any]:
    rect = (crop["x"], crop["y"], crop["x"] + crop["w"], crop["y"] + crop["h"])
    frame = source.crop(rect)
    transparent = make_background_transparent(frame, int(crop.get("tolerance", 28)))
    trimmed = trim_transparent_bounds(transparent)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trimmed.save(output_path)
    alpha_bbox = trimmed.getchannel("A").getbbox()
    return {
        "path": "/" + output_path.relative_to(SPRITE_ROOT.parent).as_posix(),
        "transparent": bool(alpha_bbox),
        "width": trimmed.width,
        "height": trimmed.height,
    }


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def main() -> None:
    config = load_config()
    source_root = SPRITE_ROOT / "source"
    report = {"frames_exported": 0, "missing_source_files": [], "frames": []}
    manifest = {"version": 2, "characters": {}, "actions": config.get("actions", [])}
    if FRAMES_ROOT.exists():
        shutil.rmtree(FRAMES_ROOT)

    for character_id, character in config["characters"].items():
        source_path = source_root / character["source"]
        if not source_path.exists():
            report["missing_source_files"].append(str(source_path))
            continue
        manifest["characters"][character_id] = {
            "displayName": character.get("displayName", character_id),
            "accent": character.get("accent", ""),
            "source": character.get("source", ""),
            "moves": {},
        }
        with Image.open(source_path) as source:
            source = source.convert("RGBA")
            for move_name, move in character["moves"].items():
                frame_crops = auto_detect_frame_crops(source, move) if "autoPanel" in move else move["frames"]
                frame_paths = []
                for index, crop in enumerate(frame_crops):
                    output_path = FRAMES_ROOT / character_id / move_name / f"{index:03d}.png"
                    result = export_frame(source, crop, output_path)
                    frame_paths.append(result["path"])
                    report["frames_exported"] += 1
                    report["frames"].append({"character": character_id, "move": move_name, **result})
                manifest["characters"][character_id]["moves"][move_name] = {
                    "category": move.get("category", "mixed"),
                    "frames": frame_paths,
                    "frameDurations": move.get("frameDurations", [120] * len(frame_paths)),
                    "anchor": move.get("anchor", {"x": 0.5, "y": 1}),
                    "notes": move.get("notes", ""),
                }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"frames_exported": report["frames_exported"], "missing_source_files": report["missing_source_files"]}, indent=2))


if __name__ == "__main__":
    main()
