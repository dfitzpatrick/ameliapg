from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

from pydantic import BaseModel

from datetime import datetime

class WithTimestamp(BaseModel):
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()





class PgNotify(BaseModel):
    table: str
    action: str
    entity: Any



