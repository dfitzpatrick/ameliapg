from __future__ import annotations

import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import StationChannelSchema, StationChannelDB, StationSchema, StationDB


class StationRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self) -> t.List[StationDB]:
        sql = "SELECT * FROM StationConfig;"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(sql)
            return [StationDB(**r) for r in records]


    async def find_by(self, column: str, value: t.Any) -> t.List[StationDB]:
        sql = "SELECT * FROM StationConfig WHERE {} = $1;"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(sql.format(column), value)
            return [StationDB(**r) for r in records]

    async def find(self, id: int):
        try:
            results = await self.find_by('id', id)
            return results[0]
        except KeyError:
            raise NoEntity

    async def create(self, taf: StationSchema) -> StationDB:
        sql = "INSERT INTO StationConfig (guild_id, restrict_channel, delete_interval) VALUES ($1, $2, $3) RETURNING id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, taf.guild_id, taf.restrict_channel, taf.delete_interval)
            return StationDB(**taf.__dict__, id=id)

    async def delete(self, id: int) -> bool:
        sql = "DELETE FROM StationConfig WHERE id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, id)
            return result == "DELETE 1"


    async def find_all_channels(self):
        sql = "SELECT * FROM StationChannel"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql)
            return [StationChannelDB(**e) for e in results]


    async def fetch_channels_by(self, column: str, value: t.Any) -> t.List[StationChannelDB]:
        sql = "SELECT * FROM StationChannel WHERE {} = $1;"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql.format(column), value)
            return [StationChannelDB(**e) for e in results]


    async def create_channel(self, channel: StationChannelSchema) -> StationChannelDB:
        sql = "INSERT INTO StationChannel (guild_id, channel_id) VALUES ($1, $2) RETURNING id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, channel.guild_id, channel.channel_id)
            return StationChannelDB(**channel.__dict__, id=id)

    async def delete_channel(self, channel_id: int) -> bool:
        sql = "DELETE FROM StationChannel WHERE channel_id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, channel_id)
            return result == "DELETE 1"