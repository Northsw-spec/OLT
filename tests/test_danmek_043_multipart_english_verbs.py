"""DANMEK-043: real-CHES-shaped English finite fragments and safe distant agents.

All examples are invented English tokens; no licensed CHES verses or
original-language materials are copied into GitHub or CI.
"""
from __future__ import annotations

from pathlib import Path
import json
import tempfile
import unittest

from scripts.danmek_039_english_only import (
    REVISION, _predicates, _predicate_lemma, reorder_english_subjects,
    build_current_english,
)


class TestDanmek043EnglishMultipart(unittest.TestCase):
    def test_progressive_verb_is_three_source_fragments_not_two(self):
        examples = (
            (["and·he-is-", "go", "ing-up", "here"],
             [(0, 3)], "going-up"),
            (["and·she-is-", "com", "ing-forth", "there"],
             [(0, 3)], "coming-forth"),
            (["and·he-is-", "be", "ing-hot", "there"],
             [(0, 3)], "being-hot"),
            (["and·he-is-", "bring", "ing-near", "here"],
             [(0, 3)], "bringing-near"),
            (["and·they-", "bring", "ing-close", "»", "objects"],
             [(0, 3)], "bringing-close"),
        )
        for tokens, spans, lemma in examples:
            with self.subTest(tokens=tokens):
                self.assertEqual(list(_predicates(tokens)), spans)
                self.assertEqual(_predicate_lemma(tokens, *spans[0]), lemma)

    def test_original_single_fragment_and_normal_split_verbs_remain_recognized(self):
        cases = [
            (["he-", "spoke", "Mira", "to·them"], [(0, 2)], "spoke"),
            (["and·he-is-saying", "Mira", "to·them"],
             [(0, 1)], "saying"),
            (["and·he-is-", "generating", "Rowan", "»", "object"],
             [(0, 2)], "generating"),
            (["he-", "gave-", "birth", "Talia", "»", "child"],
             [(0, 3)], "birth"),
        ]
        for words, expect, lemma in cases:
            with self.subTest(words=words):
                self.assertEqual(list(_predicates(words)), expect)
                self.assertEqual(_predicate_lemma(words, *expect[0]), lemma)

    def test_progressive_motion_agent_after_closed_two_fragment_adverbial(self):
        source = [
            "and·he-is-", "go", "ing-up", "in·", "·first",
            "Rowan", "son-of", "Oren",
            "and·he-is-speaking", "to·him",
        ]
        result, stats = reorder_english_subjects(source)
        self.assertEqual(
            result,
            "and Rowan son-of Oren - ·he-is- go ing-up in· ·first "
            "and·he-is-speaking to·him",
        )
        self.assertEqual(stats["applied_subject_moves"], 1)
        self.assertEqual(
            stats["rule_INTRANSITIVE_AGENT_AFTER_CLOSED_ADJUNCT"], 1,
        )
        self.assertEqual(stats["english_finite_predicates_seen"], 2)

    def test_multiple_complete_adverbials_between_finite_verb_and_subject(self):
        source = [
            "and·he-is-", "com", "ing-forth",
            "from·there", "after·him", "to·them", "here",
            "Mira", "the·prophet",
        ]
        result, counts = reorder_english_subjects(source)
        self.assertEqual(
            result,
            "and Mira the·prophet - ·he-is- com ing-forth "
            "from·there after·him to·them here",
        )
        self.assertEqual(counts["applied_subject_moves"], 1)
        self.assertEqual(result.count("Mira"), 1)

    def test_intransitive_agent_with_simple_location_adverb(self):
        cases = (
            (["and·he-is-dying", "there", "Rowan"],
             "and Rowan - ·he-is-dying there"),
            (["he-dwelt", "there", "Mira"],
             "Mira - he-dwelt there"),
            (["and·he-is-encamping", "there", "Talia", "in·the·valley"],
             "and Talia - ·he-is-encamping there in·the·valley"),
        )
        for src, expected in cases:
            with self.subTest(src=src):
                result, counts = reorder_english_subjects(src)
                self.assertEqual(result, expected)
                self.assertEqual(counts["applied_subject_moves"], 1)

    def test_transitive_location_requires_separate_explicit_marked_object(self):
        cases = (
            (["and·he-is-building", "there", "Rowan", "»", "the·altar"],
             "and Rowan - ·he-is-building there » the·altar"),
            (["and·he-is-", "apportioning", "here", "Mira", "»", "the·land"],
             "and Mira - ·he-is- apportioning here » the·land"),
        )
        for src, expected in cases:
            with self.subTest(src=src):
                result, stats = reorder_english_subjects(src)
                self.assertEqual(result, expected)
                self.assertEqual(
                    stats["rule_LOCATIVE_AGENT_BEFORE_SEPARATE_MARKED_OBJECT"], 1,
                )
                self.assertEqual(result.count("»"), " ".join(src).count("»"))

    def test_location_without_object_mark_is_not_sufficient(self):
        counterexamples = (
            ["and·you-serve", "there", "Elohim", "other-ones"],
            ["and·he-is-building", "there", "Rowan", "altar"],
            ["and·he-is-seeing", "there", "Mira", "daughter-of", "Oren"],
            ["and·he-is-calling", "there", "Rowan", "in·name-of"],
            ["and·he-is-", "bring", "ing-forth", "there", "Mira"],
            ["and·he-is-", "go", "ing-up", "from", "Mira"],
            ["and·he-is-", "go", "ing-up", "in·", "Mira"],
            ["and·he-is-coming", "from", "the·city", "Mira"],
            ["and·he-is-calling", "there", "Mira", "»", "the·place"],
            ["Rowan", "he-dwelt", "there", "Mira"],
            ["and·he-is-", "go", "ing-up", "in·", "·first",
             "Mira", "and·Talia", "in·the·city"],
            ["and·he-is-", "go", "ing-up", "in·", "·first",
             "Mira", "-", "she-went"],
        )
        for source in counterexamples:
            with self.subTest(source=source):
                result, stats = reorder_english_subjects(source)
                self.assertEqual(result, " ".join(source))
                self.assertEqual(stats.get("applied_subject_moves", 0), 0)

    def test_independent_adjacent_clauses_and_unchanged_objects(self):
        source = [
            "and·he-is-", "go", "ing-up", "in·", "·first",
            "Rowan", "son-of", "Oren",
            "and·she-is-building", "there", "Mira", "»", "the·altar",
        ]
        result, stats = reorder_english_subjects(source)
        self.assertEqual(
            result,
            "and Rowan son-of Oren - ·he-is- go ing-up in· ·first "
            "and Mira - ·she-is-building there » the·altar",
        )
        self.assertEqual(stats["applied_subject_moves"], 2)
        self.assertEqual(result.count("»"), 1)

    def test_original_private_json_untouched_and_same_current_reader(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            private = root / "ches"
            private.mkdir(mode=0o700)
            verses = [
                ["and·he-is-", "go", "ing-up", "in·", "·first", "Rowan"],
                ["and·she-is-building", "there", "Mira", "»", "the·altar"],
                ["and·you-serve", "there", "Elohim", "other-ones"],
            ]
            doc = {
                "book": "gen", "chapter": 1,
                "full_source_text_in_public_git_permitted": False,
                "verses": [
                    {"reference": f"gen.1.{i}",
                     "source_ches_spans_NOT_OLT_TRANSLATION": [
                         {"original_ches_line_text": tok} for tok in toks
                     ]}
                    for i, toks in enumerate(verses, 1)
                ],
            }
            path = private / "gen.1.json"
            original = json.dumps(doc).encode()
            path.write_bytes(original)
            audited = build_current_english(private)
            self.assertEqual(audited["source_verses"], 3)
            self.assertEqual(audited["subject_moves_applied"], 2)
            self.assertTrue(audited["english_finite_predicates_seen"] >= 3)
            self.assertFalse(audited["source_ches_modified"])
            self.assertFalse(audited["original_language_comparison_performed"])
            self.assertEqual(path.read_bytes(), original)
            destination = root / "current-private-reading"
            status = build_current_english(
                private, render_current=True, output=destination,
            )
            self.assertEqual(status["revision"], REVISION)
            page = (destination / "gen.1.html").read_text()
            self.assertIn("and Rowan - ·he-is- go ing-up in· ·first", page)
            self.assertIn("and Mira - ·she-is-building there » the·altar", page)
            self.assertIn("and·you-serve there Elohim other-ones", page)
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(
                (root / "current-private-reading.previous-private").exists()
            )


if __name__ == "__main__":
    unittest.main()
