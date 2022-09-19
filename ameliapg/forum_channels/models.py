from ameliapg.models import WithTimestamp
from typing import Optional
from datetime import datetime, timezone

class AutoPinSchema(WithTimestamp):
    guild_id: int
    parent_id: int
    created_at: Optional[datetime] = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = datetime.now(timezone.utc)


class AutoPinDB(AutoPinSchema):
    id: int
