import asyncio
from random import random
from typing import TYPE_CHECKING

import aiohttp
import backoff

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot

http_post_semaphore = asyncio.Semaphore(4)


class RateLimitExceededException(Exception):
    def __init__(self) -> None:
        super().__init__("RateLimitExceededException. Error: 429. Rate Limited.")


class HttpClient:
    def __init__(self, bot: "DiscordBot", session: aiohttp.ClientSession) -> None:
        self.bot = bot
        self.session = session

    async def fetch_data(self, *args, **kwargs) -> str | None:
        """
        Executes a GET request and handles any client errors.

        :return: The response text if the request is successful, otherwise None.
        """
        try:
            async with self.session.get(*args, **kwargs) as response:
                match response.status:
                    case 200:
                        return await response.text()
                    case _:
                        self.bot.logger.error(
                            f"GET request failed | Status code: {response.status} | "
                            f"URL: {response.url}"
                        )

        except (aiohttp.ClientError, asyncio.TimeoutError):
            self.bot.logger.exception(
                "GET request failed | "
                "ClientError or TimeoutError occurred while fetching data"
            )

    @backoff.on_exception(backoff.expo, RateLimitExceededException, logger=None)
    async def post_data(self, *args, **kwargs) -> dict | None:
        """
        Executes a POST request with rate limit handling and error logging.

        :return: The response JSON if the request is successful, otherwise None.
        """
        async with http_post_semaphore:
            try:
                async with self.session.post(*args, **kwargs) as response:
                    match response.status:
                        case 200:
                            # Add a small delay to avoid rate limits, using random to
                            # avoid patterns.
                            # TODO: Look into whether this is necessary:
                            # increases overall execution time but decreases the
                            # number of rate limited requests.
                            await asyncio.sleep(random())
                            return await response.json()
                        case 429:
                            self.bot.channel_logger.rate_limited()
                            raise RateLimitExceededException()
                        case 403:
                            self.bot.logger.error(
                                f"POST request forbidden | "
                                f"Status code: {response.status} | "
                                f"URL: {response.url}"
                            )
                            self.bot.channel_logger.forbidden()
                        case _:
                            self.bot.logger.error(
                                f"POST request failed | "
                                f"Status code: {response.status} | URL: {response.url}"
                            )

            except (aiohttp.ClientError, asyncio.TimeoutError):
                self.bot.logger.exception(
                    "Failed to POST data | ClientError or TimeoutError occurred"
                )
