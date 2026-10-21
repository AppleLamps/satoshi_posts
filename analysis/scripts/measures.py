"""Canonical feature definitions shared by every script.

Each named feature in the reports is computed by exactly one function here, so
02_features.py (per-post table), 03_evidence.py (finding counts),
05_validate_other_corpora.py (other Satoshi corpora) and 07_control_corpus.py
(other forum writers) report the same thing under the same name.

All functions take the author's prose (already cleaned of quotes, code and
signatures) and return counts. Rates are computed by the callers as
1000 * count / word tokens (textutil.words).

Case rule: lexical items (hedges, boosters, adverbs, term forms, spellings) are
matched case-insensitively. Items whose definition depends on position
(sentence openers, verdict openers) are matched on the capitalised form at the
defined position only.
"""
import re
from collections import Counter
import textutil as T

# --------------------------------------------------------------- spacing
# A sentence boundary for spacing purposes: a letter or digit, then . ! or ?,
# optional closing quote/parenthesis, then one or more spaces, then an
# optional opening quote/parenthesis and an upper-case letter. Abbreviations
# in textutil.ABBREV (e.g., etc., vs.) are not boundaries. Measured on the
# URL-masked prose with U+00A0 already converted to a space (rule R2).
_SPACE_RE = re.compile(r"([A-Za-z0-9]+)([.!?])[\"')\]]*( +)(?=[\"(]?[A-Z])")

def sentence_spacing(text):
    """Return (double, single): boundaries followed by 2+ spaces vs exactly 1."""
    t = T.mask_urls(text).replace(" ", " ")
    dbl = sgl = 0
    for m in _SPACE_RE.finditer(t):
        if m.group(2) == "." and (m.group(1).lower() in T.ABBREV or re.fullmatch(r"[A-Za-z]", m.group(1))):
            continue
        if len(m.group(3)) >= 2:
            dbl += 1
        else:
            sgl += 1
    return dbl, sgl

# --------------------------------------------------------------- sentence openers
_SECOND_PERSON = {"you", "you're", "you've", "you'd", "you'll"}

def if_you_openers(text):
    """Sentences (textutil.sentences) whose first word is 'If' and second word
    is a second-person subject. Returns (all_forms, bare_you).
    all_forms counts If you / If you're / If you've / If you'd / If you'll."""
    allf = bare = 0
    for s in T.sentences(text):
        ws = T.words(s, lower=False)
        if len(ws) >= 2 and ws[0] == "If":
            w2 = ws[1].lower().replace("’", "'")
            if w2 in _SECOND_PERSON:
                allf += 1
                bare += w2 == "you"
    return allf, bare

def sentence_opener_count(text, first, second=None):
    n = 0
    for s in T.sentences(text):
        ws = T.words(s, lower=False)
        if ws and ws[0] == first and (second is None or (len(ws) > 1 and ws[1] == second)):
            n += 1
    return n

VERDICT_RE = re.compile(r"(?m)^(?:Right|Yes|No|True|OK|Nope|Not really)[,.]")

def verdict_openers(text):
    """Paragraph- or line-initial one-word verdicts followed by ',' or '.'."""
    return len(VERDICT_RE.findall(text))

# --------------------------------------------------------------- stance lexicons
HEDGES = {
    "I think": r"\bI think\b", "I don't think": r"\bI don't think\b", "I'm not sure": r"\bI'm not sure\b",
    "not sure": r"\bnot sure\b", "I guess": r"\bI guess\b", "I suppose": r"\bI suppose\b", "I suspect": r"\bI suspect\b",
    "I assume": r"\bI assume\b", "I believe": r"\bI believe\b", "probably": r"\bprobably\b", "maybe": r"\bmaybe\b",
    "perhaps": r"\bperhaps\b", "possibly": r"\bpossibly\b", "might": r"\bmight\b",
}
BOOSTERS = {
    "obviously": r"\bobviously\b", "certainly": r"\bcertainly\b", "definitely": r"\bdefinitely\b",
    "clearly": r"\bclearly\b", "surely": r"\bsurely\b", "of course": r"\bof course\b",
    "undoubtedly": r"\bundoubtedly\b", "absolutely": r"\babsolutely\b", "I'm sure": r"\bI'm sure\b",
}
def _alternation(lex):
    """One regex with a named group per item, longest pattern first, so that
    overlapping items are matched once: "I'm not sure" is counted under
    "I'm not sure" only, and "not sure" counts the remaining uses
    (e.g. "I am not sure", "not sure if")."""
    keys = sorted(lex, key=lambda k: -len(k))
    names = {f"g{i}": k for i, k in enumerate(keys)}
    rx = re.compile("|".join(f"(?P<g{i}>{lex[k]})" for i, k in enumerate(keys)), re.I)
    return rx, names
