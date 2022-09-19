import asyncpg
import pytest

from ameliapg.AmeliaPgService import ServiceProxy, AmeliaPgService


@pytest.mark.asyncio
async def test_transaction_fails(ameliapg):
    try:
        async with ameliapg as db:
            db: ServiceProxy
            print(db.connection)
            assert hasattr(db, 'forum_channels')
            await db.connection.execute("insert into Server (guild_id, delimiter) values (1234, '!');")
            await db.connection.execute("insert into Server (guild_id, delimiter) values (456, '!');")
            raise ValueError
            await db.connection.execute("insert into Server (guild_id, delimiter) values (789, '!');")
    except ValueError:
        ameliapg: AmeliaPgService
        async with ameliapg.pool.acquire() as conn:
            conn: asyncpg.Connection
            num = await conn.fetchval("select count(id) from Server;")
            assert num == 0

@pytest.mark.asyncio
async def test_transaction_succeeds(ameliapg):

    async with ameliapg as db:
        db: ServiceProxy
        print(db.connection)
        assert hasattr(db, 'forum_channels')
        await db.connection.execute("insert into Server (guild_id, delimiter) values (1234, '!');")
        await db.connection.execute("insert into Server (guild_id, delimiter) values (456, '!');")
        await db.connection.execute("insert into Server (guild_id, delimiter) values (789, '!');")


    async with ameliapg.pool.acquire() as conn:
        conn: asyncpg.Connection
        num = await conn.fetchval("select count(id) from Server;")
        assert num == 3

@pytest.mark.asyncio
async def test_regular_commit(ameliapg):
    try:
        async with ameliapg.pool.acquire() as connection:
            await connection.execute("insert into Server (guild_id, delimiter) values (1234, '!');")
            await connection.execute("insert into Server (guild_id, delimiter) values (456, '!');")
            raise ValueError
            await connection.execute("insert into Server (guild_id, delimiter) values (789, '!');")
    except ValueError:
        async with ameliapg.pool.acquire() as conn:
            conn: asyncpg.Connection
            num = await conn.fetchval("select count(id) from Server;")
            assert num == 2

