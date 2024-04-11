from datetime import datetime

from beanie import Document, Indexed, Link

from .user_model import Submissions, User


class Record(Document):
    user: Indexed(Link[User])  # type: ignore
    timestamp: Indexed(datetime)  # type: ignore
    period: Indexed(str)  # type: ignore
    submissions: Submissions

    class Settings:
        # ! add caching
        name = "records"
        use_state_management = True
