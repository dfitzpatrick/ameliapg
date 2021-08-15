from ameliapg.models import WithTimestamp

class MetarSchema(WithTimestamp):
    guild_id: int
    restrict_channel: bool = True
    delete_interval: int = 5


class MetarDB(MetarSchema):
    id: int


class MetarSchemaApi(MetarSchema):
    guild_id: str


class MetarDBApi(MetarSchemaApi):
    id: int


class MetarChannelSchema(WithTimestamp):
    guild_id: int
    channel_id: int


class MetarChannelDB(MetarChannelSchema):
    id: int


class MetarChannelSchemaApi(MetarChannelSchema):
    guild_id: str
    channel_id: str


class MetarChannelDBApi(MetarChannelDB):
    guild_id: str
    channel_id: str


