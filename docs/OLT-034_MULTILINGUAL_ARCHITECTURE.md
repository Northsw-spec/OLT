# OLT-034 — Source-first multilingual translation-engine architecture

**Decision date:** 2026-10-30. **Status:** reusable research-packet foundation implemented; OT/NT target-language translations and publication remain BLOCKED.

## Binding owner decision

Use **one canonical source-first OLT core** in the repository Northsw-spec/OLT and **separate GitHub repositories for each target language**. The shared OLT core contains original-language textual provenance, verified source token IDs, independent lexical research, morphology, semantic alternatives, evidence citations and contextual name-meaning proposals. Each target-language repository owns its original-source-aligned lexical and grammatical editorial decisions, output and separate tests, typography and release signoff.

A separate motor forked per language is **not** recommended. The engine is kept as a versioned importable Python package inside OLT first; a future extraction to OLT-Core is optional and must preserve versioned interfaces, not rewrite different engines.

### Original language -> neutral source evidence -> locale choices

- Hebrew OT (original-source Hebrew, language code hbo); recognize Biblical Aramaic (arc) in relevant OT passages; Greek NT (grc), Robinson–Pierpont RP2018 only once the source is legitimately pinned and imported.
- The source/core layer never uses an English translation or English surface token as original-language evidence or the intermediate source for a non-English locale.
- An **English master lexicon** exists as a shared, readable, source-linked editorial REFERENCE. It records provisional candidates, owner word family locks, evidence, exceptions and status. It may guide research or propose a comparison; it is not automatically the Japanese/Amharic/Icelandic/Chinese lexicon.
- Hebrew/Greek source token IDs, morphology, disambiguated senses, original-language syntax, token-to-verse alignments, edition/commit provenance and semantic evidence are carried into all locale tasks.
- Each locale has **its own** mapping for equivalent lexical choices, sense disambiguation, inflection, word order, phonology/transliteration, punctuation, typography, culturally appropriate names, and translated underword explanations. All source-linked choices must be independently checked.

### Source facts vs user-approved OLT theology

OLT's theological positions (including the binding binitarian framework, eternal uncreated Son and exact interpretive underwords) are explicit **owner editorial policy**, not dictionary meaning in the shared neutral source corpus. The neutral core can expose the owner's editorial suggestions and citations without transforming them into lexical facts. A future language repo may select the OLT editorial tradition deliberately, keeping the theological labels and any dissenting lexicographical evidence, rather than silently treating it as the original language.

Name examples:
- The owner selected God / Mighty Governance for actual Hebrew Elohim. This English underword is an interpretive research label and not a proven literal Hebrew derivation; a different locale must create **its own local wording**, if selected at all, based on the original lemma/context and explicit editorial choice.
- Noah / Rest concerns the Hebrew nuach association. Genesis 5:29 uses separate nacham/comfort wordplay; never merge distinct roots.
- Moses / Draw is an Exodus 2:10 naming wordplay rather than a securely settled historical derivation.
- El Shaddai / My Mighty Strength contains a proposed My which **does not appear in the Hebrew source**. It is not a literal certified target gloss.
- The exact owner Gen 1:1 English text, [of His Power] supplementary note, and exceptional interpretive In / with vertical link remain unchanged, as do bara/shape, asah/make, raqia/firmament, waw/and and the wayyiqtol English SIMPLE PAST editorial rule. Other target languages must analyze verb forms in their own grammar rather than copy English tense labels mechanically.

## Deliverable design (first version)

