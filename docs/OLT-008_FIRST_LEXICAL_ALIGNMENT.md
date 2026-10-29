# OLT-008 — First original-token-aligned English lexical research

## Genesis 1:1: seven original source tokens, one verse proposal
The script maps each of seven actual source word tokens to its exact
original Hebrew form, OSHB token ID, original raw lemma and morphological tag.
This is the first *provisional* English lexical translation candidate generated
in the clean project, not a recycled older translation draft.

Main proposed English line:
> In the Beginning God — He shaped the Heavens and the Earth.

An optional explicitly **interpretive**, not literal variant is recorded:
> In the Beginning [of His Power] God — He shaped the Heavens and the Earth.

The phrase `[of His Power]` does not correspond to an independent word in
Genesis 1:1. A comparison with Gen 49:3/Deut 21:17 is a research proposition;
it does not turn `reshit` into a lexical word meaning 'power'.

## Why a seven-word alignment matters
- The actual verb `בָּרָא` (`1254 a`) is source-tagged
  `HVqp3ms` — **Qal qatal 3ms, NOT wayyiqtol**. The owner-lock
  yields `shaped`; the OLT wayyiqtol simple-past mandate does not by itself
  govern this verb.
- The original Hebrew order has the finite verb before the subject
  `אֱלֹהִים`. OLT's mandatory explicit `God — He shaped` rendering is a
  documented syntactic reordering, exposing the source verb's 3ms person.
- Both direct object markers `אֵת` remain accounted for in the aligned
  ledger, even though they have no separate English gloss.
- `וְאֵת` is conjunction `and` plus object marker; its prefix is
  not a standalone Hebrew dictionary lemma.
- The article in English `In the Beginning` is idiomatic; the first
  Hebrew phrase has no written definite article. Whether it begins a
  temporal dependent clause has a genuine scholarly dispute.
- `[of His Power]` is **explicitly unaligned** to any source token and
  retained only in the optional intertextual candidate.

## Research
- OSHB pinned WLC original source token data in `data/quality/genesis_01_source_review_dossier.json`.
- [unfoldingWord Hebrew grammar: object marker](https://uhg.readthedocs.io/en/latest/particle_direct_object_marker.html)
- [Cambridge peer-reviewed abstract on Genesis 1:1 reading traditions](https://www.repository.cam.ac.uk/items/bce448c5-e43e-416d-89da-5876ead16bc3)
- [Gerhard Hasel, discussion of Gen 1:1 temporal syntax](https://translation.bible/wp-content/uploads/2024/06/hasel-1971-recent-translations-of-genesis-1-1-a-critical-look.pdf)

## Remaining research work across Genesis 1
The companion `data/research/genesis_01_97_lemma_review_queue.json`
contains all 97 distinct actual source lemma keys, prioritized by
frequency and including original word IDs, source dictionary links,
and review-state fields. **94 English word families still require
independent research and user approval**. The owner-locked `bara`,
`asah`, and `raqia` families remain locked; conjunctional `waw`
is a source prefix and is not fabricated as a numeric lemma.

**Neither this proposal nor automatic tests authorize chapter publication.**
