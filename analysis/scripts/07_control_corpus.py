#!/usr/bin/env python3
"""Same-forum, same-period control corpus: how common is each fingerprint
habit among the other people writing in the same BitcoinTalk threads in
2009-11 .. 2010-12?

Input : cached thread pages from 06_fetch_forum_threads.py (--cache DIR)
Output: data/agg/control_population.csv   one row per tested habit
        data/agg/control_summary.json      corpus sizes and combined tests
        data/forum_last_edit.csv           BitcoinTalk "Last edit" stamps for
                                           the archived Satoshi posts (used by
                                           02_features.py for the edited-post
                                           sensitivity check)

Control text is cleaned with the same rules as the Satoshi prose: quote
blocks, quote headers, code blocks, images and signatures are removed, <br>
becomes a newline, U+00A0 becomes a space (R2), and code-looking lines are
removed with the CODE_LINE_RE of 01_extract.py (R12). Posts by the account
'satoshi' are excluded. Only posts dated 2009-11-01 .. 2010-12-31 are used.

Writers are compared only at the population level. A writer enters the
per-writer distributions with at least MIN_WORDS words; for a two-way choice
(e.g. 'block chain' vs 'blockchain') only writers who used either form count.
No output names or ranks individual control writers.
"""
import argparse, csv, glob, json, os, re, statistics, sys
from collections import defaultdict
from bs4 import BeautifulSoup
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textutil as T
import measures as M

src = open(os.path.join(HERE, "01_extract.py"), encoding="utf-8").read()
CODE_LINE_RE = eval(src.split("CODE_LINE_RE = ", 1)[1].split("\n", 1)[0])
MIN_WORDS = 500
MONTHS = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}

def parse_date(s):
    m = re.search(r"(\w+) (\d{2}), (\d{4}), (\d{2}):(\d{2}):(\d{2}) (AM|PM)", s)
    if not m or m.group(1) not in MONTHS:
        return None
    h = int(m.group(4)) % 12 + (12 if m.group(7) == "PM" else 0)
    return f"{m.group(3)}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d} {h:02d}:{m.group(5)}:{m.group(6)}"