| Component | Repository path | Present capability |
|---|---|---|
| Authoritative shared architecture | data/engine/olt_034_architecture.json | Binding architecture, source priorities, release gates |
| Reusable Python code | olt_core/engine.py | Strict original-source/locale contracts; source-token-linked research packets |
| Core API | olt_core/__init__.py | Version 0.1.0 / packet contract 1.0 |
| Read-only CLI | olt_core/cli.py | Seven true Genesis 1:1 Hebrew tokens per selected locale, no fabricated translation |
| English master reference manifest | lexicon/english_master_manifest.json | Points to existing original-linked lexical candidates/owner locks; not a complete English Bible lexicon |
| Owner name-underwords | lexicon/name_underwords.json | Ten research-only name/meaning records |
| Target-language profiles | locales/{en,am,ja,is,zh-Hans,zh-Hant}.json | Six empty distinct language configurations, separate source-first decisions |
| CI tests | tests/test_olt_034_multilingual_core.py | Positive and negative original-lemma/locale/release assertions |
| GitHub workflow | .github/workflows/olt-034.yml | Ubuntu read-only source research verification; foundation remains required |

Example: run Python standard library command:

    python -m olt_core.cli --locale ja --pretty

Result is **JSON research evidence**, not a Japanese Bible translation. All seven real Gen 1:1 Hebrew word IDs, original spellings, lemma values and OSHB raw morphology tags are kept. English research choices are separately labeled NONAUTHORITATIVE_EDITORIAL_REFERENCE. The Elohim/God example has a separate unapproved owner name-meaning proposal Mighty Governance, with a null target-language underword until explicitly translated and reviewed by the target-language team.

Amharic (am/Ethi), Japanese (ja/Jpan), Icelandic (is/Latn) and Chinese (zh-Hans and zh-Hant) are **registered but contain zero target-language Scripture words**. Their external GitHub repositories are **future proposals**, not claimed to exist.

### Interface constraints / safety boundaries

1. Source word is keyed by original edition, book/verse and exact original token ID, with raw morphology and lemma identity. A target choice must repeat the source verse/token/lemma/script identity and target-language tag; a plain English string is not an acceptable join key.
2. Preserve text-edition provenance and licensing. The current OT research data has source-tagged morphology **not independently signed off**; RP2018 Greek is not pinned/imported. Do not fabricate Greek source token references or silently substitute another NT edition.
3. Imported morphology is not the same as independent verified parsing; the builder exposes that status and always marks its output BLOCKED.
4. A source-aligned locale draft is still only UNREVIEWED_LOCALE_DRAFT. No automatic publishing, no silent underword translation, no global string substitution, and no translation through English.
5. Where original-language morphology cannot be expressed one-to-one, a locale may restructure syntax while preserving explicit alignment and documenting departures. Wayyiqtol -> English simple past is an **English editorial lock**, not a universal target-language tense feature.
6. Locale scripts/fonts, non-Western word segmentation, RTL original-language display, CJK wrapping and Amharic line breaking, accessibility, notes and A4/PDF/ODT QA all require independent implementation and review.
7. Each language repository should pin a released OLT core version and an immutable corpus/lexicon snapshot by hash/commit, preserve the original source attribution, and run its own source-provenance and language-specific CI. Do not live-fetch mutable main as a release dependency.
8. External repositories can consume the source package/JSON output but are NOT needed to pass the foundation's present prototype tests.

## Planned follow-up sequence

- **OLT-035:** Build a fully provenance-pinned original OT/NT source normalization/adapter framework, retaining Hebrew/Aramaic/Greek edition hashes and licenses; Greek NT is a true independent source-import project.
- **OLT-036:** Generate a source-keyed, complete **English master reference ledger**, with owner-approved English choices kept separate from provisional Genesis/OT research. Do not announce completeness early.
- **OLT-037:** Implement reusable locale sense-selection and verse-alignment schemas plus localized name/underword renderer, with CJK/Ethiopic/Latin script-specific PDF and ODT QA tests.
- **OLT-038:** Once an actual target locale is chosen, create its separate repository template and pin an OLT package tag/revision. No speculative code duplication or broad unreviewed translations.
- **OLT-039 and beyond:** Full biblical inventory, independent linguistics and publication reviews for every locale.

**Explicitly NOT delivered by OLT-034:** a full Hebrew/Greek-to-English Bible lexicon, any automatically translated complete book/NT, independent Hebrew/Greek or locale philological certification, a published multilingual Bible, new target-language GitHub repos, or final A4 PDF/ODT. All release gates remain BLOCKED.
