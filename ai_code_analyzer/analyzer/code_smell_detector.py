import ast
from typing import Any, Dict, List

from analyzer.ast_parser import ASTParser


class InfiniteLoopVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.issues = []

    def visit_While(self, node: ast.While) -> None:
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(child, ast.Break) for child in ast.walk(node))
            if not has_break:
                self.issues.append(
                    {
                        "type": "Potential Infinite Loop",
                        "line": node.lineno,
                        "column": 1,
                        "message": "`while True` loop found without a visible `break` statement.",
                        "why": "A loop with no exit path may hang the program or consume system resources indefinitely.",
                        "fix": "Add a break condition, timeout counter, or replace it with a condition-controlled loop.",
                        "severity": "high",
                    }
                )
        self.generic_visit(node)


class CodeSmellDetector:
    """Detects maintainability and structure smells."""

    @staticmethod
    def detect(code: str) -> List[Dict[str, Any]]:
        ast_info = ASTParser.parse_structure(code)
        issues: List[Dict[str, Any]] = []

        for fn in ast_info["function_metrics"]:
            if fn["length"] > 20:
                issues.append(
                    {
                        "type": "Long Function",
                        "line": fn["line"],
                        "column": 1,
                        "message": f"Function `{fn['name']}` has {fn['length']} top-level statements.",
                        "why": "Large functions are harder to test, debug, and understand.",
                        "fix": "Split the function into smaller helper functions with single responsibilities.",
                        "severity": "medium",
                    }
                )
            if fn["nesting_depth"] > 3:
                issues.append(
                    {
                        "type": "Deep Nesting",
                        "line": fn["line"],
                        "column": 1,
                        "message": f"Function `{fn['name']}` has nesting depth {fn['nesting_depth']}.",
                        "why": "Deeply nested code is difficult to read and often hides logic errors.",
                        "fix": "Use guard clauses, early returns, or helper functions to flatten the control flow.",
                        "severity": "medium",
                    }
                )

        tree = ast.parse(code)
        loop_visitor = InfiniteLoopVisitor()
        loop_visitor.visit(tree)
        issues.extend(loop_visitor.issues)
        return issues
