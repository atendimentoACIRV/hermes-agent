"""Real independent video decode benchmark. Measures verifier work, not Hermes UI latency."""
from __future__ import annotations
import argparse
import importlib.util
import json
from math import ceil
from pathlib import Path
import platform
import statistics
import time

FILE = Path(__file__).resolve().parents[1] / "scripts" / "verify_native_export.py"
spec = importlib.util.spec_from_file_location("cql_export_verifier", FILE)
verifier = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(verifier)


def run(video: Path, runs: int, expected_frames: int) -> dict:
    if not 3 <= runs <= 30:
        raise ValueError("runs must be between 3 and 30")
    durations: list[float] = []
    receipts: list[dict] = []
    for _ in range(runs):
        start = time.perf_counter()
        receipt = verifier.verify_video(video, expected_frames=expected_frames)
        durations.append(1000 * (time.perf_counter() - start))
        receipts.append(receipt)
    if len({r["video_sha256"] for r in receipts}) != 1:
        raise ValueError("source video changed during baseline")
    if len({r["unique_frame_hashes"] for r in receipts}) != 1:
        raise ValueError("decoded output changed during baseline")
    ordered = sorted(durations)
    p50 = statistics.median(ordered)
    p95 = ordered[ceil(0.95 * runs) - 1]
    return {
        "status": "PASS_NATIVE", "scope": "FFprobe + full FFmpeg decoded-frame verification latency only",
        "samples": runs, "measured_ms": [round(v,2) for v in durations],
        "p50_ms": round(p50,2), "p95_ms_nearest_rank": round(p95,2),
        "mean_ms": round(statistics.mean(durations),2),
        "environment": {"os": platform.platform(), "python": platform.python_version()},
        "source_sha256": receipts[0]["video_sha256"],
        "frames_each": receipts[0]["decoded_frames"],
        "missing_metrics": ["product edit latency", "CPU", "RAM", "GPU", "cost", "model tokens"],
        "baseline_comparable_only_same_machine_same_fixture": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=Path, required=True)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    data = run(args.video, args.runs, args.frames)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(data,indent=2))
