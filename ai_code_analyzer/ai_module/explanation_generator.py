import ast
from typing import Dict, List


class ExplanationGenerator:
    """Generates simple English explanation from Python code."""

    @staticmethod
    def explain(code: str) -> Dict[str, List[str] | str]:
        tree = ast.parse(code)
        functions = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                summary = f"Function `{node.name}` takes {len(node.args.args)} argument(s) and contains {len(node.body)} main statement(s)."
                if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    doc = str(node.body[0].value.value)
                    summary += f" Docstring summary: {doc[:120]}."
                functions.append(summary)

        if not functions:
            functions.append("No user-defined functions were found; the code mainly runs as a script from top to bottom.")

        overall = "This program is analyzed statically and appears to define logic using Python statements, variables, and optional functions."
        return {"overall": overall, "functions": functions}
