# OLT-031 — Genesis 1 source-lemma English variation review packet

Date: 30 October 2026. Status: **RESEARCH ONLY — PUBLICATION BLOCKED**.

## Purpose

Continue [OLT-017 independent lexical review](https://github.com/Northsw-spec/OLT/issues/6) without inventing English meanings or automatically classifying Hebrew homonyms. This checkpoint creates an exact-ID-linked review packet for the 42 out of 97 Genesis 1 original-source lemma IDs whose existing **unapproved** English research contains more than one distinct fragment.

The original canonical research input is `data/research/genesis_01_lexeme_editorial_queue.json` (OLT-016). Earlier scholarly research packets OLT-017A and OLT-017B are linked by their **exact source lemma ID**, not by spelling resemblance. Neither prior scholarly packet is a substitute for independently validating the morphological parse or selected lexical meaning.

## Corpus accounting

- **31 Genesis 1 verses, 434 original Hebrew word tokens**.
- **427** word tokens with a numeric lemma identifier; **7** original source tokens are nonnumeric grammar-only components. No extra Hebrew words are invented.
- **97** exact lemma IDs; **42** with multiple English research fragments and **55** with one fragment.
- **3** existing owner-locked English families, unchanged: bara = shape; asah = make; raqia = firmament.
- **94** remaining English lexical families have no new owner approval.
- **0** new English word approvals, **0** newly independently validated morphology annotations, **0** approved homonym links.

The 42 cases contain **322** source-token contexts, each preserving the original token ID, verse reference, pointed Hebrew spelling, imported OSHB morphology tag, and exact provisional English fragment. The packet also preserves observed Strong and BDB ID references and links to matching OLT-017A/B case identifiers where present.

## Initial review order — mechanical, not scholarly ranking

Cases sort by number of distinct exact English fragments, then number of source-token occurrences, then exact lemma ID. The first cases are:

| Exact original lemma | Distinct unapproved fragments | Source tokens | Important restriction |
|---|---:|---:|---|
| 1961 | 7 | 27 | Contains jussive, wayyiqtol and other verb forms; do not equate grammatical variation with polysemy |
| 3605 | 5 | 14 | Quantifier with grammatical prefixes and changing English syntax |
| 3117 | 5 | 11 | Day forms with articles, prepositions and number/phrase context |
| 7549 | 5 | 9 | Owner-locked **firmament** family; prepositions and articles are not independent semantic homonyms |
| 5775 | 5 | 6 | Bird-related forms requiring morphological and contextual review |

This is a **triage order**, not a judgment that these five are the hardest Hebrew lexemes or that every difference reflects different meanings. English uppercase/lowercase, conjunctions, articles and supplied English morphology can all produce distinct fragments with no lexical change.

## Machine-readable packet and reproduction

- `data/research/olt_031_lemma_variation_triage.json` — 42 auditable cases and their original-source contexts.
- `scripts/build_olt_031_variation_triage.py` — deterministic source-derived renderer, no external downloads or approval side effects.
- `tests/test_olt_031_variation_triage.py` — 12 positive and negative tests rejecting lost tokens, false approval, modified owner choices and other provenance changes.
- `.github/workflows/olt-031.yml` — read-only PR and push check with exact reproducibility.

To run the same verification:

    python -m unittest discover -s tests -p 'test_olt_031_variation_triage.py' -v
    python scripts/build_olt_031_variation_triage.py --check

A CI PASS means **the triage is deterministically traceable to the existing research source**. It does **not** mean the 42 distinctions have been classified, that 94 lexical choices have been reviewed, or that Genesis 1 can be published.

## Next independent scholarly gate

For each lemma, check Hebrew stem/form, inflection, preposition and syntactic role against independent philological evidence; review context-sensitive BDB senses and competing academic analyses. Record why a fragment is grammatical versus substantively semantic, **including uncertainty and negative findings**. Require owner approval for any proposed new English family and separate approval for truly verified homonym links. Retain OLT-022's unique In/with canonical interpretation without relabeling it as proven Hebrew homonymy.

**No new philological signoff or biblical publication authority is granted here.**
