#!/usr/bin/env python3
"""Compute per-post and corpus-wide stylometric measurements.

Inputs : analysis/data/posts_clean.jsonl (from 01_extract.py)
Outputs: analysis/post_features.csv              one row per post
         analysis/data/agg/*.csv|json            corpus-wide tables used by the
                                                 report (vocabulary, n-grams,
                                                 spelling variants, punctuation,
                                                 syntax, period/platform/topic
                                                 comparisons, anomalies)

Denominators: unless stated otherwise, rates are per 1,000 word tokens of the
author's own prose (see textutil.py for the definitions), computed over the
"core" corpus = posts with usable prose, excluding post_543 (disputed
authorship) and the four Repost posts (other members' text).
"""
import csv, json, math, os, re, sys, statistics
from collections import Counter, defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textutil as T

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
AGG = os.path.join(DATA, "agg")
os.makedirs(AGG, exist_ok=True)

recs = [json.loads(l) for l in open(os.path.join(DATA, "posts_clean.jsonl"), encoding="utf-8")]

# ----------------------------------------------------------------- lexicons
FUNCTION_WORDS = ["the", "of", "and", "to", "a", "in", "that", "it", "is", "i", "you", "for", "be", "on", "with", "if", "not", "as", "would", "are", "have", "this", "but", "they", "we", "can", "or", "so", "at", "by", "an", "will", "was", "there", "from", "just", "more", "all", "when", "than", "could", "should", "which", "then", "only", "some", "about", "any", "also", "very", "get", "one", "like", "no", "up", "out", "now", "what", "how", "do", "has", "them", "their", "because", "into", "other", "much", "still", "need", "way", "think", "probably", "maybe", "right", "sure", "yes", "yeah", "ok", "no"]
PRONOUNS = {"first_sg": ["i", "me", "my", "mine", "myself", "i'm", "i've", "i'll", "i'd"], "first_pl": ["we", "us", "our", "ours", "we're", "we've", "we'll", "we'd"], "second": ["you", "your", "yours", "you're", "you've", "you'll", "you'd"], "third_he": ["he", "him", "his"], "third_she": ["she", "her", "hers"], "third_they": ["they", "them", "their", "theirs", "they're", "they've", "they'll", "they'd"]}
MODALS = ["would", "could", "should", "might", "may", "can", "will", "must", "shall", "ought", "can't", "won't", "wouldn't", "couldn't", "shouldn't", "cannot"]
# British / American spelling pairs: (british, american). Only words whose
# variants are actually distinct in spelling. Counted on own prose.
SPELLING_PAIRS = [
    ("colour", "color"), ("colours", "colors"), ("behaviour", "behavior"), ("behaviours", "behaviors"), ("favour", "favor"), ("favourite", "favorite"), ("honour", "honor"), ("neighbour", "neighbor"), ("neighbours", "neighbors"), ("labour", "labor"), ("flavour", "flavor"), ("humour", "humor"), ("harbour", "harbor"), ("rumour", "rumor"), ("endeavour", "endeavor"), ("vapour", "vapor"), ("armour", "armor"),
    ("centre", "center"), ("centres", "centers"), ("metre", "meter"), ("litre", "liter"), ("fibre", "fiber"), ("theatre", "theater"),
    ("defence", "defense"), ("offence", "offense"), ("licence", "license"), ("practise", "practice"), ("pretence", "pretense"),
    ("programme", "program"), ("catalogue", "catalog"), ("dialogue", "dialog"), ("analogue", "analog"), ("grey", "gray"), ("cheque", "check"), ("kerb", "curb"), ("tyre", "tire"), ("aluminium", "aluminum"), ("maths", "math"), ("mum", "mom"), ("whilst", "while"), ("amongst", "among"), ("towards", "toward"), ("afterwards", "afterward"), ("forwards", "forward"), ("backwards", "backward"),
    ("travelling", "traveling"), ("travelled", "traveled"), ("cancelled", "canceled"), ("cancelling", "canceling"), ("modelling", "modeling"), ("modelled", "modeled"), ("labelled", "labeled"), ("labelling", "labeling"), ("signalling", "signaling"), ("signalled", "signaled"), ("totalling", "totaling"), ("fuelled", "fueled"), ("marvellous", "marvelous"), ("jewellery", "jewelry"), ("counsellor", "counselor"),
    ("judgement", "judgment"), ("acknowledgement", "acknowledgment"), ("ageing", "aging"), ("enquiry", "inquiry"), ("enquire", "inquire"), ("sceptical", "skeptical"), ("skilful", "skillful"), ("fulfil", "fulfill"), ("enrol", "enroll"), ("instalment", "installment"), ("plough", "plow"), ("pyjamas", "pajamas"), ("mould", "mold"), ("moult", "molt"), ("smoulder", "smolder"), ("draught", "draft"), ("learnt", "learned"), ("spelt", "spelled"), ("burnt", "burned"), ("dreamt", "dreamed"), ("leapt", "leaped"), ("smelt", "smelled"), ("spoilt", "spoiled"), ("gotten", "got"),
    ("realise", "realize"), ("realised", "realized"), ("realises", "realizes"), ("realising", "realizing"), ("recognise", "recognize"), ("recognised", "recognized"), ("recognises", "recognizes"), ("organise", "organize"), ("organised", "organized"), ("organisation", "organization"), ("optimise", "optimize"), ("optimised", "optimized"), ("optimisation", "optimization"), ("optimisations", "optimizations"), ("minimise", "minimize"), ("minimised", "minimized"), ("maximise", "maximize"), ("prioritise", "prioritize"), ("prioritised", "prioritized"), ("prioritising", "prioritizing"), ("prioritisation", "prioritization"), ("synchronise", "synchronize"), ("synchronised", "synchronized"), ("synchronisation", "synchronization"), ("serialise", "serialize"), ("serialised", "serialized"), ("serialisation", "serialization"), ("initialise", "initialize"), ("initialised", "initialized"), ("initialisation", "initialization"), ("authorise", "authorize"), ("authorised", "authorized"), ("authorisation", "authorization"), ("customise", "customize"), ("customised", "customized"), ("randomise", "randomize"), ("randomised", "randomized"), ("standardise", "standardize"), ("specialise", "specialize"), ("specialised", "specialized"), ("stabilise", "stabilize"), ("stabilised", "stabilized"), ("utilise", "utilize"), ("utilised", "utilized"), ("apologise", "apologize"), ("apologised", "apologized"), ("emphasise", "emphasize"), ("emphasised", "emphasized"), ("summarise", "summarize"), ("summarised", "summarized"), ("centralise", "centralize"), ("centralised", "centralized"), ("decentralise", "decentralize"), ("decentralised", "decentralized"), ("decentralisation", "decentralization"), ("formalise", "formalize"), ("formalised", "formalized"), ("finalise", "finalize"), ("finalised", "finalized"), ("visualise", "visualize"), ("memorise", "memorize"), ("normalise", "normalize"), ("normalised", "normalized"), ("generalise", "generalize"), ("generalised", "generalized"), ("categorise", "categorize"), ("categorised", "categorized"), ("analyse", "analyze"), ("analysed", "analyzed"), ("analysing", "analyzing"), ("paralyse", "paralyze"), ("catalyse", "catalyze"), ("capitalise", "capitalize"), ("capitalised", "capitalized"), ("monetise", "monetize"), ("monetised", "monetized"), ("incentivise", "incentivize"), ("penalise", "penalize"), ("penalised", "penalized"), ("characterise", "characterize"), ("characterised", "characterized"), ("neutralise", "neutralize"), ("neutralised", "neutralized"), ("equalise", "equalize"), ("localise", "localize"), ("localised", "localized"), ("localisation", "localization"), ("globalise", "globalize"), ("popularise", "popularize"), ("criticise", "criticize"), ("criticised", "criticized"), ("legitimise", "legitimize"), ("maximised", "maximized"), ("minimising", "minimizing"), ("maximising", "maximizing"), ("sanitise", "sanitize"), ("sanitised", "sanitized"), ("scrutinise", "scrutinize"), ("securitise", "securitize"), ("trivialise", "trivialize"), ("centralising", "centralizing"), ("optimising", "optimizing"), ("recognising", "recognizing"), ("realisation", "realization"), ("initialising", "initializing"), ("synchronising", "synchronizing"), ("serialising", "serializing"),
]
# Other spelling / form alternatives worth counting (not nationality markers)
FORM_ALTERNATIVES = [
    ("e-mail", "email"), ("web site", "website"), ("on-line", "online"), ("set up", "setup"), ("log in", "login"), ("back up", "backup"), ("cannot", "can not"), ("OK", "okay"), ("ok", "Ok"), ("alright", "all right"), ("a lot", "alot"), ("bitcoin", "Bitcoin"), ("Bitcoin", "BitCoin"), ("peer-to-peer", "peer to peer"), ("p2p", "P2P"), ("double-spend", "double spend"), ("time-stamp", "timestamp"), ("proof-of-work", "proof of work"), ("e-cash", "ecash"), ("re-send", "resend"), ("re-broadcast", "rebroadcast"), ("grey", "gray"), ("anyways", "anyway"), ("till", "until"), ("'til", "until"), ("doesn't", "does not"), ("won't", "will not"), ("can't", "can not"), ("I'm", "I am"), ("it's", "it is"), ("that's", "that is"), ("there's", "there is"), ("I'll", "I will"), ("I've", "I have"), ("you're", "you are"), ("isn't", "is not"), ("don't", "do not"), ("wouldn't", "would not"), ("didn't", "did not"), ("couldn't", "could not"), ("shouldn't", "should not"), ("aren't", "are not"), ("wasn't", "was not"), ("hasn't", "has not"), ("haven't", "have not"), ("they're", "they are"), ("we're", "we are"), ("we'll", "we will"), ("it'll", "it will"), ("you'll", "you will"), ("I'd", "I would"), ("you'd", "you would"), ("it'd", "it would"), ("could've", "could have"), ("would've", "would have"), ("should've", "should have"), ("might've", "might have"), ("what's", "what is"), ("here's", "here is"), ("let's", "let us"), ("who's", "who is"), ("how's", "how is"), ("where's", "where is"), ("that'll", "that will"), ("there'll", "there will"), ("who'd", "who would"), ("they'll", "they will"), ("he's", "he is"), ("she's", "she is"), ("we've", "we have"), ("you've", "you have"), ("they've", "they have"), ("hadn't", "had not"), ("weren't", "were not"), ("mustn't", "must not"), ("needn't", "need not"), ("ain't", "is not"),
]
IRREG_PP = "been|done|gone|seen|taken|given|made|known|shown|written|found|held|kept|left|lost|put|read|run|sent|set|spent|told|thought|built|bought|brought|caught|chosen|cut|dealt|drawn|driven|eaten|fallen|felt|forgotten|frozen|hidden|hit|led|meant|paid|proven|proved|sold|spoken|stolen|stuck|struck|taught|thrown|understood|won|broken|begun|become|come|hung|lent|rid|shut|split|spread|swept|torn|worn|bound|fed|laid|lit|met|overridden|rewritten|undone|beaten|bent|blown|bred|burnt|cast|dug|fit|flown|grown|let|ridden|risen|sought|shaken|shot|slid|sprung|stood|sung|sunk|swung|woken|wound|withdrawn"
PASSIVE_RE = re.compile(r"\b(?:is|are|was|were|be|been|being|get|gets|got|gotten|getting|'s|'re)\s+(?:(?:not|never|also|already|still|just|only|being|always|usually|often|probably|then|all|also)\s+){0,2}(?:[A-Za-z]{3,}ed|" + IRREG_PP + r")\b", re.I)
EXPRESSIONS = {  # curated recurring expressions / discourse markers (case-sensitive where capitalised)
    "I think": r"\bI think\b", "I don't think": r"\bI don't think\b", "I'm not sure": r"\bI'm not sure\b", "not sure": r"\bnot sure\b",
    "I guess": r"\bI guess\b", "I suppose": r"\bI suppose\b", "I believe": r"\bI believe\b", "I wonder": r"\bI wonder\b", "I know": r"\bI know\b",
    "I'd rather": r"\bI'd rather\b", "I'd like": r"\bI'd like\b", "I'll": r"\bI'll\b", "I'm working on": r"\bI'm working on\b", "I've been": r"\bI've been\b",
    "in theory": r"\bin theory\b", "in practice": r"\bin practice\b", "in general": r"\bin general\b", "in that case": r"\bin that case\b",
    "in the meantime": r"\bin the meantime\b", "at some point": r"\bat some point\b", "for now": r"\bfor now\b", "right now": r"\bright now\b",
    "at least": r"\bat least\b", "as long as": r"\bas long as\b", "as far as": r"\bas far as\b", "so far": r"\bso far\b", "in case": r"\bin case\b",
    "it would be": r"\bit would be\b", "it would be nice": r"\bit would be nice\b", "would be nice": r"\bwould be nice\b", "it should be": r"\bit should be\b",
    "there's no": r"\bthere's no\b", "there is no": r"\bthere is no\b", "the only": r"\bthe only\b", "ought to": r"\bought to\b",
    "sort of": r"\bsort of\b", "kind of": r"\bkind of\b", "a lot": r"\ba lot\b", "a little": r"\ba little\b", "a bit": r"\ba bit\b", "pretty much": r"\bpretty much\b",
    "probably": r"\bprobably\b", "maybe": r"\bmaybe\b", "actually": r"\bactually\b", "basically": r"\bbasically\b", "obviously": r"\bobviously\b",
    "certainly": r"\bcertainly\b", "definitely": r"\bdefinitely\b", "of course": r"\bof course\b", "anyway": r"\banyway\b", "hopefully": r"\bhopefully\b",
    "unfortunately": r"\bunfortunately\b", "essentially": r"\bessentially\b", "typically": r"\btypically\b", "usually": r"\busually\b", "really": r"\breally\b",
    "very": r"\bvery\b", "quite": r"\bquite\b", "rather": r"\brather\b", "pretty": r"\bpretty\b", "exactly": r"\bexactly\b", "completely": r"\bcompletely\b",
    "BTW": r"\bBTW\b", "FWIW": r"\bFWIW\b", "IMO": r"\bIMO\b", "AFAIK": r"\bAFAIK\b", "e.g.": r"\be\.g\.", "i.e.": r"\bi\.e\.", "etc": r"\betc\b", "vs": r"\bvs\b",
    "Thanks": r"\bThanks\b", "Thank you": r"\bThank you\b", "Sorry": r"\bSorry\b", "sorry": r"\bsorry\b", "please": r"\bplease\b", "Please": r"\bPlease\b",
    "Yes": r"\bYes\b", "Yeah": r"\bYeah\b", "Nope": r"\bNope\b", "No,": r"\bNo,", "Right": r"\bRight\b", "OK": r"\bOK\b", "okay": r"\bokay\b", "True": r"\bTrue\b",
    "Good idea": r"\bGood idea\b", "good idea": r"\bgood idea\b", "good point": r"\bgood point\b", "Good question": r"\bGood question\b", "Good catch": r"\bGood catch\b",
    "Nice": r"\bNice\b", "Cool": r"\bCool\b", "Great": r"\bGreat\b", "Welcome": r"\bWelcome\b", "Heh": r"\bHeh\b", "Hmm": r"\bHmm\b", "LOL": r"\bLOL\b",
    "I agree": r"\bI agree\b", "You're right": r"\bYou're right\b", "you're right": r"\byou're right\b", "That's right": r"\bThat's right\b", "makes sense": r"\bmakes sense\b",
    "the problem is": r"\bthe problem is\b", "the thing is": r"\bthe thing is\b", "the key is": r"\bthe key is\b", "the trick is": r"\bthe trick is\b", "worst case": r"\bworst case\b",
    "even if": r"\beven if\b", "if so": r"\bif so\b", "if not": r"\bif not\b", "unless": r"\bunless\b", "instead": r"\binstead\b", "otherwise": r"\botherwise\b",
    "however": r"\bhowever\b", "therefore": r"\btherefore\b", "thus": r"\bthus\b", "hence": r"\bhence\b", "although": r"\balthough\b", "though": r"\bthough\b",
    "whilst": r"\bwhilst\b", "amongst": r"\bamongst\b", "among": r"\bamong\b", "towards": r"\btowards\b", "toward": r"\btoward\b", "until": r"\buntil\b", "till": r"\btill\b",
    "in order to": r"\bin order to\b", "as well as": r"\bas well as\b", "a bunch of": r"\ba bunch of\b", "a couple": r"\ba couple\b", "a few": r"\ba few\b", "lots of": r"\blots of\b",
    "nutshell": r"\bnutshell\b", "huge": r"\bhuge\b", "bogged down": r"\bbogged down\b", "out the door": r"\bout the door\b", "handy": r"\bhandy\b", "neat": r"\bneat\b",
    "nifty": r"\bnifty\b", "kludge": r"\bkludge\b", "hack": r"\bhack\b", "quirky": r"\bquirky\b", "silly": r"\bsilly\b", "clunky": r"\bclunky\b", "messy": r"\bmessy\b",
    "practical": r"\bpractical\b", "impractical": r"\bimpractical\b", "trivial": r"\btrivial\b", "convenient": r"\bconvenient\b", "overhead": r"\boverhead\b", "hassle": r"\bhassle\b",
    "trusted third party": r"\btrusted third party\b", "double-spend": r"\bdouble.spend", "proof-of-work": r"\bproof.of.work\b", "block chain": r"\bblock chain\b", "blockchain": r"\bblockchain\b",
    "nobody": r"\bnobody\b", "no one": r"\bno one\b", "anyone": r"\banyone\b", "someone": r"\bsomeone\b", "everyone": r"\beveryone\b", "anybody": r"\banybody\b", "somebody": r"\bsomebody\b", "everybody": r"\beverybody\b",
}

