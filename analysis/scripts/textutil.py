"""Shared tokenisation and sentence segmentation for the stylometric analysis.

Definitions (used by every script, so counts are consistent):

* prose(post)   : the author's own prose = concatenation of 'own' segments of a
                  post (quotes, quote headers, code, inline code, reposted text,
                  emoticon images and the P2P Foundation signature are excluded).
* URL masking   : http(s)://..., www...., ftp://, and bare domain/path strings
                  such as bitcoin.org/download are replaced by the token ⟨URL⟩
                  before tokenisation; the count is kept as a feature.
* word token    : regex [A-Za-z]+(?:['’][A-Za-z]+)* on the URL-masked text, so
                  "it's", "don't", "I'd" are single tokens; hyphenated compounds
                  are split into their parts for word counts but counted
                  separately via HYPHEN_RE.  Numbers are not word tokens.
* sentence      : a maximal span ending at ., !, ? (any run of them, optionally
                  followed by closing quotes/parentheses) when followed by
                  whitespace and the next non-space char is not lowercase, OR
                  at a paragraph break (blank line) OR at a single line break
                  when the line ends without terminal punctuation (list items,
                  headings).  Abbreviations in ABBREV are protected, as are
                  version numbers (0.3.1), decimals, and the dots inside URLs
                  (masked before segmentation).
"""
import re

URL_RE = re.compile(r"(?:https?://|ftp://|www\.)[^\s<>()\"']+|(?<![\w/])(?:[a-z0-9-]+\.)+(?:org|com|net|edu|io)(?:/[^\s<>()\"']*)?", re.I)
URL_TOKEN = "⟨URL⟩"
WORD_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)*")
HYPHEN_RE = re.compile(r"\b[A-Za-z]+(?:-[A-Za-z]+)+\b")
NUM_RE = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?")
ABBREV = {"e.g", "i.e", "etc", "vs", "mr", "mrs", "dr", "st", "jr", "sr", "no", "approx", "misc", "p.s", "a.k.a", "aka", "fig", "ref", "rev", "ver", "v", "btw", "fyi", "imo", "cf", "ca", "inc", "ltd", "co", "pp", "eq"}
TERM_RE = re.compile(r"""([.!?]+)(["'”’)\]]*)(?=\s|$)""")

def mask_urls(text):
    return URL_RE.sub(URL_TOKEN, text)

def words(text, lower=True):
    t = mask_urls(text)
    toks = WORD_RE.findall(t)
    return [w.lower() for w in toks] if lower else toks

def sentences(text):
    """Return a list of sentence strings (stripped) from the author's prose."""
    t = mask_urls(text)
    out = []
    # paragraph-level first
    for para in re.split(r"\n\s*\n", t):
        para = para.strip()
        if not para:
            continue
        # split hard line breaks that end without terminal punctuation into their own units
        lines = para.split("\n")
        buf = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            buf = (buf + " " + line).strip() if buf else line
            if not re.search(r"[.!?][\"'”’)\]]*$", line):
                # line ends without terminal punctuation: treat as unit boundary
                out.extend(_split_terminal(buf))
                buf = ""
        if buf:
            out.extend(_split_terminal(buf))
    return [s for s in out if s]

def _split_terminal(s):
    res, start = [], 0
    for m in TERM_RE.finditer(s):
        end = m.end()
        # protect abbreviations and initials / decimals
        before = s[max(0, start):m.start()]
        last_word = re.findall(r"[A-Za-z.]+$", before)
        lw = last_word[0].lower().rstrip(".") if last_word else ""
        if m.group(1) == "." and (lw in ABBREV or re.fullmatch(r"[a-z]", lw) or re.search(r"\d$", before) and re.match(r"\s*\d", s[end:])):
            continue
        nxt = s[end:].lstrip()
        if nxt and nxt[0].islower() and not m.group(1).startswith("?") and not m.group(1).startswith("!"):
            # ". lowercase" : most likely an abbreviation or an ellipsis mid-sentence
            if m.group(1) != "...":
                continue
        res.append(s[start:end].strip())
        start = end
    tail = s[start:].strip()
    if tail:
        res.append(tail)
    return res

CONTRACTION_RE = re.compile(r"\b(?:[A-Za-z]+n['’]t|[A-Za-z]+['’](?:s|re|ve|ll|d|m))\b")
