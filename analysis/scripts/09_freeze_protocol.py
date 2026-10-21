#!/usr/bin/env python3
"""Record definition hashes and the incomplete next-test design.

This script is not an AUC evaluator or a completed preregistration.
PROTOCOL_NEXT_TEST.md explains the unselected material and evaluation choices.

Writes data/protocol/frozen_spec.json with:
  * SHA-256 of the definition files (textutil.py, cleaning.py, measures.py,
    07_control_corpus.py for the counts and roles, 08_control_analysis.py for
    the descriptive thresholds and sampling); changes must be reported
  * the existing features and proposed future thresholds, minimum opportunity
    counts, sample sizes, role definitions, random seed and scoring rule
  * the identifiers of every thread and writer already used, which the next
    test must exclude (writer pseudonyms require the original account mapping)
  * explicit incomplete-status fields and pending evaluation decisions

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
        version="protocol-1.1-draft",
        status="definitions recorded; evaluation incomplete",
        ready_for_confirmatory_collection=False,
        change_from_protocol_1="Correct the frozen-status overclaim; definitions and measured outputs unchanged.",
        positive_sources=None,
        evaluation_implementation=None,
        primary_sample_size_words=None,
        pending_decisions=[
            "Exact unused positive source/message IDs, provenance, inclusion rules and hashes",
            "Matched audiences, purposes and technical roles; no unused forum positives are identified",
            "Stable account exclusions: collection-specific W labels cannot identify writers in new collections",
            "Primary sample length and reporting of whole-post sample overshoot",
            "Joint feature scoring on the same sampled posts; writer weighting, ties and missing-feature policy",
            "Spacing availability across sources; low opportunity is not absence of a habit",
            "Bootstrap units, repetitions, seed and scope: one positive author and overlapping sample draws",
            "Commit and hash the evaluator and completed protocol before confirmatory collection",
        ],
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
        primary_outcome=("Proposed, not implemented: AUC of joint sample scores within registers with unused positive text and matched negatives. "
                         "Intervals require a specified dependence model: negative-writer resampling alone conditions on the selected Satoshi material; "
                         "positive conversation/episode clusters are needed to represent variability across his correspondence. "
                         "Overlapping sample draws are not independent replications."),
        success_criterion="Proposed only, inactive until the complete protocol and evaluator are committed: lower 95% AUC bound above 0.5 in each feasible matched register; report every result.",
        exclusions=dict(
            threads_already_used=sorted({int(r["topic"]) for r in rows}),
            writers_already_used=sorted({r["writer"] for r in rows if r["writer"] != "SATOSHI"}),
            writer_id_scope="W labels are collection-specific, not stable account identifiers. Recover original account identities before excluding writers from a new collection.",
            satoshi_text_already_used=["all 543 archive posts", "white paper", "cryptography, bitcoin-list and p2p-research list e-mails"],
        ),
        scope_limit="Evaluation is between held-out text of known authorship and anonymous population samples. The procedure is not to be applied to score named individuals.",
    )
    json.dump(spec, open(os.path.join(DATA, "protocol", "frozen_spec.json"), "w"), indent=1)
    print(json.dumps({k: spec[k] for k in ("version", "definition_files")}, indent=1))
    print("threads excluded:", len(spec["exclusions"]["threads_already_used"]), "writers excluded:", len(spec["exclusions"]["writers_already_used"]))

if __name__ == "__main__":
    main()
