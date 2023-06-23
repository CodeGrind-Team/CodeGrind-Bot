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


class User(Document):
    id: int
    display_username: str
    leetcode_username: str
    hyperlink: Optional[bool] = True
    rank: int
    submissions: Submissions
    history: History
    scores: Optional[List[Scores]] = []
