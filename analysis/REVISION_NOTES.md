# Revision notes (revision 2)

This revision responds to a review of the first version (commit `3518bf9`). Each point below gives what the review found, what changed, and where the result now lives. Old values are quoted so the change can be checked.

## 1. One definition per feature

**Found.** The same named feature was computed differently in different places: "If you" openers were 77 in the report and 99 in `finding_counts.json`; sentence-spacing counts differed between `02_features.py` and `05_validate_other_corpora.py`; the validation counted the empty, code-only `post_475` as a document (535 BitcoinTalk documents instead of 534).

**Changed.** New module `scripts/measures.py` holds one function per feature, and `measures.profile()` builds the pooled feature set. `02_features.py`, `03_evidence.py`, `05_validate_other_corpora.py` and the new `07_control_corpus.py` all import it; `03_evidence.py` takes its counts from it wherever a canonical function exists. `profile()` drops documents with no words.

| Feature | Old values | New value |
|---|---|---|
| "If you…" sentence openers | 77 (report), 99 (finding_counts) | 102, of which 77 with bare "you" and 25 with "you're"/"you've"/"you'd"/"you'll" |
| BitcoinTalk sentence spacing | 1,549 double / 25 single (report), 1,485 / 20 (validation) | 1,480 / 18 (0.988) |
| BitcoinTalk documents in validation | 535 | 534 |

## 2. Case sensitivity

**Found.** Lexical counts were case-sensitive, so the report gave "obviously" 0 while the prose contains "Obviously" in `post_242` and `post_260`, and missed "Certainly".

**Changed.** Lexical items are matched case-insensitively throughout; positional items (sentence and verdict openers) stay capitalised at their position. `expressions.csv` now has a `case` column.

| Item | Old | New |
|---|---|---|
| obviously | 0 | 2 |
| certainly | 3 | 4 |
| definitely | 7 | 10 |
| for example / for instance | 2 / 4 | 5 / 10 |
| otherwise | 4 | 7 |
| instead | 30 | 36 |

Boosters remain rare (26 against 281 hedges).

## 3. Factual statements

| Statement in version 1 | Correction |
|---|---|
| "none is stamped between 07:00 and 13:59 UTC" | 9 posts fall in that band (`post_156`, `157`, `175`, `176`, `386`, `387`, `522`, `538`, `539`); 1 between 07:00 and 11:59. Corrected in the report (section 4) and the addendum (section 4). |
| No "medium of exchange" in his prose | It occurs once, in `post_326`. Corrected; the economics lexicon is now committed (`measures.PROFILE_LEXICONS`). |
| "distrusts GPL" | `post_75` says "Nothing against GPL per-se, but Bitcoin is an MIT license project", and `post_450` calls GPL "a good license for operating systems". Rewritten as a licence-compatibility constraint plus a preference for permissive licences in small libraries. |
| "+1 used 19 times in 9 posts" | That count included signed numbers such as `+18%`. Approval "+1" occurs 4 times in 4 posts. |
| Cryptographic terms "123 in 46 posts", economics terms "31 in 16 posts", "14 posts mention compatib" | These came from uncommitted queries. They are now computed from committed lexicons into `data/agg/profile_counts.csv`: 156 in 54 posts, 31 in 14 posts, 9 posts. |
| `post_328` single spacing explained as "parenthetical lines" | It is ordinary prose, single-spaced almost throughout (1 double, 10 single). It is now reported as the one genuine spacing exception, with competing explanations. |
| British vs American spelling "29 vs 20 tokens" | The list missed sixteen `-ize` tokens and treated `-ize` as American. Replaced by three classes: non-US 27, US-only 5 (`color` 4, `gotten` 1), `-ize` (American or Oxford British) 28. The "British lean" wording is replaced by "no single convention". |

## 4. White-paper cleaning and shared passages

**Found.** The saved white-paper text still contained the references, diagram labels and formula fragments, and its numbered network steps had been merged into running text, so the list detector reported no numbered list. Text published in more than one corpus (`post_1` and the p2p-research announcement; `post_167` and a bitcoin-list release note) was counted as independent evidence.

**Changed.** `clean_whitepaper` now applies explicit line rules W1–W7 (script docstring). Every dropped line was audited; none is prose. The paper is 3,002 words (was 3,216) and shows its six `1)` steps. A shared-passage filter marks sentences that also occur in another source family, every corpus is reported with and without them, and per-document overlap is in `data/agg/shared_passages.csv`. No cross-register conclusion changes when shared passages are removed.

