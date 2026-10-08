import difflib


class DiffViewer:
    """Builds side-by-side HTML diff for Streamlit."""

    @staticmethod
    def generate_html(original: str, fixed: str) -> str:
        differ = difflib.HtmlDiff(wrapcolumn=80)
        return differ.make_table(
            original.splitlines(),
            fixed.splitlines(),
            fromdesc="Original Code",
            todesc="Fixed Code",
            context=True,
            numlines=2,
        )