# ----------------------------------------------------------------- helpers
def prose_of(r):
    return "\n".join(s["text"] for s in r["segments"] if s["type"] == "own").strip()

def period_of(ts):
    y, m = ts[:4], int(ts[5:7])
    if y == "2009" and m < 6: return "P1 2009-02 (P2P Foundation)"
    if y == "2009": return "P2 2009-11..12 (forum start)"
    if y == "2010" and m <= 6: return "P3 2010-01..06"
    if y == "2010" and m <= 9: return "P4 2010-07..09"
    if y == "2010": return "P5 2010-10..12"
    return "P6 2014 (disputed)"

TOPIC_KW = {
    "code_build": r"\b(compile|compiler|build|makefile|gcc|g\+\+|boost|wxwidgets|wx|svn|rev \d+|linux|ubuntu|windows|mac|osx|binary|binaries|library|libraries|dll|debug|crash|bug|patch|json-rpc|rpc|command line|daemon|bitcoind|install|tarball|source code|release candidate|rc\d|0\.\d\.\d+)\b",
    "protocol_design": r"\b(block chain|blocks?|proof-of-work|hash(es|ing)?|nonce|difficulty|node|nodes|network|double.spend|transaction|transactions|tx|inputs?|outputs?|script|signature|signatures|public key|private key|chain|peer|peers|broadcast|relay|timestamp|confirmation|confirmations|orphan|fork|protocol|generation|generate|mining|miners?|cpu|gpu|sse2|pool|seed|irc|dns|port|nat|tor|proxy|anonymous|anonymity|privacy)\b",
    "economics": r"\b(currency|currencies|money|value|price|prices|inflation|deflation|gold|dollar|dollars|fiat|central bank|banks?|economy|economic|market|markets|exchange|exchanges|supply|demand|scarce|scarcity|worth|coins? per|cents?|usd|trade|trading|merchants?|payments?|micropayments?|fee|fees|bubble|speculat|investment|invest)\b",
}

