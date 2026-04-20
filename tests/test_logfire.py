"""Tests for the optional logfire backend.

All tests monkey-patch ``mollog._logfire`` so they don't require the
real ``logfire`` package to be installed.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock

import pytest

import mollog
from mollog import Context, Level, Logger, StreamHandler
from mollog import _logfire as logfire_backend


@pytest.fixture(autouse=True)
def reset_logfire_state() -> None:
    """Save and restore the module-level configured flag + stub between tests."""

    original_mod = logfire_backend._logfire_mod
    original_configured = logfire_backend._CONFIGURED
    yield
    logfire_backend._logfire_mod = original_mod
    logfire_backend._CONFIGURED = original_configured
    Context.clear()


def _install_stub() -> MagicMock:
    stub = MagicMock(name="logfire_stub")
    logfire_backend._logfire_mod = stub
    logfire_backend._CONFIGURED = False
    return stub


class TestConfigureLogfire:
    def test_requires_logfire_installed(self) -> None:
        logfire_backend._logfire_mod = None
        logfire_backend._CONFIGURED = False
        with pytest.raises(ImportError, match="molcrafts-mollog\\[logfire\\]"):
            mollog.configure_logfire(token="x")

    def test_forwards_kwargs_verbatim(self) -> None:
        stub = _install_stub()
        mollog.configure_logfire(
            token="abc",
            service_name="svc",
            send_to_logfire=False,
            console=False,
        )
        stub.configure.assert_called_once_with(
            token="abc",
            service_name="svc",
            send_to_logfire=False,
            console=False,
        )
        assert logfire_backend._CONFIGURED is True

    def test_does_not_read_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # seed every plausible logfire env var; configure_logfire must not
        # surface any of these into its stub call.
        for key in (
            "LOGFIRE_TOKEN",
            "LOGFIRE_SERVICE_NAME",
            "LOGFIRE_SEND_TO_LOGFIRE",
            "LOGFIRE_PROJECT_NAME",
        ):
            monkeypatch.setenv(key, "should-not-be-used")
        stub = _install_stub()
        mollog.configure_logfire(token=None, send_to_logfire=False)
        kwargs = stub.configure.call_args.kwargs
        assert kwargs["token"] is None
        assert kwargs["send_to_logfire"] is False
        assert all("should-not-be-used" not in repr(v) for v in kwargs.values())

    def test_raises_importerror_when_logfire_package_missing(self) -> None:
        # Simulate logfire not installed by nulling out the stored reference.
        logfire_backend._logfire_mod = None
        logfire_backend._CONFIGURED = False
        with pytest.raises(ImportError, match="molcrafts-mollog\\[logfire\\]"):
            mollog.configure_logfire(token="x")
        # Logger.fire must surface the same signal on the hot path.
        with pytest.raises(ImportError, match="molcrafts-mollog\\[logfire\\]"):
            Logger("t").fire("msg")


class TestLoggerFire:
    def test_raises_when_unconfigured(self) -> None:
        _install_stub()
        logger = Logger("app")
        with pytest.raises(RuntimeError, match="configure_logfire"):
            logger.fire("hello")

    def test_sends_to_logfire_with_merged_attributes(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True

        logger = Logger("app")
        token = Context.bind(app="api", region="us")
        try:
            logger.bind(component="auth").fire(
                "shipped",
                level=Level.WARNING,
                status=200,
            )
        finally:
            Context.reset(token)

        stub.log.assert_called_once()
        args, kwargs = stub.log.call_args
        assert args[0] == "warn"
        assert args[1] == "shipped"
        attrs = kwargs["attributes"]
        assert attrs["app"] == "api"
        assert attrs["region"] == "us"
        assert attrs["component"] == "auth"
        assert attrs["status"] == 200
        assert attrs["logger_name"] == "app"

    def test_does_not_trigger_handlers(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True

        buf = io.StringIO()
        logger = Logger("app")
        logger.add_handler(StreamHandler(stream=buf))
        logger.fire("silent")

        assert buf.getvalue() == ""
        stub.log.assert_called_once()

    def test_level_mapping(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True

        logger = Logger("app")
        logger.fire("m", level=Level.CRITICAL)
        assert stub.log.call_args.args[0] == "fatal"
        logger.fire("m", level="debug")
        assert stub.log.call_args.args[0] == "debug"


class TestContextScopeWithLogfire:
    def test_scope_opens_span_when_configured(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True
        span_cm = MagicMock(name="span_cm")
        stub.span.return_value = span_cm

        with Context.scope("request", user_id=42):
            stub.span.assert_called_once_with("request", user_id=42)
            span_cm.__enter__.assert_called_once()
            assert Context.get()["user_id"] == 42

        span_cm.__exit__.assert_called_once()
        assert Context.get() == {}

    def test_scope_without_name_does_not_open_span(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True

        with Context.scope(user_id=42):
            assert Context.get()["user_id"] == 42

        stub.span.assert_not_called()

    def test_scope_degrades_when_logfire_unconfigured(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = False

        with Context.scope("op", step=1):
            snapshot = Context.get()
            assert snapshot["step"] == 1
            assert snapshot["scope"] == "op"

        stub.span.assert_not_called()
        assert Context.get() == {}

    def test_fire_inside_scope_inherits_attributes(self) -> None:
        stub = _install_stub()
        logfire_backend._CONFIGURED = True
        stub.span.return_value = MagicMock()

        logger = Logger("api")
        with Context.scope("request", user_id=42):
            logger.fire("handled", status=200)

        attrs = stub.log.call_args.kwargs["attributes"]
        assert attrs["user_id"] == 42
        assert attrs["status"] == 200
        assert attrs["scope"] == "request"


class TestRemovedSymbols:
    """Regression guard: legacy names must not come back accidentally."""

    @pytest.mark.parametrize(
        "name",
        [
            "BoundLogger",
            "bind_context",
            "clear_context",
            "get_context",
            "reset_context",
            "scoped_context",
            "scope",
        ],
    )
    def test_legacy_name_is_gone(self, name: str) -> None:
        with pytest.raises((ImportError, AttributeError)):
            getattr(mollog, name)
