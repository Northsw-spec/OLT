"""OLT-032: maintain one current, accurate repository status entrypoint."""
import json
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/STATUS_CURRENT.md"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class TestOLT032(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = STATUS.read_text(encoding="utf-8")
        cls.current, cls.history = cls.text.split(
            "## Historical checkpoint chronology (recorded 29–30 October 2026; superseded status where noted)", 1
        )
        cls.variants = load("data/research/olt_031_lemma_variation_triage.json")
        cls.chapter = load("data/research/genesis_01_complete_research_alignment.json")
        cls.verse = load("data/research/genesis_01_verse_01_alignment_proposal.json")
        cls.underwords = load("data/policy/olt_underword_overrides.json")

    def test_current_status_precedes_archived_chronology(self):
        # Status is a living canonical document. Do not require the date of
        # OLT-032's first publication after later verified checkpoints.
        heading = self.text.splitlines()[0]
        self.assertRegex(heading, r"^# OLT — CURRENT STATUS \\(\\d{4}-\\d{2}-\\d{2}\\)$")
        status_date = date.fromisoformat(heading.rsplit("(", 1)[1][:-1])
        self.assertGreaterEqual(status_date, date(2026, 10, 30))
        self.assertIn("OLT-031", self.current)
        self.assertIn("The old runner-admission problem", self.current)
        self.assertIn("historically recorded", self.current)
        self.assertIn("Historical checkpoint chronology", self.text)
        self.assertIn("Latest completed data checkpoints", self.history)

    def test_genesis_1_counts_agree_with_canonical_sources(self):
        v = self.variants
        self.assertEqual((v["exact_source_lemma_ids"], v["original_hebrew_word_tokens"]), (97, 434))
        self.assertEqual((v["source_tokens_with_numeric_lemma"], v["source_tokens_without_numeric_lemma"]), (427, 7))
        self.assertEqual(v["source_lemmas_with_multiple_unapproved_fragments"], 42)
        self.assertEqual(v["source_lemmas_with_one_unapproved_fragment"], 55)
        self.assertEqual(len(v["cases"]), 42)
        self.assertEqual(sum(len(c["original_source_contexts"]) for c in v["cases"]), 322)
        for count in ("31", "434", "97", "427", "7", "50", "42", "55", "322", "94"):
            self.assertIn(count, self.current)
        self.assertEqual(self.chapter["source_tagged_wayyiqtol_count"], 50)

    def test_owner_genesis_wording_and_exact_underword_are_preserved(self):
        self.assertIn(self.verse["main_english_proposal"], self.current)
        self.assertEqual(self.verse["publication_status"], "BLOCKED")
        self.assertEqual(self.underwords["publication_status"], "BLOCKED")
        self.assertEqual(len(self.underwords["underwords"]), 1)
        self.assertEqual(self.underwords["underwords"][0]["reference"], "Gen.1.1")
        self.assertIn("with", self.current)
        self.assertIn("binitarian canonical interpretation", self.current.lower())
        self.assertIn("And God — He saw the light, that [he was] — good.", self.current)

    def test_publication_boundary_not_automatically_weakened(self):
        self.assertEqual(self.variants["new_english_lexical_approvals"], 0)
        self.assertEqual(self.variants["approved_homonym_links"], 0)
        self.assertEqual(self.variants["publication_status"], "BLOCKED")
        self.assertIn("Translation publication:** BLOCKED", self.current)
        self.assertIn("Independent lexical/morphological signoff:** NOT DONE", self.current)
        self.assertIn("Passing GitHub Actions is engineering evidence", self.current)


if __name__ == "__main__":
    unittest.main()