## 5. Edited posts and chronology

**Found.** `post_42` is dated 2010-02-05 but contains difficulty entries through 2010-08-26. Date and register overlap in the paper/e-mail/forum comparison, so a "will" to "would" shift cannot show growing caution. The affect figures were not reproducible from committed code.

**Changed.**
* BitcoinTalk "Last edit" stamps for 105 archived posts were collected from the live thread pages (`data/forum_last_edit.csv`). 103 were edited by the author, 25 of them more than 24 hours after posting; `post_42` was last edited on 2010-08-27. The period profile and the topic-vocabulary table are reported for all posts, without the 25 late-edited posts, and without all 103 (`compare_period_canonical.csv`, `affect_by_period.csv`). The stability findings hold; the late-2010 rise in security vocabulary halves when all edited posts are removed, and the addendum now says so.
* "will"/"would" is reported by e-mail year and by forum period. The 2008 e-mails already use "would" at the forum rate and neither rate trends within the forum. The growing-caution reading is withdrawn.
* Topic and affect lexicons are in `measures.AFFECT`; counts by period are written by `02_features.py`, and every matched word with its post id is in `affect_matches.csv`. The addendum's earlier figures are replaced.

## 6. Biographical claims in the profile addendum

**Found.** Two-space typing and historical references do not establish a birth year before 1975; idiomatic English does not settle native-language status; number formatting does not exclude a European upbringing; applied economics and occasional cryptographic uncertainty do not establish education or credentials.

**Changed.** Each of these is now a hypothesis with competing explanations and the evidence that would distinguish them; the birth-year estimate, the native-speaker conclusion, the exclusion of European upbringing, "self-taught" and "not an academic cryptographer" are withdrawn. The control corpus also shows that 27% of contemporary writers in the same threads double-spaced as consistently, which undercuts the age inference directly.

## 7. Reasoning style

**Suggested.** Expand the cognitive profile around the pattern of naming an assumption that could fail, following the money consequences, and proposing a proportionate safeguard.

**Changed.** New section 6.1 of the addendum, with `post_523`, `post_526`, `post_241`, `post_503`, `post_419` and the 2008 cryptography-list e-mails on waiting before shipping goods. Working on `post_241` exposed an extraction fault: lines of the form "code  -- explanation" had been labelled code in full, discarding 139 words of the author's prose. Rule R12b now keeps the explanation as prose; the core corpus grows from 48,630 to 48,766 words.

## 8. Matched contemporary writers

**Suggested.** Test the strongest hypotheses against matched contemporary writers.

**Changed.** New scripts `06_fetch_forum_threads.py` and `07_control_corpus.py` and new document `CONTROL_CORPUS.md`. Other members' posts from the same 259 threads, 2009-11 to 2010-12 (442 writers, 423,409 words), cleaned and measured with the same code. Results are reported only as population shares; no control writer is named or ranked. Several fingerprint habits turn out to be common in that milieu (no semicolons or dashes, "block chain", "%", logical quotation, `1)` lists, double spacing at 27%), while the "If you…" opener rate, the "if" rate, the contraction share, the non-US spelling share and "e-mail" hyphenation are uncommon. The fingerprint table in the report now carries both the cross-register and the contemporary result for each habit.

## 9. Housekeeping

* `scripts/__pycache__` removed from version control; `analysis/.gitignore` added.
* Evidence regenerated: 357 rows, all verified at their file, line and column.

---

# Revision 3

Responds to the review of revision 2 (commit `180ac8c`).

## 1. One cleaner for both populations

**Found.** `07_control_corpus.py` removed code-looking lines without rule R12b, which keeps an explanation after ` -- `. Passing `post_241` through it gave 190 words against 326 in the archive extraction, and dropped the password-delay reasoning.

**Changed.**
* New module `scripts/cleaning.py` holds `CODE_LINE_RE`, the R12b gloss rule and the forum-post cleaner. `01_extract.py`, `05_validate_other_corpora.py` and `07_control_corpus.py` all call it.
* The archive extraction is byte-for-byte unchanged, and so is the cleaned e-mail text.
* Satoshi's posts cleaned from the thread pages now match the archive word count in 532 of 535 posts (`data/control/cleaning_parity.csv`), and `post_241` gives 326 words both ways.
* The control side of the comparison now takes Satoshi's text from the same pages through the same cleaner. It excludes `post_10` and `post_351`, whose other-member text only manual archive rules remove.

