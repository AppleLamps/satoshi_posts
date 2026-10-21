#!/usr/bin/env python3
"""Validate the forum fingerprint against the other public, self-declared
Satoshi corpora: the white paper (bitcoin.org/bitcoin.pdf), the 2008-2009
cryptography mailing list emails, the 2009 bitcoin-list (SourceForge) emails,
and the 2009 p2p-research list emails, as archived at
satoshi.nakamotoinstitute.org/emails/.

Cleaning rules for emails (same spirit as 01_extract.py):
  * lines beginning with '>' (quoted text of others) are removed
  * the signature line 'Satoshi Nakamoto' and everything after a list footer
    rule ('-----' line, 'The Cryptography Mailing List', 'Unsubscribe', 'This
    SF.net email', '_____') are removed
  * code-looking lines (same regex as 01_extract.py) are removed
Cleaning rules for the white paper (pdftotext -raw, processed line by line):
  W1 everything from the line 'References' onward is dropped
  W2 title block (title, author, e-mail, URL), section headings ('4. Proof-of-Work')
     and page numbers are dropped; the 'Abstract.' label is removed
  W3 the C code listing is dropped (lines with { or }, ending in ';', or
     starting with a C type)
  W4 formula and result-table lines are dropped: definitions ('p = ...'),
     lines with a mathematical symbol unless they carry eight or more words
     of prose ('80 bytes * 6 * 24 * 365 = 4.2MB per year. With ...'), and
     lines with fewer than three alphabetic words (except a
     short word-only line that ends an unfinished sentence, e.g. 'ownership.')
  W5 diagram labels and figure captions are dropped: a line that does not
     continue an unfinished sentence, has no sentence-final punctuation, and
     either has fewer than six words or is mostly capitalised words
     ('Transactions Hashed in a Merkle Tree'); also any short line ending in
     ' ...' ('Item Item ...', 'Tx Tx ...')
  W6 a line ending in '-' is joined to the next without a space (pdftotext
     wraps 'proof-of-work' as 'proof-' + 'of-work'); other wrapped lines are
     joined with a space
  W7 numbered steps ('1) New transactions ...') stay on their own lines, so the
     list detector sees them, and a paragraph break follows the list
Shared passages: the same text was sometimes published in more than one
corpus (the paper's abstract in the first cryptography e-mail; the v0.1
announcement on all three lists and on the P2P Foundation; release notes on
both the bitcoin-list and the forum). A sentence of a comparison corpus is
marked SHARED when it has 5+ words and at least half of its 6-word shingles
(or, under 6 words, the whole normalised sentence) also occur in a different
source family (paper, e-mail, forum). Every corpus is reported twice: with all
text, and with shared sentences removed ('independent'). Overlap per document
is written to data/agg/shared_passages.csv.
Features are computed with measures.profile(), the same function used for the
forum tables, pooled per corpus, and written to
analysis/data/agg/validation_other_corpora.csv.

Usage: python3 05_validate_other_corpora.py --cache DIR  (DIR holds emails/*.html and whitepaper.pdf)
"""
import argparse, csv, glob, json, os, re, statistics, sys, subprocess
from collections import Counter
from bs4 import BeautifulSoup
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import textutil as T

CODE_LINE_RE = None
exec(open(os.path.join(HERE, "01_extract.py")).read().split("def apply_overrides")[0].split("CODE_LINE_RE = ")[1].split("\n")[0].join(["CODE_LINE_RE = ", ""]))  # reuse the exact regex

def clean_email(html):
    s = BeautifulSoup(html, "html.parser"); m = s.find("main")
    title = m.find("h1").get_text(strip=True); t = m.find("time")
    sec = m.find("section")
    for br in sec.find_all("br"):
        br.replace_with("\n")
    text = sec.get_text().replace(" ", " ")
    out, quoted = [], 0
    for line in text.split("\n"):
        st = line.strip()
        if re.match(r"^-{20,}$|^_{20,}$", st) or st.startswith(("The Cryptography Mailing List", "Unsubscribe by sending", "This SF.net email", "Bitcoin-list mailing list", "p2p-research mailing list", "Sent from", "https://lists.sourceforge.net", "http://lists.zooko.com", "---------- Forwarded")):
            break
        if st.startswith(">"):
            quoted += 1; continue
        if re.match(r"^(On .* wrote:|.* wrote:|.*writes:|-----Original Message-----|From: |To: |Sent: |Subject: |Date: )", st):
            continue
        if st == "Satoshi Nakamoto" or st == "Satoshi":
            continue
        if CODE_LINE_RE.match(line) and not re.match(r"^#\d", st):
            continue
        out.append(line.rstrip())
    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = unwrap(body)
    return title, (t["datetime"] if t else None), body, quoted

