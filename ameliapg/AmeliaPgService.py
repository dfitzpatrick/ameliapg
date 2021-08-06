import asyncio
import json
import typing as t

import asyncpg
from ameliapg.errors import UnknownEntity
from ameliapg.models import PgNotify
from ameliapg.server import ServerRepository
from ameliapg.server.models import Server


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
        print(payload)
        payload = json.loads(payload)

        table_map = {
            'server': Server,
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


    async def get_servers(self) -> t.List[Server]:
        servers = await self._server_repo.find_all()
        return servers

    async def record_server_join(self, server: Server):
        await self._server_repo.create(server)






