# Next-test design: recorded definitions, incomplete evaluation

Status: **draft evaluation; definitions recorded**, version `protocol-1.1-draft`. The earlier label "frozen protocol" overstated what was specified. No fresh quantitative comparison material has been collected. The machine-readable specification remains at `data/protocol/frozen_spec.json` for path compatibility and is written by `scripts/09_freeze_protocol.py`. Its `ready_for_confirmatory_collection` flag is false. It records the SHA-256 of every definition file:

* `textutil.py`
* `cleaning.py`
* `measures.py`
* `07_control_corpus.py`
* `08_control_analysis.py`

Any change to those files after this commit is a deviation and must be reported with its reason.

This document records a proposed test, not a runnable preregistration. The existing `08_control_analysis.py` calculates descriptive feature medians from separately drawn samples per feature. It does not implement the proposed joint score, AUC or bootstrap. Its descriptive tables remain reproducible and unchanged.

## Question

The present results are descriptive differences within one sample: Satoshi against 442 writers in the threads he took part in, with thresholds set after inspection. The next test asks two questions:

1. Do these differences persist on **writers and threads not used so far**, under role matching?
2. Do the frozen features **distinguish held-out Satoshi text** from unseen writers' text better than chance, within the same register?

## Frozen definitions

* **Cleaning:** `cleaning.py` (quotes, code blocks, images and signatures removed; rules R12 and R12b).
* **Features:** `measures.py`; additive counts per post as in `07_control_corpus.py`.
* **Roles** (thread structure only):
  * question: the post's own prose contains a sentence ending in "?";
  * answer: no question of its own, and it quotes text containing "?" or directly follows another writer's post containing "?";
  * statement: neither.
* **Primary features and rules** (thresholds from revision 2, unchanged):

| Feature | Rule | Minimum material |
|---|---|---|
| Contracted share | ≥ 0.80 | 10 contraction choices per sample |
| "if" per 1k words | ≥ 9 | none |
| "If you…" sentence openers per 1k | ≥ 1.5 | none |
| Two spaces after sentences | ≥ 0.90 | 10 boundaries per sample; only sources that preserve spacing |
| Verdict openers per 1k | ≥ 0.5 | none |
| Non-US spelling share | ≥ 0.75 | 3 discriminating spellings per writer |
| "e-mail" hyphenated | ≥ 0.8 | 3 uses per writer |

* **Secondary features:** every other habit in `08_control_analysis.py`, same thresholds.
* **Proposed samples:** whole posts or messages pooled to at least 500 and at least 1,000 words; 25 samples per writer, writer value = median; seed 20101212. A primary length has not been selected. Whole-post sampling can exceed the target; actual lengths must be reported. Repeated samples overlap and are not independent replications.

## Material

* **Unseen writers and threads (negatives).**
  * Proposed forum population: BitcoinTalk threads from 2009-11 to 2010-12 in which Satoshi did not post, excluding the 259 threads used here and every account already in the control collection. The excluded pseudonyms are collection-specific: a fresh collection cannot exclude accounts by comparing newly allocated `W0001` labels. Recover the original account mapping from the same pages and compare stable forum account identities before anonymizing a new collection. A stable exclusion manifest has not yet been committed.
  * Proposed e-mail population: messages by other members of the cryptography, bitcoin-list and p2p-research lists in the same period. Public-list messages cannot automatically serve as matched controls for private correspondence: audience, purpose and technical role must also match. Without that match, any private/public comparison is exploratory.
* **Held-out Satoshi text (positives), not yet selected.** Later-published private correspondence is a proposed source, not a fixed positive set. Exact source and message IDs, provenance, inclusion rules and hashes must be recorded before scoring. All 543 archive posts, the white paper and the three public lists are already used and excluded as positives. No unused forum-positive set is identified here. A confirmatory forum AUC cannot be claimed without one; new negative forum text alone can only extend the descriptive prevalence comparison.
* **Collection rule.** Fix the list of sources, threads and messages, and record their hashes, before computing any feature on them.

## Proposed evaluation (not implemented or fully specified)

* **Score.** For each sample, the number of the five primary rate features whose rule is met (0–5). A feature without enough material counts as not met. Two-way choices are reported per writer, not scored, because 500–1,000-word samples rarely contain them.
* **Primary outcome under consideration.** The area under the ROC curve (AUC) of the score, for held-out Satoshi samples against unseen-writer samples, computed only for registers with both unused positives and appropriately matched negatives. A 95% interval requires an explicit dependence model. There is one positive author: resampling negative writers alone conditions on the selected Satoshi material and does not quantify its variability. For inference across his correspondence, define positive conversation or episode clusters and resample those as well as negative writers. Overlapping sample draws cannot be treated as independent positive observations.
* **Secondary outcomes:**
  * per-feature AUC;
  * the share of unseen writers meeting each rule, with denominators;
  * the four comparisons A–D of `CONTROL_CORPUS.md` repeated on the unseen writers.
* **Success criterion.** The lower bound of the primary AUC's interval is above 0.5 in each register tested. Every register and every feature is reported whatever the result.
* **Reporting.** Denominators for every share; deviations from this protocol listed separately.

Before this becomes a confirmatory protocol, commit: the exact positive and negative source selection and stable exclusions; feasible matched registers; the primary sample length; executable scoring using the same sampled posts for every feature in each score; weighting by writer; tie handling; missing-feature policy and spacing availability; bootstrap units, repetitions, seed and inferential scope. Hash that evaluator and the complete protocol. Until then there is no confirmatory success or failure to report. The present correction changes protocol status and interpretation, not feature definitions or measured outputs.

## Open items not covered by this protocol

* **Failure-anticipation reasoning** (profile addendum, 6.1) remains a qualitative finding. Testing it needs a separate design:
  * a corpus of design discussions by experienced developers;
  * coding for the sequence assumption, failure path, consequence, safeguard;
  * coders blind to authorship, with agreement reported.
* **Spelling and hyphenation habits** need far more text per writer than forum posts provide. They should be tested on longer documents.

## Scope

The test compares held-out text of known authorship with anonymous population samples, to measure whether the features generalise. It is not to be used to score named individuals or candidate authors.
