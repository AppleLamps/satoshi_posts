#!/usr/bin/env python3
"""Parse the repository's posts/*.txt files into raw and cleaned records.

Outputs (all under analysis/data/):
  posts_raw.jsonl      one record per file: header fields + the untouched body
                       text, with the 1-based line number where the body starts
  posts_clean.jsonl    the same posts split into typed segments
                       (own / quoteheader / quote / code / signature) with the
                       author's own prose isolated and paragraph breaks restored
                       where the original form could be established
  extraction_log.csv   per-file coverage, alignment status and flags

Extraction rules (documented in analysis/README.md):
  R1  File layout: line 1 = title, line 3 = platform, line 5 = timestamp
      "YYYY-MM-DD HH:MM:SS UTC - Original Post"; the body starts on line 6
      (two leading spaces added by the scraper are stripped).  post_475.txt is
      the only file whose body spans more than one line.
  R2  U+00A0 (non-breaking space) is converted to an ordinary space.  The
      forum stored double spaces as "&nbsp; ", so this conversion restores the
      author's two-space sentence spacing (verified against the source HTML).
  R3  Block structure is recovered by aligning the repo body with the live
      source HTML (analysis/data/sni_posts.jsonl, see 00_fetch_source_html.py).
      The alignment is accepted only when the two texts are identical once all
      whitespace is removed ("exact"; the scraper dropped whitespace at block
      boundaries so only non-space characters can be compared), or differ by a
      tiny edit-distance ratio >= 0.98 ("approx", every difference is logged).
      Otherwise the post keeps the repo-only heuristic segmentation and is
      flagged ("heuristic").
  R4  Quote blocks (div.quote and div.quoteheader, nested quotes included) are
      labelled quote/quoteheader and excluded from the author's prose.  The
      text that the author wrote inside a quoteheader is never his own prose
      ("Quote from: X on <date>" is forum-generated).
  R5  <br> inside the author's own prose becomes a newline; two consecutive
      newlines are a paragraph break.  Code blocks (div.code / the old site's
      "Code:" label) are labelled code.
  R6  The P2P Foundation signature "Satoshi Nakamoto" + "http://www.bitcoin.org"
      at the end of the body is labelled signature.
  R7  Heuristic fallback (no HTML alignment): "Quote from: <name> on <Month>
      <d>, <yyyy>, <hh:mm:ss AM/PM>" and bare "Quote" headers are detected by
      regex; the end of the quoted text cannot be located, so the whole post is
      flagged quote_boundary_unknown and its prose is excluded from
      clean-text statistics (but still counted in coverage).
  R8  "Repost:" posts (post_5, post_6, post_9, post_11) are Satoshi re-posting
      other members' messages from the old forum, each introduced by a dashed
      rule and "<username>:".  Their whole body is labelled repost_other.
  R9  post_10 quotes the reposted question with e-mail style "> " prefixes;
      those lines are labelled quote.
  R10 post_351: the text from "aceat64:" onwards is a manually pasted list of
      other members' benchmark reports; labelled quote.
  R11 post_543 ("I am not Dorian Nakamoto", 2014) is kept in the corpus but
      flagged disputed_authorship and excluded from the author-wide statistics;
      the archive's own timestamp (2014-03-06 00:00:00) is a placeholder, the
      source site gives 2014-03-07T01:17Z.
  R12b A code line of the form "code  -- explanation" keeps the explanation
       (5+ words after ' -- ') as the author's prose; only the code part is
       labelled inline_code.
  R12 Lines inside the author's own prose that look like code or shell commands
      (4+ leading spaces, or shell/C++ patterns) are labelled inline_code and
      excluded from prose statistics; the count is logged per post.
"""
import csv, difflib, html as htmlmod, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
POSTS = os.path.join(ROOT, "posts")
DATA = os.path.join(HERE, "..", "data")
SNI = os.path.join(DATA, "sni_posts.jsonl")

