from datetime import UTC, datetime
from typing import Optional

from beanie import Document, Indexed
from pydantic import Field


class Preference(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "preferences"
        use_state_management = True
