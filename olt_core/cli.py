"""Read-only OLT-034 original-source research packet CLI.

python -m olt_core.cli --locale ja
Output is evidence-bound JSON, NOT a finished translation of the Bible.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from .engine import build_genesis_1_1_research_packets

ROOT = Path(__file__).resolve().parents[1]
LOCALES = {"en", "am", "ja", "is", "zh-Hans", "zh-Hant"}

def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def main():
    p = argparse.ArgumentParser(description="Source-first OLT research packet generator; never publishable Scripture")
    p.add_argument("--locale", choices=sorted(LOCALES), required=True)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    records = build_genesis_1_1_research_packets(
        load("data/research/genesis_01_verse_01_alignment_proposal.json"),
        load("locales/" + args.locale + ".json"),
        load("lexicon/name_underwords.json"),
    )
    print(json.dumps(records, ensure_ascii=False, sort_keys=True,
                     indent=2 if args.pretty else None))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
