# DANMEK-004 — Complete chapter-to-YLT verse lookup (2026-10-31)

## Evidence and goal

The owner successfully generated a local 929-chapter private CHES+YLT reading. The actual terminal report shows **1,607 YLT verse-lookup misses**, localized to three source filename prefixes: `1kg=816`, `2kg=719`, and `neh=72`. No CHES source files were missing. The existing engine correctly preserved the originally printed English source when no reliable YLT target could be established.

## Book IDs

The original Scripture4All CHES file prefixes `1kg` and `2kg` are the two Books of Kings. The exact pinned public-domain Young's Literal Translation JSON uses `1ki` and `2ki`, respectively, with **22 and 25 chapters**. Only the book-ID lookup is extended; this does not alter Hebrew lemmas, verses, CHES green-text data or PDF chapter imports.

## Nehemiah 7 (strictly numbered, no new verse)

The original CHES PDF has **72 source verses**: printed primary `7:1..67`, **no primary 7:68**, then printed primary `7:69..73` with respective printed *alternate* `7:68..72`. The public-domain **YLT 1898** includes the extra `7:68` horses/mules verse and numbers the following camel verse `7:69`; the 1898 edition has **73 verses** in chapter 7. The two numbering conventions and the omitted Hebrew-MT verse are documented in [NET Bible textual note](https://classic.net.bible.org/passage.php?passage=Neh+7%3A6-69), [Biblical translation commentary](https://tips.translation.bible/story/translation-commentary-on-nehemiah-766-769/), and [Young's Literal Translation chapter](https://original.sacred-texts.com/bib/ylt/neh.htm). The original source PDF's printed markers and alternate labels were separately verified by existing `ches-neh7-source.yml` tests.

**Only** look up the original source's **printed PRIMARY verse number in YLT 1898** when:
1. Pinned exact YLT 1898 Nehemiah 7 has **73** verses, with `horses` at 68 and `camels` at 69;
2. A source row 1..67 has no alternate number; or
3. A source row 69..73 has the exact independently printed alternate number `primary - 1`.

Never create or translate a CHES source 7:68 record, never silently use the alternate number as a YLT verse, and never change the primary numbering in saved JSON/HTML. If those pinned 1898 edition controls or printed source alternate markers fail, **leave that source verse unchanged** and record it as unmapped. This is a **source-versification lookup**, not authenticated Hebrew-word-to-English fragment alignment or independent whole-translation approval.

## Pipeline and verifications

- `scripts/danmek_ylt.py`: add both Kings aliases, guarded Nehemiah 7 verse lookup, and a **new versioned overlay revision** so a corrected private snapshot cannot overwrite the previous one.
- `tests/test_danmek_002_ylt_verse_authority.py`: synthetic chapter/schema, edition corruption, missing source verse 68, alternate-number tampering, no lexical source text leakage.
- `.github/workflows/danmek-ylt-source.yml`: checks the **real exact pinned YLT 1898** 1 Kings/2 Kings book IDs and 22/25 chapter counts, Nehemiah 7 73-verse chapter and strict 68/69 horses/camels control. No public CHES content or source verses in Actions logs/artifacts.

The owner is permitted to use CHES JSON locally. No CHES payloads are committed, source PDF contents are not edited, and publication remains BLOCKED subject to separate approval/rights and English translation QA.

**After merge** the owner can run the existing offline private reader with `--use-ylt-authority`. The expected YLT lookup-miss count is **zero if all 929 chapter contents and exact edition metadata satisfy these source-numbering checks**; the actual number must be confirmed by the owner's own next report, not a CI-only synthetic claim.
