import typing as t
from datetime import datetime

from ameliapg.models import Entity


class Server(Entity):
    guild_id: int
    joined: t.Optional[datetime]
    delimiter: str = "!"

