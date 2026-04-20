# ruff: noqa: E402

import io

import pytest

rich = pytest.importorskip("rich")

from mollog import RichFormatter, StreamHandler
from mollog._level import Level
from mollog._record import LogRecord


def _rec(
    level: Level = Level.INFO,
    message: str = "hello",
    *,
    extra: dict[str, object] | None = None,
    exception: str | None = None,
    stack_info: str | None = None,
) -> LogRecord:
    return LogRecord(
        level=level,
        message=message,
        logger_name="app.worker",
        extra=extra or {},
        exception=exception,
        stack_info=stack_info,
    )


def _plain_formatter() -> RichFormatter:
    # disable terminal emulation so test assertions can look at plain text
    return RichFormatter(force_terminal=False, color_system=None)


class TestRichFormatter:
    def test_produces_pretty_line(self):
        formatter = _plain_formatter()
        out = formatter.format(_rec(extra={"job_id": "a1"}))
        assert "INFO" in out
        assert "app.worker" in out
        assert "hello" in out
        assert "job_id" in out

    def test_can_hide_extra_fields(self):
        formatter = RichFormatter(show_extra=False, force_terminal=False, color_system=None)
        out = formatter.format(_rec(extra={"job_id": "a1"}))
        assert "job_id" not in out

    def test_exception_and_stack_are_rendered(self):
        out = _plain_formatter().format(
            _rec(
                level=Level.ERROR,
                exception="ValueError: boom",
                stack_info="frame one",
            )
        )
        assert "ValueError: boom" in out
        assert "Stack (most recent call last):" in out
        assert "frame one" in out

    def test_emits_ansi_when_terminal_is_forced(self):
        formatter = RichFormatter(color_system="truecolor", force_terminal=True)
        out = formatter.format(_rec(level=Level.ERROR))
        # ANSI CSI escape present when color is on
        assert "\x1b[" in out

    def test_integrates_with_stream_handler(self):
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)
        handler.set_formatter(_plain_formatter())
        handler.handle(_rec(message="handled", extra={"job_id": "z9"}))
        out = buf.getvalue()
        assert "handled" in out
        assert "job_id" in out
        # handler adds its trailing newline
        assert out.endswith("\n")

    def test_package_export_is_available(self):
        assert RichFormatter.__name__ == "RichFormatter"