_HEDGE_ALT = _alternation(HEDGES)
_BOOST_ALT = _alternation(BOOSTERS)

def lexicon_counts(text, which):
    """Non-overlapping counts per lexicon item; sum(values) is the number of
    separate stance markers."""
    rx, names = _HEDGE_ALT if which == "hedges" else _BOOST_ALT
    out = {k: 0 for k in names.values()}
    for m in rx.finditer(T.mask_urls(text)):
        out[names[m.lastgroup]] += 1
    return out

# --------------------------------------------------------------- affect / topic lexicons
# Used for the change-over-time affect table. Lists are deliberately short and
# limited to words whose sense is evaluative or topical in this corpus; every
# match is written to data/agg/affect_matches.csv for inspection.
AFFECT = {
    "positive": r"\b(?:good|great|nice|glad|happy|pleased|thanks|thank|cool|excellent|awesome|hurray|impressive|amazing|wonderful|perfect|hope|hopefully|fun|neat|nifty|handy|elegant)\b",
    "negative": r"\b(?:unfortunately|annoying|annoyed|frustrating|frustrated|sad|worry|worried|worries|afraid|fear|ugly|terrible|awful|horrible|hate|painful|nasty|sigh|damn|upset|disappointed|disappointing|sucks|bloody|messy|clunky)\b",
    "security": r"\b(?:attack|attacks|attacked|attacker|attackers|dos|ddos|flood|flooding|exploit|exploits|vulnerability|vulnerable|malicious|spam|spammer|spammers|overflow|hacker|hackers|steal|stolen|theft|abuse|abusive)\b",
    "government_legal": r"\b(?:government|governments|regulation|regulations|regulator|regulators|law|laws|legal|illegal|legality|police|tax|taxes|taxation|censorship|censor|freedom|liberty|anonymity|anonymous|privacy|wikileaks|central bank|central banks|lawsuit|court|courts|authorities)\b",
}
_AFFECT_RX = {k: re.compile(v, re.I) for k, v in AFFECT.items()}

def affect_matches(text):
    t = T.mask_urls(text)
    return {k: [m.group(0).lower() for m in r.finditer(t)] for k, r in _AFFECT_RX.items()}

# --------------------------------------------------------------- contractions, passive
CONTRACTED = ["doesn't", "won't", "can't", "I'm", "it's", "that's", "there's", "I'll", "I've", "you're", "isn't", "don't", "wouldn't", "didn't", "couldn't", "shouldn't", "aren't", "wasn't", "hasn't", "haven't", "they're", "we're", "it'll"]
FULL = ["does not", "will not", "can not", "cannot", "I am", "it is", "that is", "there is", "I will", "I have", "you are", "is not", "do not", "would not", "did not", "could not", "should not", "are not", "was not", "has not", "have not", "they are", "we are", "it will"]

def contractions(text):
    """Return (all_contractions, contracted_where_choice, full_where_choice)."""
    t = T.mask_urls(text).replace("’", "'")
    allc = len(T.CONTRACTION_RE.findall(t))
    # case-insensitive, so "It's" / "It is" count like "it's" / "it is"
    c = sum(len(re.findall(r"\b" + re.escape(f) + r"\b", t, re.I)) for f in CONTRACTED)
    f = sum(len(re.findall(r"\b" + re.escape(x) + r"\b", t, re.I)) for x in FULL)
    return allc, c, f

IRREG_PP = "been|done|gone|seen|taken|given|made|known|shown|written|found|held|kept|left|lost|put|read|run|sent|set|spent|told|thought|built|bought|brought|caught|chosen|cut|dealt|drawn|driven|eaten|fallen|felt|forgotten|frozen|hidden|hit|led|meant|paid|proven|proved|sold|spoken|stolen|stuck|struck|taught|thrown|understood|won|broken|begun|become|come|hung|lent|rid|shut|split|spread|swept|torn|worn|bound|fed|laid|lit|met|overridden|rewritten|undone|beaten|bent|blown|bred|burnt|cast|dug|fit|flown|grown|let|ridden|risen|sought|shaken|shot|slid|sprung|stood|sung|sunk|swung|woken|wound|withdrawn"
PASSIVE_RE = re.compile(r"\b(?:is|are|was|were|be|been|being|get|gets|got|gotten|getting|'s|'re)\s+(?:(?:not|never|also|already|still|just|only|being|always|usually|often|probably|then|all|also)\s+){0,2}(?:[A-Za-z]{3,}ed|" + IRREG_PP + r")\b", re.I)

