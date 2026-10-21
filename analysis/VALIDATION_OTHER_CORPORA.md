# Validation of the forum fingerprint against the other Satoshi corpora

Purpose: test which features of the fingerprint in `STYLOMETRIC_FINDINGS.md` section 7 hold across register, using public writing attributed to the same author that the `posts/` archive does not contain. This is a within-author consistency check. It does not compare against anyone else.

## Corpora

| Corpus | Source | Date range | Documents | Words after cleaning |
|---|---|---|---|---|
| White paper | bitcoin.org/bitcoin.pdf (text via pdftotext; sentence spacing via pypdf) | 2008-10-31 | 1 | 3,216 |
| Cryptography mailing list | satoshi.nakamotoinstitute.org/emails/cryptography/ | 2008-10-31 to 2009-01-25 | 18 | 4,966 |
| bitcoin-list (SourceForge) | …/emails/bitcoin-list/ | 2008-12-10 to 2010-12-12 | 16 | 1,817 |
| p2p-research list | …/emails/p2p-research/ | 2009-02-11 to 2009-02-18 | 5 | 1,344 |
| All emails pooled, deduplicated | the three lists; the v0.1 announcement was sent to all three and is counted once | | 38 | 7,866 |
| Forum, BitcoinTalk (reference) | this repository, core corpus | 2009-11 to 2010-12 | 535 | 47,762 |
| Forum, P2P Foundation (reference) | this repository | 2009-02 | 3 | 868 |

Not included: the privately exchanged emails (to Mike Hearn, Dustin Trammell, Wei Dai, Hal Finney, Laszlo Hanyecz, Gavin Andresen) are not in the source site's email index that this script reads, so they were not fetched. They would add roughly a further few thousand words and could be run through the same script.

Cleaning (script `05_validate_other_corpora.py`): quoted lines (`>`), list footers, signatures, code-looking lines removed from emails; hard-wrapped lines re-joined; the white paper's headings, formulas, diagram labels, code appendix and references removed. The paper's abstract is also pasted into the first cryptography email and is therefore counted in both; it is 170 words.

Caveats: the e-mail corpora are small (the smallest, p2p-research, is 1,344 words), so counts below about 10 are indicative only. The pooled comparison is token-weighted. All numbers are in `data/agg/validation_other_corpora.csv`; cleaned texts are in `data/other_corpora_clean.jsonl`.

## Results

### Features that hold across every register (strengthened)

| Feature | White paper | Emails (pooled) | Forum BitcoinTalk |
|---|---|---|---|
| Two spaces after sentences (share of boundaries) | 79 of 79 = 1.00 (ordinary word gaps in the same PDF text: 5% double, so this is not an extraction artefact) | 229 of 242 = 0.946 | 1,485 of 1,505 = 0.987 |
| Semicolons | 1 | 1 | 3 |
| Em or en dashes | 0 | 0 | 0 |
| Exclamation marks | 0 | 5 (all in release notes) | 44 (0.9 per 1k) |
| "block chain" vs "blockchain" | 0 / 0 | 3 / 0 | 31 / 0 |
| "proof-of-work" hyphenated vs open | 16 / 0 | 40 / 0 | 12 / 1 |
| "double-spend(ing)" hyphenated vs open | 6 / 1 | 18 / 4 | 19 / 0 |
| "e-mail" vs "email" | 0 / 0 | 6 / 0 | 8 / 1 |
| "a lot" vs "alot" | 0 | 8 / 0 | 33 / 0 |
| "%" attached, never "percent" | 1 / 0 | 7 / 0 | 94 / 0 |
| "etc." with period, never bare | 0 | 3 / 0 | 5 / 0 |
| Bullet lists with "- ", never "*" | n/a | 49 / 0 | 137 / 0 |
| Numbered lists "1." style | 0 | 0 | 0 |
| Thousands separators in large round numbers | yes ("21,000,000") | yes ("21,000,000", "10,500,000") | yes in 2009–early 2010, inconsistent later |
| Verdict openers "Right,"/"Yes," at paragraph start | 0 (not a reply) | 7 ("Right, if it's equal in length…", "Right, exactly.", "Yes, but we can win…") | 36 |
| "probably" as the preferred hedge | 1 | 7 | 48 |
| "obviously" / "certainly" boosters | 1 / 0 | 0 / 0 | 2 / 4 |
| Logical quotation (stop outside quotes, except full sentences) | 1 outside, 0 inside | 3 outside, 2 inside (both full-sentence quotations) | 39 outside, 7 inside |
| British/American spelling mix | `favour` vs `realizes` | `neighbour(s)` ×4, `optimisation` ×3 vs `decentralized` ×3 (one text), `optimize`, `minimize`, `judgment` | 38 vs 38 tokens on the cleaned list |

