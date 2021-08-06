import pytest
from ameliapg.server.ServerRepository import ServerRepository
from ameliapg.server.models import Server
from ameliapg import errors



@pytest.mark.asyncio
async def test_server_insert(server_fixture):
    repo = ServerRepository(server_fixture)
    data = {
        "guild_id": "4567623",
        "delimiter": "/",
    }
    new = await repo.create(Server(**data))
    assert new.id == 3


@pytest.mark.asyncio
async def test_server_find(server_fixture):
    repo = ServerRepository(server_fixture)
    entity = await repo.find(1)
    assert isinstance(entity, Server)
    assert entity.delimiter == "!"
    assert entity.guild_id == 123456789

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
    assert len(entities) == 2
    assert all(isinstance(s, Server) for s in entities)

@pytest.mark.asyncio
async def test_server_update(server_fixture):
    repo = ServerRepository(server_fixture)
    server = Server(
        id=1,
        guild_id=12121212121,
        delimiter='~'
    )
    result = await repo.update(server)
    queried = await repo.find(1)
    assert queried.guild_id == server.guild_id, "guild_id did not update"
    assert queried.delimiter == server.delimiter, "delimiter did not update"
    assert result == True, "UPDATE returned False when succeeding."

@pytest.mark.asyncio
async def test_server_update_failed(server_fixture):
    repo = ServerRepository(server_fixture)
    server = Server(
        id=0,
        guild_id=12121212121,
        delimiter='~'
    )
    result = await repo.update(server)
    # There is no 0 id, so this should fail
    assert result == False, "UPDATE did not return False when failing."
