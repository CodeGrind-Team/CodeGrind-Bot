from datetime import datetime

from beanie import Document, Link, TimeSeriesConfig
from pydantic import Field, BaseModel

from .user_model import Submissions, User


class MetaRecord(BaseModel):
    user: Link[User]
    period: str


class Record(Document):
    timestamp: datetime = Field(default_factory=datetime.now)
    meta: MetaRecord
    submissions: Submissions

    class Settings:
        # ! add caching
        name = "records"
        use_state_management = True
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="meta",
            bucket_max_span_seconds=86400,
            bucket_rounding_seconds=86400,
        )
