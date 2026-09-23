#!/usr/bin/env python3
"""
Build an HTML page that plays animation previews, for showing them to the user.

Chat clients often show only a GIF's first frame, so a batch of new animations
sent as files arrives as twenty stills. A page with the GIFs as <img> tags
plays them at their real frame delays. Publish the result as an Artifact, with
each GIF passed as a supporting file:

    python3 tools/gallery.py chess_mate wordle moo_deng
    python3 tools/gallery.py --section "Opus 5.5"      # every row in that section

Descriptions come from the matching rows of docs/AI_ANIMATIONS.md, so add those
rows first. Writes tools/out/gallery/index.html and prints the
published-path -> source-path map for the Artifact tool's `files` input.
GIFs are referenced in place, not copied: render them to docs/gifs/ first.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/AI_ANIMATIONS.md"
OUT = ROOT / "tools/out/gallery/index.html"
ROW = re.compile(r"^\| `(\w+)` \| .*? \| (.*) \|$", re.M)

STYLE = """
:root { color-scheme: dark; --ground: #0c0e13; --edge: #2a2f3c; --bezel: #1a1d26;
  --ink: #e4e7ee; --muted: #8b93a7; --amber: #ffc233; }
body { background: var(--ground); color: var(--ink);
  font: 15px/1.55 "IBM Plex Sans", system-ui, sans-serif; }
main { max-width: 1180px; margin: 0 auto; padding-inline: 20px; padding-block: 40px 64px; }
h1 { font-family: "Silkscreen", "IBM Plex Mono", monospace; font-weight: 400;
  font-size: clamp(28px, 5vw, 44px); line-height: 1.1; margin: 0 0 28px; color: var(--amber); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 340px), 1fr));
  gap: 28px 24px; }
figure { margin: 0; display: grid; gap: 10px; align-content: start; }
.panel { background: #000; border: 1px solid var(--edge); border-radius: 4px; padding: 8px;
  box-shadow: inset 0 0 0 4px var(--bezel); }
.panel img { display: block; width: 100%; height: auto; image-rendering: pixelated; }
h3 { font-family: "IBM Plex Mono", ui-monospace, monospace; font-weight: 400; font-size: 14px;
  margin: 0; color: var(--amber); }
figcaption p { margin: 4px 0 0; color: var(--muted); font-size: 14px; max-width: 62ch; }
"""
FONTS = (
    "https://fonts.googleapis.com/css2?family=Silkscreen"
    "&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono&display=swap"
)


def rows(text):
    return {name: desc for name, desc in ROW.findall(text)}


def section_text(text, heading):
    start = text.find(f"## Claude {heading}\n")
    if start < 0:
        sys.exit(f"no '## Claude {heading}' section in {DOC.name}")
    end = text.find("\n## ", start + 1)
    return text[start : end if end > 0 else None]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("names", nargs="*", help="animation names, e.g. wordle")
    parser.add_argument("--section", help="model heading in AI_ANIMATIONS.md, e.g. 'Opus 5.5'")
    parser.add_argument("--title", default="New animations")
    args = parser.parse_args()

    text = DOC.read_text()
    known = rows(text)
    names = list(args.names)
    if args.section:
        names += [n for n in rows(section_text(text, args.section)) if n not in names]
    if not names:
        parser.error("give animation names or --section")

    cards, files = [], {}
    for name in names:
        gif = ROOT / "docs/gifs" / f"{name}.gif"
        if not gif.exists():
            sys.exit(f"missing {gif.relative_to(ROOT)} -- render it with preview_jt.py --gif")
        desc = html.escape(known.get(name, "")).replace("--", "—")
        files[f"gifs/{name}.gif"] = str(gif.relative_to(ROOT))
        cards.append(
            f'<figure><div class="panel"><img src="gifs/{name}.gif" alt="{name} animation"'
            f' width="288" height="48"></div><figcaption><h3>{name}</h3><p>{desc}</p>'
            "</figcaption></figure>"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        f"<title>{html.escape(args.title)}</title>\n"
        f'<link rel="stylesheet" href="{FONTS}">\n<style>{STYLE}</style>\n'
        f"<main><h1>{html.escape(args.title)}</h1>\n<section class=\"grid\">\n"
        + "\n".join(cards)
        + "\n</section></main>\n"
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({len(names)} animations)")
    print(json.dumps(files, indent=2))


if __name__ == "__main__":
    main()
