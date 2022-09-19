from ameliapg.models import WithTimestamp

class TafSchema(WithTimestamp):
    guild_id: int
    restrict_channel: bool = True
    delete_interval: int = 5


class TafDB(TafSchema):
    id: int


class TafSchemaApi(TafSchema):
    guild_id: str


class TafDBApi(TafSchemaApi):
    id: int


class TafChannelSchema(WithTimestamp):
    guild_id: int
    channel_id: int


class TafChannelDB(TafChannelSchema):
    id: int


class TafChannelSchemaApi(TafChannelSchema):
    guild_id: str
    channel_id: str


class TafChannelDBApi(TafChannelDB):
    guild_id: str
    channel_id: str

