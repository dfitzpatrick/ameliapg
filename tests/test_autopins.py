import pytest

@pytest.mark.asyncio
async def test_create_auto_pin(ameliapg):
    async with ameliapg as service:
        o = await service.forum_channels.create_auto_pin(1234,5678)
        assert o.id == 1
        assert o.guild_id == 1234
