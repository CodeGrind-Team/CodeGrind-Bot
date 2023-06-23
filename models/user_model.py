from datetime import datetime
from typing import List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Scores(BaseModel):
    timestamp: datetime
    today_score: int
    week_score: int
    yesterday_score: int
    last_week_score: int


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
    hyperlink: bool
    rank: int
    submissions: Submissions
    history: History
    scores: Optional[List[Scores]] = []
