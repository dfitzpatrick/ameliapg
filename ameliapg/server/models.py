import typing as t


from ameliapg.models import Entity


class GuildConfig(Entity):
    guild_id: int
    delimiter: str = "!"
    auto_delete_commands: bool = True


class AutoRole(Entity):
    guild_id: int
    role_id: int

GuildConfig.update_forward_refs()
AutoRole.update_forward_refs()