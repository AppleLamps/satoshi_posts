# Protocol for the next test (frozen before any new material is collected)

Status: **frozen**, version `protocol-1`. No fresh comparison material has been collected. The machine-readable specification is `data/protocol/frozen_spec.json`, written by `scripts/09_freeze_protocol.py`. It records the SHA-256 of every definition file:

* `textutil.py`
* `cleaning.py`
* `measures.py`
* `07_control_corpus.py`
* `08_control_analysis.py`

Any change to those files after this commit is a deviation and must be reported with its reason.

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
* **Samples:** whole posts or messages pooled to at least 500 and at least 1,000 words; 25 samples per writer, writer value = median; seed 20101212.

## Material

* **Unseen writers and threads (negatives).**
  * BitcoinTalk threads from 2009-11 to 2010-12 in which Satoshi did not post, excluding the 259 threads used here, and excluding every account already in the control collection. The excluded accounts are recorded as pseudonyms; running `07_control_corpus.py` on the same pages regenerates the mapping deterministically.
  * For the e-mail register: messages by other members of the cryptography, bitcoin-list and p2p-research lists in the same period.
* **Held-out Satoshi text (positives).** Text attributed to Satoshi that no analysis here has used, such as his later-published private correspondence with project contributors, cleaned with `cleaning.py`. Forum posts, the white paper and the three public lists are already used and are excluded as positives.
* **Collection rule.** Fix the list of sources, threads and messages, and record their hashes, before computing any feature on them.

## Evaluation

* **Score.** For each sample, the number of the five primary rate features whose rule is met (0–5). A feature without enough material counts as not met. Two-way choices are reported per writer, not scored, because 500–1,000-word samples rarely contain them.
* **Primary outcome.** The area under the ROC curve (AUC) of the score, for held-out Satoshi samples against unseen-writer samples, computed separately within each register (e-mail against e-mail; forum answers against forum answers). Report a 95% bootstrap interval, resampling writers.
* **Secondary outcomes:**
  * per-feature AUC;
  * the share of unseen writers meeting each rule, with denominators;
  * the four comparisons A–D of `CONTROL_CORPUS.md` repeated on the unseen writers.
* **Success criterion.** The lower bound of the primary AUC's interval is above 0.5 in each register tested. Every register and every feature is reported whatever the result.
* **Reporting.** Denominators for every share; deviations from this protocol listed separately.

## Open items not covered by this protocol

* **Failure-anticipation reasoning** (profile addendum, 6.1) remains a qualitative finding. Testing it needs a separate design:
  * a corpus of design discussions by experienced developers;
  * coding for the sequence assumption, failure path, consequence, safeguard;
  * coders blind to authorship, with agreement reported.
* **Spelling and hyphenation habits** need far more text per writer than forum posts provide. They should be tested on longer documents.

## Scope

The test compares held-out text of known authorship with anonymous population samples, to measure whether the features generalise. It is not to be used to score named individuals or candidate authors.
