from datetime import UTC, datetime
from typing import Optional

from beanie import Document, Indexed, free_fall_migration
from pydantic import BaseModel, Field


class Preference(BaseModel):
    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class WinCount(BaseModel):
    days: Optional[int] = 0
    weeks: Optional[int] = 0
    months: Optional[int] = 0

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))


class Profile(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    preference: Preference
    win_count: Optional[WinCount] = Field(default_factory=WinCount)

    class Settings:
        name = "profiles"
        use_state_management = True


class OldPreference(Document):
    user_id: Indexed(int)  # type: ignore
    server_id: Indexed(int)  # type: ignore

    name: str
    url: Optional[bool] = True
    anonymous: Optional[bool] = True

    last_updated: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "preferences"
        use_state_management = True


class Forward:
    @free_fall_migration(document_models=[OldPreference, Profile])
    async def preference_to_profile(self, session):
        async for old_preference in OldPreference.find_all():
            profile = Profile(
                id=old_preference.id,
                user_id=old_preference.user_id,
                server_id=old_preference.server_id,
                preference=Preference(
                    name=old_preference.name,
                    url=old_preference.url,
                    anonymous=old_preference.anonymous,
                    last_updated=old_preference.last_updated,
                ),
            )
            await profile.create(session=session)
            await old_preference.delete(session=session)


class Backward:
    @free_fall_migration(document_models=[OldPreference, Profile])
    async def profile_to_preference(self, session):
        async for profile in Profile.find_all():
            preference = OldPreference(
                id=profile.id,
                user_id=profile.user_id,
                server_id=profile.server_id,
                name=profile.preference.name,
                url=profile.preference.url,
                anonymous=profile.preference.anonymous,
                last_updated=profile.preference.last_updated,
            )
            await preference.create(session=session)
            await profile.delete(session=session)
