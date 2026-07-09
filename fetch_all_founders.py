#!/usr/bin/env python3
"""Fetch founders (name, title, photo, socials) for EVERY company in src/yc_mini.json
from public YC pages. Resumable: reruns skip already-fetched companies.

Writes src/founders.json  { "name|batch": [ {n,t,x,li,img}, ... ] }
Downloads avatar thumbs into avatars/.

Usage: python3 fetch_all_founders.py && python3 build.py
"""
import html, json, pathlib, re, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
AVA = ROOT / "avatars"
AVA.mkdir(exist_ok=True)
OUT = SRC / "founders.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

yc = json.load(open(SRC / "yc_mini.json"))
done = json.load(open(OUT)) if OUT.exists() else {}
lock = threading.Lock()
stats = {"ok": 0, "empty": 0, "fail": 0, "avatars": 0}

def fetch(url, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))

def save():
    tmp = OUT.with_suffix(".tmp")
    tmp.write_text(json.dumps(done, ensure_ascii=False, separators=(",", ":")))
    tmp.replace(OUT)

def work(c):
    key = c["n"].lower() + "|" + c["b"]
    if key in done:
        return
    try:
        page = fetch(c["u"]).decode("utf-8", "replace")
        m = re.search(r'data-page="([^"]*)"', page)
        founders = json.loads(html.unescape(m.group(1)))["props"]["company"]["founders"] or []
    except Exception:
        with lock:
            stats["fail"] += 1
        return  # left out of `done` so a rerun retries it
    entries = []
    for p in founders:
        e = {"n": p.get("full_name") or "?"}
        if p.get("title"):
            e["t"] = p["title"]
        tw = p.get("twitter_url") or ""
        handle = re.sub(r"^https?://(www\.)?(twitter|x)\.com/", "", tw).strip("/") if tw else ""
        if handle:
            e["x"] = handle
        if p.get("linkedin_url"):
            e["li"] = p["linkedin_url"]
        avatar = p.get("avatar_thumb_url") or ""
        k = re.search(r"avatars/([0-9a-f]+)\.(\w+)", avatar)
        if k:
            fname = f"{k.group(1)}.{k.group(2)}"
            path = AVA / fname
            if not path.exists():
                try:
                    path.write_bytes(fetch(avatar))
                    with lock:
                        stats["avatars"] += 1
                except Exception:
                    fname = ""
            if fname:
                e["img"] = fname
        entries.append(e)
    with lock:
        done[key] = entries
        stats["ok" if entries else "empty"] += 1
        n = stats["ok"] + stats["empty"]
        if n % 200 == 0:
            save()
            print(f"{n} companies done ({stats['avatars']} avatars, {stats['fail']} failures)", flush=True)
    time.sleep(0.05)

todo = [c for c in yc if (c["n"].lower() + "|" + c["b"]) not in done]
print(f"{len(todo)} companies to fetch ({len(done)} already done)", flush=True)
with ThreadPoolExecutor(max_workers=6) as ex:
    list(ex.map(work, todo))
save()
print(f"finished: {stats} — total {len(done)} companies in {OUT}", flush=True)
