import pytest
from ameliapg.server import ServerRepository
from ameliapg.server.models import AutoRole, GuildConfig

@pytest.mark.asyncio
async def test_find_auto_role(server_fixture):
    repo = ServerRepository(server_fixture)
    entities = await repo.find_auto_roles_by('guild_id', 123456789)
    assert len(entities) == 3
    for entity in entities:
        assert entity.guild_id == 123456789

@pytest.mark.asyncio
async def test_create_auto_role(server_fixture):
    repo = ServerRepository(server_fixture)
    role = AutoRole(
        guild_id=123456789,
        role_id=1234567
    )
    role = await repo.create_auto_role(role)
    assert role.id is not None, "No returning id from creation"
    assert role.guild_id == 123456789, "Did not create guild_id correctly"
    assert role.role_id == 1234567, "Did not create role_id correctly"


@pytest.mark.asyncio
async def test_remove_auto_role(server_fixture):
    repo = ServerRepository(server_fixture)
    role = AutoRole(guild_id=123456789, role_id=12345)
    result = await repo.remove_auto_role(role.id)
    assert result == True, "No objects were deleted"
