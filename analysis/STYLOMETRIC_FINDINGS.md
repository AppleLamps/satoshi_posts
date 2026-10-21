# Stylometric findings: the Satoshi Nakamoto post archive

Repository `applelamps/satoshi_posts`, commit `b442311`, 543 files under `posts/`.
All counts below are reproducible with the scripts in `analysis/scripts/` (see `analysis/README.md`). Every quoted example is listed in `analysis/evidence.csv` with its file, 1-based line and column, and `04_verify_evidence.py` confirms that all 346 quotations appear verbatim at those positions.

Notation: "per 1k" means occurrences per 1,000 word tokens of the author's own prose; "posts" means distinct posts containing the feature. Locations are written `posts/post_N.txt:line:col`. Non-breaking spaces in the files are shown as `\xa0`.

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
| Author's own prose after cleaning (core corpus) | 537 posts, 48,630 word tokens, 4,234 types, 3,933 sentences, 1,742 paragraphs, 291,164 characters |

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

Additional manual attribution rules (R8 to R12 in the script docstring): the four reposts; e-mail style `> ` quoted lines in `post_10` (X02); a pasted list of other members' benchmark results in `post_351` from `aceat64:` onward (X03); and 66 runs of code-looking lines inside prose (C++, shell commands, diffs) labelled `inline_code` and excluded from prose statistics (1,466 words of code in total, including 12 formal code blocks).

### 1.4 Features whose original form cannot be established from this archive

* **Sentence spacing in the P2P Foundation posts.** The three 2009 posts have 32 single-spaced and 0 double-spaced sentence boundaries, while BitcoinTalk posts are double-spaced 98.4% of the time (section 3.1). The source HTML of the P2P posts contains no non-breaking spaces at all, which is consistent with that platform collapsing whitespace. Whether the author typed one or two spaces there cannot be determined.
* **Emoticons.** The forum rendered text smileys as images; the scraper dropped them. The source HTML shows 11 (6 "Smiley", 3 "Wink", 1 "Huh", 1 "Undecided") in 11 posts (`post_20, 91, 126, 141, 184, 202, 309, 327, 372, 374, 417`). The exact characters the author typed are unknown. No literal text smiley survives in his prose.
* **Line breaks inside code blocks** (lost in both the archive and `get_text`).
* **Curly versus straight quotation marks.** All 1,466 apostrophes and 463 double quotes in his prose are straight; this is consistent with plain-text forum input and says little about the author's editor.
* **Capitalisation and punctuation of thread titles** (line 1) are forum metadata shared with other posters and were not analysed as the author's prose.

### 1.5 Duplicates and repeated material

`near_duplicates.csv` and `repeated_sentences.csv` list shared 6-word shingles and exact repeated sentences. All repeats are release boilerplate or deliberate repetition rather than copies of whole posts: SHA1 checksum lines repeated across `post_371/373/375`; the 0.3.13 release notes repeated in `post_465/471` (Jaccard 0.35); changelog bullets in `post_13/24`; sample account code in `post_497/535`; "Sorry to be a wet blanket." used twice (`post_166`, `post_214`). Ten quote headers quote Satoshi himself; those quotes are excluded like all others. No post is a duplicate of another, so no de-duplication beyond quote removal was needed.

---

## 2. Strongest findings (summary)

Each finding has a detailed entry in section 3 with counts, examples and competing explanations. Evidence strength: **strong** = hundreds of instances across most posts and periods; **moderate** = dozens of instances across many posts; **weak** = few instances or confounded.

| # | Finding | Measure | Strength |
|---|---|---|---|
| 1 | Two spaces after every sentence (BitcoinTalk) | 1,549 double vs 25 single; 448 of 534 posts | strong |
| 2 | Contractions dominate | 1,463 contractions, 30 per 1k; contracted form chosen 86% of the time where a full form was possible | strong |
| 3 | Conditional, reader-directed syntax: "if" 11.1 per 1k; "If you" opens 77 sentences; "you" 20.7 per 1k vs "I" 15.7 per 1k | 541 "if" in 268 posts | strong |
| 4 | Short, plain sentences: median 11 words, mean 12.6, few over 30 | 3,849 sentences | strong |
| 5 | Semicolons, em dashes and exclamation marks are almost absent | 3 prose semicolons; 0 em/en dashes; 44 exclamation marks | strong |
| 6 | Logical punctuation: full stop and comma outside closing quotation marks | 39 outside vs 7 inside (the 7 are full-sentence quotations) | moderate |
| 7 | Lists: numbered items written `1)` (41 items, 14 posts, never `1.`), bullets `- ` (140 items, 31 posts, never `*`) | 179 list lines | moderate |
| 8 | Mixed British and American spelling, with a British lean in -ise/-our words: `optimisation` 8 of 9, `colour`/`grey`/`favour`/`neighbour`/`defence`/`labelled`/`fulfil`/`maths`/`analysed`; but `realize(d)` 5, `color` 4, `criticized` 2, `decentralized` 2 | 29 British vs 20 American tokens | moderate |
| 9 | Hedged first-person stance: "I think" 54, "I'm not sure" 17, "probably" 48, "maybe" 53, "I guess" 15; near-zero "obviously" (0), "certainly" (3) | 54 posts contain a hedge | moderate |
| 10 | Verdict-first replies: posts and paragraphs open with "Right,", "Yes,", "No,", "True,", "OK," | 37 in 35 posts | moderate |
| 11 | Term formation fixed: "block chain" (31) never "blockchain" (0); "double-spend" hyphenated (23 vs 0 open); "proof-of-work" (13 vs 1); "e-mail" (8 vs 1); "a lot" (33) never "alot"; "OK" (14) never "okay" | | moderate |
| 12 | Currency unit switched from "bc" (Dec 2009–Feb 2010, 3 uses) to "BTC" (May–Dec 2010, 15 uses) | | moderate (small n) |
| 13 | Very few misspellings: `walkthough`, `idealogical`, `easer`, `Allright`, `filewall`, `generateds`, `divy`, `moreso`, `lets` for "let's" (2) | ~9 slips in 48,630 words | moderate |
| 14 | Politeness formulas and a few recurring idioms: "Thanks" 25 posts, "Sorry" opens 9 posts, "please test"; "wet blanket" (2), "eat crow", "hornet's nest", "in a nutshell" (2), "bogged down", "out the door", "up to speed" | | moderate |
| 15 | Case-preserving habit: identifiers keep their lower case at sentence start (`wxWidgets really pays off`, `getwork allows…`) | 20 sentences | moderate |

