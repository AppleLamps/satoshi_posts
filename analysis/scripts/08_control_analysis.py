#!/usr/bin/env python3
"""Offline control analysis from the committed per-post counts
(data/control/post_counts.csv.gz, built by 07_control_corpus.py).

Every feature is a ratio of summed additive counts, so a "sample" is a set of
whole posts whose words are pooled. Four comparisons, each with Satoshi's
posts from the same thread pages and the same cleaner:

  A  all text        : each writer's full text, writers with >= 500 words
  B  all text, equal : 25 random samples of whole posts totalling >= 1,000
                       words per writer (writer value = median of samples),
                       writers with >= 1,000 words
  C  declarative     : posts with no question of their own (roles answer +
                       statement), equal samples of >= 1,000 words
  D  answers         : posts that respond to a question and ask none, equal
                       samples of >= 500 words

Rate features are measured on samples (B-D) or full text (A). Two-way choices
(spelling, hyphenation, list style, ...) are measured on each writer's full
text within the comparison's role filter and require at least MIN_OPP uses of
either form. Rate features with a sparse denominator (spacing, contraction
choice, stance) require a minimum count in each sample; samples below it are
skipped and a writer needs at least half of the samples valid.

Thresholds are those fixed in revision 2 (CONTROL_CORPUS.md) and are not
re-tuned here. Satoshi's reposts of other members' text, and the two posts
whose other-member text only the archive's manual rules remove (post_10,
post_351), are excluded. Random seed fixed. Outputs:
  data/agg/control_population.csv     comparison A (one row per habit)
  data/agg/control_role_matched.csv   comparisons A-D (long format)
  data/agg/control_writer_features.csv anonymized per-writer values and
                                       opportunity counts for comparison A
  data/agg/control_summary.json       sizes, denominators, combined tests
"""
import csv, gzip, json, os, random, re, statistics
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
AGG = os.path.join(DATA, "agg")
SEED, K_SAMPLES, MIN_OPP = 20101212, 25, 3

rows = list(csv.DictReader(gzip.open(os.path.join(DATA, "control", "post_counts.csv.gz"), "rt", encoding="utf-8")))
NUM = [k for k in rows[0] if k not in ("writer", "date", "role", "text_sha256")]
for r in rows:
    for k in NUM:
        r[k] = int(r[k])
# exclude Satoshi's reposts of other members' text (archive rule R8)
excl = set()
for l in open(os.path.join(DATA, "posts_clean.jsonl"), encoding="utf-8"):
    rec = json.loads(l)
    m = re.search(r"msg(\d+)", rec.get("original_url") or "")
    # reposts, the disputed post, and the two posts whose other-member text is
    # removed only by manual archive rules (post_10 '>' lines, post_351 pasted
    # reports), since the shared page cleaner cannot remove it
    if m and any(f in rec["flags"] for f in ("repost_of_other_members", "disputed_authorship", "email_style_quote_lines", "manual_quote_split")):
        excl.add(int(m.group(1)))
rows = [r for r in rows if not (r["writer"] == "SATOSHI" and r["msg"] in excl)]

def ratio(a, b, minb=1):
    return a / b if b >= minb else None

# feature: (name, function(sum dict) -> value or None, Satoshi-like threshold text, predicate, kind)
RATE = [
    ("double_space_share", lambda s: ratio(s["double_space"], s["double_space"] + s["single_space"], 10), ">= 0.90", lambda v: v >= 0.90),
    ("contracted_share", lambda s: ratio(s["contracted_choice"], s["contracted_choice"] + s["full_choice"], 10), ">= 0.80", lambda v: v >= 0.80),
    ("if_per1k", lambda s: 1000 * s["if"] / s["words"], ">= 9", lambda v: v >= 9),
    ("if_you_openers_per1k", lambda s: 1000 * s["if_you_openers"] / s["words"], ">= 1.5", lambda v: v >= 1.5),
    ("it_would_be_per1k", lambda s: 1000 * s["it_would_be"] / s["words"], ">= 0.6", lambda v: v >= 0.6),
    ("verdict_openers_per1k", lambda s: 1000 * s["verdict_openers"] / s["words"], ">= 0.5", lambda v: v >= 0.5),
    ("hedge_share_of_stance", lambda s: ratio(s["hedges"], s["hedges"] + s["boosters"], 5), ">= 0.85", lambda v: v >= 0.85),
    ("semicolon_per1k", lambda s: 1000 * s["semicolon"] / s["words"], "<= 0.2", lambda v: v <= 0.2),
    ("em_en_dash_or_double_hyphen_per1k", lambda s: 1000 * (s["em_en_dash"] + s["double_hyphen"]) / s["words"], "<= 0.3", lambda v: v <= 0.3),
    ("exclaim_per1k", lambda s: 1000 * s["exclaim"] / s["words"], "<= 1.5", lambda v: v <= 1.5),
    ("mean_sentence_len", lambda s: ratio(s["words"], s["sentences"]), "(register-dependent)", None),
    ("you_per1k", lambda s: 1000 * s["you_group"] / s["words"], "(register-dependent)", None),
]
def choice(a, b, pred):
    return (lambda s: ratio(s[a], s[a] + s[b], MIN_OPP)), pred
