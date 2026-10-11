"""Unified render adapter contracts for interchangeable rendering engines (CWN-06)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import uuid


class RenderEngine(str, Enum):
    ELECTRON_CHROMIUM = "electron-chromium"
    HYPERFRAMES = "hyperframes"
    FFMPEG_WEBCODECS = "ffmpeg-webcodecs"
    REMOTION = "remotion"
    CHROMIUM_HEADLESS = "chromium-headless"


class RenderCapability(str, Enum):
    SEEK_ARBITRARY = "seek_arbitrary"
    FRAME_ACCURATE = "frame_accurate"
    AUDIO_SYNC = "audio_sync"
    GPU_ACCELERATION = "gpu_acceleration"
    VECTOR_RASTER = "vector_raster"
    THREE_JS = "three_js"
    PROCEDURAL_CODE = "procedural_code"


@dataclass(frozen=True)
class RenderAdapterCapabilities:
    engine: RenderEngine
    capabilities: frozenset[RenderCapability]
    supported_formats: frozenset[str]
    max_dimensions: tuple[int, int]
    license: str
    version: str


@dataclass
class RenderContext:
    workspace_root: Path | None = None
    fps: float = 30.0
    width: int = 1920
    height: int = 1080
    duration: float = 60.0
    random_seed: int = 42
    profile_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class FrameResult:
    frame_index: int
    timestamp: float
    image_path: Path | None = None
    image_bytes: bytes | None = None
    sha256: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RenderReceipt:
    operation_id: str
    engine: RenderEngine
    success: bool
    frames_rendered: int
    total_frames: int
    output_path: Path | None = None
    output_sha256: str | None = None
    duration_seconds: float = 0.0
    verified_frames: dict[int, str] = field(default_factory=dict)
    error_message: str | None = None
    provenance: dict[str, Any] = field(default_factory=dict)


class RenderAdapter(ABC):
    """Base interface for all rendering engines."""

    @property
    @abstractmethod
    def capabilities(self) -> RenderAdapterCapabilities:
        """Return static capabilities of this render engine."""
        pass

    @abstractmethod
    def prepare(self, project: Any, context: RenderContext) -> None:
        """Prepare the engine for rendering (load assets, compile, warm up)."""
        pass

    @abstractmethod
    def seek(self, frame_index: int, context: RenderContext) -> FrameResult:
        """Render a single frame at the given index (out-of-order allowed)."""
        pass

    @abstractmethod
    def ready(self) -> bool:
        """Check if engine is ready for rendering (assets loaded, compiled)."""
        pass

    @abstractmethod
    def snapshot(self, frame_index: int, context: RenderContext) -> FrameResult:
        """Capture a preview snapshot at the given frame."""
        pass

    @abstractmethod
    def render(self, context: RenderContext, output_path: Path) -> RenderReceipt:
        """Render the full composition to a video file."""
        pass

    @abstractmethod
    def cancel(self) -> None:
        """Cancel any ongoing render operation."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Clean up resources (temp files, processes, GPU contexts)."""
        pass


