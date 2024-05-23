from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


# TODO add option to silent/non-silent notifications
class Channels(BaseModel):
    maintenance: Optional[List[int]] = []
    daily_question: Optional[List[int]] = []
    winners: Optional[List[int]] = []


class Server(Document):
    id: int
    timezone: Optional[str] = "UTC"
    channels: Optional[Channels] = Field(default_factory=Channels)

    last_update_start: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    last_update_end: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    class Settings:
        name = "servers"
        use_state_management = True
