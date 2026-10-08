import textwrap
from pathlib import Path

import streamlit as st

from analyzer.ast_parser import ASTParser
from analyzer.code_smell_detector import CodeSmellDetector
from analyzer.syntax_checker import SyntaxChecker
from ai_module.explanation_generator import ExplanationGenerator
from ai_module.suggestion_engine import generate_ai_suggestions
from plagiarism.similarity_checker import SimilarityChecker
from utils.diff_viewer import DiffViewer
from utils.scoring import ScoringEngine

try:
    from code_editor import code_editor
    HAS_EDITOR = True
except Exception:
    HAS_EDITOR = False


st.set_page_config(page_title="AI Code Analyzer", page_icon="🤖", layout="wide")

SAMPLE_CODE = Path("samples/buggy_sample.py").read_text(encoding="utf-8") if Path("samples/buggy_sample.py").exists() else "print('Hello')\n"


def load_input_code() -> str:
    st.sidebar.header("Input Options")
    uploaded_file = st.sidebar.file_uploader("Upload Python file", type=["py", "txt"], max_upload_size=20)
    use_sample = st.sidebar.button("Load Sample Code")

    if use_sample:
        st.session_state["current_code"] = SAMPLE_CODE

    if uploaded_file is not None:
        st.session_state["current_code"] = uploaded_file.getvalue().decode("utf-8", errors="ignore")

    initial_code = st.session_state.get("current_code", SAMPLE_CODE)

    if HAS_EDITOR:
        response = code_editor(initial_code, lang="python", height=[18, 24], options={"wrap": True})
        if isinstance(response, dict) and response.get("text"):
            return response["text"]
        return initial_code

    return st.text_area("Paste Python code", value=initial_code, height=420)


st.title("AI-Powered Code Analyzer")
st.caption("AST, linting, AI suggestions, auto-fix, and plagiarism similarity.")

with st.expander("Phase-wise implementation plan", expanded=False):
    st.markdown(
        textwrap.dedent(
            """
            1. **Phase 1:** Basic analyzer using AST and pylint.
            2. **Phase 2:** AI-based suggestions and explanation.
            3. **Phase 3:** Safe auto-fix and diff view.
            4. **Phase 4:** Plagiarism detection with token, AST, and TF-IDF similarity.
            5. **Phase 5:** Full Streamlit integration.
            """
        )
    )

code = load_input_code()
analyze = st.button("Analyze Code", type="primary", use_container_width=True)

if analyze:
    if not code.strip():
        st.warning("Please enter or upload some Python code.")
        st.stop()

    syntax_issues = SyntaxChecker.check_syntax(code)
    if syntax_issues:
        ast_info = {"function_metrics": [], "node_count": 0}
    else:
        ast_info = ASTParser.parse_structure(code)

    ast_issues = [] if syntax_issues else ASTParser.build_issue_list(ast_info)
    smell_issues = [] if syntax_issues else CodeSmellDetector.detect(code)
    lint_issues = SyntaxChecker.run_pylint(code)
    logic_issues = SyntaxChecker.basic_logical_checks(code)

    all_issues = syntax_issues + ast_issues + smell_issues + lint_issues + logic_issues
    ai_result = generate_ai_suggestions(code, all_issues)
    fixed_code = ai_result.get("fixed_code", code)
    explanation = ExplanationGenerator.explain(code) if not syntax_issues else {"overall": "Code explanation is limited because the code contains syntax errors.", "functions": []}
    scores = ScoringEngine.calculate(all_issues, ast_info)
    plagiarism = SimilarityChecker().compare(code)
    diff_html = DiffViewer.generate_html(code, fixed_code)

    score_cols = st.columns(4)
    score_cols[0].metric("Readability", f"{scores['readability']}/10")
    score_cols[1].metric("Efficiency", f"{scores['efficiency']}/10")
    score_cols[2].metric("Maintainability", f"{scores['maintainability']}/10")
    score_cols[3].metric("Overall", f"{scores['overall']}/10")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Issues",
        "Suggestions",
        "Explanation",
        "Auto-Fix",
        "Plagiarism",
        "AST Details",
    ])

    with tab1:
        st.subheader("Detected Issues")
        if not all_issues:
            st.success("No major issues detected.")
        for issue in all_issues:
            with st.container(border=True):
                st.markdown(f"**{issue['type']}** — line {issue.get('line', '-')}, column {issue.get('column', '-')}")
                st.write(issue.get("message", ""))
                st.caption(f"Why: {issue.get('why', '')}")
                st.caption(f"How to fix: {issue.get('fix', '')}")

    with tab2:
        st.subheader("AI Suggestions")
        st.write(f"Suggestion engine source: {ai_result.get('source', 'unknown')}")
        for section_name, label in [
            ("best_practices", "Better Coding Practices"),
            ("readability", "Readability Improvements"),
            ("optimization", "Optimization Tips"),
        ]:
            st.markdown(f"### {label}")
            for item in ai_result.get(section_name, []):
                st.write(f"- {item}")

    with tab3:
        st.subheader("Code Explanation")
        st.write(explanation["overall"])
        st.markdown("### Function-wise Explanation")
        for item in explanation["functions"]:
            st.write(f"- {item}")

    with tab4:
        left, right = st.columns(2)
        with left:
            st.subheader("Original Code")
            st.code(code, language="python")
        with right:
            st.subheader("Fixed Code")
            st.code(fixed_code, language="python")
        st.subheader("Highlighted Differences")
        st.components.v1.html(diff_html, height=500, scrolling=True)

    with tab5:
        st.subheader("Plagiarism Detection")
        st.metric("Similarity", f"{plagiarism['similarity_percent']}%")
        st.write(f"Most similar file: {plagiarism['top_match_name']}")
        st.write(f"Token similarity: {plagiarism['token_similarity']}%")
        st.write(f"AST similarity: {plagiarism['ast_similarity']}%")
        st.write(f"Cosine similarity: {plagiarism['cosine_similarity']}%")
        st.markdown("### Matching Section")
        st.code(plagiarism["matching_snippet"] or "No similar section found.", language="python")

    with tab6:
        st.subheader("AST and Structural Details")
        st.json({
            "function_metrics": ast_info.get("function_metrics", []),
            "imports": ast_info.get("imports", []),
            "classes": ast_info.get("classes", []),
            "node_count": ast_info.get("node_count", 0),
            "unused_variables": ast_info.get("unused_variables", []),
        })
