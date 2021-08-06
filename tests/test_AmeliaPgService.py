from ameliapg.AmeliaPgService import AmeliaPgService
from ameliapg.server.models import Server
import pytest

@pytest.mark.asyncio
async def test_amelia_listen(dsn):
    async def foo(payload):
        print(payload)

    amelia = await AmeliaPgService.from_dsn(dsn)
    await amelia.start_listening()

    server = Server(
        guild_id=1234,
        delimiter="/",
    )
    amelia.register_listener(foo)
    await amelia.record_server_join(server)
    await amelia.end()

