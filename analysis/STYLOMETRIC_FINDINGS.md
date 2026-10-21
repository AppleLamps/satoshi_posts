# Stylometric findings: the Satoshi Nakamoto post archive

Repository `applelamps/satoshi_posts`, source files from commit `b442311`, 543 files under `posts/`. Revision 2 (see `REVISION_NOTES.md` for every change from the first version).
All counts below are reproducible with the scripts in `analysis/scripts/` (see `analysis/README.md`). Every named feature is computed by one function in `scripts/measures.py`, which the per-post table, the evidence counts, the validation and the control comparison all import, so a feature has the same value wherever it is reported. Every quoted example is listed in `analysis/evidence.csv` with its file, 1-based line and column, and `04_verify_evidence.py` confirms that all 357 quotations appear verbatim at those positions.

Companion documents: `VALIDATION_OTHER_CORPORA.md` (the white paper and the 2008–2010 e-mails), `CONTROL_CORPUS.md` (other writers in the same threads), `PROFILE_ADDENDUM.md` (what the writing does and does not say about the writer).

Notation: "per 1k" means occurrences per 1,000 word tokens of the author's own prose; "posts" means distinct posts containing the feature. Lexical items (hedges, boosters, adverbs, spellings, term forms) are counted case-insensitively; positional items (sentence openers, verdict openers) are counted in their capitalised form at that position. Locations are written `posts/post_N.txt:line:col`. Non-breaking spaces in the files are shown as `\xa0`.

---

## 1. Corpus and extraction quality

### 1.1 Inventory and coverage

| Item | Value |
|---|---|
| Files under `posts/` | 543 (`post_1.txt` … `post_543.txt`), all processed |
| Platform (line 3 of each file) | BitcoinTalk 539, P2P Foundation 4 |
| Timestamps (line 5) | 2009-02-11 to 2010-12-12, plus one file dated 2014-03-06 |
| Files whose body spans more than one line | 1 (`post_475.txt`, a code diff) |
| Raw word tokens in all files (headers included) | 63,456 |
| Author's own prose after cleaning (core corpus) | 537 posts (534 BitcoinTalk, 3 P2P Foundation), 48,766 word tokens, 4,239 types, 3,858 sentences with at least one word, 1,745 paragraphs, 291,944 characters |

Files not entering the author-wide statistics (all were processed and are in `post_features.csv`):

| File(s) | Reason | Evidence |
|---|---|---|
| `post_5`, `post_6`, `post_9`, `post_11` | "Repost:" threads: Satoshi re-posting other members' messages from the old forum, each introduced by a dashed rule and a username (406 words of other people's text) | X01, `posts/post_5.txt:6:3` `--------------------bitcoinbitcoin:` |
| `post_543` | "I am not Dorian Nakamoto." (2014). Authorship of this message is disputed in public reporting and it lies three years after every other post; the archive's timestamp `2014-03-06 00:00:00` is a placeholder (the source site gives 2014-03-07T01:17Z) | X04 |
| `post_475` | Body is a code diff only; no prose | extraction_log flag `has_code` |

The core corpus is therefore 537 posts (the 543 files minus these 6). The four P2P Foundation posts (`post_1`, `post_2`, `post_3`, plus the disputed `post_543`) contribute 868 words from 3 posts.

### 1.2 What the scraper did to the text

The notebook `post_scraper.ipynb` wrote `BeautifulSoup.get_text()` of the post `div`. That call removes every HTML block boundary, so in the repository files:

* Paragraphs run together with no space: `posts/post_1.txt:6:1706` `s.One of` (X08). Any "no space after a period" pattern in the raw files is an extraction artefact, not the author's habit.
* Forum quote blocks (quoted text of other members) are fused with Satoshi's reply: `posts/post_60.txt:6:3` `Quote from: Sabunir on February 16, 2010, 08:51:51 AM. Perhaps it has to…` (X05). 201 such quote blocks occur in 149 files and contain 7,032 words of other people's text.
* The P2P Foundation signature is fused with the URL: `posts/post_1.txt:6:3045` `Satoshi Nakamotohttp://www.bitcoin.org` (X06).
* Forum emoticon images were dropped silently (see 1.4).
* The author's double spaces survive as U+00A0 + space: `posts/post_60.txt:6:375` `e.\xa0 The` (X07). 2,999 non-breaking spaces occur in 476 files.

### 1.3 How block structure was recovered

Because the boundaries cannot be reconstructed from the text alone, `00_fetch_source_html.py` fetched the current structured HTML of the same 543 posts from the site the archive was scraped from (satoshi.nakamotoinstitute.org), and `01_extract.py` aligned each repository body with it. The alignment is accepted only when the two texts are identical once all whitespace is removed. Result: 537 files identical, 6 files (`post_241`, `post_253`, `post_272`, `post_361`, `post_483`, `post_520`) differing only in escaped `\n`/`\r` characters inside code fragments. No file needed the heuristic fallback. The repository text remains the primary corpus; the HTML was used only to label segments (own prose, quote header, quote, code, emoticon) and to restore line and paragraph breaks.

Additional manual attribution rules (R8 to R12b in the script docstring): the four reposts; e-mail style `> ` quoted lines in `post_10` (X02); a pasted list of other members' benchmark results in `post_351` from `aceat64:` onward (X03); and runs of code-looking lines inside prose (C++, shell commands, diffs) labelled `inline_code` and excluded from prose statistics. Rule R12b, added in revision 2, keeps the explanation after a ` -- ` on a code line as the author's prose: the first version had discarded three such explanations in `post_241` (139 words, including the reasoning about password delays quoted in the profile addendum).

### 1.4 Features whose original form cannot be established from this archive

* **Sentence spacing in the P2P Foundation posts.** The three 2009 posts have 31 single-spaced and 0 double-spaced sentence boundaries, while BitcoinTalk posts are double-spaced 98.8% of the time (section 3.1). The source HTML of the P2P posts contains no non-breaking spaces at all, which is consistent with that platform collapsing whitespace. Whether the author typed one or two spaces there cannot be determined.
* **Emoticons.** The forum rendered text smileys as images; the scraper dropped them. The source HTML shows 11 (6 "Smiley", 3 "Wink", 1 "Huh", 1 "Undecided") in 11 posts (`post_20, 91, 126, 141, 184, 202, 309, 327, 372, 374, 417`). The exact characters the author typed are unknown. No literal text smiley survives in his prose.
* **Line breaks inside code blocks** (lost in both the archive and `get_text`).
* **Curly versus straight quotation marks.** All 1,473 apostrophes and 463 double quotes in his prose are straight; this is consistent with plain-text forum input and says little about the author's editor.
* **Capitalisation and punctuation of thread titles** (line 1) are forum metadata shared with other posters and were not analysed as the author's prose.

