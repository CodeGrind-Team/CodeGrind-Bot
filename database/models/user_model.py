from datetime import UTC, datetime
from typing import List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class DisplayInformation(BaseModel):
    server_id: Indexed(int)  # type: ignore
    name: str
    url: Optional[bool] = True
    visible: Optional[bool] = False
    last_updated: Optional[datetime]


class Votes(BaseModel):
    last_voted: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC))
    count: Optional[int] = 0


class Submissions(BaseModel):
    easy: Optional[int] = 0
    medium: Optional[int] = 0
    hard: Optional[int] = 0


class Stats(BaseModel):
    submissions: Optional[Submissions] = Field(default_factory=Submissions)
    streak: Optional[int] = 0
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(UTC))


class User(Document):
    id: int
    leetcode_username: str
    display_information: List[DisplayInformation]
    scores: Optional[Stats] = Field(default_factory=Stats)
    votes: Optional[Votes] = Field(default_factory=Votes)

    class Settings:
        name = "users"
        use_state_management = True
