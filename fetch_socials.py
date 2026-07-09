#!/usr/bin/env python3
"""Fetch each company's own social links (X/Twitter, LinkedIn) from its public
YC page. Only stores links that actually exist. Resumable.

Writes src/socials.json  { "name|batch": {"x": url, "li": url} }

Usage: python3 fetch_socials.py && python3 build.py
"""
import html, json, pathlib, re, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
OUT = SRC / "socials.json"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

yc = json.load(open(SRC / "yc_mini.json"))
done = json.load(open(OUT)) if OUT.exists() else {}
lock = threading.Lock()
stats = {"done": 0, "with_socials": 0, "fail": 0}

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
        co = json.loads(html.unescape(m.group(1)))["props"]["company"]
    except Exception:
        with lock:
            stats["fail"] += 1
        return
    e = {}
    if co.get("twitter_url"):
        e["x"] = co["twitter_url"]
    if co.get("linkedin_url"):
        e["li"] = co["linkedin_url"]
    with lock:
        done[key] = e
        stats["done"] += 1
        if e:
            stats["with_socials"] += 1
        if stats["done"] % 300 == 0:
            save()
            print(f"{stats['done']} done ({stats['with_socials']} with socials, {stats['fail']} failures)", flush=True)
    time.sleep(0.05)

todo = [c for c in yc if (c["n"].lower() + "|" + c["b"]) not in done]
print(f"{len(todo)} companies to fetch ({len(done)} already done)", flush=True)
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(work, todo))
save()
print(f"finished: {stats} — total {len(done)} in {OUT}", flush=True)
