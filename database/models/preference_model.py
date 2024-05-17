from datetime import datetime
from typing import Optional

from beanie import Document, Indexed


class Preference(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True

    last_updated: Optional[datetime]

    class Settings:
        name = "preferences"
        use_state_management = True
