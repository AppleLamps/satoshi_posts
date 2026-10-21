#!/usr/bin/env python3
"""Build the committed, anonymized control dataset from the cached BitcoinTalk
thread pages (06_fetch_forum_threads.py).

Input : --cache DIR with t<topic>_<offset>.html pages
Output (all committed, so 08_control_analysis.py runs offline):
  data/control/pages_manifest.csv   one row per page: URL, bytes, SHA-256
  data/control/post_counts.csv.gz   one row per post 2009-11-01..2010-12-31:
                                    pseudonymous writer id, topic, msg id,
                                    date, thread position, role label and
                                    role inputs, SHA-256 of the cleaned prose,
                                    and every additive feature count used by
                                    the analysis (words, sentences, opportunity
                                    counts for each two-way choice, ...)
  data/control/cleaning_parity.csv  Satoshi's posts cleaned from the thread
                                    pages vs the archive extraction (word
                                    counts), to check that both populations
                                    are cleaned the same way
  data/forum_last_edit.csv          "Last edit" stamps for the archived posts

Cleaning: cleaning.clean_forum_post_html(), the same R12/R12b rules that
01_extract.py applies to the archive. Satoshi's posts are taken from the same
pages with the same cleaner (writer id "SATOSHI") so the comparison is like
for like; his archive-based figures elsewhere in the report are unaffected.

Anonymization: writer ids are W0001, W0002, ... in order of each account's
first post (by message id). Account names, quoted text and post text are not
written. The pages are public, so anyone who re-fetches them can map ids back
to accounts; the ids prevent casual naming, not determined re-identification.

Role labels (computed from thread structure, never from the features under
test):
  question  : the post's own prose contains a sentence ending in "?"
  answer    : no question sentence in its own prose, and it either quotes text
              containing "?" or directly follows, in the thread, a post by
              another writer whose own prose contains "?"
  statement : neither (announcements, reports, comments, follow-ups)
"""
import argparse, csv, glob, gzip, hashlib, json, os, re, sys
from collections import defaultdict
from bs4 import BeautifulSoup
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textutil as T
import measures as M
from cleaning import clean_forum_post_html

OUT = os.path.join(HERE, "..", "data", "control")
MONTHS = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}

def parse_date(s):
    m = re.search(r"(\w+) (\d{2}), (\d{4}), (\d{2}):(\d{2}):(\d{2}) (AM|PM)", s)
    if not m or m.group(1) not in MONTHS:
        return None
    h = int(m.group(4)) % 12 + (12 if m.group(7) == "PM" else 0)
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d} {h:02d}:{m.group(5)}:{m.group(6)}"

COUNT_KEYS = ["words", "sentences", "double_space", "single_space", "semicolon", "exclaim", "em_en_dash", "double_hyphen",
              "if_you_openers", "if_you_openers_bare", "verdict_openers", "it_would_be", "hedges", "boosters",
              "quote_punct_outside", "quote_punct_inside", "list_num_paren", "list_num_dot", "bullet_dash", "bullet_star",
              "percent_attached", "percent_word", "spelling_non_us", "spelling_us_only", "spelling_ize", "gotten"]

