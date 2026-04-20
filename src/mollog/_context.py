from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Any

_context: ContextVar[dict[str, Any]] = ContextVar("mollog_context", default={})


class Context:
    """Structured context fields propagated to every log record.

    All state lives in a module-level :class:`contextvars.ContextVar`, so
    operations are thread- and asyncio-safe. The class itself is stateless
    and is used purely as a namespace; do not instantiate it.

    ``Context.scope`` doubles as a logfire span opener when
    :func:`mollog.configure_logfire` has been called, unifying mollog's
    scoped context with logfire's span API.
    """

    def __init__(self) -> None:  # pragma: no cover - defensive
        raise TypeError("Context is a namespace; do not instantiate.")

    @classmethod
    def get(cls) -> dict[str, Any]:
        """Return a shallow copy of the current context fields."""

        return dict(_context.get())

    @classmethod
    def bind(cls, **attrs: Any) -> Token[dict[str, Any]]:
        """Merge fields into the current context; return a token for :meth:`reset`."""

        merged = dict(_context.get())
        merged.update(attrs)
        return _context.set(merged)

    @classmethod
    def reset(cls, token: Token[dict[str, Any]]) -> None:
        """Restore the context to the state captured by *token*."""

        _context.reset(token)

    @classmethod
    def clear(cls) -> None:
        """Drop all current context fields."""

        _context.set({})

    @classmethod
    @contextmanager
    def scope(cls, name: str | None = None, **attrs: Any) -> Iterator[dict[str, Any]]:
        """Enter a nested context scope.

        Merges *attrs* into the context for the duration of the ``with``
        block. When *name* is given **and** :func:`mollog.configure_logfire`
        has been called, a matching ``logfire.span(name, attributes=attrs)``
        is opened alongside. If logfire is not configured, the *name* is
        still recorded as a ``scope`` field so the structured record keeps
        the same shape across environments.
        """

        bound_attrs = dict(attrs)
        if name is not None:
            bound_attrs.setdefault("scope", name)

        token = cls.bind(**bound_attrs)
        span_cm = None
        if name is not None:
            from mollog import _logfire

            span_cm = _logfire.open_span(name, attrs)

        try:
            if span_cm is not None:
                span_cm.__enter__()
            try:
                yield cls.get()
            finally:
                if span_cm is not None:
                    span_cm.__exit__(None, None, None)
        finally:
            cls.reset(token)
