import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List


class SyntaxChecker:
    """Handles syntax and lint-based issue detection."""

    @staticmethod
    def check_syntax(code: str) -> List[Dict[str, Any]]:
        issues = []
        try:
            ast.parse(code)
        except SyntaxError as exc:
            issues.append(
                {
                    "type": "Syntax Error",
                    "line": exc.lineno,
                    "column": exc.offset,
                    "message": exc.msg,
                    "why": "Python could not parse the source code because the statement structure is invalid.",
                    "fix": "Check brackets, colons, indentation, and statement order near the highlighted line.",
                    "severity": "high",
                }
            )
        return issues

    @staticmethod
    def basic_logical_checks(code: str) -> List[Dict[str, Any]]:
        issues = []
        patterns = [
            (r"while\s+True\s*:", "Potential Infinite Loop", "A `while True` loop can run forever if there is no break condition.", "Add a terminating condition or `break` logic inside the loop."),
            (r"if\s+True\s*:", "Redundant Condition", "The condition is always true, which makes branching unnecessary.", "Remove the condition or replace it with a real runtime check."),
            (r"if\s+False\s*:", "Dead Code Pattern", "The block will never execute.", "Remove the block or replace the condition with a valid expression."),
        ]
        for line_no, line in enumerate(code.splitlines(), start=1):
            for pattern, label, why, fix in patterns:
                if re.search(pattern, line):
                    issues.append(
                        {
                            "type": label,
                            "line": line_no,
                            "column": 1,
                            "message": line.strip(),
                            "why": why,
                            "fix": fix,
                            "severity": "medium",
                        }
                    )
        return issues

    @staticmethod
    def run_pylint(code: str) -> List[Dict[str, Any]]:
        issues = []
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "temp_input.py"
            temp_path.write_text(code, encoding="utf-8")
            command = [
                sys.executable,
                "-m",
                "pylint",
                str(temp_path),
                "--output-format=json",
                "--disable=import-error,missing-module-docstring,missing-function-docstring,missing-class-docstring,invalid-name",
            ]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=25)
                if result.stdout.strip():
                    raw = json.loads(result.stdout)
                    for item in raw:
                        issues.append(
                            {
                                "type": item.get("type", "warning").title(),
                                "line": item.get("line"),
                                "column": item.get("column"),
                                "message": item.get("message"),
                                "symbol": item.get("symbol"),
                                "why": "This warning comes from static lint analysis and indicates a quality or maintainability concern.",
                                "fix": f"Review the `{item.get('symbol', 'warning')}` issue and rewrite the related code for clarity or correctness.",
                                "severity": "medium" if item.get("type") != "error" else "high",
                            }
                        )
            except Exception:
                pass
        return issues
