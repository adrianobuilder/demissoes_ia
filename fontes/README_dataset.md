# AI Layoffs Register: a source-cited dataset of AI-attributed job cuts (2023 to 2026)

A machine-readable, source-cited register of layoff and workforce-reduction events
that companies, filings, or credible reporting have linked to artificial
intelligence. It is the underlying evidence base of the **AI Layoffs Index**
(https://ailayoffs.org), an open observatory that scores AI's estimated impact on
jobs relative to AI's own history since 2023.

Every row links to its source (an SEC filing, an official company statement, or
named reporting), and every source opens without a paywall. Each row also carries an
explicit classification of how strongly the cut is attributed to AI and whether its
figure is counted. This is a register built to be **cited and audited**, not a
press-clipping tally.

- **Canonical, continuously-updated version:** https://ailayoffs.org/events?utm_source=kaggle&utm_medium=dataset&utm_campaign=kaggle-dataset
- **Live JSON API (keyless):** https://ailayoffs.org/api/index
- **Full register as CSV (always current):** https://ailayoffs.org/api/register.csv
- **Methodology:** https://ailayoffs.org/methodology?utm_source=kaggle&utm_medium=dataset&utm_campaign=kaggle-dataset
- **Permanent archives:** Zenodo (CERN), concept DOI https://doi.org/10.5281/zenodo.22759361 (always the latest version), and Harvard Dataverse, https://doi.org/10.7910/DVN/ZTXNYY

## Version history

- **2026-10-23, methodology 1.36.** A register release; the written method is unchanged
  from 1.33. The daily checks of news, company filings and earnings calls from 18 to 22 October
  2026, a check of every company page for new cuts, a check of AI-linked cuts in India and leads
  left open by earlier checks add 20 entries. One is counted: Barclays' plan to cut about
  5,000 roles, announced with its third-quarter results on 22 October 2026, which the bank tied in
  part to AI. Eight carry a reported figure that is set aside with its grounds stated:
  Intesa Sanpaolo (about 12,400 exits by 2029 through voluntary exits and natural turnover), National Australia Bank (up to 2,500), GSK (up to 1,217), Capgemini (up to 748), Zomato (about 250, a press figure), Bendigo and Adelaide Bank (137, a union figure), IBM (57, a union figure) and Lookiero (50, a press figure). Six are recorded without a figure: Paytm (May 2024), Fi Money, Google
  (June 2026), Commonwealth Bank (July 2026), Disney's legal department and Vermont Information
  Processing. Five are workforce statements, not cuts: JPMorgan Chase, Wells Fargo, Axis Bank,
  Anthropic and HDFC Bank. The entry for Disney's late-September 2026 layoffs (about 300 roles in
  human resources and technology, a press figure) adds the remarks its president and chief creative
  officer, Dana Walden, made on 1 October 2026 at Bloomberg's Screentime conference; she did not
  mention AI, and the entry's grade and figure are unchanged. None of the new entries counts in the
  US index. Corrections: Intesa Sanpaolo's October 2024 entry (9,000 exits by 2027) no longer calls
  its figure a net change in headcount; it is set aside because the reduction comes through
  attrition. The snapshot table's country count is corrected: it had counted the words "other
  countries" in one row's country field as a country, so version 1.35's figure of 28 should have
  read 27. Roles counted across all years: 78,847 to 83,847; roles reported and
  set aside: 268,610 to 285,969. 320 events in all.
