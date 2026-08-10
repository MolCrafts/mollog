---
title: mollog
description: Structured logging for Python with a stdlib-compatible API.
hide:
  - navigation
  - toc
hero:
  kicker: mollog Manual
  title: mollog
  description: A structured logger you can drop in where <code>import logging</code> was. Keep the stdlib format strings and the third-party ecosystem that emits through <code>logging</code>, and gain structured fields, context propagation, JSON / Rich formatters, and an optional Logfire backend.
  install:
    label: Install
    command: pip install molcrafts-mollog
  badges:
    - img: https://img.shields.io/pypi/v/molcrafts-mollog
      href: https://pypi.org/project/molcrafts-mollog/
      alt: PyPI version
    - img: https://img.shields.io/badge/python-3.12%2B-blue.svg
      href: https://pypi.org/project/molcrafts-mollog/
      alt: Python 3.12+
    - img: https://img.shields.io/badge/license-BSD--3--Clause-blue.svg
      href: https://github.com/MolCrafts/mollog/blob/master/LICENSE
      alt: License BSD-3-Clause
  actions:
    - label: Get started
      href: getting-started/
      style: primary
    - label: Configuration
      href: configuration/
    - label: API reference
      href: api/
---

Structured logging for Python with a stdlib-compatible API — projects can drop `import logging` entirely while keeping access to `%(asctime)s`-style format strings and the third-party library ecosystem that emits through stdlib.

[Get started](getting-started.md){ .md-button .md-button--primary }
[API reference](api.md){ .md-button }

## What it gives you

- Drop-in for `logging.basicConfig`: stdlib-style `format=` strings via `StdlibStyleFormatter`
- Stdlib bridge that captures records from libraries which still use `logging` (httpx, urllib3, openai, …) and routes them through mollog
- Top-level helpers — `mollog.info(...)`, `mollog.warning(...)`, `mollog.set_level(...)` — and `Logger.set_level()` that also propagates to stdlib
- Named loggers with hierarchy and propagation
- Structured `extra` fields and reusable context via `Logger.bind()`
- Context-local fields via the `Context` namespace (`Context.scope(...)` doubles as a logfire span when `configure_logfire(...)` has been called)
- Exception and stack capture on every record
- Text, JSON, Rich, and stdlib-style formatters
- Stream, file, rotating-file, timed-rotating, queue, and null handlers
- Optional Logfire backend via `LogfireHandler` and `configure_logfire(...)`
- `configure()` and `shutdown()` helpers for application lifecycle

## Quick example

```python
import mollog

mollog.configure(
    level="INFO",
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
mollog.get_logger("httpx").set_level("WARNING")

mollog.info("service booted", port=8080)
```

## Documentation map

- [Getting Started](getting-started.md) — installation, setup, common patterns
- [Configuration](configuration.md) — root logger setup, stdlib bridge, teardown
- [Context Propagation](context.md) — request and task scoped metadata
- [Behavior](behavior.md) — concurrency, reserved fields, shutdown semantics
- [Logfire](logfire.md) — optional Pydantic Logfire backend
- [Rich Console](rich.md) — colored terminal output
- [API Reference](api.md) — complete exported surface
