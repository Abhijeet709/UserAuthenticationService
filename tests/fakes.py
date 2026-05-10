"""Shared test doubles used across multiple test modules."""

from __future__ import annotations

from typing import Any


class FakeDB:
    """Minimal async stand-in for :class:`repository.database.Database`.

    Each entry in ``responses`` is either a row dict (or ``None``) returned from
    ``fetchrow``, or an :class:`Exception` instance to raise on that call."""

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, tuple[Any, ...]]] = []

    async def fetchrow(self, query: str, *args: Any) -> Any:
        self.calls.append((query, args))
        response = self._responses[len(self.calls) - 1]
        if isinstance(response, BaseException):
            raise response
        return response
