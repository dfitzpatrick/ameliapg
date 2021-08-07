from __future__ import annotations
import asyncio
import json
import typing as t

import asyncpg
from ameliapg.errors import UnknownEntity
from ameliapg.models import PgNotify
from ameliapg.server import ServerRepository
from ameliapg.server.models import GuildConfig, AutoRole
import logging
log = logging.getLogger(__name__)

class AmeliaPgService():

    @classmethod
    async def from_dsn(cls, dsn: str, listen: bool = True) -> 'AmeliaPgService':
        pool = await asyncpg.create_pool(dsn)
        conn = await asyncpg.connect(dsn)
        o = cls(pool, conn)
        await o.start_listening()
        return o

    def __init__(self, pool, connection, loop=None):
        self.pool: asyncpg.Pool = pool
        self._server_repo = ServerRepository(self.pool)
        self._conn: asyncpg.Connection = connection
        self.listeners: t.List[t.Callable] = []
        self.loop = asyncio.get_running_loop() if loop is None else loop

    def _notify(self, connection: asyncpg.Connection, pid: int, channel: str, payload: str):
        log.debug(f"PG Notify: {payload}")
        payload = json.loads(payload)

        table_map = {
            'server': GuildConfig,
        }
        entity_t = table_map.get(payload['table'])
        if entity_t is None:
            raise UnknownEntity

        result = PgNotify(
            table=payload['table'],
            action=payload['action'],
            entity=entity_t(**payload['data'])
        )
        for callback in self.listeners:
            asyncio.ensure_future(callback(result))


    def register_listener(self, callback: t.Callable):
        self.listeners.append(callback)

    async def start_listening(self):
        if not self._conn.is_closed():
            await self._conn.add_listener('events', self._notify)

    async def stop_listening(self):
        if self._conn is not None and not self._conn.is_closed():
            await self._conn.remove_listener('events', self._notify)
            await self._conn.close()

    async def end(self):
        await self.pool.close()
        if not self._conn.is_closed():
            await self.stop_listening()
            await self._conn.close()


    async def get_servers(self) -> t.List[GuildConfig]:
        servers = await self._server_repo.find_all()
        return servers

    async def new_guild_config(self, guild_id: int) -> GuildConfig:
        gc = await self._server_repo.create(GuildConfig(guild_id=guild_id))
        return gc

    async def add_auto_role_to_guild(self, guild_id: int, role_id: int) -> AutoRole:
        """
        Adds a new instance for an AutoRole in the database.
        Parameters
        ----------
        guild_id
            The discord identifier for a guild
        role_id
            The discord identifier for a role
        Returns
        -------
        AutoRole
        """
        auto_role = AutoRole(guild_id=guild_id, role_id=role_id)
        role = await self._server_repo.create_auto_role(auto_role)
        return role

    async def remove_auto_role_from_guild(self, role_id: int):
        await self._server_repo.remove_auto_role(role_id)

    async def fetch_guild_config(self, guild_id: int):
        """
        Fetches off a unique key in the database guild_id.
        Parameters
        ----------
        guild_id
            The discord identifier for a guild
        Returns
        -------
        GuildConfig
        """
        gc = await self._server_repo.find_by('guild_id', guild_id)
        return gc

    async def fetch_auto_roles(self, by=()):
        if by == ():
            return await self._server_repo.find_all_auto_roles()
        return await self._server_repo.find_auto_roles_by(by[0], by[1])


    def __del__(self):
        try:
            if self.loop.is_running():
                self.loop.create_task(self.end())
            else:
                self.loop.run_until_complete(self.end())
        except Exception:
            pass