---

## 3. Detailed results

### 3.1 Spacing and formatting

**Double space after sentence-final punctuation (F01).** In BitcoinTalk prose, 1,549 sentence boundaries have two spaces and 25 have one (share 0.984; 448 of 534 posts have at least one). The forum stored the second space as `&nbsp;`, which is why the repository files contain `.\xa0 ` sequences. Examples: `posts/post_7.txt:6:486` `k.\xa0 O`; `posts/post_53.txt:6:285` `c.\xa0 A`; `posts/post_400.txt:6:41` `h.\xa0 Someone`. The share is above 0.93 in every month from 2009-11 to 2010-12 (`compare_month.csv`, column `double_space_share`). The 25 single-spaced boundaries are mostly inside parentheses, after URLs or in list-like lines, and all 12 posts containing one also contain double spacing. Competing explanation: none for BitcoinTalk, since nbsp cannot be produced by the platform without the user typing two spaces. The P2P Foundation posts are the exception discussed in 1.4 (F02: `posts/post_1.txt:6:67` `n. I`).

**Paragraphing.** 1,742 paragraphs, mean 2.26 sentences, median 2; 651 (37.4%) are one sentence long. Longer posts are built from many short paragraphs rather than long ones (distribution: 1 sentence 651, 2 sentences 532, 3 sentences 312, 4 sentences 129, 5+ sentences 118). This is measured on breaks recovered from the source HTML, not from the repository text.

**Lists (F10).** Numbered lists use `1)`, `2)` (41 items in 14 posts; `1.` style 0). Bullet lists use `- ` (140 items in 31 posts; `* ` 0). Examples: `posts/post_119.txt:6:3` `3) Nothing, if sending by bitcoin address`; `posts/post_3.txt:6:135` `- Whenever someone finds proof-of-work to generate a block, th…`. List items usually have no terminal punctuation (797 line-final units without `.!?`, 192 posts), which also lowers the measured sentence length.

**Release-note template (F27).** Announcements follow a fixed skeleton: `Version X is now available` (6 posts), a `Changes:` block of `- ` bullets, `Download:` plus URL, often SHA1 lines. "I uploaded … to SVN" appears 14 times (14 posts): `posts/post_38.txt:6:3` `I uploaded this fix to the SVN`. "SVN rev N" occurs 33 times in 32 posts; "rev" is never spelled out.

**Post-hoc edits (F25).** Four posts carry an explicit `Edit:` or `Update:` marker (`posts/post_310.txt:6:585`, `posts/post_246.txt:6:446`). Inline corrections are otherwise made in a new sentence ("Sorry, actually it's ECDSA", `post_276`).

### 3.2 Punctuation

Totals over the core corpus (`punctuation_syntax_totals.csv`):

| Mark | Count | Per 1k words | Posts | Note |
|---|---|---|---|---|
| Comma | 1,784 | 36.7 | 450 | moderate; 1 comma per 2.2 sentences |
| Colon | 327 | 6.7 | 160 | mainly introducing lists, URLs, code |
| Parentheses (open) | 216 | 4.4 | 142 | 58 stand-alone parenthetical sentences; `).` 25 vs `.)` 4 |
| Question mark | 240 | 4.9 | 139 | 216 interrogative sentences; 39 posts end on a question |
| Double quotes | 463 | 9.5 | 113 | 97 posts; used for UI strings, switches, terms being named |
| Exclamation mark | 44 | 0.91 | 36 | see below |
| Ellipsis | 17 | 0.35 | 16 | "That's amazing...", "Sigh...", `[params...]` |
| Double hyphen `--` | 10 | 0.21 | 3 | as a dash in only 2 prose contexts |
| Semicolon | 4 | 0.08 | 4 | 3 in prose, 1 inside a URL |
| Em dash / en dash | 0 | 0 | 0 | none in 48,630 words |
| Spaced hyphen as dash | 1 | | 1 | `(credit - debit)` in `post_225` |

