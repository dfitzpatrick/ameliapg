import pytest
import asyncpg
import os

dsn_base = f"postgresql://{os.environ['TEST_DB_USER']}:{os.environ['TEST_DB_PWD']}" + \
               f"@{os.environ['TEST_DB_HOST']}:{os.environ['TEST_DB_PORT']}"

@pytest.mark.asyncio
async def test_db_connection():
    conn = await asyncpg.connect(dsn_base)
    assert not conn.is_closed()
    await conn.close()

@pytest.mark.asyncio
async def test_db_server_insert(db):
    query = "INSERT INTO server (guild_id, delimiter) VALUES (123456789, '/');"
    async with db.acquire() as conn:
        status = await conn.execute(query)
        assert status is not None

@pytest.mark.asyncio
async def test_db_server_select(server_fixture):
    query = "SELECT * FROM server"
    async with server_fixture.acquire() as conn:
        records = await conn.fetch(query)
    assert len(records) == 2
