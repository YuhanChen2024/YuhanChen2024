#!/usr/bin/env python3
"""Generate an auto-scrolling news ticker SVG from assets/news.json."""

import json
import pathlib
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "assets" / "news.json"
OUT = ROOT / "assets" / "news-ticker.svg"

WIDTH = 830          # matches GitHub README content width
ROW_H = 32           # height of one news row
VISIBLE = 3          # rows visible at once
HEADER_Y = 18
PANEL_Y = 26
SEC_PER_ROW = 2.6    # scroll speed: seconds spent per row
MAX_CHARS = 100      # truncate long titles so they never overflow

FONT = ('ui-sans-serif, -apple-system, "Segoe UI", Helvetica, Arial, '
        '"Apple Color Emoji", "Segoe UI Emoji", sans-serif')

STYLE = """
  <style>
    .t    { font: 500 14px %(font)s; fill: #24292f; }
    .v    { font: 400 13px %(font)s; fill: #57606a; }
    .hdr  { font: 700 13px %(font)s; fill: #57606a; }
    .panel{ fill: #f6f8fa; stroke: #d0d7de; stroke-width: 1; }
    .track{ animation: roll __DUR__s linear infinite; }
    @keyframes roll {
      from { transform: translateY(0); }
      to   { transform: translateY(-__TRACK__px); }
    }
    @media (prefers-color-scheme: dark) {
      .t { fill: #c9d1d9; } .v { fill: #8b949e; } .hdr { fill: #8b949e; }
      .panel { fill: #0d1117; stroke: #30363d; }
    }
  </style>
""" % {"font": FONT}


def truncate(text: str, limit: int = MAX_CHARS) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "\u2026"


def build(data: dict) -> str:
    items = data["items"]
    n = len(items)
    track_h = n * ROW_H
    duration = round(n * SEC_PER_ROW, 1)
    panel_h = VISIBLE * ROW_H + 12
    height = PANEL_Y + panel_h + 6
    content_top = PANEL_Y + 6

    rows = []
    for rep in range(2):  # two copies -> seamless loop
        for i, item in enumerate(items):
            y = rep * track_h + i * ROW_H + 21
            head = f"{item['emoji']} [{item['year']}] {truncate(item['title'])}"
            rows.append(f'<text class="t" x="16" y="{y}">{escape(head)}</text>')
            if item.get("venue"):
                rows.append(
                    f'<text class="v" x="16" y="{y + 14}">'
                    f'{escape(item["venue"])}</text>'
                )

    style = STYLE.replace("__DUR__", str(duration)).replace("__TRACK__", str(track_h))
    header = f"News \u00b7 auto-scrolling \u00b7 updated {data['generated']}"

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="Latest news, auto-scrolling">\n'
        f"{style}"
        f'  <defs><clipPath id="ticker-clip">'
        f'<rect x="1" y="{PANEL_Y}" width="{WIDTH - 2}" height="{panel_h}" rx="6"/>'
        f"</clipPath></defs>\n"
        f'  <text class="hdr" x="4" y="{HEADER_Y}">{escape(header)}</text>\n'
        f'  <rect class="panel" x="1" y="{PANEL_Y}" width="{WIDTH - 2}" '
        f'height="{panel_h}" rx="6"/>\n'
        f'  <g clip-path="url(#ticker-clip)">\n'
        f'    <g transform="translate(0,{content_top})">\n'
        f'      <g class="track">\n        ' + "\n        ".join(rows) + "\n"
        f"      </g>\n    </g>\n  </g>\n</svg>\n"
    )


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(data), encoding="utf-8")
    print(f"wrote {OUT} ({len(data['items'])} items)")


if __name__ == "__main__":
    main()