class ElectronChromiumAdapter(RenderAdapter):
    """Native Electron/Chromium WebContentsView render adapter."""

    @property
    def capabilities(self) -> RenderAdapterCapabilities:
        return RenderAdapterCapabilities(
            engine=RenderEngine.ELECTRON_CHROMIUM,
            capabilities=frozenset([
                RenderCapability.SEEK_ARBITRARY,
                RenderCapability.FRAME_ACCURATE,
                RenderCapability.VECTOR_RASTER,
            ]),
            supported_formats=frozenset(["png", "svg"]),
            max_dimensions=(4096, 4096),
            license="MIT",
            version="1.0.0",
        )

    def __init__(self):
        self._prepared = False
        self._project = None
        self._context = None

    def prepare(self, project: Any, context: RenderContext) -> None:
        self._project = project
        self._context = context
        self._prepared = True

    def seek(self, frame_index: int, context: RenderContext) -> FrameResult:
        if not self._prepared:
            raise RuntimeError("Adapter not prepared")
        # Delegate to existing creative_render.py implementation
        from workstation.creative_render import render_project_for_run
        # This would need actual implementation with WebContentsView
        return FrameResult(
            frame_index=frame_index,
            timestamp=frame_index / context.fps,
            metadata={"engine": "electron-chromium"},
        )

    def ready(self) -> bool:
        return self._prepared

    def snapshot(self, frame_index: int, context: RenderContext) -> FrameResult:
        return self.seek(frame_index, context)

    def render(self, context: RenderContext, output_path: Path) -> RenderReceipt:
        if not self._prepared:
            raise RuntimeError("Adapter not prepared")
        # Delegate to creative_export.py for video encoding
        from workstation.creative_export import export_composition_to_video, VideoExportRequest
        from workstation.creative_time import CanonicalTime, RationalFps

        req = VideoExportRequest(
            project_id=self._project.project_id if hasattr(self._project, 'project_id') else uuid.uuid4().hex,
            composition_id=self._project.compositions[0].composition_id if hasattr(self._project, 'compositions') and self._project.compositions else "",
            output_path=output_path,
            width=context.width,
            height=context.height,
            fps=RationalFps(int(context.fps), 1),
            duration=CanonicalTime.from_seconds(context.duration),
        )
        result = export_composition_to_video(self._project, req, workspace_root=context.workspace_root)
        return RenderReceipt(
            operation_id=uuid.uuid4().hex,
            engine=RenderEngine.ELECTRON_CHROMIUM,
            success=result.success,
            frames_rendered=result.frame_count,
            total_frames=result.frame_count,
            output_path=Path(result.output_path),
            output_sha256=result.sha256,
            duration_seconds=result.duration_seconds,
            verified_frames=result.verified_frames,
        )

    def cancel(self) -> None:
        from workstation.creative_export import cancel_active_render
        if self._project and hasattr(self._project, 'project_id'):
            cancel_active_render(self._project.project_id)

    def dispose(self) -> None:
        self._prepared = False
        self._project = None
        self._context = None


class HyperFramesAdapter(RenderAdapter):
    """HyperFrames CLI render adapter with ffprobe verification."""

    @property
    def capabilities(self) -> RenderAdapterCapabilities:
        return RenderAdapterCapabilities(
            engine=RenderEngine.HYPERFRAMES,
            capabilities=frozenset([
                RenderCapability.SEEK_ARBITRARY,
                RenderCapability.FRAME_ACCURATE,
                RenderCapability.AUDIO_SYNC,
                RenderCapability.GPU_ACCELERATION,
                RenderCapability.THREE_JS,
                RenderCapability.PROCEDURAL_CODE,
            ]),
            supported_formats=frozenset(["mp4", "webm", "png", "gif"]),
            max_dimensions=(7680, 4320),
            license="MPL-2.0",
            version="1.0.0",
        )

    def __init__(self):
        self._prepared = False
        self._installation = None
        self._project_dir = None

    def prepare(self, project: Any, context: RenderContext) -> None:
        # Would load HyperFrames installation and project directory
        self._prepared = True

    def seek(self, frame_index: int, context: RenderContext) -> FrameResult:
        if not self._prepared:
            raise RuntimeError("HyperFrames adapter not prepared")
        return FrameResult(
            frame_index=frame_index,
            timestamp=frame_index / context.fps,
            metadata={"engine": "hyperframes"},
        )

    def ready(self) -> bool:
        return self._prepared

    def snapshot(self, frame_index: int, context: RenderContext) -> FrameResult:
        return self.seek(frame_index, context)

    def render(self, context: RenderContext, output_path: Path) -> RenderReceipt:
        if not self._prepared:
            raise RuntimeError("HyperFrames adapter not prepared")
        # Delegate to creative_hyperframes_render.py
        return RenderReceipt(
            operation_id=uuid.uuid4().hex,
            engine=RenderEngine.HYPERFRAMES,
            success=False,
            frames_rendered=0,
            total_frames=int(context.duration * context.fps),
            error_message="Not fully implemented - delegate to creative_hyperframes_render.py",
        )

    def cancel(self) -> None:
        pass

    def dispose(self) -> None:
        self._prepared = False