**Semicolons (F11).** Three in prose: `posts/post_3.txt:6:1319` `…positive feedback loop; as users increase, the value…`; `posts/post_284.txt:6:161` `…SHA-256 didn't work correctly; it returned the same incorrec…`; `posts/post_421.txt:6:1243` `…easily available as a package; a lot of people were frustrat…`. Independent clauses are otherwise joined by a full stop or a comma plus "but"/"so"/"and".

**Dashes (F12).** No em or en dash anywhere. `--` is used as a gloss separator in a command list (`posts/post_106.txt:6:118` `getreceivedbyaddress -- amount received on…`) and twice as a sentence dash (`post_54` "-- fixed", `post_166`). Parentheses do the work a dash would do: `posts/post_18.txt:6:544` `(0.1.5 doesn't have -min so it would be an open window)`.

**Exclamation marks (F14).** 44 marks in 36 posts, 0.9 per 1k. They cluster in release announcements and thanks: `posts/post_63.txt:6:191` `IP address, post it here!`; `post_288` "Please upgrade to 0.3.6 ASAP!" (2 marks in an 87-word emergency alert, the highest rate in the corpus); `post_124` `(thanks you guys!)`. Technical explanations essentially never carry one (protocol_design topic: 0.59 per 1k).

**Quotation marks and logical punctuation (F09).** When a quoted term ends a clause, the full stop or comma is placed outside the quotation mark 39 times in 32 posts: `posts/post_21.txt:6:473` `"natural deflation".`; `posts/post_61.txt:6:342` `"nl".`; `posts/post_152.txt:6:49` `"Beta".`. The 7 cases with the stop inside (F09b) are all quotations of complete sentences or messages (`posts/post_31.txt:6:509` `…wallet file on another computer."`). This is a consistent "logical quotation" style; it is common among programmers and in British usage and is not by itself a nationality marker.

**Apostrophes.** All straight; 1,466 in-word apostrophes, almost all contractions or possessives. Apostrophe errors are rare: `lets` for "let's" twice (`posts/post_251.txt:6:552` `lets go`; `posts/post_311.txt:6:841` `lets say`); no `it's`/`its` or `your`/`you're` confusion found (0 of 33 `its`).

### 3.3 Spelling and word forms

**British versus American variants (F15, F16).** Only words with an opportunity for a variant are counted; words that are the same in both varieties, or ambiguous (`check`, `program`, `practice`, `license`), are excluded. Counts over the core corpus:

| British form (posts) | American form (posts) |
|---|---|
| optimisation 8 (8), optimised 1 (1) | optimization 1 (1), optimized 2 (2) |
| colour 2 (2) | color 4 (2) |
| grey 2 (2) | gray 0 |
| favour 1, neighbour 1, defence 1, labelled 1, labelling 1, fulfil 1, maths 1 | (no American counterpart used) |
| analysed 1, formalised 1, prioritising 1, amortised 1, reorganised 1, modernised 1, liberalising 1 | realize 3 (3), realized 2 (2), criticized 2 (2) |
| decentralised 2 (2) | decentralized 2 (2) |
| towards 9 (8) | toward 2 (2) |
| gotten 1 (1), as past participle, is the American form | |
| **total 29 tokens, 27 posts** | **20 tokens, 16 posts** |

Examples: `posts/post_142.txt:6:46` `optimisation`; `posts/post_82.txt:6:143` `colour`; `posts/post_134.txt:6:418` `maths`; `posts/post_44.txt:6:671` `analysed`; versus `posts/post_34.txt:6:145` `realize`; `posts/post_129.txt:6:484` `color`; `posts/post_1.txt:6:86` `decentralized`.

Interpretation and competing explanations: the mix is real within this archive, not a time split. `decentralized` (both 2009 P2P Foundation posts) becomes `decentralised` in 2010, but `realize/realized` (American) run from 2010-01 to 2010-12 alongside `optimisation` (2010-06 to 2010-12). `color` in `post_129` describes UI colours in a technical list where `colour` is used for the same thing in `post_82`. `minimize` (8) is almost entirely the name of the UI option "Minimize to tray" and was not counted. The sample is small (49 tokens) and a spelling variant is not evidence of nationality; what the archive supports is that the writer did not apply a single consistent convention and leaned British for `-isation`/`-our`/`grey`/`maths` while writing the common verbs `realize`/`criticize` the American way.

**Misspellings and slips (F18).** With a dictionary check of all 4,234 types and manual review of every unknown word, the genuine errors are: `walkthough` (`posts/post_400.txt:6:32`), `idealogical` (`post_363`), `easer` for "easier" (`post_19`), `Allright` (`post_251`), `filewall` for "firewall" (`post_493`), `generateds` as a noun (`post_141`), `divy` (`post_516`, a variant of "divvy"), `moreso` (`post_401`), and `lets` for "let's" (2). `exisits` in `post_81` is quoting a compiler message. That is roughly 9 slips in 48,630 words, with no repeated misspelling. The lexicon is otherwise clean, including long technical words.

**Compounds, hyphenation and fixed forms (F19, F33).**