def unwrap(body):
    """E-mails are hard-wrapped at ~72 columns. Re-join a line to the previous
    one unless the previous line ends a paragraph (blank line), ends with ':',
    or either line is a list item / URL / indented line."""
    paras = []
    for para in re.split(r"\n\s*\n", body):
        lines = para.split("\n"); out = []
        for line in lines:
            st = line.strip()
            is_item = bool(re.match(r"^(?:[-*]\s|\d+[).]\s|\s{2,}|http)", line)) or line.startswith(" ")
            if out and not is_item and not re.search(r":\s*$", out[-1]) and not re.match(r"^(?:[-*]\s|\d+[).]\s|\s{2,})", out[-1]) and not out[-1].rstrip().endswith(("---", "===")):
                out[-1] = out[-1].rstrip() + " " + st
            else:
                out.append(line.rstrip())
        paras.append("\n".join(out))
    return "\n\n".join(paras)

MATH_CHARS = set("=<>∑∞−⋅≤≥λ∏√±×÷")
def clean_whitepaper(pdf):
    raw = subprocess.run(["pdftotext", "-raw", pdf, "-"], capture_output=True, text=True).stdout.replace("\f", "")
    lines = raw.split("\n")
    if "References" in [l.strip() for l in lines]:
        lines = lines[:[l.strip() for l in lines].index("References")]          # W1
    kept = []                                                                     # (text, is_list_item)
    clean_whitepaper.dropped = []
    def ends_sentence(t): return bool(re.search(r"[.!?:]$", t))
    for line in lines:
        st = line.strip()
        if not st: continue
        if re.match(r"^(Bitcoin: A Peer-to-Peer Electronic Cash System|Satoshi Nakamoto|satoshin@|www\.bitcoin\.org)$", st): continue   # W2
        if re.match(r"^\d{1,2}\.\s+[A-Z][A-Za-z -]+$", st) or re.fullmatch(r"\d+", st): continue                                  # W2
        if st.startswith("Abstract."): st = st[len("Abstract."):].strip()
        if re.search(r"[{}]|;\s*$", st) or re.match(r"^(#include|double |int |return\b|for \()", st): continue                  # W3
        words_ = re.findall(r"[A-Za-z]{2,}", st)
        prev_open = bool(kept) and not ends_sentence(kept[-1][0])
        completes = prev_open and bool(re.fullmatch(r"[A-Za-z][\w' +-]*[.!?]", st))   # e.g. 'ownership.' or 'gap by -1.' ending a wrapped sentence
        is_def = bool(re.match(r"^[A-Za-z]\w*\s*[=<>]", st))                                                                    # 'p = probability ...', 'q=0.1'
        long_prose = len(words_) >= 8 and not is_def                                                                              # prose with an inline formula
        if is_def or (any(c in MATH_CHARS for c in st) and not long_prose) or (len(words_) < 3 and not completes): continue      # W4
        if re.search(r"\s\.\.\.$", st): continue                                                                                # W5
        if len(st.split()) < 6 and not ends_sentence(st) and not prev_open: continue                                            # W5
        caps = [w for w in st.split() if w[:1].isalpha()]
        if not prev_open and not ends_sentence(st) and caps and sum(w[0].isupper() for w in caps) >= 0.6 * len(caps): continue  # W5 captions
        kept.append((st, bool(re.match(r"^\d\)\s", st))))
    out, in_list = "", False
    for st, is_item in kept:
        if not out:
            out = st
        elif is_item:
            out += "\n" + st; in_list = True                                                                                     # W7
        elif in_list and re.search(r"[.!?]$", out) and st[:1].isupper():
            out += "\n\n" + st; in_list = False                                                                                 # W7
        elif out.endswith("-"):
            out += st                                                                                                             # W6
        else:
            out += " " + st
    return out

import measures as M

def features(docs):
    return M.profile(docs)

def shingles(text, k=6):
    w = T.words(text)
    return {" ".join(w[i:i + k]) for i in range(len(w) - k + 1)}

