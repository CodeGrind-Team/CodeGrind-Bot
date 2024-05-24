from datetime import datetime

from beanie import Document, Granularity, TimeSeriesConfig

from .user import Submissions


class Record(Document):
    timestamp: datetime
    user_id: int
    submissions: Submissions

    class Settings:
        name = "records"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user_id",
            granularity=Granularity.hours,
        )
