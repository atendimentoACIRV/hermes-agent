"""Tests for CWN-06 render adapter contracts and engine selection."""
from fractions import Fraction
from pathlib import Path
import pytest

from workstation.creative_document import (
    Asset,
    Clip,
    Composition,
    CreativeDocument,
    Track,
    create_empty_project,
)
from workstation.creative_time import CanonicalTime, RationalFps, TimeRange
from workstation.creative_render_adapters import (
    ElectronChromiumAdapter,
    FFmpegWebCodecsAdapter,
    FrameResult,
    HyperFramesAdapter,
    RenderAdapterCapabilities,
    RenderCapability,
    RenderContext,
    RenderEngine,
    get_adapter,
    list_available_adapters,
    select_best_adapter,
)


def test_adapter_capabilities_registration():
    """All three default adapters should be registered with correct capabilities."""
    adapters = list_available_adapters()
    engines = {a.engine for a in adapters}
    assert RenderEngine.ELECTRON_CHROMIUM in engines
    assert RenderEngine.HYPERFRAMES in engines
    assert RenderEngine.FFMPEG_WEBCODECS in engines


def test_electron_chromium_capabilities():
    """Electron adapter declares vector raster and seek capabilities."""
    adapter = get_adapter(RenderEngine.ELECTRON_CHROMIUM)
    assert adapter is not None
    caps = adapter.capabilities
    assert caps.engine == RenderEngine.ELECTRON_CHROMIUM
    assert RenderCapability.SEEK_ARBITRARY in caps.capabilities
    assert RenderCapability.VECTOR_RASTER in caps.capabilities
    assert RenderCapability.AUDIO_SYNC not in caps.capabilities  # No native audio sync
    assert caps.max_dimensions == (4096, 4096)
    assert caps.license == "MIT"


def test_hyperframes_capabilities():
    """HyperFrames adapter declares full motion capabilities including 3D and procedural."""
    adapter = get_adapter(RenderEngine.HYPERFRAMES)
    assert adapter is not None
    caps = adapter.capabilities
    assert caps.engine == RenderEngine.HYPERFRAMES
    assert RenderCapability.THREE_JS in caps.capabilities
    assert RenderCapability.PROCEDURAL_CODE in caps.capabilities
    assert RenderCapability.AUDIO_SYNC in caps.capabilities
    assert RenderCapability.GPU_ACCELERATION in caps.capabilities
    assert caps.max_dimensions == (7680, 4320)
    assert caps.license == "MPL-2.0"


def test_ffmpeg_capabilities():
    """FFmpeg adapter declares frame accuracy and audio sync."""
    adapter = get_adapter(RenderEngine.FFMPEG_WEBCODECS)
    assert adapter is not None
    caps = adapter.capabilities
    assert caps.engine == RenderEngine.FFMPEG_WEBCODECS
    assert RenderCapability.FRAME_ACCURATE in caps.capabilities
    assert RenderCapability.AUDIO_SYNC in caps.capabilities
    assert RenderCapability.GPU_ACCELERATION in caps.capabilities
    assert RenderCapability.THREE_JS not in caps.capabilities  # No 3D support
    assert caps.max_dimensions == (7680, 4320)
    assert caps.license == "LGPL-2.1"


def test_select_best_adapter_vector_only():
    """For vector-only project, Electron adapter should be selected."""
    required = frozenset([RenderCapability.VECTOR_RASTER, RenderCapability.SEEK_ARBITRARY])
    adapter = select_best_adapter(required)
    assert adapter is not None
    assert adapter.capabilities.engine == RenderEngine.ELECTRON_CHROMIUM


def test_select_best_adapter_audio_video():
    """For A/V project with audio sync, FFmpeg or HyperFrames should be selected."""
    required = frozenset([RenderCapability.FRAME_ACCURATE, RenderCapability.AUDIO_SYNC])
    adapter = select_best_adapter(required)
    assert adapter is not None
    # HyperFrames has more capabilities, should be preferred
    assert adapter.capabilities.engine == RenderEngine.HYPERFRAMES


