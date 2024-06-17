from datetime import datetime

from beanie import Document, Granularity, TimeSeriesConfig

from .user import Submissions, LanguageProblemCount, SkillProblemCount

from typing import List, Optional


class Record(Document):
    timestamp: datetime
    user_id: int
    submissions: Submissions
    languages_problem_count: Optional[List[LanguageProblemCount]] = []
    skills_problem_count_advanced: Optional[List[SkillProblemCount]] = []
    skills_problem_count_intermediate: Optional[List[SkillProblemCount]] = []
    skills_problem_count_fundamental: Optional[List[SkillProblemCount]] = []

    class Settings:
        name = "records"
        timeseries = TimeSeriesConfig(
            time_field="timestamp",
            meta_field="user_id",
            granularity=Granularity.hours,
        )