The spelling split is the same split in every corpus: `-our` and `-isation` words British (`favour` in the paper; `neighbour`, `optimisation` in the emails), `decentralized`/`realize`/`optimize`/`judgment` American. The one `optimize` in the cryptography list (2008-11) and the `optimisation`s in the bitcoin-list (2009-02, 2010-12) show the mix is present from the first month of the record, not something that developed on the forum.

### Features that move with register (topic- or genre-driven, as the report predicted)

| Feature | White paper | Emails (pooled) | Forum |
|---|---|---|---|
| Mean sentence length (words) | 22.3 | 15.1 | 12.6 |
| Contractions per 1k | 6.5 | 20.9 | 30.4 |
| Contracted share where a choice existed | 0.26 | 0.71 | 0.86 |
| Passive constructions per sentence | 0.44 | 0.18 | 0.12 |
| "the" per 1k | 74 | 62 | 53 |
| "I" per 1k | 0 | 7.4 | 15.9 |
| "you" per 1k | 0 | 9.5 | 20.9 |
| "we" per 1k | 7.5 | 2.4 | 6.2 |
| "if" per 1k | 5.9 | 9.9 | 11.3 |
| "If you" sentence openers | 0 | 13 | 99 |
| Question marks per 1k | 0 | 0.13 | 5.0 |
| Commas per 1k | 47.9 | 40.8 | 36.5 |
| Double quotes per 1k | 5.6 | 3.3 | 9.7 |
| Parentheses per 1k | 0 | 2.2 | 4.5 |
| "I think" / "not sure" | 0 / 0 | 3 / 0 | 53 / 18 |
| "It would be" | 2 | 4 | 46 |

These form a clean gradient from paper to list to forum. The direction is exactly what a single writer adjusting formality produces: the paper has no first or second person at all (0 "I", 0 "you") and quadruple the passive rate; the mailing lists sit between; the forum is the conversational extreme. None of these should be used as fixed author constants; they are register constants.

One feature that does not fit the gradient is "will": 5.0 per 1k in the paper and 5.5 in the emails against 2.8 on the forum, where "would" (6.7) and "it'll" take over. Predictions in the 2008–2009 writing are stated in the future indicative; on the forum they are hedged into the conditional. This is consistent with a writer growing more cautious in public as the project became real, and matches the 2010 drift noted in the main report (section 5 of the profile addendum).

### Features that could not be tested

* P2P Foundation spacing: still 0 of 32 double, consistent with that platform collapsing whitespace; the paper and the e-mail archives both preserve double spacing, which makes it very unlikely the author ever single-spaced by choice.
* Emoticons: none in paper or emails; the forum smileys remain unverifiable in form.
* Day-first dates: no dates typed in prose in the paper or the emails, so the forum's 79 day-first dates have no cross-register check.
* "OK", "vs", "e.g.", "i.e.", "BTW": absent from paper and emails (0 each); the forum conventions (always "OK", "vs" without period, "e.g." without comma, no "i.e.") stand unconfirmed but uncontradicted.

## Effect on the report's claims

Strengthened (now seen in three registers over 26 months, 2008-10 to 2010-12): two-space sentence spacing; near-total absence of semicolons and dashes; hyphenated "proof-of-work" and "double-spend"; two-word "block chain"; "e-mail"; "- " bullets; "%" attached; "etc." with period; "probably" over boosters; logical quotation; "Right,"/"Yes," reply openers; and the British/American split with the same words on each side.

Reclassified from author constants to register-dependent: sentence length, contraction rate, passive rate, pronoun rates, "if" and "If you" rates, question rate, "I think", "It would be". They remain characteristic of his forum register and are still useful for comparison against other forum writing, but a formal text by the same hand would score very differently on them.

Unchanged: no claim about identity. The validation shows internal consistency of a single writer across registers; it says nothing about who that writer is.

## Reproduce

```
cd analysis/scripts
mkdir -p /tmp/val/emails
# download the 39 e-mail pages listed at satoshi.nakamotoinstitute.org/emails/{cryptography,bitcoin-list,p2p-research}/N/
#   into /tmp/val/emails/<list>_<N>.html, and bitcoin.org/bitcoin.pdf into /tmp/val/whitepaper.pdf
python3 05_validate_other_corpora.py --cache /tmp/val
```