class FFmpegWebCodecsAdapter(RenderAdapter):
    """FFmpeg/WebCodecs render adapter for native video encoding."""

    @property
    def capabilities(self) -> RenderAdapterCapabilities:
        return RenderAdapterCapabilities(
            engine=RenderEngine.FFMPEG_WEBCODECS,
            capabilities=frozenset([
                RenderCapability.FRAME_ACCURATE,
                RenderCapability.AUDIO_SYNC,
                RenderCapability.GPU_ACCELERATION,
            ]),
            supported_formats=frozenset(["mp4", "webm", "mov", "mkv", "png", "jpg"]),
            max_dimensions=(7680, 4320),
            license="LGPL-2.1",
            version="1.0.0",
        )

    def __init__(self):
        self._prepared = False

    def prepare(self, project: Any, context: RenderContext) -> None:
        self._prepared = True

    def seek(self, frame_index: int, context: RenderContext) -> FrameResult:
        if not self._prepared:
            raise RuntimeError("FFmpeg adapter not prepared")
        return FrameResult(
            frame_index=frame_index,
            timestamp=frame_index / context.fps,
            metadata={"engine": "ffmpeg-webcodecs"},
        )

    def ready(self) -> bool:
        return self._prepared

    def snapshot(self, frame_index: int, context: RenderContext) -> FrameResult:
        return self.seek(frame_index, context)

    def render(self, context: RenderContext, output_path: Path) -> RenderReceipt:
        if not self._prepared:
            raise RuntimeError("FFmpeg adapter not prepared")
        # Delegate to creative_export.py
        from workstation.creative_export import export_composition_to_video, VideoExportRequest
        from workstation.creative_time import CanonicalTime, RationalFps

        req = VideoExportRequest(
            project_id=project.project_id if hasattr(project, 'project_id') else uuid.uuid4().hex,
            composition_id=project.compositions[0].composition_id if hasattr(project, 'compositions') and project.compositions else "",
            output_path=output_path,
            width=context.width,
            height=context.height,
            fps=RationalFps(int(context.fps), 1),
            duration=CanonicalTime.from_seconds(context.duration),
        )
        result = export_composition_to_video(project, req, workspace_root=context.workspace_root)
        return RenderReceipt(
            operation_id=uuid.uuid4().hex,
            engine=RenderEngine.FFMPEG_WEBCODECS,
            success=result.success,
            frames_rendered=result.frame_count,
            total_frames=result.frame_count,
            output_path=Path(result.output_path),
            output_sha256=result.sha256,
            duration_seconds=result.duration_seconds,
            verified_frames=result.verified_frames,
        )

    def cancel(self) -> None:
        from workstation.creative_export import cancel_active_render
        if hasattr(project, 'project_id'):
            cancel_active_render(project.project_id)

    def dispose(self) -> None:
        self._prepared = False


_RENDER_ADAPTERS: dict[RenderEngine, RenderAdapter] = {}


def register_adapter(engine: RenderEngine, adapter: RenderAdapter) -> None:
    _RENDER_ADAPTERS[engine] = adapter


def get_adapter(engine: RenderEngine) -> RenderAdapter | None:
    return _RENDER_ADAPTERS.get(engine)


def list_available_adapters() -> list[RenderAdapterCapabilities]:
    return [adapter.capabilities for adapter in _RENDER_ADAPTERS.values()]


def select_best_adapter(required: frozenset[RenderCapability]) -> RenderAdapter | None:
    """Select the best available adapter that supports all required capabilities."""
    candidates = [
        adapter for adapter in _RENDER_ADAPTERS.values()
        if required.issubset(adapter.capabilities.capabilities)
    ]
    if not candidates:
        return None
    # Prefer engines with more capabilities
    return max(candidates, key=lambda a: len(a.capabilities.capabilities))


# Register default adapters
register_adapter(RenderEngine.ELECTRON_CHROMIUM, ElectronChromiumAdapter())
register_adapter(RenderEngine.HYPERFRAMES, HyperFramesAdapter())
register_adapter(RenderEngine.FFMPEG_WEBCODECS, FFmpegWebCodecsAdapter())