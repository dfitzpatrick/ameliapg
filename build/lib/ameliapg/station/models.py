from ameliapg.models import WithTimestamp

class StationSchema(WithTimestamp):
    guild_id: int
    restrict_channel: bool = True
    delete_interval: int = 5


class StationDB(StationSchema):
    id: int


class StationSchemaApi(StationSchema):
    guild_id: str


class StationDBApi(StationSchemaApi):
    id: int


class StationChannelSchema(WithTimestamp):
    guild_id: int
    channel_id: int


class StationChannelDB(StationChannelSchema):
    id: int


class StationChannelSchemaApi(StationChannelSchema):
    guild_id: str
    channel_id: str


class StationChannelDBApi(StationChannelDB):
    guild_id: str
    channel_id: str

