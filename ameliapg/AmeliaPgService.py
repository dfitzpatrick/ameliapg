from __future__ import annotations

import asyncio
import json
import logging
import typing as t

import asyncpg

from ameliapg.autorole.models import AutoRoleDB, AutoRoleSchema
from ameliapg.autorole.repository import AutoRoleRepository
from ameliapg.errors import UnknownEntity, DuplicateEntity
from ameliapg.metar.models import MetarChannelDB, MetarChannelSchema, MetarDB, MetarSchema
from ameliapg.metar.repository import MetarRepository
from ameliapg.taf.models import TafChannelDB, TafDB, TafSchema, TafChannelSchema
from ameliapg.taf.repository import TafRepository
from ameliapg.station.models import StationChannelDB, StationDB, StationChannelSchema, StationSchema
from ameliapg.station.repository import StationRepository
from ameliapg.models import PgNotify
from ameliapg.server import ServerRepository
from ameliapg.server.models import GuildDB, GuildSchema

log = logging.getLogger(__name__)

class AmeliaPgService():

    @classmethod
    async def from_dsn(cls, dsn: str, listen: bool = True) -> 'AmeliaPgService':
        pool = await asyncpg.create_pool(dsn)
        conn = await asyncpg.connect(dsn)
        o = cls(pool, conn)

        if listen:
            await o.start_listening()
        return o

    def __init__(self, pool, connection, loop=None):
        self.pool: asyncpg.Pool = pool
        self._repo_autorole = AutoRoleRepository(self.pool)
        self._server_repo = ServerRepository(self.pool)
        self._repo_metar = MetarRepository(self.pool)
        self._repo_taf = TafRepository(self.pool)
        self._repo_station = StationRepository(self.pool)
        self._conn: asyncpg.Connection = connection
        self.listeners: t.List[t.Callable] = []
        self.loop = asyncio.get_running_loop() if loop is None else loop

    def _notify(self, connection: asyncpg.Connection, pid: int, channel: str, payload: str):
        log.debug(f"PG Notify: {payload}")
        payload = json.loads(payload)

        table_map = {
            'server': GuildDB,
            'autorole': AutoRoleDB,
            'metarconfig': MetarDB,
            'metarchannel': MetarChannelDB,
            'tafconfig': TafDB,
            'tafchannel': TafChannelDB,
            'stationconfig': StationDB,
            'stationchannel': StationChannelDB,
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


    ###########
    ## GUILD CONFIG
    ###########

    async def get_servers(self) -> t.List[GuildDB]:
        servers = await self._server_repo.find_all()
        return servers

    async def get_guild_config(self, guild_id: int) -> t.List[GuildDB]:
        return await self._server_repo.find_by('guild_id', guild_id)

    async def new_guild_config(self, guild_id: int) -> GuildDB:
        try:
            gc = await self._server_repo.create(GuildSchema(guild_id=guild_id))
            return gc
        except asyncpg.UniqueViolationError:
            raise DuplicateEntity

    async def update_guild_config(self, guild_config: GuildDB) -> bool:
        return await self._server_repo.update(guild_config)

    async def fetch_metar_configs(self):
        return await self._repo_metar.find_all()

    async def new_metar_config(self, guild_id: int) -> MetarDB:
        try:
            mc = await self._repo_metar.create(MetarSchema(guild_id=guild_id))
            return mc
        except asyncpg.UniqueViolationError:
            raise DuplicateEntity

    async def add_metar_channel(self, guild_id: int, channel_id: int) -> MetarChannelDB:
        mc = MetarChannelSchema(guild_id=guild_id, channel_id=channel_id)
        result = await self._repo_metar.create_channel(mc)
        return result

    async def remove_metar_channel(self, channel_id: int) -> bool:
        result = await self._repo_metar.delete_channel(channel_id)
        return result

    async def fetch_metar_channels(self, guild_id: int) -> t.List[MetarChannelDB]:
        return await self._repo_metar.fetch_channels_by("guild_id", guild_id)

    async def fetch_all_metar_channels(self) -> t.List[MetarChannelDB]:
        return await self._repo_metar.find_all_channels()


    async def fetch_taf_configs(self) -> t.List[TafDB]:
        return await self._repo_taf.find_all()

    async def fetch_all_taf_channels(self) -> t.List[TafChannelDB]:
        return await self._repo_taf.find_all_channels()

    async def new_taf_config(self, guild_id: int) -> TafDB:
        try:
            tc = await self._repo_taf.create(TafSchema(guild_id=guild_id))
            return tc
        except asyncpg.UniqueViolationError:
            raise DuplicateEntity

    async def add_taf_channel(self, guild_id: int, channel_id: int) -> TafChannelDB:
        mc = TafChannelSchema(guild_id=guild_id, channel_id=channel_id)
        result = await self._repo_taf.create_channel(mc)
        return result

    async def remove_taf_channel(self, channel_id: int) -> bool:
        result = await self._repo_taf.delete_channel(channel_id)
        return result




    async def fetch_station_configs(self) -> t.List[StationDB]:
        return await self._repo_station.find_all()

    async def fetch_all_station_channels(self) -> t.List[StationChannelDB]:
        return await self._repo_station.find_all_channels()

    async def new_station_config(self, guild_id: int) -> StationDB:
        try:
            tc = await self._repo_station.create(StationSchema(guild_id=guild_id))
            return tc
        except asyncpg.UniqueViolationError:
            raise DuplicateEntity

    async def add_station_channel(self, guild_id: int, channel_id: int) -> StationChannelDB:
        mc = StationChannelSchema(guild_id=guild_id, channel_id=channel_id)
        result = await self._repo_station.create_channel(mc)
        return result

    async def remove_station_channel(self, channel_id: int) -> bool:
        result = await self._repo_station.delete_channel(channel_id)
        return result

    async def add_auto_role_to_guild(self, guild_id: int, role_id: int) -> AutoRoleDB:
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
        AutoRoleConfig
        """
        auto_role = AutoRoleSchema(guild_id=guild_id, role_id=role_id)
        role = await self._repo_autorole.create(auto_role)
        return role

    async def remove_auto_role_from_guild(self, role_id: int) -> bool:
        return await self._repo_autorole.delete(role_id)

    async def fetch_guild_config(self, guild_id: int) -> GuildDB:
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
        gc = await self._server_repo.find_guild(guild_id)
        return gc


    async def fetch_all_auto_roles(self) -> t.List[AutoRoleDB]:
        return await self._repo_autorole.find_all()

    async def fetch_auto_roles(self, guild_id: int) -> t.List[AutoRoleDB]:
        return await self._repo_autorole.find_by('guild_id', guild_id)

    async def create_auto_role(self, auto_role: AutoRoleSchema) -> AutoRoleDB:
        return await self._repo_autorole.create(auto_role)

    async def delete_auto_role(self, role_id: int) -> bool:
        return await self._repo_autorole.delete(role_id)




    def __del__(self):
        try:
            if self.loop.is_running():
                self.loop.create_task(self.end())
            else:
                self.loop.run_until_complete(self.end())
        except Exception:
            pass

