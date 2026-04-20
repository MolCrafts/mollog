import io
import json

from mollog import (
    Context,
    JSONFormatter,
    Logger,
    StreamHandler,
)


class TestContext:
    def teardown_method(self) -> None:
        Context.clear()

    def test_bind_injects_fields(self):
        buf = io.StringIO()
        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        token = Context.bind(request_id="req-1", trace_id="tr-1")
        try:
            logger.info("started")
        finally:
            Context.reset(token)

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "req-1"
        assert data["trace_id"] == "tr-1"

    def test_scope_restores_previous_state(self):
        token = Context.bind(request_id="outer")
        try:
            with Context.scope(request_id="inner", user_id="u-1"):
                assert Context.get()["request_id"] == "inner"
                assert Context.get()["user_id"] == "u-1"
            assert Context.get()["request_id"] == "outer"
            assert "user_id" not in Context.get()
        finally:
            Context.reset(token)

    def test_scope_with_name_records_scope_field(self):
        with Context.scope("request", user_id="u-2"):
            snapshot = Context.get()
            assert snapshot["scope"] == "request"
            assert snapshot["user_id"] == "u-2"
        # name-only scope still restores cleanly
        assert "scope" not in Context.get()

    def test_scope_without_logfire_degrades_gracefully(self):
        # logfire is not configured during the default test suite; Context.scope
        # with a name must still work as a pure bind/reset scope.
        with Context.scope("op", a=1):
            assert Context.get()["a"] == 1
        assert Context.get() == {}

    def test_per_call_extra_overrides_context(self):
        buf = io.StringIO()
        logger = Logger("app")
        handler = StreamHandler(stream=buf)
        handler.set_formatter(JSONFormatter())
        logger.add_handler(handler)

        token = Context.bind(request_id="outer")
        try:
            logger.info("started", request_id="inner")
        finally:
            Context.reset(token)

        data = json.loads(buf.getvalue().strip())
        assert data["request_id"] == "inner"
