import ast
from collections import Counter
from typing import Any, Dict, List


class VariableUsageVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.assigned = []
        self.used = []

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.assigned.append((node.id, node.lineno))
        elif isinstance(node.ctx, ast.Load):
            self.used.append(node.id)
        self.generic_visit(node)


class FunctionMetricsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.functions = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        length = len(node.body)
        nesting = self._max_nesting(node)
        self.functions.append(
            {
                "name": node.name,
                "line": node.lineno,
                "length": length,
                "nesting_depth": nesting,
                "args": [arg.arg for arg in node.args.args],
            }
        )
        self.generic_visit(node)

    def _max_nesting(self, node: ast.AST, level: int = 0) -> int:
        children = list(ast.iter_child_nodes(node))
        if not children:
            return level
        extra = 1 if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)) else 0
        return max(self._max_nesting(child, level + extra) for child in children)


class ASTParser:
    """Extracts structural insights from Python AST."""

    @staticmethod
    def parse_structure(code: str) -> Dict[str, Any]:
        tree = ast.parse(code)
        var_visitor = VariableUsageVisitor()
        var_visitor.visit(tree)

        fn_visitor = FunctionMetricsVisitor()
        fn_visitor.visit(tree)

        assigned_counter = Counter(name for name, _ in var_visitor.assigned)
        used_counter = Counter(var_visitor.used)
        unused = [
            {"name": name, "line": line}
            for name, line in var_visitor.assigned
            if name not in used_counter and not name.startswith("_")
        ]

        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        return {
            "tree": tree,
            "function_metrics": fn_visitor.functions,
            "unused_variables": unused,
            "imports": imports,
            "classes": classes,
            "node_count": sum(1 for _ in ast.walk(tree)),
            "assigned_counter": dict(assigned_counter),
            "used_counter": dict(used_counter),
        }

    @staticmethod
    def build_issue_list(ast_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        for item in ast_info["unused_variables"]:
            issues.append(
                {
                    "type": "Unused Variable",
                    "line": item["line"],
                    "column": 1,
                    "message": f"Variable `{item['name']}` is assigned but never used.",
                    "why": "Unused variables increase clutter and can confuse future readers about the purpose of the code.",
                    "fix": "Remove the variable or use it meaningfully.",
                    "severity": "low",
                }
            )
        return issues
