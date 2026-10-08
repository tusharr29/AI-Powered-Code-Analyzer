from typing import Any, Dict, List


class ScoringEngine:
    """Calculates code quality scores between 0 and 10."""

    @staticmethod
    def calculate(issues: List[Dict[str, Any]], ast_info: Dict[str, Any]) -> Dict[str, float]:
        readability = 9.0
        efficiency = 8.5
        maintainability = 9.0

        severity_penalty = {"low": 0.3, "medium": 0.7, "high": 1.3}
        for issue in issues:
            penalty = severity_penalty.get(issue.get("severity", "low"), 0.3)
            if issue["type"] in {"Long Function", "Deep Nesting", "Unused Variable"}:
                readability -= penalty
                maintainability -= penalty
            elif issue["type"] in {"Potential Infinite Loop", "Syntax Error"}:
                efficiency -= penalty
                maintainability -= penalty
            else:
                readability -= penalty * 0.5
                maintainability -= penalty * 0.6

        function_count = len(ast_info.get("function_metrics", []))
        if function_count == 0:
            maintainability -= 0.5
        if ast_info.get("node_count", 0) > 250:
            readability -= 0.6
            maintainability -= 0.6

        readability = max(0.0, min(10.0, round(readability, 1)))
        efficiency = max(0.0, min(10.0, round(efficiency, 1)))
        maintainability = max(0.0, min(10.0, round(maintainability, 1)))
        overall = round((readability + efficiency + maintainability) / 3, 1)

        return {
            "readability": readability,
            "efficiency": efficiency,
            "maintainability": maintainability,
            "overall": overall,
        }
