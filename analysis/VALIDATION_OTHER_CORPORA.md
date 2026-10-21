# Validation of the forum fingerprint against the other Satoshi corpora

Purpose: test which features of the fingerprint in `STYLOMETRIC_FINDINGS.md` section 7 hold across register, using public writing attributed to the same author that the `posts/` archive does not contain. This is a within-author consistency check; the comparison with other writers is in `CONTROL_CORPUS.md`.

Revision 2 changes (details in `REVISION_NOTES.md`): all features now come from `measures.profile()`, the function used for the forum tables; the white paper was re-cleaned (references, figure labels, captions and formula fragments removed; numbered steps kept as a list); text published in more than one corpus is reported with and without the shared passages; the code-only `post_475` no longer counts as a document; and the "will"/"would" reading is withdrawn.

## Corpora

| Corpus | Source | Date range | Documents | Words after cleaning |
|---|---|---|---|---|
| White paper | bitcoin.org/bitcoin.pdf (text via pdftotext; sentence spacing via pypdf) | 2008-10-31 | 1 | 3,002 |
| Cryptography mailing list | satoshi.nakamotoinstitute.org/emails/cryptography/ | 2008-10-31 to 2009-01-25 | 18 | 4,966 |
| bitcoin-list (SourceForge) | …/emails/bitcoin-list/ | 2008-12-10 to 2010-12-12 | 16 | 1,817 |
| p2p-research list | …/emails/p2p-research/ | 2009-02-11 to 2009-02-18 | 5 | 1,344 |
| All e-mails pooled | the three lists; the v0.1 announcement sent to all three is counted once | | 38 | 7,866 |
| Forum, BitcoinTalk (reference) | this repository, core corpus | 2009-11 to 2010-12 | 534 | 47,898 |
| Forum, P2P Foundation (reference) | this repository | 2009-02 | 3 | 868 |

The first version listed 535 BitcoinTalk documents because it counted the code-only `post_475`, which has no prose; `measures.profile()` now drops empty documents, so the reference matches the core corpus (534 BitcoinTalk + 3 P2P Foundation = 537).

Not included: the privately exchanged e-mails (to Mike Hearn, Dustin Trammell, Wei Dai, Hal Finney, Laszlo Hanyecz, Gavin Andresen) are not in the source site's e-mail index that this script reads.

### Cleaning

E-mails (`clean_email`): lines quoted from others (`>`), list footers, signatures and code-looking lines are removed, and hard-wrapped lines are re-joined.

White paper (`clean_whitepaper`, rules W1–W7 in the script docstring): everything from "References" on is dropped; title block, section headings and page numbers are dropped; the C listing, definitions (`p = probability…`), result tables and formula lines are dropped; diagram labels and figure captions ("Item Item ...", "Owner 1's Public Key", "Transactions Hashed in a Merkle Tree…") are dropped; line-end hyphens are rejoined ("proof-" + "of-work"); and the six numbered network steps stay on their own lines. The first version kept the reference list, several diagram labels and formula fragments, and merged the numbered steps into running text, which is why it reported no numbered list in the paper. Every line the new cleaner drops was checked by hand: all 156 are headings, labels, captions, definitions, code or table rows, and no prose line is lost. Cleaned texts are in `data/other_corpora_clean.jsonl`.

### Shared passages

Some text was published in more than one corpus. A sentence is marked **shared** when it has at least five words and at least half of its 6-word shingles (or, under six words, the whole sentence) also occur in a different source family (paper, e-mail, forum). Overlap per document (`data/agg/shared_passages.csv`):

| Document | Words | Shared words | Closest document elsewhere | 6-gram Jaccard |
|---|---|---|---|---|
| p2p-research e-mail 35 / forum `post_1` | 519 / 518 | 517 / 518 | each other (the v0.1 announcement essay) | 0.998 |
| bitcoin-list e-mail 33 / forum `post_525` | 69 / 65 | 52 / 57 | each other (release note) | 0.938 |
| bitcoin-list e-mail 30 / forum `post_167` | 127 / 127 | 103 / 105 | each other (release note) | 0.906 |
| bitcoin-list e-mail 29 / forum `post_24` | 102 / 103 | 49 / 51 | each other (changelog) | 0.403 |
| cryptography e-mail 1 / white paper | 271 / 3,002 | 166 / 229 | each other (the abstract and introduction) | 0.047 |
| others (cryptography 5, p2p-research 39, `post_13`, `post_209`) | | 7–46 | | ≤ 0.13 |

