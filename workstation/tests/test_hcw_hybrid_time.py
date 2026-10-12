"""H-C3: exact Hermesian frame mapping for independently editable native engines."""
from fractions import Fraction
import pytest

from workstation.creative_time import RationalFps
from workstation.creative_hybrid_time import HybridTimeMapping


def test_seek_order_independence():
    mapping = HybridTimeMapping(
        timeline_fps=RationalFps(30, 1), source_fps=RationalFps(30, 1),
        timeline_start_frame=0, source_start_frame=0,
    )
    frames = [mapping.source_frame(n) for n in [40, 0, 80, 40]]
    assert frames == [40, 0, 80, 40]


def test_2997_to_30_exact_fraction():
    mapping = HybridTimeMapping(
        timeline_fps=RationalFps(30000, 1001), source_fps=RationalFps(30, 1),
        timeline_start_frame=0, source_start_frame=0,
    )
    assert mapping.source_time(300).to_seconds() == Fraction(1001, 100)
    assert mapping.source_frame(300) == 300


def test_speed_offset_reverse_and_freeze():
    forward = HybridTimeMapping(RationalFps(30), RationalFps(60),
        timeline_start_frame=10, source_start_frame=20, speed=Fraction(1, 2))
    assert forward.source_frame(10) == 20
    assert forward.source_frame(40) == 50

    reverse = HybridTimeMapping(RationalFps(30), RationalFps(30),
        timeline_start_frame=0, source_start_frame=100, reverse=True)
    assert reverse.source_frame(10) == 90

    frozen = HybridTimeMapping(RationalFps(30), RationalFps(30),
        timeline_start_frame=0, source_start_frame=77, freeze=True)
    assert [frozen.source_frame(x) for x in (0, 40, 80)] == [77, 77, 77]


def test_out_of_range_invalid_ratios_and_unsupported_time():
    bounded = HybridTimeMapping(RationalFps(30), RationalFps(30),
        timeline_start_frame=20, timeline_end_frame=30)
    with pytest.raises(ValueError):
        bounded.source_frame(19)
    with pytest.raises(ValueError):
        bounded.source_frame(30)
    with pytest.raises(ValueError):
        HybridTimeMapping(RationalFps(30), RationalFps(30), speed=Fraction(-1))
    with pytest.raises(ValueError):
        HybridTimeMapping(RationalFps(30), RationalFps(30), speed=Fraction(0))
