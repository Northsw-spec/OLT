# DanMek-001 — CHES decides contextual English readings (owner-directed)

**Priority:** Finish the smallest working offline English OT workflow first. DanMek is the working name for OLT's CHES-first English layer, **not** a new from-scratch Hebrew lexicon or a morphological word-generator project.

## Decisive lexical policy

For **each occurrence**, the English **reading printed in that chapter and verse of the privately authorized CHES source is the default choice** when several English senses of a Hebrew/Aramaic lemma are possible. DanMek does **not** run a second automatic sense selector, ask a user to adjudicate every polysemous lemma, pick a generic Strong's-dictionary first sense, or construct a bespoke lemma-to-sense lexicon.

Pipeline:

1. Read the existing **private** original CHES chapter JSON; validate its provenance, printed verse markers and original English fragment sequence.
2. Render **the CHES contextual English source reading as printed**, retaining original fragments and the corresponding source verse reference; no word-order reorganization or invented missing verses.
3. **Optional later:** apply a small, explicitly described OLT exception (for example `shaped` instead of a particular occurrence of `created`, or English simple past for a securely linked original wayyiqtol). Such a modification requires an exact local occurrence and original-source evidence; never blindly replace every matching English word across the corpus.
4. If an English green PDF fragment cannot be unambiguously linked to a specific original-language token, **keep the CHES verse reading unchanged**. Do not infer a one-to-one source-word ↔ green-PDF-fragment relationship from proximity or count. No complicated alignment engine is a prerequisite to a usable private English reading edition.

The current 14 source-pinned OSHB-checked English draft path remains valid as *additional* evidence where available, but it is **not a prerequisite** to generating a private CHES-first reading for all imported OT chapters.

## Direct offline reader

`scripts.ches_015_direct_private_reader` uses the owner's previously imported local JSON files under `.olt-private/ches/`. It supports existing incomplete archives and creates a separate static private HTML reading snapshot. This implementation deliberately **does not alter any CHES English word**, nor claim a finished DanMek-modified translation.

```bash
cd ~/OLT-CHES-tools
git pull --ff-only

~/.local/share/olt-ches-venv/bin/python \
  -m scripts.ches_015_direct_private_reader \
  --private-root "$HOME/.olt-private/ches" \
  --confirm-machine-readable-use-permission \
  --build-private-reader
```

The generated HTML is stored locally under `$HOME/.olt-private/ches-direct-reader/snapshot-<hash>/index.html`. Outputs are user-private (directories 0700 and files 0600); source originals are never overwritten, and copyrighted CHES English content is never printed to CLI stdout, committed to Git, or uploaded to GitHub Actions artifacts.

The interpreter of the CHES PDF source is **not** the origin of a public-republication license. Neither formatting changes nor a large number of altered words automatically grants rights to republish a protected third-party translation. Owner-reported machine-readable-source permission and any public derivative/redistribution license are different questions; **publication remains BLOCKED** unless separately established.

## Completion target and separate quality questions

The engineering goal is **one offline command to read all 929 locally imported OT chapters**, count missing/malformed chapters, and present an unchanged English source reading. The actual private archive may be incomplete; a reader that renders 419 chapters must never claim all 929 completed.

This is **not** a word-by-word Hebrew DanMek sublinear yet; a true source-token-level sublinear requires independently justified alignment of every rendered word. Nor does it itself cover the Robinson–Pierpont Greek NT. Do not equate operational completion of the small private reader with an independently authored, fully edited, legally publishable 66-book OLT Bible.

**Next:** after the direct reader is CI-verified, add only a tiny optional and **source-anchored** private exception layer, leaving CHES's contextual reading unchanged by default. Do not revive the historical large lexical engine.
