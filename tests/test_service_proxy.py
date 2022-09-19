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
            await db.connection.execute("insert into Server (guild_id, delimiter) values (34653246457457, '!');")
            await db.connection.execute("insert into Server (guild_id, delimiter) values (475457457437, '!');")
            raise ValueError
            await db.connection.execute("insert into Server (guild_id, delimiter) values (47457437543743, '!');")
    except ValueError:
        ameliapg: AmeliaPgService
        async with ameliapg.pool.acquire() as conn:
            conn: asyncpg.Connection
            num = await conn.fetchval("select count(id) from Server;")
            assert num == 3 # 3 already in fixture

@pytest.mark.asyncio
async def test_transaction_succeeds(ameliapg):

    async with ameliapg as db:
        db: ServiceProxy
        print(db.connection)
        assert hasattr(db, 'forum_channels')
        # 3 already preconfigured in this fixture
        await db.connection.execute("insert into Server (guild_id, delimiter) values (456456, '!');")
        await db.connection.execute("insert into Server (guild_id, delimiter) values (546545, '!');")
        await db.connection.execute("insert into Server (guild_id, delimiter) values (465465, '!');")


    async with ameliapg.pool.acquire() as conn:
        conn: asyncpg.Connection
        num = await conn.fetchval("select count(id) from Server;")
        assert num == 6

@pytest.mark.asyncio
async def test_regular_commit(ameliapg):
    try:
        async with ameliapg.pool.acquire() as connection:
            # 3 already preconfigured in this fixture
            await connection.execute("insert into Server (guild_id, delimiter) values (5465654, '!');")
            await connection.execute("insert into Server (guild_id, delimiter) values (45565, '!');")
            raise ValueError
            await connection.execute("insert into Server (guild_id, delimiter) values (44565465, '!');")
    except ValueError:
        async with ameliapg.pool.acquire() as conn:
            conn: asyncpg.Connection
            num = await conn.fetchval("select count(id) from Server;")
            assert num == 5

