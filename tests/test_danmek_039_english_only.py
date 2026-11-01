"""DANMEK-039: the active English grammar engine and policy, synthetic only."""
from __future__ import annotations

import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.danmek_039_english_only import (
    DanMekEnglishError, build_current_english, reorder_english_subjects,
    main,
)

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts/danmek_039_english_only.py"
POLICY = ROOT / "data/policy/danmek_039_english_subject_verb_only.json"
MASTER = ROOT / "docs/DANMEK_MASTERPROMPT.md"


def chapter(book="gen", ch=1, lines=None):
    lines = lines or [
        ["and·he-is-", "generating", "Rowan", "»", "Micah"],
        ["and·he-is-saying", "Mira", "to", "Natan"],
    ]
    return {
        "book": book, "chapter": ch, "full_source_text_in_public_git_permitted": False,
        "verses": [
            {
                "reference": f"{book}.{ch}.{n}",
                "source_ches_spans_NOT_OLT_TRANSLATION": [
                    {"original_ches_line_text": text,
                     "page": 1, "pdf_x": 50.0+i*10, "pdf_y": 120.0}
                    for i, text in enumerate(words)
                ]
            }
            for n, words in enumerate(lines, 1)
        ]
    }


class TestDanMek039EnglishOnly(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.folder = Path(t.name)
        self.source = self.folder / "private-ches"
        self.source.mkdir(mode=0o700)
        (self.source / "gen.1.json").write_text(
            json.dumps(chapter()), encoding="utf-8",
        )
        self.initial = (self.source / "gen.1.json").read_bytes()

    def test_real_user_structure_but_invented_names(self):
        english, stats = reorder_english_subjects(
            ["and·he-is-", "generating", "Rowan", "»", "Micah"]
        )
        self.assertEqual(english, "and Rowan ·he-is- generating » Micah")
        self.assertEqual(stats["applied_subject_moves"], 1)
        self.assertEqual(stats["rule_FINITE_NOMINAL_EXPLICIT_OBJECT"], 1)

    def test_multiple_clause_subject_moves_and_objects_retained(self):
        tokens = [
            "and·he-is-seeing", "Rowan", "»", "the·light",
            "and·he-is-saying", "Mira", "to·Natan", "behold !",
        ]
        after, counts = reorder_english_subjects(tokens)
        self.assertIn("and Rowan - ·he-is-seeing » the·light", after)
        self.assertIn("and Mira - ·he-is-saying to·Natan", after)
        self.assertEqual(counts["applied_subject_moves"], 2)
        self.assertEqual(after.count("Rowan"), 1)
        self.assertEqual(after.count("Mira"), 1)
        self.assertIn("» the·light", after)

    def test_identified_relative_subject_crosses_clause_boundaries(self):
        tokens = [
            "and·he-is-becoming", "as·which", "Natan", "-",
            "he-sits", "in·house-of·him",
            "and·he-is-saying", "Natan", "to", "Mira",
        ]
        after, summary = reorder_english_subjects(tokens)
        self.assertEqual(
            after,
            "and Natan - ·he-is-becoming as·which - he-sits "
            "in·house-of·him and Natan - ·he-is-saying to Mira",
        )
        self.assertEqual(summary["applied_subject_moves"], 2)
        self.assertIn("DISTANT_RELATIVE_CLAUSE_SUBJECT",
                      " ".join(summary.keys()))

    def test_no_distance_limit_for_anchored_relative_subject(self):
        words = ["and·he-is-becoming", "as·which"]
        words += ["formerly"] * 150
        words += ["Rowan", "-", "he-sits", "quietly"]
        after, stats = reorder_english_subjects(words)
        self.assertEqual(stats["applied_subject_moves"], 1)
        self.assertTrue(after.startswith("and Rowan - ·he-is-becoming"))
        self.assertEqual(after.count("formerly"), 150)

    def test_transitive_object_and_infinitive_are_not_moved(self):
        for tokens in (
            ["and·he-saw", "Rowan", "in·the·street"],
            ["and·he-is-saying", "Rowan", "to·to-carry-of", "the·bag"],
            ["he-loves", "Mira"],
            ["and·he-is-making", "Rowan", "and·Mira"],
            ["and·he-is-taking", "the·vessel", "to·Mira"],
            ["and·he-is-saying", "I-saw", "to·Rowan"],
            ["he-says", "Rowan", "the·king", "of", "the·city"],
            ["he-chose", "Yahweh", "to·to-carry-of"],
        ):
            with self.subTest(tokens=tokens):
                before = " ".join(tokens)
                after, stats = reorder_english_subjects(tokens)
                self.assertEqual(after, before)
                self.assertEqual(stats.get("applied_subject_moves", 0), 0)

    def test_compound_subject_keeps_full_phrase(self):
        tokens = [
            "and·he-is-saying", "Rowan", "the·prophet", "to·Mira"
        ]
        after, counts = reorder_english_subjects(tokens)
        self.assertEqual(
            after, "and Rowan the·prophet - ·he-is-saying to·Mira",
        )
        self.assertEqual(counts["applied_subject_moves"], 1)

    def test_audit_directory_and_full_ot_guard(self):
        report = build_current_english(self.source)
        self.assertEqual(report["source_books"], 1)
        self.assertEqual(report["source_chapters"], 1)
        self.assertEqual(report["source_verses"], 2)
        self.assertEqual(report["mode"], "AUDIT_ONLY")
        self.assertGreater(report["subject_moves_applied"], 0)
        self.assertFalse(report["original_language_code_imported"])
        self.assertFalse(report["original_language_comparison_performed"])
        self.assertFalse((self.folder / "ches-english-current").exists())
        self.assertEqual((self.source / "gen.1.json").read_bytes(), self.initial)
        with self.assertRaisesRegex(DanMekEnglishError,
                                    "EXPECTED_CHES_OT_INVENTORY_CHANGED"):
            build_current_english(self.source, require_full_ot=True)

    def test_single_private_output_atomically_replaces_previous_reader(self):
        destination = self.folder / "reader"
        report = build_current_english(
            self.source, render_current=True, output=destination,
        )
        self.assertEqual(report["mode"], "CURRENT_PRIVATE_ENGLISH_OT")
        self.assertEqual(set(p.name for p in destination.iterdir()),
                         {"index.html", "MANIFEST.json", "gen.1.html", "gen.txt"})
        self.assertEqual(destination.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600
                            for p in destination.iterdir()))
        page = (destination / "gen.1.html").read_text()
        self.assertIn("and Rowan ·he-is- generating » Micah", page)
        self.assertIn("and Mira - ·he-is-saying to Natan", page)
        (destination / "gen.1.html").write_text("OUTDATED_RESULT")
        again = build_current_english(
            self.source, render_current=True, output=destination,
        )
        self.assertEqual(again["subject_moves_applied"],
                         report["subject_moves_applied"])
        self.assertNotIn("OUTDATED_RESULT",
                         (destination / "gen.1.html").read_text())
        self.assertFalse((self.folder / "reader.previous-private").exists())
        self.assertEqual((self.source / "gen.1.json").read_bytes(), self.initial)

    def test_zip_input_no_extraction_or_private_leak(self):
        archive = self.folder / "private.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("ches/gen.1.json", self.initial)
        original = archive.read_bytes()
        report = build_current_english(archive)
        self.assertEqual(report["source_verses"], 2)
        self.assertEqual(original, archive.read_bytes())
        with zipfile.ZipFile(archive, "a") as z:
            z.writestr("../escape.txt", "forbidden")
        with self.assertRaisesRegex(DanMekEnglishError, "UNSAFE_ARCHIVE_ENTRY"):
            build_current_english(archive)

    def test_cli_aggregates_never_print_source_words_or_paths(self):
        with patch("sys.argv", [
            "danmek039", "--source", str(self.source),
            "--confirm-private-machine-readable-use", "--audit-only",
        ]):
            stream = io.StringIO()
            with redirect_stdout(stream):
                self.assertEqual(main(), 0)
        data = json.loads(stream.getvalue())
        self.assertEqual(data["source_verses"], 2)
        for private in ("Rowan", "Mira", "Micah", "gen.1.1", str(self.source)):
            self.assertNotIn(private, stream.getvalue())


