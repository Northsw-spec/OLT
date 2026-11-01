# DANMEK-029 — Systematic English clause-role audit

**Status:** Implemented private review utility. Validation requires GitHub Actions; running the genuine private CHES corpus on GitHub is prohibited.

**Program:** scripts/danmek_029_private_english_clause_review.py

## Binding purpose

DANMEK-029 adds a **read-only, English-only, verse-by-verse classification** of candidate post-verbal noun phrases. It does not change the CHES original or any locked/approved DANMEK-013/014 reading, and does not change or regenerate DANMEK-028 snapshots.

The owner requires the noun subject to precede its associated pronoun–verb expression in the English view, including multiple clauses in the same verse. A *possible subject* must not be confused with a *possible direct object*. CHES is the accepted authority for English lexical correspondence; no routine translation comparison to Hebrew/Aramaic or OSHB/WLC is performed.

## What the classifier actually records

Every imported English verse is inspected, not just the 311 historically flagged English regex ambiguities. A bounded English tokenizer locates possible pronoun–verb expressions followed immediately by a capitalized or article-marked noun phrase. Its three **review categories** are:

| Review status | Meaning | Automated action |
|---|---|---|
| BOUNDED_ENGLISH_SUBJECT_PATTERN_CANDIDATE | A constrained, already tested DANMEK-028 English pattern is compatible with the owner’s subject-first editorial convention; includes some passives, intransitives and the expressly requested multi-clause hearing/report construction | Report only; do not apply in 029 |
| TRANSITIVE_OBJECT_RISK_UNRESOLVED | The verbal head can take a direct object, so the following noun might not be the subject; examples in synthetic tests include “he-saw Sailors”, “he-is-making Worker” | Preserve order, flag private review |
| ENGLISH_ROLE_UNRESOLVED_NO_REORDER | A candidate post-verbal noun exists but the current English evidence does not justify either a bounded subject assumption or a transitive object-risk cue | Preserve order, flag private review |

These statuses are **not** a machine-verified grammatical analysis, and **none** proves subjecthood/objecthood. Parsing and English context may remain ambiguous. Absence of a match **never** certifies that a verse is correct, and a parser finding is not a translation defect. This stage does **not** make the full English grammar review complete.

## Historical 311-case review and old reader

The 311 cases previously found by DANMEK-020/022 are English typography ambiguities, not verified translation or grammar errors. Their occurrence is independently counted against the exact existing owner-reader snapshot and may be enforced with --require-311; all old ambiguous verses appear in the optional private report even when they have no detected noun pair.

The 029 program also calls the guarded DANMEK-028 presentation **in memory only**, and records whether an older DANMEK-011 reorder was withheld, and how many bounded v2 moves are observed. It does not write either existing reader, does not mark those moves editorially correct, and never uses an original-language comparison.

## Local private execution

From the existing working repository on Parrot:

    cd "$HOME/OLT-CHES-tools"
    git pull --ff-only origin main
    "$HOME/.local/share/olt-ches-venv/bin/python" \
      -m scripts.danmek_029_private_english_clause_review \
      --private-root "$HOME/.olt-private/ches" \
      --confirm-machine-readable-use-permission \
      --require-311 \
      --audit-only

The default produces **no files**, only anonymized count/flag metadata in stdout. In this command, --require-311 is intended for the owner's historical 311-case private archive and fails closed if the data has drifted. For intentionally incomplete *test* archives, omit the flag.

To produce a **separately private** JSON and offline HTML side-by-side review, replace --audit-only with --write-private-report. Reports contain actual CHES-derived English only inside:

    ~/.olt-private/ches-clause-review/

This folder uses 0700; files use 0600, content-hash identities, no overwrite, escaped HTML, no scripts/network/forms, and publication remains blocked. The CLI never prints private text, verse references or local file paths.

## Evidence and next engineering phase

GitHub Actions executes synthetic English fixtures, not the actual private CHES corpus. Its PASS proves tool behavior in those tests, **not** accurate sentence parsing or complete 311-case review.

DANMEK-030 can use the resulting *private evidence* to prioritize more defensible grammatical recognizers. Add new transformations only with stable syntactic evidence and regression tests protecting direct objects, clause boundaries, early-modern/poetic English, reader immutability and the owner's subject-first convention. Preserve NO_CHANGE for unresolved roles.

**No Hebrew comparison. No automatic edit or grammar certification. Publication BLOCKED.**
