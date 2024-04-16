from datetime import datetime

from beanie import Document, Link, TimeSeriesConfig

from .user_model import Submissions, User


class Record(Document):
    timestamp: datetime
    user: Link[User]
    submissions: Submissions

    class Settings:
        # ! add caching
        name = "records"
        use_state_management = True
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user",
            bucket_max_span_seconds=86400,
            bucket_rounding_seconds=86400,
        )
