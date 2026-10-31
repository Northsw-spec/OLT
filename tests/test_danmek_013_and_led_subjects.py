"""DANMEK-013 English And-led subject discovery: fabricated examples only."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ches_015_direct_private_reader import build_private_reader, main
from scripts.ches_import import write_private_json
from scripts.danmek_011_owner_order import (
    apply_owner_approved_candidates, discover_candidates,
)
from test_ches_015_direct_private_reader import invented_chapter


class TestDanMek013AndLedOtherSubjects(unittest.TestCase):
    def test_other_proper_names_after_nonobject_verbs(self):
        cases = {
            "and·he-cameDavidfrom·Town": "And David — he came from·Town",
            "And·he-saidMosesto·Council": "And Moses — he said to·Council",
            "and·he-is-speakingNoahto·Town": "And Noah — he is speaking to·Town",
            "and·he-goesGodin·Town": "And God — he goes in·Town",
            "And·she-aroseMaryfrom·Village": "And Mary — she arose from·Village",
            "and·he-returnedthe·kingto·Town": "And the king — he returned to·Town",
            "and·he-restedthe·priestat·Gate": "And the priest — he rested at·Gate",
            "and·he-shall-comeSolomonto·Town": "And Solomon — he shall come to·Town",
        }
        for original, expected in cases.items():
            with self.subTest(original=original):
                proposed, ambiguous = discover_candidates(
                    "gen.1.1", "f" * 64, [original],
                )
                self.assertFalse(ambiguous)
                self.assertEqual(len(proposed), 1)
                self.assertFalse(proposed[0]["source_syntax_reviewed"])
                self.assertEqual(proposed[0]["mode"], "inline")
                result, reason = apply_owner_approved_candidates(
                    reference="gen.1.1", chapter_sha256="f" * 64,
                    original=[original], visible=[original],
                )
                self.assertEqual(reason, "APPLIED")
                self.assertEqual(result, [expected])
                self.assertNotIn(" — He", result[0])

    def test_and_alone_does_not_prove_name_is_subject(self):
        cases = (
            "and·he-sawMosesfrom·Town",  # object-taking predicate
            "and·he-metDavidat·Gate",
            "and·he-shall-cut-offDavidfrom·Town",
            "and·he-shall-seeYahwehfrom·Town",
            "he-cameDavidfrom·Town",  # no initial And
            "prologue and·he-cameDavidfrom·Town",  # not clause-initial
            "and·he-cameDavidand·Solomon",  # ambiguous candidate boundary
            "and·he-returnedDavidof·Town",  # no supported boundary
        )
        for original in cases:
            with self.subTest(original=original):
                proposed, ambiguous = discover_candidates(
                    "gen.1.1", "f" * 64, [original],
                )
                self.assertFalse(proposed)
                self.assertFalse(ambiguous)
                result, reason = apply_owner_approved_candidates(
                    reference="gen.1.1", chapter_sha256="f" * 64,
                    original=[original], visible=[original],
                )
                self.assertEqual(reason, "NO_CANDIDATE")
                self.assertEqual(result, [original])

    def test_only_clause_initial_And_match_is_newly_reordered(self):
        original = (
            "and·he-saidMosesto·Town "
            "And·he-cameDavidfrom·Village"
        )
        result, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[original], visible=[original],
        )
        # Second And appears inside a larger line; the new bounded
        # sentence-initial matcher must not move that expression.
        self.assertEqual(reason, "APPLIED")
        self.assertEqual(
            result, ["And Moses — he said to·Town And·he-cameDavidfrom·Village"],
        )

    def test_ylt_changed_fragment_stays_unchanged(self):
        original = "and·he-cameDavidfrom·Town"
        ylt = "and·he-cameDavidfrom·City"
        result, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[original], visible=[ylt],
        )
        self.assertEqual(reason, "YLT_OVERLAP")
        self.assertEqual(result, [ylt])

    def test_older_Yahweh_case_and_other_forms_remain_compatible(self):
        original = "and·he-shall-cut-offYahwehfrom·Townfrontand·rear"
        result, reason = apply_owner_approved_candidates(
            reference="gen.1.1", chapter_sha256="f" * 64,
            original=[original], visible=[original],
        )
        self.assertEqual(reason, "APPLIED")
        self.assertEqual(
            result, ["And Yahweh — he shall cut off from·Townfrontand·rear"],
        )
        other, reason = apply_owner_approved_candidates(
            reference="gen.1.2", chapter_sha256="f" * 64,
            original=["and·he-shaped", "Leader"],
            visible=["and·he-shaped", "Leader"],
        )
        self.assertEqual(reason, "APPLIED")
        self.assertEqual(other, ["and Leader — ", "he-shaped"])

    def test_private_source_and_old_snapshots_unchanged(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / ".olt-private"
            root.mkdir(mode=0o700)
            folder = root / "ches"
            folder.mkdir(mode=0o700)
            doc = invented_chapter("gen", 1)
            first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"]
            first[0]["original_ches_line_text"] = "and·he-saidMosesto·Town"
            second = doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
            second[0]["original_ches_line_text"] = "and·he-cameDavidfrom·Town"
            source = folder / "gen.1.json"
            write_private_json(doc, source)
            original_bytes = source.read_bytes()
            with patch("urllib.request.urlopen",
                       side_effect=AssertionError("NO NETWORK")):
                baseline = build_private_reader(folder, render=True)
                updated = build_private_reader(
                    folder, render=True, olt_owner_approved_candidates=True,
                )
                self.assertEqual(
                    build_private_reader(
                        folder, render=True,
                        olt_owner_approved_candidates=True,
                    )["snapshot_id"], updated["snapshot_id"],
                )
            self.assertEqual(updated["olt_owner_approved_candidate_reorders_applied"], 2)
            self.assertFalse(updated["olt_owner_candidate_original_language_subject_verified"])
            self.assertNotEqual(baseline["snapshot_id"], updated["snapshot_id"])
            base_html = (root / "ches-direct-reader" /
                         baseline["snapshot_id"] / "gen.1.html").read_text()
            edited_html = (root / "ches-direct-reader" /
                           updated["snapshot_id"] / "gen.1.html").read_text()
            self.assertIn("and·he-saidMosesto·Town", base_html)
            self.assertIn("And Moses — he said to·Town", edited_html)
            self.assertIn("And David — he came from·Town", edited_html)
            self.assertEqual(source.read_bytes(), original_bytes)
            with patch("sys.argv", [
                "reader", "--private-root", str(folder),
                "--confirm-machine-readable-use-permission",
                "--audit-only", "--olt-owner-approved-candidates",
            ]):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(main(), 0)
            counts = json.loads(output.getvalue())
            self.assertEqual(counts["olt_owner_approved_candidate_reorders_applied"], 2)
            self.assertNotIn("Moses", output.getvalue())
            self.assertNotIn(str(folder), output.getvalue())


if __name__ == "__main__":
    unittest.main()