BINARY = [
    ("block_chain_two_word_share", "term_block_chain", "term_blockchain", "= 1.0", lambda v: v == 1.0),
    ("double_spend_hyphen_share", "term_double_spend_hyphen", "term_double_spend_open", ">= 0.9", lambda v: v >= 0.9),
    ("proof_of_work_hyphen_share", "term_pow_hyphen", "term_pow_open", ">= 0.9", lambda v: v >= 0.9),
    ("e_mail_hyphen_share", "term_e_mail_hyphen", "term_email_solid", ">= 0.8", lambda v: v >= 0.8),
    ("OK_caps_share", "term_OK_caps", "term_okay", "= 1.0", lambda v: v == 1.0),
    ("etc_with_period_share", "term_etc_period", "term_etc_bare", "= 1.0", lambda v: v == 1.0),
    ("towards_share", "term_towards", "term_toward", ">= 0.75", lambda v: v >= 0.75),
    ("percent_sign_share", "percent_attached", "percent_word", "= 1.0", lambda v: v == 1.0),
    ("bullet_dash_share", "bullet_dash", "bullet_star", "= 1.0", lambda v: v == 1.0),
    ("numbered_paren_share", "list_num_paren", "list_num_dot", "= 1.0", lambda v: v == 1.0),
    ("logical_quotation_share", "quote_punct_outside", "quote_punct_inside", ">= 0.75", lambda v: v >= 0.75),
    ("non_us_spelling_share", "spelling_non_us", "spelling_us_only", ">= 0.75", lambda v: v >= 0.75),
]

def summed(posts):
    s = defaultdict(int)
    for p in posts:
        for k in NUM:
            s[k] += p[k]
    return s

def samples(posts, n_words, k, rng):
    """k samples of whole posts in random order until >= n_words."""
    out = []
    for _ in range(k):
        order = posts[:]; rng.shuffle(order)
        pick, w = [], 0
        for p in order:
            pick.append(p); w += p["words"]
            if w >= n_words:
                break
        out.append(summed(pick))
    return out

def pct_rank(value, values):
    if value is None or not values:
        return None
    return round(100 * sum(1 for v in values if v < value) / len(values) + 50 * sum(1 for v in values if v == value) / len(values), 1)

COMPARISONS = [
    ("A all text", lambda r: True, 500, None),
    ("B all text, equal samples", lambda r: True, 1000, 1000),
    ("C declarative posts, equal samples", lambda r: r["role"] in ("answer", "statement"), 1000, 1000),
    ("D answers to questions, equal samples", lambda r: r["role"] == "answer", 500, 500),
]