TS_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC - Original Post\s*$")
QH_RE = re.compile(r"Quote from: (?P<who>.+?) on (?P<when>(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}, \d{2}:\d{2}:\d{2} [AP]M)")

CP1252 = {"\x91": "\u2018", "\x92": "\u2019", "\x93": "\u201c", "\x94": "\u201d",
          "\x96": "\u2013", "\x97": "\u2014", "\x85": "\u2026"}

def norm_ws(s):
    """Comparison key: all whitespace removed (the scraper dropped the whitespace
    at block boundaries, so only non-space characters can be compared), U+00A0
    treated as whitespace, stray CP1252 control bytes mapped to the Unicode
    punctuation they stand for."""
    s = s.replace("\u00a0", " ")
    for k, v in CP1252.items():
        s = s.replace(k, v)
    return re.sub(r"\s+", "", s)

def read_repo():
    recs = []
    for name in sorted(os.listdir(POSTS), key=lambda n: int(re.search(r"\d+", n).group())):
        path = os.path.join(POSTS, name)
        raw = open(path, encoding="utf-8").read()
        lines = raw.split("\n")
        title = lines[0].strip()
        platform = lines[2].strip()
        m = TS_RE.match(lines[4])
        ts = m.group(1)
        body_lines = lines[5:]
        # drop trailing empty element produced by a final newline (if any)
        body = "\n".join(body_lines)
        body_start_line = 6
        if body.startswith("  "):
            body = body[2:]
            body_col_offset = 2
        else:
            body_col_offset = 0
        recs.append(dict(file=f"posts/{name}", post_id=int(re.search(r"\d+", name).group()),
                         title=title, platform=platform, timestamp=ts,
                         body_raw=body, body_start_line=body_start_line,
                         body_col_offset=body_col_offset, n_lines=len(lines)))
    return recs

def load_sni():
    if not os.path.exists(SNI):
        return []
    return [json.loads(l) for l in open(SNI, encoding="utf-8")]

# ---------- HTML segmentation ----------
def html_segments(post_html):
    """Walk the post body HTML and return typed segments in document order."""
    soup = BeautifulSoup(post_html, "html.parser")
    segs = []
    def emit(kind, text):
        if text == "":
            return
        if segs and segs[-1]["type"] == kind:
            segs[-1]["text"] += text
        else:
            segs.append({"type": kind, "text": text})
    def walk(node, kind):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                emit(kind, str(ch))
            elif isinstance(ch, Tag):
                cls = ch.get("class", [])
                if ch.name == "br":
                    emit(kind, "\n")
                elif "quoteheader" in cls:
                    emit("quoteheader", ch.get_text())
                elif "quote" in cls:
                    walk(ch, "quote")
                elif "code" in cls or ch.name == "pre" or "codeheader" in cls:
                    emit("code", ch.get_text())
                elif ch.name in ("img",):
                    # forum emoticons are images; the old scrape dropped them.
                    segs.append({"type": "emoticon", "text": ch.get("alt", "") or ch.get("src", "")})
                elif ch.name in ("p", "div", "li", "ul", "ol", "blockquote", "h1", "h2", "h3"):
                    emit(kind, "\n")
                    walk(ch, kind)
                    emit(kind, "\n")
                else:
                    walk(ch, kind)
    walk(soup, "own")
    for s in segs:
        s["text"] = s["text"].replace("\u00a0", " ")
    return segs

# ---------- heuristic segmentation (repo only) ----------
def heuristic_segments(body):
    text = body.replace("\u00a0", " ")
    segs = []
    pos = 0
    flags = set()
    for m in QH_RE.finditer(text):
        if m.start() > pos:
            segs.append({"type": "own", "text": text[pos:m.start()]})
        segs.append({"type": "quoteheader", "text": m.group(0)})
        pos = m.end()
        flags.add("quote_boundary_unknown")
    if pos < len(text):
        segs.append({"type": "own", "text": text[pos:]})
    if re.search(r"(?<![A-Za-z])Quote(?![A-Za-z ])", text) or re.search(r"\bQuote[A-Z]", text):
        flags.add("quote_boundary_unknown")
    if "Code:" in text:
        flags.add("code_boundary_unknown")
    return segs, flags

