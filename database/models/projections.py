from pydantic import BaseModel, Field

from database.models.user_model import Submissions


class IdProjection(BaseModel):
    id: int = Field(alias='_id')


class SubmissionsProjection(BaseModel):
    submissions: Submissions


class LeetCodeUsernameProjection(BaseModel):
    leetcode_username: str
