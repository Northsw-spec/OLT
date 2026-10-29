# OLT-006 – Unresolved source IDs and 97 Genesis 1 lexical research cards

**Status:** software/data audit, not philological publication.

## Why
The source-ID crosswalk resolves 9,252 of 9,519 observed numeric lemma
identifiers. 267 are missing an exact AugIndex match: 256 suffixed with `+`
and 11 others. A potential numeric-base match is a **research lead**, not
permission to erase suffixes or conflate homonyms.

## Output A: unresolved lexeme triage
`data/quality/unresolved_lexeme_triage.json` records each of the 267
source keys, verified source occurrence count, real word examples with
OSHB stable token IDs, a separate plus-marker flag, and (when present)
a potential *base-number source lookup* labeled not authoritative.
No '+' marker is silently stripped. All 267 remain for investigation
until primary-source documentation justifies an exact link.

## Output B: Genesis 1 dictionary study cards
`data/quality/genesis_01_dictionary_study_cards.json` has one research
card per exactly observed Genesis 1 lemma (97), containing:
source text forms, verse/token IDs, occurrence counts, actual verified
Lexical Index identifiers, real Strong and BDB target IDs and original
dictionary source fields where available. Missing or malformed dictionary
IDs raise an error; no ungrounded dictionary translations are inserted.

Owner locks apply to `1254 a` (bara → shape), `6213 a`
(asah → make) and `7549` (raqia → firmament) **as English word
families only**. The separate conjunctional waw → and lock is a
grammatical prefix decision, not a fabricated numeric lemma.

The cards are a ready-to-review research queue, not 97 approved
English renderings. Each card's morphology, homonymy, literary links,
English readability, English word alignment and Christian typology
remain review tasks until separately checked.
