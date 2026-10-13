"""Independent native video acceptance: FFprobe metadata + FFmpeg decoded RGB frames.

This is not a renderer. No project state, authority, or video pixels are synthesized.
Use this on actual artifacts emitted by the existing native engines.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


class VerificationError(RuntimeError):
    pass


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_video(
    video: Path, *, source: Path | None = None, expected_frames: int | None = None,
    expected_width: int | None = None, expected_height: int | None = None,
    require_motion: bool = True, ffmpeg: str = "ffmpeg", ffprobe: str = "ffprobe",
    max_frames: int = 900,
) -> dict:
    start = time.perf_counter()
    if not video.is_file() or video.stat().st_size < 100:
        raise VerificationError("video missing or empty")
    if source is not None and (not source.is_file() or source.stat().st_size == 0):
        raise VerificationError("editable source missing or empty")
    try:
        probe = subprocess.run([
            ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames",
            "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_read_frames",
            "-of", "json", str(video)
        ], capture_output=True, text=True, timeout=35, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise VerificationError(f"ffprobe unavailable: {exc}") from exc
    if probe.returncode != 0:
        raise VerificationError(f"ffprobe failed: {probe.stderr[:400]}")
    try:
        info = json.loads(probe.stdout)["streams"][0]
        width, height = int(info["width"]), int(info["height"])
        rate = Fraction(info["r_frame_rate"])
    except (KeyError, IndexError, ValueError, ZeroDivisionError, TypeError) as exc:
        raise VerificationError("missing or invalid video stream metadata") from exc
    if not 0 < width <= 4096 or not 0 < height <= 4096 or rate <= 0:
        raise VerificationError("invalid dimensions or frame rate")
    if expected_width is not None and width != expected_width:
        raise VerificationError(f"width mismatch: {width} != {expected_width}")
    if expected_height is not None and height != expected_height:
        raise VerificationError(f"height mismatch: {height} != {expected_height}")
    frame_bytes = width * height * 3
    try:
        proc = subprocess.Popen([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(video),
            "-map", "0:v:0", "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError as exc:
        raise VerificationError(f"ffmpeg unavailable: {exc}") from exc
    hashes: list[str] = []
    black_count = 0
    try:
        assert proc.stdout is not None
        while True:
            frame = proc.stdout.read(frame_bytes)
            if not frame:
                break
            if len(frame) != frame_bytes:
                raise VerificationError("truncated decoded RGB frame")
            hashes.append(hashlib.sha256(frame).hexdigest())
            if not any(frame):
                black_count += 1
            if len(hashes) > max_frames:
                raise VerificationError(f"frame safety budget exceeded: {max_frames}")
        assert proc.stderr is not None
        stderr = proc.stderr.read(4000).decode("utf-8", "replace")
        if proc.wait(timeout=25) != 0:
            raise VerificationError(f"ffmpeg decode failed: {stderr[:400]}")
    except Exception:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        raise
    finally:
        if proc.stdout is not None:
            proc.stdout.close()
        if proc.stderr is not None:
            proc.stderr.close()
    count = len(hashes)
    if count == 0:
        raise VerificationError("zero decoded frames")
    if expected_frames is not None and count != expected_frames:
        raise VerificationError(f"decoded frames mismatch: {count} != {expected_frames}")
    reported = info.get("nb_read_frames")
    if reported not in (None, "N/A") and int(reported) != count:
        raise VerificationError(f"ffprobe/decode count mismatch: {reported} != {count}")
    unique = len(set(hashes))
    if require_motion and unique < 2:
        raise VerificationError("no decoded motion: all frame hashes identical")
    if black_count == count:
        raise VerificationError("all decoded frames are black")
    return {
        "status": "PASS_NATIVE",
        "method": "independent ffprobe + full ffmpeg RGB decode",
        "video": str(video.resolve()), "video_sha256": digest(video),
        "source": str(source.resolve()) if source else None,
        "source_sha256": digest(source) if source else None,
        "codec": info.get("codec_name"), "width": width, "height": height,
        "fps": str(rate), "decoded_frames": count, "unique_frame_hashes": unique,
        "black_frames": black_count, "sample_rgb_sha256": {
            str(i): hashes[i] for i in sorted({0, count // 2, count - 1})
        }, "verification_seconds": round(time.perf_counter() - start, 3),
        "scope": "media decode and file integrity only; not native project reopen or UI E2E",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--expected-frames", type=int)
    parser.add_argument("--expected-width", type=int)
    parser.add_argument("--expected-height", type=int)
    parser.add_argument("--allow-static", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = verify_video(
            args.video, source=args.source, expected_frames=args.expected_frames,
            expected_width=args.expected_width, expected_height=args.expected_height,
            require_motion=not args.allow_static,
        )
    except (VerificationError, OSError, ValueError) as exc:
        result = {"status": "FAIL", "reason": str(exc), "video": str(args.video)}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS_NATIVE" else 1


if __name__ == "__main__":
    sys.exit(main())
