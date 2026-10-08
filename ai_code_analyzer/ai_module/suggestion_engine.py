import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()


def _fallback_suggestions(code: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    practices = [
        "Use meaningful variable and function names.",
        "Prefer smaller functions with one clear responsibility.",
        "Add input validation for edge cases and invalid values.",
    ]
    if any(issue["type"] == "Unused Variable" for issue in issues):
        practices.append("Remove unused variables to reduce noise.")
    if any(issue["type"] == "Deep Nesting" for issue in issues):
        practices.append("Reduce nesting using early returns or helper methods.")
    if "for" in code and "range(len(" in code:
        practices.append("Consider iterating directly over items instead of using `range(len(...))` when possible.")

    improved = code.rstrip()
    improved += "\n"

    return {
        "best_practices": practices,
        "readability": [
            "Keep line lengths manageable and group related logic together.",
            "Add docstrings for functions that perform non-trivial tasks.",
        ],
        "optimization": [
            "Avoid unnecessary repeated work inside loops.",
            "Cache reusable intermediate results when appropriate.",
        ],
        "fixed_code": improved,
        "source": "fallback",
    }


def generate_ai_suggestions(code: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not api_key:
        return _fallback_suggestions(code, issues)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""
You are a code review assistant.
Analyze this Python code and return strict JSON with keys:
best_practices, readability, optimization, fixed_code.
Each key except fixed_code should be a list of concise strings.
Keep fixed_code runnable and safe.
Issues: {json.dumps(issues)}
Code:\n{code}
"""
        response = client.responses.create(
            model=model,
            input=prompt,
            temperature=0.2,
        )
        text = response.output_text
        data = json.loads(text)
        data["source"] = "openai"
        return data
    except Exception:
        return _fallback_suggestions(code, issues)