- **2026-10-17, methodology 1.35.** A register release; the written method is unchanged
  from 1.33. Two changes. First, a check of AI-linked cuts announced in 2023 and 2024, years the
  register had covered thinly, adds 26 entries (2023: 5 to 13 events, 2024: 12 to 30). Six are
  counted, each from the employer's own words: Cisco's August 2024 restructuring (about 6,328 roles,
  7% of its workforce), AMD's November 2024 cut (about 1,040), Dropbox's April 2023 cut (about 500),
  Telenor Norge (about 100), The 1% Club (28) and Onclusive (218). Among those recorded without a
  counted figure are Amazon's November 2023 Alexa cut, Dukaan, Paytm, Google's January and April 2024
  cuts, ThredUp, TikTok's October 2024 moderation cut and Turnitin's 2023 forecast; Radio Krakow is
  recorded against its employer's denial. Dell's 2026 entry is corrected: its September 2024 filing
  speaks of "leveraging new technology" and does not name AI. Second, four columns are appended to the
  CSV, so every earlier column keeps its position: `Event ID` (the register's stable id), `Kind`
  (`cut` or `workforce statement`: 13 rows are an employer's
  statement about AI and headcount, not a layoff, and should be left out of any count of cuts),
  `What the employer said` (the label the site shows for the employer's own position) and `Job
  families` (the register's own coding of the kinds of work cut). Roles counted across all years:
  70,633 to 78,847; roles reported and set aside:
  256,469 to 268,610. 300 events in all.
- **2026-10-15, methodology 1.34.** A register release; the written method is unchanged
  from 1.33. Three changes. First, a check of news, company filings and the first third-quarter
  earnings calls from 2026-10-11 to 2026-10-15 adds six entries, none counted: Kroger's plan to cut
  about 3,000 corporate roles (`blamed`: Reuters and Bloomberg tie it to AI, Kroger's memo names
  technology but not AI); One Zero (about 25, a press figure, `mixed`); Sunrise (up to 450, an upper
  limit, `mixed`: the company names AI and automation as tools of its restructuring); KLM (the work of
  126 full-time jobs moved to Manila, which De Telegraaf ties to an AI translation tool, `blamed`); and
  two employer statements that are not layoffs: Bank of America's chief executive tying part of a
  headcount fall of about 3,000 to AI (`mixed`, no figure recorded, since the fall overlaps a figure the
  register already holds), and Worldia's co-founder saying AI cut its headcount by 40% in 18 months
  (`explicit`, no figure). Second, from a check of the full layoff history of the 23 companies whose
  pages people reach from search (2026-10-14): Chegg's June 2023 (about 80), June 2024 (441) and
  November 2024 (319) cuts are added and counted, each from Chegg's own filings; ING's expected fall of
  about 1,250 operations staff in 2026 (a net change, not counted) and Amdocs' 2026 restructuring (2,700,
  a press figure) are added. Third, corrections: Teleperformance's AI-transformation plans now concern
  about 5,400 employees (was 3,300, from its July 2026 half-year report); Darrow named its own AI
  milestones among its reasons, so its July 2026 cut moves from `blamed` to `mixed` and its 60 roles
  count; Atlassian's 2025 support cut is 350, not 150; C.H. Robinson's entry is dated August 2025, when
  its AI-linked restructuring was first disclosed, and an unsupported 1,400 is removed; and the company
  recorded as Bolt is renamed Bolt Financial, the US checkout company it always described. Roles counted
  across all years: 67,433 to 70,633; roles reported and set
  aside: 250,378 to 256,469. 274 events in all.
- **2026-10-10, methodology 1.33.** Four changes. First, a written rule for which events
  belong in the register: a cut is included only when the employer, or credible reporting, ties that cut
  to AI (AI doing the work of the people cut, money moved from their roles into AI, or AI changing the
  business that employed them); automation with machines, a cut at a company whose product is AI, or AI
  mentioned only as an industry backdrop is not enough. Under it, UPS's April 2025 plan (about 20,000
  operational jobs) and January 2026 plan (up to 30,000) were removed: no credible report we found tied
  either to AI, and UPS gave the decline in its Amazon volume as the reason. UPS's October 2025 row stays.
  Second, regrades: British American Tobacco's June 2026 cut moves from `blamed` to `mixed` and its
  circa 5,500 roles now count, because its interim finance chief said on the record that the programme
  behind it would make the business "more digital and AI-focused"; CrowdStrike's May 2025 cut and
  Chegg's May and October 2025 cuts move from `explicit` to `mixed`, because each employer's own
  announcement also gives other reasons (their figures still count); Klarna's February 2024 row is now
  an employer statement rather than a cut, with no reported figure (the 700 described the work its AI
  assistant did); and, from 2026-10-09, Tata Consultancy Services' July 2025 cut moves from `blamed`
  to `mixed`, its 12,000 and Intuit's 3,000 are marked as press figures, and Walmart's 1,000 as
  including relocations. Third, sources: five rows whose own source was a subscriber or registration-only
  article now link to free sources (WPP, GeoComply, Envato, Culture Amp, The Washington Post), as do
  Walmart and Verizon (2026-10-09); and smaller corrections to the `Claim`, `Functions`, `Date` or
  `% of workforce` of Amazon (January 2026), ClickUp, Microsoft (July 2026), Allianz Partners and
  Walmart. Fourth, 10 events are added from a scan of news and filings through 2026-10-10 and of
  earlier leads: Freshworks (500, May 2026) and BenchSci (70, January 2024) are counted; HoneyBook
  (about 30, a press figure) and EBRA (up to 400) are reported and set aside; Konecta in Italy (670
  full-time equivalents), Ouest-France (156), Meta's Reality Labs (more than 1,000, a press figure),
  Amazon's AGI unit, Nielsen Media Italy (43, a union figure) and McClatchy (more than 90, a union
  figure) are `blamed`. Roles counted across all years: 61,363 to
  67,433; roles reported and set aside: 304,189 to
  250,378. 263 events in all.
- **2026-10-08, methodology 1.32.** Three changes. First, a written rule for the roles in
  the `Functions` column: a role is recorded only when the employer, or reporting the row cites, says
  it was cut (marked "per" the outlet when it comes from reporting). The areas where a company says it
  is applying AI, the processes it is redesigning, the teams it is still hiring for and its description
  of its own business are not roles cut; internal support functions are not customer service; and
  severance a company books by function in its own filing counts line by line. Re-reading the sources
  of every cut where the employer named AI under this rule changed the roles of 84 rows, 27 of which
  now begin "Not specified"; eight more rows changed only so that no entry contains a semicolon, the
  separator between entries, so `Functions` changed in 92 rows. Second, corrections to existing rows:
  the `Claim` of 12 rows, where it quoted wording no listed source prints or misattributed a remark
  (among them the Washington Post, Meta, PayPal, Intuit, Oracle, Autodesk and Freshworks) or, for
  Telus, to state what its new sources say; the `Source` of Atlassian's March 2026 row now points to
  the document that states its figure, and Telus's row on its 2024 workforce reduction (dated
  2025-02-13) to Telus's own annual filings instead of a subscriber-only article. `Why not counted` now reads "the company has not named AI as the cause"
  where it said the company's own announcement or filing does not name AI, and a figure a union gave
  is labelled as the union's rather than the press's (49 rows in all). No existing figure, grade or
  tier changed. Third, 12 events are added from a scan of news and filings through 2026-10-08, and from
  gaps found on the way: HubSpot (660), FICO (581, 15% of the workforce it publishes), DNB (400
  full-time equivalents) and E.W. Scripps (268) are counted; Tamedia (34) is set aside because its
  editorial director said AI is not the reason for the cut, although its announcement makes AI part of
  the change; Groupe SEB (up to 2,100), Proximus (1,200, through attrition), Cariad (about 1,000, a
  press figure) and F-Secure (up to 145) are reported and set aside; HSBC's UK wealth cuts, Future plc
  and CWT Italia (190, a union figure) are `blamed`. Roles counted across all years:
  59,454 to 61,363. 255 events in all.
- **2026-10-05, methodology 1.31.** A consistency check applied the register's written
  rules to events that earlier reviews had not re-read, and wrote down a rule for an employer
  whose own statements conflict: a statement that AI was not a reason for the cut keeps
  its figure out of the count, while the event keeps the grade its statements support. Set aside: Amazon's October 2025 cut of about 14,000 (its
  chief executive said the round was not AI-driven), Klarna's December 2024 figure of
  1,000 (a fall between two headcounts, reached by not hiring), ERGO's 1,000 and Telstra's
  200, which include work moving to other countries, and BT's 2023 figure of 10,000, which BT
  states as part of its total labour resource, contractors included. Counted: HP's plan to cut
  4,000 to 6,000, at its lower end; IONOS's planned cut from about 3,800 to about 3,350 staff;
  percentages of a workforce the employer publishes at Elastic, Rapid7, Playtika, Zscaler,
  PagerDuty, Rackspace and lastminute.com; Ocado's 1,000, which the press reports as the
  company's own figure; and Atlassian's 150 and Altruist's 50, whose employers named AI among their reasons. UPS's October 2025 and Procter & Gamble's June 2025 cuts are now `blamed`,
  since neither company named AI; SAP 2024, Intuit 2024 and Business Insider 2025 are
  now `mixed`, as is GitLab's June 2026 cut, whose chief executive named AI as part of the plan.
  One event is added: Firebolt's February 2026 cut, which the 1.30 check had left
  out although its coverage presents the cut itself as AI-driven (`blamed`, no figure). Figures for eight events that the register had left blank are now recorded in
  `Roles reported (not counted)` with their grounds, among them SAP's 8,000 and
  Accenture's 11,000. Roles counted across all years: 77,339 to 59,454. The
  snapshot table now counts countries named in the country field (22), not its distinct
  entries (37, given as the number of countries in version 1.30). A working paper describing the register and what it shows is
  published with this version: https://doi.org/10.5281/zenodo.23148082 . 243 events in all.
- **2026-10-04, methodology 1.30.** The register was checked for completeness
  against 21 public trackers and the news. For 2026 it gained 83 events (13 from a scan of news and
  filings from late August to early October, one of them announced in May, and 70 from January to August that Layoffs.fyi's AI list or
  news reports held and the register lacked), each re-read against the employer's own
  words; for 2025, the leads that check deferred were verified the same way on
  2026-10-04, which took 2025 from 37 events to 80, so both years now meet one
  standard. A written rule now covers cuts that
  other trackers or the press present as AI layoffs while the employer names another
  cause or says AI was not the reason: each is recorded as `blamed`, with its claim
  and why it fails, and is never counted, so a reader who meets the claim elsewhere
  can check it here. Events per year: 2023: 4, 2024: 9, 2025: 80, 2026: 149. 242 events in all.
- **2026-10-01, methodology 1.29.** A written rule now decides when a figure is the
  employer's own: the company put the number on the record in a filing, a release or
  a letter it publishes, through a named executive speaking publicly, or through its
  spokesperson. Re-checking about 55 events under that rule newly counted Meta's May
  2026 cut of about 8,000 (its quarterly filing), Teleperformance's 3,300, Visa's
  2,600, ERGO's 1,000, monday.com's 620 and Starling Bank's 130. It set aside six
  figures the register had counted, among them Salesforce's 4,000 from 2025 (a net
  change in headcount, shed through attrition), Vodafone Germany's 2,000 (the company
  did not name AI, and the number includes roles moved elsewhere) and Klarna's 700
  from 2024 (the company said the cut was not caused by AI). Reported figures that
  2026 rows had left out are now recorded, among them Oracle's 21,000 and Dell's
  11,000, both set aside. Five events were added (Arctic Wolf, DeepL, Lufthansa Group,
  Playtika and Recruit Holdings), six were re-dated to their sources, and the Axel
  Springer row now covers its 2023 Bild announcement, whose figure is a press report
  and is set aside. 116 events in all.
- **2026-09-30.** Every row now links to a source anyone can open for free: 13 rows
  that cited subscriber-only articles were re-sourced, and re-reading them corrected
  four details (Microsoft's July 2025 cut in Washington state was 830, not 1,985;
  about two-thirds of the UPS building closures were in the eastern US, not half;
  Goldman Sachs had about 1,900 more staff than a year earlier; Thomson Reuters
  announced only "a small number of roles"). The `Primary source` and
  `Primary source URL` columns are renamed `Source` and `Source URL`, because about
  half the sources are named news reports rather than primary documents. `Why not
  counted` no longer cites US scope: a figure without a US breakdown still counts in
  the worldwide totals, and US scope decides only `Counts in US index`.
- **2026-09-28, a correction.** In the first deposit the `Counts in US index` column
  repeated whether an event's roles were US-based, so 19 rows that count zero were
  marked `yes`, among them UPS, Verizon and Walmart. The column now marks only the
  rows whose counted figure enters the US index sum. Added the `Why not counted`
  column (111 events).
- **2026-09-14:** first deposit (110 events).

## Snapshot in this copy

Register snapshot of 2026-10-23, methodology version 1.36. Figures below are computed
from the CSV in this copy and are internally consistent with it.

| Measure | Value |
| --- | --- |
| Events (rows) | 320 |
| Distinct companies | 257 |
| Date range of events | 2023-02-22 to 2026-10-22 |
| Events per year | 2023: 13, 2024: 31, 2025: 80, 2026: 196 |
| Rows with a source URL | 320 (100%) |
| Distinct source domains | 162 |
| Rows sourced to SEC filings (sec.gov) | 68 |
| Evidence tier 1 / 2 / 3 | 146 / 149 / 25 |
| Attribution explicit / mixed / blamed | 39 / 199 / 82 |
| Rows with a counted figure | 93 (83,847 roles) |
| Rows with a reported figure set aside | 164 (285,969 roles) |
| Rows counted in the US index | 7 |
| Countries named in the country field | 28 |

For 2026 alone: 196,424 roles reported in AI-linked cuts, 58,949 where the company
itself named AI and stated the number.

The AI Layoffs Index headline reading recomputes live at the canonical site. Cite a
live reading with its date and methodology version, not this static snapshot, when
you need the current number. The working paper at https://doi.org/10.5281/zenodo.23148082
describes how the register is built and what it shows, using version 1.31.

## Files

- `ai-layoffs-register.csv` : the register, one row per event, UTF-8, comma-separated,
  header row included. Its content is identical to the live
  `https://ailayoffs.org/api/register.csv` endpoint for version 1.36 (published 2026-10-23);
  the live file starts with a byte-order mark, this copy does not.
- `README.md` : this file (data dictionary and method card).
- `LICENSE.txt` : the full data license and custom terms of use.

## Column dictionary (`ai-layoffs-register.csv`)

| Column | Meaning |
| --- | --- |
| `Company` | Employer name as it appears in the source. |
| `Date` | Event date (ISO `YYYY-MM-DD`): the announcement, filing, or effective date. |
| `Sector` | The employer's sector. |
| `Country` | The employer's home country (headquarters or domicile), as free text; for a few events it names where the roles were instead, or notes that the employer is global. |
| `Functions` | The roles cut, where a source says which, as entries separated by "; " (no entry contains a semicolon). An entry that comes from reporting names the outlet ("per ..."); when no source says which roles went, the entry begins "Not specified". |
| `Roles counted` | Headcount that meets the register's standard for an AI-attributed cut and enters the worldwide totals. Blank when no qualifying figure exists. |
| `Roles reported (not counted)` | Headcount reported for the event that the register deliberately does not count. Kept separate so counted and reported facts are never conflated. |
| `Why not counted` | The grounds for setting that reported figure aside, in plain words: the company said the cut was not caused by AI, or it has not named AI as the cause; or the number is not a figure the company stated as a cut (reported by the press or given by a union rather than stated by the company, an upper limit, a net change in headcount, roles shed through attrition, or a count that includes contractors or roles moved to other teams or locations). |
| `% of workforce` | Share of the workforce affected, where the source expresses it. |
| `Evidence tier` | Strength of the evidence for the AI attribution. Tier 1 = primary filing or first-party company statement; Tier 2 = named, credible reporting; Tier 3 = weaker or single-source signal. |
| `Attribution` | How strongly the cut is tied to AI. `explicit` = the employer itself names AI as the cause; `mixed` = AI is one stated factor among others (efficiency, restructuring); `blamed` = a credible source names AI but the employer does not, so the row is never counted. |
| `Execution` | Status: `announced`, `executed`, `partial`, `reversed` or `unknown`. |
| `Counts in US index` | `yes` only when a counted figure covers US-based roles, so it enters the US index sum. `no` for every other row, including US-based rows whose figure is not counted. |
| `Claim` | A short, sourced description of exactly what was disclosed and how it is classified. |
| `Source` | The name of the source (for example, a specific Form 8-K or a named news report). |
| `Source URL` | A resolvable link to that source, free to open. |
| `Event ID` | The register's stable identifier for the event (for example `cisco-2024-08`), the same id the JSON API uses. Added in 1.35. |
| `Kind` | `cut` for a layoff or workforce reduction; `workforce statement` for an employer's public statement about AI and the size of its workforce made when no discrete cut was announced (a forecast, or a headcount said to have fallen through attrition). A statement never carries a counted figure; leave these rows out of any count of cuts. Added in 1.35. |
| `What the employer said` | The employer's own position on AI for this event, in one of seven fixed labels the site also shows: "Declared the cut AI-related", "Cited AI among other reasons", "Cited AI, but also said AI was not a reason", "Credited AI; reduced through attrition, not layoffs", "Denied the AI link others made", "Named no AI reason; others linked it to AI", "Spoke about AI and headcount; no cut announced". Added in 1.35. |
| `Job families` | The kinds of work cut, coded by the register from the roles its sources name, separated by "; ": Customer service and support, Operations and back office, Software engineering and IT, Corporate functions, Sales and marketing, Management layers, Product and design, Writing, editorial and translation, Content moderation, Frontline and manual work, Consulting and professional services, or Not specified when no source says which roles went. Added in 1.35. |

## Method, in brief

- **Inclusion:** an event enters the register only with a resolvable source and a
  defensible link to AI. Restructurings with no AI link are excluded.
- **Counted vs reported:** a figure is counted when the employer itself ties the cut
  to AI (explicitly, or as one of several stated reasons) and puts the number on the
  record: in a filing, a release or a letter it publishes, through a named executive
  speaking publicly, or through its spokesperson. A number whose origin is the
  reporting itself (unnamed sources, an internal memo the company has not confirmed,
  or reporters' arithmetic) stays in the register as reported, with its grounds in
  `Why not counted`, and so does a net change in headcount, an "up to" ceiling, or a
  count that includes contractors or roles moved elsewhere. An invented number would
  look exactly like a measurement, so none is ever filled in.
- **Ranges and percentages (since 1.31):** a range the employer states counts at its lower end, and a
  percentage the employer states counts when the employer also publishes the workforce it
  applies to (its most recent published headcount); the register then computes the number (for example 7% of the 4,019 employees
  Elastic reports). A planned cut the employer states as its headcount before and after counts as
  the difference.
- **Conflicting statements (since 1.31):** when an employer's own statements conflict, a
  statement that AI was not a reason keeps its figure out of the count; the event keeps the grade
  its statements support (Amazon's October 2025, Intuit's May 2026 and Thinkific's September 2026 cuts are `mixed`).
- **Moved roles (since 1.31):** a figure that includes roles moved to other teams or locations rather than
  eliminated is set aside (ERGO's and Telstra's 2026 figures, as Lufthansa's 2025 figure).
- **What is recorded as `blamed` (written in 1.31):** a cut the employer did not tie to AI is recorded only when
  a source that can be opened presents the cut itself as caused by AI; a tracker's label alone, or coverage
  that only mentions the employer's AI plans beside the cut, is not enough.
- **Roles cut (since 1.32):** the `Functions` column records only roles the employer, or reporting the
  row cites, says were cut; where the roles come from reporting, the text says which outlet. The areas
  where a company applies AI, the processes it redesigns and the teams it is still hiring for are not
  roles cut. Internal support functions are not customer service. Severance a company books by
  function in its own filing counts line by line. When no source says which roles went, the entry
  begins "Not specified". No entry contains a semicolon, so the column splits cleanly on "; ".
- **Which events belong (since 1.33):** a cut is included only when the employer, or credible
  reporting, ties that cut to AI: AI doing the work of the people cut, money moved from their roles
  into AI, or AI changing the business that employed them. Automation with machines, a cut at a
  company whose product is AI, or AI mentioned only as an industry backdrop is not enough. An event a
  later review finds without such a link is removed, and the version history says so.
- **Attribution honesty:** the register distinguishes an employer naming AI itself
  (`explicit`) from AI being one factor among many (`mixed`) from a third party
  attributing it (`blamed`). Most public "AI layoff" claims are `mixed` or `blamed`,
  and the data preserves that distinction rather than flattening it.
- **The index built on this register** blends the register signal with independent
  labor-market series (Challenger job-cut reports, jobless claims, sector postings,
  AI-exposure research). Full methodology, versioned, at
  https://ailayoffs.org/methodology.

## How to cite

> AI Layoffs Register (methodology v1.36), AI Layoffs Index, snapshot 2026-10-23.
> https://ailayoffs.org . Permanent archive: https://doi.org/10.5281/zenodo.22759361

For a specific event, also cite that row's linked source.

## License

Free to read, quote, redistribute, and build on (including commercially) with
attribution. This is a custom attribution license, **not** Creative Commons, by
design: the register links to sources under many different licenses, so a blanket
CC grant would claim rights the project does not hold. See `LICENSE.txt` in this
dataset, or the canonical page at https://ailayoffs.org/license .
