"""Builds the paste-ready WordPress snippets in dist/ from the files in src/.

Run:  python3 build.py
"""
import pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

PAGES = {
    "home": ("1-markets-overview", "Markets overview", "/markets/"),
    "india": ("2-markets-india", "Indian stock market", "/markets/india/"),
    "usa": ("3-markets-usa", "US stock market", "/markets/usa/"),
    "symbol": ("4-markets-symbol", "Symbol details", "/markets/symbol/"),
}

css = (SRC / "shared.css").read_text()
js = (SRC / "shared.js").read_text()
nav = (SRC / "nav.html").read_text()
footer = (SRC / "footer.html").read_text()

DIST.mkdir(exist_ok=True)


for key, (fname, title, path) in PAGES.items():
    body = (SRC / "pages" / f"{key}.html").read_text()
    page_js = (SRC / "pages" / f"{key}.js").read_text()
    page_nav = nav
    for k in ("HOME", "INDIA", "USA"):
        page_nav = page_nav.replace("{{ON_%s}}" % k, "on" if k.lower() == key else "")
    script = js.replace("  /*PAGE*/\n", page_js)
    assert "/*PAGE*/" not in script
    snippet = (
        f"<!-- WebThru Markets: {title}. Paste into an Elementor HTML widget on the page at {path} -->\n"
        f"<style>\n{css}</style>\n"
        f'<div class="wt-mkt">\n{page_nav}{body}{footer}</div>\n'
        f"<script>\n{script}</script>\n"
    )
    (DIST / f"{fname}.html").write_text(snippet)
    print("built", fname, len(snippet), "bytes")
