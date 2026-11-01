"""DANMEK-042 — English-only long-distance subjects with closed clause adjuncts.

Only invented syntactic fixtures. No CHES English verses may enter public CI.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.danmek_039_english_only import (
    REVISION, build_current_english, reorder_english_subjects,
)


class TestDanMek042DistantSubjects(unittest.TestCase):
    def test_complete_prep_phrase_before_agent_of_intransitive_verb(self):
        fixtures = [
            (
                ["and·he-is-reigning", "instead-of·him",
                 "Rowan", "son-of", "Oren", "from·the·city"],
                "and Rowan son-of Oren - ·he-is-reigning instead-of·him from·the·city",
            ),
            (
                ["and·he-is-going", "from·there", "Mira",
                 "and·he-is-camping", "in·the·valley"],
                "and Mira - ·he-is-going from·there and·he-is-camping in·the·valley",
            ),
            (
                ["and·she-is-coming", "to·him", "Talia",
                 "and·she-is-speaking", "to·him"],
                "and Talia - ·she-is-coming to·him and·she-is-speaking to·him",
            ),
            (
                ["he-dwelt", "in·them", "Oren"],
                "Oren - he-dwelt in·them",
            ),
            (
                ["he-", "appeared", "to·you", "Rowan"],
                "Rowan - he- appeared to·you",
            ),
        ]
        for source, expected in fixtures:
            with self.subTest(source=source):
                actual, counts = reorder_english_subjects(source)
                self.assertEqual(actual, expected)
                self.assertEqual(counts["applied_subject_moves"], 1)
                self.assertEqual(
                    counts["rule_INTRANSITIVE_AGENT_AFTER_CLOSED_ADJUNCT"], 1,
                )

    def test_dative_agent_between_recipient_and_standalone_marked_object(self):
        fixtures = [
            (
                ["and·he-is-giving", "to·him", "Rowan",
                 "»", "the·book"],
                "and Rowan - ·he-is-giving to·him » the·book",
            ),
            (
                ["and·he-is-", "telling", "to·her", "Mira",
                 "»", "all-of", "matters"],
                "and Mira - ·he-is- telling to·her » all-of matters",
            ),
            (
                ["and·she-is-", "relating", "to·them", "Talia",
                 "»", "the·event"],
                "and Talia - ·she-is- relating to·them » the·event",
            ),
            (
                ["he-said", "to·him", "Natan", "»", "horses-of·them"],
                "Natan - he-said to·him » horses-of·them",
            ),
        ]
        for source, expected in fixtures:
            with self.subTest(source=source):
                result, counts = reorder_english_subjects(source)
                self.assertEqual(result, expected)
                self.assertEqual(
                    counts["rule_DATIVE_AGENT_BEFORE_MARKED_OBJECT"], 1,
                )
                self.assertEqual(result.count("»"), " ".join(source).count("»"))

    def test_both_structures_in_same_verse_without_clause_interference(self):
        src = [
            "and·he-is-reigning", "instead-of·him", "Rowan", "son-of", "Oren",
            "and·she-is-giving", "to·him", "Mira", "»", "the·book",
        ]
        result, counts = reorder_english_subjects(src)
        self.assertEqual(
            result,
            "and Rowan son-of Oren - ·he-is-reigning instead-of·him "
            "and Mira - ·she-is-giving to·him » the·book",
        )
        self.assertEqual(counts["applied_subject_moves"], 2)
        self.assertEqual(result.count("»"), 1)

    def test_ambiguous_preposition_or_no_marked_object_is_not_moved(self):
        negatives = [
            # A single name following a finite transitive verb is not proof.
            ["he-gave", "to·him", "Rowan", "in·the·house"],
            ["he-spoke", "to·him", "Rowan", "he-served"],
            ["he-said", "to·them", "Rowan", "not", "he-served"],
            ["he-is-seeing", "to·him", "Rowan", "»", "the·stone"],
            ["and·he-is-blessing", "to·him", "Rowan", "»", "the·city"],
            # PP with unclosed noun complement cannot prove next name subject.
            ["and·he-is-coming", "from", "the·city", "Mira"],
            ["and·he-is-going", "to", "Rowan", "in·the·city"],
            ["and·he-is-reigning", "instead-of", "Rowan", "in·the·city"],
            # No borrowing a name from an unrelated clause.
            ["Rowan", "he-dwelt", "in·them", "Mira"],
            # The full phrase may include a coordinate or interrupted title.
            ["and·he-is-reigning", "instead-of·him",
             "Rowan", "and·Mira", "there"],
            ["and·he-is-giving", "to·him",
             "Mira", "and·Talia", "»", "the·books"],
            ["and·he-is-coming", "to·him",
             "Rowan", "m", "son-of", "Oren", "and·he-is-saying"],
            # Do not move a relative clause's subject to outer predicate.
            ["and·he-is-coming", "to·them",
             "Rowan", "-", "he-went", "in·the·city"],
        ]
        for source in negatives:
            with self.subTest(source=source):
                result, counts = reorder_english_subjects(source)
                self.assertEqual(result, " ".join(source))
                self.assertEqual(counts.get("applied_subject_moves", 0), 0)

    def test_single_active_reader_and_privacy_stay_intact(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            src = root / "ches"
            src.mkdir(mode=0o700)
            items = [
                ["and·he-is-reigning", "instead-of·him",
                 "Rowan", "son-of", "Oren"],
                ["and·he-is-telling", "to·her", "Mira",
                 "»", "the·news"],
            ]
            doc = {
                "book": "gen", "chapter": 1,
                "full_source_text_in_public_git_permitted": False,
                "verses": [
                    {
                        "reference": f"gen.1.{i}",
                        "source_ches_spans_NOT_OLT_TRANSLATION": [
                            {"original_ches_line_text": val}
                            for val in row
                        ],
                    }
                    for i, row in enumerate(items, 1)
                ],
            }
            original = json.dumps(doc).encode()
            source = src / "gen.1.json"
            source.write_bytes(original)
            audit = build_current_english(src)
            self.assertEqual(audit["source_verses"], 2)
            self.assertEqual(audit["subject_moves_applied"], 2)
            self.assertFalse(audit["source_ches_modified"])
            self.assertFalse(audit["original_language_comparison_performed"])
            out = root / "current-reading"
            published = build_current_english(src, output=out, render_current=True)
            self.assertEqual(published["revision"], REVISION)
            text = (out / "gen.1.html").read_text(encoding="utf-8")
            self.assertIn("and Rowan son-of Oren - ·he-is-reigning", text)
            self.assertIn("and Mira - ·he-is-telling to·her » the·news", text)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse((root / "current-reading.previous-private").exists())


if __name__ == "__main__":
    unittest.main()