def clean_post(div):
    for sel in ["div.quoteheader", "div.quote", "div.codeheader", "div.code", "img", "div.signature"]:
        for x in div.select(sel):
            x.decompose()
    for br in div.find_all("br"):
        br.replace_with("\n")
    text = div.get_text().replace(" ", " ")
    lines = [l for l in text.split("\n") if not CODE_LINE_RE.match(l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

def parse_pages(cache):
    posts = {}
    for f in sorted(glob.glob(os.path.join(cache, "t*_*.html"))):
        s = BeautifulSoup(open(f, encoding="latin-1").read(), "html.parser")
        for td in s.select("td.td_headerandpost"):
            subj = td.select_one("div.subject")
            mid = re.search(r"subject_(\d+)", subj.get("id", "")) if subj else None
            body = td.select_one("div.post")
            if not mid or body is None:
                continue
            row = td.find_parent("tr")
            pi = row.select_one("td.poster_info") if row else None
            author = pi.find("b").get_text(strip=True) if pi and pi.find("b") else None
            date = parse_date(td.select_one("div.smalltext").get_text(" ", strip=True)) if td.select_one("div.smalltext") else None
            ed = td.select_one("span.edited")
            last_edit = parse_date(ed.get("title", "")) if ed and "Last edit" in ed.get("title", "") else None
            edited_by = re.search(r" by (.+)$", ed.get("title", "")).group(1) if ed and " by " in ed.get("title", "") else None
            posts[int(mid.group(1))] = dict(msg=int(mid.group(1)), author=author, date=date, last_edit=last_edit, edited_by=edited_by, text=clean_post(body))
    return posts

def pct_rank(value, values):
    if value is None or not values:
        return None
    return round(100 * sum(1 for v in values if v < value) / len(values) + 50 * sum(1 for v in values if v == value) / len(values), 1)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); a = ap.parse_args()
    posts = parse_pages(a.cache)
    # ------------------------------------------------ last-edit stamps of the archived Satoshi posts
    recs = {json.loads(l)["post_id"]: json.loads(l) for l in open(os.path.join(HERE, "..", "data", "posts_clean.jsonl"), encoding="utf-8")}
    edit_rows = []
    for pid in sorted(recs):
        m = re.search(r"msg(\d+)", recs[pid].get("original_url") or "")
        if m and int(m.group(1)) in posts:
            p = posts[int(m.group(1))]
            if p["last_edit"]:
                edit_rows.append((pid, recs[pid]["timestamp"], p["date"], p["last_edit"], p["edited_by"]))
    with open(os.path.join(HERE, "..", "data", "forum_last_edit.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["post_id", "archive_timestamp", "forum_posted", "forum_last_edit", "edited_by"]); w.writerows(edit_rows)
    # ------------------------------------------------ control writers
    by_writer = defaultdict(list)
    for p in posts.values():
        if not p["author"] or p["author"].lower() == "satoshi" or not p["date"]:
            continue
        if not ("2009-11-01" <= p["date"][:10] <= "2010-12-31"):
            continue
        if T.words(p["text"]):
            by_writer[p["author"]].append(p["text"])
    eligible = {w: docs for w, docs in by_writer.items() if sum(len(T.words(d)) for d in docs) >= MIN_WORDS}
    prof = {w: M.profile(docs) for w, docs in eligible.items()}
    pooled = M.profile([d for docs in by_writer.values() for d in docs])
    # Satoshi reference: BitcoinTalk core prose (same platform as the control)
    core = [r for r in recs.values() if r["usable_for_prose_stats"] and "disputed_authorship" not in r["flags"] and "repost_of_other_members" not in r["flags"] and r["platform"] == "Bitcointalk"]
    sat = M.profile(["\n".join(s["text"] for s in r["segments"] if s["type"] == "own") for r in core])

    def share(p, a_, b_):
        x, y = p[a_], p[b_]
        return round(x / (x + y), 3) if (x + y) else None
    TESTS = [  # name, function(profile) -> value or None, Satoshi-like condition description, predicate
        ("double_space_share", lambda p: p["double_space_share"] if (p["double_space"] + p["single_space"]) >= 10 else None, ">= 0.90", lambda v: v >= 0.90),
        ("semicolon_per1k", lambda p: p["semicolon_per1k"], "<= 0.2", lambda v: v <= 0.2),
        ("em_en_dash_or_double_hyphen_per1k", lambda p: round(1000 * (p["em_en_dash"] + p["double_hyphen"]) / p["words"], 2), "<= 0.3", lambda v: v <= 0.3),
        ("exclaim_per1k", lambda p: p["exclaim_per1k"], "<= 1.5", lambda v: v <= 1.5),
        ("contracted_share", lambda p: p["contracted_share"] if p["contracted_share"] is not None else None, ">= 0.80", lambda v: v >= 0.80),
        ("if_per1k", lambda p: p["if_per1k"], ">= 9", lambda v: v >= 9),
        ("if_you_openers_per1k", lambda p: round(1000 * p["if_you_openers"] / p["words"], 2), ">= 1.5", lambda v: v >= 1.5),
        ("it_would_be_per1k", lambda p: round(1000 * p["it_would_be"] / p["words"], 2), ">= 0.6", lambda v: v >= 0.6),
        ("hedge_share_of_stance", lambda p: round(p["hedges"] / (p["hedges"] + p["boosters"]), 3) if p["hedges"] + p["boosters"] >= 5 else None, ">= 0.85", lambda v: v >= 0.85),
        ("verdict_openers_per1k", lambda p: round(1000 * p["verdict_openers"] / p["words"], 2), ">= 0.5", lambda v: v >= 0.5),
        ("block_chain_two_word_share", lambda p: share(p, "term_block_chain", "term_blockchain"), "= 1.0", lambda v: v == 1.0),
        ("double_spend_hyphen_share", lambda p: share(p, "term_double_spend_hyphen", "term_double_spend_open"), ">= 0.9", lambda v: v >= 0.9),
        ("proof_of_work_hyphen_share", lambda p: share(p, "term_pow_hyphen", "term_pow_open"), ">= 0.9", lambda v: v >= 0.9),
        ("e_mail_hyphen_share", lambda p: share(p, "term_e_mail_hyphen", "term_email_solid"), ">= 0.8", lambda v: v >= 0.8),
        ("OK_caps_share", lambda p: share(p, "term_OK_caps", "term_okay"), "= 1.0", lambda v: v == 1.0),
        ("etc_with_period_share", lambda p: share(p, "term_etc_period", "term_etc_bare"), "= 1.0", lambda v: v == 1.0),
        ("towards_share", lambda p: share(p, "term_towards", "term_toward"), ">= 0.75", lambda v: v >= 0.75),
        ("percent_sign_share", lambda p: share(p, "percent_attached", "percent_word"), "= 1.0", lambda v: v == 1.0),
        ("bullet_dash_share", lambda p: share(p, "bullet_dash", "bullet_star"), "= 1.0", lambda v: v == 1.0),
        ("numbered_paren_share", lambda p: share(p, "list_num_paren", "list_num_dot"), "= 1.0", lambda v: v == 1.0),
        ("logical_quotation_share", lambda p: share(p, "quote_punct_outside", "quote_punct_inside"), ">= 0.75", lambda v: v >= 0.75),
        ("non_us_spelling_share", lambda p: round(p["spelling_non_us"] / (p["spelling_non_us"] + p["spelling_us_only"]), 3) if p["spelling_non_us"] + p["spelling_us_only"] else None, ">= 0.75", lambda v: v >= 0.75),
        ("mean_sentence_len", lambda p: p["mean_sentence_len"], "(no threshold; register-dependent)", None),
        ("you_per1k", lambda p: p["you_per1k"], "(no threshold; register-dependent)", None),
    ]
    rows, match_sets = [], defaultdict(set)
    for name, fn, cond, pred in TESTS:
        sv = fn(sat)
        vals = {w: fn(p) for w, p in prof.items()}
        vals = {w: v for w, v in vals.items() if v is not None}
        vs = sorted(vals.values())
        pv = fn(pooled)
        n_match = sum(1 for v in vs if pred(v)) if pred else None
        if pred:
            match_sets[name] = {w for w, v in vals.items() if pred(v)}
        rows.append(dict(habit=name, satoshi_value=sv, satoshi_like_if=cond, control_pooled_value=pv,
                         writers_with_opportunity=len(vs), writers_satoshi_like=n_match,
                         share_satoshi_like=round(n_match / len(vs), 3) if pred and vs else None,
                         satoshi_percentile_among_writers=pct_rank(sv, vs),
                         control_min=vs[0] if vs else None, control_q1=vs[len(vs) // 4] if vs else None,
                         control_median=statistics.median(vs) if vs else None, control_q3=vs[3 * len(vs) // 4] if vs else None,
                         control_max=vs[-1] if vs else None))
    with open(os.path.join(HERE, "..", "data", "agg", "control_population.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    # combined tests: how many eligible writers show a set of habits together
    def combined(names):
        meas = [w for w in prof if all(fn(prof[w]) is not None for n, fn, c, p in TESTS if n in names)]
        return len(meas), sum(1 for w in meas if all(w in match_sets[n] for n in names))
    COMBOS = {"punctuation_and_spacing": ["double_space_share", "semicolon_per1k", "em_en_dash_or_double_hyphen_per1k", "exclaim_per1k", "contracted_share"],
              "most_distinctive_frequent": ["double_space_share", "contracted_share", "if_per1k", "if_you_openers_per1k"]}
    combos = {k: dict(habits=v, writers_measurable=combined(v)[0], writers_matching_all=combined(v)[1]) for k, v in COMBOS.items()}
    summary = dict(control_posts=sum(len(v) for v in by_writer.values()), control_writers=len(by_writer),
                   control_words=sum(len(T.words(d)) for v in by_writer.values() for d in v),
                   eligible_writers=len(eligible), min_words=MIN_WORDS, satoshi_words=sat["words"],
                   combined_tests=combos,
                   satoshi_last_edit_stamps=len(edit_rows))
    json.dump(summary, open(os.path.join(HERE, "..", "data", "agg", "control_summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for r in rows:
        print(f"{r['habit']:36s} sat={str(r['satoshi_value']):7s} pooled={str(r['control_pooled_value']):7s} n={r['writers_with_opportunity']:4d} like={r['writers_satoshi_like']} share={r['share_satoshi_like']} pct={r['satoshi_percentile_among_writers']}")

if __name__ == "__main__":
    main()
