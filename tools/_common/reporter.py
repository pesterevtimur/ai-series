# tools/_common/reporter.py
"""JSON report format for lint scripts."""
from dataclasses import dataclass, field
from enum import Enum
import json


class IssueLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Issue:
    level: IssueLevel
    path: str
    message: str
    context: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.level, IssueLevel):
            self.level = IssueLevel(self.level)

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "path": str(self.path),
            "message": self.message,
            "context": self.context,
        }


@dataclass
class Reporter:
    script: str
    issues: list[Issue] = field(default_factory=list)
    diversity_warnings: list[Issue] = field(default_factory=list)

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)

    def add_diversity_warning(self, issue: Issue) -> None:
        self.diversity_warnings.append(issue)

    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == IssueLevel.ERROR]

    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == IssueLevel.WARNING]

    def exit_code(self) -> int:
        return 1 if self.errors() else 0

    def to_json(self) -> str:
        return json.dumps({
            "script": self.script,
            "status": "fail" if self.errors() else "pass",
            "issues": [i.to_dict() for i in self.errors()],
            "warnings": [i.to_dict() for i in self.warnings()],
            "diversity_warnings": [i.to_dict() for i in self.diversity_warnings],
        }, ensure_ascii=False, indent=2)
