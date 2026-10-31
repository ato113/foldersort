import pytest

from tidy import suggest


def test_groups_known_families(tmp_path):
    for name in ("a.png", "b.jpg", "c.pdf", "d.mp3"):
        (tmp_path / name).write_bytes(b"x")

    names = {s.name for s in suggest.scan(tmp_path)}

    assert {"Images", "Documents", "Audio"} <= names


def test_counts_files_per_rule(tmp_path):
    for name in ("a.png", "b.jpg", "c.gif"):
        (tmp_path / name).write_bytes(b"x")

    images = next(s for s in suggest.scan(tmp_path) if s.name == "Images")

    assert images.count == 3


def test_screenshots_come_first(tmp_path):
    (tmp_path / "Screenshot 2026-01-01.png").write_bytes(b"x")
    (tmp_path / "holiday.png").write_bytes(b"x")

    suggestions = suggest.scan(tmp_path)

    assert suggestions[0].name == "Screenshots"
    # The screenshot is not also counted as a plain image.
    images = next(s for s in suggestions if s.name == "Images")
    assert images.count == 1


def test_unknown_extensions_grouped_when_repeated(tmp_path):
    for i in range(3):
        (tmp_path / f"file{i}.xyz").write_bytes(b"x")

    names = {s.name for s in suggest.scan(tmp_path)}

    assert "XYZ files" in names


def test_one_off_unknown_extension_is_ignored(tmp_path):
    (tmp_path / "lonely.xyz").write_bytes(b"x")
    assert suggest.scan(tmp_path) == []


def test_hidden_files_ignored(tmp_path):
    (tmp_path / ".secret.png").write_bytes(b"x")
    assert suggest.scan(tmp_path) == []


def test_generated_config_is_loadable(tmp_path):
    """The whole point: what suggest writes must parse back as a config."""
    from tidy.config import Config

    for name in ("a.png", "b.pdf", "Screenshot 1.png"):
        (tmp_path / name).write_bytes(b"x")

    config_file = tmp_path / "tidy.yaml"
    config_file.write_text(suggest.to_config(tmp_path, suggest.scan(tmp_path)), encoding="utf-8")

    config = Config.load(config_file)

    assert config.source == tmp_path
    assert len(config.rules) >= 2


def test_missing_source_raises(tmp_path):
    with pytest.raises(NotADirectoryError):
        suggest.scan(tmp_path / "nope")
