"""Thin async wrapper around an asyncpg connection pool."""
from __future__ import annotations

import asyncio
from typing import Any, Optional

import asyncpg

from configs.settings import get_settings


class Database:
    def __init__(self, database_url: Optional[str] = None) -> None:
        self.database_url = database_url or get_settings().DATABASE_URL
        if not self.database_url:
            raise ValueError("DATABASE_URL is not set.")
        self.pool: Optional[asyncpg.Pool] = None
        self._connect_lock = asyncio.Lock()

    async def connect(self) -> None:
        if self.pool is not None:
            return
        # Lock prevents two coroutines from creating the pool concurrently.
        async with self._connect_lock:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.database_url)

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        await self.connect()
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]

    async def fetchrow(self, query: str, *args: Any) -> Optional[dict[str, Any]]:
        await self.connect()
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row is not None else None

    async def execute(self, query: str, *args: Any) -> str:
        await self.connect()
        assert self.pool is not None
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
