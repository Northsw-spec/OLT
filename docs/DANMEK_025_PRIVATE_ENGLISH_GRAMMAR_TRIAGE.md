# DANMEK-025 — English-only private grammatical-error review

**Implementation:** scripts/danmek_025_private_english_grammar.py  
**Owner decisions:** DANMEK-024 (preserve poetic, Hebraic English) and DANMEK-026 (CHES is the accepted authoritative English source).  
**Status:** Implemented as a separately opt-in, read-only review utility. Real private CHES execution **NOT YET OBSERVED** by GitHub Actions.

## Intent

DANMEK-025 does **not** verify CHES English against imported Hebrew/Aramaic
words. That earlier research is no longer part of the required DANMEK workflow.
The current CHES-derived English reading remains the owner-approved reference.
Do not try to make unusual English idiomatic or modern. Keep archaic, poetic
and Hebrew-like syntax whenever grammatically defensible and comprehensible.

This tool inspects the English fragments **as displayed** by the existing
owner-approved DANMEK-013/014 presentation options, without altering the
source JSON or reader HTML. It reidentifies the historical 311 English
ambiguity patterns strictly from their English pattern signals, and scans
every verse for one intentionally narrow type of suspected grammatical error.

## Current bounded candidate rule

The first detector recognizes explicit subject pronouns followed immediately
by a finite form of English "be" that disagrees with that pronoun, such as
synthetic **"He are walking" → "He is walking"** and
**"Thou is resting" → "Thou art resting"**.

- This detector does not invert subject/object positions, paraphrase, update
  morphology, infer Hebrew word alignments or move any words. It proposes
  only a replacement for the observed finite English verb token.
- Archaic correct English such as "thou art", deliberate fronting such as
  "And the lantern — the worker saw", and ambiguous original-style glosses
  remain unchanged.
- Its rule match is a **candidate**, not proof that a verse is incorrect.
  Subjunctive, ellipsis, poetic/dialectal usage, semantic context and
  typography may require expert review. Proposals are never automatically
  accepted or applied.
- All 311 pattern cases are represented in the optional private review
  even if no error rule matches. The status in that case is
  GRAMMAR_UNRESOLVED_NO_REORDER; **not** "correct" and **not** "translation
  error". Unflagged verses are never automatically grammar-certified.
- This is a useful, limited first grammar-detection pass, not an exhaustive
  grammatical parser or proof that the full English Old Testament is sound.

## Safety and actual use

From the Parrot working checkout of the public OLT GitHub repository,
after merging the PR:

    cd "$HOME/OLT-CHES-tools"
    git pull --ff-only origin main
    "$HOME/.local/share/olt-ches-venv/bin/python" \
      -m scripts.danmek_025_private_english_grammar \
      --private-root "$HOME/.olt-private/ches" \
      --confirm-machine-readable-use-permission \
      --require-311

The default command writes **zero** files and reports only numerical
aggregates and fixed status codes. It validates the entire existing private
CHES archive and the owner-accepted reader snapshot twice, so a changed
archive is rejected. The optional **--require-311** flag refuses unexpected
ambiguity count drift; omit only for intentionally incomplete synthetic tests.

To generate a private, immutable **side-by-side JSON and static HTML review**,
run the same command with **--write-private-report**. These files contain
private source-derived English and remain **only** in:

    ~/.olt-private/ches-grammar-review/

The folder and reports use restrictive permissions (0700 and 0600).
Output names are derived from the review JSON SHA-256. A differing existing
file is never replaced. HTML escapes source text and disallows scripts,
network resources and forms via a restrictive Content Security Policy.

**Never upload the private report, CHES text, local source path or screen
content to public GitHub/Actions**. CI uses invented English fixtures only.
No text fragments, verse references or file paths appear in terminal output.

## What is deliberately absent

No original Hebrew/Aramaic token loading, OSHB book crosswalk, morph parsing,
automatic English->Hebrew alignment or CHES error audit is performed. There
is no network access, no writing to any CHES source chapter, no mutation of
the locked owner-verified DANMEK-013/014 HTML, no apply-mode, and no
public redistribution authorization.

This tool's success can certify **engineering behavior only**. It cannot
certify the true grammatical validity of all verses, the accuracy or
infallibility of CHES, an approved final OLT translation or publication rights.

**Next editorial action:** examine only the reported private candidate
corrections and unresolved cases, justify any real English error using
English grammar, and obtain the owner's explicit acceptance before building
a **separately versioned, never-overwriting** revised private reader.
No source-language re-verification is required for this DANMEK grammar scope.

**Publication: BLOCKED.**
