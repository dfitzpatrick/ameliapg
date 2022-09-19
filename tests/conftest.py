import pytest
import asyncpg
import yoyo
import os
import pathlib
from ameliapg import AmeliaPgService

dsn_base = f"postgresql://{os.environ['TEST_DB_USER']}:{os.environ['TEST_DB_PWD']}" + \
               f"@{os.environ['TEST_DB_HOST']}:{os.environ['TEST_DB_PORT']}"
test_dsn = dsn_base + "/tmpdb"
MIGRATIONS = pathlib.Path(__file__).parents[1] / 'migrations'

@pytest.fixture
async def reset_db():

    conn = await asyncpg.connect(dsn_base + "/template1")

    await conn.execute("DROP DATABASE IF EXISTS tmpdb WITH (FORCE);")
    await conn.execute(f"CREATE DATABASE tmpdb OWNER {os.environ['TEST_DB_USER']};")
    await conn.close()
    backend = yoyo.get_backend(test_dsn)
    migrations = yoyo.read_migrations(str(MIGRATIONS))
    print(migrations)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    backend.break_lock()
    yield


@pytest.fixture
async def dsn(reset_db):
    db = await asyncpg.create_pool(test_dsn)

    servers = [
        (123456789, '!'),
        (987654321, ','),
        (455465466, ','),
    ]
    autoroles = [
        (123456789, 12345),
        (123456789, 67890),
        (123456789, 98765),
        (987654321, 43210)
    ]
    async with db.acquire() as conn:
        await conn.executemany("INSERT INTO Server (guild_id, delimiter) VALUES ($1, $2);", servers)

    async with db.acquire() as conn:
        await conn.executemany("INSERT INTO AutoRole (guild_id, role_id) VALUES ($1, $2);", autoroles)

    yield test_dsn

@pytest.fixture
async def ameliapg(reset_db):
    pool = await asyncpg.create_pool(test_dsn)
    conn = await asyncpg.connect(test_dsn)

    servers = [
        (1234, '!'),
        (5678, ','),
        (9123, ','),
    ]
    async with pool.acquire() as conn:
        await conn.executemany("INSERT INTO Server (guild_id, delimiter) VALUES ($1, $2);", servers)
    ameliapg = AmeliaPgService(pool, conn)
    yield ameliapg
    await ameliapg.end()

@pytest.fixture
async def db(reset_db):
    pool = await asyncpg.create_pool(test_dsn)
    yield pool
    await pool.close()

@pytest.fixture
async def server_fixture(db: asyncpg.Pool):
    servers = [
        (123456789, '!'),
        (987654321, ','),
        (455465466, ','),
    ]
    autoroles = [
        (123456789, 12345),
        (123456789, 67890),
        (123456789, 98765),
        (987654321, 43210)
    ]
    async with db.acquire() as conn:
        await conn.executemany("INSERT INTO Server (guild_id, delimiter) VALUES ($1, $2);", servers)

    async with db.acquire() as conn:
        await conn.executemany("INSERT INTO AutoRole (guild_id, role_id) VALUES ($1, $2);", autoroles)
    yield db