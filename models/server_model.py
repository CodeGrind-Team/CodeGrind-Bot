from datetime import datetime
from typing import List, Optional

from beanie import Document, Link  # type: ignore
from pydantic import BaseModel, Field

from models.user_model import User


class Rankings(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    winner: Optional[Link[User]] = None
    daily: List[Link[User]]
    weekly: List[Link[User]]


class Server(Document):
    id: int
    users: Optional[List[Link[User]]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    timezone: Optional[str] = None
    setup_completed: Optional[bool] = False
    channels: Optional[List[int]] = []
    rankings: Optional[List[Link[Rankings]]] = []