## 2. Contraction choice is case-insensitive

"It's" and "It is" now count like "it's" and "it is".

| Measure | Old | New |
|---|---|---|
| BitcoinTalk contracted share | 0.857 | 0.864 |
| E-mails (pooled) | 0.71 | 0.75 |
| White paper | 0.26 | 0.24 |
| Control writers at ≥ 0.80 (comparison A) | 25 of 135 | 24 of 128 |

## 3. Hedges and boosters counted without overlap

The lexicon is matched as one alternation, longest item first, so "I'm not sure" counts once. "not sure" now counts only the remaining uses, such as "I am not sure" (2).

| Measure | Old | New |
|---|---|---|
| Hedges, core corpus | 281 | 264 |
| Hedges, BitcoinTalk | 278 | 261 |
| Hedge share | 92% | 91% |

## 4. Role matching and equal samples

The control analysis is now split in two:
* `07_control_corpus.py` builds per-post additive counts with role labels taken from thread structure (question, answer, statement).
* `08_control_analysis.py` runs four comparisons: all text; all text in equal 1,000-word samples; declarative posts; and answers to questions in 500-word samples.

Two-way choices need at least 3 uses per writer, where revision 2 needed 1. At the fixed "If you…" threshold of 1.5 per 1k, 14 of 136 writers qualify on all text and 16 of 44 among answers. Revision 3 incorrectly described these as writers reaching Satoshi's actual rate and attributed much of the difference to role; revision 4 below corrects that interpretation. The contraction threshold is met by 15–19% of eligible writers in every comparison. `CONTROL_CORPUS.md`, the summary table and the fingerprint give every share as writers meeting / writers eligible.

## 5. Offline reproduction

Committed in `data/control/`:
* anonymized per-post counts with opportunity counts, roles and the SHA-256 of each cleaned post;
* the URL and SHA-256 of every fetched page;
* per-writer feature values and opportunity counts (`data/agg/control_writer_features.csv`).

`08_control_analysis.py` runs from these files alone.

## 6. Recorded protocol proposal

Revision 3 recorded the following in `PROTOCOL_NEXT_TEST.md` and `data/protocol/frozen_spec.json` before any new quantitative material was collected:
* the definition files, by SHA-256;
* the primary features, thresholds, minimum material, sample sizes, seed and scoring rule;
* a proposed evaluation by AUC within register on unseen writers and threads against held-out Satoshi text, with a proposed success criterion;
* the threads and writers already used.

The failure-anticipation pattern stays labelled as a qualitative finding, with the design a comparable test would need.

---

# Revision 4: interpretation corrections and a qualitative style comparison

Changes by Codex, made directly at the user's request.

* **Conditional rates survive role matching.** The 16/44 and 15/44 figures use fixed thresholds (1.5 "If you" and 9 "if" per 1k), not Satoshi's actual answer-sample medians (1.969 and 12.55). Both actual values are at the 93.2nd percentile. Removed the conclusions that role matching explains away the pattern or establishes that contractions are the sole useful candidate. Changing role, eligibility and sample length together does not estimate a causal role contribution.
* **Career dating corrected.** MSVC6 compatibility does not establish professional experience in the 1990s. Removed that remaining unsupported start-date inference. The failure-anticipation section now describes recurrence without claiming measured distinctiveness or optimal safeguards.
* **Protocol status corrected in both prose and generated JSON.** `protocol-1.1-draft` records the same five definition-file hashes and thresholds but declares `ready_for_confirmatory_collection=false`. Exact positives, matched audiences, joint scoring, sample length and uncertainty estimation remain unspecified. It identifies the absent unused forum positives, the private/public e-mail confound, overlapping samples, the single positive author and the collection-specific writer labels. No confirmatory test or new quantitative control collection was performed.
* **Qualitative comparison added.** `STYLE_COMPARISON.md` maps the complete feature profile to practical security engineering and compares selected primary texts by Hal Finney, Nick Szabo and Wei Dai. It separates similarities in explanatory voice from conceptual lineage, discusses the technical context of all four `color` tokens, and reports no identity score.
* **Measurement integrity.** No source post, cleaner, feature definition, role definition, threshold or measured aggregate was changed. The offline control analysis and quotation verification are rerun as validation; the protocol JSON is regenerated and checked for deterministic output and unchanged definition hashes.
