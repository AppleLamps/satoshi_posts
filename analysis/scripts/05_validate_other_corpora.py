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
Cleaning rules for the white paper:
  * pdftotext (raw mode); drop everything from the 'References' heading
  * drop the title block, section headings, figure captions/diagram text,
    formula lines (lines dominated by symbols, single letters, '=' or digits),
    page numbers, and the AppendixC-style code; keep running prose paragraphs
Features are computed with the same textutil tokeniser/sentence splitter and
the same regexes as 02_features.py, pooled per corpus, and written to
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

def clean_whitepaper(pdf):
    txt = subprocess.run(["pdftotext", "-raw", pdf, "-"], capture_output=True, text=True).stdout
    txt = txt.split("\nReferences\n")[0]
    keep = []
    for line in txt.split("\n"):
        st = line.strip()
        if not st: keep.append(""); continue
        if re.match(r"^\d+\.\s+[A-Z][A-Za-z -]+$", st): continue          # section headings
        if re.match(r"^(Bitcoin: A Peer-to-Peer|Satoshi Nakamoto|satoshin@|www\.bitcoin\.org|Abstract\.)", st):
            if st.startswith("Abstract."): keep.append(st[len("Abstract."):].strip()); 
            continue
        if re.fullmatch(r"\d+", st): continue                               # page numbers
        letters = sum(c.isalpha() for c in st)
        if letters < 0.6 * len(st.replace(" ", "")): continue               # formulas, diagrams, tables
        if re.match(r"^(Block|Tx|Hash|Prev Hash|Nonce|Root Hash|Owner \d|Public Key|Signature|Verify|Sign|Item|Hash\d+|Timestamp|Root|Transactions Hashed|Header|Longest Proof-of-Work Chain|Merkle Branch|Block Header)\b", st): continue
        if re.match(r"^(#include|double |int |return|\{|\}|for \(|if \(|printf|AttackerSuccessProbability|lambda|sum|poisson|q=|z=|P=|p=)", st): continue
        if re.search(r"\b(qz|z=\d|q=0\.\d|P=\d|P < 0\.\d)\b", st): continue
        keep.append(st)
    body = "\n".join(keep)
    body = re.sub(r"\n{3,}", "\n\n", body)
    # rejoin hard-wrapped lines inside paragraphs
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", body)]
    return "\n\n".join(p for p in paras if p)

IRREG_PP = open(os.path.join(HERE, "02_features.py")).read().split('IRREG_PP = "')[1].split('"')[0]
PASSIVE_RE = re.compile(r"\b(?:is|are|was|were|be|been|being|get|gets|got|gotten|getting|'s|'re)\s+(?:(?:not|never|also|already|still|just|only|being|always|usually|often|probably|then|all|also)\s+){0,2}(?:[A-Za-z]{3,}ed|" + IRREG_PP + r")\b", re.I)

