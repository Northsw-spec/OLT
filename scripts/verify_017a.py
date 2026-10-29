#!/usr/bin/env python3
"""Validate OLT-017A research provenance, source lemma anchors and limits."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"data/research/olt_017a_scholarly_wave.json").read_text())
queue=json.loads((ROOT/"data/research/genesis_01_lexeme_editorial_queue.json").read_text())
qids={x["source_lemma_id"] for x in queue["entries"]}
assert data["publication_status"]=="BLOCKED"
assert data["new_english_family_approvals"]==0
assert data["approved_homonym_links"]==0
assert data["homonym_layout"]=="UNDER_ENGLISH_WORD"
assert not data["independent_philological_signoff"]
assert len(data["cases"])==5
assert len({x["id"] for x in data["cases"]})==5
for x in data["cases"]:
    assert x["source_lemma"] in qids, x["source_lemma"]
    assert x["id"].startswith("OLT-017A-")
    assert x["sources"] and all(y["url"].startswith("https://") for y in x["sources"])
    assert all(y["evidence"] in {"PUBLISHER_ABSTRACT","JOURNAL_ABSTRACT",
                                   "PUBLISHED_ARTICLE_EXCERPT","TRANSLATOR_NOTE",
                                   "MORPHOLOGY_DISPLAY"} for y in x["sources"])
    assert len(x["competing_analyses"])>=2
    assert x["research_decision"] and x["christological"]
print("PASS: source-backed disputable lexical research only, no English approval")