def passives(text):
    return len(PASSIVE_RE.findall(T.mask_urls(text)))

# --------------------------------------------------------------- lists, quotes, marks
def list_lines(text):
    return dict(
        num_paren=len(re.findall(r"(?m)^\s*\d{1,2}\)\s", text)),
        num_dot=len(re.findall(r"(?m)^\s*\d{1,2}\.\s+[A-Za-z]", text)),
        bullet_dash=len(re.findall(r"(?m)^\s*- \S", text)),
        bullet_star=len(re.findall(r"(?m)^\s*\* \S", text)),
    )

def quote_punctuation(text):
    """(outside, inside): '"term".' or '"term",' vs a sentence-final word
    followed by .!? inside the closing quote."""
    t = T.mask_urls(text)
    return len(re.findall(r"\"[^\"\n]{1,40}\"[.,]", t)), len(re.findall(r"[a-z]{3,}[.!?]\"(?=\s|$)", t))

def marks(text):
    t = T.mask_urls(text)
    return dict(
        comma=t.count(","), semicolon=t.count(";"), colon=len(re.findall(r":(?!\d)", t)),
        question=t.count("?"), exclaim=t.count("!"), paren=t.count("("),
        dquote=t.count('"') + t.count("“") + t.count("”"),
        ellipsis=len(re.findall(r"\.{3,}|…", t)), em_en_dash=t.count("—") + t.count("–"),
        double_hyphen=len(re.findall(r"(?<!-)--(?!-)", t)),
        percent_attached=len(re.findall(r"\d%", t)), percent_word=len(re.findall(r"\bpercent\b", t, re.I)),
    )

# --------------------------------------------------------------- term forms
TERM_FORMS = {  # key: (regex, case_sensitive)
    "block_chain": (r"\bblock chain\b", False), "blockchain": (r"\bblockchain\b", False),
    "double_spend_hyphen": (r"\bdouble-spend", False), "double_spend_open": (r"\bdouble spend", False),
    "pow_hyphen": (r"\bproof-of-work\b", False), "pow_open": (r"\bproof of work\b", False),
    "e_mail_hyphen": (r"\be-mail\b", False), "email_solid": (r"\bemail\b", False),
    "a_lot": (r"\ba lot\b", False), "alot": (r"\balot\b", False),
    "OK_caps": (r"\bOK\b", True), "okay": (r"\bokay\b", False),
    "etc_period": (r"\betc\.", False), "etc_bare": (r"\betc\b(?!\.)", False),
    "eg": (r"\be\.g\.", False), "eg_comma": (r"\be\.g\.,", False), "ie": (r"\bi\.e\.", False),
    "vs_bare": (r"\bvs\b(?!\.)", False), "vs_period": (r"\bvs\.", False),
    "towards": (r"\btowards\b", False), "toward": (r"\btoward\b", False),
}
_TERM_RX = {k: re.compile(v) if cs else re.compile(v, re.I) for k, (v, cs) in TERM_FORMS.items()}

def term_forms(text):
    t = T.mask_urls(text)
    return {k: len(r.findall(t)) for k, r in _TERM_RX.items()}

