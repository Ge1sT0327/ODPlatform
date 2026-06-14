"""结构化质检报告。"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
from odp_platform.data_validation.registry import CheckResult, CheckSeverity

@dataclass
class ValidationReport:
    dataset_name: str
    task_type: str
    split: str
    total_checks: int
    results: List[CheckResult]
    overall_severity: CheckSeverity
    summary: Dict[str, int] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "dataset_name": self.dataset_name,
            "task_type": self.task_type,
            "split": self.split,
            "total_checks": self.total_checks,
            "overall_severity": self.overall_severity.value,
            "summary": self.summary,
            "error": self.error,
            "results": [
                {
                    "check_name": r.check_name,
                    "severity": r.severity.value,
                    "message": r.message,
                    "passed": r.passed,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
