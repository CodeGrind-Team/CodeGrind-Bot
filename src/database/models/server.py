from datetime import UTC, datetime
from typing import List

from beanie import Document
from pydantic import BaseModel, Field


class Channels(BaseModel):
    maintenance: List[int] = Field(default_factory=list)
    daily_question: List[int] = Field(default_factory=list)
    winners: List[int] = Field(default_factory=list)


class Server(Document):
    id: int  # type: ignore
    timezone: str = "UTC"
    channels: Channels = Field(default_factory=Channels)

    last_update_start: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_update_end: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "servers"
        use_state_management = True
