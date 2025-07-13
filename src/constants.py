from dataclasses import dataclass
from enum import Enum

import discord


class LeaderboardSortBy(Enum):
    SCORE = "score"
    WIN_COUNT = "win_count"


class Period(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALLTIME = "alltime"


class DifficultyScore(Enum):
    EASY = 1
    MEDIUM = 3
    HARD = 7


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    RANDOM = 4


class RankEmoji(Enum):
    FIRST = "🥇"
    SECOND = "🥈"
    THIRD = "🥉"


class Language(Enum):
    PYTHON3 = "python"
    JAVA = "java"
    CPP = "c++"
    C = "c"
    CSHARP = "c#"
    JAVASCRIPT = "javascript"
    GO = "go"
    KOTLIN = "kotlin"
    RUBY = "ruby"
    SWIFT = "swift"
    RUST = "rust"
    SCALA = "scala"
    TYPESCRIPT = "typescript"
    DART = "dart"


class ProblemList(Enum):
    LEETCODE_ALL = "leetcode_all"
    GRIND_75 = "grind_75"
    BLIND_75 = "blind_75"
    NEETCODE_150 = "neetcode_150"
    NEETCODE_250 = "neetcode_250"
    NEETCODE_ALL = "neetcode_all"


class StatsCardExtensions(Enum):
    ACTIVITY = "activity"
    HEATMAP = "heatmap"
    CONTEST = "contest"
    NONE = "none"


class NotificationOptions(Enum):
    MAINTENANCE = "maintenance"
    DAILY_QUESTION = "daily_question"
    WINNERS = "winners"


class CodeGrindMilestone(Enum):
    NOVICE = "Novice"
    APPRENTICE = "Apprentice"
    CAPABLE = "Capable"
    COMPETENT = "Competent"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    MASTER = "Master"
    LEGEND = "Legend"


class CodeGrindStreak(Enum):
    INITIATE = "Streak Initiate"
    PURSUER = "Streak Pursuer"
    ADVENTURER = "Streak Adventurer"
    DOMINATOR = "Streak Dominator"
    LEGEND = "Streak Legend"


@dataclass
class CodeGrindTierInfo:
    threshold: int
    title: str
    role_name: str
    role_colour: discord.Colour
    icon_path: str | None = None


GLOBAL_LEADERBOARD_ID = 0

# Threshold is in points.
MILESTONE_ROLES = {
    CodeGrindMilestone.NOVICE: CodeGrindTierInfo(
        threshold=1,
        title="Novice",
        role_name="Novice (1 pt)",
        role_colour=discord.Colour.dark_grey(),
        icon_path="src/ui/assets/milestones/novice.png",
    ),
    CodeGrindMilestone.APPRENTICE: CodeGrindTierInfo(
        threshold=100,
        title="Apprentice",
        role_name="Apprentice (100 pts)",
        role_colour=discord.Colour.green(),
        icon_path="src/ui/assets/milestones/apprentice.png",
    ),
    CodeGrindMilestone.CAPABLE: CodeGrindTierInfo(
        threshold=300,
        title="Capable",
        role_name="Capable (300 pts)",
        role_colour=discord.Colour.blue(),
        icon_path="src/ui/assets/milestones/capable.png",
    ),
    CodeGrindMilestone.COMPETENT: CodeGrindTierInfo(
        threshold=500,
        title="Competent",
        role_name="Competent (500 pts)",
        role_colour=discord.Colour.dark_blue(),
        icon_path="src/ui/assets/milestones/competent.png",
    ),
    CodeGrindMilestone.ADVANCED: CodeGrindTierInfo(
        threshold=1000,
        title="Advanced",
        role_name="Advanced (1000 pts)",
        role_colour=discord.Colour.orange(),
        icon_path="src/ui/assets/milestones/advanced.png",
    ),
    CodeGrindMilestone.EXPERT: CodeGrindTierInfo(
        threshold=2000,
        title="Expert",
        role_name="Expert (2000 pts)",
        role_colour=discord.Colour.red(),
        icon_path="src/ui/assets/milestones/expert.png",
    ),
    CodeGrindMilestone.MASTER: CodeGrindTierInfo(
        threshold=4000,
        title="Master",
        role_name="Master (4000 pts)",
        role_colour=discord.Colour.purple(),
        icon_path="src/ui/assets/milestones/master.png",
    ),
    CodeGrindMilestone.LEGEND: CodeGrindTierInfo(
        threshold=6000,
        title="Legend",
        role_name="Legend (6000 pts)",
        role_colour=discord.Colour.gold(),
        icon_path="src/ui/assets/milestones/legend.png",
    ),
}

# Threshold is in days.
STREAK_ROLES = {
    CodeGrindStreak.INITIATE: CodeGrindTierInfo(
        threshold=3,
        title="Streak Initiate",
        role_name="Streak Initiate (3 Days)",
        role_colour=discord.Colour.green(),
    ),
    CodeGrindStreak.PURSUER: CodeGrindTierInfo(
        threshold=7,
        title="Streak Pursuer",
        role_name="Streak Pursuer (7 Days)",
        role_colour=discord.Colour.blue(),
    ),
    CodeGrindStreak.ADVENTURER: CodeGrindTierInfo(
        threshold=14,
        title="Streak Advent",
        role_name="Streak Adventurer (14 Days)",
        role_colour=discord.Colour.red(),
    ),
    CodeGrindStreak.DOMINATOR: CodeGrindTierInfo(
        threshold=30,
        title="Streak Dominator",
        role_name="Streak Dominator (30 Days)",
        role_colour=discord.Colour.purple(),
    ),
    CodeGrindStreak.LEGEND: CodeGrindTierInfo(
        threshold=90,
        title="Streak Legend",
        role_name="Streak Legend (90 Days)",
        role_colour=discord.Colour.gold(),
    ),
}

VERIFIED_ROLE = "CodeGrind Verified"

GRIND_75_QUESTION_TITLES = {
    "two-sum",
    "longest-substring-without-repeating-characters",
    "longest-palindromic-substring",
    "clone-graph",
    "ransom-note",
    "string-to-integer-atoi",
    "container-with-most-water",
    "word-break",
    "linked-list-cycle",
    "middle-of-the-linked-list",
    "3sum",
    "rotting-oranges",
    "letter-combinations-of-a-phone-number",
    "lru-cache",
    "valid-parentheses",
    "merge-two-sorted-lists",
    "evaluate-reverse-polish-notation",
    "merge-k-sorted-lists",
    "first-bad-version",
    "longest-palindrome",
    "binary-search",
    "min-stack",
    "time-based-key-value-store",
    "01-matrix",
    "diameter-of-binary-tree",
    "partition-equal-subset-sum",
    "search-in-rotated-sorted-array",
    "combination-sum",
    "find-median-from-data-stream",
    "majority-element",
    "trapping-rain-water",
    "serialize-and-deserialize-binary-tree",
    "permutations",
    "maximum-subarray",
    "spiral-matrix",
    "minimum-height-trees",
    "merge-intervals",
    "insert-interval",
    "find-all-anagrams-in-a-string",
    "unique-paths",
    "coin-change",
    "add-binary",
    "climbing-stairs",
    "binary-tree-right-side-view",
    "number-of-islands",
    "maximum-profit-in-job-scheduling",
    "sort-colors",
    "minimum-window-substring",
    "subsets",
    "word-search",
    "reverse-linked-list",
    "course-schedule",
    "implement-trie-prefix-tree",
    "accounts-merge",
    "largest-rectangle-in-histogram",
    "contains-duplicate",
    "flood-fill",
    "basic-calculator",
    "validate-binary-search-tree",
    "invert-binary-tree",
    "binary-tree-level-order-traversal",
    "kth-smallest-element-in-a-bst",
    "maximum-depth-of-binary-tree",
    "construct-binary-tree-from-preorder-and-inorder-traversal",
    "implement-queue-using-stacks",
    "lowest-common-ancestor-of-a-binary-search-tree",
    "lowest-common-ancestor-of-a-binary-tree",
    "task-scheduler",
    "balanced-binary-tree",
    "product-of-array-except-self",
    "valid-anagram",
    "k-closest-points-to-origin",
    "best-time-to-buy-and-sell-stock",
    "valid-palindrome",
    "word-ladder",
)
