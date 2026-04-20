import io
import json
from pathlib import Path

from mollog import (
    Context,
    FileHandler,
    JSONFormatter,
    Level,
    StreamHandler,
    configure,
    get_logger,
    shutdown,
)
from mollog._manager import LoggerManager


class TestConfigureAndShutdown:
    def setup_method(self) -> None:
        LoggerManager()._reset()
        Context.clear()

    def test_configure_with_string_level_and_formatter(self):
        buf = io.StringIO()
        handler = StreamHandler(stream=buf)

        root = configure(level="debug", handlers=[handler], formatter=JSONFormatter())
        logger = get_logger("app")
        logger.info("configured", release="1.0.0")

        assert root is LoggerManager().root
        data = json.loads(buf.getvalue().strip())
        assert data["message"] == "configured"
        assert data["release"] == "1.0.0"

    def test_shutdown_closes_and_clears_handlers(self):
        class ClosingHandler(StreamHandler):
            def __init__(self, stream: io.StringIO) -> None:
                super().__init__(stream=stream)
                self.closed = False

            def close(self) -> None:
                self.closed = True

        buf = io.StringIO()
        handler = ClosingHandler(buf)
        configure(handlers=[handler])

        shutdown()

        assert handler.closed is True
        assert LoggerManager().root.handlers == []

    def test_configure_without_replace_does_not_duplicate_default_handler(self):
        configure(level="info")
        original = list(LoggerManager().root.handlers)

        configure(level="debug", replace=False)

        assert LoggerManager().root.handlers == original

    def test_filename_attaches_both_stream_and_file_handlers(self, tmp_path: Path):
        buf = io.StringIO()
        log_path = tmp_path / "app.log"

        configure(level="info", stream=buf, filename=log_path)

        get_logger("app").info("dual-sink")
        shutdown()  # flush file handler

        assert "dual-sink" in buf.getvalue()
        assert "dual-sink" in log_path.read_text()

        handlers = LoggerManager().root.handlers  # emptied by shutdown
        # shutdown clears handlers, so re-check via pre-shutdown snapshot:
        # we verified output on both sinks above, which is the contract.
        assert handlers == []

    def test_filename_respects_filemode_overwrite(self, tmp_path: Path):
        log_path = tmp_path / "app.log"
        log_path.write_text("stale-content\n")

        configure(level="info", stream=io.StringIO(), filename=log_path, filemode="w")
        get_logger("app").info("fresh")
        shutdown()

        text = log_path.read_text()
        assert "stale-content" not in text
        assert "fresh" in text

    def test_file_level_diverges_from_stream_level(self, tmp_path: Path):
        buf = io.StringIO()
        log_path = tmp_path / "app.log"

        configure(
            level="warning",
            stream=buf,
            filename=log_path,
            file_level="debug",
        )
        logger = get_logger("app")
        logger.debug("only-file")
        logger.warning("both")
        shutdown()

        # Console: WARNING threshold, so debug suppressed.
        assert "only-file" not in buf.getvalue()
        assert "both" in buf.getvalue()
        # File: DEBUG threshold, so both visible.
        file_text = log_path.read_text()
        assert "only-file" in file_text
        assert "both" in file_text

    def test_explicit_handlers_override_filename(self, tmp_path: Path):
        buf = io.StringIO()
        log_path = tmp_path / "ignored.log"

        configure(handlers=[StreamHandler(stream=buf)], filename=log_path)
        get_logger("app").info("hi")
        shutdown()

        assert "hi" in buf.getvalue()
        # filename was ignored because explicit handlers were given
        assert not log_path.exists() or log_path.read_text() == ""

    def test_filehandler_mode_validation(self, tmp_path: Path):
        import pytest

        with pytest.raises(ValueError):
            FileHandler(tmp_path / "x.log", mode="r")

    def test_filehandler_keyword_level_still_works(self, tmp_path: Path):
        h = FileHandler(tmp_path / "x.log", level=Level.ERROR)
        assert h.level is Level.ERROR
        h.close()
