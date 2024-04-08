from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class AnalyticsHistory(BaseModel):
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))
    distinct_users: Optional[List[int]] = []
    command_count: int


class Analytics(Document):
    distinct_users_total: Optional[List[int]] = []
    distinct_users_today: Optional[List[int]] = []
    command_count_today: int = 0
    history: Optional[List[AnalyticsHistory]] = []

    class Settings:
        name = "analytics"
        use_state_management = True
