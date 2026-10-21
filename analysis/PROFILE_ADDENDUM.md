# Profile addendum: deeper reading of the writer behind the archive

Companion to `STYLOMETRIC_FINDINGS.md`. Same corpus (537 posts, 48,630 words of the author's own forum prose, 2009-02 to 2010-12), same definitions. This document goes beyond style counts into dialect, knowledge, working environment, social behaviour and self-presentation. Each claim is tagged **[measured]** (a count anyone can reproduce with the scripts) or **[inferred]** (my reading of those counts). Nothing here identifies a person; it describes a writer.

---

## 1. Dialect: a writer with two Englishes

### 1.1 What points away from the United States [measured]

| Marker | Evidence |
|---|---|
| Day-first dates | `30 Dec 2009`, `04 Feb` (`post_42`, 2010-02-05); `28 January 2010` (`post_54`); `29/09/2010 16:41` (`post_481`); a hand-typed difficulty table in `post_42`/`57`/`77`/`280` entirely in `dd/mm/yyyy`. No month-first date anywhere in his prose. |
| `flats` for apartments | "Many small flats have electric heat out of convenience." (`post_363`, 2010-08-15) |
| `maths` | "cranking away at maths" (`post_134`) |
| `bloody` as intensifier | "is bloody hard" (`post_166`) |
| `have got` | "You could have got a lot more money" (`post_68`); "we've got", "you've got" (3) |
| `-our`, `-ise`, `grey`, `defence`, `fulfil`, `labelled`, `towards` | 29 British tokens vs 20 American (see main report 3.3); `optimisation` 8 of 9 |
| Full stop outside closing quotes | 39 vs 7 |
| `in future` (bare) | once (`post_532`); `in the future` 12 |

### 1.2 What points toward North America [measured]

| Marker | Evidence |
|---|---|
| `baseboard electric heating` | `post_363`, in the same sentence as "flats". "Baseboard heater" is a North American term; a British writer would say storage heater or electric radiator. |
| `heating oil` priced against electricity | `post_363`; oil heat is common in the north-eastern US and Canada, uncommon as a household reference point in the UK. |
| `gotten` | "would have gotten into both forks" (`post_404`) |
| `a couple little corrections` (no "of") | `post_299` |
| Bare adverb `likely` | "it would likely take a week" (`post_3`), "would likely destroy us" (`post_522`) |
| `realize(d)`, `color`, `criticized` | 9 tokens |
| `fall back` (verb) is neutral; `fall` for autumn never occurs | |
| `%appdata%`, `c:\program files\bitcoin` | Windows paths in US-locale style, but these are OS conventions, not dialect |

### 1.3 Reading [inferred]

The two lists are not noise: each contains items that are hard to produce by accident (`flats`, `maths`, `bloody`, day-first dates on one side; `baseboard`, `gotten`, bare `likely`, `a couple little` on the other). The simplest single explanation is a writer raised or schooled in a Commonwealth spelling tradition who has lived or worked for a long time in North America, or the reverse. Canada fits both lists without strain (Commonwealth spelling and day-first dates coexist with baseboard heaters, heating oil and `gotten`), but so does a Briton or Australian long resident in the US, or an American who worked abroad. Deliberate mixing cannot be excluded, though the pattern is too consistent across 14 months for casual obfuscation: the British items cluster in low-attention words (`maths`, `flats`, `bloody`, dates) and the American items in equally low-attention grammar (`gotten`, `likely`). A deliberate disguiser usually gets the spellings right and the grammar wrong; here both are mixed. I would not go further than "two Englishes, long exposure to both".

Native speaker: yes, with high confidence [inferred from measured absence]. No article errors, no preposition interference, idiomatic phrasal verbs ("get bogged down", "scrape up", "out the door", "sort it out"), 86% contraction rate, and no recurring pattern of any second-language type across 48,630 words.

Not continental European by writing convention [measured]: thousands separators are commas (`1,464,800`), decimals are points, there is no `1.000.000` or `0,5`, and no spacing before `?`/`!` or `%`.

---

## 2. Age cohort [inferred from measured]

* Two-space sentence spacing on 98.4% of 1,574 boundaries, with zero drift. This habit is learned on typewriters or in typing classes before the mid-1990s and is very rare in people who learned to write on word processors.
* Frames the present against history he treats as lived: "A generation ago, multi-user time-sharing computer systems had a similar problem" (`post_1`); "all the companies that failed since the 1990's" (`post_2`); "When I wrote it more than 2 years ago, there were screaming hot SHA1 implementations" (`post_242`); "transaction types that I designed years ago" (`post_125`); MSVC6 compatibility "at that time" (`post_264`). Knows Fortran as a cautionary example (`post_273`: "the Fortran scenario").
* References the Hunt brothers' 1979 silver corner (`post_173`) and Chaumian e-cash (`post_2`) as familiar history, and Wei Dai's 1998 b-money and Szabo's 2005 bit gold as lineage (`post_248`).
* Apostrophe in decades: `1990's` (once; no bare `1990s`). This is an older convention.
* No youth markers at all: 0 "lol", 0 "haha", 0 text smileys, 0 "awesome", 0 "epic", 0 "dude"; the one laugh is "Heh"-free and the sole celebratory word is "Hurray!" (`post_112`).

Reading: an adult who learned to type and to program before about 1995; the time-sharing comparison and MSVC6 habits suggest professional programming experience reaching back to the 1990s at least. I would put the writer's birth year before roughly 1975 and would not try to be narrower.

---

## 3. Professional profile [measured, with inference marked]

**Platform of origin: Windows, C++ [measured].** His own machine and build are Windows: `%appdata%\Bitcoin` paths (6 posts), `c:\program files\bitcoin`, MinGW/MSVC build talk, "I had full wxWidgets on my computer" fixing a Windows link order (`post_81`). Linux ports were done by others (Martti, `post_12`), Mac builds by Laszlo (`post_471`), and he says "I don't have an i5 or AMD" (`post_365/366`) and asks others to test on them. He builds on Ubuntu only to make a Linux release and worries he did it wrong (`post_144`). Linux paths appear as `~/.bitcoin` and `/usr/share/locale` correctly, so he is competent but not native there.

**Depth: systems programmer with cryptography literacy, not an academic cryptographer [inferred].** 123 cryptographic terms in 46 posts (ECDSA, secp256k1, RIPEMD-160, Merkle tree, blinding, zero-knowledge proofs, preimage, hash collisions). He explains blinding as "x = (x * large_random_int) mod m" (`post_355`), knows the 160-bit birthday bound (`post_215`), chooses ECDSA for signature size (`post_32`). But he hedges on crypto details more than on code: "Correct me if I'm wrong (please, and I'll gladly eat crow)" when discussing RIPEMD-160(SHA-256(x)) strength (`post_271`), "Sorry, actually it's ECDSA" (`post_276`), "I'm not sure" about the exact HTTP status in JSON-RPC (`post_260`). His confidence is highest on networking, threading, Berkeley DB, serialization and Win32 priorities (`post_89` includes a full nice-to-Win32 priority table), which is the profile of a long-time applications and systems developer who read the cryptography literature carefully rather than produced it.

**Engineering values [measured phrases].** "dead simple and flat as possible" (`post_307`), "something simple and safe" (`post_388`), "kludge", "hack", "clunky", "quirky", "cruft"-type words; "the code is completely 32-bit"; keeps old-compiler compatibility until forced; distrusts GPL ("If you GPL stuff, I have to avoid using it", `post_75`); releases into the public domain "(copyright-free)" (`post_74`). Backward compatibility is a recurring worry (14 posts mention "compatib").

**Economics: self-taught, Austrian-flavoured, applied [measured and inferred].** 31 economics terms in 16 posts, all at the level of an informed reader rather than a trained economist: seigniorage, fiat, scarcity, cornering the market, marginal cost, Moore's Law as a cost driver, "the price of any commodity tends to gravitate toward the production cost" (`post_64`), "natural deflation" (`post_21`), thought experiment of a base metal "as scarce as gold but ... boring grey in colour" (`post_427`). No "velocity", "liquidity", "Gresham", "store of value" or "medium of exchange": he reasons in production-cost and supply terms, not in monetary-economics vocabulary. The Hunt brothers passage is quoted from Wikipedia with its footnote numbers still attached (`post_173`), which shows where he reads.

**Reading sources [measured].** Links are to Wikipedia (3), wxWidgets docs, Oracle/Berkeley DB docs, MinGW, a JSON-RPC spec, Wei Dai's site, Szabo's blog. He says "I read that the record companies would like to DoS all the file sharing networks" (`post_317`) and mentions Slashdot coverage twice. No references to books, academic venues, or newspapers by name.

---

## 4. Working pattern and circumstances [measured]

* **Hours.** 537 posts, none stamped 07:00–13:59 UTC; the bulk falls 16:00–02:00 UTC (hourly counts in the main report, section 4). The curve has one peak (17:00–18:00 UTC) and a long tail to 02:00. It is consistent with afternoon-to-late-night posting in the Americas, or evening-to-small-hours posting in the UK/Western Europe. It is not consistent with a daytime poster in East Asia unless they kept night hours.
* **Days.** Thu 102, Fri 92, Sun 90, Wed 82, Mon 64, Sat 58, Tue 49. Weekend share 27.6% versus 28.6% expected if days did not matter. No weekday-job signature in the day-of-week distribution.
* **Load.** "Sorry, I've been so busy lately I've been skimming messages" (`post_424`, 2010-08-27); "I don't have time to try to convince you, sorry" (`post_286`); "haven't had time to" (4 posts). Posting volume peaked July–August 2010 (272 posts) and fell to 22 a month by November–December.
* **Personal life leakage: essentially none.** Across 48,630 words there is no "my wife", "kids", "weekend", "tonight", "this morning", "at work", "my job", "I live", "here in", or any place name attached to himself. The only first-person possessions are "my computer" (once, about wxWidgets) and "a program I use to find all the spacing inconsistencies" in translations (`post_195`). The heating-cost passage is about other people ("kids putting it on their parent's power bill, employees their employer"). This absence is itself measurable: in a sample of forum writers of comparable volume one expects dozens of such incidental references. The writer is disciplined about it, or writes only when in a narrowly technical frame of mind, or both.

---

## 5. Social behaviour and self-presentation

**Leader who does not say "my" [measured].** Zero instances of "my code", "my design", "my implementation", "my idea", "my plan". The system is "the design", "the network", "the software" (93 mentions in 68 posts). First-person creative claims are rare and factual: "I designed years ago" (1), "When I wrote it" (1), "I implemented this change in SVN rev 157" (1), "I built" (4, about builds). Yet he makes decisions unilaterally and announces them: "OK, back to 0.3 then." (`post_163`), "I renamed your thread" (`post_242`), "We don't support MSVC6 anymore" (`post_264`), "I'm leaving the -limitfreerelay part as a switch for now" (`post_542`).

**"We" is the project, not a company [measured].** "we" runs at 6 to 7 per 1k in 2010 and refers to the developer group and users together: "we need the small size of ECDSA", "we've never heard of that before now", "we haven't found any new bugs for a long time". It never refers to an employer or an organisation outside Bitcoin.

**Credits others by name, briefly [measured].** 19 posts mention Gavin (from 2010-07, rising to 1.1 per 1k in Q4 as hand-over proceeds), "thanks to tcatm", "thanks to Martti Malmi (sirius-m) for all his coding work", "Thanks Laszlo for the Mac OSX build", "Gavin Andresen:" as a changelog heading. "+1" is used 19 times in 9 posts as approval. Praise is short ("Nice graph!", "Good idea.", "That's a good optimisation."); 14 "good/nice/great + idea/point/catch/question" in 13 posts.

**Handles disagreement by stating the fact [measured].** "That's not possible." (`post_43`), "No, not at all." (`post_317`), "You were looking at the wrong code." (`post_285`), "Not really." (`post_258`). The sharpest sentence in the corpus is "If you don't believe me or don't get it, I don't have time to try to convince you, sorry." (`post_286`, 2010-07-29). He never writes "I was wrong" or "I'm wrong" as a statement (0), but corrects himself with "Sorry, actually…" and "Edit:", and pre-empts with "Correct me if I'm wrong".

**Affect over time [measured, per 1k words].** Positive-affect words fall from 5.0 (late 2009) to 3.7, 3.1, 2.5 across 2010; negative-affect words are near zero in 2009, rise to ~1 in mid-2010 (the bug-fix and DoS period) and fall to 0.1 in Q4. Security/attack vocabulary rises from 0.1 (H1 2010) to 2.1–2.6 (H2 2010). Government/legal/anonymity vocabulary is concentrated in the 2009 posts (3.5 and 1.8 per 1k) and almost vanishes in 2010 (0.3–0.4), with the one late exception being the WikiLeaks warning: "WikiLeaks has kicked the hornet's nest, and the swarm is headed towards us." (`post_541`, 2010-12-11). Reading: the writer's public persona narrowed over 2010 from advocate-designer to maintainer, and the political register he opened with was deliberately put away.

**Humour [measured].** Dry, rare, self-deprecating or deadpan: "I'll gladly eat crow", "Sorry to be a wet blanket" (twice), "+1 to you for having such a long password that you found this bug", "yes Windows, see I'm in a DLL like you insisted", "Writing a description for this thing for general audiences is bloody hard. There's nothing to relate it to." No jokes at others' expense.

---

## 6. Cognitive style [inferred from measured]

* **Conditional and scenario-based.** `if` at 11 per 1k and "If you…" opening 77 sentences; worked examples with numbers; "Suppose", "As a thought experiment", "Think of it as". He reasons forward from a concrete case to a rule.
* **Quantifies by default.** 1,736 numerals in 48,630 words (36 per 1k); percentages always as `%`; multipliers as `1.7x`; estimates with orders of magnitude ("an order of magnitude", 4). He converts qualitative questions into rates: "2 seconds of latency in both directions should reduce your generation success by less than 1%."
* **Low certainty display, high decisiveness.** Hedges in every 10th sentence, boosters almost never, yet decisions are announced flatly. The hedges attach to predictions and to other people's domains; the flat statements attach to his own code.
* **Economy of words.** Median post 69 words, median sentence 11, 37% of paragraphs a single sentence, no filler openers ("Well," once; "Basically" 3; "Actually," 1 as opener). He answers the question asked and stops, often on a one-line commitment ("I'll look into it").

---

## 7. What the deeper pass does not support

* Any specific nationality. The dialect evidence is genuinely split (section 1); the honest statement is "Commonwealth spelling habits plus North American living vocabulary".
* Any specific profession beyond "experienced Windows/C++ systems programmer with cryptography reading". There is no vocabulary of academia (no "paper" in the academic sense except his own design paper, no "we show", no citations), of finance employment (no trading-desk terms), or of large-company engineering (no "sprint", "ticket", "QA", "manager").
* Multiple authors. Every feature examined here, from date format to hedging rate to the two-space habit, is uniform across the 14 months; the only structural change is a shift of register from advocate to maintainer.
* The 2014 post. Five words; nothing to profile.