def topic_of(text):
    low = text.lower()
    scores = {k: len(re.findall(v, low)) for k, v in TOPIC_KW.items()}
    n = max(1, len(T.words(text)))
    scores = {k: v / n for k, v in scores.items()}
    best = max(scores, key=scores.get)
    if scores[best] < 0.02:
        return "general_conversational"
    return best

def syllables(w):
    w = w.lower()
    v = re.findall(r"[aeiouy]+", w)
    n = len(v)
    if w.endswith("e") and not w.endswith(("le", "ee")) and n > 1:
        n -= 1
    return max(1, n)

# ----------------------------------------------------------------- per-post
rows = []
corpus_tokens = []          # (post_id, token) for core corpus
core_ids = set()
post_prose = {}
for r in recs:
    prose = prose_of(r)
    post_prose[r["post_id"]] = prose
    flags = set(r["flags"])
    is_core = r["usable_for_prose_stats"] and "disputed_authorship" not in flags and "repost_of_other_members" not in flags and len(prose.strip()) > 0
    toks = T.words(prose)
    toks_cased = T.words(prose, lower=False)
    sents = T.sentences(prose)
    sent_lens = [len(T.words(s)) for s in sents]
    sent_lens_nz = [x for x in sent_lens if x > 0]
    nw = len(toks)
    masked = T.mask_urls(prose)
    nchar = len(prose)
    def per1k(x): return round(1000.0 * x / nw, 2) if nw else None
    cnt = Counter(toks)
    paragraphs = [p for p in re.split(r"\n\s*\n", prose) if p.strip()]
    double_space = len(re.findall(r"[.!?][\"')]*  +[A-Z\"(]", prose))
    single_space = len(re.findall(r"[.!?][\"')]* [A-Z\"(]", prose))
    row = dict(
        file=r["file"], post_id=r["post_id"], platform=r["platform"], timestamp=r["timestamp"], date=r["timestamp"][:10],
        period=period_of(r["timestamp"]), title=r["title"], is_reply=r["title"].startswith("Re:"),
        alignment=r["alignment"], flags=";".join(sorted(flags)), core_corpus=is_core,
        n_quote_blocks=sum(1 for s in r["segments"] if s["type"] == "quoteheader"),
        n_code_blocks=sum(1 for s in r["segments"] if s["type"] in ("code",)),
        n_inline_code_lines=sum(s["text"].count("\n") or 1 for s in r["segments"] if s["type"] == "inline_code"),
        n_emoticons=sum(1 for s in r["segments"] if s["type"] == "emoticon" and not s["text"].startswith("http")),
        n_urls=len(T.URL_RE.findall(prose)),
        n_chars=nchar, n_words=nw, n_sentences=len(sents), n_paragraphs=len(paragraphs),
        mean_sentence_len=round(statistics.mean(sent_lens_nz), 2) if sent_lens_nz else None,
        median_sentence_len=statistics.median(sent_lens_nz) if sent_lens_nz else None,
        sd_sentence_len=round(statistics.pstdev(sent_lens_nz), 2) if len(sent_lens_nz) > 1 else None,
        max_sentence_len=max(sent_lens_nz) if sent_lens_nz else None,
        mean_word_len=round(sum(len(t) for t in toks) / nw, 3) if nw else None,
        mean_syllables=round(sum(syllables(t) for t in toks) / nw, 3) if nw else None,
        type_token_ratio=round(len(cnt) / nw, 3) if nw else None,
        hapax_ratio=round(sum(1 for v in cnt.values() if v == 1) / nw, 3) if nw else None,
        long_words_pct=round(100 * sum(1 for t in toks if len(t) >= 7) / nw, 2) if nw else None,
        mean_paragraph_sentences=round(len(sents) / len(paragraphs), 2) if paragraphs else None,
        # punctuation (raw counts; rates per 1k words below)
        c_comma=masked.count(","), c_semicolon=masked.count(";"), c_colon=len(re.findall(r":(?!\d)", masked)),
        c_period=len(re.findall(r"(?<!\.)\.(?!\.)", masked)), c_question=masked.count("?"), c_exclaim=masked.count("!"),
        c_paren_open=masked.count("("), c_paren_close=masked.count(")"), c_dquote=masked.count('"') + masked.count("“") + masked.count("”"),
        c_squote_quotation=len(re.findall(r"(?<![A-Za-z])'[^'\n]{1,80}'(?![A-Za-z])", masked)),
        c_apostrophe=len(re.findall(r"[A-Za-z]['’][A-Za-z]", masked)), c_curly_apostrophe=masked.count("’") + masked.count("‘"),
        c_ellipsis=len(re.findall(r"\.{3,}|…", masked)), c_double_hyphen=len(re.findall(r"(?<!-)--(?!-)", masked)),
        c_spaced_hyphen=len(re.findall(r"\s-\s", masked)), c_en_dash=masked.count("–"), c_em_dash=masked.count("—"),
        c_hyphen_compound=len(T.HYPHEN_RE.findall(masked)), c_slash=len(re.findall(r"(?<=[A-Za-z])/(?=[A-Za-z])", masked)),
        c_ampersand=masked.count("&"), c_asterisk=masked.count("*"), c_percent=masked.count("%"), c_numbers=len(T.NUM_RE.findall(masked)),
        c_allcaps_words=sum(1 for t in toks_cased if len(t) >= 2 and t.isupper() and t not in ("I",)),
        c_sent_start_lower=sum(1 for s in sents if s[:1].islower()),
        c_sent_end_no_punct=sum(1 for s in sents if not re.search(r"[.!?][\"')]*$", s)),
        c_double_space_after_sentence=double_space, c_single_space_after_sentence=single_space,
        c_contractions=len(T.CONTRACTION_RE.findall(masked)),
        c_passive=len(PASSIVE_RE.findall(masked)),
        c_if=cnt["if"], c_questions_sentences=sum(1 for s in sents if s.rstrip().endswith("?")),
        c_exclaim_sentences=sum(1 for s in sents if s.rstrip().endswith("!")),
        c_fragments=sum(1 for s in sents if 0 < len(T.words(s)) <= 3),
        c_list_lines=len(re.findall(r"(?m)^\s*(?:[-*•]|\d+[.)])\s", prose)),
    )
    for grp, ws in PRONOUNS.items():
        row["pron_" + grp] = sum(cnt[w] for w in ws)
    row["modals"] = sum(cnt[w] for w in MODALS)
    for m in ["would", "could", "should", "might", "may", "can", "will", "must"]:
        row["modal_" + m] = cnt[m]
    for w in ["the", "of", "and", "to", "a", "in", "that", "it", "is", "i", "you", "if", "not", "but", "would", "just", "so", "very", "probably", "maybe"]:
        row["fw_" + w] = per1k(cnt[w])
    # rates
    for k in list(row.keys()):
        if k.startswith("c_") and nw:
            row["r_" + k[2:] + "_per1k"] = per1k(row[k])
    row["contractions_per1k"] = per1k(row["c_contractions"])
    row["passive_per_sentence"] = round(row["c_passive"] / len(sents), 3) if sents else None
    row["question_sentence_pct"] = round(100 * row["c_questions_sentences"] / len(sents), 2) if sents else None
    row["double_space_share"] = round(double_space / (double_space + single_space), 3) if (double_space + single_space) else None
    row["topic"] = topic_of(prose)
    rows.append(row)
    if is_core:
        core_ids.add(r["post_id"])
        corpus_tokens.extend((r["post_id"], t) for t in toks)

