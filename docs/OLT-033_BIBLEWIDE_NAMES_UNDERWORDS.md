# OLT-033 — Mandatory Bible-wide source-aware name-underword policy

Date: 2026-10-30. Canonical scope: every relevant occurrence throughout **Old and New Testament**, not merely the English Genesis research preview.

The project owner now requires names of people, settlements, cities, regions, divine names/titles and other distinctive meaningful scriptural terms to be evaluated for an English word or phrase **vertically below** the preserved main English name, with independent source identity and notes. A meaning with inadequate source support must remain REVIEW_REQUIRED; the text must not invent a false etymology merely to meet a display quota. This is a **binding editorial policy**, not a claim that each proposed expression is a verified lexical equivalent.

## Latest owner corrections incorporated

| Main English name | Requested lower English text | Evidence category | Release condition |
|---|---|---|---|
| Moses | Draw | Exod 2:10 narrative Hebrew wordplay; historical etymology disputed | Original occurrence plus interpretation evidence |
| God (Elohim) | **Mighty Governance** | Owner semantic/theological interpretation, NOT a literal translation of אֱלֹהִים | Confirm each Hebrew Elohim referent; singular God not multiple beings |
| El | Mighty | Possible strength-related association, not universally compulsory lexical meaning | Distinguish deity noun אֵל from preposition אֶל |
| El Shaddai | My Mighty Strength | Disputed/unsupported-as-literal owner proposal | **No Hebrew My possessive**; do not certify as literal |
| Jerusalem | City of Peace | Traditional historical name interpretation; debated | Independent place-name and source identity check |
| David | The Beloved | Beloved-associated etymology; source history requires caution | Actual name occurrence and lexicon evidence |
| **Noah** | **Rest** | Hebrew נוח rest name association; Gen 5:29 has different root נחם comfort | Distinguish naming wordplay from lexical root |
| Shiloh (Gen 49:10) | To Whom It Belongs | DISPUTED source reading and interpretation | Do not equate automatically with place |
| Shiloh (Joshua 18:1) | Place of Rest | Traditional place-name association | Distinguish from disputed Genesis reading |
| Siloam (John 9:7) | Sent | Explicit Gospel explanation | Greek NT RP2018 source still unpinned, so no invented token ID |

Source-cited full records: `lexicon/name_underwords.json`; binding policy `data/policy/olt_name_underword_policy.json`. The existing `lexicon/hebrew.json` references the candidate-name registry without changing its fifteen original entries or the owner locks bara/asah/raqia/waw.

## Data model and implementation milestones

Each meaning record must retain **original-language word** and text edition, original lemma or name identity, exact source verse/token ID once imported, referent disambiguation, intended upper English display and secondary English wording, evidence category, citation, negative evidence, approval status, source-specific footnote and printed/accessible layout. Hebrew and Greek names cannot be matched by English substring, and transliterated names must be rechecked in their own source language.

1. Treat the 10 records as **research candidates**, not a completed name lexicon.
2. Build exact 39-book Hebrew name-entity occurrence indexing on pinned OSHB identifiers, with all ambiguous token cases held for review.
3. Pin/import the source of the Greek NT (Robinson–Pierpont RP2018) under confirmed licenses; then index Greek original names and transliterations with no fabricated ID chain.
4. Add occurrence-aware, multiword line-wrap-safe vertical renderer and evidence notes; check coexistence with Gen 1:1 **In/with** and `[of His Power]`, original RTL Hebrew and Greek accents.
5. Require independent morphological/onomastic review, explicitly owner-selected interpretation labeling, per-name coverage reports, visual print QA, and separate publication authorization.
6. Provide names as locale-specific semantic data to the forthcoming multilingual Bible translation engine; the **English** owner underwords are NOT automatically translations into Amharic, Japanese, Icelandic or Chinese.

## Safety and progress limits

- Ten initial name examples; zero Bible-wide occurrence mappings completed; no source-derived NT names yet.
- Owner wording decisions **Mighty Governance** and **Rest** supersede any prior `Mighty Powers` wording in the OLT-033 draft.
- Underword colors remain purple `#5B277D` for the primary and blue `#2463A6` for lower text; no slash notation.
- The singular God must never be misrepresented as multiple independent gods because of Elohim's plural morphology.
- The singular OLT-022 **In/with** exception at Genesis 1:1 is a different interpretive layer and remains untouched.
- No independent name etymology/morphology certification and no new approved English Bible verse. **Publication BLOCKED.**

## Automated QA

`scripts/validate_olt_033_names.py`, `tests/test_olt_033_names.py`, and `.github/workflows/olt-033.yml` verify the policy, actual Genesis 1:1 Elohim token `01TyA`, name category separations, owner corrections, and fail-closed status. GitHub Actions success means **consistency of research records**, not final factual proof of disputed name etymologies.
