from __future__ import annotations

import typing as t

import asyncpg

from ameliapg.errors import NoEntity
from .models import AutoRoleDB, AutoRoleSchema


class AutoRoleRepository:

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def find_all(self) -> t.List[AutoRoleDB]:
        sql = "SELECT * FROM AutoRole"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql)
            return [AutoRoleDB(**e) for e in results]

    async def find_by(self, column: str, value: t.Any) -> t.List[AutoRoleDB]:
        sql = "SELECT * FROM AutoRole WHERE {} = $1;"
        async with self.pool.acquire() as conn:
            results = await conn.fetch(sql.format(column), value)
            return [AutoRoleDB(**e) for e in results]

    async def find(self, id: int) -> AutoRoleDB:
        try:
            results = await self.find_by('id', id)
            return results[0]
        except KeyError:
            raise NoEntity

    async def create(self, auto_role: AutoRoleSchema) -> AutoRoleDB:
        sql = "INSERT INTO AutoRole (guild_id, role_id) VALUES ($1, $2) RETURNING id;"
        async with self.pool.acquire() as conn:
            id = await conn.fetchval(sql, auto_role.guild_id, auto_role.role_id)
            return AutoRoleDB(**auto_role.__dict__, id=id)

    async def delete(self, role_id: int) -> bool:
        sql = "DELETE FROM AutoRole WHERE role_id = $1;"
        async with self.pool.acquire() as conn:
            result = await conn.execute(sql, role_id)
            return result == "DELETE 1"