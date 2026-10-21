# Profile addendum: what the writing does and does not tell us about the writer

Companion to `STYLOMETRIC_FINDINGS.md`. Same corpus (537 posts of the author's own forum prose, 2009-02 to 2010-12), same definitions, and the same shared measurement code (`scripts/measures.py`). Each statement is tagged:

* **[measured]**: a count anyone can reproduce with the scripts;
* **[hypothesis]**: a reading of those counts, stated with the competing explanations and with the evidence that would tell them apart.

Nothing here identifies a person. Revision 2 of this document removes several earlier conclusions that went further than the evidence: an estimated birth year, native-speaker status, a ruling-out of European upbringing, statements about education, a "distrusts GPL" characterisation, a claim that the posting-hour record has a complete gap, and an affect trend that was not reproducible from committed code. `REVISION_NOTES.md` lists each change.

---

## 1. Dialect: two sets of habits

### 1.1 Forms not used in standard American English [measured]

| Marker | Evidence |
|---|---|
| Day-first dates | `30 Dec 2009`, `04 Feb` (`post_42`); `28 January 2010` (`post_54`); `29/09/2010 16:41` (`post_481`); a difficulty table in `dd/mm/yyyy` (`post_42`). No month-first date in his prose. |
| `flats` for apartments | "Many small flats have electric heat out of convenience." (`post_363`) |
| `maths` | "cranking away at maths" (`post_134`) |
| `bloody` as intensifier | "is bloody hard" (`post_166`) |
| Non-US spellings | 27 tokens in 25 posts: `-isation`/`-ise`/`-yse` (`optimisation` 8, `decentralised` 2, `analysed`, `formalised`, `amortised`, `modernised`, `reorganised`, `liberalising`, `prioritising`), `-our` (`colour` 2, `favour`, `neighbour`), `grey` 2, `defence`, `labelled`, `labelling`, `fulfil`, `maths` (`data/agg/spelling_classes.csv`) |
| `in future` (bare) | once (`post_532`); `in the future` 12 |

### 1.2 Forms not used in standard British English [measured]

| Marker | Evidence |
|---|---|
| `color` | 4 tokens in 2 posts (`post_129`, `post_202`) |
| `gotten` | "would have gotten into both forks" (`post_404`) |
| `baseboard electric heating`, heating oil priced against electricity | `post_363` (North American household vocabulary) |
| `a couple little corrections` | `post_299` |
| `license` as a noun | "GPL is a good license for operating systems" (`post_450`); British spelling would be `licence` |

### 1.3 Forms valid in both [measured]

`-ize` spellings (28 tokens in 22 posts: `realize`/`realized` 5, `optimized`/`optimization(s)` 4, `serialize`/`serialization` 6, `criticized` 2, `decentralized` 2, `minimized` 2, `standardized`/`standardizing` 2, `generalizes`, `summarize`, `recognize`, `initialize`, `internationalization`) are standard American spelling and also standard British spelling in the Oxford style. The previous version counted them as American and reported "29 British vs 20 American tokens"; that count also missed sixteen `-ize` tokens. The same stem appears both ways (`optimisation` 9 vs `optimiz-` 4; `decentralised` 2 vs `decentralized` 2), so the writer did not follow one convention for this suffix.

### 1.4 Reading [hypothesis]

The two lists each contain items that are hard to produce by accident (`flats`, `maths`, `bloody`, day-first dates on one side; `baseboard`, `gotten`, `color` on the other). Competing explanations:

1. A writer schooled in a Commonwealth spelling tradition who has lived or worked for a long time in North America (Canada fits both lists without strain).
2. A North American who spent formative or working years in Britain or a Commonwealth country.
3. A writer with long exposure to both through work, reading or software localisation, without residence in either.
4. Deliberate mixing to obscure origin.

What the archive can and cannot do: the mix is present from the first month of the record (validation report) and runs through low-attention words on both sides, which makes explanation 4 harder to sustain but does not exclude it. The archive offers no way to choose between 1, 2 and 3. Evidence that would discriminate: dated autobiographical references (there are none), place-specific institutional vocabulary (school, tax, health system; none found), or the same habits measured in a control group of known Canadian, British and American developers writing in the same period (not attempted here).

### 1.5 Language background [hypothesis]

**What is measured:** no article or preposition errors were found in a manual pass, phrasal verbs are idiomatic ("get bogged down", "scrape up", "out the door", "sort it out"), the contracted form is chosen 86% of the time where a choice exists, and the dictionary check finds about nine slips in 48,766 words, none repeated (main report 3.3).

**What it supports:** a highly proficient, idiomatic writer of English.

**What it does not settle:** whether English is the writer's first language. Very proficient second-language writers who have lived in an English-speaking environment for years can produce text with these properties, especially in a narrow technical register, and careful writing can suppress transfer errors. The earlier "native speaker: yes, with high confidence" is withdrawn. Evidence that could discriminate: comparison with matched first- and second-language writers of the same proficiency on the same forum, or spontaneous spoken-style text; neither is available here.

**Number formatting:** thousands separators are commas (`1,464,800`), decimals are points, there is no `1.000.000` or `0,5`, and no space before `?`, `!` or `%` [measured]. These are the conventions of English-language technical text, and many writers from continental Europe and elsewhere adopt them when writing English. They do not exclude a European upbringing; the earlier statement that they did is withdrawn.

---

## 2. Era indicators [measured, with hypotheses]

**Two spaces after sentences** (98.8% of 1,498 BitcoinTalk boundaries; 100% in the white paper; 95% in the e-mails). The earlier version treated this as evidence of typewriter-era training and estimated a birth year before about 1975. The control corpus shows why that is too strong: among the 120 other BitcoinTalk writers of 2009–2010 in the same threads with enough text to measure, 32 (27%) also double-space at least 90% of the time (`CONTROL_CORPUS.md`). Competing explanations for the habit: typing instruction before the mid-1990s; learning from a teacher, employer or style guide that kept the convention; plain-text e-mail and monospaced-editor culture (Emacs, for example, treats a double space as the sentence boundary by default); and deliberate choice. The habit is consistent with an older writer but common enough among contemporary developers that it cannot date one.

**Historical references** [measured]: "A generation ago, multi-user time-sharing computer systems had a similar problem" (`post_1`); "all the companies that failed since the 1990's" (`post_2`); "When I wrote it more than 2 years ago" (`post_242`); MSVC6 compatibility; "the Fortran scenario" (`post_273`); the Hunt brothers' silver corner (`post_173`, quoted from Wikipedia with footnote numbers attached). These show familiarity with computing and financial history; they do not show that the writer lived through it. The decade apostrophe `1990's` (once) is an older or informal convention and is weak evidence at n = 1.

**Absent youth-forum markers** [measured]: 0 "lol", 0 "haha", 0 text smileys in surviving text (11 graphical smileys were dropped by the scraper), 0 "awesome". This is equally consistent with a professional register as with age.

**Reading** [hypothesis]: an adult with professional programming experience reaching back at least to the late 1990s (MSVC6, a self-described design written "more than 2 years ago" in 2010). No birth-year estimate is given; the earlier "before roughly 1975" is withdrawn. Evidence that could narrow it: first-hand, dated references to tools, events or employers, which the archive does not contain.

---

## 3. Technical and subject-matter profile

**Platform of origin: Windows, C++ [measured].** `%appdata%` paths (7 in 5 posts), `c:\program files\bitcoin`, MinGW/MSVC build talk, "I had full wxWidgets on my computer" (`post_81`). Linux and Mac builds were done by others (`post_12`, `post_471`); he asks others to test on hardware he does not have ("I don't have an i5 or AMD", `post_365`). He builds on Ubuntu for releases and asks whether he did it right (`post_144`).

**Depth of cryptographic knowledge [hypothesis].** 156 cryptographic terms in 54 posts on the lexicon in `measures.PROFILE_LEXICONS` (ECDSA, secp256k1, RIPEMD-160, SHA-256, Merkle tree, blinding, zero-knowledge, preimage, collisions, public/private key, signatures; `data/agg/profile_counts.csv`). He explains blinding as "x = (x * large_random_int) mod m" (`post_355`), knows the 160-bit birthday bound (`post_215`), and chooses ECDSA for signature size (`post_32`). He also hedges on details: "Correct me if I'm wrong (please, and I'll gladly eat crow)" (`post_271`), "Sorry, actually it's ECDSA" (`post_276`). The earlier text concluded "a systems programmer, not an academic cryptographer". That is not supported: occasional uncertainty and self-correction are what careful experts also write, and the archive contains no information about training or credentials. What can be said is that his stated confidence is highest on networking, threading, Berkeley DB, serialization and Win32 scheduling (`post_89` includes a Win32 priority table), and that his cryptographic statements are accurate where checked.

**Engineering values [measured phrases].** "dead simple and flat as possible" (`post_307`), "something simple and safe" (`post_388`), "kludge", "hack", "clunky"; old-compiler compatibility kept until forced; `compatib*` in 9 posts. Licensing: Bitcoin is "an MIT license project", so GPL code cannot be merged ("If you GPL stuff, I have to avoid using it. Nothing against GPL per-se, but Bitcoin is an MIT license project. Anything GPL please clearly mark it as such.", `post_75`). He calls GPL "a good license for operating systems" while thinking "the fear of a closed-source takeover is overdone" for small projects (`post_450`). The earlier "distrusts GPL" mischaracterised these passages and is withdrawn. The position is a licence-compatibility constraint plus a preference for permissive licences in small libraries.

**Economics [measured, with hypothesis].** 31 economics terms in 14 posts (lexicon in `measures.PROFILE_LEXICONS`): seigniorage, fiat, scarcity, cornering the market, marginal cost, Moore's Law as a cost driver, "the price of any commodity tends to gravitate toward the production cost" (`post_64`), "natural deflation" (`post_21`), the base-metal thought experiment (`post_427`). "Medium of exchange" does occur in his prose, once (`post_326`); the earlier statement that it never did was wrong. "Velocity", "liquidity", "Gresham" and "store of value" do not occur. The reasoning is applied: production cost, supply, incentives. That says how he argues in this venue. It does not establish whether he had formal economics training, and the earlier "self-taught" label is withdrawn.

**Reading sources [measured].** Links to Wikipedia (3 links in 2 posts), wxWidgets docs, Oracle/Berkeley DB docs, MinGW, a JSON-RPC spec, Wei Dai's site, Szabo's blog; Slashdot coverage mentioned twice. No books, academic venues or newspapers are named. Absence of citations in forum replies is normal for the register and says little about reading habits elsewhere.

---

## 4. Working pattern [measured]

* **Hours.** Of 537 posts, 9 are stamped between 07:00 and 13:59 UTC (`post_156`, `157`, `175`, `176`, `386`, `387`, `522`, `538`, `539`), and only 1 between 07:00 and 11:59 (`post_522`, 09:08). The quietest band is 05:00–13:59 UTC with 15 posts (2.8%). The peak is 16:00–00:59 UTC. The earlier "none stamped 07:00–13:59" was wrong. Hourly counts (UTC 0–23): 32, 23, 15, 10, 9, 3, 3, 0, 0, 1, 0, 0, 3, 5, 14, 18, 46, 64, 62, 43, 42, 55, 47, 42.
* **What the hours can mean [hypothesis].** A low band of about nine hours is what a sleep period plus commute or work looks like, but the band's position fits several time zones depending on assumed sleep and work schedules (afternoon-to-night posting in the Americas, evening-to-small-hours posting in Western Europe), and a single writer can shift habits. The record does not identify a time zone.
* **Days.** Thu 102, Fri 92, Sun 90, Wed 82, Mon 64, Sat 58, Tue 49; weekend share 27.6% versus 28.6% expected under uniform posting.
* **Load.** "Sorry, I've been so busy lately I've been skimming messages" (`post_424`); "I don't have time to try to convince you, sorry" (`post_286`). Volume peaked July–August 2010 and fell to about 22 posts a month by November–December.
* **Personal references.** 0 matches for the personal-life lexicon in `measures.PROFILE_LEXICONS` ("my wife", "my kids", "tonight", "this morning", "at work", "my job", "I live", "my house" and similar), and no place attached to himself on manual reading. The only first-person possessions are "my computer" and "a program I use". Whether this absence is unusual was not tested against the control corpus, so it is reported as a property of this archive only.

---

## 5. Social behaviour and self-presentation [measured]

**Does not say "my" about the system.** 0 "my code", "my design", "my implementation", "my idea", "my plan", "my system", "my software" (`profile_counts.csv`); the system is "the design", "the network", "the software". First-person creative claims are rare and factual ("I designed years ago", "When I wrote it", "I implemented this change in SVN rev 157"). Decisions are announced plainly: "OK, back to 0.3 then." (`post_163`), "We don't support MSVC6 anymore" (`post_264`).

**"We" is the project.** It refers to the developers and users together ("we need the small size of ECDSA", "we haven't found any new bugs for a long time") and never to an outside organisation.

**Credits others by name, briefly.** 19 posts mention Gavin (from 2010-07); "thanks to tcatm", "Thanks Laszlo for the Mac OSX build"; "+1" as approval 4 times in 4 posts (the first version's "19 times in 9 posts" counted signed numbers such as `+18%`); terse praise ("Nice graph!", "Good idea.").

**Disagreement is stated as fact, then explained.** "That's not possible." (`post_43`), "No, not at all." (`post_317`), "You were looking at the wrong code." (`post_285`). Self-correction uses "Sorry, actually…" and "Edit:"; "Correct me if I'm wrong" pre-empts.

**Vocabulary over time** (`data/agg/affect_by_period.csv`, lexicons in `measures.AFFECT`, every match listed in `data/agg/affect_matches.csv`; per 1,000 words):

| Period | Words | Positive | Negative | Security / attack | Government / legal / privacy |
|---|---|---|---|---|---|
| 2009-02 (P2P Foundation, 3 posts) | 868 | 2.3 | 0 | 0 | 5.8 |
| 2009-11..12 | 2,819 | 4.6 | 0.7 | 0 | 2.5 |
| 2010-01..06 | 13,542 | 4.3 | 0.8 | 0.15 | 0.3 |
| 2010-07..09 | 24,288 | 3.8 | 0.7 | 1.6 | 0.3 |
| 2010-10..12 | 7,249 | 2.6 | 0.3 | 2.1 | 0.4 |

The earlier version gave figures for these categories that were not produced by any committed script; they are replaced by the table above, which `02_features.py` writes. Excluding the 25 posts edited more than a day after posting changes no cell by more than 0.2. Excluding all 103 author-edited posts (a conservative check that removes 49% of the late-2010 text) leaves the positive, negative and government/privacy rows within 0.3 of the values above, but lowers late-2010 security vocabulary from 2.1 to 1.1, so the size of the late-2010 security rise depends on a few edited alert and release posts. Two caveats limit the reading. First, the categories are topic-sensitive: the security rise follows the July–August 2010 overflow bug and denial-of-service work, and the government/privacy share is driven by a handful of 2009 announcement and design posts (5 matches in 2 posts in February 2009). Second, positive words include formulaic thanks and "good idea", which track release and review activity. A plausible reading is a shift from advocate-designer to maintainer, but topic mix explains much of the movement, and a change in disposition is not established.

**Humour.** Dry and rare: "I'll gladly eat crow", "Sorry to be a wet blanket" (twice), "+1 to you for having such a long password that you found this bug", "Writing a description for this thing for general audiences is bloody hard."

---

## 6. Cognitive style

### 6.1 Anticipating failure and sizing the safeguard [qualitative finding; not yet tested against other developers]

The most distinctive reasoning pattern in the archive is a sequence: name an assumption that users or programmers will reasonably make, show how it fails, trace the money consequence, and propose the smallest safeguard that closes it.

* **Accounting after reorganisations.** "Programmers are naturally inclined to want to use listtransactions like this: feed me the new transactions since I last asked, and I'll keep my own tally… This will seem to work in all regular use, but if you use the amounts for anything, it is highly exploitable" followed by a numbered list of failure cases ("When there's a block-chain reorg, it would be easy to double-count transactions") and the safeguard: "always … go back to bitcoin and ask for a current balance total … and be ready for the possibility that it can go down" (`post_523`, 2010-12-08). The follow-up states the design principle: "It doesn't seem right to have a function that seems tailor made to be used a certain obvious way, and that way is a non-obvious trap." (`post_526`).
* **A safeguard that opens a new attack.** On the JSON-RPC password: a 50 ms delay after a failed attempt on short passwords "might be used as a DoS attack, but I figured if it's a short password, it's more important to protect against brute force password scan", with the residual leak named ("This may tell outsiders whether the password is less than 15 characters") and a user-side remedy ("If you want to close the DoS possibility, just use a password 15 characters or longer"); batched requests are cut off after one bad password "so you can't stuff it with millions of password attempts in one packet" (`post_241`, 2010-07-18). This text was hidden by the inline-code rule in the first version and is now recovered (rule R12b).
* **Harm to third parties.** Rejecting OP_BLOCKNUMBER: after a reorganisation the transaction "and all its dependants would become invalid. This wouldn't be fair to later owners of the coins who weren't involved in the time limited transaction." (`post_503`).
* **Code over instructions.** "Any backup process/procedure would just be a stopgap until there's time to properly work on coding solutions in software. We can try to use words to help the situation until code gets there." (`post_419`).
* **The same pattern in 2008 e-mail.** Receivers "should wait before taking an action such as shipping goods" (cryptography list, 2008-11-09); an attacker "would have to buy something from a merchant, wait till it ships, then overpower the network and try to take his money back" (2008-11-03); "If a merchant actually has a problem with theft, they can make the customer wait 2 minutes" (2008-11-15); "It's all prevention." (2008-11-15).

The pattern is reported from close reading, with the examples above as the evidence; it was not reduced to a single counted feature, because its surface wording varies. Its stylistic correlates are counted: "It would be very easy to" (4), "If you…" sentence openers (102, of which 77 bare "If you"), "Suppose" (5), and `1)` numbered items (39, several of them failure lists). Whether this reasoning style distinguishes the writer from other experienced protocol developers has not been tested. Until it is, it stays a qualitative finding: the examples show that the writer reasons this way, not that others in the same position do so less. A comparable test would need a matched corpus of design discussions by experienced developers, coded for the same sequence (assumption, failure path, consequence, safeguard) by readers who do not know the authors, with agreement between coders reported. It is listed as an open item in `PROTOCOL_NEXT_TEST.md`.

### 6.2 Other habits [measured]

* **Conditional and scenario-based.** `if` 11.2 per 1k (control writers' median 7.2; but 15 of 44 writers reach Satoshi's level when only answers to questions are compared, so much of this is his answering role; `CONTROL_CORPUS.md`), "If you…" opening 102 sentences, worked examples with numbers, "As a thought experiment", "Think of it as".
* **Quantifies by default.** About 36 numerals per 1,000 words; percentages always as `%`; multipliers as `1.7x`; "an order of magnitude" (4).
* **Hedged predictions, flat decisions.** 264 hedges against 26 boosters, counted without overlap (91% hedges; 47 of 107 eligible contemporary writers are as hedge-heavy), with the hedges attached to predictions and other people's domains and the flat statements attached to his own code.
* **Economy.** Median post 69 words, median sentence 11, 37% of paragraphs a single sentence; answers end on a commitment ("I'll look into it").

---

## 7. What this profile does not support

* A nationality, residence or first language. The dialect evidence is split (section 1), and proficiency does not settle native status (1.5).
* A birth year or age range (section 2).
* Education, degrees or professional credentials in cryptography or economics (section 3).
* A time zone (section 4).
* A change of disposition over time, as distinct from a change of topic (section 5).
* Multiple authors. Every feature examined is stable across the 14 months of the forum record and, for the register-independent features, across the paper and e-mails (validation report).
* The 2014 post. Five words; nothing to profile.
