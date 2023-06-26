from datetime import datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import BaseModel, Field

from models.user_model import User


class Channel(BaseModel):
    maintenance: Optional[List[int]] = []
    daily_question: Optional[List[int]] = []
    winners: Optional[List[int]] = []


class Rankings(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    winner: Optional[Link[User]] = None
    daily: List[Link[User]]
    weekly: List[Link[User]]


class Server(Document):
    id: int
    users: Optional[List[Link[User]]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    timezone: Optional[str] = "UCT"
    setup_completed: Optional[bool] = False
    channels: Optional[Channel] = Field(default_factory=Channel)
    rankings: Optional[List[Rankings]] = []
