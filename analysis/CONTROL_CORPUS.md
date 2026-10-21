# Distinctiveness test: Satoshi's forum habits against contemporary writers in the same threads

Purpose: the main report describes habits that are characteristic **within** the archive. This test asks how common each habit was among other people writing in the same BitcoinTalk threads at the same time, and (revision 3) how much of the difference reflects Satoshi's role in those threads rather than personal habit. It is a population comparison only. Control writers appear under pseudonymous ids (`W0001`…), and no output names or ranks them.

Every share below is written as **writers meeting the habit / writers eligible for that habit**. The eligible number differs by habit and by comparison, and is much smaller than the 442 writers in the collection. A summary should quote the eligible number, not 442.

## Data

| Item | Value |
|---|---|
| Source | the 259 BitcoinTalk threads that contain the archived posts, 491 pages, fetched by `06_fetch_forum_threads.py` |
| Period | posts dated 2009-11-01 to 2010-12-31 |
| Control collection | 5,736 posts by 442 writers, 423,409 words of their own prose |
| Satoshi, same pages, same cleaner | 532 posts, 47,427 words. The four reposts and the disputed post are excluded, and so are `post_10` and `post_351`, whose other-member text only the archive's manual rules can remove. |
| Committed data | `data/control/post_counts.csv.gz` (one row per post: pseudonymous writer, topic, message id, date, role, SHA-256 of the cleaned text, and all additive feature and opportunity counts); `data/control/pages_manifest.csv` (URL, size and SHA-256 of every page); `data/agg/control_writer_features.csv` (per-writer values and opportunity counts) |

**Same cleaning for both populations (revision 3).** Revision 2 cleaned control posts with the code-line rule (R12) but not the rule that keeps an explanation after ` -- ` (R12b). Both rules now live in `scripts/cleaning.py`, which the archive extraction, the control parser and the e-mail cleaner all call.

The check below runs Satoshi's own posts through the control cleaner, from the thread pages, and compares word counts with the archive extraction (`data/control/cleaning_parity.csv`):

* 532 of 535 BitcoinTalk posts give identical counts.
* `post_241` now gives 326 words both ways, keeping the password-delay reasoning; revision 2's control cleaner gave 190.
* The three differences are `post_10` and `post_351` (manual quote rules, excluded above) and 2 words in `post_483`.

**Corrected definitions (revision 3).** The contraction-choice counts are now case-insensitive ("It's" counts like "it's", and "It is" like "it is"), which moves Satoshi's BitcoinTalk contracted share from 0.857 to 0.864. Hedges and boosters are counted without overlap ("I'm not sure" counts once, not also as "not sure"). For two-way choices a writer now needs at least 3 uses of either form, where revision 2 needed 1. That shrinks those denominators and is the main reason they differ from revision 2.

**Offline reproduction.** `08_control_analysis.py` reads only the committed counts. Anyone can recompute every table here without the page cache. Re-fetching the pages and running step 7 reproduces the counts. Page hashes will differ, because pages carry live merit and view counts, but the per-post SHA-256 of the cleaned text should match.

## Four comparisons

Roles come from thread structure only, never from the features under test (`07_control_corpus.py`):

* **question**: the post's own prose contains a sentence ending in "?".
* **answer**: no question of its own, and the post either quotes text containing "?" or directly follows another writer's post containing "?".
* **statement**: neither.

Satoshi's text splits 12,576 words of answers (137 posts), 20,860 of statements (264) and 13,991 of posts containing a question (131). The control collection is 94,906, 155,201 and 173,302 words respectively.

| Comparison | Text used | Eligible control writers |
|---|---|---|
| A all text | each writer's full text, at least 500 words | 136 |
| B all text, equal samples | 25 random samples of whole posts totalling ≥ 1,000 words; writer value is the median sample (Satoshi: 200 samples) | 87 |
| C declarative posts | answers + statements only, equal samples of ≥ 1,000 words | 54 |
| D answers to questions | answers only, equal samples of ≥ 500 words | 44 |

Rate features with a sparse denominator need enough material in each sample: 10 sentence boundaries for spacing, 10 contraction choices, 5 stance markers. A writer needs at least half of the samples valid. Two-way choices are measured on the writer's full text within the comparison's role filter. Thresholds are the ones fixed in revision 2 and were not re-tuned.

## Results

Source: `data/agg/control_role_matched.csv`. Each cell is "Satoshi-like writers / eligible writers (share)". Satoshi's percentile among the eligible writers is in brackets.

### Rate habits

| Habit (Satoshi-like if) | A all text | B equal samples | C declarative | D answers |
|---|---|---|---|---|
| Contracted share ≥ 0.80 | 24/128 (19%) [91] | 13/86 (15%) [94] | 9/53 (17%) [94] | 6/38 (16%) [95] |
| Two spaces after sentences ≥ 0.90 | 32/120 (27%) [86] | 23/76 (30%) [91] | 14/47 (30%) [88] | 9/35 (26%) [89] |
| "If you…" openers ≥ 1.5 per 1k | 14/136 (10%) [96] | 7/87 (8%) [94] | 5/54 (9%) [94] | **16/44 (36%)** [93] |
| "if" ≥ 9 per 1k | 34/136 (25%) [93] | 16/87 (18%) [92] | 13/54 (24%) [89] | 15/44 (34%) [93] |
| "It would be" ≥ 0.6 per 1k | 39/136 (29%) [82] | 28/87 (32%) [85] | 21/54 (39%) [78] | 9/44 (20%) [40] |
| Verdict openers ≥ 0.5 per 1k | 51/136 (38%) [75] | 34/87 (39%) [66] | 23/54 (43%) [67] | 13/44 (30%) [86] |
| Hedges ≥ 0.85 of stance markers | 47/107 (44%) [78] | 36/79 (46%) [92] | 18/49 (37%) [75] | 8/19 (42%) [not measurable] |
| Semicolons ≤ 0.2 per 1k | 84/136 (62%) | 57/87 (66%) | 38/54 (70%) | 34/44 (77%) |
| Dashes ≤ 0.3 per 1k | 107/136 (79%) | 68/87 (78%) | 40/54 (74%) | 39/44 (89%) |
| Exclamation marks ≤ 1.5 per 1k | 76/136 (56%) | 45/87 (52%) | 21/54 (39%) | 22/44 (50%) |

