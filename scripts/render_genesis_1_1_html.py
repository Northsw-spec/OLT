#!/usr/bin/env python3
"""OLT-023: deterministic, unapproved Genesis 1:1 styled HTML research proof.

Uses the exact OLT-018 verse proposal and OLT-022 owner-selected underword
policy, not a newly translated or independently reviewed source.
"""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
VERSE = ROOT / "data/research/genesis_01_verse_01_alignment_proposal.json"
POLICY = ROOT / "data/policy/olt_underword_overrides.json"
OUTPUT = ROOT / "genesis/GENESIS_01_01_RESEARCH_LAYOUT.html"
MAIN = "In the Beginning [of His Power] God — He shaped the Heavens and the Earth."
SOURCE_IDS = ("01xeN", "01Nvk", "01TyA", "01vuQ", "01TSc", "01k5P", "01nPh")


def build_html(verse: dict, policy: dict) -> str:
    """Fail closed on provenance, locked wording, underword scope or note status."""
    if (verse.get("reference"), verse.get("publication_status"),
        verse.get("independent_scholarly_review"), verse.get("main_english_proposal")) != (
            "Gen.1.1", "BLOCKED", "NOT_DONE", MAIN):
        raise ValueError("Unapproved Genesis 1:1 source or changed English main line")
    words = verse.get("source_alignment", [])
    if verse.get("source_token_count") != 7 or tuple(w.get("source_token_id") for w in words) != SOURCE_IDS:
        raise ValueError("Original seven Genesis 1:1 source tokens changed")
    if tuple(verse.get("original_hebrew_token_sequence", [])) != tuple(w.get("pointed_hebrew") for w in words):
        raise ValueError("Original Hebrew token spelling and source alignment differ")
    w0 = words[0]
    if (w0.get("source_raw_lemma"), w0.get("source_morphology"), w0.get("pointed_hebrew"),
        w0.get("proposed_english_surface")) != ("b/7225", "HR/Ncfsa", "בְּ/רֵאשִׁ֖ית", "In the Beginning"):
        raise ValueError("The original Hebrew bet source anchor changed")
    if policy.get("policy_id") != "OLT-022" or policy.get("publication_status") != "BLOCKED" or (
        policy.get("scope"), policy.get("automatically_generalize_to_other_bet")) != (
            "ONE_EXCEPTION_GENESIS_1_1_ONLY", False):
        raise ValueError("Unapproved or globally applied underword policy")
    underwords = policy.get("underwords")
    if not isinstance(underwords, list) or len(underwords) != 1:
        raise ValueError("Exactly one underword is required")
    u = underwords[0]
    if (u.get("reference"), u.get("source_token_id"), u.get("source_ordinal"),
        u.get("primary_english"), u.get("secondary_english"), u.get("placement"),
        u.get("interpretation_label")) != (
            "Gen.1.1", "01xeN", 1, "In", "with", "DIRECTLY_BELOW_ENGLISH_WORD",
            "BINITARIAN_CANONICAL_INTERPRETATION"):
        raise ValueError("Genesis 1:1 In / with source-to-display mapping changed")
    if any(u.get(k) is not False for k in (
        "this_verse_instrumental_bet_independently_established", "underword_is_verified_homonym",
        "source_lexeme_means_jesus")) or u.get("owner_selected_display") is not True:
        raise ValueError("Underword erroneously claimed as verified lexical fact")
    primary_color, secondary_color = u.get("primary_word_color"), u.get("secondary_word_color")
    if (primary_color, secondary_color) != ("#5B277D", "#2463A6"):
        raise ValueError("Owner-locked primary/underword colors changed")
    if u.get("english_main_verse_remains") != MAIN:
        raise ValueError("Underword policy main verse diverges from original")
    unote = u.get("footnote", {})
    if (unote.get("id"), unote.get("anchor"), unote.get("status")) != (
        "gen-1-1-bet-with", "with", "OWNER_INTERPRETIVE_LINK_NOT_PHILOLOGICALLY_APPROVED"):
        raise ValueError("Missing or silently approved underword interpretive note")
    footnotes = [n for n in verse.get("footnote_drafts", []) if n.get("id") == "gen-1-1-power"]
    if len(footnotes) != 1:
        raise ValueError("Power footnote absent or duplicated")
    power = footnotes[0]
    if (power.get("anchor"), power.get("category"), power.get("editorial_status"),
        power.get("is_independent_hebrew_lexeme"), power.get("evidence_references")) != (
            "[of His Power]", "INTERTEXTUAL_THEOLOGICAL_SUPPLEMENT", "RESEARCH_DRAFT",
            False, ["Gen.49.3", "Deut.21.17"]):
        raise ValueError("The interpretive [of His Power] status or evidence changed")
    if not all(isinstance(n, str) and n.strip() for n in (unote.get("english"), power.get("english"))):
        raise ValueError("Footnote body missing")
    if not all(s in unote["english"] for s in (
        "temporal", "With Wisdom", "eternal uncreated Son",
        "NOT an independently established instrumental", "NOT a proven lexical identification")):
        raise ValueError("The owner-interpreted with must not be treated as established Hebrew grammar")
    if not all(s in power["english"] for s in (
        "Genesis 49:3", "Deuteronomy 21:17", "ABSENT from Genesis 1:1")):
        raise ValueError("[of His Power] no longer has a transparent evidence boundary")
    evidence = unote.get("evidence", [])
    if len(evidence) < 2 or any(not isinstance(row, dict) or
        urlsplit(row.get("url", "")).scheme != "https" or
        not urlsplit(row["url"]).netloc for row in evidence):
        raise ValueError("Missing HTTPS scholarly evidence for owner underword")
    if MAIN.count("[of His Power]") != 1 or not MAIN.startswith("In "):
        raise ValueError("Expected fixed English anchors")
    before, after = MAIN[3:].split("[of His Power]")
    hebrew = " ".join(w.replace("/", "") for w in verse["original_hebrew_token_sequence"])
    links = "\n".join(
        '        <li><a href="{}">{}</a> — {}</li>'.format(
            escape(e["url"], quote=True), escape(e["url"]), escape(e.get("type", "research source")))
        for e in evidence
    )
    # CSS supports a real two-line underword. The layout is a research proof,
    # NOT proof of page-bottom footnotes in a final printed manuscript.
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OLT — Genesis 1:1 | Unapproved research layout</title>
<style>
  @page {{ size: A4; margin: 23mm 21mm; }}
  :root {{ --main-link: {primary_color}; --under-link: {secondary_color}; }}
  * {{ box-sizing: border-box; }}
  body {{ color: #191919; background: #fff; font: 17px/1.7 Georgia, "Times New Roman", serif; max-width: 850px; margin: 2rem auto; padding: 0 1.5rem; }}
  h1 {{ font-size: 1.55rem; margin-bottom: .3rem; }}
  .warning {{ border-left: 4px solid #555; padding: .6rem .9rem; background: #f2f2f2; font: 14px/1.5 system-ui, sans-serif; }}
  .hebrew {{ direction: rtl; text-align: right; font-size: 26px; line-height: 1.9; margin: 1.5rem 0; }}
  .english {{ font-size: 24px; line-height: 2.2; margin: 1.4rem 0; }}
  .linked-word {{ display: inline-flex; flex-direction: column; align-items: center; vertical-align: middle; line-height: 1.08; margin-right: .2em; }}
  .linked-word .primary {{ color: var(--main-link); font-weight: 700; }}
  .linked-word .secondary {{ color: var(--under-link); font-size: .66em; font-weight: 700; margin-top: .12em; }}
  .supplement {{ white-space: nowrap; }}
  sup {{ font-size: .57em; line-height: 0; vertical-align: super; }}
  a {{ color: #245787; }}
  .notes {{ font: 15px/1.6 Georgia, "Times New Roman", serif; border-top: 1px solid #888; margin-top: 2.3rem; padding-top: .5rem; }}
  .notes li {{ margin: .8rem 0; }}
  .evidence {{ overflow-wrap: anywhere; font: 12px/1.5 system-ui, sans-serif; }}
  .status {{ font: 12px/1.4 system-ui, sans-serif; text-transform: uppercase; letter-spacing: .06em; }}
  @media print {{ body {{ margin: 0; max-width: none; padding: 0; }} .warning {{ background: transparent; }} .english {{ break-inside: avoid; }} }}
</style>
</head>
<body>
<h1>Genesis 1:1 — Research layout</h1>
<p class="status">OLT-023 · Research only · Release blocked</p>
<p class="warning"><strong>NOT APPROVED BIBLE TEXT.</strong> The source-linked English is a research proposal. Its grammar, interpretation, typography and notes have not received independent publication review. The blue <em>with</em> is an owner-selected canonical interpretation, not a certified Hebrew gloss.</p>
<p class="hebrew" lang="he" dir="rtl">{escape(hebrew)}</p>
<p class="english" lang="en" data-primary-source-token="01xeN" data-publication-status="BLOCKED"><span class="linked-word" aria-label="In; interpretive under-word: with"><span class="primary">In</span><span class="secondary">with<sup><a href="#note-with" aria-label="Under-word research note 1">1</a></sup></span></span>{escape(before)}<span class="supplement">[of His Power]<sup><a href="#note-power" aria-label="Editorial supplement research note 2">2</a></sup></span>{escape(after)}</p>
<section class="notes" aria-label="Research notes (not page-bottom printed footnotes)">
<h2>Research notes — not independently approved</h2>
<ol>
  <li id="note-with">{escape(unote["english"])}</li>
  <li id="note-power">{escape(power["english"])}</li>
</ol>
</section>
<section class="evidence" aria-label="Under-word research references">
<h2>Research references</h2>
<ul>
{links}
</ul>
</section>
<p class="status">Original Hebrew word-token count: 7 · One owner-selected under-word · Release BLOCKED</p>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if saved HTML differs from regenerated file")
    args = parser.parse_args()
    html = build_html(json.loads(VERSE.read_text(encoding="utf-8")),
                      json.loads(POLICY.read_text(encoding="utf-8")))
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != html:
            raise SystemExit("FAIL: OLT-023 HTML is missing or differs from locked source/policy")
        print("PASS: OLT-023 derived layout unchanged; publication remains BLOCKED")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(html, encoding="utf-8")
        print(f"Wrote {OUTPUT} — RESEARCH ONLY, NOT APPROVED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
