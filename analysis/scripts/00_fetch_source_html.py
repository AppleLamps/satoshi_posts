#!/usr/bin/env python3
"""Fetch the structured HTML of every post from satoshi.nakamotoinstitute.org
(the site the repository's posts/ files were scraped from) and store the inner
HTML of each post body plus its metadata in analysis/data/sni_posts.jsonl.

The repository files were produced with BeautifulSoup.get_text(), which dropped
every block boundary (paragraphs, blockquotes, code blocks). The live site still
has those boundaries, so this companion data set is used ONLY to establish the
original form of quotes, paragraph breaks and code blocks. The repository text
remains the primary corpus; 01_extract.py verifies that the two agree
character-for-character after whitespace normalisation before using the HTML
segmentation, and falls back to heuristics (and flags the post) otherwise.

Usage:
    python3 00_fetch_source_html.py --cache DIR [--fetch]
      --fetch   download pages into DIR (skips files already present)
      (without --fetch, only parses pages already in DIR)
"""
import argparse, json, os, re, sys, time, glob
import urllib.request
from bs4 import BeautifulSoup

BASE = "https://satoshi.nakamotoinstitute.org"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "sni_posts.jsonl")

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "satoshi-stylometry/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")

def list_urls(cache):
    idx = os.path.join(cache, "index.html")
    if not os.path.exists(idx):
        open(idx, "w").write(get(BASE + "/posts/"))
    html = open(idx).read()
    urls = sorted(set(re.findall(r'href="(%s/posts/(?:bitcointalk|p2pfoundation)/\d+/)"' % re.escape(BASE), html)))
    return urls

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--fetch", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.cache, "pages"), exist_ok=True)
    if a.fetch:
        for u in list_urls(a.cache):
            plat, n = u.rstrip("/").split("/")[-2:]
            out = os.path.join(a.cache, "pages", f"{plat}_{n}.html")
            if os.path.exists(out) and os.path.getsize(out) > 0:
                continue
            open(out, "w").write(get(u))
            time.sleep(0.25)
    recs = []
    for f in sorted(glob.glob(os.path.join(a.cache, "pages", "*.html"))):
        plat, n = os.path.basename(f)[:-5].rsplit("_", 1)
        s = BeautifulSoup(open(f).read(), "html.parser")
        main_ = s.find("main")
        h1 = main_.find("h1")
        t = main_.find("time")
        post = main_.find("div", class_="post")
        if post is None:
            # p2pfoundation pages use a different body container; take the section
            sec = main_.find("section")
            post = sec
        orig = main_.find("a", string=re.compile("View original"))
        recs.append({
            "sni_platform": plat,
            "sni_number": int(n),
            "title": h1.get_text(strip=True),
            "datetime": t["datetime"] if t and t.has_attr("datetime") else None,
            "original_url": orig["href"] if orig else None,
            "post_html": post.decode_contents() if post else None,
        })
    recs.sort(key=lambda r: (r["sni_platform"], r["sni_number"]))
    with open(OUT, "w") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(recs)} records to {OUT}")

if __name__ == "__main__":
    main()
