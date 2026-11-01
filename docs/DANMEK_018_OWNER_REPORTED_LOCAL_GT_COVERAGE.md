# DANMEK-018 — Local owner-run OT coverage report (2026-11-01)

This checkpoint records numerical output the owner pasted from the private
Parrot run of DANMEK-016, after updating local main to commit
`156eab909426e86ae0ab56db1d513a4f8f03892b`.

**Owner-reported observations**

- 929 locally imported chapter files, 39 source filename prefixes, zero
  internal chapter-number gaps.
- 23,144 observed source verse rows and 401,460 original source fragments.
- 2,990 English editorial reorders; 311 ambiguous cases unchanged;
  19,843 verses with no detected order candidate.
- 9,540 isolated lowercase-c letters hidden; 2 faces simplifications;
  9,368 verses with one or more display edits.
- YLT conflict counter zero **because YLT comparison was not enabled**.
- Publication status: **BLOCKED**.

Per-prefix chapter/verse counts as **shared by the owner**, and only
numeric observations, are kept in
`data/observations/danmek_018_owner_reported_gt_coverage_20261101.json`.
The 39 reported prefix totals add up to 929 chapters and 23,144 verse rows.
The three exclusive English reorder outcome counters also add up to
23,144. The 9,368 edited verses are a union, not the sum of all edits.

**Critical provenance limits:** The assistant did not open the private
archive, re-run the scan on the user's machine or authenticate original
source files. The result proves observed local counts by the existing
source-validated reader, not each original Biblical word or translation.
Actual DANMEK-017 membership against the supplied original index has
**not** been run; no confirmed index HTML path was provided.

**Known source exception:** Nehemiah 7 uses source primary verse labels
1–67 and 69–73, with original alternative labels 68–72. The importer
preserves that numbering. Do not introduce an invented 7:68 record
merely because a conventional verse total differs from 23,144.

**Owner locks:** The DANMEK-013/014 English HTML presentation remains
visually approved and unchanged. Ambiguous clauses are not automatically
translation errors. The 66-book English translation is not complete or
fully owner-approved; publication remains **BLOCKED**.

This document stores only source-archive counts and owner-shared filename
prefix IDs; never store actual private text or files in public Git.