Every corpus is reported twice: **all** text, and **independent** text with the shared sentences removed (229 words from the paper, 961 from the pooled e-mails, 245 from BitcoinTalk, 518 from the P2P Foundation posts). Removal deletes the sentence and the spaces after it from the original, so the spacing of the remaining boundaries is untouched.

## Results

All numbers are in `data/agg/validation_other_corpora.csv` (both variants, plus e-mails by year). Values below are "all / independent" where they differ.

### Features that hold across every register

| Feature | White paper | E-mails (pooled) | Forum, BitcoinTalk |
|---|---|---|---|
| Two spaces after sentences (share of boundaries) | 79 of 79 = 1.00 (ordinary word gaps in the same PDF text are 5% double, so this is not an extraction artefact) | 225 of 237 = 0.949 / 194 of 203 = 0.956 | 1,480 of 1,498 = 0.988 / 1,476 of 1,494 |
| Semicolons | 1 | 1 | 3 |
| Em or en dashes | 0 | 0 | 0 |
| Exclamation marks | 0 | 5 / 3 (release notes) | 44 / 42 (0.9 per 1k) |
| "block chain" vs "blockchain" | 0 / 0 | 3 / 0 | 31 / 0 |
| "proof-of-work" hyphenated vs open | 18 / 0 (13 / 0 independent) | 40 / 0 (36 / 0) | 12 / 1 (11 / 1) |
| "double-spend(ing)" hyphenated vs open | 6 / 1 (4 / 1) | 18 / 4 (11 / 4) | 19 / 0 |
| "e-mail" vs "email" | 0 / 0 | 6 / 0 | 8 / 1 |
| "a lot" vs "alot" | 0 | 8 / 0 | 34 / 0 |
| "%" attached, never "percent" | 1 / 0 | 7 / 0 | 94 / 0 |
| "etc." with period, never bare | 0 | 3 / 0 | 5 / 0 |
| Bullet lists "- ", never "* " | none | 49 / 0 (35 / 0) | 137 / 0 (120 / 0) |
| Numbered lists `1)`, never `1.` | 6 / 0 (the network steps) | 0 / 0 | 39 / 0 |
| Verdict openers "Right,"/"Yes,"/"No," at line start | 0 (not a reply) | 7 | 37 |
| Hedges vs boosters | 1 vs 2 ("obviously", "of course") | 19 vs 1 | 278 vs 26 |
| Logical quotation (stop outside quotes, except full sentences) | 1 outside, 0 inside | 3 outside, 2 inside (both full-sentence quotations) | 39 outside, 7 inside |
| Spelling: non-US / US-only / `-ize` | 1 (`favour`) / 0 / 2 (`characterized`, `realizes`) | 9 (`neighbour(s)`, `optimisation`, `synchronisation`) / 0 / 6 (`decentralized`, `optimize`, `specialized`) | 27 / 4 / 26 |

The spelling mix is present from the first document: the paper has `favour` beside `realizes` and `characterized`, and the e-mails `optimisation` beside `optimize`. Under the revised three-class scheme the e-mails contain no US-only form; the paper and e-mails therefore show the same non-US forms with `-ize`, which is also Oxford British usage. The first version's statement that the e-mails showed the "British/American split with the same words on each side" overstated this.

Hedges against boosters: in the paper, with almost no stance marking, the direction does not hold (1 hedge, 2 boosters). The low-boost stance is therefore a feature of the conversational registers, not of all writing.

### Features that move with register

