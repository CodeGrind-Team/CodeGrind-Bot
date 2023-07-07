from datetime import datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import BaseModel, Field

from models.user_model import User


class Channel(BaseModel):
    maintenance: Optional[List[int]] = []
    daily_question: Optional[List[int]] = []
    winners: Optional[List[int]] = []


class UserRank(BaseModel):
    user_id: int
    rank: int


class Rankings(BaseModel):
    date: datetime
    timeframe: str  # "daily" or "weekly"
    winner: int  # user id
    rankings_order: List[UserRank]  # leaderboard rankings


class Server(Document):
    id: int
    users: Optional[List[Link[User]]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    timezone: Optional[str] = "UCT"
    channels: Optional[Channel] = Field(default_factory=Channel)
    rankings: Optional[List[Rankings]] = []

    class Settings:
        name = "servers"
        use_state_management = True
