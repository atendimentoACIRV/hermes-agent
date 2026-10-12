"""H-C3: pure rational mapping from Hermes timeline frames to native-engine frames.

Does not introduce an independent playback clock or engine authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from workstation.creative_time import CanonicalTime, RationalFps


@dataclass(frozen=True)
class HybridTimeMapping:
    timeline_fps: RationalFps
    source_fps: RationalFps
    timeline_start_frame: int = 0
    source_start_frame: int = 0
    speed: Fraction = Fraction(1, 1)
    reverse: bool = False
    freeze: bool = False
    timeline_end_frame: int | None = None

    def __post_init__(self) -> None:
        if type(self.timeline_start_frame) is not int or self.timeline_start_frame < 0:
            raise ValueError("Invalid timeline start frame")
        if type(self.source_start_frame) is not int or self.source_start_frame < 0:
            raise ValueError("Invalid source start frame")
        if self.timeline_end_frame is not None and (
            type(self.timeline_end_frame) is not int
            or self.timeline_end_frame <= self.timeline_start_frame
        ):
            raise ValueError("Invalid half-open timeline end")
        if not isinstance(self.speed, Fraction) or self.speed <= 0:
            raise ValueError("Speed must be a positive rational")

    def source_time(self, frame: int) -> CanonicalTime:
        if (type(frame) is not int or frame < self.timeline_start_frame
                or (self.timeline_end_frame is not None and frame >= self.timeline_end_frame)):
            raise ValueError("Frame is outside the timeline range")
        origin = Fraction(self.source_start_frame, 1) / self.source_fps.as_fraction()
        if self.freeze:
            return CanonicalTime(origin)
        elapsed = Fraction(frame - self.timeline_start_frame, 1) / self.timeline_fps.as_fraction()
        delta = elapsed * self.speed
        position = origin - delta if self.reverse else origin + delta
        if position < 0:
            raise ValueError("Reverse seek precedes native source beginning")
        return CanonicalTime(position)

    def source_frame(self, frame: int) -> int:
        exact = self.source_time(frame).fraction * self.source_fps.as_fraction()
        return exact.numerator // exact.denominator
