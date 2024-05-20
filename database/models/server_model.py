from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import BaseModel, Field

from .user_model import User


# TODO add option to silent/non-silent notifications
class Channel(BaseModel):
    maintenance: Optional[List[int]] = []
    daily_question: Optional[List[int]] = []
    winners: Optional[List[int]] = []


class Server(Document):
    id: int
    users: Optional[List[Link[User]]] = []
    timezone: Optional[str] = "UTC"
    channels: Optional[Channel] = Field(default_factory=Channel)

    last_update_start: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    last_update_end: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    class Settings:
        name = "servers"
        use_state_management = True
