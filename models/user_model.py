from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel


class Scores(BaseModel):
    timestamp: datetime
    today_score: Optional[int] = 0
    week_score: Optional[int] = 0
    yesterday_score: Optional[int] = 0
    last_week_score: Optional[int] = 0


class Submissions(BaseModel):
    easy: int
    medium: int
    hard: int
    total_score: int


class History(BaseModel):
    timestamp: datetime
    submissions: Submissions


class DisplayInformation(BaseModel):
    server_id: int
    display_username: str
    hyperlink: Optional[bool] = True


class User(Document):
    id: int
    leetcode_username: str
    rank: int
    display_information: List[DisplayInformation]
    submissions: Submissions
    history: Optional[List[History]] = []
    scores: Optional[List[Scores]] = []
