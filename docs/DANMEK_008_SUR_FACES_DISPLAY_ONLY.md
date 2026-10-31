# DANMEK-008 — Display-only `sur faces` → `faces` in private OLT English

**Binding owner request (2026-10-31):** For the English word that the owner describes as CHES's `pnei` reading, the visible CHES gloss `sur faces` is unnecessarily awkward in OLT. **Display `faces`** instead, without rewriting the actual CHES JSON or implying that the source gloss was wrong.

## Precise supported behavior

The original 929 private CHES chapter JSON files remain immutable and are still shown unchanged in the default **source-faithful CHES reader**. An explicit `--olt-display-faces` flag creates a **different private, versioned OLT English display snapshot**:

- In a single PDF text fragment, the complete exact word sequence `sur faces` becomes `faces` (case preserved at the start: `Sur faces` → `Faces`).
- When consecutive CHES source PDF text fragments **in the same verse** consist of an entire `sur` fragment and an entire `faces` fragment, suppress the former **in the derived HTML only**; keep `faces` visible and keep both source fragments unchanged in the JSON.
- Only explicitly matching English forms are considered. Never remove `sur` by itself, change `surfaces` (one word), operate across an intervening fragment or verse boundary, or touch real `the` articles and `c` morphology markers.
- This is a small owner-selected **English presentation convention**, not a claim that a Hebrew lemma-to-CHES fragment correspondence has been formally verified for each case. The exact source display phrase and local structure are sufficient to *display* the requested simpler English; any uncertain nonmatching source segmentation remains unchanged.

The revision `DANMEK-008-SUR-FACES-DISPLAY-ONLY-v1` is included in the SHA-derived snapshot ID **only when this flag is enabled**. Preexisting source-faithful and YLT-only snapshot IDs and bytes remain unchanged. The original CHES corpus and PDF source are never updated.

## Usage: private local OLT display with existing YLT 1898 option

```bash
cd "$HOME/OLT-CHES-tools"
git pull --ff-only origin main
"$HOME/.local/share/olt-ches-venv/bin/python" -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader \
  --use-ylt-authority \
  --olt-display-faces
```

This command writes a distinct `~/.olt-private/ches-direct-reader/snapshot-*/` with `index.html`; it prints **sanitized counts only**, including `olt_display_sur_faces_to_faces_count`, not third-party CHES verses or source texts. No new PDF or public-domain YLT download is required if the original files already exist.

## Unrelated decisions remain fixed

The later **DANMEK-007** owner reversal is permanent: no divine-referent-based `He/Him/His` capitalization. This display simplification has nothing to do with pronouns, gender, reverential typography or the still separately planned source-anchored subject-before-verb OLT English order. Full Hebrew lexical alignment and publication permission are not certified; `publication_status=BLOCKED` remains intact. All tests use artificial/synthetic fragments only.