def features(docs):
    """docs: list of prose strings. Returns pooled feature dict."""
    text = "\n\n".join(docs); masked = T.mask_urls(text)
    toks = T.words(text); nw = len(toks); cnt = Counter(toks)
    sents = [s for d in docs for s in T.sentences(d)]; sl = [len(T.words(s)) for s in sents if T.words(s)]
    def per1k(x): return round(1000 * x / nw, 2) if nw else None
    dbl = len(re.findall(r"[a-z0-9)\"'][.!?]  [A-Z\"(]", text)); sgl = len(re.findall(r"[a-z0-9)\"'][.!?] [A-Z\"(]", text))
    contr = len(T.CONTRACTION_RE.findall(masked))
    full_forms = sum(len(re.findall(r"\b" + f + r"\b", masked)) for f in ["does not", "will not", "can not", "cannot", "I am", "it is", "that is", "there is", "I will", "I have", "you are", "is not", "do not", "would not", "did not", "could not", "should not", "are not", "was not", "has not", "have not", "they are", "we are", "it will"])
    contr_choice = sum(len(re.findall(r"\b" + f + r"\b", masked)) for f in ["doesn't", "won't", "can't", "I'm", "it's", "that's", "there's", "I'll", "I've", "you're", "isn't", "don't", "wouldn't", "didn't", "couldn't", "shouldn't", "aren't", "wasn't", "hasn't", "haven't", "they're", "we're", "it'll"])
    quotes_out = len(re.findall(r"\"[^\"\n]{1,40}\"[.,]", masked)); quotes_in = len(re.findall(r"[a-z]{3,}[.!?]\"(?=\s|$)", masked))
    f = dict(
        documents=len(docs), words=nw, sentences=len(sl),
        mean_sentence_len=round(statistics.mean(sl), 2) if sl else None, median_sentence_len=statistics.median(sl) if sl else None,
        mean_word_len=round(sum(map(len, toks)) / nw, 3) if nw else None,
        double_space=dbl, single_space=sgl, double_space_share=round(dbl / (dbl + sgl), 3) if dbl + sgl else None,
        contractions_per1k=per1k(contr), contracted_share=round(contr_choice / (contr_choice + full_forms), 3) if contr_choice + full_forms else None,
        comma_per1k=per1k(masked.count(",")), semicolon=masked.count(";"), colon_per1k=per1k(len(re.findall(r":(?!\d)", masked))),
        paren_per1k=per1k(masked.count("(")), question_per1k=per1k(masked.count("?")), exclaim=masked.count("!"), ellipsis=len(re.findall(r"\.{3,}", masked)),
        em_dash=masked.count("—") + masked.count("–"), double_hyphen=len(re.findall(r"(?<!-)--(?!-)", masked)),
        dquote_per1k=per1k(masked.count('"')), quote_punct_outside=quotes_out, quote_punct_inside=quotes_in,
        passive_per_sentence=round(len(PASSIVE_RE.findall(masked)) / len(sl), 3) if sl else None,
        the_per1k=per1k(cnt["the"]), it_per1k=per1k(cnt["it"]), and_per1k=per1k(cnt["and"]), if_per1k=per1k(cnt["if"]),
        I_per1k=per1k(sum(cnt[w] for w in ["i", "me", "my", "i'm", "i've", "i'll", "i'd"])), you_per1k=per1k(sum(cnt[w] for w in ["you", "your", "you're", "you've", "you'll", "you'd"])),
        we_per1k=per1k(sum(cnt[w] for w in ["we", "us", "our", "we're", "we've", "we'll"])),
        would_per1k=per1k(cnt["would"]), can_per1k=per1k(cnt["can"]), could_per1k=per1k(cnt["could"]), should_per1k=per1k(cnt["should"]), will_per1k=per1k(cnt["will"]), must_per1k=per1k(cnt["must"]), may_might_per1k=per1k(cnt["may"] + cnt["might"]),
        if_you_openers=len(re.findall(r"(?:^|[.!?]\s+|\n)If you\b", text)), it_would_be=len(re.findall(r"\b[Ii]t would be\b", text)),
        I_think=len(re.findall(r"\bI think\b", text)), not_sure=len(re.findall(r"\bnot sure\b", text)), probably=cnt["probably"], maybe=cnt["maybe"], obviously=cnt["obviously"], certainly=cnt["certainly"],
        verdict_openers=len(re.findall(r"(?:^|\n)(?:Right|Yes|No|True|OK|Nope)[,.]", text)),
        thanks=len(re.findall(r"\b[Tt]hanks\b", text)), sorry=len(re.findall(r"\b[Ss]orry\b", text)), please=len(re.findall(r"\b[Pp]lease\b", text)),
        list_num_paren=len(re.findall(r"(?m)^\s*\d\)\s", text)), list_num_dot=len(re.findall(r"(?m)^\s*\d\.\s", text)), bullet_dash=len(re.findall(r"(?m)^\s*- ", text)), bullet_star=len(re.findall(r"(?m)^\s*\* ", text)),
        block_chain=len(re.findall(r"\bblock chain\b", text, re.I)), blockchain=len(re.findall(r"\bblockchain\b", text, re.I)),
        double_spend_hyphen=len(re.findall(r"\bdouble-spend", text, re.I)), double_spend_open=len(re.findall(r"\bdouble spend", text, re.I)),
        pow_hyphen=len(re.findall(r"\bproof-of-work\b", text, re.I)), pow_open=len(re.findall(r"\bproof of work\b", text, re.I)),
        email_hyphen=len(re.findall(r"\be-mail\b", text, re.I)), email_solid=len(re.findall(r"\bemail\b", text, re.I)),
        a_lot=len(re.findall(r"\ba lot\b", text)), OK=len(re.findall(r"\bOK\b", text)), okay=len(re.findall(r"\bokay\b", text, re.I)),
        british_tokens=len(re.findall(r"(?<![A-Za-z])(?:optimis\w+|colour\w*|grey|favour\w*|neighbour\w*|defence|labell\w+|fulfil|maths|analys(?:e|ed|ing)|formalis\w+|prioritis\w+|amortis\w+|reorganis\w+|modernis\w+|liberalis\w+|decentralis\w+|centralis\w+|realis\w+|recognis\w+|minimis\w+|organis\w+|behaviour\w*|centre|licence|offence|programme|catalogue|whilst|amongst|learnt|spelt|towards|cheque|tyre|aluminium|judgement|acknowledgement)(?![A-Za-z])", text, re.I)),
        american_tokens=len(re.findall(r"(?<![A-Za-z])(?:optimiz\w+|color\w*|gray|favor\w*|neighbor\w*|defense|labeled|labeling|fulfill|math|analyz\w+|formaliz\w+|prioritiz\w+|amortiz\w+|reorganiz\w+|moderniz\w+|liberaliz\w+|decentraliz\w+|centraliz\w+|realiz\w+|recogniz\w+|minimiz\w+|organiz\w+|behavior\w*|center|offense|catalog|gotten|toward|aluminum|judgment|acknowledgment)(?![A-Za-z])", text, re.I)),
        british_examples=" ".join(sorted(set(m.lower() for m in re.findall(r"(?<![A-Za-z])(?:optimis\w+|colour\w*|grey|favour\w*|neighbour\w*|defence|labell\w+|fulfil|maths|analys(?:e|ed|ing)|formalis\w+|prioritis\w+|amortis\w+|reorganis\w+|modernis\w+|liberalis\w+|decentralis\w+|centralis\w+|realis\w+|recognis\w+|minimis\w+|organis\w+|behaviour\w*|centre|licence|programme|catalogue|whilst|amongst|learnt|spelt|towards|cheque|judgement)(?![A-Za-z])", text, re.I)))),
        american_examples=" ".join(sorted(set(m.lower() for m in re.findall(r"(?<![A-Za-z])(?:optimiz\w+|color\w*|gray|favor\w*|neighbor\w*|defense|labeled|fulfill|math|analyz\w+|formaliz\w+|prioritiz\w+|decentraliz\w+|centraliz\w+|realiz\w+|recogniz\w+|minimiz\w+|organiz\w+|behavior\w*|center|gotten|toward|judgment)(?![A-Za-z])", text, re.I)))),
        day_first_dates=len(re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b", text)),
        percent_attached=len(re.findall(r"\d%", text)), percent_word=len(re.findall(r"\bpercent\b", text)),
        eg=len(re.findall(r"\be\.g\.", text)), eg_comma=len(re.findall(r"\be\.g\.,", text)), etc_period=len(re.findall(r"\betc\.", text)), etc_bare=len(re.findall(r"\betc\b(?!\.)", text)), vs_bare=len(re.findall(r"\bvs\b(?!\.)", text)), vs_period=len(re.findall(r"\bvs\.", text)), ie=len(re.findall(r"\bi\.e\.", text)),
    )
    return f

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
    core = [r for r in recs if r["usable_for_prose_stats"] and "disputed_authorship" not in r["flags"] and "repost_of_other_members" not in r["flags"]]
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
    rows = []
    order = ["whitepaper", "cryptography", "bitcoin-list", "p2p-research", "emails_all", "forum_p2pfoundation", "forum_bitcointalk"]
    for k in order:
        f = features(corpora[k]); f = dict(corpus=k, **f)
        if k == "whitepaper" and wp_dbl is not None:
            f["double_space"], f["single_space"], f["double_space_share"] = wp_dbl, wp_sgl, round(wp_dbl / (wp_dbl + wp_sgl), 3)
        rows.append(f)
    out = os.path.join(HERE, "..", "data", "agg", "validation_other_corpora.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    with open(os.path.join(HERE, "..", "data", "other_corpora_clean.jsonl"), "w", encoding="utf-8") as fh:
        for r in records: fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    # transposed view
    keys = [k for k in rows[0] if k != "corpus"]
    print(f"{'feature':24s}" + "".join(f"{r['corpus'][:16]:>17s}" for r in rows))
    for k in keys:
        print(f"{k:24s}" + "".join(f"{str(r[k])[:16]:>17s}" for r in rows))

if __name__ == "__main__":
    main()