def test_select_best_adapter_3d_procedural():
    """For 3D/procedural project, HyperFrames should be selected."""
    required = frozenset([RenderCapability.THREE_JS, RenderCapability.PROCEDURAL_CODE])
    adapter = select_best_adapter(required)
    assert adapter is not None
    assert adapter.capabilities.engine == RenderEngine.HYPERFRAMES


def test_select_best_adapter_impossible_requirements():
    """Impossible capability combination should return None."""
    required = frozenset([RenderCapability.THREE_JS, RenderCapability.VECTOR_RASTER])  # No single adapter has both
    adapter = select_best_adapter(required)
    assert adapter is None


def test_adapter_prepare_and_ready():
    """Adapter prepare/ready lifecycle."""
    adapter = ElectronChromiumAdapter()
    assert adapter.ready() is False

    doc = create_empty_project()
    ctx = RenderContext(width=1920, height=1080, fps=30.0, duration=10.0)
    adapter.prepare(doc, ctx)
    assert adapter.ready() is True


def test_adapter_seek_returns_frame_result():
    """Adapter seek returns FrameResult with correct metadata."""
    adapter = ElectronChromiumAdapter()
    doc = create_empty_project()
    ctx = RenderContext(width=1920, height=1080, fps=30.0, duration=10.0)
    adapter.prepare(doc, ctx)

    result = adapter.seek(15, ctx)
    assert isinstance(result, FrameResult)
    assert result.frame_index == 15
    assert result.timestamp == 15 / 30.0
    assert result.metadata.get("engine") == "electron-chromium"


def test_adapter_snapshot_alias():
    """Snapshot is an alias for seek."""
    adapter = FFmpegWebCodecsAdapter()
    doc = create_empty_project()
    ctx = RenderContext(width=1920, height=1080, fps=30.0, duration=10.0)
    adapter.prepare(doc, ctx)

    seek_result = adapter.seek(30, ctx)
    snap_result = adapter.snapshot(30, ctx)
    assert seek_result.frame_index == snap_result.frame_index
    assert seek_result.timestamp == snap_result.timestamp


def test_adapter_cancel_and_dispose():
    """Cancel and dispose should not raise."""
    adapter = ElectronChromiumAdapter()
    doc = create_empty_project()
    ctx = RenderContext(width=1920, height=1080, fps=30.0, duration=10.0)
    adapter.prepare(doc, ctx)

    adapter.cancel()  # Should not raise
    adapter.dispose()
    assert adapter.ready() is False


def test_render_context_creation():
    """RenderContext holds all necessary rendering parameters."""
    ctx = RenderContext(
        workspace_root=Path("/tmp/workspace"),
        fps=60.0,
        width=3840,
        height=2160,
        duration=30.0,
        random_seed=12345,
    )
    assert ctx.fps == 60.0
    assert ctx.width == 3840
    assert ctx.height == 2160
    assert ctx.duration == 30.0
    assert ctx.random_seed == 12345
    assert ctx.workspace_root == Path("/tmp/workspace")


def test_render_receipt_structure():
    """RenderReceipt contains all provenance fields."""
    from workstation.creative_render_adapters import RenderReceipt

    receipt = RenderReceipt(
        operation_id="abc123",
        engine=RenderEngine.HYPERFRAMES,
        success=True,
        frames_rendered=900,
        total_frames=900,
        output_path=Path("/tmp/output.mp4"),
        output_sha256="a" * 64,
        duration_seconds=30.0,
        verified_frames={0: "hash1", 899: "hash2"},
        provenance={"task_id": "task_1", "run_id": 1},
    )
    assert receipt.operation_id == "abc123"
    assert receipt.engine == RenderEngine.HYPERFRAMES
    assert receipt.success is True
    assert receipt.frames_rendered == 900
    assert receipt.verified_frames[0] == "hash1"