Satoshi's own sample-to-sample spread is wide for the sparse rates. In comparison B his 10th–90th percentile range is 0.0–3.8 per 1k for "If you…" openers and 7.3–16.1 for "if". In 500-word answer samples the "If you" range is 0.0–5.5. For contraction share and spacing it is narrow (0.78–0.94 and 0.97–1.00 in B). His answer samples have too few stance markers for the hedge share, so comparison D cannot measure it for him.

### Two-way choices (each writer's full text, at least 3 uses of either form)

| Habit | A all text | C declarative | D answers |
|---|---|---|---|
| Non-US spelling share ≥ 0.75 | 6/29 (21%) | 2/12 | 0/6 |
| "e-mail" hyphenated ≥ 0.8 | 2/13 | 2/4 | 2/2 |
| "double-spend" hyphenated ≥ 0.9 | 3/8 | 2/6 | none eligible |
| "proof-of-work" hyphenated ≥ 0.9 | 2/10 | 1/5 | none eligible |
| "etc." with a period, always | 4/22 (18%) | 1/9 | 2/4 |
| "- " bullets, never "* " | 5/16 (31%) | 4/8 | 1/2 |
| `1)` numbering, never `1.` | 24/46 (52%) | 7/19 | 4/10 |
| Logical quotation ≥ 0.75 | 27/43 (63%) | 11/22 | 6/10 |
| "block chain" always two words | 17/23 (74%) | 12/15 | 6/8 |
| "%" always, never "percent" | 26/28 (93%) | 14/16 | 7/7 |
| "OK", never "okay" | 4/6 | 2/3 | 1/1 |
| "towards" ≥ 0.75 | 2/5 | 0/2 | 0/1 |

With a minimum of 3 uses most two-way choices have fewer than 30 eligible writers, and in the role-matched comparisons fewer than 10. Shares on such denominators are reported for completeness and should not be quoted as rates. Comparison B uses the same full-text rule as A, so its values (in the CSV) differ from A only through the 1,000-word eligibility floor.

### Combined tests (comparison A)

| Habits required together | Writers measurable | Writers matching all |
|---|---|---|
| Double spacing, ≤ 0.2 semicolons, ≤ 0.3 dashes, ≤ 1.5 exclamation marks per 1k, contracted share ≥ 0.80 | 116 | 2 |
| Double spacing, contracted share ≥ 0.80, "if" ≥ 9 per 1k, "If you" ≥ 1.5 per 1k | 116 | 0 |

These remain illustrations, not probabilities. The second set was chosen after seeing where Satoshi is extreme, and the thresholds sit near his values. The habits are also correlated, since contraction rate, "if" and "If you" all rise in instructional replies.

## What the role matching shows

* **"If you…" openers are largely a function of answering.** On all text and declarative text, 5–14 writers (8–10%) reach Satoshi's rate. Among answers to questions, 16 of 44 do (36%). The reader-addressed conditional is what answering looks like on this forum, and Satoshi answered more than most. His answer-text rate still sits at the 93rd percentile, so he remains at the high end, but the habit is not distinctive once role is matched.
* **The "if" rate behaves the same way**, less sharply: 18–25% of writers outside answers and 34% in answers.
* **The contraction share is the most robust difference.** It stays at 15–19% of eligible writers and the 91st–95th percentile in every comparison, including equal-sized samples and answers only. It is also register-dependent across Satoshi's own writing (white paper 0.24, e-mails 0.75, forum 0.86; validation report), so it describes his informal register, not his writing in general.
* **Double spacing stays at 26–30% of writers** in every comparison: stable for him, common around him.
* **Verdict openers become more distinctive among answers** (13 of 44, 86th percentile), which fits answering by stating a verdict first. The denominator is small.
* **Spelling and hyphenation cannot be role-matched with this collection.** Too few writers use the words often enough. The all-text result (6 of 29 writers with a non-US share ≥ 0.75; 2 of 13 hyphenating "e-mail") is the best available and rests on small numbers.

## Limitations

* Thresholds are those fixed in revision 2, near Satoshi's values; the shares describe prevalence, not discriminative power.
* Role labels are structural approximations. An "answer" may be a correction or a disagreement, and a "question" post may be mostly explanation with one rhetorical question.
* Writers with as few as 500 words are compared with Satoshi's 47,427; equal-sized samples (B–D) remove the length advantage but not the difference in how stable each writer's estimate is.
* Unmarked quotations of other people inside a control post count as that writer's text.
* One forum, one period. The next step is a pre-registered test on unseen writers and threads (`PROTOCOL_NEXT_TEST.md`).

## Reproduce

```
cd analysis/scripts
python3 08_control_analysis.py                                  # offline, from the committed counts
# to rebuild the counts from the forum:
python3 06_fetch_forum_threads.py --cache /path/to/bt_cache     # network; about 490 pages
python3 07_control_corpus.py --cache /path/to/bt_cache
```

`07_control_corpus.py` also writes `data/forum_last_edit.csv`, the "Last edit" stamps that `02_features.py` uses for the edited-post sensitivity check.
