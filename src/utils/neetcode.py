import json
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.constants import Language

if TYPE_CHECKING:
    # To prevent circular imports
    from src.bot import DiscordBot


@dataclass
class NeetcodeSolution:
    problem_id: int
    title: str
    name: str
    pattern: str
    difficulty: str
    video: str
    code: str
    blind75: bool = False
    neetcode150: bool = False
    neetcode250: bool = False


class NeetcodeSolutions:
    def __init__(self, bot: "DiscordBot") -> None:
        self.bot = bot
        # {link/question-title-slug: NeetcodeSolution}
        self.solutions: dict[str, NeetcodeSolution] = {}

    async def update_solutions(self) -> None:
        """
        Updates the solutions.
        """
        self.solutions = await self._fetch_neetcode_solutions()
        self.bot.logger.info("Updated NeetCode solutions")

    async def _fetch_neetcode_solutions(self) -> dict[str, NeetcodeSolution]:
        """
        Fetches the NeetCode solutions data.

        :return: The dictionary mapping from link/question-title-slug to
        `NeetcodeSolution`.
        """
        main_js_filename = await self._retrieve_neetcode_main_js_filename()

        if not (
            response_data := await self.bot.http_client.fetch_data(
                f"https://neetcode.io/{main_js_filename}", timeout=10
            )
        ):
            return {}

        solutions = self._parse_main_js(response_data)
        return solutions

    async def _retrieve_neetcode_main_js_filename(self) -> str | None:
        """
        Fetches https://neetcode.io/ and retrieves the filename of the
        main.[a-z0-9]{16}.js file.

        :return: The full name of the main.[a-z0-9]{16}.js file.
        """
        if not (
            response_data := await self.bot.http_client.fetch_data(
                "https://neetcode.io/", timeout=10
            )
        ):
            return

        filename = re.search(r"main\.[a-z0-9]{16}\.js", response_data)
        if not filename:
            return

        # Return the entire match.
        return filename.group(0)

    def _parse_main_js(self, main_js: str) -> dict[str, NeetcodeSolution]:
        """
        Parses the main.js file and finds the array of objects containing the solution
        data.

        :param main_js: The main_js file as a string.

        :return: The dictionary mapping from link/question-title-slug to
        `NeetcodeSolution`.
        """
        solutions_full = re.search(r"M=(\[\{.*?\}\])", main_js)
        if not solutions_full:
            return {}

        solutions = solutions_full.group(1)
        solutions = solutions.replace("!0", "true")
        solutions = re.sub(r"([{,])(\w+):", r'\1"\2":', solutions)
        solutions_objects: list[dict] = json.loads(solutions)

        link_to_solution: dict[str, NeetcodeSolution] = {}
        for solution in solutions_objects:
            try:
                title = solution["link"].strip("/")
                link_to_solution[title] = NeetcodeSolution(
                    problem_id=int(solution["code"].split("-")[0]),
                    title=title,
                    name=solution["problem"],
                    pattern=solution["pattern"],
                    difficulty=solution["difficulty"],
                    video=solution["video"],
                    code=solution["code"],
                    blind75=True if "blind75" in solution else False,
                    neetcode150=True if "neetcode150" in solution else False,
                    neetcode250=True if "neetcode250" in solution else False,
                )
            except ValueError as e:
                self.bot.logger.exception(
                    f"Error parsing a NeetCode solution ({solution}): {e}"
                )

        return link_to_solution


def neetcode_solution_github_link(github_code_filename: str, language: Language) -> str:
    """
    Generates the NeetCode GitHub solution code url.

    :param github_code_filename: The filename of the code solution.
    :param language: The selected programming language of the solution.

    :return: The GitHub NeetCode solution link of the LC problem.
    """
    language_to_github = {
        Language.PYTHON3: {"name": "python", "extension": "py"},
        Language.JAVA: {"name": "java", "extension": "java"},
        Language.CPP: {"name": "cpp", "extension": "cpp"},
        Language.C: {"name": "c", "extension": "c"},
        Language.CSHARP: {"name": "csharp", "extension": "cs"},
        Language.JAVASCRIPT: {"name": "javascript", "extension": "js"},
        Language.GO: {"name": "go", "extension": "go"},
        Language.KOTLIN: {"name": "kotlin", "extension": "kt"},
        Language.RUBY: {"name": "ruby", "extension": "rb"},
        Language.SWIFT: {"name": "swift", "extension": "swift"},
        Language.RUST: {"name": "rust", "extension": "rs"},
        Language.SCALA: {"name": "scala", "extension": "scala"},
        Language.TYPESCRIPT: {"name": "typescript", "extension": "ts"},
        Language.DART: {"name": "dart", "extension": "dart"},
    }

    link = (
        f"https://raw.githubusercontent.com/neetcode-gh/leetcode/main/"
        f"{language_to_github[language]['name']}/{github_code_filename}."
        f"{language_to_github[language]['extension']}"
    )
    return link
