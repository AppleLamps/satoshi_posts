# Stylometric analysis of the Satoshi Nakamoto post archive

This directory contains a reproducible stylometric analysis of every file under
`posts/`. The source posts are never modified.

Analyzed commit: `b442311` ("remove ipynb text file"), 543 files `posts/post_1.txt` … `posts/post_543.txt`.

## Deliverables

| File | Content |
|---|---|
| `STYLOMETRIC_FINDINGS.md` | Findings report (corpus quality, strongest findings, detailed results, change over time, anomalies, limitations, fingerprint) |
| `evidence.csv` | 346 verbatim examples with `file`, `line`, `col` (1-based) into the original repository files, plus per-finding counts |
| `post_features.csv` | ~120 measurements for each of the 543 posts (see column notes below) |
| `data/posts_raw.jsonl` | Header fields and the untouched body text of every file |
| `data/posts_clean.jsonl` | Each post split into typed segments (`own`, `quoteheader`, `quote`, `code`, `inline_code`, `repost_other`, `emoticon`, `signature`) with the author's own prose isolated |
| `data/extraction_log.csv` | Per-file alignment status, flags and coverage |
| `data/sni_posts.jsonl` | Structured HTML of each post fetched from the source site (used only to recover block boundaries) |
| `PROFILE_ADDENDUM.md` | Deeper profile of the writer (dialect, era, profession, behaviour), each claim tagged measured or inferred |
| `VALIDATION_OTHER_CORPORA.md` | Cross-register validation against the white paper and the 2008–2010 mailing-list emails; table in `data/agg/validation_other_corpora.csv`, cleaned texts in `data/other_corpora_clean.jsonl` |
| `data/agg/*.csv` | Corpus-wide tables: word frequencies, word 2–5-grams, character 3/4-grams, sentence openers/enders, expressions, spelling variants, capitalisation, punctuation totals, pronouns/modals, period/platform/topic/length/month comparisons, anomalies, near-duplicates, repeated sentences, unknown words |

## Reproducing

Requirements: Python 3.10+, `beautifulsoup4`, optionally `pyspellchecker` (for `unknown_words.csv`).

```
cd analysis/scripts
# 0. (optional, needs network) refresh the structured source HTML
python3 00_fetch_source_html.py --cache /tmp/sni_cache --fetch
# 1. parse repo files, align with source HTML, segment
python3 01_extract.py
# 2. per-post features and corpus-wide tables
python3 02_features.py
# 3. locate verbatim evidence for each finding
python3 03_evidence.py
# 4. verify every evidence row against the repository files (exit 0 = all match)
python3 04_verify_evidence.py
# 5. (optional, needs network to fetch the e-mails and bitcoin.pdf into a cache dir) cross-register validation
python3 05_validate_other_corpora.py --cache /path/to/cache
```

Step 0 is optional because `data/sni_posts.jsonl` is included; steps 1–4 run offline in under a minute.

## Extraction rules (summary; full text in the docstring of `01_extract.py`)

* R1 file layout: line 1 title, line 3 platform, line 5 timestamp, body from line 6.
* R2 U+00A0 → space (the forum stored the author's double spaces as `&nbsp; `).
* R3 block structure recovered by aligning the body with the source HTML; accepted only when the two texts are identical with all whitespace removed (537 files) or differ only in escaped newline characters inside code (6 files).
* R4 quote blocks and forum-generated quote headers are not the author's prose.
* R5 `<br>` → newline; two newlines = paragraph break; code blocks labelled `code`.
* R6 P2P Foundation signature labelled `signature`.
* R7 heuristic fallback for unaligned files (none were needed).
* R8–R11 manual attribution: four `Repost:` posts are other members' text; `> ` lines in post_10 are quoted; post_351 pastes others' benchmark reports; post_543 is of disputed authorship.
* R12 code-looking lines inside prose are labelled `inline_code`.

## Definitions (see `scripts/textutil.py`)

* Word token: `[A-Za-z]+(?:['’][A-Za-z]+)*` after URL masking, so contractions are one token; numbers are not word tokens.
* Sentence: maximal span ending at `.`, `!` or `?` followed by whitespace and a non-lowercase character (abbreviations, decimals and version numbers protected), or at a line/paragraph break.
* Rates are per 1,000 word tokens of the author's own prose unless stated otherwise.
* "Core corpus" = the 537 posts with usable prose after excluding the four reposts, the disputed 2014 post and the code-only post_475.

## Column notes for `post_features.csv`

`c_*` are raw counts within the post's own prose, `r_*_per1k` the same per 1,000 words, `fw_*` function-word rates per 1,000 words, `pron_*`/`modal_*` raw counts, `period` the analysis period (P1 … P6), `topic` a keyword-based label (`code_build`, `protocol_design`, `economics`, `general_conversational`), `core_corpus` whether the post enters the author-wide statistics, `alignment` the HTML alignment status, `flags` extraction flags.
