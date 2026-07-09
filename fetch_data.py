#!/usr/bin/env python3
"""Re-download the YC directory and refresh src/yc_mini.json, then rebuild.

Usage: python3 fetch_data.py && python3 build.py
"""
import json, pathlib, re, urllib.request

URL = "https://yc-oss.github.io/api/companies/all.json"
SRC = pathlib.Path(__file__).parent / "src"

print(f"downloading {URL} …")
with urllib.request.urlopen(URL) as r:
    companies = json.load(r)

BF = "https://bookface-images.s3.amazonaws.com/small_logos/"

def logo(c):
    u = c.get("small_logo_thumb_url") or ""
    return u[len(BF):] if u.startswith(BF) else u

def trim(s, cap=900):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    if len(s) <= cap:
        return s
    cut = s.rfind(". ", 0, cap)
    return s[:cut+1] if cut > 200 else s[:cap] + "…"

mini = [{
    "n": c["name"],
    "b": c["batch"],
    "i": c["industry"],
    "s": c["subindustry"].split(" -> ")[-1] if c["subindustry"] else "",
    "o": c["one_liner"],
    "d": trim(c["long_description"]),
    "w": c["website"],
    "u": c["url"],
    "t": c["team_size"],
    "st": c["status"],
    "top": c["top_company"],
    "l": logo(c),
    "sg": c.get("stage") or "",
    "h": (c.get("all_locations") or "").split("; ")[0],
} for c in companies]

out = SRC / "yc_mini.json"
out.write_text(json.dumps(mini, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(mini)} companies. Now run: python3 build.py")
