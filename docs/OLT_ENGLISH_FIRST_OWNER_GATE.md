# Binding owner decision: English-first translation scope (OLT-ENGLISH-FIRST-001)

**Effective 2026-10-31. Owner instruction. This policy takes precedence over earlier planning documents where they discuss actively implementing Japanese, Amharic, Chinese, Icelandic, Swedish or any other non-English target translation before the English Bible is finished and personally verified.**

## What is being built now

**English is the sole active target language.** The immediate deliverable is a *working* original-language-to-English OLT translation engine and ultimately a complete, balanced-yet-literal English Bible translation covering **all 66 canonical books**, translated from the original source languages:

- **Hebrew** for applicable Old Testament text.
- **Biblical Aramaic** for applicable Old Testament passages.
- **Greek** for the New Testament.

This does not authorize automatic scholarly validation or publication. Original source alignment, lexical and morphology controls, systematic tests, and separate independent philological checks remain required. Original-source evidence is distinguished from OLT editorial choices. The permanent Hebrew **wayyiqtol → English simple past** rule continues to apply *only when the original Hebrew verb has actually been morphologically identified as wayyiqtol*. Do not apply that rule based on a guess or to other Hebrew verb forms.

The owner **must personally verify and explicitly approve** the *complete Hebrew/Aramaic/Greek → English Bible translation* before the English milestone is considered finished or another translation target becomes active. CI may confirm engineering repeatability; **CI is not owner approval** and must never invent a user decision.

## What is postponed

**Japanese is NOT a current translation target.** The same is true of Amharic, Icelandic, Chinese, Swedish and all other non-English target languages. Do not build their verse translations, translation-specific lexical engines, output generators, independent translation repositories, PDFs or publications in this phase.

Older OLT-034 multilingual research profiles are **preserved as historical or future-facing schemas**, not as permission to start translation work. The architecture of a common original-language core for eventual other language repositories is retained as a **future option only**. Do not delete historical architecture or original-language source research, and do not change original source-data facts to fit this planning decision.

The English master/reference lexicon is now part of the **English-only active deliverable**, not an English intermediate through which other-language translations are generated. Original Hebrew/Aramaic/Greek will remain the evidence for English; future languages, if authorized later, must be researched against original languages rather than blindly translated from English.

## Revised immediate engineering priority

1. **Make the actual source→English engine produce reviewable English draft verses**, beginning with a small deterministic proof of concept using already pinned original-source passages. Each produced word, phrase, tense and note must retain original-verse/token provenance, decisions and unresolved evidence.
2. **Demonstrate English output against source evidence and owner rules** before expanding more specialized documentation. Clearly distinguish `UNREVIEWED_ENGLISH_DRAFT` from verified/approved English and publication-ready Scripture.
3. Expand demonstrably tested and reviewable coverage from verses to books, then the entire OT+NT, while retaining explicit uncertainty and human linguistic review.
4. Request complete-owner approval only when the entire 66-book **English** translation exists and can actually be inspected by the owner. Partial Genesis/NT approval, checkmarks, CI or model responses do **not** satisfy the completion gate.
5. Only **after** explicit owner approval of the complete English base may later non-English language translation projects be discussed as active implementation. **No automatic gate release** is permitted.

## Verification of this project's binding decision

Machine-readable source of truth: [`data/policy/olt_english_first_owner_verification.json`](../data/policy/olt_english_first_owner_verification.json). Tests must enforce the single English active target, all other targets deferred, full English Bible completeness requirement, explicit user approval and no release by GitHub Actions. The current canonical state is in [`STATUS_CURRENT.md`](STATUS_CURRENT.md).

**Current state:** working end-to-end source-to-English full-Bible engine **NOT DONE**; owner verification of complete English Bible **NOT DONE**; translation publication **BLOCKED**. This is a scope decision, not a claim that any English Bible has been completed.