| Form | Count | Alternative | Count |
|---|---|---|---|
| block chain | 31 (23 posts) | blockchain | 0 |
| double-spend / double-spending | 23 | double spend | 0 |
| proof-of-work | 13 | proof of work | 1 |
| e-mail | 8 (7 posts) | email | 1 |
| a lot | 33 (27 posts) | alot | 0 |
| OK | 14 (13 posts) | okay / Ok | 0 |
| backup (noun/verb) | 17 | back up | 0 |
| website | 12 | web site | 0 |
| online | 8 | on-line | 0 |
| set up | 6 | setup (noun) | 6 |
| until | 46 | till / 'til | 0 |
| peer-to-peer | 2 | peer to peer | 0 |
| timestamp | 6 | time-stamp | 0 |

Hyphenated compounds occur 310 times (6.4 per 1k) in 170 posts.

**Capitalisation.** `bitcoin` is lower case in 239 of 354 uses (68%), including sentence-medial references to the system; `Bitcoin` capitalised 115 times, concentrated at sentence starts and in release titles. `bitcoin address` lower case 47 vs `Bitcoin Address` 4. Acronyms are fully capitalised: `SVN` 81, `CPU` 44, `IRC` 40, `RPC` 38, `TOR` 24 (vs `Tor` 4, all in February 2010), `JSON-RPC` 34 (vs `json-rpc` 18, mostly as a command-line token), `BTC` 16. Lower-case identifiers are preserved at sentence start (F29): `posts/post_20.txt:6:524` `.\xa0 wxWidgets really pays off for cross platform.`; `posts/post_45.txt:6:542` `.\xa0 e.g. moving the decimal place 3 places would…`. 20 sentences in 20 posts begin this way; no identifier is ever capitalised to fit sentence rules.

**Abbreviations.** `e.g.` 4 (never followed by a comma), `etc.` 5 (always with a period), `vs` 7 (never with a period), `i.e.` 0, `BTW` 5, `AFAIK`/`afaik` 1, `OTOH` 1, `FWIW`/`IMO`/`IMHO` 0, `w/o` 1.

**Numbers (F31).** Percentages are written with the sign attached (94 cases, 0 "percent"): `posts/post_42.txt:6:3278` `28%`. Multipliers as `1.7x`, `4x` (7). Thousands separators are inconsistent: `1,464,800 bc` and `29,296 blocks` in 2009 but `50000 BTC`, `74000`, `115000` later (8 numbers with commas vs 58 five-digit numbers without).

### 3.4 Vocabulary

**Function words** (rate per 1k, share of posts): the 53.0 (87%), to 35.8 (81%), it 25.3 (76%), a 23.6 (68%), is 15.1 (62%), and 14.5 (58%), you 14.1 (53%), of 14.0 (57%), that 13.0 (60%), in 11.5 (56%), I 11.5 (52%), be 11.5 (49%), if 11.1 (50%), for 10.8 (53%), would 6.6 (33%), it's 5.7 (33%), can 5.8 (35%), we 4.7 (26%). Notable relative to ordinary English prose: `it` outranks `a`, `if` is as frequent as `for`, `would` is the most frequent modal, and `and` is low (14.5 per 1k) because clauses are separated by full stops rather than coordinated.

**Pronouns and modals** (`pronouns_modals.csv`): you/your 20.7 per 1k; I/me/my 15.7; they/them 6.8; we/our 6.3; he/his 0.7; she/her 0. Modals: would 6.6, can 5.8, could 3.4, should 2.8, will 2.7, may 1.1, might 0.8, must 0.8. The absolute `must` and the probabilistic `might`/`may` are rare; `would` and `could` frame most proposals.

**Recurring expressions** (`expressions.csv`; count, posts): I think 54 (47); maybe 53 (45); probably 48 (42); a lot 33 (27); at least 31 (27); instead 30 (28); a few 28 (26); Thanks 25 (25); it would be 46 (39) with would be nice 14 (13); actually 20 (19); though 20 (20, 15 of them clause-final "…, though."); I'm not sure 17 (17); I guess 15 (14); the only 25 (23); kind of 12 (12); unless 12 (12); I don't think 11 (11); nobody 11 (9); I hope 12 (11); I assume 7 (7); ought to 7 (7); sort of 1; basically 3; certainly 3; obviously 0; definitely 7.

**Characteristic phrases from the n-gram tables** (`word_3grams.csv`, `word_4grams.csv`): "it would be" 46 (39 posts); "a lot of" 21; "be able to" 19; "the block chain" 18; "that would be" 17; "I'm not sure" 17; "would have to" 16; "a bitcoin address" 15; "initial block download" 15 (12 posts, always this three-word form); "if you have" 15; "I don't know" 14; "would be nice" 14; "in SVN rev" 14; "to make sure" 12; "do you think" 11 ("What do you think" 5); "I can't think of" 5; "let me know if" 5; "it would be very easy to" 4; "for a long time" 6; "an order of magnitude" 4.

**Sentence openers** (`sentence_openers.csv`, first word; count, posts): The 338 (221), I 313 (207), If 222 (152), It 208 (159), It's 119 (91), You 91 (75), This 74 (64), We 63 (59), In 53, When 46, There 45, That's 39, There's 38, I'm 36, Maybe 26, Thanks 25, Please 18, Here's 17, I'll 16. Two-word openers: "If you" 77 (68), "It would" 44 (39), "This is" 34, "I think" 32 (28), "I don't" 30 (30), "You can" 22, "If it" 20, "I uploaded" 14, "It looks" 11, "I guess" 11, "The only" 10, "There's no" 8, "For now" 7, "On Windows" 7. Post-initial words: I 62, The 33, It 23, That's 22, It's 15, Thanks 14, Right 8, Yes 7, No 5, OK 5, True 4, Sorry 4.

