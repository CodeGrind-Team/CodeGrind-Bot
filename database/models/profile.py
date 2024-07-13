from datetime import UTC, datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field, BaseModel


class Preference(BaseModel):
    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class WinCount(BaseModel):
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class Profile(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    preference: Preference
    win_count: Optional[WinCount] = Field(default_factory=WinCount)

    class Settings:
        name = "profiles"
        use_state_management = True