def counts(text):
    """Additive counts for one post. Every rate or share in the analysis is
    a ratio of sums of these columns, so samples of whole posts can be pooled."""
    if not T.words(text):
        return None
    p = M.profile([text])
    toks = T.words(text)
    c = {k: p[k] for k in COUNT_KEYS}
    allc, cc, ff = M.contractions(text)
    c.update(contractions=allc, contracted_choice=cc, full_choice=ff)
    c["if"] = sum(1 for t in toks if t == "if")
    c["you_group"] = sum(1 for t in toks if t in ("you", "your", "you're", "you've", "you'll", "you'd"))
    c["i_group"] = sum(1 for t in toks if t in ("i", "me", "my", "i'm", "i've", "i'll", "i'd"))
    c["question_marks"] = T.mask_urls(text).count("?")
    c["question_sentences"] = sum(1 for s in T.sentences(text) if s.rstrip().endswith("?"))
    for k in M.TERM_FORMS:
        c["term_" + k] = p["term_" + k]
    return c

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    pages, posts = [], {}
    for f in sorted(glob.glob(os.path.join(a.cache, "t*_*.html")), key=lambda x: [int(n) for n in re.findall(r"\d+", os.path.basename(x))]):
        raw = open(f, "rb").read()
        topic, offset = [int(n) for n in re.findall(r"\d+", os.path.basename(f))]
        pages.append(dict(topic=topic, offset=offset, url=f"https://bitcointalk.org/index.php?topic={topic}.{offset}", bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
        s = BeautifulSoup(raw.decode("latin-1"), "html.parser")
        for td in s.select("td.td_headerandpost"):
            subj = td.select_one("div.subject")
            mid = re.search(r"subject_(\d+)", subj.get("id", "")) if subj else None
            body = td.select_one("div.post")
            if not mid or body is None or int(mid.group(1)) in posts:
                continue
            row = td.find_parent("tr")
            pi = row.select_one("td.poster_info") if row else None
            author = pi.find("b").get_text(strip=True) if pi and pi.find("b") else None
            sm = td.select_one("div.smalltext")
            date = parse_date(sm.get_text(" ", strip=True)) if sm else None
            ed = td.select_one("span.edited")
            last_edit = parse_date(ed.get("title", "")) if ed and "Last edit" in ed.get("title", "") else None
            edited_by = re.search(r" by (.+)$", ed.get("title", "")).group(1) if ed and " by " in ed.get("title", "") else None
            quotes_q = any("?" in q.get_text() for q in body.select("div.quote"))
            text = clean_forum_post_html(body)
            posts[int(mid.group(1))] = dict(msg=int(mid.group(1)), topic=topic, author=author, date=date, last_edit=last_edit,
                                           edited_by=edited_by, quotes_question=quotes_q, text=text)
    with open(os.path.join(OUT, "pages_manifest.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pages[0].keys())); w.writeheader(); w.writerows(pages)

    # ---------------------------------------------- archive mapping, last-edit stamps, cleaning parity
    recs = {json.loads(l)["post_id"]: json.loads(l) for l in open(os.path.join(HERE, "..", "data", "posts_clean.jsonl"), encoding="utf-8")}
    edit_rows, parity = [], []
    for pid in sorted(recs):
        m = re.search(r"msg(\d+)", recs[pid].get("original_url") or "")
        if not m or int(m.group(1)) not in posts:
            continue
        p = posts[int(m.group(1))]
        if p["last_edit"]:
            edit_rows.append((pid, recs[pid]["timestamp"], p["date"], p["last_edit"], p["edited_by"]))
        r = recs[pid]
        if r["platform"] == "Bitcointalk" and r["usable_for_prose_stats"] and "repost_of_other_members" not in r["flags"]:
            own = "\n".join(s_["text"] for s_ in r["segments"] if s_["type"] == "own")
            parity.append((pid, len(T.words(own)), len(T.words(p["text"])), len(T.words(own)) == len(T.words(p["text"])), ";".join(r["flags"])))
    with open(os.path.join(HERE, "..", "data", "forum_last_edit.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["post_id", "archive_timestamp", "forum_posted", "forum_last_edit", "edited_by"]); w.writerows(edit_rows)
    with open(os.path.join(OUT, "cleaning_parity.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["post_id", "archive_words", "thread_page_words", "equal", "archive_flags"]); w.writerows(parity)

    # ---------------------------------------------- roles from thread structure
    by_topic = defaultdict(list)
    for p in posts.values():
        by_topic[p["topic"]].append(p)
    for lst in by_topic.values():
        lst.sort(key=lambda x: x["msg"])
        prev = None
        for i, p in enumerate(lst):
            p["position"] = i
            p["own_question"] = bool(T.words(p["text"])) and any(s.rstrip().endswith("?") for s in T.sentences(p["text"]))
            p["prev_question"] = bool(prev and prev["author"] != p["author"] and prev["own_question"])
            p["role"] = "question" if p["own_question"] else ("answer" if (p["quotes_question"] or p["prev_question"]) else "statement")
            prev = p

    # ---------------------------------------------- anonymized per-post counts
    ids, rows = {}, []
    for p in sorted(posts.values(), key=lambda x: x["msg"]):
        if not p["author"] or not p["date"] or not ("2009-11-01" <= p["date"][:10] <= "2010-12-31"):
            continue
        c = counts(p["text"])
        if c is None:
            continue
        wid = "SATOSHI" if p["author"].lower() == "satoshi" else ids.setdefault(p["author"], f"W{len(ids) + 1:04d}")
        rows.append(dict(writer=wid, msg=p["msg"], topic=p["topic"], date=p["date"], position=p["position"], role=p["role"],
                         own_question=int(p["own_question"]), quotes_question=int(p["quotes_question"]), prev_question=int(p["prev_question"]),
                         text_sha256=hashlib.sha256(p["text"].encode("utf-8")).hexdigest(), **c))
    with gzip.open(os.path.join(OUT, "post_counts.csv.gz"), "wt", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    n_ctrl = sum(1 for r in rows if r["writer"] != "SATOSHI")
    print(f"pages {len(pages)}; posts in period {len(rows)} ({n_ctrl} control, {len(rows) - n_ctrl} Satoshi); control writers {len(ids)}; "
          f"last-edit stamps {len(edit_rows)}; parity equal {sum(1 for x in parity if x[3])} of {len(parity)}")

if __name__ == "__main__":
    main()
