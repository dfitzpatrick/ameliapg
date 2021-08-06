import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import Server

SQL_SERVER_CREATE = "INSERT INTO Server (guild_id, delimiter)  VALUES ($1, $2) RETURNING id, guild_id, joined, delimiter;"
SQL_SERVER_FIND = "SELECT * FROM Server WHERE Server.{} = $1;"
SQL_SERVER_SELECT_ALL = "SELECT * FROM Server"
SQL_SERVER_UPDATE = "UPDATE Server SET guild_id = $2, delimiter= $3 WHERE id = $1;"
SQL_SERVER_DELETE = "DELETE Server WHERE id = $1;"


class ServerRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self) -> t.List[Server]:
        async with self.pool.acquire() as conn:

            records = await conn.fetch(SQL_SERVER_SELECT_ALL)
            return [Server(**r) for r in records]

    async def find(self, id: int) -> Server:
        return await self.find_by('id', id)

    async def find_by(self, column: str, value: t.Any) -> Server:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(SQL_SERVER_FIND.format(column), value)
            if record is None:
                raise NoEntity
            result = Server(**record)
            return result

    async def create(self, server: Server) -> t.Optional[Server]:
        assert server.id is None, "Cannot create an entity with an id defined"
        async with self.pool.acquire() as conn:
            # We use fetch because of RETURNING statement
            entity = await conn.fetch(SQL_SERVER_CREATE, server.guild_id, server.delimiter)
            return Server(**entity[0])

    async def update(self, server: Server) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(SQL_SERVER_UPDATE, server.id, server.guild_id, server.delimiter)
            return result == "UPDATE 1"

    async def delete(self, server):
        async with self.pool.acquire() as conn:
            await conn.execute(SQL_SERVER_DELETE, server.guild_id)
