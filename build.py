#!/usr/bin/env python3
"""Assemble index.html from src/template.html + data files."""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"

def load(name):
    with open(SRC / name, encoding="utf-8") as f:
        return json.load(f)

def js(obj):
    # compact JSON, safe to inline inside a <script> block
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).replace("</", "<\\/")

yc = load("yc_mini.json")
featured = load("featured.json")
dictionary = load("dictionary.json")
jargon = load("jargon.json")
founders = load("founders.json") if (SRC / "founders.json").exists() else {}
socials = load("socials.json") if (SRC / "socials.json").exists() else {}

# sanity: every featured (name, batch) pair must exist in the dataset
pairs = {(c["n"].lower(), c["b"]) for c in yc}
missing = [f["name"] for f in featured if (f["name"].lower(), f.get("batch")) not in pairs]
if missing:
    sys.exit(f"featured (name, batch) not in dataset: {missing}")

html = (SRC / "template.html").read_text(encoding="utf-8")
for token, payload in [
    ("__YC_DATA__", js(yc)),
    ("__FEATURED__", js(featured)),
    ("__DICT__", js(dictionary)),
    ("__JARGON__", js(jargon)),
    ("__FOUNDERS__", js(founders)),
    ("__SOCIALS__", js(socials)),
]:
    assert token in html, token
    html = html.replace(token, payload)

out = ROOT / "index.html"
out.write_text(html, encoding="utf-8")

# extract inline app script for a node syntax check
m = re.search(r'<script id="app">\n(.*?)\n</script>', html, re.S)
(ROOT / ".app_check.js").write_text(m.group(1), encoding="utf-8")

print(f"built {out} ({out.stat().st_size/1e6:.2f} MB), "
      f"{len(yc)} companies, {len(featured)} featured, {len(founders)} founder sets, "
      f"{len(dictionary)} dictionary terms")
