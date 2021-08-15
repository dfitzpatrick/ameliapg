from ameliapg.models import WithTimestamp

class AutoRoleSchema(WithTimestamp):
    guild_id: int
    role_id: int


class AutoRoleDB(AutoRoleSchema):
    id: int


class AutoRoleSchemaApi(AutoRoleSchema):
    guild_id: str
    role_id: str


class AutoRoleDBApi(AutoRoleDB):
    guild_id: str
    role_id: str

