from ameliapg.models import WithTimestamp


class GuildSchema(WithTimestamp):
    guild_id: int
    delimiter: str = "!"
    auto_delete_commands: bool = True


class GuildDB(GuildSchema):
    id: int


class GuildSchemaApi(GuildSchema):
    guild_id: str


class GuildDBApi(GuildSchemaApi):
    id: int

