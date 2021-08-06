import typing as t

from pydantic import BaseModel



class Entity(BaseModel):
    id: t.Optional[int]


class PgNotify(BaseModel):
    table: str
    action: str
    entity: Entity


