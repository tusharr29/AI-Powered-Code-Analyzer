# AI-Powered Code Analyzer, Auto-Fixer, and Plagiarism Detection System

A final-year engineering project built with Python and Streamlit.

## Features
- Syntax error detection using Python AST
- Rule-based code quality analysis
- Code smell detection
- Auto-fix suggestions and fixed code generation
- Function-wise code explanation
- Plagiarism detection using token similarity, AST similarity, and TF-IDF cosine similarity
- Quality scoring for readability, efficiency, maintainability, and overall score
- Web-based UI with editor, file upload, diff view, and result sections

## Project Structure
```
ai_code_analyzer/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   └── sample_corpus.json
├── samples/
│   └── buggy_sample.py
├── analyzer/
│   ├── __init__.py
│   ├── syntax_checker.py
│   ├── ast_parser.py
│   └── code_smell_detector.py
├── ai_module/
│   ├── __init__.py
│   ├── suggestion_engine.py
│   └── explanation_generator.py
├── plagiarism/
│   ├── __init__.py
│   └── similarity_checker.py
└── utils/
    ├── __init__.py
    ├── scoring.py
    └── diff_viewer.py
```

## Phase-wise Build
### Phase 1: Basic analyzer
- Parse code with AST
- Detect syntax errors, unused variables, long functions, deep nesting, and basic infinite loops
- Run pylint for rule-based lint messages

### Phase 2: AI suggestions
- Generate coding practice suggestions
- Improve readability and optimization tips
- Works with OpenAI API if key is available, otherwise uses deterministic fallback suggestions

### Phase 3: Auto-fix
- Apply safe auto-fixes like whitespace cleanup, trailing space removal, tab normalization, and missing final newline
- Generate an improved version with readable formatting and comments-free cleanup
- Show original vs fixed diff

### Phase 4: Plagiarism detection
- Compare code with preloaded corpus and optional previous submissions
- Compute token similarity, AST structure similarity, and TF-IDF cosine similarity
- Return similarity percentage, matching snippet, and top match

### Phase 5: UI integration
- Streamlit app with code editor or file upload
- Organized result sections for errors, suggestions, explanation, score, plagiarism, and diff

## Setup
1. Create a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Optional: configure AI suggestions
   ```bash
   cp .env.example .env
   ```
   Add your OpenAI API key in `.env`.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Notes
- Python is supported first, but the architecture is modular for future Java/C++ analyzers.
- Plagiarism corpus is stored in `data/sample_corpus.json` and can be replaced with your own submissions.
- Auto-fix is intentionally conservative for a student project.
