# Logfire Integration

`mollog` can forward structured events to
[pydantic-logfire](https://logfire.pydantic.dev) as an optional backend.
Install the extra to pull it in:

```bash
pip install "molcrafts-mollog[logfire]"
```

## Configuration

`configure_logfire(...)` is a thin wrapper around `logfire.configure(...)`.
It reads **no environment variables** — every setting must be passed
explicitly as a keyword argument:

```python
import mollog

mollog.configure_logfire(
    token="your-write-token",
    service_name="my-api",
)
```

Pass `send_to_logfire=False` to run offline (the logfire console exporter
will still produce output, but nothing is uploaded):

```python
mollog.configure_logfire(token=None, send_to_logfire=False, service_name="dev")
```

Any other keyword you pass is forwarded verbatim to `logfire.configure`.

## Emitting events with `logger.fire`

`logger.fire(...)` is a dedicated channel that forwards an event to
logfire only — it does **not** produce a `LogRecord` and does not go
through any mollog `Handler`. Use `logger.info` / `logger.debug` / etc.
for your local logs, and `logger.fire` when you specifically want an
event on logfire:

```python
logger = mollog.get_logger("api")

logger.info("served locally")                       # mollog only
logger.fire("shipped to logfire", status=200)       # logfire only
logger.fire("warning", level="warning", code=42)    # custom level
```

`Logger.fire` raises `RuntimeError` if `configure_logfire` has not been
called, and `ImportError` if the `logfire` package is not installed.

## Spans via `Context.scope`

`Context.scope(name, **attrs)` unifies mollog's scoped context with
logfire's span API. When `name` is provided **and** logfire is
configured, a matching `logfire.span(name, **attrs)` is opened for the
duration of the block:

```python
from mollog import Context, get_logger

logger = get_logger("api")

with Context.scope("request", user_id=42):
    logger.info("processed locally")       # mollog record, user_id=42
    logger.fire("processed", status=200)   # logfire event inside the span
```

If logfire is not configured (or not installed), `Context.scope` falls
back to a plain context-binding block so the same application code runs
in any environment.

## Merge order

A single `logger.fire(...)` attribute map is built as:

1. `Context.get()` (current `Context.bind` / `scope` fields)
2. `Logger.bind(...)` fields
3. keyword arguments passed to `logger.fire(...)`

Later sources win.
