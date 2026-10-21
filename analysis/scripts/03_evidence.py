#!/usr/bin/env python3
"""Locate verbatim examples for each finding in the ORIGINAL repository files
and write analysis/evidence.csv.

Every row gives: finding id, finding label, repo path, 1-based line number,
1-based column of the first character of the quoted span in that line, the
exact text as it appears in the repository file (U+00A0 non-breaking spaces are
written as the two characters "\\xa0" so the CSV is readable; the verifier
re-expands them), 80 characters of context on each side, platform, timestamp,
and the per-finding corpus statistics (count / posts / per 1,000 words) that
the report cites.

Matching is done on the author's own prose (posts_clean.jsonl segments of type
"own"), i.e. quotes, code and other people's text are never used as evidence.
The matched span is then re-located in the raw file with whitespace made
flexible (the scraper collapsed block boundaries), so the quoted text is
always a literal substring of the repo file.
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textutil as T
import measures as M

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.join(HERE, "..", "data")
recs = [json.loads(l) for l in open(os.path.join(DATA, "posts_clean.jsonl"), encoding="utf-8")]
raw = {r["post_id"]: open(os.path.join(ROOT, r["file"]), encoding="utf-8").read() for r in recs}
core = [r for r in recs if r["usable_for_prose_stats"] and "disputed_authorship" not in r["flags"] and "repost_of_other_members" not in r["flags"]]
N_WORDS = sum(len(T.words("\n".join(s["text"] for s in r["segments"] if s["type"] == "own"))) for r in core)

def prose(r):
    return "\n".join(s["text"] for s in r["segments"] if s["type"] == "own")

def locate(pid, span):
    """Find `span` (from the HTML-derived prose) in the raw repo file, allowing
    any whitespace run (incl. none) where the span has whitespace, and U+00A0
    for spaces. Returns (line, col, exact_text) or None."""
    text = raw[pid]
    parts = [re.escape(p) for p in re.split(r"\s+", span.strip()) if p]
    if not parts:
        return None
    pat = re.compile(r"[\s\u00a0]*".join(parts))
    # search only in the body (line 6 onwards) so a title never serves as evidence
    body_start = len("\n".join(text.split("\n")[:5])) + 1
    m = pat.search(text, body_start)
    if not m:
        return None
    line = text.count("\n", 0, m.start()) + 1
    col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
    return line, col, text[m.start():m.end()], text[max(0, m.start() - 80):m.start()], text[m.end():m.end() + 80]

# finding_id, label, regex (applied to own prose; flags), max examples, restrict platform or None, stat note
FINDINGS = [
    ("F01", "Two spaces after sentence-final punctuation (BitcoinTalk; stored by the forum as NBSP+space)", r"[a-z0-9)\"'][.!?]  [A-Z\"(]", 8, "Bitcointalk"),
    ("F02", "Single space after sentence-final punctuation in P2P Foundation posts (platform collapsed whitespace; original form not established)", r"[a-z][.!?] [A-Z]", 4, "P2P Foundation"),
    ("F03", "Heavy use of contractions (it's, don't, I'm, you're, it'll, there's)", r"\b(?:it'll|there's|you're|doesn't|I'm|can't|it's|don't|that's|won't)\b", 10, None),
    ("F04", "Conditional-politeness frame 'It would be' / 'would be nice'", r"\b[Ii]t would be\b[^.\n]{0,60}", 8, None),
    ("F05", "Sentence-initial 'If you' second-person conditional", r"(?:^|(?<=[.!?]\s)|(?<=[.!?]\s\s)|(?<=\n))If you\b[^.\n]{0,70}", 8, None),
    ("F06", "Hedges 'I think' and 'I'm not sure'", r"\b(?:I think|I'm not sure|I don't think|I guess)\b[^.\n]{0,60}", 10, None),
    ("F07", "One-word verdict openers 'Right,' 'Yes,' 'No,' 'True,' 'OK,' 'Nope.'", r"(?:^|(?<=\n))(?:Right|Yes|No|True|OK|Nope|Not really)[,.][^\n]{0,60}", 12, None),
    ("F08", "Politeness formulas 'Thanks' / 'Sorry' / 'please'", r"(?:(?:^|(?<=\n))Sorry[^\n]{0,60}|\bThanks(?: for [^.\n]{0,40})?[!.]|\b[Pp]lease (?:test|upgrade|report|post|let me know)[^.\n]{0,40})", 10, None),
    ("F09", "Logical punctuation: period or comma placed outside closing quotation mark", r"\"[^\"\n]{1,40}\"[.,]", 10, None),
    ("F09b", "Full-sentence quotation with period inside the closing quotation mark (the exceptions)", r"[a-z]{3,}[.!?]\"(?=\s|$)", 6, None),
    ("F10", "Numbered lists with '1)' style and bullet lists with '- '", r"(?m)^\s*(?:\d\)|- )[^\n]{3,60}", 10, None),
    ("F11", "Semicolon in prose (very rare: 3 in the whole corpus)", r"[^;\n]{30};[^;\n]{30}", 5, None),
    ("F12", "Double hyphen used as a dash (no em dash anywhere)", r"[^-\n]{20}(?<!-)--(?!-)[^-\n]{20}", 6, None),
    ("F13", "Ellipsis for trailing thought", r"[^.\n]{20}\.{3}[^.\n]{0,25}", 8, None),
    ("F14", "Exclamation marks concentrated in release announcements and thanks", r"[^!\n]{25}![^\n]{0,10}", 10, None),
    ("F15", "Non-US spellings (-ise/-isation/-yse, -our, grey, defence, maths, labelled, fulfil)", r"(?<![A-Za-z])(?:optimisation|optimised|colour|grey|favour|neighbour|defence|labelled|labelling|fulfil|maths|analysed|formalised|prioritising|amortised|reorganised|modernised|liberalising|decentralised)(?![A-Za-z])", 40, None),
    ("F16", "-ize forms (American or Oxford British) and US-only forms (color, gotten)", r"(?<![A-Za-z])(?:color|realize|realized|criticized|optimized|optimization|optimizations|decentralized|gotten|generalizes|standardized|standardizing|summarize|recognize|serialize|serialization|internationalization|minimized|initialize)(?![A-Za-z])", 40, None),
    ("F17", "'towards' preferred over 'toward'", r"\b(?:towards|toward)\b", 12, None),
    ("F18", "Misspellings and slips", r"(?<![A-Za-z'])(?:walkthough|idealogical|easer|Allright|filewall|generateds|divy|moreso|lets go|lets say)(?![A-Za-z])", 12, None),
    ("F19", "Term formation: 'block chain' as two words, hyphenated 'double-spend' and 'proof-of-work', lower-case 'bitcoin'", r"\b(?:block chain|double-spend\w*|proof-of-work|e-mail)\b", 14, None),
    ("F20", "Currency unit: 'bc' in 2009-Feb 2010, 'BTC' from May 2010", r"\b\d[\d,.]*\s?(?:bc|BTC)\b", 12, None),
    ("F21", "Upper-case acronyms (TOR, SVN, IRC, CPU, JSON-RPC) and 'SVN rev N' formula", r"\b(?:TOR|SVN rev \d+|IRC|JSON-RPC|CPU)\b[^\n]{0,40}", 12, None),
    ("F22", "Idioms and analogies", r"\b(?:in a nutshell|think of it as|wet blanket|eat crow|hornet's nest|bogged down|out the door|up to speed|brute force|thought experiment|To use an analogy)\b[^\n]{0,50}", 12, None),
    ("F24", "Parenthetical asides, often as stand-alone sentences", r"(?:(?<=[.!?]\s)|(?<=[.!?]\s\s)|(?<=\n))\([^()\n]{8,80}\)", 10, None),
    ("F25", "Post-hoc 'Edit:' / 'Update:' markers", r"(?:^|(?<=\n))(?:Edit|Update|edit):[^\n]{0,60}", 6, None),
    ("F26", "Instructional second person 'you can' / 'you need to'", r"\b[Yy]ou (?:can|need to|should|could|have to|don't need to)\b[^.\n]{0,50}", 10, None),
    ("F27", "Release-note template: 'Version X is now available', 'Changes:', 'Download:', 'I uploaded ... to SVN'", r"(?:(?:^|(?<=\n))Version [\d.]+(?: rc\d)? is now available[^\n]*|(?:^|(?<=\n))(?:Changes|Download|Downloads|Note|Builds):\s*|\bI uploaded [^.\n]{0,60}SVN[^.\n]{0,30})", 12, None),
    ("F28", "Interjections are rare (Hmm, Sigh, Hurray)", r"\b(?:Hmm|Sigh|Hurray|Heh)\b[^\n]{0,40}", 5, None),
    ("F29", "Case-preserving: identifiers keep lower case at sentence start", r"[.!?]  [a-z][A-Za-z0-9_.]*[^\n]{0,40}", 8, None),
    ("F30", "Verdict fragments and very short sentences", r"(?:(?<=[.!?]\s\s)|(?<=\n))(?:Nope|Probably|Good idea|Not yet|Agreed|That works|Good catch|Good question|Sounds good|Nice|Cool|Correct|Exactly)[.!,][^\n]{0,40}", 10, None),
    ("F31", "Numbers: '%' attached without space, 'Nx' multipliers, few thousands separators", r"\b\d+(?:\.\d+)?(?:%|x)(?![A-Za-z])[^\n]{0,30}", 10, None),
    ("F33", "'a lot' always two words; 'OK' always upper case", r"\b(?:a lot|OK)\b[^\n]{0,30}", 8, None),
    ("F34", "Sentence-initial 'Also,' / 'Then' / 'Anyway' are rare; preferred connectives 'but', 'so', 'then'", r"(?:(?<=[.!?]\s\s)|(?<=\n))(?:Also|Anyway|Then|So|But|Otherwise|Instead|Unless|Although)[, ][^\n]{0,50}", 10, None),
    ("F35", "Future-tense self-commitments 'I'll ...'", r"\bI'll (?:add|fix|look|post|try|put|have|make|change|check|get|see|think|be|do|update|write|take|work|go)\b[^.\n]{0,50}", 10, None),
    ("F36", "Passive constructions (moderate; 'is designed', 'was merged', 'be trusted')", r"\b(?:is|are|was|were|be|been)\s+(?:not\s+)?(?:designed|merged|trusted|needed|required|accepted|rejected|released|uploaded|fixed|confirmed|included|spent|sent|received|broadcast|checked|stored|generated|found|intended|limited)\b[^.\n]{0,40}", 10, None),
]

# Where measures.py defines the feature, the reported count comes from that
# canonical function (so the report, post_features.csv and the validation
# tables agree); the regex above is then used only to pick examples.
CANONICAL = {
    "F01": lambda t: M.sentence_spacing(t)[0],
    "F05": lambda t: M.if_you_openers(t)[0],
    "F07": M.verdict_openers,
    "F09": lambda t: M.quote_punctuation(t)[0],
    "F09b": lambda t: M.quote_punctuation(t)[1],
    "F10": lambda t: M.list_lines(t)["num_paren"] + M.list_lines(t)["bullet_dash"],
    "F15": lambda t: len(M.spelling(t)["non_us"]),
    "F16": lambda t: len(M.spelling(t)["ize"]) + len(M.spelling(t)["us_only"]) + len(M.spelling(t)["gotten"]),
    "F06": lambda t: sum(M.lexicon_counts(t, "hedges")[k] for k in ("I think", "I'm not sure", "I don't think", "I guess")),
}
rows = []
summary = {}
for fid, label, pat, maxn, platform in FINDINGS:
    rx = re.compile(pat)
    total, docs, examples = 0, 0, []
    for r in core:
        if platform and r["platform"] != platform:
            continue
        pr = prose(r)
        ms = list(rx.finditer(pr))
        k = CANONICAL[fid](pr) if fid in CANONICAL else len(ms)
        if k:
            total += k; docs += 1
        if not ms:
            continue
        for m in ms:
            examples.append((r, m.group(0)))
    # spread examples across the corpus: take evenly spaced picks
    picks = []
    if examples:
        step = max(1, len(examples) // maxn)
        picks = examples[::step][:maxn]
    stat = f"count={total}; posts={docs}; per1k_words={1000*total/N_WORDS:.2f}" if not platform else f"count={total}; posts={docs} (platform={platform})"
    if fid in CANONICAL:
        stat += "; count from measures.py"
    summary[fid] = (label, total, docs)
    for r, span in picks:
        loc = locate(r["post_id"], span)
        if loc is None:
            rows.append(dict(finding_id=fid, finding=label, file=r["file"], line="", col="", quote=span.replace("\u00a0", "\\xa0"), context_before="", context_after="", platform=r["platform"], timestamp=r["timestamp"], stats=stat, note="NOT LOCATED IN RAW FILE"))
            continue
        line, col, exact, before, after = loc
        rows.append(dict(finding_id=fid, finding=label, file=r["file"], line=line, col=col,
                         quote=exact.replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         context_before=before.replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         context_after=after.replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         platform=r["platform"], timestamp=r["timestamp"], stats=stat, note=""))

# non-prose evidence rows (exclusions / anomalies) quoted from raw files
EXTRA = [
    ("X01", "Repost posts contain other members' text (excluded from author statistics)", [5, 6, 9, 11], r"--------------------\s*[A-Za-z0-9_-]+:"),
    ("X02", "E-mail style '>' quoting of another member in post_10 (excluded)", [10], r"> Can nodes on the network tell"),
    ("X03", "Pasted benchmark reports attributed to other members in post_351 (excluded)", [351], r"aceat64:\s*My system went from"),
    ("X04", "Disputed 2014 post (excluded; archive timestamp is a placeholder, source gives 2014-03-07T01:17Z)", [543], r"I am not Dorian Nakamoto\."),
    ("X05", "Forum quote header merged into prose by the scraper (shows why quotes had to be re-segmented)", [60, 15, 300], r"Quote from: [^\n]{0,60}"),
    ("X06", "Signature in P2P Foundation post merged with the URL by the scraper", [1], r"Satoshi Nakamotohttp://www\.bitcoin\.org"),
    ("X07", "Non-breaking space encoding of the double space in the raw file", [60, 400], r"[a-z]\.\u00a0 [A-Z][a-z]+"),
    ("X08", "Merged paragraph boundary (no space between sentences) produced by the scraper, not the author", [1, 2], r"[a-z]\.[A-Z][a-z]+ [a-z]+"),
]
for fid, label, pids, pat in EXTRA:
    rx = re.compile(pat)
    for pid in pids:
        text = raw[pid]
        m = rx.search(text)
        if not m:
            continue
        line = text.count("\n", 0, m.start()) + 1
        col = m.start() - (text.rfind("\n", 0, m.start()) + 1) + 1
        r = next(x for x in recs if x["post_id"] == pid)
        rows.append(dict(finding_id=fid, finding=label, file=r["file"], line=line, col=col,
                         quote=text[m.start():m.end()].replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         context_before=text[max(0, m.start() - 80):m.start()].replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         context_after=text[m.end():m.end() + 80].replace("\u00a0", "\\xa0").replace("\n", "\\n"),
                         platform=r["platform"], timestamp=r["timestamp"], stats="", note="raw-file evidence (not author prose)"))

# drop duplicate locations
seen, dedup = set(), []
for r in rows:
    key = (r["finding_id"], r["file"], r["line"], r["col"])
    if key in seen:
        continue
    seen.add(key); dedup.append(r)
rows = dedup
with open(os.path.join(HERE, "..", "evidence.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump({k: dict(label=v[0], count=v[1], posts=v[2]) for k, v in summary.items()}, open(os.path.join(DATA, "agg", "finding_counts.json"), "w"), indent=1)
print(len(rows), "evidence rows;", sum(1 for r in rows if r["note"].startswith("NOT")), "not located")
for k, v in summary.items():
    print(k, v[1], v[2], v[0][:70])
