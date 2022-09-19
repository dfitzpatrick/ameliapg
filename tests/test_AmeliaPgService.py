from ameliapg.AmeliaPgService import AmeliaPgService
import pytest

@pytest.mark.asyncio
async def test_amelia_listen(dsn):
    async def foo(payload):
        print(payload)

    amelia = await AmeliaPgService.from_dsn(dsn)
    await amelia.start_listening()

    amelia.register_listener(foo)
    await amelia.new_guild_config(123456985454)
    await amelia.end()