def main():
    rng = random.Random(SEED)
    by_w = defaultdict(list)
    for r in rows:
        by_w[r["writer"]].append(r)
    long_rows, summary, writer_rows = [], dict(seed=SEED, samples_per_writer=K_SAMPLES, min_opportunities=MIN_OPP, comparisons={}), []
    for cname, filt, min_words, sample_words in COMPARISONS:
        sel = {w: [p for p in ps if filt(p)] for w, ps in by_w.items()}
        sel = {w: ps for w, ps in sel.items() if sum(p["words"] for p in ps) >= min_words}
        sat_posts = sel.get("SATOSHI", [])
        ctrl = {w: ps for w, ps in sel.items() if w != "SATOSHI"}
        summary["comparisons"][cname] = dict(min_words=min_words, sample_words=sample_words, eligible_control_writers=len(ctrl),
                                             satoshi_posts=len(sat_posts), satoshi_words=sum(p["words"] for p in sat_posts),
                                             control_posts=sum(len(v) for v in ctrl.values()), control_words=sum(p["words"] for v in ctrl.values() for p in v))
        # rate features
        def writer_value(ps, fn, k=K_SAMPLES):
            if sample_words is None:
                return fn(summed(ps)), None
            vals = [fn(s) for s in samples(ps, sample_words, k, rng)]
            vals = [v for v in vals if v is not None]
            if len(vals) < k / 2:
                return None, None
            return statistics.median(vals), vals
        for name, fn, cond, pred in RATE:
            sv, svals = writer_value(sat_posts, fn, k=200 if sample_words else K_SAMPLES)
            cv = {w: writer_value(ps, fn)[0] for w, ps in ctrl.items()}
            vs = sorted(v for v in cv.values() if v is not None)
            n_like = sum(1 for v in vs if pred(v)) if pred else None
            long_rows.append(dict(comparison=cname, habit=name, kind="rate", satoshi_value=round(sv, 3) if sv is not None else None,
                                  satoshi_sample_p10=round(sorted(svals)[len(svals) // 10], 3) if svals else None,
                                  satoshi_sample_p90=round(sorted(svals)[9 * len(svals) // 10], 3) if svals else None,
                                  satoshi_like_if=cond, writers_with_opportunity=len(vs), writers_satoshi_like=n_like,
                                  share_satoshi_like=round(n_like / len(vs), 3) if pred and vs else None,
                                  satoshi_percentile=pct_rank(sv, vs), control_median=round(statistics.median(vs), 3) if vs else None,
                                  control_q1=round(vs[len(vs) // 4], 3) if vs else None, control_q3=round(vs[3 * len(vs) // 4], 3) if vs else None))
            if cname.startswith("A"):
                for w, v in cv.items():
                    writer_rows.append((w, name, round(v, 4) if v is not None else None))
        # two-way choices on full role-filtered text
        for name, a_, b_, cond, pred in BINARY:
            fn = lambda s: ratio(s[a_], s[a_] + s[b_], MIN_OPP)
            sat_s = summed(sat_posts); sv = fn(sat_s)
            cvals, opps = {}, {}
            for w, ps in ctrl.items():
                s = summed(ps); opps[w] = s[a_] + s[b_]; cvals[w] = fn(s)
            vs = sorted(v for v in cvals.values() if v is not None)
            n_like = sum(1 for v in vs if pred(v))
            long_rows.append(dict(comparison=cname, habit=name, kind=f"two-way choice, >= {MIN_OPP} uses", satoshi_value=round(sv, 3) if sv is not None else None,
                                  satoshi_sample_p10=None, satoshi_sample_p90=None, satoshi_like_if=cond, writers_with_opportunity=len(vs),
                                  writers_satoshi_like=n_like, share_satoshi_like=round(n_like / len(vs), 3) if vs else None,
                                  satoshi_percentile=pct_rank(sv, vs), control_median=round(statistics.median(vs), 3) if vs else None,
                                  control_q1=round(vs[len(vs) // 4], 3) if vs else None, control_q3=round(vs[3 * len(vs) // 4], 3) if vs else None))
            if cname.startswith("A"):
                for w in ctrl:
                    writer_rows.append((w, name, round(cvals[w], 4) if cvals[w] is not None else None))
                    writer_rows.append((w, name + "__opportunities", opps[w]))
    fields = list(long_rows[0].keys())
    with open(os.path.join(AGG, "control_role_matched.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(long_rows)
    with open(os.path.join(AGG, "control_population.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows([r for r in long_rows if r["comparison"].startswith("A")])
    # anonymized per-writer table (comparison A): words, posts by role, feature values, opportunity counts
    wide = defaultdict(dict)
    for wid, k, v in writer_rows:
        wide[wid][k] = v
    for wid, ps in by_w.items():
        if wid in wide:
            wide[wid].update(posts=len(ps), words=sum(p["words"] for p in ps),
                             **{f"words_{role}": sum(p["words"] for p in ps if p["role"] == role) for role in ("answer", "statement", "question")})
    cols = ["writer", "posts", "words", "words_answer", "words_statement", "words_question"] + sorted({k for d in wide.values() for k in d} - {"posts", "words", "words_answer", "words_statement", "words_question"})
    with open(os.path.join(AGG, "control_writer_features.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(cols)
        for wid in sorted(wide):
            w.writerow([wid] + [wide[wid].get(c) for c in cols[1:]])
    # population totals and combined tests (comparison A, as in revision 2)
    ctrl_all = [r for r in rows if r["writer"] != "SATOSHI"]
    summary.update(control_posts=len(ctrl_all), control_writers=len({r["writer"] for r in ctrl_all}), control_words=sum(r["words"] for r in ctrl_all),
                   satoshi_posts=len(by_w["SATOSHI"]), satoshi_words=sum(r["words"] for r in by_w["SATOSHI"]))
    A = {(r["habit"]): r for r in long_rows if r["comparison"].startswith("A")}
    elig = {w: summed(ps) for w, ps in by_w.items() if w != "SATOSHI" and sum(p["words"] for p in ps) >= 500}
    preds = {n: (f, p) for n, f, c, p in RATE if p}
    def combined(names):
        meas = [w for w, s in elig.items() if all(preds[n][0](s) is not None for n in names)]
        return dict(habits=names, writers_measurable=len(meas), writers_matching_all=sum(1 for w in meas if all(preds[n][1](preds[n][0](elig[w])) for n in names)))
    summary["combined_tests_A"] = {"punctuation_and_spacing": combined(["double_space_share", "semicolon_per1k", "em_en_dash_or_double_hyphen_per1k", "exclaim_per1k", "contracted_share"]),
                                   "most_distinctive_frequent": combined(["double_space_share", "contracted_share", "if_per1k", "if_you_openers_per1k"])}
    json.dump(summary, open(os.path.join(AGG, "control_summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for r in long_rows:
        print(f"{r['comparison'][:2]} {r['habit']:36s} sat={str(r['satoshi_value']):7s} [{r['satoshi_sample_p10']},{r['satoshi_sample_p90']}] n={r['writers_with_opportunity']:4d} like={r['writers_satoshi_like']} share={r['share_satoshi_like']} pct={r['satoshi_percentile']} med={r['control_median']}")

if __name__ == "__main__":
    main()
