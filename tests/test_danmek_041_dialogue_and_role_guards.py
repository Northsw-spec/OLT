"""DANMEK-041: English-only ambiguous speech and naming-complement guards.

Synthetic English examples only; no licensed CHES verses or original-language
data in GitHub. The one active DANMEK-039 reader is exercised directly.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest

from scripts.danmek_039_english_only import (
    REVISION,
    build_current_english,
    reorder_english_subjects,
)


class TestDanMek041ClauseRoles(unittest.TestCase):
    def test_postrecipient_named_speaker_with_explicit_speech_opening(self):
        fixtures = (
            (
                ["and·he-is-saying", "to·them", "Rowan", "thus",
                 "you-speak", "to·people"],
                "and Rowan - ·he-is-saying to·them thus you-speak to·people",
            ),
            (
                ["and·he-is-saying", "to·him", "Mira", "must-not",
                 "you-are-fearing"],
                "and Mira - ·he-is-saying to·him must-not you-are-fearing",
            ),
            (
                ["and·she-is-", "responding", "to·them", "Talia",
                 "sing-you", "!", "to·Lord"],
                "and Talia - ·she-is- responding to·them sing-you ! to·Lord",
            ),
            (
                ["he-", "told", "to·her", "Natan", "not",
                 "you-shall-come"],
                "Natan - he- told to·her not you-shall-come",
            ),
        )
        for source, expected in fixtures:
            with self.subTest(source=source):
                actual, counts = reorder_english_subjects(source)
                self.assertEqual(actual, expected)
                self.assertEqual(counts.get("applied_subject_moves"), 1)
                self.assertEqual(
                    counts.get("rule_REPORTING_SPEAKER_AFTER_PRONOMINAL_RECIPIENT"),
                    1,
                )
                self.assertEqual(actual.count("»"), " ".join(source).count("»"))

    def test_quoted_clause_subject_not_misassigned_as_reporting_speaker(self):
        examples = (
            # "They said to them, Ahab served ..." - Ahab belongs to the
            # quoted proposition, not demonstrably to the verb "said".
            ["and·he-is-saying", "to·them", "Ahab", "he-served",
             "»", "the·altar"],
            # "They said to them: Oren ... he-appeared" does not prove
            # that Oren was the reporter (even with English source only).
            ["and·he-is-saying", "to·them", "Oren",
             "Elohim-of", "fathers", "he-", "appeared"],
            ["and·he-is-saying", "to·him", "Rowan",
             "he-tore", "Mira", "»", "the·land"],
            # Second-person recipient can contain a name in vocative:
            # "he spoke to you, Daniel..."
            ["and·he-is-", "speaking", "to·you", "Mira",
             "understand-you", "!"],
            ["and·he-is-saying", "to·me", "Talia",
             "must-not", "you-go"],
            # No separate direct-speech cue after the name.
            ["and·he-is-saying", "to·them", "Rowan", "in·the·city"],
            # Multiword noun phrase cannot be partially moved.
            ["and·he-is-saying", "to·them", "Rowan",
             "and·Mira", "thus", "you-go"],
        )
        for source in examples:
            with self.subTest(source=source):
                result, counts = reorder_english_subjects(source)
                self.assertEqual(result, " ".join(source))
                self.assertEqual(counts.get("applied_subject_moves", 0), 0)

    def test_naming_verbs_do_not_turn_predicative_name_into_agent(self):
        examples = (
            ["and·he-is-calling", "»·her", "Sheba",
             "on·so", "the·place"],
            ["he-named", "»·him", "Natan", "at·dawn"],
            ["and·he-is-", "identifying", "»·him",
             "Rowan", "in·the·city"],
            ["and·he-is-naming", "»·them", "Mira",
             "at·the·gate"],
        )
        for source in examples:
            with self.subTest(source=source):
                result, counts = reorder_english_subjects(source)
                self.assertEqual(result, " ".join(source))
                self.assertEqual(counts.get("applied_subject_moves", 0), 0)

    def test_other_delayed_marked_object_agents_still_move_when_supported(self):
        cases = (
            (
                ["and·he-is-blessing", "»·them", "Rowan",
                 "in·the·field"],
                "and Rowan - ·he-is-blessing »·them in·the·field",
            ),
            (
                ["and·he-is-seeing", "»·her", "Mira",
                 "son-of", "Oren", "on·the·road"],
                "and Mira son-of Oren - ·he-is-seeing »·her on·the·road",
            ),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                result, counts = reorder_english_subjects(source)
                self.assertEqual(result, expected)
                self.assertEqual(
                    counts.get("rule_POSTPOSED_AGENT_AFTER_PRONOMINAL_OBJECT"), 1,
                )

    def test_two_independent_speech_and_marked_object_clauses(self):
        source = [
            "and·he-is-saying", "to·them", "Rowan", "thus", "you-speak",
            "and·she-is-blessing", "»·them", "Mira",
        ]
        after, stats = reorder_english_subjects(source)
        self.assertEqual(
            after,
            "and Rowan - ·he-is-saying to·them thus you-speak "
            "and Mira - ·she-is-blessing »·them",
        )
        self.assertEqual(stats.get("applied_subject_moves"), 2)
        self.assertEqual(after.count("»"), 1)
        self.assertEqual(after.count("Rowan"), 1)
        self.assertEqual(after.count("Mira"), 1)

    def test_source_unchanged_audit_and_one_current_reader_with_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            src = parent / "ches"
            src.mkdir(mode=0o700)
            out = parent / "reader"
            fake = {
                "book": "gen", "chapter": 1,
                "full_source_text_in_public_git_permitted": False,
                "verses": [
                    {
                        "reference": f"gen.1.{n}",
                        "source_ches_spans_NOT_OLT_TRANSLATION": [
                            {"original_ches_line_text": word}
                            for word in words
                        ],
                    }
                    for n, words in enumerate((
                        ["and·he-is-saying", "to·them", "Rowan",
                         "must-not", "you-go"],
                        ["and·he-is-calling", "»·her", "Sheba", "on·so"],
                    ), 1)
                ],
            }
            original = json.dumps(fake, ensure_ascii=False).encode()
            sourcefile = src / "gen.1.json"
            sourcefile.write_bytes(original)
            audit = build_current_english(src)
            self.assertEqual(audit["subject_moves_applied"], 1)
            self.assertEqual(audit["source_verses"], 2)
            self.assertFalse(audit["source_ches_modified"])
            self.assertFalse(audit["original_language_comparison_performed"])
            self.assertEqual(sourcefile.read_bytes(), original)
            read = build_current_english(src, render_current=True, output=out)
            self.assertEqual(read["revision"], REVISION)
            page = (out / "gen.1.html").read_text()
            self.assertIn("and Rowan - ·he-is-saying to·them", page)
            self.assertIn("and·he-is-calling »·her Sheba", page)
            self.assertEqual(sourcefile.read_bytes(), original)
            self.assertFalse((parent / "reader.previous-private").exists())


if __name__ == "__main__":
    unittest.main()
