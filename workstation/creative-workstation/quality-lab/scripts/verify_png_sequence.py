"""Independent HyperFrames PNG sequence inspection (read-only). Requires Pillow."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image, ImageStat


def inspect(directory: Path, expected_count: int, require_motion: bool = True,
            require_transparency: bool = True) -> dict:
    frames = sorted(directory.glob("*.png"))
    if not frames or len(frames) != expected_count:
        raise ValueError(f"PNG frame count mismatch: {len(frames)} != {expected_count}")
    dims = None
    digests = []
    alpha_min, alpha_max = 255, 0
    for file in frames:
        with Image.open(file) as im:
            im.load()
            if im.mode != "RGBA":
                raise ValueError(f"not RGBA: {file.name}: {im.mode}")
            if dims is None:
                dims = im.size
            if im.size != dims:
                raise ValueError(f"inconsistent dimensions: {file.name}")
            low, high = im.getchannel("A").getextrema()
            alpha_min, alpha_max = min(alpha_min, low), max(alpha_max, high)
            raw = im.tobytes()
        digests.append(hashlib.sha256(raw).hexdigest())
    if require_transparency and not (alpha_min < 255 and alpha_max > 0):
        raise ValueError(f"alpha not compositable: {alpha_min}..{alpha_max}")
    unique = len(set(digests))
    if require_motion and unique < 2:
        raise ValueError("no source motion in decoded PNGs")
    return {"status": "PASS_NATIVE", "method": "Pillow decoded RGBA pixel data",
            "directory": str(directory.resolve()), "dimensions": list(dims),
            "decoded_frames": len(frames), "unique_pixel_frames": unique,
            "alpha_min": alpha_min, "alpha_max": alpha_max,
            "first_pixel_sha256": digests[0], "last_pixel_sha256": digests[-1],
            "scope": "source PNG/alpha/motion only, not composite/export provenance"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--expected-frames", required=True, type=int)
    parser.add_argument("--allow-static", action="store_true")
    parser.add_argument("--allow-opaque", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.directory, args.expected_frames,
                         require_motion=not args.allow_static,
                         require_transparency=not args.allow_opaque)
    except (ValueError, OSError) as exc:
        result = {"status": "FAIL", "reason": str(exc)}
    data = json.dumps(result, ensure_ascii=False, indent=2)
    print(data)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(data + "\n", encoding="utf-8")
    sys.exit(0 if result["status"] == "PASS_NATIVE" else 1)
