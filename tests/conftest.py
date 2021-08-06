import pytest
import asyncpg
import yoyo
import os
dsn_base = f"postgresql://{os.environ['TEST_DB_USER']}:{os.environ['TEST_DB_PWD']}" + \
               f"@{os.environ['TEST_DB_HOST']}:{os.environ['TEST_DB_PORT']}"
test_dsn = dsn_base + "/tmpdb"


@pytest.fixture
async def reset_db():

    conn = await asyncpg.connect(dsn_base + "/template1")

    await conn.execute("DROP DATABASE IF EXISTS tmpdb WITH (FORCE);")
    await conn.execute(f"CREATE DATABASE tmpdb OWNER {os.environ['TEST_DB_USER']};")
    await conn.close()
    backend = yoyo.get_backend(test_dsn)
    migrations = yoyo.read_migrations('../migrations')
    print(migrations)
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
    backend.break_lock()
    yield


@pytest.fixture
async def dsn(reset_db):
    yield test_dsn


@pytest.fixture
async def db(reset_db):
    pool = await asyncpg.create_pool(test_dsn)
    yield pool
    await pool.close()

@pytest.fixture
async def server_fixture(db: asyncpg.Pool):
    data = [
        (123456789, '!'),
        (987654321, ','),
    ]
    async with db.acquire() as conn:
        await conn.executemany("INSERT INTO Server (guild_id, delimiter) VALUES ($1, $2);", data)
    yield db