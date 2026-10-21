#!/usr/bin/env python3
"""Fetch the BitcoinTalk threads that contain the archived Satoshi posts, to
build a same-forum, same-period CONTROL corpus of other members' writing.

Purpose: test whether the fingerprint habits are distinctive against
contemporary writers on the same forum and topics. The control corpus is used
only for population-level comparisons (how common is each habit among other
writers). No per-writer ranking or similarity search is produced by this
pipeline, and the outputs do not name control writers.

Topic numbers come from the `original_url` field of data/sni_posts.jsonl.
Pages are fetched in order (20 posts per page) and fetching of a topic stops at
the first page whose first post is dated after 2010-12-31. Every response is
cached; re-running only fetches missing pages. A delay of --delay seconds
(default 2) separates requests.

Usage: python3 06_fetch_forum_threads.py --cache DIR [--delay 2]
"""
import argparse, json, os, re, subprocess, sys, time
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (stylometry research; cached, rate-limited)"

def fetch(url, path, delay):
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return open(path, encoding="latin-1").read()
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-A", UA, "--max-time", "60", url, "-o", path], capture_output=True, text=True)
        time.sleep(delay)
        if r.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > 5000:
            return open(path, encoding="latin-1").read()
        time.sleep(delay * (2 ** attempt))
    print("FAILED", url, file=sys.stderr)
    return None

def first_date(html):
    s = BeautifulSoup(html, "html.parser")
    for td in s.select("td.td_headerandpost"):
        d = td.select_one("div.smalltext")
        if d:
            m = re.search(r"(\w+ \d{2}, (\d{4}))", d.get_text(" ", strip=True))
            if m:
                return m.group(1)
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--delay", type=float, default=2.0)
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    topics = []
    for l in open(os.path.join(HERE, "..", "data", "sni_posts.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        m = re.search(r"topic=(\d+)", r.get("original_url") or "")
        if m and int(m.group(1)) not in topics:
            topics.append(int(m.group(1)))
    print(len(topics), "topics")
    for t in topics:
        start = 0
        while True:
            html = fetch(f"https://bitcointalk.org/index.php?topic={t}.{start}", os.path.join(a.cache, f"t{t}_{start}.html"), a.delay)
            if html is None:
                break
            fd = first_date(html)
            year = int(re.search(r"\d{4}", fd).group(0)) if fd else 9999
            offsets = [int(x) for x in re.findall(rf"topic={t}\.(\d+)", html)]
            if year > 2010 or not offsets or max(offsets) <= start:
                break
            nxt = sorted(o for o in set(offsets) if o > start and o % 20 == 0)
            if not nxt:
                break
            start = nxt[0]
    print("done")

if __name__ == "__main__":
    main()