# --------------------------------------------------------------- spelling classes
# Three classes, because -ize is correct in both American and Oxford British
# spelling and is therefore not evidence of American usage on its own:
#   NON_US : forms not used in standard American spelling (-ise/-isation/-yse,
#            -our, grey, defence, offence, maths, labelled/labelling,
#            travelled, cancelled, modelled, fulfil, centre, catalogue,
#            whilst, amongst, learnt, spelt, judgement)
#   US_ONLY: forms not used in standard British spelling (-or for -our,
#            gray, defense, offense, math, labeled, traveled, canceled,
#            modeled, fulfill, center, judgment is excluded as it is also
#            standard British legal usage; gotten is counted separately)
#   IZE    : -ize/-ization/-izing forms (American, or British Oxford style)
# Excluded before counting: UI labels, switches, file and function names
# (LABELS below), and anything inside double quotes.
LABELS = re.compile(r"(?i)Minimiz\w* to (?:the )?(?:system )?tray|-minimizetotray|minimize,maximize,close|serialize\.h|boost serialization|\bReorganize\b|Catalog->|->[A-Za-z ]+|\"[^\"\n]*\"")
_IZE_STEMS = r"(?:optimi|reali|recogni|organi|reorgani|minimi|maximi|initiali|seriali|standardi|summari|generali|internationali|critici|decentrali|centrali|formali|priori|amorti|moderni|liberali|synchroni|customi|utili|apologi|emphasi|categori|capitali|moneti|incentivi|penali|characteri|neutrali|locali|globali|populari|legitimi|saniti|stabili|speciali|normali|finali|visuali|memori|randomi|authori)"
NON_US_RE = re.compile(r"(?<![A-Za-z])(?:" + _IZE_STEMS + r"s(?:e|ed|es|ing|ation|ations)|analys(?:e|ed|es|ing)|paralys(?:e|ed)|colour\w*|favour\w*|neighbour\w*|behaviour\w*|honour\w*|labour\w*|flavour\w*|humour\w*|rumour\w*|grey|defence|offence|maths|labell(?:ed|ing)|travell(?:ed|ing)|cancell(?:ed|ing)|modell(?:ed|ing)|fulfil|fulfils|centre|centres|catalogue|whilst|amongst|learnt|spelt|judgement)(?![A-Za-z])", re.I)
US_ONLY_RE = re.compile(r"(?<![A-Za-z])(?:analyz(?:e|ed|es|ing)|paralyz(?:e|ed)|color\w*|favor\w*|neighbor\w*|behavior\w*|honor\w*|labor\w*|flavor\w*|humor\w*|rumor\w*|gray|defense|offense|math|label(?:ed|ing)|travel(?:ed|ing)|cancel(?:ed|ing)|model(?:ed|ing)|fulfill|fulfills|center|centers)(?![A-Za-z])", re.I)
IZE_RE = re.compile(r"(?<![A-Za-z])" + _IZE_STEMS + r"z(?:e|ed|es|ing|ation|ations)(?![A-Za-z])", re.I)
GOTTEN_RE = re.compile(r"\bgotten\b", re.I)

def spelling(text):
    """Return dict of token lists per class (lower-cased), after removing LABELS."""
    t = LABELS.sub(" ", T.mask_urls(text))
    return dict(
        non_us=[m.group(0).lower() for m in NON_US_RE.finditer(t)],
        us_only=[m.group(0).lower() for m in US_ONLY_RE.finditer(t)],
        ize=[m.group(0).lower() for m in IZE_RE.finditer(t)],
        gotten=[m.group(0).lower() for m in GOTTEN_RE.finditer(t)],
    )

