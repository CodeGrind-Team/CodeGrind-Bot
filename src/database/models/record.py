from datetime import datetime
from typing import List

from pydantic import Field
from beanie import Document, Granularity, TimeSeriesConfig

from .user import LanguageProblemCount, SkillsProblemCount, Submissions


class Record(Document):
    timestamp: datetime
    user_id: int

    submissions: Submissions
    languages_problem_count: List[LanguageProblemCount] = Field(default_factory=list)
    skills_problem_count: SkillsProblemCount = Field(default_factory=SkillsProblemCount)

    class Settings:
        name = "records"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user_id",
            granularity=Granularity.hours,
        )
