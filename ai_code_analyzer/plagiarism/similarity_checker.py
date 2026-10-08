import ast
import io
import json
import keyword
import tokenize
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimilarityChecker:
    """Compares code against a corpus using tokens, AST, and TF-IDF."""

    def __init__(self, corpus_path: str = "data/sample_corpus.json") -> None:
        self.corpus_path = Path(corpus_path)
        self.corpus = self._load_corpus()

    def _load_corpus(self) -> List[Dict[str, str]]:
        if self.corpus_path.exists():
            return json.loads(self.corpus_path.read_text(encoding="utf-8"))
        return []

    @staticmethod
    def tokenize_code(code: str) -> List[str]:
        tokens = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(code).readline):
                if tok.type == tokenize.NAME:
                    if tok.string in keyword.kwlist:
                        tokens.append(tok.string)
                    else:
                        tokens.append("IDENT")
                elif tok.type == tokenize.NUMBER:
                    tokens.append("NUMBER")
                elif tok.type == tokenize.STRING:
                    tokens.append("STRING")
                elif tok.string.strip():
                    tokens.append(tok.string)
        except tokenize.TokenError:
            pass
        return tokens

    @staticmethod
    def ast_signature(code: str) -> List[str]:
        try:
            tree = ast.parse(code)
            return [type(node).__name__ for node in ast.walk(tree)]
        except SyntaxError:
            return []

    @staticmethod
    def jaccard_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
        set_a, set_b = set(tokens_a), set(tokens_b)
        if not set_a or not set_b:
            return 0.0
        return len(set_a & set_b) / len(set_a | set_b)

    @staticmethod
    def multiset_similarity(items_a: List[str], items_b: List[str]) -> float:
        counter_a, counter_b = Counter(items_a), Counter(items_b)
        common = sum((counter_a & counter_b).values())
        total = sum((counter_a | counter_b).values())
        return common / total if total else 0.0

    @staticmethod
    def extract_matching_snippet(code_a: str, code_b: str) -> Tuple[str, float]:
        matcher = SequenceMatcher(None, code_a, code_b)
        match = matcher.find_longest_match(0, len(code_a), 0, len(code_b))
        snippet = code_b[match.b : match.b + match.size].strip()
        return snippet[:500], matcher.ratio()

    def compare(self, input_code: str) -> Dict[str, Any]:
        if not self.corpus:
            return {
                "similarity_percent": 0.0,
                "top_match_name": "No corpus loaded",
                "matching_snippet": "",
                "token_similarity": 0.0,
                "ast_similarity": 0.0,
                "cosine_similarity": 0.0,
            }

        texts = [input_code] + [item["code"] for item in self.corpus]
        vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        tfidf = vectorizer.fit_transform(texts)
        cosine_scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

        input_tokens = self.tokenize_code(input_code)
        input_ast = self.ast_signature(input_code)

        best = None
        best_score = -1.0

        for index, item in enumerate(self.corpus):
            corpus_tokens = self.tokenize_code(item["code"])
            corpus_ast = self.ast_signature(item["code"])
            token_score = self.jaccard_similarity(input_tokens, corpus_tokens)
            ast_score = self.multiset_similarity(input_ast, corpus_ast)
            cosine_score = float(cosine_scores[index])
            combined = (token_score * 0.3) + (ast_score * 0.3) + (cosine_score * 0.4)

            if combined > best_score:
                snippet, _ = self.extract_matching_snippet(input_code, item["code"])
                best_score = combined
                best = {
                    "similarity_percent": round(combined * 100, 2),
                    "top_match_name": item["name"],
                    "matching_snippet": snippet,
                    "token_similarity": round(token_score * 100, 2),
                    "ast_similarity": round(ast_score * 100, 2),
                    "cosine_similarity": round(cosine_score * 100, 2),
                }

        return best or {
            "similarity_percent": 0.0,
            "top_match_name": "No match",
            "matching_snippet": "",
            "token_similarity": 0.0,
            "ast_similarity": 0.0,
            "cosine_similarity": 0.0,
        }
