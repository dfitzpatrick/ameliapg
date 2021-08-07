from __future__ import annotations
import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import GuildConfig, AutoRole


SQL_SERVER_CREATE = """
INSERT INTO Server (guild_id, delimiter, auto_delete_commands)  
    VALUES ($1, $2, $3) 
    RETURNING id, guild_id, created_at, updated_at, auto_delete_commands, delimiter;
"""
SQL_SERVER_FIND = "SELECT * FROM Server WHERE Server.{} = $1;"
SQL_SERVER_SELECT_ALL = "SELECT * FROM Server"
SQL_SERVER_UPDATE = "UPDATE Server SET guild_id = $2, delimiter = $3, auto_delete_commands = $4 WHERE id = $1;"
SQL_SERVER_DELETE = "DELETE Server WHERE id = $1;"


class ServerRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self) -> t.List[GuildConfig]:
        async with self.pool.acquire() as conn:

            records = await conn.fetch(SQL_SERVER_SELECT_ALL)
            return [GuildConfig(**r) for r in records]

    async def find(self, id: int) -> GuildConfig:
        return await self.find_by('id', id)

    async def find_by(self, column: str, value: t.Any) -> GuildConfig:
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow(SQL_SERVER_FIND.format(column), value)
            if record is None:
                raise NoEntity
            result = GuildConfig(**record)
            return result

    async def create(self, server: GuildConfig) -> t.Optional[GuildConfig]:
        assert server.id is None, "Cannot create an entity with an id defined"
        async with self.pool.acquire() as conn:
            # We use fetch because of RETURNING statement
            entity = await conn.fetch(
                SQL_SERVER_CREATE,
                server.guild_id,
                server.delimiter,
                server.auto_delete_commands
            )
            return GuildConfig(**entity[0])

    async def update(self, server: GuildConfig) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                SQL_SERVER_UPDATE,
                server.id,
                server.guild_id,
                server.delimiter,
                server.auto_delete_commands
            )
            return result == "UPDATE 1"

    async def delete(self, server):
        async with self.pool.acquire() as conn:
            await conn.execute(SQL_SERVER_DELETE, server.guild_id)

    async def find_all_auto_roles(self) -> t.List[AutoRole]:
        sql = """
            SELECT * FROM AutoRole
        """
        async with self.pool.acquire() as conn:
            records = await conn.fetch(sql)
            return [AutoRole(**r) for r in records]


    async def create_auto_role(self, role: AutoRole) -> AutoRole:
        sql = """
        INSERT INTO AutoRole (guild_id, role_id)  
            VALUES ($1, $2) 
            RETURNING id, created_at, updated_at, guild_id, role_id;
        """
        async with self.pool.acquire() as conn:
            # We use fetch because of RETURNING statement
            entity = await conn.fetch(
                sql,
                role.guild_id,
                role.role_id
            )
            record = entity[0]
            return AutoRole(**record)


    async def find_auto_roles_by(self, column: str, value: t.Any) -> t.List[AutoRole]:
        sql = f"""
        SELECT * FROM AutoRole
        WHERE {column} = $1;
        
        """
        container = []
        async with self.pool.acquire() as conn:
            record = await conn.fetch(
                sql,
                value
            )
            if record is None:
                raise NoEntity
            for r in record:
                role = AutoRole(**r)
                container.append(role)
            return container

    async def remove_auto_role(self, role_id: int) -> bool:
        sql = "DELETE FROM AutoRole WHERE role_id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, role_id)
            return result != "DELETE 0"