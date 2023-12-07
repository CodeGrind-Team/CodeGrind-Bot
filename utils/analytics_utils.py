from database.models.analytics_model import Analytics, AnalyticsHistory
from bot_globals import logger


async def save_analytics() -> None:
    logger.info("file: cogs/analytics_utils.py ~ save_analytics ~ run")

    analytics = await Analytics.find_all().to_list()

    if not analytics:
        analytics = Analytics()
        await analytics.create()
    else:
        analytics = analytics[0]

    analytics.history.append(AnalyticsHistory(
        distinct_users=analytics.distinct_users_today, command_count=analytics.command_count_today))

    analytics.distinct_users_today = []
    analytics.command_count_today = 0

    await analytics.save()
