from datetime import datetime
from typing import List, Optional

from pydantic import Field
from beanie import Document, Granularity, TimeSeriesConfig

from .user import LanguageProblemCount, SkillsProblemCount, Submissions


class Record(Document):
    timestamp: datetime
    user_id: int

    submissions: Submissions
    languages_problem_count: Optional[List[LanguageProblemCount]] = Field(
        default_factory=list
    )
    skills_problem_count: Optional[SkillsProblemCount] = Field(
        default_factory=SkillsProblemCount
    )

    class Settings:
        name = "records"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user_id",
            granularity=Granularity.hours,
        )
