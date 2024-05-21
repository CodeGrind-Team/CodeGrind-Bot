from datetime import datetime

from beanie import Document, TimeSeriesConfig

from .user import Submissions


class Record(Document):
    timestamp: datetime
    user_id: int
    submissions: Submissions

    class Settings:
        # ! add caching
        name = "records"
        use_state_management = True
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user_id",
            bucket_max_span_seconds=86400,
            bucket_rounding_seconds=86400,
        )