def is_shared(snt, other_shingles, other_sents):
    ws = T.words(snt)
    if len(ws) < 5:
        return False
    if len(ws) < 6:
        return " ".join(ws) in other_sents
    sh = shingles(snt)
    return len(sh & other_shingles) >= 0.5 * len(sh)

def split_shared(docs, other_shingles, other_sents):
    """Remove SHARED sentences from each document by deleting the sentence and
    the spaces that follow it from the (URL-masked) original, so the spacing
    of the remaining boundaries is untouched.
    Returns (independent_docs, n_shared_sentences, n_shared_words)."""
    out, ns, nw = [], 0, 0
    for d in docs:
        t = T.mask_urls(d)
        for snt in T.sentences(d):
            if is_shared(snt, other_shingles, other_sents):
                pat = r"\s+".join(re.escape(x) for x in snt.split())
                m = re.search(pat + r"[ \t\u00a0]*", t)
                if m:
                    t = t[:m.start()] + t[m.end():]
                    ns += 1; nw += len(T.words(snt))
        out.append(t)
    return out, ns, nw

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); a = ap.parse_args()
    corpora = {}
    records = []
    for f in sorted(glob.glob(os.path.join(a.cache, "emails", "*.html"))):
        lst = os.path.basename(f).rsplit("_", 1)[0]
        title, dt, body, quoted = clean_email(open(f, encoding="utf-8").read())
        records.append(dict(corpus=lst, file=os.path.basename(f), title=title, datetime=dt, words=len(T.words(body)), quoted_lines_removed=quoted, text=body))
        corpora.setdefault(lst, []).append(body)
    wp = clean_whitepaper(os.path.join(a.cache, "whitepaper.pdf" if os.path.exists(os.path.join(a.cache, "whitepaper.pdf")) else "bitcoin.pdf"))
    corpora["whitepaper"] = [wp]
    # sentence spacing in the PDF has to be read with a layout-preserving extractor
    try:
        import pypdf
        t = "\n".join(pg.extract_text() for pg in pypdf.PdfReader(os.path.join(a.cache, "whitepaper.pdf" if os.path.exists(os.path.join(a.cache, "whitepaper.pdf")) else "bitcoin.pdf")).pages).split("References")[0]
        wp_dbl, wp_sgl = len(re.findall(r"[a-z]\.  [A-Z]", t)), len(re.findall(r"[a-z]\. [A-Z]", t))
        wp_gap_dbl, wp_gap_sgl = len(re.findall(r"[a-z]  [a-z]", t)), len(re.findall(r"[a-z] [a-z]", t))
        print(f"whitepaper (pypdf): sentence boundaries double={wp_dbl} single={wp_sgl}; ordinary word gaps double={wp_gap_dbl} single={wp_gap_sgl}")
    except Exception as e:
        wp_dbl = wp_sgl = None; print("pypdf unavailable:", e)
    records.append(dict(corpus="whitepaper", file="bitcoin.pdf", title="Bitcoin: A Peer-to-Peer Electronic Cash System", datetime="2008-10-31", words=len(T.words(wp)), quoted_lines_removed=0, text=wp))
    # forum reference: reuse posts_clean.jsonl own prose, core corpus
    recs = [json.loads(l) for l in open(os.path.join(HERE, "..", "data", "posts_clean.jsonl"), encoding="utf-8")]
    core = [r for r in recs if r["usable_for_prose_stats"] and "disputed_authorship" not in r["flags"] and "repost_of_other_members" not in r["flags"]
            and T.words("\n".join(s_["text"] for s_ in r["segments"] if s_["type"] == "own"))]   # excludes the code-only post_475
    corpora["forum_bitcointalk"] = ["\n".join(s["text"] for s in r["segments"] if s["type"] == "own") for r in core if r["platform"] == "Bitcointalk"]
    corpora["forum_p2pfoundation"] = ["\n".join(s["text"] for s in r["segments"] if s["type"] == "own") for r in core if r["platform"] == "P2P Foundation"]
    # the v0.1 release announcement was sent to all three lists; pool each distinct text once
    seen, pooled = set(), []
    for k in ("cryptography", "bitcoin-list", "p2p-research"):
        for b in corpora[k]:
            key = re.sub(r"\s+", "", b)[:400]
            if key in seen:
                continue
            seen.add(key); pooled.append(b)
    corpora["emails_all"] = pooled
    # source families for the shared-passage test
    fam_docs = {"paper": [("whitepaper", wp)],
                "email": [(r["file"], r["text"]) for r in records if r["corpus"] != "whitepaper"],
                "forum": [(f"post_{r['post_id']}", "\n".join(s_["text"] for s_ in r["segments"] if s_["type"] == "own")) for r in core]}
    fam_sh = {f: set().union(*[shingles(t) for _, t in ds]) for f, ds in fam_docs.items()}
    fam_short = {f: {" ".join(T.words(snt)) for _, t in ds for snt in T.sentences(t) if 5 <= len(T.words(snt)) < 6} for f, ds in fam_docs.items()}
    family_of = {"whitepaper": "paper", "cryptography": "email", "bitcoin-list": "email", "p2p-research": "email", "emails_all": "email",
                 "forum_p2pfoundation": "forum", "forum_bitcointalk": "forum"}
    def others(fam):
        osh = set().union(*[fam_sh[f] for f in fam_sh if f != fam]); ost = set().union(*[fam_short[f] for f in fam_short if f != fam])
        return osh, ost
    # per-document overlap table
    share_rows = []
    doc_sh = {f: {name: shingles(t) for name, t in ds} for f, ds in fam_docs.items()}
    for fam, ds in fam_docs.items():
        osh, ost = others(fam)
        for name, t in ds:
            ss = [snt for snt in T.sentences(t) if is_shared(snt, osh, ost)]
            if not ss:
                continue
            best, bj = None, 0.0
            for f2 in doc_sh:
                if f2 == fam: continue
                for n2, sh2 in doc_sh[f2].items():
                    a_, b_ = doc_sh[fam][name], sh2
                    if a_ and b_:
                        j_ = len(a_ & b_) / len(a_ | b_)
                        if j_ > bj: best, bj = n2, j_
            share_rows.append(dict(family=fam, document=name, words=len(T.words(t)), shared_sentences=len(ss),
                                   shared_words=sum(len(T.words(x)) for x in ss), closest_other_document=best, jaccard_6gram=round(bj, 3),
                                   example=ss[0][:120]))
    with open(os.path.join(HERE, "..", "data", "agg", "shared_passages.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(share_rows[0].keys())); w.writeheader(); w.writerows(share_rows)
    rows = []
    order = ["whitepaper", "cryptography", "bitcoin-list", "p2p-research", "emails_all", "forum_p2pfoundation", "forum_bitcointalk"]
    for k in order:
        osh, ost = others(family_of[k])
        indep, ns, nwd = split_shared(corpora[k], osh, ost)
        for variant, docs in (("all", corpora[k]), ("independent", indep)):
            f = features(docs); f = dict(corpus=k, variant=variant, shared_sentences_removed=ns if variant == "independent" else 0,
                                          shared_words_removed=nwd if variant == "independent" else 0, **f)
            if k == "whitepaper" and wp_dbl is not None:
                # spacing is read from the PDF layout text for the whole paper (abstract included in both variants)
                f["double_space"], f["single_space"], f["double_space_share"] = wp_dbl, wp_sgl, round(wp_dbl / (wp_dbl + wp_sgl), 3)
            rows.append(f)
    # e-mails by year, to separate date from register for will/would
    by_year = {}
    for r in records:
        if r["corpus"] != "whitepaper" and r["datetime"]:
            by_year.setdefault(r["datetime"][:4], []).append(r["text"])
    for y, docs in sorted(by_year.items()):
        seen_y, uniq = set(), []
        for b in docs:
            key = re.sub(r"\s+", "", b)[:400]
            if key not in seen_y:
                seen_y.add(key); uniq.append(b)
        f = features(uniq); rows.append(dict(corpus=f"emails_{y}", variant="all", shared_sentences_removed=0, shared_words_removed=0, **f))
    out = os.path.join(HERE, "..", "data", "agg", "validation_other_corpora.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, "..", "data", "other_corpora_clean.jsonl"), "w", encoding="utf-8") as fh:
        for r in records: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    # transposed view
    keys = [k for k in rows[0] if k not in ("corpus", "variant")]
    print(f"{'feature':24s}" + "".join(f"{(r['corpus'][:11] + '/' + r['variant'][:4]):>17s}" for r in rows))
    for k in keys:
        print(f"{k:24s}" + "".join(f"{str(r[k])[:16]:>17s}" for r in rows))

if __name__ == "__main__":
    main()