fieldnames = list(rows[0].keys())
with open(os.path.join(HERE, "..", "post_features.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

# ----------------------------------------------------------------- corpus-wide
core = [r for r in recs if r["post_id"] in core_ids]
core_rows = {r["post_id"]: r for r in rows}
ALL_TOK = Counter(t for _, t in corpus_tokens)
DOC_FREQ = Counter()
for pid in core_ids:
    DOC_FREQ.update(set(T.words(post_prose[pid])))
N_TOK = sum(ALL_TOK.values())
N_CORE = len(core_ids)
json.dump(dict(n_core_posts=N_CORE, n_tokens=N_TOK, n_types=len(ALL_TOK), n_sentences=sum(core_rows[p]["n_sentences"] for p in core_ids),
               n_chars=sum(core_rows[p]["n_chars"] for p in core_ids)), open(os.path.join(AGG, "corpus_summary.json"), "w"), indent=1)

def write_csv(name, header, rows_):
    with open(os.path.join(AGG, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(header); w.writerows(rows_)

# vocabulary
write_csv("word_freq.csv", ["word", "count", "per1k", "doc_freq", "doc_pct"],
          [(w, c, round(1000 * c / N_TOK, 3), DOC_FREQ[w], round(100 * DOC_FREQ[w] / N_CORE, 1)) for w, c in ALL_TOK.most_common()])

# n-grams (word) with doc frequency
def ngrams(tokens, n):
    return zip(*[tokens[i:] for i in range(n)])
for n in (2, 3, 4, 5):
    c, d = Counter(), Counter()
    for pid in core_ids:
        toks = T.words(post_prose[pid])
        grams = list(ngrams(toks, n))
        c.update(grams); d.update(set(grams))
    write_csv(f"word_{n}grams.csv", ["ngram", "count", "doc_freq"], [(" ".join(g), k, d[g]) for g, k in c.most_common(3000) if k >= 3])
# character n-grams (on lower-cased prose with URLs masked, whitespace collapsed to single space)
for n in (3, 4):
    c = Counter()
    for pid in core_ids:
        t = re.sub(r"\s+", " ", T.mask_urls(post_prose[pid]).lower())
        c.update(t[i:i + n] for i in range(len(t) - n + 1))
    write_csv(f"char_{n}grams.csv", ["ngram", "count"], [(g.replace("\n", "\\n"), k) for g, k in c.most_common(2000)])

# sentence openers / enders
op, en = Counter(), Counter(); op_d, en_d = Counter(), Counter()
for pid in core_ids:
    seen_o, seen_e = set(), set()
    for s in T.sentences(post_prose[pid]):
        ws = T.words(s, lower=False)
        if not ws: continue
        o = ws[0]; e = ws[-1].lower()
        op[o] += 1; en[e] += 1; seen_o.add(o); seen_e.add(e)
    op_d.update(seen_o); en_d.update(seen_e)
write_csv("sentence_openers.csv", ["first_word", "count", "doc_freq"], [(w, c, op_d[w]) for w, c in op.most_common(300)])
write_csv("sentence_enders.csv", ["last_word", "count", "doc_freq"], [(w, c, en_d[w]) for w, c in en.most_common(300)])
# two-word openers
op2 = Counter(); op2_d = Counter()
for pid in core_ids:
    seen = set()
    for s in T.sentences(post_prose[pid]):
        ws = T.words(s, lower=False)
        if len(ws) >= 2:
            g = ws[0] + " " + ws[1]; op2[g] += 1; seen.add(g)
    op2_d.update(seen)
write_csv("sentence_openers_2w.csv", ["first_two_words", "count", "doc_freq"], [(w, c, op2_d[w]) for w, c in op2.most_common(300)])

# expressions
rows_ = []
for name, pat in EXPRESSIONS.items():
    rx = re.compile(pat)
    c = 0; d = 0
    for pid in core_ids:
        k = len(rx.findall(T.mask_urls(post_prose[pid])))
        c += k; d += 1 if k else 0
    rows_.append((name, c, round(1000 * c / N_TOK, 3), d, round(100 * d / N_CORE, 1)))
rows_.sort(key=lambda x: -x[1])
write_csv("expressions.csv", ["expression", "count", "per1k_words", "doc_freq", "doc_pct"], rows_)

# spelling variants (word-bounded, case-insensitive) with doc freq, on core prose
def count_word(w):
    rx = re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I)
    c = 0; docs = []
    for pid in sorted(core_ids):
        k = len(rx.findall(T.mask_urls(post_prose[pid])))
        if k: c += k; docs.append(pid)
    return c, docs
sp_rows = []
for br, am in SPELLING_PAIRS:
    cb, db = count_word(br); ca, da = count_word(am)
    if cb or ca:
        sp_rows.append((br, am, cb, len(db), ca, len(da), " ".join(map(str, db[:12])), " ".join(map(str, da[:12]))))
write_csv("spelling_british_american.csv", ["british", "american", "british_count", "british_docs", "american_count", "american_docs", "british_post_ids", "american_post_ids"], sp_rows)
# generic -ise/-ize and -our/-or scans to catch pairs not in the list
ise = Counter(); ize = Counter(); our = Counter(); yse = Counter(); yze = Counter()
for w, c in ALL_TOK.items():
    if re.search(r"i[sz](e|ed|es|ing|ation|ations)$", w) and len(w) > 6:
        (ise if re.search(r"is(e|ed|es|ing|ation|ations)$", w) else ize)[w] += c
    if re.search(r"ou?r(s|ed|ing|ite|able)?$", w) and len(w) > 5:
        our[w] += c
    if re.search(r"y[sz](e|ed|es|ing)$", w):
        (yse if "ys" in w[-5:] else yze)[w] += c
json.dump(dict(ise=ise.most_common(), ize=ize.most_common(), yse=yse.most_common(), yze=yze.most_common()), open(os.path.join(AGG, "ise_ize_scan.json"), "w"), indent=1)
# form alternatives (case-sensitive where the alternative differs only by case)
fa_rows = []
for a, b in FORM_ALTERNATIVES:
    def cnt_cs(x):
        rx = re.compile(r"(?<![A-Za-z'])" + re.escape(x) + r"(?![A-Za-z])")
        c = 0; d = 0
        for pid in core_ids:
            k = len(rx.findall(T.mask_urls(post_prose[pid]))); c += k; d += bool(k)
        return c, d
    ca, da = cnt_cs(a); cb, db = cnt_cs(b)
    if ca or cb:
        fa_rows.append((a, ca, da, b, cb, db))
write_csv("form_alternatives.csv", ["form_a", "count_a", "docs_a", "form_b", "count_b", "docs_b"], fa_rows)

# capitalisation of key terms
cap_rows = []
for term in ["bitcoin", "bitcoins", "bitcoin address", "block chain", "proof-of-work", "internet", "web", "linux", "windows", "mac", "tor", "irc", "svn", "json-rpc", "rpc", "cpu", "gpu", "ok", "btc", "p2p", "e-mail", "email", "wallet", "node", "nodes"]:
    forms = Counter()
    rx = re.compile(r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])", re.I)
    for pid in core_ids:
        for m in rx.finditer(T.mask_urls(post_prose[pid])):
            forms[m.group(0)] += 1
    for f, c in forms.most_common():
        cap_rows.append((term, f, c))
write_csv("capitalisation.csv", ["term", "surface_form", "count"], cap_rows)

# punctuation / syntax corpus totals
tot = Counter()
for pid in core_ids:
    for k, v in core_rows[pid].items():
        if k.startswith("c_") and isinstance(v, (int, float)):
            tot[k] += v
tot_rows = [(k[2:], v, round(1000 * v / N_TOK, 3), sum(1 for pid in core_ids if core_rows[pid][k]), round(100 * sum(1 for pid in core_ids if core_rows[pid][k]) / N_CORE, 1)) for k, v in sorted(tot.items(), key=lambda x: -x[1])]
write_csv("punctuation_syntax_totals.csv", ["feature", "count", "per1k_words", "doc_freq", "doc_pct"], tot_rows)
# pronoun & modal totals
pm = Counter()
for pid in core_ids:
    for k, v in core_rows[pid].items():
        if k.startswith(("pron_", "modal_", "modals")):
            pm[k] += v
write_csv("pronouns_modals.csv", ["feature", "count", "per1k_words"], [(k, v, round(1000 * v / N_TOK, 3)) for k, v in pm.most_common()])

# function-word profile vs. a reference distribution is not available offline; report ranks only
# period / platform / topic / length comparisons
def group_stats(key_fn, name):
    groups = defaultdict(list)
    for pid in core_ids:
        groups[key_fn(core_rows[pid])].append(pid)
    out = []
    feats = ["mean_sentence_len", "mean_word_len", "type_token_ratio", "contractions_per1k", "r_comma_per1k", "r_semicolon_per1k", "r_colon_per1k", "r_paren_open_per1k", "r_question_per1k", "r_exclaim_per1k", "r_ellipsis_per1k", "r_double_hyphen_per1k", "r_dquote_per1k", "passive_per_sentence", "fw_the", "fw_i", "fw_you", "fw_it", "fw_would", "fw_if", "fw_probably", "double_space_share"]
    for g, pids in sorted(groups.items()):
        nw = sum(core_rows[p]["n_words"] for p in pids)
        # pooled rates (token-weighted) are more robust than mean of per-post rates for short posts
        pooled = {}
        for f in feats:
            if f.startswith("r_") or f.startswith("fw_") or f == "contractions_per1k":
                base = "c_" + f[2:-6] if f.startswith("r_") else None
                if base:
                    pooled[f] = round(1000 * sum(core_rows[p][base] for p in pids) / nw, 2) if nw else None
                elif f == "contractions_per1k":
                    pooled[f] = round(1000 * sum(core_rows[p]["c_contractions"] for p in pids) / nw, 2) if nw else None
                else:
                    wd = f[3:]
                    pooled[f] = round(1000 * sum(Counter(T.words(post_prose[p]))[wd] for p in pids) / nw, 2) if nw else None
            elif f == "mean_sentence_len":
                ns = sum(core_rows[p]["n_sentences"] for p in pids); pooled[f] = round(nw / ns, 2) if ns else None
            elif f == "mean_word_len":
                pooled[f] = round(sum(len(t) for p in pids for t in T.words(post_prose[p])) / nw, 3) if nw else None
            elif f == "type_token_ratio":
                # TTR depends on sample size; report on first 3000 tokens of the pooled group
                toks = [t for p in sorted(pids) for t in T.words(post_prose[p])][:3000]
                pooled[f] = round(len(set(toks)) / len(toks), 3) if toks else None
            elif f == "passive_per_sentence":
                ns = sum(core_rows[p]["n_sentences"] for p in pids); pooled[f] = round(sum(core_rows[p]["c_passive"] for p in pids) / ns, 3) if ns else None
            elif f == "double_space_share":
                d = sum(core_rows[p]["c_double_space_after_sentence"] for p in pids); s_ = sum(core_rows[p]["c_single_space_after_sentence"] for p in pids)
                pooled[f] = round(d / (d + s_), 3) if d + s_ else None
        out.append(dict(group=g, n_posts=len(pids), n_words=nw, **pooled))
    with open(os.path.join(AGG, f"compare_{name}.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    return out
group_stats(lambda r: r["period"], "period")
group_stats(lambda r: r["platform"], "platform")
group_stats(lambda r: r["topic"], "topic")
group_stats(lambda r: "A <50 words" if r["n_words"] < 50 else "B 50-149" if r["n_words"] < 150 else "C 150-299" if r["n_words"] < 300 else "D 300+", "length")
group_stats(lambda r: r["timestamp"][:7], "month")
group_stats(lambda r: "reply" if r["is_reply"] else "original", "reply_vs_original")

# anomalies: z-scores for posts with >= 80 words on robust features
feats_z = ["mean_sentence_len", "mean_word_len", "contractions_per1k", "r_comma_per1k", "r_paren_open_per1k", "r_question_per1k", "r_exclaim_per1k", "r_dquote_per1k", "fw_the", "fw_i", "fw_you", "fw_it", "double_space_share", "passive_per_sentence", "type_token_ratio"]
big = [core_rows[p] for p in core_ids if core_rows[p]["n_words"] >= 80]
stats = {}
for f in feats_z:
    vals = [r[f] for r in big if r[f] is not None]
    stats[f] = (statistics.mean(vals), statistics.pstdev(vals) or 1e-9)
an_rows = []
for r in big:
    zs = {f: (r[f] - stats[f][0]) / stats[f][1] for f in feats_z if r[f] is not None}
    score = math.sqrt(sum(z * z for z in zs.values()) / len(zs))
    top = sorted(zs.items(), key=lambda x: -abs(x[1]))[:4]
    an_rows.append((r["file"], r["timestamp"], r["title"][:60], r["n_words"], round(score, 2), "; ".join(f"{f}={r[f]} (z={z:+.1f})" for f, z in top), r["flags"]))
an_rows.sort(key=lambda x: -x[4])
write_csv("anomalies_zscore.csv", ["file", "timestamp", "title", "n_words", "rms_z", "top_deviations", "flags"], an_rows)

# duplicates / near duplicates of own prose (shingle Jaccard on 5-word shingles)
def shingles(t, k=6):
    w = T.words(t)
    return set(" ".join(w[i:i + k]) for i in range(len(w) - k + 1))
sh = {pid: shingles(post_prose[pid]) for pid in post_prose if len(T.words(post_prose[pid])) >= 12}
dup_rows = []
pids = sorted(sh)
for i, a in enumerate(pids):
    for b in pids[i + 1:]:
        inter = len(sh[a] & sh[b])
        if inter >= 3:
            jac = inter / len(sh[a] | sh[b])
            if jac >= 0.05 or inter >= 8:
                dup_rows.append((a, b, inter, round(jac, 3), " ".join(sorted(sh[a] & sh[b])[:1])))
write_csv("near_duplicates.csv", ["post_id_a", "post_id_b", "shared_6word_shingles", "jaccard", "example_shared_shingle"], dup_rows)
# repeated sentences across posts (exact, >= 6 words)
sent_occ = defaultdict(list)
for pid in core_ids:
    for s in T.sentences(post_prose[pid]):
        if len(T.words(s)) >= 6:
            sent_occ[re.sub(r"\s+", " ", s.strip().lower())].append(pid)
write_csv("repeated_sentences.csv", ["sentence", "n_posts", "post_ids"], [(s, len(set(p)), " ".join(map(str, sorted(set(p))))) for s, p in sent_occ.items() if len(set(p)) >= 2])

# misspelling candidates: core-prose words not known to pyspellchecker, with counts and posts
try:
    from spellchecker import SpellChecker
    sp = SpellChecker()
    unknown = []
    for w, c in ALL_TOK.items():
        base = w.replace("’", "'")
        if "'" in base or len(base) < 4 or not base.isalpha():
            continue
        if base in sp:
            continue
        posts = sorted(pid for pid in core_ids if re.search(r"(?<![A-Za-z])" + re.escape(base) + r"(?![A-Za-z])", post_prose[pid], re.I))
        unknown.append((w, c, len(posts), " ".join(map(str, posts[:10])), sp.correction(base)))
    unknown.sort(key=lambda x: -x[1])
    write_csv("unknown_words.csv", ["word", "count", "doc_freq", "post_ids", "spellchecker_suggestion"], unknown)
except Exception as e:
    print("spellchecker unavailable:", e)

print("core posts", N_CORE, "tokens", N_TOK, "types", len(ALL_TOK))
