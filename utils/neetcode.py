from constants import Language


def generate_neetcode_link(question_id: str, question_title: str, language: Language):
    """
    Generates the NeetCode GitHub code url.

    :param question_id: The ID of the selected LeetCode problem.
    :param question_title: The title of the selected LeetCode problem.
    :param language: The selected programming language of the solution.
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

    question_number = question_id.zfill(4)
    neetcode_github_title = (
        f"{question_number}-{question_title.replace(' ', '-').lower()}"
    )
    neetcode_link = (
        f"https://raw.githubusercontent.com/neetcode-gh/leetcode/main/"
        f"{language_to_github[language]['name']}/{neetcode_github_title}."
        f"{language_to_github[language]['extension']}"
    )
    return neetcode_link
