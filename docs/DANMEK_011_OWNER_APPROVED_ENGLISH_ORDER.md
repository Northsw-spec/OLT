# DANMEK-011 — Owner-approved English-order proposals, applied in a private OLT reader

**Binding owner decision (2026-10-31):** The owner explicitly accepts **every subject-before-verb connection suggested by the DANMEK-010 English pattern detector** for the OLT English presentation. This **authorizes English editorial output**, not a factual statement that each detected pair is a verified Hebrew/Aramaic grammatical subject and verb. The owner previously discontinued reverential capitalization (DANMEK-007); that cancellation remains permanent.

## Implemented behavior

The opt-in `--olt-owner-approved-candidates` flag builds a **separate, immutable, private OLT reading snapshot** from the already present, strictly validated `~/.olt-private/ches/*.json` files. It uses the exact **shared** DANMEK-010 candidate detector, rather than reconstructing a second heuristic:

- **One candidate in a verse:** apply the owner's approved English editorial reorder to that exact CHES source phrase, placing the potential explicit subject before the verb phrase. Text remains private and is never placed in GitHub.
- **Several candidates in the same verse:** ambiguous; **do not move any** of them. Report the number of excluded ambiguous verses.
- **No detected candidate:** source order remains unchanged; report the number left as-is.
- **A competing YLT noun/tense edit in an affected span:** keep that YLT-edited English verse in its existing order; report the conflict. Do not invent a combined interpretation or abort an entire 929-chapter build for a localized conflict.
- **No capitalizing divine-referent pronouns:** e.g., synthetic `and·he-shaped` + `God` renders as `and God — he-shaped`, never `He-shaped` based on theology.
- **No source modifications:** the original private source JSON, original CHES-faithful HTML snapshots, separately source-reviewed DANMEK-009 manifests, and prior YLT/faces-only snapshot identifiers are untouched.

This mode **does not require individually approved entries** in `approved.json`, because the owner has now authorized every unique detector proposal as an **English stylistic choice**. It is **mutually exclusive** with DANMEK-009's separately `--olt-subject-first` **individually syntax-reviewed** rules. The latter remain available without alteration for high-assurance cases.

## Private operation on Parrot OS

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
PY="$HOME/.local/share/olt-ches-venv/bin/python"

# Count-only offline audit: no HTML written, no CHES text printed.
"$PY" -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --audit-only \
  --use-ylt-authority \
  --olt-display-faces \
  --olt-owner-approved-candidates

# Build a distinct private English snapshot from all present chapters.
"$PY" -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority \
  --olt-display-faces \
  --olt-owner-approved-candidates
```

YLT is optional; if the locally pinned public-domain YLT has not yet been installed, omit `--use-ylt-authority` from both commands. No new CHES download, modified source JSON, global English replacement table, or review manifest is required.

Look at the metadata fields:

- `olt_owner_approved_candidate_reorders_applied` — exact count of moved **English candidate phrases**, not certified Hebrew syntactic links.
- `olt_owner_candidate_ambiguous_verses_unchanged` — verses containing multiple candidate pairs, all left as they were.
- `olt_owner_candidate_ylt_conflicts_unchanged` — source-span conflicts with YLT overlays.
- `olt_owner_candidate_other_verses_unchanged` — verses not reordered (includes ambiguous/conflicting/no-candidate).
- `olt_owner_candidate_original_language_subject_verified` — deliberately **false**.
- `observed_chapter_count`, `observed_verse_count`, `snapshot_id`, `publication_status` — private corpus and snapshot identity; publication **BLOCKED**.

The private HTML is written under `~/.olt-private/ches-direct-reader/<snapshot_id>/index.html` (not GitHub). CLI output is metadata-only.

## DANMEK-012 targeted display repair

The subsequent owner's report exposed a joined-name shape not recognized by the
original English detector: a leading `and·he-shall-cut-off` followed
immediately by `Yahwehfrom·…`. The owner-approved mode now renders that
narrow form as `And Yahweh — he shall cut off from·…`, but it **does not**
infer a subject whenever a verse merely contains `And` and `Yahweh`.
The same private OLT mode suppresses a source fragment consisting of exactly
lowercase `c`. Old CHES and YLT readings remain untouched.
[Details](DANMEK_012_DISPLAY_JOINED_YAHWEH.md).

## Quality boundary and further accuracy work

A capitalized English fragment can be an **object, place name, title, or other expression**; a hyphenated pronoun-verb can have different grammar from what a regex suggests. Explicit owner approval means these candidate **editorial transformations** are authorized, not that all are faithful to the Hebrew syntax. An entire OT can be covered by the *reader* while only a subset of verses are *reordered*. Never call that 100% sentence-order correction or Hebrew syntax certification.

The next engineering step is to make exception rates and false-positive categories measurable **locally**, using real private review samples and independent Hebrew syntax evidence, so more than the current narrow candidate shapes can be handled without silently losing other clauses. GitHub Actions checks technical determinism, snapshot isolation, source immutability, ambiguity handling, YLT-conflict handling, HTML privacy, and no false release or grammatical certification. No real CHES text belongs in public Git or CI artifacts.

**Preserved rules:** CHES original JSON unchanged; DANMEK-007 no divine pronoun capitalization; OLT English first; OLT-TENSE-001 wayyiqtol as simple past only where original morphology justifies; publication remains BLOCKED.