def strip_signature(segs, platform):
    if platform != "P2P Foundation":
        return segs, False
    last = segs[-1] if segs else None
    if last and last["type"] == "own":
        m = re.search(r"\s*Satoshi Nakamoto\s*(?:http://www\.bitcoin\.org)?\s*$", last["text"])
        if m:
            sig = last["text"][m.start():]
            last["text"] = last["text"][:m.start()]
            segs.append({"type": "signature", "text": sig})
            return segs, True
    return segs, False

import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from cleaning import CODE_LINE_RE, GLOSS_RE, split_code_lines  # shared with 07_control_corpus.py

def apply_overrides(segs, rec):
    flags = set()
    pid = rec["post_id"]
    if rec["title"].startswith("Repost:") and any(s["type"] == "own" and s["text"].lstrip().startswith("--------") for s in segs):
        for s in segs:
            if s["type"] == "own":
                s["type"] = "repost_other"
        flags.add("repost_of_other_members")
    if pid == 10:
        new = []
        for s in segs:
            if s["type"] != "own":
                new.append(s); continue
            for line in s["text"].split("\n"):
                kind = "quote" if line.startswith("> ") else "own"
                new.append({"type": kind, "text": line + "\n"})
        segs = new
        flags.add("email_style_quote_lines")
    if pid == 351:
        new = []
        for s in segs:
            if s["type"] == "own" and "aceat64:" in s["text"]:
                i = s["text"].index("aceat64:")
                new.append({"type": "own", "text": s["text"][:i]})
                new.append({"type": "quote", "text": s["text"][i:]})
            else:
                new.append(s)
        segs = new
        flags.add("manual_quote_split")
    if pid == 543:
        flags.add("disputed_authorship")
    # inline code lines (R12, R12b; cleaning.split_code_lines)
    new, n_code_lines, n_gloss = [], 0, [0]
    for s in segs:
        if s["type"] != "own" or not CODE_LINE_RE.search(s["text"]) and "\n" not in s["text"]:
            new.append(s); continue
        parts, nc, ng = split_code_lines(s["text"])
        new.extend(parts); n_code_lines += nc; n_gloss[0] += ng
    if n_code_lines:
        flags.add(f"inline_code_lines={n_code_lines}")
    if n_gloss[0]:
        flags.add(f"code_gloss_kept_as_prose={n_gloss[0]}")
    return new, flags

