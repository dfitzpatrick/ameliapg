from __future__ import annotations

import asyncpg

from ameliapg.forum_channels.models import AutoPinSchema, AutoPinDB


class ForumChannelRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_auto_pin(self, schema: AutoPinSchema):
        sql = "insert into autopins (guild_id, parent_id) values ($1, $2) returning id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, schema.guild_id, schema.parent_id)
            return AutoPinDB(**schema.__dict__, id=id)

    async def remove_auto_pin(self, parent_id: int):
        sql = "DELETE FROM autopins WHERE parent_id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, parent_id)
            return result == "DELETE 1"
