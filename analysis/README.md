# Stylometric analysis of the Satoshi Nakamoto post archive

This directory contains a reproducible stylometric analysis of every file under
`posts/`. The source posts are never modified.

Analyzed commit: `b442311` ("remove ipynb text file"), 543 files `posts/post_1.txt` … `posts/post_543.txt`.

## Deliverables

| File | Content |
|---|---|
| `STYLOMETRIC_FINDINGS.md` | Findings report (corpus quality, strongest findings, detailed results, change over time, anomalies, limitations, fingerprint) |
| `evidence.csv` | 357 verbatim examples with `file`, `line`, `col` (1-based) into the original repository files, plus per-finding counts |
| `post_features.csv` | ~120 measurements for each of the 543 posts (see column notes below) |
| `data/posts_raw.jsonl` | Header fields and the untouched body text of every file |
| `data/posts_clean.jsonl` | Each post split into typed segments (`own`, `quoteheader`, `quote`, `code`, `inline_code`, `repost_other`, `emoticon`, `signature`) with the author's own prose isolated |
| `data/extraction_log.csv` | Per-file alignment status, flags and coverage |
| `data/sni_posts.jsonl` | Structured HTML of each post fetched from the source site (used only to recover block boundaries) |
| `PROFILE_ADDENDUM.md` | What the writing does and does not say about the writer (dialect, era indicators, subject knowledge, working pattern, reasoning style), each claim tagged measured or hypothesis with competing explanations |
| `CONTROL_CORPUS.md` | Distinctiveness test: how common each habit was among 442 other writers in the same BitcoinTalk threads, 2009-11 to 2010-12 (`data/agg/control_population.csv`, `control_summary.json`) |
| `REVISION_NOTES.md` | Every change made in revision 2 in response to review, with the old and new values |
| `VALIDATION_OTHER_CORPORA.md` | Cross-register validation against the white paper and the 2008–2010 mailing-list e-mails, with and without passages shared between corpora; tables in `data/agg/validation_other_corpora.csv` and `shared_passages.csv`, cleaned texts in `data/other_corpora_clean.jsonl` |
| `data/forum_last_edit.csv` | BitcoinTalk "Last edit" stamps for 105 archived posts (from `07_control_corpus.py`); used for the edited-post sensitivity tables |
| `data/agg/*.csv` | Corpus-wide tables, including the revision-2 tables `compare_period_canonical.csv` (period profile with and without edited posts), `edited_posts.csv`, `affect_by_period.csv` and `affect_matches.csv`, `spelling_classes.csv`, `profile_counts.csv`, `canonical_summary.json`, and the earlier word frequencies, word 2–5-grams, character 3/4-grams, sentence openers/enders, expressions, spelling variants, capitalisation, punctuation totals, pronouns/modals, period/platform/topic/length/month comparisons, anomalies, near-duplicates, repeated sentences, unknown words |

## Reproducing

Requirements: Python 3.10+, `beautifulsoup4`, `pdftotext` (poppler) and `pypdf` for step 5, optionally `pyspellchecker` (for `unknown_words.csv`).

```
cd analysis/scripts
# 0. (optional, needs network) refresh the structured source HTML
python3 00_fetch_source_html.py --cache /tmp/sni_cache --fetch
# 1. parse repo files, align with source HTML, segment
python3 01_extract.py
# 2. per-post features and corpus-wide tables (reads data/forum_last_edit.csv if present)
python3 02_features.py
# 3. locate verbatim evidence for each finding
python3 03_evidence.py
# 4. verify every evidence row against the repository files (exit 0 = all match)
python3 04_verify_evidence.py
# 5. (needs the e-mails and bitcoin.pdf in a cache dir) cross-register validation
python3 05_validate_other_corpora.py --cache /path/to/val_cache
# 6. (network) fetch the BitcoinTalk threads that contain the archived posts
python3 06_fetch_forum_threads.py --cache /path/to/bt_cache
# 7. control-corpus comparison; also rewrites data/forum_last_edit.csv
python3 07_control_corpus.py --cache /path/to/bt_cache
```

Steps 1–4 run offline (step 2 takes a few minutes because of the spell-check and near-duplicate passes). `data/sni_posts.jsonl` and `data/forum_last_edit.csv` are committed, so steps 0, 6 and 7 are needed only to refresh them; if step 7 is re-run, re-run step 2 afterwards.

**Shared definitions.** `scripts/measures.py` holds the one definition of every feature named in the reports (sentence spacing, "If you" openers, verdict openers, hedges and boosters, contractions, passives, list styles, quotation punctuation, term forms, spelling classes, topic and profile lexicons) and `measures.profile()` builds the pooled feature set used by the period, validation and control tables. A feature reported in two documents therefore comes from the same code.

## Extraction rules (summary; full text in the docstring of `01_extract.py`)

* R1 file layout: line 1 title, line 3 platform, line 5 timestamp, body from line 6.
* R2 U+00A0 → space (the forum stored the author's double spaces as `&nbsp; `).
* R3 block structure recovered by aligning the body with the source HTML; accepted only when the two texts are identical with all whitespace removed (537 files) or differ only in escaped newline characters inside code (6 files).
* R4 quote blocks and forum-generated quote headers are not the author's prose.
* R5 `<br>` → newline; two newlines = paragraph break; code blocks labelled `code`.
* R6 P2P Foundation signature labelled `signature`.
* R7 heuristic fallback for unaligned files (none were needed).
* R8–R11 manual attribution: four `Repost:` posts are other members' text; `> ` lines in post_10 are quoted; post_351 pastes others' benchmark reports; post_543 is of disputed authorship.
* R12 code-looking lines inside prose are labelled `inline_code`; R12b keeps an explanation written after ` -- ` on such a line as prose.

## Definitions (see `scripts/textutil.py`)

* Word token: `[A-Za-z]+(?:['’][A-Za-z]+)*` after URL masking, so contractions are one token; numbers are not word tokens.
* Sentence: maximal span ending at `.`, `!` or `?` followed by whitespace and a non-lowercase character (abbreviations, decimals and version numbers protected), or at a line/paragraph break.
* Rates are per 1,000 word tokens of the author's own prose unless stated otherwise.
* Lexical items are matched case-insensitively; positional items (sentence and verdict openers) in their capitalised form at that position.
* "Core corpus" = the 537 posts with usable prose (534 BitcoinTalk, 3 P2P Foundation) after excluding the four reposts, the disputed 2014 post and the code-only post_475.

## Column notes for `post_features.csv`

`c_*` are raw counts within the post's own prose, `r_*_per1k` the same per 1,000 words, `fw_*` function-word rates per 1,000 words, `pron_*`/`modal_*` raw counts, `period` the analysis period (P1 … P6), `topic` a keyword-based label (`code_build`, `protocol_design`, `economics`, `general_conversational`), `core_corpus` whether the post enters the author-wide statistics, `alignment` the HTML alignment status, `flags` extraction flags.

Revision 2 adds `c_if_you_openers` and `c_if_you_openers_bare`, `c_verdict_openers`, `c_hedges`, `c_boosters`, `c_contracted_choice`, `c_full_form_choice`, `c_list_num_paren`, `c_list_num_dot`, `c_bullet_dash` and `c_bullet_star` (all from `measures.py`); `c_double_space_after_sentence` and `c_single_space_after_sentence` now use `measures.sentence_spacing`.
