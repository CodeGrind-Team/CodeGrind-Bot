from datetime import UTC, datetime
from typing import List

from beanie import Document
from pydantic import BaseModel, Field


class Votes(BaseModel):
    count: int = 0
    last_voted: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Submissions(BaseModel):
    easy: int = 0
    medium: int = 0
    hard: int = 0
    score: int = 0


class Stats(BaseModel):
    submissions: Submissions = Field(default_factory=Submissions)
    streak: int = 0


class LanguageProblemCount(BaseModel):
    language: str
    count: int


class SkillProblemCount(BaseModel):
    skill: str
    count: int


class SkillsProblemCount(BaseModel):
    fundamental: List[SkillProblemCount] = Field(default_factory=list)
    intermediate: List[SkillProblemCount] = Field(default_factory=list)
    advanced: List[SkillProblemCount] = Field(default_factory=list)


class User(Document):
    id: int  # type: ignore
    leetcode_id: str
    stats: Stats = Field(default_factory=Stats)
    votes: Votes = Field(default_factory=Votes)

    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "users"
        use_state_management = True
