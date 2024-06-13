from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # To prevent circular imports
    from bot import DiscordBot
from constants import Language

def generate_neetcode_link(bot: "DiscordBot", question_id: str, question_title: str, language: Language):
    language_dict = {
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
    
    question_number = question_id.zfill(4)
    neetcode_github_title = f"{question_number}-{question_title.replace(' ', '-').lower()}"
    neetcode_link = f"https://raw.githubusercontent.com/neetcode-gh/leetcode/main/{language_dict[language]['name']}/{neetcode_github_title}.{language_dict[language]['extension']}"
    return neetcode_link