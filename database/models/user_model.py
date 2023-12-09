from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class DisplayInformation(BaseModel):
    server_id: Indexed(int)
    name: str
    url: Optional[bool] = True
    private: Optional[bool] = True


class Votes(BaseModel):
    last_voted: Optional[datetime] = Field(default_factory=datetime.utcnow)
    count: Optional[int] = 0


class Scores(BaseModel):
    # TODO: use this data to determine if scores should be updated if there was downtime during a scheduled score update
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)

    start_of_week_total_score: Optional[int]
    start_of_day_total_score: Optional[int]

    day_score: Optional[int] = 0
    week_score: Optional[int] = 0

    yesterday_score: Optional[int] = 0
    last_week_score: Optional[int] = 0

    streak: Optional[int] = 0


class Submissions(BaseModel):
    easy: int
    medium: int
    hard: int
    total_score: Optional[int]


class History(BaseModel):
    timestamp: datetime
    submissions: Submissions
    streak: Optional[int] = 0


class User(Document):
    id: int
    leetcode_username: str
    rank: int
    display_information: List[DisplayInformation]
    submissions: Submissions
    history: Optional[List[History]] = []
    scores: Optional[Scores] = Field(default_factory=Scores)
    votes: Optional[Votes] = Field(default_factory=Votes)

    class Settings:
        name = "users"
        use_state_management = True
