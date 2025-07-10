import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

import bs4
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

from src.constants import Difficulty
from src.utils.common import convert_to_score

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://leetcode.com",
    "Referer": "https://leetcode.com",
    "Cookie": "csrftoken=; LEETCODE_SESSION=;",
    "x-csrftoken": "",
    "user-agent": "Mozilla/5.0 LeetCode API",
}


@dataclass
class QuestionInfo:
    premium: bool
    question_id: int
    difficulty: str
    title: str
    link: str
    total_accepted: int
    total_submission: int
    ac_rate: float
    question_rating: int | None
    description: str
    example_one: str
    follow_up: str | None


@dataclass
class Submissions:
    easy: int
    medium: int
    hard: int
    score: int


@dataclass
class LanguageProblemCount:
    language: str
    problem_count: int


@dataclass
class SkillProblemCount:
    skill: str
    problem_count: int


@dataclass
class SkillsProblemCount:
    fundamental: list[SkillProblemCount]
    intermediate: list[SkillProblemCount]
    advanced: list[SkillProblemCount]


@dataclass
class UserStats:
    real_name: str
    submissions: Submissions
    languages_problem_count: list[LanguageProblemCount]
    skills_problem_count: SkillsProblemCount


class LeetCodeMarkdownConverter(MarkdownConverter):
    """Custom converter for LeetCode HTML content."""

    def convert(self, html: str) -> str:
        # Remove `&nbsp;`.
        html = html.replace("&nbsp;", " ")

        return super().convert(html)

    def convert_sup(  # type: ignore
        self,
        el: bs4.element.Tag,
        text: str,
        parent_tags: set | None = None,
    ) -> str:
        """Convert superscript `<sup>...</sup>` to `^` notation."""
        return f"^{text}"

    def convert_img(  # type: ignore
        self,
        el: bs4.element.Tag,
        text,
        parent_tags: set | None = None,
    ) -> str:
        """Remove images entirely."""
        return ""

    def convert_style(  # type: ignore
        self,
        el: bs4.element.Tag,
        text: str,
        parent_tags: set | None = None,
    ) -> str:
        """Remove style tags entirely."""
        return ""

    def convert_code(  # type: ignore
        self,
        el: bs4.element.Tag,
        text: str,
        parent_tags: set | None = None,
    ) -> str:
        """Convert code blocks while removing formatting inside them."""
        # Remove any nested formatting tags from code content
        clean_text = self.__clean_code_content(text)
        return f"`{clean_text}`"

    def convert_pre(  # type: ignore
        self,
        el: bs4.element.Tag,
        text: str,
        parent_tags: set | None = None,
    ) -> str:
        """Convert pre blocks while removing formatting inside them."""
        clean_text = self.__clean_code_content(text)
        return f"\n```\n{clean_text}\n```\n"

    def convert_hn(  # type: ignore
        self,
        n: int,
        el: bs4.element.Tag,
        text: str,
        parent_tags: set | None = None,
    ) -> str:
        """Convert headers using ATX style."""
        return f"{'#' * n} {text}\n\n"

    def __clean_code_content(self, text: str) -> str:
        """Remove formatting from code content."""
        soup = BeautifulSoup(text, "html.parser")

        # Remove formatting tags but keep their text content.
        for tag in soup.find_all(["b", "strong", "em", "i", "u"]):
            tag.unwrap()  # type: ignore

        return soup.get_text()


def parse_content(content: str) -> tuple[str, str, str | None]:
    """
    Parses the content of a LeetCode question to extract description, example one, and
    follow-up sections.

    :param content: The HTML content of the question.
    :return: A tuple containing the description, example one, and follow-up sections.
    """
    EXAMPLE_ONE_TAG = '<p><strong class="example">Example 1:</strong></p>'
    P_STRONG_TAG = "<p><strong"
    FOLLOW_UP_TAG = "<strong>Follow up:</strong>"

    converter = LeetCodeMarkdownConverter()

    position_example_one = content.find(EXAMPLE_ONE_TAG)
    # Section 1: Description, Section 2: Example One, Section 3: ...
    position_section_three = content.find(
        P_STRONG_TAG, position_example_one + len(EXAMPLE_ONE_TAG)
    )
    position_follow_up = content.find(FOLLOW_UP_TAG)

    description = converter.convert(content[:position_example_one])
    example_one = converter.convert(
        content[position_example_one + len(EXAMPLE_ONE_TAG) : position_section_three]
    )

    follow_up = None
    if position_follow_up != -1:
        follow_up = converter.convert(
            content[position_follow_up + len(FOLLOW_UP_TAG) :]
        )

    # Ensure the description, example one, and follow-up are within embed
    # description/field size limits.
    EMBED_DESCRIPTION_MAX_LEN = 4096
    EMBED_FIELD_MAX_LEN = 1024

    return (
        description[:EMBED_DESCRIPTION_MAX_LEN],
        example_one[:EMBED_FIELD_MAX_LEN],
        follow_up[:EMBED_FIELD_MAX_LEN] if follow_up else None,
    )


