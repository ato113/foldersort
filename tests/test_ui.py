import io

from tidy.ui import paint, supports_color


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


def test_no_color_when_not_a_terminal():
    assert not supports_color(io.StringIO())


def test_color_when_terminal(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm")
    assert supports_color(FakeTTY())


def test_no_color_env_wins(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert not supports_color(FakeTTY())


def test_paint_is_passthrough_without_tty():
    assert paint("hello", "red", stream=io.StringIO()) == "hello"


def test_paint_wraps_when_enabled(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("TERM", "xterm")
    result = paint("hello", "red", stream=FakeTTY())
    assert result.startswith("\033[31m") and result.endswith("\033[0m")


def test_unknown_style_is_ignored():
    assert paint("hello", "chartreuse", stream=io.StringIO()) == "hello"
