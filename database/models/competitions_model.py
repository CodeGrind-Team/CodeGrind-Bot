from datetime import datetime
from typing import List, Optional

from beanie import Document, Link
from pydantic import Field

from .user_model import User


class Competition(Document):
    id: int
    users: Optional[List[Link[User]]] = []
    last_updated: Optional[datetime] = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "competitions"
        use_state_management = True
