# OLT-005 — Genesis 1 token-by-token research ledger

This checkpoint **does not reuse any old English translation**. It uses the
full source-derived `data/quality/genesis_01_morphology.json` and the
newly checked XML `verified_id_crosswalk.jsonl` to produce the first
source-backed 434-token review ledger.

Each word records original pointed form, source lemma, morphology code,
all exact lemma identifiers, prefix-only components, registered BDB/Strong
references, and the initial style decision if that lemma has an owner lock.
All nonapproved English choices remain `null`, not guessed.

The ledger also lists every distinct Genesis 1 lemma, ranked by frequency,
with a research queue, homonym/typology review field and the exact original
word-token IDs in which it occurs. Each source-tagged wayyiqtol is flagged,
but the editor's English simple-past requirement is tested only once a real
English verb has been aligned to the source.

Genesis 1 remains `SOURCE_CROSSWALKED_ENGLISH_NOT_INDEPENDENTLY_REVIEWED`;
no ODT/PDF publication or lexical final signoff exists yet.
