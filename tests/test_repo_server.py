import pytest
from ameliapg.server.ServerRepository import ServerRepository
from ameliapg.server.models import GuildConfig
from ameliapg import errors



@pytest.mark.asyncio
async def test_server_insert(server_fixture):
    repo = ServerRepository(server_fixture)
    data = {
        "guild_id": "4567623",
        "delimiter": "/",
    }
    new = await repo.create(GuildConfig(**data))
    assert new.id == 4


@pytest.mark.asyncio
async def test_server_find(server_fixture):
    repo = ServerRepository(server_fixture)
    entity = await repo.find(1)
    assert isinstance(entity, GuildConfig)
    assert entity.delimiter == "!"
    assert entity.guild_id == 123456789
    assert entity.auto_delete_commands == True

@pytest.mark.asyncio
async def test_server_find_by(server_fixture):
    repo = ServerRepository(server_fixture)
    entity = await repo.find_by('guild_id', 123456789)
    assert entity.delimiter == "!"
    assert entity.guild_id == 123456789

@pytest.mark.asyncio
async def test_server_find_notfound(server_fixture):
    repo = ServerRepository(server_fixture)
    with pytest.raises(errors.NoEntity) as e:
        entity = await repo.find(0)

@pytest.mark.asyncio
async def test_server_find_all(server_fixture):
    repo = ServerRepository(server_fixture)
    entities = await repo.find_all()
    assert len(entities) == 3
    assert all(isinstance(s, GuildConfig) for s in entities)

@pytest.mark.asyncio
async def test_server_update(server_fixture):
    repo = ServerRepository(server_fixture)


    old = queried = await repo.find(3)
    queried.guild_id = 123456223547457
    result = await repo.update(queried)
    new = await repo.find(3)
    assert result == True

@pytest.mark.asyncio
async def test_server_update_failed(server_fixture):
    repo = ServerRepository(server_fixture)
    server = GuildConfig(
        id=0,
        guild_id=1212121212,
        delimiter='~'
    )
    result = await repo.update(server)
    # There is no 0 id, so this should fail
    assert result == False, "UPDATE did not return False when failing."