**Sentence enders** (last word): it 140, that 39, this 36, version 33, time 32, block 29, them 27, way 27, address 26, rev 26, yet 17, right 16, later 14, again 13. Sentences frequently end on the pronoun "it" (`…I'll look into it`, `…you don't need it`) and on "yet"/"later"/"again".

### 3.5 Syntax

**Sentence length.** 3,849 non-empty sentences: mean 12.6 words, median 11, standard deviation 8.5, quartiles 6/11/17. Histogram (words): 0–4: 621; 5–9: 986; 10–14: 888; 15–19: 625; 20–24: 374; 25–29: 200; 30–39: 119; 40+: 36 (longest 95, a run-on list item). Sentence length rises with post length (8.7 words in posts under 50 words, 14.6 in posts over 300) and with topic (10.5 in build/compile threads, 13.2 protocol design, 14.5 economics). The short sentences are not fragments of a lazy writer but list items and one-clause verdicts (457 sentences of 1 to 3 words, 205 posts: "No.", "Nope.", "That works.", "Good idea.").

**Conditionals (F05, F26).** `if` occurs 541 times (11.1 per 1k) in 268 posts, nearly half the corpus. "If you" opens 77 sentences in 68 posts: `posts/post_7.txt:6:705` `If you were to locate the last link, then go off for an hour and forge your…`; `posts/post_40.txt:6:156` `If you didn't set up port forwarding, then incoming connections won't go to…`. Explanations are built as reader-addressed scenarios ("If you …, then …"; "Suppose …"; "Say …" 4 each) rather than abstract statements. Second-person instruction "you can / you need to / you should / you could" occurs 150 times in 116 posts (`posts/post_58.txt:6:761` `you could have two that connect out and the rest connect to…`).

**Hedged proposals (F04, F06).** "It would be …" 46 times (39 posts), typically "It would be nice/easy/possible/a good idea": `posts/post_63.txt:6:3` `It would be nice to have a list of static IPs…`; `posts/post_101.txt:6:482` `It would be a good idea to add a little code…`. Epistemic hedges: "I think" 54 (32 sentence-initial, 21 clause-medial, 1 sentence-final), "I'm not sure" 17, "I guess" 15, "I don't think" 11, "probably" 48, "maybe" 53, "I hope" 12, "I assume" 7, "I suspect" 4. Boosters are scarce: "obviously" 0, "clearly" 3, "certainly" 3, "definitely" 7, "I'm sure" 1. Example `posts/post_247.txt:6:699` `I'm not sure is a net win`.

**Verdict-first replies (F07, F30).** A reply or paragraph frequently opens with a one-word judgement followed by a comma and the explanation: "Right," 7, "Yes," 8, "No," 10, "True," 4, "OK," 5, "Nope." 2, "Not really." 1 (37 in 35 posts). `posts/post_18.txt:6:3` `Right, the SVN has the almost-release-candidate 0.2 source, which…`; `posts/post_53.txt:6:3` `True, sending by IP through Tor trades one problem for another.`; `posts/post_71.txt:6:173` `No, each generated transaction uses a new, single-use address.`

**Passive voice (F36).** A regex over be-forms plus past participle finds 466 passives, 0.118 per sentence (44.5% of posts contain one). Passives cluster in design description ("is designed to", "must be trusted", "are included"), highest in economics (0.17 per sentence) and lowest in build threads (0.08). Active first person dominates the rest.

**Clause joining.** Low `and` rate (14.5 per 1k) and almost no semicolons; sentences start with "But" 13 times, "So" 13 times and "Also" 11 times; the formal connectives "However", "Therefore", "Thus", "Hence", "Moreover" and "Furthermore" total 5 occurrences in 48,630 words. Connectives are informal: "though" 20 (15 clause-final "…, though."), "unless" 12, "instead" 30, "otherwise" 4, "anyway" 13, "then" 134.

**Questions.** 216 interrogatives in 131 posts; 39 posts end on a question, typically a request for information ("What block number is…?", "Does it actually work after just that…?!") or a rhetorical check ("What do you think?" 5).

### 3.6 Explanatory habits