# --------------------------------------------------------------- pooled profile
def profile(docs):
    """Pooled feature dictionary for a list of prose strings. Every report
    table that compares corpora uses this function."""
    docs = [d for d in docs if T.words(d)]          # empty documents never count
    text = "\n\n".join(docs)
    toks = T.words(text); nw = len(toks); cnt = Counter(toks)
    sents = [s for d in docs for s in T.sentences(d)]
    sl = [len(T.words(s)) for s in sents if T.words(s)]
    def per1k(x): return round(1000 * x / nw, 2) if nw else None
    dbl = sgl = 0; ify = ifb = 0; verd = 0
    for d in docs:
        a, b = sentence_spacing(d); dbl += a; sgl += b
        a, b = if_you_openers(d); ify += a; ifb += b
        verd += verdict_openers(d)
    allc, cc, ff = contractions(text)
    qo, qi = quote_punctuation(text)
    mk = marks(text); ls = list_lines(text); tf = term_forms(text); sp = spelling(text)
    hed = lexicon_counts(text, "hedges"); bst = lexicon_counts(text, "boosters")
    import statistics
    out = dict(
        documents=len(docs), words=nw, sentences=len(sl),
        mean_sentence_len=round(nw / len(sl), 2) if sl else None,
        median_sentence_len=statistics.median(sl) if sl else None,
        double_space=dbl, single_space=sgl, double_space_share=round(dbl / (dbl + sgl), 3) if dbl + sgl else None,
        contractions_per1k=per1k(allc), contracted_share=round(cc / (cc + ff), 3) if cc + ff else None,
        passive_per_sentence=round(passives(text) / len(sl), 3) if sl else None,
        comma_per1k=per1k(mk["comma"]), semicolon=mk["semicolon"], semicolon_per1k=per1k(mk["semicolon"]),
        colon_per1k=per1k(mk["colon"]), paren_per1k=per1k(mk["paren"]), question_per1k=per1k(mk["question"]),
        exclaim=mk["exclaim"], exclaim_per1k=per1k(mk["exclaim"]), ellipsis=mk["ellipsis"], em_en_dash=mk["em_en_dash"],
        double_hyphen=mk["double_hyphen"], dquote_per1k=per1k(mk["dquote"]),
        quote_punct_outside=qo, quote_punct_inside=qi,
        the_per1k=per1k(cnt["the"]), and_per1k=per1k(cnt["and"]), if_per1k=per1k(cnt["if"]),
        I_per1k=per1k(sum(cnt[w] for w in ["i", "me", "my", "i'm", "i've", "i'll", "i'd"])),
        you_per1k=per1k(sum(cnt[w] for w in ["you", "your", "you're", "you've", "you'll", "you'd"])),
        we_per1k=per1k(sum(cnt[w] for w in ["we", "us", "our", "we're", "we've", "we'll"])),
        will_per1k=per1k(cnt["will"] + cnt["it'll"] + cnt["i'll"] + cnt["we'll"] + cnt["you'll"] + cnt["they'll"]),
        will_bare_per1k=per1k(cnt["will"]), would_per1k=per1k(cnt["would"]),
        if_you_openers=ify, if_you_openers_bare=ifb, verdict_openers=verd,
        it_would_be=len(re.findall(r"\bit would be\b", text, re.I)),
        hedges=sum(hed.values()), hedges_per1k=per1k(sum(hed.values())),
        boosters=sum(bst.values()), boosters_per1k=per1k(sum(bst.values())),
        I_think=hed["I think"], not_sure=hed["I'm not sure"] + hed["not sure"], probably=hed["probably"], maybe=hed["maybe"],
        obviously=bst["obviously"], certainly=bst["certainly"], definitely=bst["definitely"],
        list_num_paren=ls["num_paren"], list_num_dot=ls["num_dot"], bullet_dash=ls["bullet_dash"], bullet_star=ls["bullet_star"],
        percent_attached=mk["percent_attached"], percent_word=mk["percent_word"],
        spelling_non_us=len(sp["non_us"]), spelling_us_only=len(sp["us_only"]), spelling_ize=len(sp["ize"]), gotten=len(sp["gotten"]),
        spelling_non_us_forms=" ".join(sorted(set(sp["non_us"]))), spelling_us_only_forms=" ".join(sorted(set(sp["us_only"]))),
        spelling_ize_forms=" ".join(sorted(set(sp["ize"]))),
    )
    for k, v in tf.items():
        out["term_" + k] = v
    return out

# --------------------------------------------------------------- profile lexicons
# Counted by 02_features.py into data/agg/profile_counts.csv (count, posts,
# post ids) so that every number in PROFILE_ADDENDUM.md is reproducible.
PROFILE_LEXICONS = {
    "crypto_terms": r"\b(?:ecdsa|secp256k1|ripemd-?160|sha-?256|sha-?1|sha256|merkle|blinding|blind signatures?|zero[- ]knowledge|preimage|hash collisions?|collision|elliptic curve|public key|private key|signatures?|nonce|birthday)\b",
    "economics_terms": r"\b(?:seigniorage|fiat|scarcity|scarce|inflation|deflation|deflationary|inflationary|marginal cost|production cost|commodity|commodities|corner(?:ing)? the market|monetary|money supply|medium of exchange|store of value|velocity|liquidity|gresham|central bank|precious metals?)\b",
    "medium_of_exchange": r"\bmedium of exchange\b",
    "compatib": r"\bcompatib\w*",
    "gavin": r"\bgavin\b",
    "plus_one": r"(?:^|(?<=\s))\+1(?=[\s.,]|$)",          # approval, not "+1.23" or "+18%"
    "possessive_my_work": r"\bmy (?:code|design|implementation|idea|plan|system|software|invention|project)\b",
    "personal_life": r"\b(?:my wife|my kids|my children|my family|my girlfriend|my boyfriend|tonight|this morning|at work|my job|my boss|my office|i live|my house|my apartment|my flat|my weekend)\b",
    "appdata_paths": r"%appdata%",
    "wikipedia_links": r"wikipedia\.org",
    "lol_haha": r"\b(?:lol|haha|hehe|rofl|lmao)\b",
    "very_easy_to": r"\bit would be very easy to\b",
    "suppose": r"\bsuppose\b",
}
_PROFILE_RX = {k: re.compile(v, re.I) for k, v in PROFILE_LEXICONS.items()}

def profile_lexicon_counts(raw_text):
    """Counted on the prose before URL masking, so link domains are visible."""
    return {k: len(r.findall(raw_text)) for k, r in _PROFILE_RX.items()}
