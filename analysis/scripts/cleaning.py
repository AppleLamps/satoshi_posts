"""Shared prose-cleaning rules, used for Satoshi's posts (01_extract.py) and
for the control writers (07_control_corpus.py), so both populations are
cleaned identically.

R12  A line inside prose that looks like code or a shell command is labelled
     inline_code and excluded from prose statistics (CODE_LINE_RE).
R12b A code line of the form "code  -- explanation" keeps the explanation
     (5+ words after ' -- ') as the author's prose.
"""
import re

CODE_LINE_RE = re.compile(r"^(?: {4,}\S|sudo |cd |make\b|tar -|mkdir |ldconfig|\.\./configure|LIBS=|#|-l |-Wl|\$ |svn |git |apt-get|wget |curl |export |chmod |\./|\+\s|gdb |bt$|run$|[A-Za-z_][A-Za-z0-9_:<>.\[\]-]*\s*\(.*\)\s*;|.*\)\s*;\s*(?://.*)?$|.*;\s*//.*$|.*\bwx[A-Z]\w*\s*[|)]|\s*[{}]\s*$|//|\s*(?:if|else if|while|for)\s*\(.*\)\s*$|[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^=].*;\s*$|(?:bitcoind?|gdb)\s+-|\w+\s*(?:<<|>>)\s*\w+;|.*\(\s*$|.*\bstr[A-Z]\w+.*;|\s*\d+\)\s+\w+\(.*\)\s*;|.*\\n\s*$|[\w.\\/]+\.(?:cpp|h|dat|exe|dll|txt|conf|po|mo)\s*$|\(\s*wait for)")

GLOSS_RE = re.compile(r"\s--\s+(\S.*)$")


def split_code_lines(text):
    """Split one prose segment into own/inline_code segments (R12, R12b).
    Returns (segments, n_code_lines, n_glosses_kept); each segment is
    {"type": "own" | "inline_code", "text": str}."""
    new, n_code, n_gloss = [], 0, 0
    buf_kind, buf = None, []
    for line in text.split("\n"):
        kind = "inline_code" if CODE_LINE_RE.match(line) else "own"
        gloss = None
        if kind == "inline_code":
            n_code += 1
            gm = GLOSS_RE.search(line)
            if gm and len(re.findall(r"[A-Za-z]+", gm.group(1))) >= 5:
                gloss = gm.group(1); line = line[:gm.start(1)]
                n_gloss += 1
        if kind != buf_kind and buf:
            new.append({"type": buf_kind, "text": "\n".join(buf) + "\n"}); buf = []
        buf_kind = kind; buf.append(line)
        if gloss:
            new.append({"type": "inline_code", "text": "\n".join(buf)})
            new.append({"type": "own", "text": gloss + "\n"})
            buf_kind, buf = None, []
    if buf:
        new.append({"type": buf_kind, "text": "\n".join(buf)})
    return new, n_code, n_gloss


def prose_from_text(text):
    """Own prose of a block of forum text after R12/R12b, joined the same way
    as the Satoshi prose ('own' segments joined with a newline)."""
    segs, _, _ = split_code_lines(text)
    return "\n".join(s["text"] for s in segs if s["type"] == "own").strip()


def clean_forum_post_html(div):
    """BitcoinTalk post <div class="post"> -> author's own prose. Removes quote
    blocks, quote headers, code blocks, images and signatures; <br> becomes a
    newline; U+00A0 becomes a space (R2); then R12/R12b."""
    for sel in ["div.quoteheader", "div.quote", "div.codeheader", "div.code", "img", "div.signature"]:
        for x in div.select(sel):
            x.decompose()
    for br in div.find_all("br"):
        br.replace_with("\n")
    text = div.get_text().replace("\u00a0", " ")
    return re.sub(r"\n{3,}", "\n\n", prose_from_text(text)).strip()
