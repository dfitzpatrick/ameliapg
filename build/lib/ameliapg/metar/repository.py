from __future__ import annotations

import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import MetarSchema, MetarDB, MetarChannelDB, MetarChannelSchema


class MetarRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self):
        sql = "SELECT * FROM MetarConfig;"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(sql)
            return [MetarDB(**r) for r in records]

    async def find_by(self, column: str, value: t.Any) -> t.List[MetarDB]:
        sql = "SELECT * FROM MetarConfig WHERE {} = $1;"
        async with self.pool.acquire() as conn:
            records = await conn.fetch(sql.format(column), value)
            return [MetarDB(**r) for r in records]

    async def find(self, id: int):
        try:
            results = await self.find_by('id', id)
            return results[0]
        except KeyError:
            raise NoEntity

    async def create(self, metar_config: MetarSchema) -> MetarDB:
        sql = "INSERT INTO MetarConfig (guild_id, restrict_channel, delete_interval) VALUES ($1, $2, $3) RETURNING id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, metar_config.guild_id, metar_config.restrict_channel, metar_config.delete_interval)
            return MetarDB(**metar_config.__dict__, id=id)

    async def delete(self, id: int) -> bool:
        sql = "DELETE FROM MetarConfig WHERE id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, id)
            return result == "DELETE 1"

    async def find_all_channels(self):
        sql = "SELECT * FROM MetarChannel"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql)
            return [MetarChannelDB(**e) for e in results]

    async def fetch_channels_by(self, column: str, value: t.Any) -> t.List[MetarChannelDB]:
        sql = "SELECT * FROM MetarChannel WHERE {} = $1;"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql.format(column), value)
            return [MetarChannelDB(**e) for e in results]


    async def create_channel(self, channel: MetarChannelSchema) -> MetarChannelDB:
        sql = "INSERT INTO MetarChannel (guild_id, channel_id) VALUES ($1, $2) RETURNING id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, channel.guild_id, channel.channel_id)
            return MetarChannelDB(**channel.__dict__, id=id)

    async def delete_channel(self, channel_id: int) -> bool:
        sql = "DELETE FROM MetarChannel WHERE channel_id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, channel_id)
            return result == "DELETE 1"