**Analogies (F22).** 28 analogy or comparison markers in 25 posts: `posts/post_1.txt` "In a nutshell, the network works like a distributed timestamp server"; `post_355` "Blinding, in a nutshell, is x = (x * large_random_int) mod m."; `post_389` "Maybe think of it as a reference coin that you measure other coins against"; `post_215` "To use an analogy, it's more like the step from 32-bit to 64-bit"; `post_427` "As a thought experiment, imagine there was a base metal as scarce as gold but…"; `post_237` "Think something like a credit card processor with a new job"; `post_99` "It would work just like a mailto: link". Analogies are drawn from computing (time-sharing systems, webmail, FAT drives, credit-card processors) and from physical commodities (gold, base metal, a coin's lineage).

**Worked examples.** "For example" 2, "for instance" 4, "e.g." 4, "suppose" 5, with concrete numbers: "(1008/2016) / (3.5/14) = 0.5/0.25 = 2.0" (`post_302`); "a single 9000 BTC bill… to get 1 BTC and 8999 BTC change" (`post_342`).

**Corrections and disagreement.** Disagreement is stated flatly and briefly, then explained: "That's not possible." (`post_43`), "No, not related at all." (`post_221`), "No, not at all." (`post_317`), "You were looking at the wrong code." (`post_285`), "Not really. I'll change it to 1000 next time." (`post_258`). Self-correction uses "Sorry, actually…" (`post_276`), "Correct me if I'm wrong (please, and I'll gladly eat crow)" (`post_271`), and explicit `Edit:` markers (4 posts). Mistakes are owned in the first person ("Sorry, I didn't test compile on linux", `posts/post_120.txt:6:3`).

**Politeness (F08).** "Thanks"/"thanks" in 25 posts, usually as a stand-alone closing ("Thanks!") or "Thanks for that survey!"; "Sorry" opens 9 posts; "please" 33 (Please 18, please 15), almost always attached to a test or upgrade request ("please test it!", "Please upgrade to 0.3.6 ASAP!"). Praise is terse: "Nice graph!", "Good idea.", "+1 to you for having such a long password that you found this bug."

**Humour and idiom.** Dry rather than jokey: 11 forum smileys in 537 posts, 0 "lol"/"haha", 1 "Heh"-type interjection (`Hurray!`, `Hmm,` and `Sigh...` once each; F28). Idioms are few but recur: "Sorry to be a wet blanket." (twice), "I'll gladly eat crow", "WikiLeaks has kicked the hornet's nest, and the swarm is headed towards us.", "bogged down", "get 0.2 out the door", "up to speed", "brute force", "an order of magnitude" (4), "slashdotted" (2).

**Commitments (F35).** Future first-person promises are a fixed move: "I'll look into it", "I'll post TOR instructions at that time", "I'll try -m64 and see what the problem is", "I'll add that next time I update SVN" (19 "I'll + verb" promises in 19 posts; "I'll" 36 total).

### 3.7 Technical versus conversational register

Posts were labelled by keyword density (`topic` column): protocol_design 192 posts (22,091 words), code_build 187 (12,737), general_conversational 135 (10,200), economics 23 (3,602). Pooled measures (`compare_topic.csv`):

| Measure | code_build | protocol_design | economics | conversational |
|---|---|---|---|---|
| Mean sentence length (words) | 10.5 | 13.2 | 14.5 | 12.8 |
| "the" per 1k | 45.5 | 58.2 | 61.3 | 47.3 |
| "I" per 1k | 18.2 | 7.6 | 5.6 | 13.5 |
| "you" per 1k | 12.9 | 14.8 | 11.7 | 14.8 |
| "would" per 1k | 2.5 | 7.7 | 10.3 | 8.1 |
| Double quotes per 1k | 17.0 | 4.5 | 12.8 | 10.7 |
| Colons per 1k | 12.6 | 4.7 | 7.2 | 3.7 |
| Exclamation per 1k | 1.65 | 0.59 | 0.83 | 0.69 |
| Passive per sentence | 0.08 | 0.14 | 0.17 | 0.12 |
| Contractions per 1k | 30.8 | 29.2 | 25.0 | 32.9 |
| Double-space share | 0.98 | 0.97 | 0.83 | 0.98 |

Technical build threads are first-person, short-sentenced, colon- and quote-heavy (UI strings, switches, file names). Protocol and economics explanations lengthen sentences, drop "I", raise "the" and "would", and use more passives. The features that do not move with topic are the ones listed as the fingerprint in section 7: double spacing, contraction rate (25 to 33 per 1k in every group), "if" conditionals (10 to 11.5 per 1k in every group), absence of semicolons and dashes, and list and quotation conventions.

Preferred technical terminology: "block chain" (never one word), "node(s)" 157, "proof-of-work", "double-spend(ing)", "bitcoin address" (not "public key" when speaking to users), "initial block download", "generate"/"generation" for what is now called mining (`mining`/`miner(s)` appear 23 times in 11 posts, none before August 2010, first about gold mining and then about GPU miners), "transaction fee", "the network", "SVN rev". The unit of account changes from `bc` (`posts/post_16.txt:6:731` `1,464,800 bc`, 2009-12; last use 2010-02-16) to `BTC` (`posts/post_101.txt:6:355` `50000 BTC`, first 2010-05-16; 15 uses to December). The baht sign `฿` does not appear in his prose (only in a quoted member's post).

---

## 4. Changes over time

Periods are defined on the archive timestamps (not file numbers; file numbers happen to be chronological for all but the 2014 post). Pooled, token-weighted rates (`compare_period.csv`):

| Period | Posts | Words | Sentence len | Contractions /1k | Comma /1k | Colon /1k | "(" /1k | "?" /1k | "!" /1k | "the" /1k | "I" /1k | "you" /1k | "if" /1k | Double-space share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 2009-02 (P2P Foundation) | 3 | 868 | 17.7 | 12.7 | 49.5 | 3.5 | 1.2 | 0 | 0 | 73.7 | 3.5 | 2.3 | 3.5 | 0 (platform) |
| P2 2009-11..12 | 19 | 2,819 | 12.2 | 33.4 | 32.6 | 10.6 | 5.3 | 2.8 | 1.1 | 57.2 | 6.4 | 14.8 | 8.8 | 0.93 |
| P3 2010-01..06 | 133 | 13,542 | 13.1 | 28.3 | 38.6 | 5.0 | 3.6 | 3.8 | 0.4 | 56.0 | 10.3 | 14.0 | 10.7 | 0.99 |
| P4 2010-07..09 | 310 | 24,152 | 12.0 | 31.9 | 35.7 | 6.8 | 4.6 | 6.1 | 1.3 | 51.8 | 13.8 | 14.1 | 12.3 | 0.98 |
| P5 2010-10..12 | 72 | 7,249 | 11.9 | 28.3 | 36.4 | 8.7 | 5.7 | 4.6 | 0.6 | 45.8 | 9.1 | 15.0 | 11.0 | 1.00 |

Observations, with the competing explanation tested first:

* **The 2009 P2P Foundation posts look different** (longer sentences, 4x fewer contractions, very few "I"/"you", no questions, no double spacing). The first competing explanation is genre: `post_1` is a prepared announcement essay (518 words, 3.75 sentences per paragraph) addressed to no one in particular, not a reply, and the platform collapsed spacing (1.4). The vocabulary and spelling are continuous with the later posts (`decentralized` is the one divergence, see 3.3). The difference is best described as register (essay versus forum reply) rather than a change of writer; the sample is 868 words.
* **From November 2009 onward the profile is flat.** Contraction rate stays between 28 and 33 per 1k, "if" between 9 and 12, "you" between 14 and 15, the double-space share at or above 0.93 in every month with at least six posts, mean sentence length between 11.9 and 13.1. Month-by-month figures (`compare_month.csv`) show no monotonic trend in any of 22 features.
* **"I" rises in mid-2010 (13.8 per 1k)** when most posts are first-person release and bug-fix notes ("I uploaded…", "I'll…"); it falls again in P5 when posts return to design discussion. This tracks topic mix (code_build posts: "I" 18.2 per 1k), not a change of habit.
* **Lexical shifts are terminological, not stylistic**: `bc` → `BTC` (2010-02 to 2010-05 gap); `TOR` (2009-11 to 2010-10) with a brief `Tor` in February 2010; `mining`/`miners` appear only from mid-2010 as GPU mining became a topic; "block chain" is two words in all periods.
* **Spelling** shows no drift: British `-isation` forms and American `realize` co-occur in the same months (3.3).

Posting times are metadata rather than style, but they are consistent across the whole archive: of 537 posts, none is stamped between 07:00 and 13:59 UTC (hour counts, UTC 0–23: 32, 23, 15, 10, 9, 3, 3, 0, 0, 1, 0, 0, 3, 5, 14, 18, 46, 64, 62, 43, 42, 55, 47, 42). This is reported as an observation of the archive only.

---

## 5. Anomalies and outliers

`anomalies_zscore.csv` ranks posts of 80+ words by root-mean-square z-score across 15 features. Every post in the top dozen has a mundane explanation:

| Post | Deviation | Explanation after inspection |
|---|---|---|
| `post_260` (2010-07-24) | double quotes 182 per 1k, commas 91 per 1k | The post reproduces JSON request/response examples inline (`{"method": "postMessage", …}`); the quotes belong to data, not prose |
| `post_288` (2010-07-29) | exclamation 23 per 1k, "you" 57 per 1k, "the" 0 | Emergency alert ("*** ALERT *** Upgrade to 0.3.6"): imperative short sentences addressed to all users |
| `post_1`, `post_2`, `post_3` (2009-02) | double-space share 0; low contractions | P2P Foundation platform collapsed spacing; essay register (section 4) |
| `post_228` (2010-07-17) | parentheses 50 per 1k | A list of rounding cases each annotated in parentheses |
| `post_229` (2010-07-17) | passive 1.1 per sentence, sentence length 22.9 | Formal explanation of change-address privacy; the regex counts "is sent… are spent… be returned" |
| `post_444` (2010-09-10) | question marks 59 per 1k | A diagnostic reply made of five questions to the user |
| `post_328` (2010-08-07) | double-space share 0.09, TTR low | An escrow proposal written as a numbered scenario with many single-spaced parenthetical lines; otherwise ordinary vocabulary ("I'd like to", "Thoughts?") |
| `post_362`, `post_357` | "I" 50–63 per 1k, quotes | Short first-person build reports quoting compiler flags |
| `post_422` | "it" 98 per 1k | Six-sentence answer entirely about "it" (the wallet file) |

No post in the core corpus deviates in a way that survives the quotation, code, genre or platform explanation. The only post whose authorship this analysis cannot support from style is `post_543` ("I am not Dorian Nakamoto."): five words, three years later, no stylistic features to measure, excluded on those grounds and not because of any measured difference.

Posts with unusually low feature values were also checked: the 12 BitcoinTalk posts with a single-spaced sentence boundary (`single_space_after_sentence` > 0) all also contain double spacing, with the single spaces following URLs, closing parentheses or list fragments.

---

## 6. Limitations

* **No comparison corpus.** Every feature is described as characteristic within this archive. Without a matched set of contemporary forum writers, nothing here can be called distinctive or identifying, and no probability of authorship is estimated.
* **Short texts.** Median post is 69 words; 189 posts have fewer than 50. Per-post rates are noisy, so group comparisons use pooled token-weighted rates, and the anomaly screen is restricted to posts of 80+ words.
* **Platform effects.** Double spacing survives only because SMF (BitcoinTalk) stored it as `&nbsp;`; emoticons, P2P Foundation spacing and code line breaks are lost (1.4). Line and paragraph breaks come from the current source HTML, not from the 2018 scrape, and the two could differ if the source site re-edited posts (the character-level content matches exactly for all 543, which makes silent edits unlikely but not impossible).
* **Heuristics.** Sentence segmentation, passive detection, topic labels and inline-code detection are regular-expression heuristics defined in `textutil.py` and `02_features.py`; counts that depend on them (sentence length, passive rate, topic groups) carry a few percent error. Word-boundary counts (spellings, expressions, punctuation marks) are exact.
* **Quoted text.** 7,032 words of other members' text were removed using the source HTML. Satoshi's own pasted lists of other members' comments (`post_351`) and reposts were removed manually; any remaining short pasted phrases inside his sentences could not be detected automatically.
* **Scope.** The archive contains only BitcoinTalk and P2P Foundation posts (no e-mails or the white paper), so register comparisons are limited to forum writing.

---

## 7. Writing fingerprint (best-supported habits)

Measured in this archive of 537 posts and 48,630 words of the author's own forum prose, 2009-02 to 2010-12:

1. **Two spaces after every sentence** (98.4% of 1,574 boundaries on BitcoinTalk), stable in every month.
2. **Short declarative sentences** (median 11 words, mean 12.6), separated by full stops; **almost no semicolons** (3), **no em or en dashes** (0), **rare exclamation marks** (0.9 per 1k) and ellipses (0.35 per 1k); parentheses carry asides, often as stand-alone sentences.
3. **Contractions by default** (30 per 1k; 86% contracted where a choice existed: `it's`, `don't`, `doesn't`, `I'm`, `you're`, `it'll`, `there's`), but never `would've`/`could've`/`it'd` (0 against 32/6/45 full forms).
4. **Reader-addressed conditionals**: `if` 11 per 1k, "If you …" opening 77 sentences; `you` outnumbers `I` (20.7 vs 15.7 per 1k); `would` is the leading modal; `must`, `may`, `might` are rare.
5. **Hedged, low-boost stance**: "I think" (54), "maybe" (53), "probably" (48), "I'm not sure" (17), "I guess" (15); "obviously" 0, "certainly" 3.
6. **Verdict-first replies**: "Right,", "Yes,", "No,", "True,", "OK," then the reason; terse one-line answers ("No, not at all.", "That works.").
7. **Proposal frame "It would be nice/easy/possible/a good idea to …"** (46 instances) and **first-person commitments "I'll …"** (36).
8. **Logical quotation**: stop and comma outside the closing quote for quoted terms (39 vs 7 inside, the 7 being full sentences); straight quotes only.
9. **List conventions**: `1)` `2)` numbering (never `1.`), `- ` bullets (never `*`), items without terminal punctuation; release notes with `Changes:` / `Download:` headings and "SVN rev N".
10. **Fixed term forms**: "block chain" (two words, 31/0), "double-spend" and "proof-of-work" hyphenated, "e-mail", "a lot", "OK", "until" (never "till"), upper-case `TOR`, `SVN`, `IRC`, `CPU`; lower-case `bitcoin` in running text (68%); identifiers keep their case at sentence start.
11. **Mixed spelling with a British lean**: `optimisation` (8), `colour`, `grey`, `favour`, `neighbour`, `defence`, `labelled`, `fulfil`, `maths`, `analysed`, `towards` (9 vs 2 `toward`), alongside American `realize(d)` (5), `color` (4), `criticized` (2); `-ize` and `-ise` in the same months.
12. **Clean spelling** (about 9 slips in 48,630 words, none repeated), including `lets` for "let's" twice and `walkthough`, `idealogical`, `easer`, `Allright`, `filewall`.
13. **Explanation by analogy and worked numeric example** ("in a nutshell", "think of it as", "to use an analogy", "as a thought experiment"), with computing and commodity analogies; disagreement stated flatly then explained; apologies in first person ("Sorry, I …"); idioms "wet blanket", "eat crow", "hornet's nest", "out the door", "bogged down", "up to speed".

**Features most useful for a future authorship comparison** (because they are frequent, topic-independent and measurable on short texts): sentence spacing (where the platform preserves it); contraction rate and the specific never-contracted set (`would have`, `could have`, `it would`); `if`/"If you" rate; `you`:`I` ratio; `would` share of modals; semicolon, dash and exclamation rates; punctuation placement at closing quotes; `1)`/`- ` list style; "It would be …" and "I think …" frequencies; the two-word "block chain" and hyphenated "double-spend"; `-isation`/`-our` versus `realize`-type spelling split; `towards`:`toward`; `OK`; `e.g.` without comma, `vs` without period, `etc.` with period; `%` attached to the number. Features that should **not** be used alone: spelling variants as nationality evidence (mixed here), passive rate and sentence length (topic-driven), exclamation and question rates (genre-driven), and any feature of the three 2009 P2P Foundation posts (platform-altered, 868 words).
