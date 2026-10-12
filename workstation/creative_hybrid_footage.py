"""Fail-closed numbered RGBA image sequence preflight for EffectCraft footage imports.

This validates real images on disk. It does NOT claim they were rendered by
HyperFrames or imported by a running EffectCraft engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

from PIL import Image, UnidentifiedImageError


class HybridFootageError(ValueError):
    """Native frame sequence is incomplete, unsafe or not compositable."""


_FRAME_NAME = re.compile(r"^([A-Za-z0-9_-]+_)([0-9]{4,})\.png$")


@dataclass(frozen=True)
class HybridFootage:
    first_frame: Path
    frame_count: int
    width: int
    height: int
    has_alpha: bool
    has_motion: bool
    frame_hashes: tuple[str, ...]


def validate_rgba_footage(
    folder: Path, *, frame_count: int, width: int, height: int
) -> HybridFootage:
    """Require consecutive numbered RGBA PNGs, actual transparent pixels and motion."""
    folder = Path(folder)
    if (folder.is_symlink() or not folder.is_dir() or
            any(type(value) is not int or value < 1 for value in (frame_count, width, height)) or
            frame_count < 2 or frame_count > 30_000):
        raise HybridFootageError("Invalid footage directory or frame bounds")
    paths = sorted(folder.glob("*.png"))
    if len(paths) != frame_count:
        raise HybridFootageError("Footage has missing or extra PNG frames")
    parsed = [_FRAME_NAME.fullmatch(p.name) for p in paths]
    if any(m is None for m in parsed):
        raise HybridFootageError("Invalid numbered PNG filename")
    assert all(m is not None for m in parsed)
    stems = {m.group(1) for m in parsed}
    if len(stems) != 1:
        raise HybridFootageError("Footage frame names do not share a sequence prefix")
    indices = [int(m.group(2)) for m in parsed]
    if indices != list(range(indices[0], indices[0] + frame_count)):
        raise HybridFootageError("Footage frame numbering is not consecutive")
    digest_list: list[str] = []
    pixel_digests: list[str] = []
    has_alpha = False
    has_visible = False
    for path in paths:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 128_000_000:
            raise HybridFootageError("Unsafe native footage frame")
        try:
            with Image.open(path) as image:
                if image.format != "PNG" or image.mode != "RGBA" or image.size != (width, height):
                    raise HybridFootageError("Expected actual RGBA PNG pixels with exact dimensions")
                image.load()
                pixels = image.tobytes()
                alpha = image.getchannel("A")
                low, high = alpha.getextrema()
                if high > 0:
                    has_visible = True
                if low < 255:
                    has_alpha = True
                pixel_digests.append(hashlib.sha256(pixels).hexdigest())
        except (OSError, UnidentifiedImageError) as exc:
            raise HybridFootageError("Unreadable native RGBA footage") from exc
        digest_list.append(hashlib.sha256(path.read_bytes()).hexdigest())
    if not has_alpha or not has_visible:
        raise HybridFootageError("Footage lacks compositable visible and transparent pixels")
    moving = len(set(pixel_digests)) > 1
    if not moving:
        raise HybridFootageError("Footage has no visible frame changes")
    return HybridFootage(paths[0].resolve(), frame_count, width, height, has_alpha,
                         moving, tuple(digest_list))


def effectcraft_import_command(footage: HybridFootage, *, fps: int) -> dict:
    """Typed EffectCraft command payload. Execute only via admitted engine runner."""
    if type(fps) is not int or fps < 1 or fps > 240:
        raise HybridFootageError("Unsupported footage frame rate")
    return {
        "command": "file.import",
        "params": {
            "paths": [str(footage.first_frame)],
            "sequence": True,
            "frameRate": fps,
            "addToComp": True,
        },
    }
