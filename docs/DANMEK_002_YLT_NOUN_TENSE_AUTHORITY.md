# DANMEK-002 — YLT governs noun and tense editing (1898 edition)

**Binding owner decision, 2026-10-31:** CHES remains the **direct default English text**, loaded from already imported private `.json` chapter files. Whenever DanMek applies an **English tense change or replacement of an excessively modern CHES noun**, **Young's Literal Translation (YLT, 1898)** is the contextual decision authority. No new independent Hebrew lemma dictionary, no general word-sense selector, and no re-generation of CHES are necessary.

Example: **`portal → door` only where the matching YLT verse actually uses the English word `door`**. If that YLT verse instead uses `gate`, an automatic `door` substitution is NOT supported by YLT and the original CHES reading is retained. The same per-verse rule applies to tense: never blindly replace `said` with `saith` across a whole corpus. The first explicit candidate set is deliberately small: `portal → door`, `portals → doors` (nouns) and `says → saith`, `said → saith` (tense).

## Actual lightweight implementation

The existing `scripts.ches_015_direct_private_reader` now supports an **optional** YLT-guided overlay. It first validates the original CHES JSON as before and then compares **only the same printed chapter/verse**, using YLT 1898 from a pinned, public-domain JSON edition. It applies a candidate replacement only if there is exactly **one CHES old-form occurrence, exactly one YLT proposed target occurrence, and no YLT old form**, and no other eligible candidate change in that verse. Otherwise the CHES text is left unchanged, and an ambiguity or unmapped verse is counted. This is a conservative contextual text check, **not** claimed Hebrew-token-to-English-word alignment.

The primary Nehemiah 7 source PDF prints a special 72/73 alternative verse-numbering scheme. No CHES↔YLT verse crosswalk is established for this chapter, so **all Nehemiah 7 corrections are skipped** rather than guessed. Unknown book IDs/verse numbers are likewise left unchanged.

The original private `~/.olt-private/ches/*.json` bytes are **never modified**. YLT-guided HTML output is a **separate immutable, SHA-derived private snapshot** from the unmodified CHES reader; existing different files cannot be overwritten. YLT source and CHES English text are never printed in GitHub Actions logs or CLI summary. The private output explicitly discloses that these are YLT-guided editorial changes, not a certified full Hebrew-word alignment.

## Getting public-domain YLT locally

The 1898 Robert Young translation is identified as **public domain** by [eBible.org](https://ebible.org/Bible/details.php?id=engylt). For a small, deterministic JSON loader, this checkpoint pins an independent JSON transcription by exact Git commit `847ee02ed0d2ee19cad3c474b96d757287c3dc0a` and exact Git blob SHA-1 `d98d6b775ae3f95e3e28790c324bbe65c55946ef`. The [source project](https://github.com/malexander-ogletree/ScriptureDesk) credits its underlying 1898 YLT text to a public-domain transcription; code uses only the Bible text and no external application code. If the file changes, the SHA pin fails instead of silently upgrading YLT. This older historic YLT edition is **not** an assertion that all YLT electronic editions have identical punctuation.

The one-time YLT download is **explicit**, with normal verified HTTPS and exact source hash validation, and stores data under `.olt-private/ylt-public-domain/` (not public Git). All subsequent rendering is **offline**.

```bash
cd ~/OLT-CHES-tools
git pull --ff-only

# One-time public-domain YLT download, hash-pinned; CHES not uploaded.
~/.local/share/olt-ches-venv/bin/python \
  -m scripts.danmek_ylt \
  --private-root "$HOME/.olt-private/ches" \
  --prepare-private-ylt

# Build a separate private YLT-guided DanMek reading snapshot.
~/.local/share/olt-ches-venv/bin/python \
  -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority
```

To reproduce the original CHES-only reading snapshot, omit `--use-ylt-authority`. `--audit-only --use-ylt-authority` computes metadata-only counts without HTML writes.

## Quality and rights status

- Source-YLT spelling, article, tense and English word choice are evidence for a **specific English verse comparison**, not an original Hebrew morphological certificate.
- The existing owner wayyiqtol/simple-past rule and some YLT source tense expressions (e.g., archaic historic present `saith`) can conflict. This layer implements the owner's **latest YLT-contextual preference for its bounded private editorial candidates** without rewriting verified original morphology or claiming the old global tense policy has been exhaustively harmonized. Such conflicts remain reviewable.
- These initial noun/tense candidates do **not** mean every biblical English tense form or noun is automatically corrected. New candidate mappings require an explicit, testable policy; unknown cases keep CHES original.
- Source edition pins and the operator-provided permission to use CHES do not establish new permissions to publicly redistribute the CHES-derived edition. All original CHES text and generated working output remain private; publication stays `BLOCKED` pending rights. YLT 1898 itself is public domain.
- The 929-chapter CHES OT source archive is still not independently known to have completed on the operator's local computer. The Greek New Testament remains outside the CHES OT workflow.

**Engineering validation:** GitHub Actions regression tests use **invented** CHES/YLT sentences, and a dedicated ephemeral real-source test verifies only the pinned public-domain YLT edition/structure, with no CHES English or YLT verse text in logs.
