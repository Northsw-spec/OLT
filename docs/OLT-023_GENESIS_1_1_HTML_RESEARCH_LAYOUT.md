# OLT-023 — Genesis 1:1 source-derived styled HTML RESEARCH layout

## Scope

This checkpoint adds an **unapproved, single-verse HTML typography proof** for the existing OLT-018 and OLT-022 decisions. It does not create a new translation, approve Hebrew grammar, or publish Genesis 1.

- Original source: data/research/genesis_01_verse_01_alignment_proposal.json, with **seven original OSHB Genesis 1:1 word tokens**, Hebrew text and original source identifiers.
- Owner display policy: data/policy/olt_underword_overrides.json, with exactly **one** underword in Genesis 1:1, bound to source token 01xeN / Hebrew preposition בְּ.
- Main English stays **"In the Beginning [of His Power] God — He shaped the Heavens and the Earth."**
- HTML shows purple **In** directly above blue **with**, using a vertically stacked CSS layout; **with** remains the owner's binitarian canonical interpretation, **not** a certified Hebrew homonym, an independent Hebrew source word, or a proven instrumental reading in this verse.
- Both existing research footnotes remain anchored to their own spans. The supplied [of His Power] remains explicitly identified as theological editorial material absent from original Genesis 1:1.
- Pointed Hebrew is included right-to-left with separators removed **for display only**, not from the source data.
- A4-friendly CSS exists, but this is **not** final ODT/PDF, a certified page-bottom-footnote renderer, or a visually inspected publication.

## Generated file

genesis/GENESIS_01_01_RESEARCH_LAYOUT.html

To regenerate and verify locally (Python 3.12, standard library only):

    python scripts/render_genesis_1_1_html.py
    python -m unittest discover -s tests -p 'test_olt_023_html.py' -v
    python scripts/render_genesis_1_1_html.py --check

The --check mode fails if the committed HTML differs from freshly rendered canonical input. This prevents a hand-edited design from silently diverging from locked source or owner policy.

## Verification boundaries

Eight focused regression cases cover exact underword positioning and colors, seven source IDs, retained English, research notes, denied global substitution, denied false homonym/lexical signoff, and denied publication status.

A local run against a representative fixture exercised these tests; GitHub Actions against the repository remain **UNVERIFIED until a hosted runner executes**. See [OLT-CI-001](https://github.com/Northsw-spec/OLT/issues/7) for the pre-step runner failures. A future CI PASS validates deterministic code/data behavior only, not independent Hebrew philology or visual print QA.

## Remaining gates

Independent expert review of morphology and lexical interpretation; owner editorial approvals for outstanding Genesis English proposals; manuscript line-breaking and real page-bottom notes; visual inspection of actual A4 ODT/PDF; explicit final publication authorization. All remain **BLOCKED**.
