from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

from datetime import datetime

class PgModel(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()



class Entity(PgModel):
    """
    Serial-based PKs for our internal models.
    """
    id: Optional[int]



class PgNotify(BaseModel):
    table: str
    action: str
    entity: Entity



