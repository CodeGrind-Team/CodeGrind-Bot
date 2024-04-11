from datetime import datetime
from typing import Optional

from beanie import Document, Indexed, Link

from .server_model import Server
from .user_model import User


class Preference(Document):
    user: Indexed(Link[User])  # type: ignore
    server: Indexed(Link[Server])  # type: ignore

    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True
    last_updated: Optional[datetime]

    class Settings:
        name = "preferences"
        use_state_management = True