async def fetch_random_question(
    bot: "DiscordBot", difficulty: Difficulty
) -> str | None:
    """
    Fetches a random LeetCode question title slug based on the given difficulty.

    :param difficulty: The difficulty level of the question ("easy", "medium", or "hard"
    ).

    :return: The title slug of a randomly selected question, or None if an error occurs.
    """
    payload = {
        "operationName": "randomQuestion",
        "query": """
        query randomQuestion($categorySlug: String, $filters: QuestionListFilterInput) {
            randomQuestion(categorySlug: $categorySlug, filters: $filters) {
                titleSlug
                isPaidOnly
            }
        }
        """,
        "variables": {
            "categorySlug": "all-code-essentials",
            "filters": (
                {"difficulty": difficulty.name}
                if difficulty != Difficulty.RANDOM
                else {}
            ),
        },
    }

    # Maximum number of attempts to fetch a non-premium question.
    MAX_ATTEMPTS = 10

    # Try to fetch a non-premium question for a maximum of MAX_ATTEMPTS times.
    # This prevents excessive (and even possibly infinite) API calls, ensuring safety.
    for _ in range(MAX_ATTEMPTS):
        response_data = await bot.http_client.post_data(
            URL, json=payload, headers=HEADERS, timeout=10
        )
        if not response_data:
            return

        try:
            question = response_data["data"]["randomQuestion"]

            if not question["isPaidOnly"]:
                return question["titleSlug"]

        except (ValueError, TypeError):
            bot.logger.exception(
                f"fetch_random_question: failed to decode json. Error code "
                f"({response_data})"
            )
            return

    # Log a warning if no non-premium question is found after MAX_ATTEMPTS attempts.
    bot.logger.warning(
        f"fetch_random_question: failed to find an unpaid question after "
        f"{MAX_ATTEMPTS} attempts"
    )
    return


async def fetch_daily_question(bot: "DiscordBot") -> str | None:
    """
    Fetches the title slug of the active daily coding challenge question.

    :return: The title slug of the daily coding challenge question,
             or None if an error occurs.
    """
    data = {
        "operationName": "daily",
        "query": """
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                question {
                    titleSlug
                }
            }
        }
    """,
    }

    response_data = await bot.http_client.post_data(
        URL, json=data, headers=HEADERS, timeout=10
    )
    if not response_data:
        return

    try:
        title_slug = response_data["data"]["challenge"]["question"]["titleSlug"]

    except (ValueError, TypeError):
        bot.logger.exception(
            f"fetch_daily_question: failed to decode json. Error code ({response_data})"
        )
        return

    return title_slug


async def search_question(bot: "DiscordBot", text: str) -> str | None:
    """
    Searches for a LeetCode question title slug based on the provided text.

    :param text: The text to search for in the question titles.

    :return: The title slug of the matched question, or None if no match is found or an
             error occurs.
    """
    payload = {
        "operationName": "problemsetQuestionList",
        "query": """
        query problemsetQuestionList(
            $categorySlug: String,
            $limit: Int,
            $skip: Int,
            $filters: QuestionListFilterInput
        ) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug,
                limit: $limit,
                skip: $skip,
                filters: $filters
            ) {
                questions:
                    data {
                        titleSlug
                    }
                }
            }
        """,
        "variables": {
            "categorySlug": "",
            "skip": 0,
            "limit": 1,
            "filters": {"searchKeywords": text},
        },
    }

    response_data = await bot.http_client.post_data(
        URL, json=payload, headers=HEADERS, timeout=10
    )
    if not response_data:
        return

    try:
        questions_matched_list = response_data["data"]["problemsetQuestionList"]
        if not questions_matched_list or not questions_matched_list["questions"]:
            return

        question_title_slug = questions_matched_list["questions"][0]["titleSlug"]

    except (ValueError, TypeError):
        bot.logger.exception(
            f"search_question: failed to decode json. Error code ({response_data})"
        )
        return

    return question_title_slug