def main():
    repo = read_repo()
    sni = load_sni()
    sni_by_norm = {}
    sni_by_dt = {}
    for r in sni:
        if r["post_html"] is None:
            continue
        segs = html_segments(r["post_html"])
        r["_segs"] = segs
        r["_norm"] = norm_ws("".join(s["text"] for s in segs if s["type"] != "emoticon"))
        sni_by_norm.setdefault(r["_norm"], []).append(r)
        if r["datetime"]:
            sni_by_dt.setdefault(r["datetime"][:19].replace("T", " "), []).append(r)
    used = set()
    log_rows = []
    raw_out = open(os.path.join(DATA, "posts_raw.jsonl"), "w", encoding="utf-8")
    clean_out = open(os.path.join(DATA, "posts_clean.jsonl"), "w", encoding="utf-8")
    for rec in repo:
        body = rec["body_raw"]
        bnorm = norm_ws(body)
        match, status, ratio, diff_note = None, "heuristic", None, ""
        cands = sni_by_norm.get(bnorm, [])
        if cands:
            match, status, ratio = cands[0], "exact", 1.0
        else:
            cands = sni_by_dt.get(rec["timestamp"], [])
            best = None
            for c in cands or sni:
                if "_norm" not in c:
                    continue
                rt = difflib.SequenceMatcher(None, bnorm, c["_norm"], autojunk=False).ratio() if abs(len(bnorm) - len(c["_norm"])) < 400 else 0
                if best is None or rt > best[0]:
                    best = (rt, c)
            if best and best[0] >= 0.98:
                match, status, ratio = best[1], "approx", round(best[0], 4)
                sm = difflib.SequenceMatcher(None, bnorm, best[1]["_norm"], autojunk=False)
                diffs = [(op, bnorm[i1:i2], best[1]["_norm"][j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
                diff_note = " | ".join(f"{op}:{a!r}->{b!r}" for op, a, b in diffs[:6])
            elif best:
                ratio = round(best[0], 4)
        flags = set()
        if match is not None:
            key = (match["sni_platform"], match["sni_number"])
            if key in used:
                flags.add("sni_page_matched_twice")
            used.add(key)
            segs = [dict(s) for s in match["_segs"]]
        else:
            segs, hflags = heuristic_segments(body)
            flags |= hflags
        segs, had_sig = strip_signature(segs, rec["platform"])
        segs, oflags = apply_overrides(segs, rec)
        flags |= oflags
        if had_sig:
            flags.add("signature_removed")
        # sanity: segment concatenation must reproduce the body text (whitespace-insensitive)
        if status == "exact" and norm_ws("".join(s["text"] for s in segs if s["type"] != "emoticon")) != bnorm:
            flags.add("segment_roundtrip_mismatch")
        own_text = "\n".join(s["text"] for s in segs if s["type"] == "own")
        own_text = re.sub(r"[ \t]+\n", "\n", own_text)
        own_text = re.sub(r"\n{3,}", "\n\n", own_text).strip("\n")
        n_quote = sum(1 for s in segs if s["type"] == "quoteheader")
        n_code = sum(1 for s in segs if s["type"] == "code")
        n_emo = sum(1 for s in segs if s["type"] == "emoticon")
        if n_emo:
            flags.add("emoticon_image_dropped_by_scraper")
        if n_code:
            flags.add("has_code")
        if n_quote:
            flags.add("has_quotes")
        if status == "heuristic" and n_quote == 0 and not (flags & {"quote_boundary_unknown", "code_boundary_unknown"}):
            status = "heuristic_noquotes"  # body is entirely the author's prose; safe to use
        usable = status in ("exact", "approx", "heuristic_noquotes")
        clean = dict(rec)
        del clean["body_raw"]
        clean.update(dict(alignment=status, alignment_ratio=ratio, alignment_diff=diff_note,
                          sni_platform=match["sni_platform"] if match else None,
                          sni_number=match["sni_number"] if match else None,
                          sni_datetime=match["datetime"] if match else None,
                          original_url=match["original_url"] if match else None,
                          segments=segs, own_text=own_text, usable_for_prose_stats=usable,
                          flags=sorted(flags)))
        raw_out.write(json.dumps(rec, ensure_ascii=False) + "\n")
        clean_out.write(json.dumps(clean, ensure_ascii=False) + "\n")
        log_rows.append(dict(file=rec["file"], post_id=rec["post_id"], platform=rec["platform"], timestamp=rec["timestamp"],
                             title=rec["title"], body_chars=len(body), alignment=status, alignment_ratio=ratio,
                             sni_number=clean["sni_number"], sni_datetime=clean["sni_datetime"],
                             n_quote_blocks=n_quote, n_code_blocks=n_code, own_chars=len(own_text),
                             usable_for_prose_stats=usable, flags=";".join(sorted(flags)), alignment_diff=diff_note))
    with open(os.path.join(DATA, "extraction_log.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(log_rows[0].keys()))
        w.writeheader(); w.writerows(log_rows)
    from collections import Counter
    print("files:", len(repo), "alignment:", Counter(r["alignment"] for r in log_rows))
    unmatched_sni = [(r["sni_platform"], r["sni_number"], r["title"]) for r in sni if "_norm" in r and (r["sni_platform"], r["sni_number"]) not in used]
    print("SNI pages not matched by any repo file:", unmatched_sni)
    print("repo files with flags:", Counter(f for r in log_rows for f in r["flags"].split(";") if f))

if __name__ == "__main__":
    main()
