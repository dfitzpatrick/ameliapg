import asyncpg
import logging

from ameliapg.forum_channels.models import AutoPinDB

log = logging.getLogger(__name__)

class ForumChannelService:

    def __init__(self, connection: asyncpg.Connection):
        self._conn = connection


    async def create_auto_pin(self, guild_id: int, parent_id: int) -> AutoPinDB:
        sql = "insert into autopins (guild_id, parent_id) values ($1, $2) returning *;"
        row = await self._conn.fetchrow(sql, guild_id, parent_id)
        return AutoPinDB(**row)

    async def delete_auto_pin(self, parent_id: int):
        sql = "delete from autopins where parent_id = $1;"
        await self._conn.execute(sql)
