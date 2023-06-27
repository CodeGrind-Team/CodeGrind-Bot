from datetime import datetime
from typing import List, Optional

from beanie import Document, Indexed
from pydantic import BaseModel
# from pymongo import IndexModel


class DisplayInformation(BaseModel):
    server_id: Indexed(int)
    name: str
    hyperlink: Optional[bool] = True


class Scores(BaseModel):
    timezone: str
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
    leetcode_username: str
    rank: int
    display_information: List[DisplayInformation]
    submissions: Submissions
    history: Optional[List[History]] = []
    scores: Optional[List[Scores]] = []

    class Settings:
        name = "users"
