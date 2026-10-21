#!/usr/bin/env python3
"""Freeze the feature definitions and evaluation procedure for the next test
(PROTOCOL_NEXT_TEST.md) before any fresh comparison material is collected.

Writes data/protocol/frozen_spec.json with:
  * SHA-256 of the definition files (textutil.py, cleaning.py, measures.py,
    07_control_corpus.py for the counts and roles, 08_control_analysis.py for
    the thresholds and sampling); any later change to them invalidates the
    freeze and must be reported as a deviation
  * the pre-specified features, thresholds, minimum opportunity counts,
    sample sizes, role definitions, random seed and scoring rule
  * the identifiers of every thread and writer already used, which the next
    test must exclude

Re-running the script on unchanged files reproduces the same hashes; the
committed JSON is the reference.
"""
import csv, gzip, hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def main():
    os.makedirs(os.path.join(DATA, "protocol"), exist_ok=True)
    rows = list(csv.DictReader(gzip.open(os.path.join(DATA, "control", "post_counts.csv.gz"), "rt", encoding="utf-8")))
    spec = dict(
        version="protocol-1",
        definition_files={f: sha(os.path.join(HERE, f)) for f in ["textutil.py", "cleaning.py", "measures.py", "07_control_corpus.py", "08_control_analysis.py"]},
        primary_features=[
            dict(name="contracted_share", kind="rate", rule=">= 0.80", min_denominator="10 contraction choices per sample"),
            dict(name="if_per1k", kind="rate", rule=">= 9", min_denominator=None),
            dict(name="if_you_openers_per1k", kind="rate", rule=">= 1.5", min_denominator=None),
            dict(name="double_space_share", kind="rate", rule=">= 0.90", min_denominator="10 sentence boundaries per sample; only where the source preserves spacing"),
            dict(name="verdict_openers_per1k", kind="rate", rule=">= 0.5", min_denominator=None),
            dict(name="non_us_spelling_share", kind="two-way choice", rule=">= 0.75", min_denominator="3 discriminating spellings in the writer's text"),
            dict(name="e_mail_hyphen_share", kind="two-way choice", rule=">= 0.8", min_denominator="3 uses of e-mail/email"),
        ],
        secondary_features="all other habits in 08_control_analysis.py (RATE and BINARY lists), same thresholds",
        sample_sizes_words=[500, 1000],
        samples_per_text_unit=25,
        random_seed=20101212,
        roles=dict(question="own prose contains a sentence ending in '?'",
                   answer="no question of its own; quotes text containing '?' or directly follows another writer's post containing '?'",
                   statement="neither"),
        scoring_rule=("For each sample: score = number of primary rate features (first five) whose rule is met, 0-5, "
                      "features with too small a denominator count as not met. Two-way choices are reported per writer, not scored, "
                      "because their opportunities are too sparse in 500-1,000-word samples."),
        primary_outcome=("Area under the ROC curve of the score for held-out Satoshi samples vs samples from previously unseen writers, "
                         "within the same register (e-mail vs e-mail, forum answer vs forum answer), with a 95% bootstrap interval over writers; "
                         "plus per-feature AUCs and the share of unseen writers meeting each rule."),
        success_criterion="Lower bound of the 95% interval of the primary AUC above 0.5 in each register tested; report every register whatever the result.",
        exclusions=dict(
            threads_already_used=sorted({int(r["topic"]) for r in rows}),
            writers_already_used=sorted({r["writer"] for r in rows if r["writer"] != "SATOSHI"}),
            satoshi_text_already_used=["all 543 archive posts", "white paper", "cryptography, bitcoin-list and p2p-research list e-mails"],
        ),
        scope_limit="Evaluation is between held-out text of known authorship and anonymous population samples. The procedure is not to be applied to score named individuals.",
    )
    json.dump(spec, open(os.path.join(DATA, "protocol", "frozen_spec.json"), "w"), indent=1)
    print(json.dumps({k: spec[k] for k in ("version", "definition_files")}, indent=1))
    print("threads excluded:", len(spec["exclusions"]["threads_already_used"]), "writers excluded:", len(spec["exclusions"]["writers_already_used"]))

if __name__ == "__main__":
    main()
