import pytest

from tidy import organizer
from tidy.config import Config, ConfigError
from tidy.rules import Rule


def make_config(tmp_path, **overrides):
    rules = overrides.pop(
        "rules",
        [
            Rule.from_dict({"name": "Images", "target": "Images", "extensions": ["png", "jpg"]}),
            Rule.from_dict({"name": "Docs", "target": "Docs", "extensions": ["pdf", "txt"]}),
        ],
    )
    return Config(source=tmp_path, rules=rules, **overrides)


def test_plan_groups_files_by_rule(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "b.pdf").write_bytes(b"x")
    (tmp_path / "c.xyz").write_bytes(b"x")

    moves = organizer.plan(make_config(tmp_path))

    assert len(moves) == 2
    assert {m.rule for m in moves} == {"Images", "Docs"}


def test_plan_skips_hidden_files(tmp_path):
    (tmp_path / ".secret.png").write_bytes(b"x")
    assert organizer.plan(make_config(tmp_path)) == []


def test_plan_ignores_files_already_in_target(tmp_path):
    """Running twice should not shuffle files that are already filed."""
    images = tmp_path / "Images"
    images.mkdir()
    (images / "already.png").write_bytes(b"x")

    assert organizer.plan(make_config(tmp_path, recursive=True)) == []


def test_first_matching_rule_wins(tmp_path):
    (tmp_path / "screenshot1.png").write_bytes(b"x")
    rules = [
        Rule.from_dict({"name": "Shots", "target": "Shots", "patterns": ["screenshot*"]}),
        Rule.from_dict({"name": "Images", "target": "Images", "extensions": ["png"]}),
    ]

    moves = organizer.plan(make_config(tmp_path, rules=rules))

    assert len(moves) == 1
    assert moves[0].rule == "Shots"


def test_apply_moves_files(tmp_path):
    (tmp_path / "a.png").write_bytes(b"content")
    moves = organizer.plan(make_config(tmp_path))

    performed = organizer.apply(moves)

    assert len(performed) == 1
    assert not (tmp_path / "a.png").exists()
    assert (tmp_path / "Images" / "a.png").read_bytes() == b"content"


def test_apply_renames_on_conflict(tmp_path):
    images = tmp_path / "Images"
    images.mkdir()
    (images / "a.png").write_bytes(b"first")
    (tmp_path / "a.png").write_bytes(b"second")

    moves = organizer.plan(make_config(tmp_path))
    organizer.apply(moves, on_conflict="rename")

    assert (images / "a.png").read_bytes() == b"first"
    assert (images / "a (1).png").read_bytes() == b"second"


def test_apply_skips_on_conflict(tmp_path):
    images = tmp_path / "Images"
    images.mkdir()
    (images / "a.png").write_bytes(b"first")
    (tmp_path / "a.png").write_bytes(b"second")

    moves = organizer.plan(make_config(tmp_path))
    performed = organizer.apply(moves, on_conflict="skip")

    assert performed == []
    assert (tmp_path / "a.png").exists()


def test_undo_restores_everything(tmp_path):
    (tmp_path / "a.png").write_bytes(b"x")
    (tmp_path / "b.pdf").write_bytes(b"y")

    performed = organizer.apply(organizer.plan(make_config(tmp_path)))
    organizer.undo(performed)

    assert (tmp_path / "a.png").read_bytes() == b"x"
    assert (tmp_path / "b.pdf").read_bytes() == b"y"


def test_plan_rejects_missing_source(tmp_path):
    config = make_config(tmp_path / "nope")
    with pytest.raises(NotADirectoryError):
        organizer.plan(config)


def test_config_rejects_unknown_conflict_policy(tmp_path):
    config_file = tmp_path / "tidy.yaml"
    config_file.write_text(
        "source: .\non_conflict: explode\nrules:\n  - name: X\n    target: X\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError):
        Config.load(config_file)


def test_config_requires_rules(tmp_path):
    config_file = tmp_path / "tidy.yaml"
    config_file.write_text("source: .\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        Config.load(config_file)
