# OLT-007 — Full structured BDB lexical evidence (no unapproved translations)

The first lexicon import was deliberately conservative: it extracted top-level
dictionary metadata, leaving `<sense>`, `<ref>` and other nested BDB nodes
unrepresented. An accurate Hebrew Master Lexicon must not silently flatten or
erase such source structure.

This checkpoint loads `BrownDriverBriggs.xml` at the pinned
`HebrewLexicon` revision `21c9add13bc727d3a951361778e97e3ff7afd1ce`
and preserves each original dictionary entry's full node tree (including tag,
attributes, text, tail, child order and nested senses). Original BDB content
and edited digital markup have different attribution conditions; see
`sources/REGISTRY.md`.

The full XML-structured resource is stored deterministically as
`data/imported/lexicon/bdb_nested.jsonl.gz`. Source checksum, archive
checksum, node and entry totals appear in
`data/quality/bdb_nested_manifest.json`.

The 97 Genesis 1 research cards are now supplemented by
`data/quality/genesis_01_bdb_sense_evidence.json`, which carries exact source
dictionary structures, real BDB IDs and still **zero newly approved English
meanings**. The `bara`, `asah`, `raqia` owner locks remain separate from
lexical research; a dictionary entry is not permission to change them.

CI verifies coverage and the continued **release-blocked** status, not the
philological accuracy or final English translation.