| Feature | White paper | E-mails (pooled) | Forum |
|---|---|---|---|
| Mean sentence length (words) | 22.7 | 15.1 | 12.6 |
| Contractions per 1k | 7.0 | 20.9 | 30.5 |
| Contracted share where a choice existed | 0.26 | 0.71 | 0.86 |
| Passive constructions per sentence | 0.48 | 0.18 | 0.12 |
| "the" per 1k | 78 | 62 | 53 |
| "I" group per 1k | 0 | 7.4 | 15.9 |
| "you" group per 1k | 0 | 9.5 | 20.9 |
| "we" group per 1k | 8.0 | 2.4 | 6.2 |
| "if" per 1k | 5.7 | 9.9 | 11.3 |
| "If you…" sentence openers | 0 | 14 (9 bare) | 102 (77 bare) |
| Question marks per 1k | 0 | 0.13 | 5.0 |
| Commas per 1k | 40.3 | 40.8 | 36.5 |
| Double quotes per 1k | 0.7 | 3.3 | 9.7 |
| Parentheses per 1k | 0 | 2.2 | 4.5 |
| "I think" / "not sure" | 0 / 0 | 3 / 0 | 53 / 19 |
| "It would be" | 2 | 4 | 46 |

These form a gradient from paper to list to forum, the direction a single writer adjusting formality produces. Removing shared passages changes none of these by more than 1.5 per 1k (largest: e-mail contractions 20.9 to 22.3). None of them should be used as a fixed author constant.

### "will" and "would": the earlier reading is withdrawn

The first version noted "will" at 5.0 per 1k in the paper and 5.5 in the e-mails against 2.8 on the forum, and read it as the writer "growing more cautious in public". That comparison confounds date with register: the paper and the early e-mails are specifications and announcements, which use the future tense. Separating the two:

| Text | "will" (bare) per 1k | "would" per 1k |
|---|---|---|
| E-mails 2008 (16 documents, 4,106 words) | 6.3 | 6.3 |
| E-mails 2009 (17 documents, 3,498 words) | 4.9 | 3.7 |
| Forum 2009-11..12 | 3.2 | 7.1 |
| Forum 2010-01..06 | 1.5 | 7.2 |
| Forum 2010-07..09 | 3.5 | 6.1 |
| Forum 2010-10..12 | 2.6 | 7.5 |

The 2008 e-mails already use "would" at the forum rate, and within the forum neither rate trends over 14 months. There is no evidence of a shift from "will" to "would" over time; the difference is between genres. (E-mails from 2010 total 262 words and are not interpreted.)

### Features that could not be tested

* P2P Foundation spacing: 0 of 31 boundaries double, consistent with that platform collapsing whitespace; the paper and the e-mail archives both preserve double spacing, which makes it very unlikely the author single-spaced by choice there.
* Emoticons: none in paper or e-mails; the forum smileys remain unverifiable in form.
* Day-first dates: none typed in the paper or the e-mails.
* "OK", "vs", "e.g.", "i.e.", "BTW": absent from paper and e-mails.

## Effect on the report's claims

Holding in all three registers over 26 months (2008-10 to 2010-12), with and without shared passages: two-space sentence spacing; near-total absence of semicolons and dashes; hyphenated "proof-of-work" and "double-spend"; two-word "block chain"; "e-mail"; "- " bullets and `1)` numbering; "%" attached; "etc." with period; logical quotation; and the coexistence of non-US forms with `-ize`.

Register-dependent: sentence length, contraction rate, passive rate, pronoun rates, "if" and "If you" rates, question rate, "I think", "It would be", the hedge-over-booster balance, and "will"/"would".

Distinctiveness is a separate question: several of the cross-register constants (no semicolons or dashes, "%", "block chain", logical quotation, `1)` lists) were shared by most contemporary forum writers (`CONTROL_CORPUS.md`). Holding across registers makes a habit reliable for this writer; it does not make it rare.

## Reproduce

```
cd analysis/scripts
mkdir -p /tmp/val/emails
# download the 39 e-mail pages listed at satoshi.nakamotoinstitute.org/emails/{cryptography,bitcoin-list,p2p-research}/N/
#   into /tmp/val/emails/<list>_<N>.html, and bitcoin.org/bitcoin.pdf into /tmp/val/whitepaper.pdf
python3 05_validate_other_corpora.py --cache /tmp/val
```
