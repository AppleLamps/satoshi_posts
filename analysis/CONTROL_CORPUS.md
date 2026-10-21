# Distinctiveness test: Satoshi's forum habits against contemporary writers in the same threads

Purpose: the main report describes habits that are characteristic **within** the archive. This test asks how common each habit was among the other people writing in the same BitcoinTalk threads at the same time, so that "characteristic" can be separated from "distinctive". It is a population comparison only. No control writer is named, ranked or compared one-to-one with Satoshi, and the outputs contain no per-writer rows.

## Control corpus

| Item | Value |
|---|---|
| Source | the 259 BitcoinTalk threads that contain the archived posts (topic numbers from `data/sni_posts.jsonl`), fetched by `06_fetch_forum_threads.py` with caching and a delay between requests |
| Period | posts dated 2009-11-01 to 2010-12-31 (the span of Satoshi's BitcoinTalk posts) |
| Excluded | the account `satoshi` |
| Control posts / writers / words | 5,736 posts by 442 writers, 423,409 words of their own prose |
| Writers with at least 500 words (enter the per-writer distributions) | 136 |
| Satoshi reference | his 534 BitcoinTalk core posts, 47,898 words, measured with the same code |

Cleaning parity: control posts go through the same rules as Satoshi's prose: quote blocks, quote headers, code blocks, images and signatures removed; `<br>` to newline; U+00A0 to space (the forum stores a typed double space as `&nbsp; `, for every member alike); code-looking lines removed with the same regular expression. All features come from `measures.profile()`, the function used for every other table.

For a two-way choice (for example "block chain" versus "blockchain"), a writer counts only if they used either form at least once, so the number of writers differs by row. For double spacing, a writer needs at least 10 measurable sentence boundaries; for the hedge share, at least 5 hedges or boosters.

## Results

"Satoshi-like" uses a threshold set near Satoshi's own value (column 2). Percentile is Satoshi's position among the eligible writers (50 = median; ties count half). Source: `data/agg/control_population.csv`.

### Habits that few contemporaries shared (at most about a third of writers)

| Habit | Satoshi | Satoshi-like if | Writers with opportunity | Satoshi-like | Share | Satoshi percentile | Control median |
|---|---|---|---|---|---|---|---|
| "If you…" sentence openers per 1k words | 2.13 | ≥ 1.5 | 136 | 14 | 10% | 96 | 0.37 |
| "e-mail" hyphenated (share of e-mail/email) | 0.89 | ≥ 0.8 | 40 | 6 | 15% | 85 | 0 |
| Contracted form where a full form was possible | 0.86 | ≥ 0.80 | 135 | 25 | 19% | 89 | 0.59 |
| Non-US spellings (share of non-US + US-only forms) | 0.87 | ≥ 0.75 | 76 | 18 | 24% | 78 | 0 |
| "if" per 1k words | 11.3 | ≥ 9 | 136 | 34 | 25% | 93 | 7.2 |
| Two spaces after sentences | 0.988 | ≥ 0.90 | 120 | 32 | 27% | 86 | 0 |
| "It would be" per 1k words | 0.96 | ≥ 0.6 | 136 | 39 | 29% | 81 | 0 |
| "double-spend" hyphenated | 1.0 | ≥ 0.9 | 23 | 7 | 30% | 85 | 0 |
| Bullets "- " rather than "* " | 1.0 | = 1.0 | 19 | 6 | 32% | 84 | 0.5 |

### Habits shared by many contemporaries (about 40% or more)

| Habit | Satoshi | Satoshi-like if | Writers with opportunity | Satoshi-like | Share | Satoshi percentile |
|---|---|---|---|---|---|---|
| Verdict openers ("Right,", "Yes,", "No,") per 1k | 0.77 | ≥ 0.5 | 136 | 53 | 39% | 76 |
| Etc. with a period | 1.0 | = 1.0 | 67 | 30 | 45% | 78 |
| Hedges as share of hedges + boosters | 0.91 | ≥ 0.85 | 108 | 50 | 46% | 77 |
| "proof-of-work" hyphenated | 0.92 | ≥ 0.9 | 28 | 13 | 46% | 54 |
| Numbered items "1)" rather than "1." | 1.0 | = 1.0 | 50 | 26 | 52% | 74 |
| Exclamation marks per 1k | 0.92 | ≤ 1.5 | 136 | 76 | 56% | 46 |
| Semicolons per 1k | 0.06 | ≤ 0.2 | 136 | 84 | 62% | 60 |
| "towards" rather than "toward" | 0.82 | ≥ 0.75 | 16 | 10 | 63% | 38 |
| Logical quotation (stop outside the closing quote) | 0.85 | ≥ 0.75 | 78 | 50 | 64% | 42 |
| "OK" rather than "okay" | 1.0 | = 1.0 | 29 | 19 | 66% | 67 |
| "block chain" as two words | 1.0 | = 1.0 | 56 | 39 | 70% | 65 |
| No dashes (em/en dash or "--" per 1k) | 0.21 | ≤ 0.3 | 136 | 107 | 79% | 77 |
| "%" rather than "percent" | 1.0 | = 1.0 | 68 | 64 | 94% | 53 |

Register-dependent measures, for orientation: Satoshi's mean sentence length (12.6 words) is at the 32nd percentile of the control writers (median 14.6), and his "you" rate (20.9 per 1k) at the 80th (median 12.4). Both reflect his role in the threads (answering and instructing) as much as personal style.

### Combined tests

| Habits required together | Writers measurable | Writers matching all |
|---|---|---|
| Double spacing, ≤ 0.2 semicolons per 1k, ≤ 0.3 dashes per 1k, ≤ 1.5 exclamation marks per 1k, contracted share ≥ 0.80 | 120 | 2 |
| Double spacing, contracted share ≥ 0.80, "if" ≥ 9 per 1k, "If you" openers ≥ 1.5 per 1k | 120 | 0 |

These are illustrations, not probabilities. The second set was chosen after seeing where Satoshi is extreme, and every threshold was set near his value, so a low match count is partly built in. The habits are also correlated (contraction rate, "if" and "If you" all rise in instructional replies). A proper discriminative test would fix features and thresholds in advance on one set of writers and evaluate them on another.

## What this changes in the report

* **Double spacing is characteristic, not rare.** About a quarter of contemporary writers on the same threads double-spaced as consistently. It stays in the fingerprint as a stable, cross-register habit but cannot single out a writer, and it no longer supports any inference about age (profile addendum, section 2).
* **The absence of semicolons, dashes and exclamation marks is common.** Most control writers also avoid them in short forum replies. These are weak discriminators and are reclassified as such in the fingerprint.
* **Term forms are mostly community conventions in 2010.** "block chain" (70% of writers who used the term), "%", "OK", logical quotation and "1)" lists are shared by a majority. "e-mail", hyphenated "double-spend" and "- " bullets remain unusual, but on small numbers of writers.
* **The most distinctive frequent habits are syntactic and lexical**: the reader-addressed conditional ("If you…" at the 96th percentile, "if" at the 93rd), the contraction rate (89th), and the non-US spelling share. All four are measurable on short texts. The first three are partly register-driven (validation report), so they distinguish forum replies, not formal writing.

## Limitations

* Thresholds are post hoc and set near Satoshi's values (see Combined tests).
* Satoshi's 47,898 words are compared with writers who have as few as 500 words; small samples produce more extreme values in both directions, so shares at the extremes (0 or 1) are inflated among control writers with little text.
* The same threads match topic and period but not role: Satoshi mostly answers and announces, while many control posts ask questions or report problems.
* Some control writers quote Satoshi in text that the forum did not mark as a quote; such text would be counted as theirs. Quote blocks marked by the forum are removed.
* The control is one forum. It says nothing about how common these habits were on mailing lists or in formal writing.

## Reproduce

```
cd analysis/scripts
python3 06_fetch_forum_threads.py --cache /path/to/bt_cache     # network; about 490 pages
python3 07_control_corpus.py --cache /path/to/bt_cache
```

`07_control_corpus.py` also writes `data/forum_last_edit.csv`, the BitcoinTalk "Last edit" stamps for the archived posts, which `02_features.py` uses for the edited-post sensitivity check.
