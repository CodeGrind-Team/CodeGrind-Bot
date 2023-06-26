from pydantic import BaseModel, Field


class IdProjection(BaseModel):
    id: int = Field(alias='_id')


class LeetCodeUsernameProjection(BaseModel):
    leetcode_username: str