async def fetch_question_info(
    bot: "DiscordBot", question_title_slug: str
) -> QuestionInfo | None:
    """
    Retrieves information about a LeetCode question based on its title slug.

    :param question_title_slug: The title slug of the LeetCode question.

    :return: Information about the LeetCode question, or None if an error occurs or no
             question is found.
    """
    bot.logger.info(f"Fetched question with title: {question_title_slug}")

    payload = {
        "operationName": "questionInfo",
        "query": """
        query questionInfo($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionFrontendId
                title
                difficulty
                content
                likes
                dislikes
                stats
                isPaidOnly
            }
        }
        """,
        "variables": {"titleSlug": question_title_slug},
    }

    response_data = await bot.http_client.post_data(
        URL, json=payload, headers=HEADERS, timeout=10
    )
    if not response_data:
        return

    try:
        question = response_data["data"]["question"]

        question_id = question["questionFrontendId"]
        difficulty = question["difficulty"]
        title = question["title"]
        is_paid_only = question["isPaidOnly"]
        content = question["content"] if not is_paid_only else ""
        link = f"https://leetcode.com/problems/{question_title_slug}"

        stats = ast.literal_eval(question["stats"])
        total_accepted = stats["totalAccepted"]
        total_submission = stats["totalSubmission"]
        ac_rate = stats["acRate"]

    except (ValueError, TypeError):
        bot.logger.exception(
            f"fetch_question_info: failed to decode json. Error code ({response_data})",
        )
        return

    # Get question rating
    question_rating = None
    if not is_paid_only:
        rating = bot.ratings.fetch_rating(title)
        if rating:
            question_rating = int(rating)

    # Parse content for description, example one, and follow up
    description, example_one, follow_up = parse_content(content)

    return QuestionInfo(
        premium=is_paid_only,
        question_id=question_id,
        difficulty=difficulty,
        title=title,
        link=link,
        total_accepted=total_accepted,
        total_submission=total_submission,
        ac_rate=ac_rate,
        question_rating=question_rating,
        description=description,
        example_one=example_one,
        follow_up=follow_up,
    )


async def fetch_problems_solved_and_rank(
    bot: "DiscordBot", leetcode_id: str
) -> UserStats | None:
    """
    Retrieves the statistics of problems solved and rank of a LeetCode user.

    :param leetcode_id: The LeetCode username.

    :return: Statistics of problems solved and rank of the user, or None if an error
    occurs.
    """
    payload = {
        "operationName": "getProblemsSolvedAndRank",
        "query": """query getProblemsSolvedAndRank($username: String!) {
            matchedUser(username: $username) {
                profile {
                    realName
                }
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
                languageProblemCount {
                    languageName
                    problemsSolved
                }
                tagProblemCounts {
                    advanced {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    intermediate {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    fundamental {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                }
            }
        }
        """,
        "variables": {"username": leetcode_id},
    }

    response_data = await bot.http_client.post_data(
        URL, json=payload, headers=HEADERS, timeout=10
    )
    if not response_data:
        return

    try:
        matched_user = response_data["data"]["matchedUser"]

        if not matched_user:
            return None

        real_name = matched_user["profile"]["realName"]
        submit_stats_global = matched_user["submitStatsGlobal"]
        ac_submission_num = submit_stats_global["acSubmissionNum"]
        language_problem_count = matched_user["languageProblemCount"]
        tag_problem_counts = matched_user["tagProblemCounts"]

        language_problem_counts = [
            LanguageProblemCount(
                language=item["languageName"], problem_count=item["problemsSolved"]
            )
            for item in language_problem_count
        ]
        tag_problem_counts_advanced = [
            SkillProblemCount(
                skill=item["tagName"], problem_count=item["problemsSolved"]
            )
            for item in tag_problem_counts["advanced"]
        ]
        tag_problem_counts_intermediate = [
            SkillProblemCount(
                skill=item["tagName"], problem_count=item["problemsSolved"]
            )
            for item in tag_problem_counts["intermediate"]
        ]
        tag_problem_counts_fundamental = [
            SkillProblemCount(
                skill=item["tagName"], problem_count=item["problemsSolved"]
            )
            for item in tag_problem_counts["fundamental"]
        ]

        easy_count = next(
            (
                item["count"]
                for item in ac_submission_num
                if item["difficulty"] == "Easy"
            ),
            0,
        )
        medium_count = next(
            (
                item["count"]
                for item in ac_submission_num
                if item["difficulty"] == "Medium"
            ),
            0,
        )
        hard_count = next(
            (
                item["count"]
                for item in ac_submission_num
                if item["difficulty"] == "Hard"
            ),
            0,
        )

    except (ValueError, TypeError):
        bot.logger.exception(
            f"fetch_problems_solved_and_rank: Failed to decode json for user "
            f"({leetcode_id}): {response_data}",
        )
        return

    return UserStats(
        real_name=real_name,
        submissions=Submissions(
            easy=easy_count,
            medium=medium_count,
            hard=hard_count,
            score=convert_to_score(
                easy=easy_count, medium=medium_count, hard=hard_count
            ),
        ),
        languages_problem_count=language_problem_counts,
        skills_problem_count=SkillsProblemCount(
            fundamental=tag_problem_counts_fundamental,
            intermediate=tag_problem_counts_intermediate,
            advanced=tag_problem_counts_advanced,
        ),
    )
