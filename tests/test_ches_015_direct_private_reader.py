"""CHES-015 minimal offline private source reader; invented English ONLY.

The public tests use no original CHES words, source PDFs or private file data.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr

from scripts.ches_015_direct_private_reader import (
    CHES015ReaderError, build_private_reader, main,
)
from scripts.ches_import import NEH7_PRIMARY_VERSES, write_private_json
from scripts.danmek_008_english_display import (
    DanMek008DisplayError, simplify_sur_faces_for_olt_view,
)


ARTIFICIAL = 'FAKE-ENGLISH<ruby data-x="&">NO-LICENSED-WORDS</ruby>'


def invented_chapter(prefix: str, chapter: int, *,
                     alternate_neh7: bool = False, source_sha: str | None = None) -> dict:
    numbers = NEH7_PRIMARY_VERSES if alternate_neh7 else (1, 2)
    rows = []
    for n in numbers:
        alt = (
            {"original_pdf_alternate_verse_number_not_oshb_crosswalk": n - 1}
            if alternate_neh7 and n >= 69 else {}
        )
        rows.append({
            "reference": f"{prefix}.{chapter}.{n}",
            "publication_status": "BLOCKED",
            "english_draft_status": "CHES_SOURCE_ONLY_UNALIGNED",
            "explicit_original_pdf_verse_anchor_page": 1,
            "explicit_original_pdf_verse_anchor_y": float(n * 5),
            "source_ches_spans_NOT_OLT_TRANSLATION": [{
                "page": 1, "pdf_x": 14.0,
                "pdf_y": float(n * 5 + 1),
                "original_ches_line_text": f"{ARTIFICIAL} Verse {n}",
            }],
            **alt,
        })
    return {
        "source_origin_url": (
            "https://www.scripture4all.org/OnlineInterlinear/OTpdf/"
            f"{prefix}{chapter}.pdf"
        ),
        "book": prefix, "chapter": chapter,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "original_source_pdf_sha256": source_sha or f"{chapter:064x}",
        "source_original_index_sha256": "b" * 64,
        "source_pdf_byte_length": 3000,
        "source_pdf_page_count": 1,
        "verses_extracted": len(numbers),
        "ches_pdf_green_spans": len(numbers),
        "owner_attested_machine_readable_permission_no_public_distribution": True,
        "source_chapter_verse_count_independent_oshb_qa": "NOT_DONE",
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "independent_grammar_or_sense_approved": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }


class TestPrivateDirectSourceReader(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source = self.base / "ches"
        self.source.mkdir(mode=0o700)

    def add(self, prefix="gen", chapter=1, **kw):
        target = self.source / f"{prefix}.{chapter}.json"
        write_private_json(invented_chapter(prefix, chapter, **kw), target)
        return target

    def test_private_html_escapes_synthetic_fragment_and_preserves_exact_words(self):
        original = self.add().read_bytes()
        with patch("urllib.request.urlopen", side_effect=AssertionError("NETWORK NOT USED")):
            result = build_private_reader(self.source, render=True)
        self.assertEqual(result["observed_chapter_count"], 1)
        self.assertEqual(result["observed_verse_count"], 2)
        self.assertEqual(result["observed_source_fragment_count"], 2)
        self.assertFalse(result["source_fragment_text_linguistically_modified"])
        self.assertFalse(result["independent_english_olt_translation_produced"])
        self.assertFalse(result["original_pdf_bytes_independently_rehashed"])
        self.assertFalse(result["public_distribution_permitted_by_this_tool"])
        self.assertEqual(result["publication_status"], "BLOCKED")
        self.assertEqual(result["private_html_pages_written_or_reused"], 2)
        self.assertNotIn(ARTIFICIAL, json.dumps(result))
        self.assertNotIn(str(self.source), json.dumps(result))
        output = self.base / "ches-direct-reader" / result["snapshot_id"]
        page = (output / "gen.1.html").read_text(encoding="utf-8")
        self.assertIn("FAKE-ENGLISH&lt;ruby", page)
        self.assertIn("NO-LICENSED-WORDS&lt;/ruby&gt;", page)
        self.assertNotIn('<ruby data-x="&">', page)
        self.assertIn("gen.1.1", page)
        self.assertIn('default-src \'none\'', page)
        self.assertIn('name="robots" content="noindex', page)
        self.assertIn("gen.1.html", (output / "index.html").read_text())
        self.assertEqual(output.stat().st_mode & 0o777, 0o700)
        self.assertEqual((output / "gen.1.html").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.source / "gen.1.json").read_bytes(), original)

    def test_optional_faces_view_changes_only_display_not_original_or_prior_snapshot(self):
        doc = invented_chapter("gen", 1)
        first = doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0]
        first["original_ches_line_text"] = "Synthetic sur faces with c the the"
        second = doc["verses"][1]["source_ches_spans_NOT_OLT_TRANSLATION"]
        second[0]["original_ches_line_text"] = "sur"
        split = dict(second[0])
        split["pdf_x"] = second[0]["pdf_x"] + 15
        split["original_ches_line_text"] = "faces"
        second.append(split)
        doc["ches_pdf_green_spans"] = 3
        target = self.source / "gen.1.json"
        write_private_json(doc, target)
        original = target.read_bytes()

        faithful = build_private_reader(self.source, render=True)
        simplified = build_private_reader(
            self.source, render=True, olt_display_faces=True,
        )
        self.assertNotEqual(faithful["snapshot_id"], simplified["snapshot_id"])
        self.assertEqual(simplified["mode"], "PRIVATE_OLT_ENGLISH_DISPLAY")
        self.assertEqual(simplified["olt_display_sur_faces_to_faces_count"], 2)
        self.assertTrue(simplified["source_fragment_text_linguistically_modified"])
        self.assertFalse(simplified["olt_display_hebrew_lemma_alignment_verified"])
        self.assertEqual(target.read_bytes(), original)

        base = self.base / "ches-direct-reader"
        faithful_page = (base / faithful["snapshot_id"] / "gen.1.html").read_text()
        derived_page = (base / simplified["snapshot_id"] / "gen.1.html").read_text()
        self.assertIn("Synthetic sur faces with c the the", faithful_page)
        self.assertIn('>sur</span><span class="gloss">faces</span>', faithful_page)
        self.assertIn("Synthetic faces with c the the", derived_page)
        self.assertEqual(derived_page.count('>faces</span>'), 1)
        self.assertNotIn("Synthetic sur faces", derived_page)
        self.assertIn("c the the", derived_page)
        self.assertEqual(
            build_private_reader(
                self.source, render=True, olt_display_faces=True,
            )["snapshot_id"], simplified["snapshot_id"],
        )
        self.assertEqual(target.read_bytes(), original)

    def test_sur_faces_rule_is_exact_and_never_crosses_verses_or_erases_articles(self):
        examples = [
            (["sur faces"], ["faces"], 1),
            (["Sur faces"], ["Faces"], 1),
            (["sur", "faces"], [None, "faces"], 1),
            (["Sur", "faces"], [None, "Faces"], 1),
            (["the", "the", "c", "sur", "faces"],
             ["the", "the", "c", None, "faces"], 1),
            (["surfaces", "surface", "sur facing"],
             ["surfaces", "surface", "sur facing"], 0),
            (["sur", "the", "faces"], ["sur", "the", "faces"], 0),
            (["sur", "faces!"], ["sur", "faces!"], 0),
            (["abcsur faces"], ["abcsur faces"], 0),
            (["sur faceless"], ["sur faceless"], 0),
        ]
        for original, expected, count in examples:
            with self.subTest(original=original):
                before = list(original)
                result, changed = simplify_sur_faces_for_olt_view(original)
                self.assertEqual((result, changed), (expected, count))
                self.assertEqual(original, before)
        self.assertEqual(simplify_sur_faces_for_olt_view(["sur"])[1], 0)
        self.assertEqual(simplify_sur_faces_for_olt_view(["faces"])[1], 0)
        for unsafe in ("sur faces", [None], [123], {}):
            with self.assertRaises(DanMek008DisplayError):
                simplify_sur_faces_for_olt_view(unsafe)

    def test_faces_cli_audit_counts_without_creating_html(self):
        doc = invented_chapter("gen", 1)
        doc["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "Synthetic sur faces"
        write_private_json(doc, self.source / "gen.1.json")
        argv = ["reader", "--private-root", str(self.source),
                "--confirm-machine-readable-use-permission",
                "--audit-only", "--olt-display-faces"]
        with patch("sys.argv", argv), patch(
            "urllib.request.urlopen", side_effect=AssertionError("NO NETWORK")
        ):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["olt_display_sur_faces_to_faces_count"], 1)
        self.assertEqual(result["private_html_pages_written_or_reused"], 0)
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_audit_only_has_no_filesystem_output_and_supports_partial_archive(self):
        self.add("gen", 1)
        self.add("gen", 3)
        summary = build_private_reader(self.source)
        self.assertEqual(summary["observed_chapter_count"], 2)
        self.assertEqual(summary["local_internal_numbering_gaps"], 1)
        self.assertFalse(summary["all_929_39_present_by_count_only"])
        self.assertEqual(summary["private_html_pages_written_or_reused"], 0)
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_special_original_neh7_primary_and_alternative_numbers_not_rewritten(self):
        self.add("neh", 7, alternate_neh7=True)
        result = build_private_reader(self.source, render=True)
        folder = self.base / "ches-direct-reader" / result["snapshot_id"]
        page = (folder / "neh.7.html").read_text()
        self.assertIn("neh.7.67", page)
        self.assertNotIn('neh.7.68</span>', page)
        self.assertIn("neh.7.69 (source alternate 68)", page)
        self.assertIn("neh.7.73 (source alternate 72)", page)
        self.assertEqual(result["observed_verse_count"], 72)

    def test_repeat_is_idempotent_and_changed_existing_reader_never_overwritten(self):
        self.add()
        result = build_private_reader(self.source, render=True)
        page = (self.base / "ches-direct-reader" / result["snapshot_id"] / "gen.1.html")
        original = page.read_bytes()
        repeated = build_private_reader(self.source, render=True)
        self.assertEqual(repeated["snapshot_id"], result["snapshot_id"])
        self.assertEqual(page.read_bytes(), original)
        page.write_text("OWNER EDIT: KEEP", encoding="utf-8")
        page.chmod(0o600)
        with self.assertRaisesRegex(CHES015ReaderError, "CONFLICT"):
            build_private_reader(self.source, render=True)
        self.assertEqual(page.read_text(), "OWNER EDIT: KEEP")

    def test_changed_source_produces_new_snapshot_not_overwrite(self):
        path = self.add()
        first = build_private_reader(self.source, render=True)
        data = invented_chapter("gen", 1)
        data["verses"][0]["source_ches_spans_NOT_OLT_TRANSLATION"][0][
            "original_ches_line_text"
        ] = "ANOTHER-SYNTHETIC-TEXT"
        write_private_json(data, path)
        second = build_private_reader(self.source, render=True)
        self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
        self.assertTrue((self.base / "ches-direct-reader" /
                         first["snapshot_id"] / "gen.1.html").exists())
        self.assertTrue((self.base / "ches-direct-reader" /
                         second["snapshot_id"] / "gen.1.html").exists())

    def test_rejects_duplicate_pdf_hash_and_multiple_index_snapshot_hashes(self):
        self.add("gen", 1)
        self.add("exo", 1)
        with self.assertRaisesRegex(CHES015ReaderError, "DUPLICATE_ORIGINAL_PDF"):
            build_private_reader(self.source)
        self.add("exo", 1, source_sha="f" * 64)
        second = invented_chapter("exo", 1, source_sha="f" * 64)
        second["source_original_index_sha256"] = "a" * 64
        write_private_json(second, self.source / "exo.1.json")
        with self.assertRaisesRegex(CHES015ReaderError, "MIXED_SOURCE_INDEX"):
            build_private_reader(self.source)

    def test_malformed_source_symlink_outside_archive_and_public_permissions_fail(self):
        path = self.add()
        path.chmod(0o644)
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(self.source)
        path.chmod(0o600)
        other = self.source / "mystery.txt"
        other.write_text("not a source chapter")
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(self.source)
        other.unlink()
        path.rename(self.source / "original.json")
        path.symlink_to(self.source / "original.json")
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(self.source)
        path.unlink()
        (self.source / "original.json").rename(path)
        self.source.chmod(0o755)
        with self.assertRaises(CHES015ReaderError):
            build_private_reader(self.source)

    def test_invalid_content_and_duplicate_json_fail_without_rendering(self):
        path = self.add()
        for raw in (
            '{"book":"gen","book":"gen"}',
            '{"reference": NaN}',
            '{"book":"gen","verses": ["'+ARTIFICIAL+'"]}',
        ):
            with self.subTest(raw=raw[:30]):
                path.write_text(raw, encoding="utf-8")
                path.chmod(0o600)
                with self.assertRaises(CHES015ReaderError) as caught:
                    build_private_reader(self.source, render=True)
                self.assertNotIn(ARTIFICIAL, str(caught.exception))
        self.assertFalse((self.base / "ches-direct-reader").exists())

    def test_cli_stdout_contains_only_status_counts_and_sanitized_error(self):
        self.add()
        argv = ["reader", "--private-root", str(self.source),
                "--confirm-machine-readable-use-permission", "--audit-only"]
        with patch("sys.argv", argv):
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(), 0)
            self.assertEqual(json.loads(stdout.getvalue())["checkpoint"],
                             "CHES-015-DIRECT")
            self.assertNotIn(ARTIFICIAL, stdout.getvalue())
        (self.source / "gen.1.json").write_text('{"private": "'+ARTIFICIAL+'"}')
        with patch("sys.argv", argv):
            stderr = io.StringIO()
            with redirect_stderr(stderr), self.assertRaises(SystemExit) as failure:
                main()
            self.assertEqual(failure.exception.code, 2)
            self.assertNotIn(ARTIFICIAL, stderr.getvalue())
            self.assertNotIn(str(self.source), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