### 1.5 Duplicates and repeated material

`near_duplicates.csv` and `repeated_sentences.csv` list shared 6-word shingles and exact repeated sentences within the archive. Text shared with the other Satoshi corpora (for example `post_1` with the p2p-research announcement, `post_167` with a bitcoin-list release note) is listed in `data/agg/shared_passages.csv` and handled in the validation report. All repeats are release boilerplate or deliberate repetition rather than copies of whole posts: SHA1 checksum lines repeated across `post_371/373/375`; the 0.3.13 release notes repeated in `post_465/471` (Jaccard 0.35); changelog bullets in `post_13/24`; sample account code in `post_497/535`; "Sorry to be a wet blanket." used twice (`post_166`, `post_214`). Ten quote headers quote Satoshi himself; those quotes are excluded like all others. No post is a duplicate of another, so no de-duplication beyond quote removal was needed.

### 1.6 Edited posts

BitcoinTalk shows a "Last edit" stamp on edited posts. The live thread pages (fetched for the control corpus) give stamps for 105 archived posts: 103 edited by the author and 2 by others (a moderator's thread move, a co-developer). Most author edits are same-day corrections, but 25 posts were edited more than 24 hours after posting, among them `post_42` (posted 2010-02-05, last edited 2010-08-27, with difficulty entries through 2010-08-26), `post_74` (edited nine months later) and three alert posts edited on 2010-10-04 (`data/agg/edited_posts.csv`, `data/forum_last_edit.csv`). The archive stores only the final text, so the content of a late-edited post cannot be assigned confidently to its posting date. Every time-based table is therefore also computed without the 25 late-edited posts and without all 103 edited posts (section 4).

---

## 2. Strongest findings (summary)

Each finding has a detailed entry in section 3 with counts, examples and competing explanations. Evidence strength within the archive: **strong** = hundreds of instances across most posts and periods; **moderate** = dozens of instances across many posts; **weak** = few instances or confounded. The last column reports how many contemporary writers in the same threads share the habit (`CONTROL_CORPUS.md`); "common" means shared by about 40% or more of the writers who had the opportunity, which makes the habit characteristic but not distinctive.

| # | Finding | Measure | Strength | Among contemporaries |
|---|---|---|---|---|
| 1 | Two spaces after sentences (BitcoinTalk) | 1,480 double vs 18 single (0.988); 435 of 534 posts | strong | 27% of writers also ≥ 0.90 |
| 2 | Contractions dominate | 1,470 contractions, 30 per 1k; contracted form chosen 86% of the time where a full form was possible | strong | 19% of writers ≥ 0.80 |
| 3 | Conditional, reader-directed syntax: "if" 11.2 per 1k; "If you…" opens 102 sentences (77 with bare "you", 25 with "you're"/"you've"/"you'd"/"you'll"); "you" 20.7 per 1k vs "I" 15.7 | 546 "if" in 268 posts | strong | "If you" openers: 10% of writers; "if" rate: 25% |
| 4 | Short, plain sentences: median 11 words, mean 12.6 | 3,858 sentences | strong | register-dependent; 32nd percentile |
| 5 | Semicolons, dashes and exclamation marks almost absent | 3 prose semicolons; 0 em/en dashes; 44 exclamation marks | strong | common (56–79% of writers) |
| 6 | Logical punctuation: full stop and comma outside closing quotation marks | 39 outside vs 7 inside (the 7 are full-sentence quotations) | moderate | common (64%) |
| 7 | Lists: numbered items `1)` (39 items, 13 posts, never `1.`), bullets `- ` (140 items, 31 posts, never `*`) | 179 list lines | moderate | `1)`: common (52%); `- `: 32% of 19 writers |
| 8 | Spelling in three classes: non-US forms 27 tokens (25 posts: `optimisation` 8, `colour`, `grey`, `favour`, `neighbour`, `defence`, `labelled`, `fulfil`, `maths`, `analysed`…); US-only forms 5 (`color` 4, `gotten` 1); `-ize` forms valid in both American and Oxford British spelling 28 (22 posts) | 60 tokens | moderate | non-US share ≥ 0.75: 24% of writers |
| 9 | Hedged stance: "I think" 54, "maybe" 53, "probably" 49, "not sure" 19, "I guess" 15; boosters rare: "definitely" 10, "certainly" 4, "clearly" 3, "surely" 3, "obviously" 2 | 281 hedges vs 26 boosters (92%) | moderate | common (46% of writers ≥ 0.85) |
| 10 | Verdict-first replies: lines open with "Right,", "Yes,", "No,", "True,", "OK," | 37 in 35 posts | moderate | 39% of writers |
| 11 | Term formation: "block chain" (31) never "blockchain"; "double-spend" hyphenated (23 vs 0 open); "proof-of-work" (14 vs 1); "e-mail" (8 vs 1); "a lot" (35) never "alot"; "OK" (14) never "okay" | | moderate | "e-mail": 15%; "double-spend": 30%; "block chain", "OK": common |
| 12 | Currency unit switched from "bc" (Dec 2009–Feb 2010, 3 uses) to "BTC" (May–Dec 2010, 15 uses) | | moderate (small n) | not tested |
| 13 | Very few misspellings: `walkthough`, `idealogical`, `easer`, `Allright`, `filewall`, `generateds`, `divy`, `moreso`, `lets` for "let's" (2) | ~9 slips in 48,766 words | moderate | not tested |
| 14 | Politeness formulas and a few recurring idioms: "Thanks" 25 posts, "Sorry" opens 9 posts, "please test"; "wet blanket" (2), "eat crow", "hornet's nest", "in a nutshell" (2), "bogged down", "out the door", "up to speed" | | moderate | not tested |
| 15 | Case-preserving habit: identifiers keep their lower case at sentence start (`wxWidgets really pays off`, `getwork allows…`) | 20 sentences | moderate | not tested |

---

## 3. Detailed results

### 3.1 Spacing and formatting

**Double space after sentence-final punctuation (F01).** A boundary is a letter or digit, then `.`, `!` or `?`, optional closing quote or parenthesis, one or more spaces, and an upper-case letter; listed abbreviations are not boundaries (`measures.sentence_spacing`). In BitcoinTalk prose, 1,480 boundaries have two spaces and 18 have one (share 0.988; 435 of 534 posts have at least one). The first version reported 1,549 and 25 from a looser pattern in one script and 1,485 and 20 from a stricter one in another; both now use the single definition. The forum stored the second space as `&nbsp;`, which is why the repository files contain `.\xa0 ` sequences. Examples: `posts/post_7.txt:6:486` `k.\xa0 O`; `posts/post_53.txt:6:285` `c.\xa0 A`; `posts/post_400.txt:6:41` `h.\xa0 Someone`. The share is at least 0.95 in every month from 2009-11 to 2010-12 (`compare_month.csv`, column `double_space_share`). Of the 18 single-spaced boundaries, 10 are in one post (`post_328`, the one genuine exception, section 5) and 3 inside a pasted quotation of documentation (`post_22`); the other 5 are isolated, one per post. Competing explanation: none for BitcoinTalk, since the platform stores a typed double space as nbsp + space for every member alike. Distinctiveness: 32 of 120 contemporary writers in the same threads (27%) double-space at least as consistently (`CONTROL_CORPUS.md`), so the habit is stable for this writer but common in his milieu. The P2P Foundation posts are the exception discussed in 1.4 (F02: `posts/post_1.txt:6:67` `n. I`).

**Paragraphing.** 1,745 paragraphs, mean 2.21 sentences, median 2; 656 (37.6%) are one sentence long. Longer posts are built from many short paragraphs rather than long ones (distribution: 1 sentence 656, 2 sentences 535, 3 sentences 306, 4 sentences 129, 5+ sentences 113; 6 paragraphs contain no word, such as a lone URL). This is measured on breaks recovered from the source HTML, not from the repository text.

**Lists (F10).** Numbered lists use `1)`, `2)` (39 items in 13 posts; `1.` style 0). Bullet lists use `- ` (140 items in 31 posts; `* ` 0). Examples: `posts/post_119.txt:6:3` `3) Nothing, if sending by bitcoin address`; `posts/post_3.txt:6:135` `- Whenever someone finds proof-of-work to generate a block, th…`. List items usually have no terminal punctuation (797 line-final units without `.!?`, 192 posts), which also lowers the measured sentence length.

**Release-note template (F27).** Announcements follow a fixed skeleton: `Version X is now available` (6 posts), a `Changes:` block of `- ` bullets, `Download:` plus URL, often SHA1 lines. "I uploaded … to SVN" appears 14 times (14 posts): `posts/post_38.txt:6:3` `I uploaded this fix to the SVN`. "SVN rev N" occurs 33 times in 32 posts; "rev" is never spelled out.

**Post-hoc edits (F25).** Four posts carry an explicit `Edit:` or `Update:` marker (`posts/post_310.txt:6:585`, `posts/post_246.txt:6:446`). Inline corrections are otherwise made in a new sentence ("Sorry, actually it's ECDSA", `post_276`).

### 3.2 Punctuation

Totals over the core corpus (`punctuation_syntax_totals.csv`):

| Mark | Count | Per 1k words | Posts | Note |
|---|---|---|---|---|
| Comma | 1,792 | 36.7 | 450 | moderate; 1 comma per 2.2 sentences |
| Colon | 327 | 6.7 | 160 | mainly introducing lists, URLs, code |
| Parentheses (open) | 217 | 4.5 | 143 | 58 stand-alone parenthetical sentences; `).` 25 vs `.)` 4 |
| Question mark | 241 | 4.9 | 139 | 217 interrogative sentences; 39 posts end on a question |
| Double quotes | 463 | 9.5 | 113 | 97 posts; used for UI strings, switches, terms being named |
| Exclamation mark | 44 | 0.91 | 36 | see below |
| Ellipsis | 17 | 0.35 | 16 | "That's amazing...", "Sigh...", `[params...]` |
| Double hyphen `--` | 10 | 0.21 | 3 | as a dash in only 2 prose contexts |
| Semicolon | 4 | 0.08 | 4 | 3 in prose, 1 inside a URL |
| Em dash / en dash | 0 | 0 | 0 | none in 48,766 words |
| Spaced hyphen as dash | 1 | | 1 | `(credit - debit)` in `post_225`; the 142 "spaced hyphens" in the totals table are `- ` bullet markers and switches |

**Semicolons (F11).** Three in prose: `posts/post_3.txt:6:1319` `…positive feedback loop; as users increase, the value…`; `posts/post_284.txt:6:161` `…SHA-256 didn't work correctly; it returned the same incorrec…`; `posts/post_421.txt:6:1243` `…easily available as a package; a lot of people were frustrat…`. Independent clauses are otherwise joined by a full stop or a comma plus "but"/"so"/"and".

**Dashes (F12).** No em or en dash anywhere. `--` is used as a gloss separator in a command list (`posts/post_106.txt:6:118` `getreceivedbyaddress -- amount received on…`) and twice as a sentence dash (`post_54` "-- fixed", `post_166`). Parentheses do the work a dash would do: `posts/post_18.txt:6:544` `(0.1.5 doesn't have -min so it would be an open window)`.

**Exclamation marks (F14).** 44 marks in 36 posts, 0.9 per 1k. They cluster in release announcements and thanks: `posts/post_63.txt:6:191` `IP address, post it here!`; `post_288` "Please upgrade to 0.3.6 ASAP!" (2 marks in an 87-word emergency alert, the highest rate in the corpus); `post_124` `(thanks you guys!)`. Technical explanations essentially never carry one (protocol_design topic: 0.59 per 1k).

**Quotation marks and logical punctuation (F09).** When a quoted term ends a clause, the full stop or comma is placed outside the quotation mark 39 times in 32 posts: `posts/post_21.txt:6:473` `"natural deflation".`; `posts/post_61.txt:6:342` `"nl".`; `posts/post_152.txt:6:49` `"Beta".`. The 7 cases with the stop inside (F09b) are all quotations of complete sentences or messages (`posts/post_31.txt:6:509` `…wallet file on another computer."`). This is a consistent "logical quotation" style; it is common among programmers and in British usage and is not by itself a nationality marker.

**Apostrophes.** All straight; 1,473 in-word apostrophes, almost all contractions or possessives. Apostrophe errors are rare: `lets` for "let's" twice (`posts/post_251.txt:6:552` `lets go`; `posts/post_311.txt:6:841` `lets say`); no `it's`/`its` or `your`/`you're` confusion found (0 of 33 `its`).

### 3.3 Spelling and word forms

**Spelling variants in three classes (F15, F16).** The first version counted every `-ize` form as American and reported "29 British vs 20 American tokens" from a hand-made list that missed sixteen `-ize` tokens. Revision 2 uses one classifier (`measures.spelling`) with three classes, because `-ize` is standard in American spelling and also in British Oxford spelling, so it is not evidence of American usage by itself. UI labels and switches (`Minimize to tray`, `-minimizetotray`), file and function names (`serialize.h`, `Reorganize`), menu paths (`Catalog->`) and text inside double quotes are removed before counting. Full token list with post ids: `data/agg/spelling_classes.csv`.

| Class | Tokens (posts) | Forms |
|---|---|---|
| Non-US (`-ise`/`-isation`/`-yse`, `-our`, `grey`, `defence`, `maths`, `labelled`, `fulfil`) | 27 (25) | optimisation 8, optimised 1, decentralised 2, colour 2, grey 2, analysed, amortised, formalised, liberalising, modernised, prioritising, reorganised, favour, neighbour, defence, labelled, labelling, fulfil, maths |
| US-only (`-or`, `gotten`) | 5 (3) | color 4, gotten 1 |
| `-ize` (American, or British Oxford style) | 28 (22) | serialize/serialization 6, realize/realized 5, optimized/optimization(s) 4, criticized 2, decentralized 2, minimized 2, standardized/standardizing 2, generalizes, summarize, recognize, initialize, internationalization |
| Preference, not spelling | | towards 9 vs toward 2; noun `license` 4 and `licenses` 1 (three in the name "MIT license"), where British spelling uses `licence` |

Examples: `posts/post_142.txt:6:46` `optimisation`; `posts/post_82.txt:6:143` `colour`; `posts/post_134.txt:6:418` `maths`; `posts/post_44.txt:6:671` `analysed`; versus `posts/post_34.txt:6:145` `realize`; `posts/post_129.txt:6:484` `color`; `posts/post_1.txt:6:86` `decentralized`.

Interpretation and competing explanations: the same stems are spelled both ways (`optimis-` 9 vs `optimiz-` 4; `decentralised` 2 vs `decentralized` 2), and the two `-our`/`-or` cases split (`colour` 2 in `post_82` and `post_427`, `color` 4 in `post_129` and `post_202`). `decentralized` (both 2009 P2P Foundation posts) becomes `decentralised` in 2010, but `realize/realized` run from 2010-01 to 2010-12 alongside `optimisation` (2010-06 to 2010-12). What the archive supports is that the writer did not apply one convention; non-US forms are the majority among the variants that discriminate (27 of 32 non-US or US-only tokens). Among contemporary writers who used a discriminating spelling at all, 24% have a non-US share of at least 0.75 (`CONTROL_CORPUS.md`). A spelling variant is not evidence of nationality; see the profile addendum, section 1.

**Misspellings and slips (F18).** With a dictionary check of all 4,234 types and manual review of every unknown word, the genuine errors are: `walkthough` (`posts/post_400.txt:6:32`), `idealogical` (`post_363`), `easer` for "easier" (`post_19`), `Allright` (`post_251`), `filewall` for "firewall" (`post_493`), `generateds` as a noun (`post_141`), `divy` (`post_516`, a variant of "divvy"), `moreso` (`post_401`), and `lets` for "let's" (2). `exisits` in `post_81` is quoting a compiler message. That is roughly 9 slips in 48,766 words, with no repeated misspelling. The lexicon is otherwise clean, including long technical words.

**Compounds, hyphenation and fixed forms (F19, F33).**

| Form | Count | Alternative | Count |
|---|---|---|---|
| block chain | 31 (23 posts) | blockchain | 0 |
| double-spend / double-spending | 23 | double spend | 0 |
| proof-of-work | 14 | proof of work | 1 |
| e-mail | 8 (7 posts) | email | 1 |
| a lot | 35 (29 posts) | alot | 0 |
| OK | 14 (13 posts) | okay / Ok | 0 |
| backup (noun/verb) | 17 | back up | 0 |
| website | 12 | web site | 0 |
| online | 8 | on-line | 0 |
| set up | 6 | setup (noun) | 6 |
| until | 46 | till / 'til | 0 |
| peer-to-peer | 2 | peer to peer | 0 |
| timestamp | 6 | time-stamp | 0 |

Hyphenated compounds occur 311 times (6.4 per 1k) in 170 posts. Among contemporary writers who wrote the word, 15% hyphenate "e-mail" as consistently, 30% "double-spend", 46% "proof-of-work", and 70% write "block chain" as two words, so the last was the forum's usual form in 2010 (`CONTROL_CORPUS.md`).

**Capitalisation.** `bitcoin` is lower case in 239 of 354 uses (68%), including sentence-medial references to the system; `Bitcoin` capitalised 115 times, concentrated at sentence starts and in release titles. `bitcoin address` lower case 47 vs `Bitcoin Address` 4. Acronyms are fully capitalised: `SVN` 81, `CPU` 44, `IRC` 40, `RPC` 38, `TOR` 24 (vs `Tor` 4, all in February 2010), `JSON-RPC` 34 (vs `json-rpc` 18, mostly as a command-line token), `BTC` 16. Lower-case identifiers are preserved at sentence start (F29): `posts/post_20.txt:6:524` `.\xa0 wxWidgets really pays off for cross platform.`; `posts/post_45.txt:6:542` `.\xa0 e.g. moving the decimal place 3 places would…`. 20 sentences in 20 posts begin this way; no identifier is ever capitalised to fit sentence rules.

**Abbreviations.** `e.g.` 4 (never followed by a comma), `etc.` 5 (always with a period), `vs` 7 (never with a period), `i.e.` 0, `BTW` 5, `AFAIK`/`afaik` 1, `OTOH` 1, `FWIW`/`IMO`/`IMHO` 0, `w/o` 1.

**Numbers (F31).** Percentages are written with the sign attached (94 cases, 0 "percent"): `posts/post_42.txt:6:3278` `28%`. Multipliers as `1.7x`, `4x` (7). Thousands separators are inconsistent: `1,464,800 bc` and `29,296 blocks` in 2009 but `50000 BTC`, `74000`, `115000` later (8 numbers with commas vs 58 five-digit numbers without).

### 3.4 Vocabulary

**Function words** (rate per 1k): the 52.9, to 35.8, it 25.2, a 23.7, is 15.1, and 14.4, you 14.1, of 14.0, that 13.0, in 11.5, I 11.5, be 11.4, if 11.2, for 10.7, would 6.6, it's 5.7, can 5.7, we 4.7 (document shares in `word_freq.csv`). Notable relative to ordinary English prose: `it` outranks `a`, `if` is as frequent as `for`, `would` is the most frequent modal, and `and` is low (14.4 per 1k) because clauses are separated by full stops rather than coordinated.

**Pronouns and modals** (`pronouns_modals.csv`): you/your 20.7 per 1k; I/me/my 15.7; they/them 6.8; we/our 6.3; he/his 0.7; she/her 0. Modals: would 6.6, can 5.7, could 3.4, should 2.8, will 2.7, may 1.1, might 0.8, must 0.8. The absolute `must` and the probabilistic `might`/`may` are rare; `would` and `could` frame most proposals.

**Recurring expressions** (`expressions.csv`, case-insensitive unless capitalised; count, posts): I think 54 (47); maybe 53 (45); probably 49 (43); a lot 35 (29); at least 34 (30); instead 36 (33); a few 28 (26); Thanks 25 (25); it would be 46 (39) with would be nice 14 (13); actually 21 (20); though 20 (20, 15 of them clause-final "…, though."); I'm not sure 17 (17); I guess 15 (14); the only 25 (23); kind of 12 (12); unless 13 (13); I don't think 11 (11); nobody 11 (9); I hope 12 (11); I assume 7 (7); ought to 7 (7); sort of 1; basically 3; definitely 10 (9); certainly 4 (4); clearly 3; surely 3; obviously 2 (2). The first version matched these adverbs in lower case only and so missed sentence-initial uses such as "Obviously" (`post_242`, `post_260`) and "Certainly" (`post_136`).

**Characteristic phrases from the n-gram tables** (`word_3grams.csv`, `word_4grams.csv`): "it would be" 46 (39 posts); "a lot of" 21; "be able to" 19; "the block chain" 18; "that would be" 17; "I'm not sure" 17; "would have to" 16; "a bitcoin address" 15; "initial block download" 15 (12 posts, always this three-word form); "if you have" 15; "I don't know" 14; "would be nice" 14; "in SVN rev" 14; "to make sure" 12; "do you think" 11 ("What do you think" 5); "I can't think of" 5; "let me know if" 5; "it would be very easy to" 4; "for a long time" 6; "an order of magnitude" 4.

**Sentence openers** (`sentence_openers.csv`, first word; count, posts): The 338 (221), I 313 (207), If 222 (152), It 208 (159), It's 119 (91), You 91 (75), This 74 (64), We 63 (59), In 53, When 46, There 45, That's 39, There's 38, I'm 36, Maybe 26, Thanks 25, Please 18, Here's 17, I'll 16. Two-word openers: "If you" 77 (68), "It would" 44 (39), "This is" 34, "I think" 32 (28), "I don't" 30 (30), "You can" 22, "If it" 20, "I uploaded" 14, "It looks" 11, "I guess" 11, "The only" 10, "There's no" 8, "For now" 7, "On Windows" 7. Post-initial words: I 62, The 33, It 23, That's 22, It's 15, Thanks 14, Right 8, Yes 7, No 5, OK 5, True 4, Sorry 4.

**Sentence enders** (last word): it 140, that 39, this 36, version 33, time 32, block 29, them 27, way 27, address 26, rev 26, yet 17, right 16, later 14, again 13. Sentences frequently end on the pronoun "it" (`…I'll look into it`, `…you don't need it`) and on "yet"/"later"/"again".

### 3.5 Syntax

**Sentence length.** 3,858 sentences with at least one word: mean 12.6 words, median 11, standard deviation 8.5, quartiles 6/11/17. Histogram (words): 1–4: 621; 5–9: 988; 10–14: 890; 15–19: 628; 20–24: 375; 25–29: 201; 30–39: 119; 40+: 36 (longest 95, a run-on list item). Sentence length rises with post length (8.7 words in posts under 50 words, 14.6 in posts over 300) and with topic (10.5 in build/compile threads, 13.2 protocol design, 14.5 economics). The short sentences are not fragments of a lazy writer but list items and one-clause verdicts (457 sentences of 1 to 3 words, 205 posts: "No.", "Nope.", "That works.", "Good idea.").

**Conditionals (F05, F26).** `if` occurs 546 times (11.2 per 1k) in 268 posts, nearly half the corpus. A sentence (as segmented by `textutil.sentences`) beginning "If" plus a second-person subject occurs 102 times in 81 posts: 77 with bare "you" (68 posts) and 25 with "you're", "you've", "you'd" or "you'll" (`measures.if_you_openers`). The first version gave 77 in the report and 99 in `finding_counts.json` because the two used different boundary rules and only one counted the contracted forms; both now report the canonical pair. Examples: `posts/post_7.txt:6:705` `If you were to locate the last link, then go off for an hour and forge your…`; `posts/post_40.txt:6:156` `If you didn't set up port forwarding, then incoming connections won't go to…`. Explanations are built as reader-addressed scenarios ("If you …, then …"; "Suppose …"; "Say …" 4 each) rather than abstract statements. Second-person instruction "you can / you need to / you should / you could" occurs 150 times in 116 posts (`posts/post_58.txt:6:761` `you could have two that connect out and the rest connect to…`).

**Hedged proposals (F04, F06).** "It would be …" 46 times (39 posts), typically "It would be nice/easy/possible/a good idea": `posts/post_63.txt:6:3` `It would be nice to have a list of static IPs…`; `posts/post_101.txt:6:482` `It would be a good idea to add a little code…`. Epistemic hedges: "I think" 54 (32 sentence-initial, 21 clause-medial, 1 sentence-final), "I'm not sure" 17, "I guess" 15, "I don't think" 11, "probably" 49, "maybe" 53, "I hope" 12, "I assume" 7, "I suspect" 4. Boosters are scarce but not absent: "definitely" 10, "certainly" 4, "clearly" 3, "surely" 3, "obviously" 2, "I'm sure" 1. With the hedge and booster lexicons in `measures.py`, hedges are 92% of stance markers (281 vs 26). About half of contemporary writers (46%) have a hedge share of at least 0.85, so the low-boost stance is typical of the forum rather than distinctive. Example `posts/post_247.txt:6:699` `I'm not sure is a net win`.

**Verdict-first replies (F07, F30).** A reply or paragraph frequently opens with a one-word judgement followed by a comma and the explanation: "Right," 7, "Yes," 8, "No," 10, "True," 4, "OK," 5, "Nope." 2, "Not really." 1 (37 in 35 posts). `posts/post_18.txt:6:3` `Right, the SVN has the almost-release-candidate 0.2 source, which…`; `posts/post_53.txt:6:3` `True, sending by IP through Tor trades one problem for another.`; `posts/post_71.txt:6:173` `No, each generated transaction uses a new, single-use address.`

**Passive voice (F36).** A regex over be-forms plus past participle finds 466 passives, 0.118 per sentence (44.5% of posts contain one). Passives cluster in design description ("is designed to", "must be trusted", "are included"), highest in economics (0.17 per sentence) and lowest in build threads (0.08). Active first person dominates the rest.

**Clause joining.** Low `and` rate (14.4 per 1k) and almost no semicolons; sentences start with "But" 13 times, "So" 12 times and "Also" 11 times; the formal connectives "However", "Therefore", "Thus", "Hence", "Moreover" and "Furthermore" total 5 occurrences in 48,766 words. Connectives are informal: "though" 20 (15 clause-final "…, though."), "unless" 13, "instead" 36, "otherwise" 7, "anyway" 13, "then" 134.

**Questions.** 217 interrogatives in 131 posts; 39 posts end on a question, typically a request for information ("What block number is…?", "Does it actually work after just that…?!") or a rhetorical check ("What do you think?" 5).

### 3.6 Explanatory habits

**Analogies (F22).** 28 analogy or comparison markers in 25 posts: `posts/post_1.txt` "In a nutshell, the network works like a distributed timestamp server"; `post_355` "Blinding, in a nutshell, is x = (x * large_random_int) mod m."; `post_389` "Maybe think of it as a reference coin that you measure other coins against"; `post_215` "To use an analogy, it's more like the step from 32-bit to 64-bit"; `post_427` "As a thought experiment, imagine there was a base metal as scarce as gold but…"; `post_237` "Think something like a credit card processor with a new job"; `post_99` "It would work just like a mailto: link". Analogies are drawn from computing (time-sharing systems, webmail, FAT drives, credit-card processors) and from physical commodities (gold, base metal, a coin's lineage).

**Worked examples.** "for example" 5, "for instance" 10, "e.g." 4, "suppose" 5, with concrete numbers: "(1008/2016) / (3.5/14) = 0.5/0.25 = 2.0" (`post_302`); "a single 9000 BTC bill… to get 1 BTC and 8999 BTC change" (`post_342`).

**Corrections and disagreement.** Disagreement is stated flatly and briefly, then explained: "That's not possible." (`post_43`), "No, not related at all." (`post_221`), "No, not at all." (`post_317`), "You were looking at the wrong code." (`post_285`), "Not really. I'll change it to 1000 next time." (`post_258`). Self-correction uses "Sorry, actually…" (`post_276`), "Correct me if I'm wrong (please, and I'll gladly eat crow)" (`post_271`), and explicit `Edit:` markers (4 posts). Mistakes are owned in the first person ("Sorry, I didn't test compile on linux", `posts/post_120.txt:6:3`).

**Politeness (F08).** "Thanks"/"thanks" in 25 posts, usually as a stand-alone closing ("Thanks!") or "Thanks for that survey!"; "Sorry" opens 9 posts; "please" 33 (Please 18, please 15), almost always attached to a test or upgrade request ("please test it!", "Please upgrade to 0.3.6 ASAP!"). Praise is terse: "Nice graph!", "Good idea.", "+1 to you for having such a long password that you found this bug."

**Humour and idiom.** Dry rather than jokey: 11 forum smileys in 537 posts, 0 "lol"/"haha", 1 "Heh"-type interjection (`Hurray!`, `Hmm,` and `Sigh...` once each; F28). Idioms are few but recur: "Sorry to be a wet blanket." (twice), "I'll gladly eat crow", "WikiLeaks has kicked the hornet's nest, and the swarm is headed towards us.", "bogged down", "get 0.2 out the door", "up to speed", "brute force", "an order of magnitude" (4), "slashdotted" (2).

**Commitments (F35).** Future first-person promises are a fixed move: "I'll look into it", "I'll post TOR instructions at that time", "I'll try -m64 and see what the problem is", "I'll add that next time I update SVN" (19 "I'll + verb" promises in 19 posts; "I'll" 36 total).

### 3.7 Technical versus conversational register

Posts were labelled by keyword density (`topic` column): protocol_design 192 posts (22,091 words), code_build 186 (12,547), general_conversational 136 (10,526), economics 23 (3,602). Pooled measures (`compare_topic.csv`):

| Measure | code_build | protocol_design | economics | conversational |
|---|---|---|---|---|
| Mean sentence length (words) | 10.6 | 13.2 | 14.5 | 12.6 |
| "the" per 1k | 45.8 | 58.2 | 61.4 | 47.3 |
| "I" per 1k | 18.3 | 7.7 | 5.6 | 13.7 |
| "you" per 1k | 12.8 | 14.9 | 11.7 | 15.0 |
| "would" per 1k | 2.6 | 7.7 | 10.3 | 7.9 |
| Double quotes per 1k | 17.6 | 4.5 | 12.8 | 9.1 |
| Colons per 1k | 12.6 | 4.7 | 7.2 | 3.8 |
| Exclamation per 1k | 1.67 | 0.59 | 0.83 | 0.67 |
| Passive per sentence | 0.08 | 0.14 | 0.17 | 0.12 |
| Contractions per 1k | 30.9 | 29.2 | 25.0 | 33.0 |
| Double-space share | 0.99 | 0.97 | 0.84 | 0.99 |

The double-space shares include the single-spaced P2P Foundation posts (`post_3` is in the economics group, `post_1` in protocol design), which lowers those two groups.

Technical build threads are first-person, short-sentenced, colon- and quote-heavy (UI strings, switches, file names). Protocol and economics explanations lengthen sentences, drop "I", raise "the" and "would", and use more passives. The features that do not move with topic are the ones listed as the fingerprint in section 7: double spacing, contraction rate (25 to 33 per 1k in every group), "if" conditionals (10 to 11.5 per 1k in every group), absence of semicolons and dashes, and list and quotation conventions.

Preferred technical terminology: "block chain" (never one word), "node(s)" 157, "proof-of-work", "double-spend(ing)", "bitcoin address" (not "public key" when speaking to users), "initial block download", "generate"/"generation" for what is now called mining (`mining`/`miner(s)` appear 23 times in 11 posts, none before August 2010, first about gold mining and then about GPU miners), "transaction fee", "the network", "SVN rev". The unit of account changes from `bc` (`posts/post_16.txt:6:731` `1,464,800 bc`, 2009-12; last use 2010-02-16) to `BTC` (`posts/post_101.txt:6:355` `50000 BTC`, first 2010-05-16; 15 uses to December). The baht sign `฿` does not appear in his prose (only in a quoted member's post).

---

## 4. Changes over time

Periods are defined on the archive timestamps (not file numbers; file numbers happen to be chronological for all but the 2014 post). Pooled, token-weighted rates from `measures.profile()` (`compare_period_canonical.csv`, variant "all posts"):

| Period | Posts | Words | Sentence len | Contractions /1k | Comma /1k | Colon /1k | "(" /1k | "?" /1k | "!" /1k | "the" /1k | "I" /1k | "you" /1k | "if" /1k | "will" /1k | "would" /1k | Double-space share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 2009-02 (P2P Foundation) | 3 | 868 | 17.7 | 12.7 | 49.5 | 3.5 | 1.2 | 0 | 0 | 73.7 | 4.6 | 2.3 | 3.5 | 0 | 3.5 | 0 (platform) |
| P2 2009-11..12 | 19 | 2,819 | 12.8 | 33.4 | 32.6 | 10.6 | 5.3 | 2.8 | 1.1 | 57.5 | 11.7 | 23.8 | 8.9 | 6.7 | 7.1 | 0.96 |
| P3 2010-01..06 | 133 | 13,542 | 13.5 | 28.3 | 38.6 | 5.0 | 3.6 | 3.8 | 0.4 | 56.0 | 13.6 | 19.9 | 10.7 | 3.0 | 7.2 | 0.99 |
| P4 2010-07..09 | 310 | 24,288 | 12.3 | 32.0 | 35.9 | 6.7 | 4.6 | 6.1 | 1.3 | 51.9 | 18.5 | 20.6 | 12.2 | 5.5 | 6.1 | 0.99 |
| P5 2010-10..12 | 72 | 7,249 | 12.0 | 28.3 | 36.4 | 8.7 | 5.7 | 4.6 | 0.6 | 46.1 | 12.7 | 22.2 | 10.8 | 4.6 | 7.5 | 1.00 |

"I" and "you" here are the pronoun groups (I/me/my and contractions; you/your and contractions); "will" includes `'ll` contractions. These differ from the bare-word rates in the first version's period table, which used a different function.

**Edited-post sensitivity.** The same table without the 25 posts edited more than 24 hours after posting, and without all 103 author-edited posts, is in `compare_period_canonical.csv`. Removing the late-edited posts (none fall in P2) changes no rate by more than 0.7 per 1k (colons in P5, 8.7 to 8.0) and no relative value by more than 27% (exclamation marks, which are rare: P3 0.44 to 0.32). Removing every edited post is a conservative check that drops 37% of the text in P2 and 49% in P5; it produces large swings in rare features of the small periods (P2 colons 10.6 to 3.4; P5 exclamation marks 0.55 to 0; P5 questions 4.6 to 6.5) and widens the P2–P5 ranges of the main measures (contractions 27–35 per 1k, "if" 10–12, "you" 20–28, sentence length 12.3–14.4, double-space share 0.98–1.00) without introducing a trend. The late-2009 values are the least stable because P2 has only 19 posts.

Observations, with the competing explanation tested first:

* **The 2009 P2P Foundation posts look different** (longer sentences, fewer contractions, very few "I"/"you", no questions, no double spacing). The first competing explanation is genre: `post_1` is a prepared announcement essay (518 words) addressed to no one in particular, not a reply, and it is the same text the author sent to the p2p-research list (`shared_passages.csv`, 6-word Jaccard 0.998). The platform collapsed spacing (1.4). The vocabulary and spelling are continuous with the later posts. The difference is register (essay versus forum reply) rather than a change of writer; the sample is 868 words.
* **From November 2009 onward the profile is flat.** Contraction rate stays between 28 and 34 per 1k, "if" between 9 and 12, "you" between 20 and 24, the double-space share at or above 0.95 in every month, mean sentence length between 12.0 and 13.5. Month-by-month figures (`compare_month.csv`) show no monotonic trend.
* **"I" rises in mid-2010 (18.5 per 1k)** when most posts are first-person release and bug-fix notes ("I uploaded…", "I'll…"); it falls again in P5. This tracks topic mix (code_build posts: "I" 18.3 per 1k), not a change of habit.
* **No shift from "will" to "would".** Within the forum, "will" runs 6.7, 3.0, 5.5, 4.6 per 1k across P2–P5 and "would" 7.1, 7.2, 6.1, 7.5, with no trend. The first version's validation report read a lower forum "will" rate than in the 2008–2009 e-mails as growing caution; that comparison confounds date with register (announcements and specifications use the future), and the 2008 e-mails already use "would" at the forum rate (6.3 per 1k). The claim is withdrawn (validation report).
* **Lexical shifts are terminological, not stylistic**: `bc` → `BTC` (2010-02 to 2010-05 gap); `TOR` (2009-11 to 2010-10) with a brief `Tor` in February 2010; `mining`/`miners` appear only from mid-2010 as GPU mining became a topic; "block chain" is two words in all periods.
* **Spelling** shows no drift: non-US `-isation` forms and `-ize` forms co-occur in the same months (3.3).
* **Topic vocabulary** (positive, negative, security, government/legal) is tabulated by period in `affect_by_period.csv` and discussed in the profile addendum (section 5), including its sensitivity to edited posts and to topic mix.

**Posting times.** Of 537 posts, 9 are stamped between 07:00 and 13:59 UTC and 1 between 07:00 and 11:59 (`post_522`, 09:08). The quietest band is 05:00–13:59 UTC, with 15 posts (2.8%). Hour counts, UTC 0–23: 32, 23, 15, 10, 9, 3, 3, 0, 0, 1, 0, 0, 3, 5, 14, 18, 46, 64, 62, 43, 42, 55, 47, 42. The first version stated that no post fell between 07:00 and 13:59; that was wrong. The forum's own stamps match the archive timestamps exactly for the 105 posts checked (section 1.6), so the hours are not shifted by the scrape. Posting hours are metadata rather than style and are reported as an observation of the archive only.

---

## 5. Anomalies and outliers

`anomalies_zscore.csv` ranks posts of 80+ words by root-mean-square z-score across 15 features. Every post in the top dozen has a mundane explanation:

| Post | Deviation | Explanation after inspection |
|---|---|---|
| `post_260` (2010-07-24) | double quotes 182 per 1k, commas 91 per 1k | The post reproduces JSON request/response examples inline (`{"method": "postMessage", …}`); the quotes belong to data, not prose |
| `post_288` (2010-07-29) | exclamation 23 per 1k, "you" 57 per 1k, "the" 0 | Emergency alert ("*** ALERT *** Upgrade to 0.3.6"): imperative short sentences addressed to all users |
| `post_1`, `post_2`, `post_3` (2009-02) | double-space share 0; low contractions | P2P Foundation platform collapsed spacing; essay register (section 4) |
| `post_370` (2010-08-15), `post_28` (2010-01-14) | double-space share 0 | Each has a single measurable boundary, single-spaced: a numbered recovery step in the overflow-bug alert (`4) It should start out with less than 74000 blocks. Let it…`) and one sentence in a short build reply. One boundary is too few to read as a habit |
| `post_228` (2010-07-17) | parentheses 50 per 1k | A list of rounding cases each annotated in parentheses |
| `post_229` (2010-07-17) | passive 1.1 per sentence, sentence length 22.9 | Formal explanation of change-address privacy; the regex counts "is sent… are spent… be returned" |
| `post_444` (2010-09-10) | question marks 59 per 1k | A diagnostic reply made of five questions to the user |
| `post_328` (2010-08-07, "Escrow") | double-space share 0.09 (1 double, 10 single), "the" 100 per 1k | The one genuine spacing exception: a 291-word proposal in ordinary prose, single-spaced almost throughout (`The buyer commits a payment to escrow. The seller receives…`). The first version described these as parenthetical lines, which was wrong. Competing explanations: composed in another editor or form that collapses double spaces and pasted in; typed differently on another device; or a lapse. The archive cannot separate these. Vocabulary and syntax are otherwise ordinary ("I'd like to", "Thoughts?", "Why on earth would the fraudster…") |
| `post_362`, `post_357` | "I" 50–63 per 1k, quotes | Short first-person build reports quoting compiler flags |
| `post_422` | "it" 98 per 1k | Six-sentence answer entirely about "it" (the wallet file) |

No post in the core corpus deviates in a way that survives the quotation, code, genre or platform explanation. The only post whose authorship this analysis cannot support from style is `post_543` ("I am not Dorian Nakamoto."): five words, three years later, no stylistic features to measure, excluded on those grounds and not because of any measured difference.

Posts with unusually low feature values were also checked. Seven BitcoinTalk posts contain a single-spaced boundary (18 in total): `post_328` (10, discussed above); `post_22` (3, all inside a pasted quotation of wxWidgets documentation that the forum did not mark as a quote, so it is not the author's spacing); `post_7`, `post_41`, `post_89` (1 each, alongside 5, 9 and 3 double-spaced boundaries); and `post_28` and `post_370` (1 each, with no double-spaced boundary).

---

## 6. Limitations

* **Comparison corpora are limited.** Revision 2 adds two: the other public Satoshi writing (white paper and e-mails; `VALIDATION_OTHER_CORPORA.md`), which tests stability across register, and 423,409 words by 442 other writers in the same BitcoinTalk threads (`CONTROL_CORPUS.md`), which tests how common each habit was. The control's thresholds were set near Satoshi's values after inspection, so its results describe prevalence, not discriminative power, and no probability of authorship is estimated anywhere in this analysis.
* **Short texts.** Median post is 69 words; 189 posts have fewer than 50. Per-post rates are noisy, so group comparisons use pooled token-weighted rates, and the anomaly screen is restricted to posts of 80+ words.
* **Edited posts.** 103 posts were edited by the author after posting, 25 of them more than a day later (1.6). The archive holds only the final text. Time-based tables are reported with and without these posts.
* **Platform effects.** Double spacing survives only because SMF (BitcoinTalk) stored it as `&nbsp;`; emoticons, P2P Foundation spacing and code line breaks are lost (1.4). Line and paragraph breaks come from the current source HTML, not from the 2018 scrape; the character-level content matches exactly for all 543 files, which makes silent re-editing by the source site unlikely but not impossible.
* **Heuristics.** Sentence segmentation, passive detection, topic labels and inline-code detection are regular-expression heuristics defined in `textutil.py`, `measures.py` and `01_extract.py`; counts that depend on them (sentence length, passive rate, topic groups) carry a few percent error. Word-boundary counts (spellings, expressions, punctuation marks) are exact for the stated patterns.
* **Quoted and pasted text.** 7,032 words of other members' text were removed using the forum's quote markup. Pasted text that the forum did not mark as a quote can remain in the author's prose; one such case was found by inspection (`post_22`, a paragraph of wxWidgets documentation) and others may exist.
* **Lexicons.** Hedge, booster and topic-vocabulary lists are short, fixed lists in `measures.py`; every match of the topic lists is written out for inspection (`affect_matches.csv`). Other lists would give other numbers.

---

## 7. Writing fingerprint (best-supported habits)

Measured on 537 posts and 48,766 words of the author's own forum prose, 2009-02 to 2010-12. "Across registers" refers to the white paper and e-mails (`VALIDATION_OTHER_CORPORA.md`); "among contemporaries" to the share of other writers in the same threads with the same habit (`CONTROL_CORPUS.md`).

| # | Habit | Across registers | Among contemporaries |
|---|---|---|---|
| 1 | **Two spaces after sentences** (98.8% of 1,498 BitcoinTalk boundaries; one long exception, `post_328`) | holds (paper 100%, e-mails 95%) | 27% of writers; common |
| 2 | **Short declarative sentences** (median 11 words, mean 12.6) | register-dependent (paper 23.5, e-mails 15.1) | 32nd percentile |
| 3 | **Almost no semicolons** (3 in prose), **no em or en dashes**, **rare exclamation marks** (0.9 per 1k), parentheses for asides | holds | common (56–79%) |
| 4 | **Contractions by default** (86% contracted where a choice existed), but never `would've`/`could've`/`it'd` | register-dependent (paper 0.26, e-mails 0.71) | 19% of writers ≥ 0.80 |
| 5 | **Reader-addressed conditionals**: `if` 11.2 per 1k; "If you…" opens 102 sentences (2.1 per 1k); `you` outnumbers `I` | register-dependent | "If you": 10% of writers (96th percentile); "if": 25% |
| 6 | **Hedged, low-boost stance** (281 hedges vs 26 boosters) | holds in direction | common (46%) |
| 7 | **Verdict-first replies** ("Right,", "Yes,", "No,", "True,", "OK,") | holds in replies (7 in the e-mails) | 39% |
| 8 | **Proposal frame "It would be …"** (46) and **commitments "I'll …"** (36) | register-dependent | "It would be": 29% |
| 9 | **Logical quotation** (39 outside vs 7 inside, the 7 being full sentences) | holds | common (64%) |
| 10 | **List conventions**: `1)` numbering, `- ` bullets, items without terminal punctuation | holds (paper's numbered steps use `1)`) | `1)`: common; `- `: 32% of 19 writers |
| 11 | **Fixed term forms**: "block chain", "double-spend", "proof-of-work", "e-mail", "a lot", "OK", "etc.", `%` | holds | "e-mail" 15%, "double-spend" 30%; the rest common |
| 12 | **Spelling without one convention**: non-US `-isation`/`-our`/`grey`/`maths` (27) beside `-ize` (28) and US-only `color`/`gotten` (5) | holds (same split in paper and e-mails) | non-US share ≥ 0.75: 24% |
| 13 | **Clean spelling** (about 9 slips in 48,766 words, none repeated) | not tested | not tested |
| 14 | **Explanation by scenario, analogy and worked numbers**, and anticipation of how a reasonable assumption fails (profile addendum, 6.1) | holds (e-mails, 2008) | not tested |

**Most useful for comparison** (frequent, measurable on short texts, and uncommon among contemporaries): the "If you…" opener rate and the `if` rate, the contraction share, the non-US spelling share, "e-mail" and "double-spend" hyphenation, `- ` bullets, and sentence spacing in combination with these. The first three are register-dependent and should be compared only with forum or e-mail replies.

**Not useful alone**: the absence of semicolons, dashes and exclamation marks, logical quotation, `%`, "OK", "block chain" and `1)` lists, which most contemporaries shared; passive rate and sentence length (topic- and register-driven); spelling variants as evidence of nationality; and any feature of the three 2009 P2P Foundation posts (platform-altered, 868 words).