class TestDanMek039PolicyReset(unittest.TestCase):
    def test_one_active_masterprompt_no_hebrew_revalidation(self):
        master = MASTER.read_text(encoding="utf-8")
        self.assertIn("NO HEBREW REVALIDATION", master)
        self.assertIn("CHES's linguistic decisions", master)
        self.assertIn("oavsett", master)
        self.assertIn("scripts/danmek_039_english_only.py", master)
        self.assertLess(len(master), 12000)
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["status"], "ACTIVE")
        self.assertFalse(policy["original_language_comparison_permitted"])
        self.assertFalse(policy["ches_vs_hebrew_crossvalidation_permitted"])
        self.assertFalse(policy["source_morphology_or_lemma_recheck_required"])
        self.assertFalse(policy["old_danmek_scripts_are_active_grammar_authority"])
        self.assertTrue(policy["english_grammatical_subject_must_precede_related_verb"])

    def test_active_code_has_no_legacy_or_original_language_import(self):
        parsed = ast.parse(ENGINE.read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(parsed):
            if isinstance(node, ast.Import):
                imports.extend(n.name for n in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        for name in imports:
            self.assertFalse(name.startswith(("scripts.", "olt_core",
                "hebrew", "oshb", "wlc", "danmek_", "ches_")), name)
        self.assertNotIn("load_ot_book", ENGINE.read_text())
        self.assertNotIn("read_provenance", ENGINE.read_text())
        self.assertNotIn("from scripts.", ENGINE.read_text())
        self.assertNotIn("from olt_core", ENGINE.read_text())


if __name__ == "__main__":
    unittest.main()
