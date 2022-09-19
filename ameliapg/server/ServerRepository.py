from __future__ import annotations

import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import GuildDB, GuildSchema

SQL_SERVER_CREATE = """
INSERT INTO Server (guild_id, delimiter, auto_delete_commands)  
    VALUES ($1, $2, $3) 
    RETURNING id, guild_id, created_at, updated_at, auto_delete_commands, delimiter;
"""
SQL_SERVER_FIND = "SELECT * FROM Server WHERE {} = $1;"
SQL_SERVER_SELECT_ALL = "SELECT * FROM Server"
SQL_SERVER_UPDATE = "UPDATE Server SET guild_id = $2, delimiter = $3, auto_delete_commands = $4 WHERE id = $1;"
SQL_SERVER_DELETE = "DELETE Server WHERE id = $1;"


class ServerRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self) -> t.List[GuildDB]:
        async with self.pool.acquire() as conn:

            records = await conn.fetch(SQL_SERVER_SELECT_ALL)
            return [GuildDB(**r) for r in records]

    async def find(self, id: int) -> GuildDB:
        try:
            return (await self.find_by('id', id))[0]
        except IndexError:
            raise NoEntity

    async def find_guild(self, guild_id: int) -> GuildDB:
        try:
            return await self.find_by('guild_id', id)[0]
        except IndexError:
            raise NoEntity

    async def find_by(self, column: str, value: t.Any) -> t.List[GuildDB]:
        async with self.pool.acquire() as conn:
            records = await conn.fetch(SQL_SERVER_FIND.format(column), value)
            return [GuildDB(**r) for r in records]


    async def create(self, server: GuildSchema) -> GuildDB:
        async with self.pool.acquire() as conn:
            # We use fetch because of RETURNING statement
            entity = await conn.fetch(
                SQL_SERVER_CREATE,
              server.guild_id,
                server.delimiter,
                server.auto_delete_commands
            )
            return GuildDB(**entity[0])

    async def update(self, server: GuildDB) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                SQL_SERVER_UPDATE,
                server.id,
                server.guild_id,
                server.delimiter,
                server.auto_delete_commands
            )
            return result == "UPDATE 1"

    async def delete(self, server: GuildDB) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(SQL_SERVER_DELETE, server.guild_id)
            return result == "DELETE 1"
