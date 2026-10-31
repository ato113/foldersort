import os
import time
from datetime import timedelta

import pytest

from foldersort.rules import Rule, RuleError, _parse_age, _parse_size


@pytest.mark.parametrize(
    "value,expected",
    [("1024", 1024), ("1KB", 1024), ("10MB", 10 * 1024**2), ("1.5GB", int(1.5 * 1024**3)), (42, 42)],
)
def test_parse_size(value, expected):
    assert _parse_size(value) == expected


def test_parse_size_rejects_nonsense():
    with pytest.raises(RuleError):
        _parse_size("soon")


@pytest.mark.parametrize(
    "value,expected",
    [("7d", timedelta(days=7)), ("2w", timedelta(days=14)), ("1y", timedelta(days=365)), (3, timedelta(days=3))],
)
def test_parse_age(value, expected):
    assert _parse_age(value) == expected


def test_extensions_are_normalized():
    rule = Rule.from_dict({"name": "Images", "target": "Images", "extensions": ["PNG", ".jpg"]})
    assert rule.extensions == [".png", ".jpg"]


def test_rule_requires_target():
    with pytest.raises(RuleError):
        Rule.from_dict({"name": "Broken"})


def test_matches_by_extension(tmp_path):
    rule = Rule.from_dict({"name": "Images", "target": "Images", "extensions": ["png"]})
    image = tmp_path / "photo.PNG"
    image.write_bytes(b"x")
    document = tmp_path / "notes.txt"
    document.write_text("x")

    assert rule.matches(image)
    assert not rule.matches(document)


def test_matches_by_pattern(tmp_path):
    rule = Rule.from_dict({"name": "Shots", "target": "Shots", "patterns": ["screenshot*"]})
    hit = tmp_path / "Screenshot 2026-01-01.png"
    hit.write_bytes(b"x")
    miss = tmp_path / "holiday.png"
    miss.write_bytes(b"x")

    assert rule.matches(hit)
    assert not rule.matches(miss)


def test_conditions_combine(tmp_path):
    """A file must satisfy every condition, not just one."""
    rule = Rule.from_dict(
        {"name": "Big images", "target": "Big", "extensions": ["png"], "larger_than": "1KB"}
    )
    big = tmp_path / "big.png"
    big.write_bytes(b"x" * 5000)
    small = tmp_path / "small.png"
    small.write_bytes(b"x")

    assert rule.matches(big)
    assert not rule.matches(small)


def test_matches_by_age(tmp_path):
    rule = Rule.from_dict({"name": "Old", "target": "Old", "older_than": "30d"})
    old = tmp_path / "old.txt"
    old.write_text("x")
    long_ago = time.time() - timedelta(days=60).total_seconds()
    os.utime(old, (long_ago, long_ago))

    fresh = tmp_path / "fresh.txt"
    fresh.write_text("x")

    assert rule.matches(old)
    assert not rule.matches(fresh)


def test_directories_never_match(tmp_path):
    rule = Rule.from_dict({"name": "Everything", "target": "All"})
    folder = tmp_path / "folder"
    folder.mkdir()
    assert not rule.matches(folder)
