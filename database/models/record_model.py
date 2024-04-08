from datetime import datetime

from beanie import Document, Indexed, Link

from .user_model import Submissions, User


class Records(Document):
    user_id: Indexed(Link[User])  # type: ignore
    timestamp: Indexed(datetime)  # type: ignore
    submissions: Submissions

    class Settings:
        name = "records"
        use_state_management = True
