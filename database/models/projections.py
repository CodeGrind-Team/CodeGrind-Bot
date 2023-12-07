from pydantic import BaseModel, Field

from .user_model import Submissions


class IdProjection(BaseModel):
    id: int = Field(alias='_id')


class SubmissionsProjection(BaseModel):
    submissions: Submissions


class LeetCodeUsernameProjection(BaseModel):
    leetcode_username: str
