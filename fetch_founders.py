#!/usr/bin/env python3
"""Fetch founder profiles (name, title, photo, socials) for featured companies
from their public YC pages, download avatars locally, and update src/featured.json.

Usage: python3 fetch_founders.py && python3 build.py
"""
import html, json, pathlib, re, time, urllib.request

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
AVA = ROOT / "avatars"
AVA.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

yc = json.load(open(SRC / "yc_mini.json"))
feat = json.load(open(SRC / "featured.json"))
url_by_key = {(c["n"].lower(), c["b"]): c["u"] for c in yc}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

for f in feat:
    url = url_by_key.get((f["name"].lower(), f["batch"]))
    if not url:
        print(f"!! no YC url for {f['name']}")
        continue
    try:
        page = fetch(url).decode("utf-8", "replace")
        m = re.search(r'data-page="([^"]*)"', page)
        founders = json.loads(html.unescape(m.group(1)))["props"]["company"]["founders"]
    except Exception as e:
        print(f"!! {f['name']}: {e}")
        continue
    if not founders:
        print(f"-- {f['name']}: page lists no founders, keeping curated names")
        continue
    old_x = {p["n"].lower(): p.get("x") for p in f["founders"]}
    new = []
    for p in founders:
        entry = {"n": p["full_name"]}
        if p.get("title"):
            entry["t"] = p["title"]
        tw = p.get("twitter_url") or ""
        handle = re.sub(r"^https?://(www\.)?(twitter|x)\.com/", "", tw).strip("/") if tw else ""
        if handle:
            entry["x"] = handle
        elif old_x.get(p["full_name"].lower()):
            entry["x"] = old_x[p["full_name"].lower()]
        li = p.get("linkedin_url") or ""
        if li:
            entry["li"] = li
        avatar = p.get("avatar_thumb_url") or ""
        key = re.search(r"avatars/([0-9a-f]+)\.(\w+)", avatar)
        if key:
            fname = f"{key.group(1)}.{key.group(2)}"
            path = AVA / fname
            if not path.exists():
                try:
                    path.write_bytes(fetch(avatar))
                except Exception as e:
                    print(f"   avatar failed for {p['full_name']}: {e}")
                    fname = ""
            if fname:
                entry["img"] = fname
        new.append(entry)
    f["founders"] = new
    print(f"ok {f['name']}: {len(new)} founders, "
          f"{sum(1 for p in new if 'img' in p)} photos, "
          f"{sum(1 for p in new if 'li' in p)} linkedin, "
          f"{sum(1 for p in new if 'x' in p)} x")
    time.sleep(0.3)

json.dump(feat, open(SRC / "featured.json", "w"), ensure_ascii=False, indent=0)
total = sum(len(f["founders"]) for f in feat)
print(f"\nsaved featured.json — {total} founders, avatars in {AVA}/")
