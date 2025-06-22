from datetime import UTC, datetime

from beanie import Document, Indexed
from pydantic import Field, BaseModel


class Preference(BaseModel):
    name: str
    url: bool = True
    anonymous: bool = True

    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WinCount(BaseModel):
    days: int = 0
    weeks: int = 0
    months: int = 0

    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Profile(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    preference: Preference
    win_count: WinCount = Field(default_factory=WinCount)

    class Settings:
        name = "profiles"
        use_state_management = True
