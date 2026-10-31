"""DanMek-002: synthetic-only YLT authority tests; no CHES English source.

YLT edition metadata/pin are checked; invented Bible sentences exercise
the one-verse noun/tense decisions without giving invented source mappings
false Hebrew-word certification.
"""
from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout

from scripts.danmek_ylt import (
    CANDIDATES, DanMekYLTError, YLT_GIT_BLOB_SHA1,
    _validate_ylt_document, git_blob_sha1, load_private_ylt,
    prepare_public_domain_ylt, propose_ylt_verse_overrides,
    ylt_verse_for_source,
)
from scripts.ches_015_direct_private_reader import build_private_reader
from scripts.ches_import import NEH7_PRIMARY_VERSES, write_private_json
def invented_chapter(prefix: str, chapter: int, *, alternate_neh7: bool = False) -> dict:
    numbers = NEH7_PRIMARY_VERSES if alternate_neh7 else (1, 2)
    rows = []
    for number in numbers:
        row = {
            "reference": f"{prefix}.{chapter}.{number}",
            "publication_status": "BLOCKED",
            "english_draft_status": "CHES_SOURCE_ONLY_UNALIGNED",
            "explicit_original_pdf_verse_anchor_page": 1,
            "explicit_original_pdf_verse_anchor_y": float(number * 5),
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {"page": 1, "pdf_x": 14.0, "pdf_y": float(number * 5+1),
                 "original_ches_line_text": f"SYNTHETIC-ONLY-{number}"}
            ],
        }
        if alternate_neh7 and number >= 69:
            row["original_pdf_alternate_verse_number_not_oshb_crosswalk"] = number-1
        rows.append(row)
    return {
        "source_origin_url": "https://www.scripture4all.org/OnlineInterlinear/OTpdf/"
                             + f"{prefix}{chapter}.pdf",
        "book": prefix, "chapter": chapter,
        "source_book_identifier_is_not_verified_oshb_book_mapping": True,
        "original_source_pdf_sha256": f"{chapter:064x}",
        "source_original_index_sha256": "b"*64,
        "source_pdf_byte_length": 3000,
        "source_pdf_page_count": 1,
        "verses_extracted": len(rows),
        "ches_pdf_green_spans": len(rows),
        "owner_attested_machine_readable_permission_no_public_distribution": True,
        "source_chapter_verse_count_independent_oshb_qa": "NOT_DONE",
        "full_source_text_in_public_git_permitted": False,
        "alignment_with_oshb_words_verified": False,
        "independent_grammar_or_sense_approved": False,
        "olt_english_translation_approved": False,
        "publication_status": "BLOCKED",
        "verses": rows,
    }





def invented_ylt() -> dict:
    books = [
        {"id": "gen", "testament": "OT", "chapters": [
            ["A door is found here", "And he saith", "A gate is here"],
            ["Synthetic next chapter"]
        ]},
        {"id": "exo", "testament": "OT", "chapters": [
            ["A door is found here"]
        ]},
        {"id": "neh", "testament": "OT", "chapters": [
            ["A door is found here"] for _ in range(7)
        ]},
        {"id": "ecc", "testament": "OT", "chapters": [
            ["A door is found here"] for _ in range(12)
        ]},
        {"id": "sng", "testament": "OT", "chapters": [
            ["A door is found here"] for _ in range(8)
        ]},
    ]
    books += [
        {"id": f"ot{i:02}", "testament": "OT",
         "chapters": [["Synthetic neutral sentence"]]} for i in range(34)
    ]
    books += [
        {"id": f"nt{i:02}", "testament": "NT",
         "chapters": [["Synthetic neutral sentence"]]} for i in range(27)
    ]
    return {
        "id": "ylt", "name": "Young's Literal Translation",
        "year": 1898, "license": "Public domain",
        "books": books,
    }


def tiny_source(verse_texts: list[str]) -> dict:
    doc = invented_chapter("gen", 1)
    doc["verses"] = [
        {
            **copy.deepcopy(doc["verses"][0]),
            "reference": f"gen.1.{i+1}",
            "source_ches_spans_NOT_OLT_TRANSLATION": [
                {"page": 1, "pdf_x": 11.0, "pdf_y": 20.0 + i*10,
                 "original_ches_line_text": text}
            ],
        }
        for i, text in enumerate(verse_texts)
    ]
    doc["verses_extracted"] = len(doc["verses"])
    doc["ches_pdf_green_spans"] = len(doc["verses"])
    return doc


class TestYLTAuthority(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name) / ".olt-private"
        self.base.mkdir(mode=0o700)
        self.source_root = self.base / "ches"
        self.source_root.mkdir(mode=0o700)
        self.ylt = invented_ylt()

    def test_ylt_edition_1898_format_and_blob_hash_validation(self):
        raw = json.dumps(self.ylt, ensure_ascii=False).encode()
        self.assertEqual(len(_validate_ylt_document(raw, original_pin=False)["books"]), 66)
        self.assertEqual(git_blob_sha1(raw), hashlib.sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw
        ).hexdigest())
        self.assertEqual(len(YLT_GIT_BLOB_SHA1), 40)
        with self.assertRaises(DanMekYLTError):
            _validate_ylt_document(raw, original_pin=True)
        for broken in [
            {**self.ylt, "year": 2026},
            {**self.ylt, "id": "fake"},
            {**self.ylt, "books": self.ylt["books"][:-1]},
            {**self.ylt, "books": [
                {**self.ylt["books"][0], "chapters": [[""]]},
                *self.ylt["books"][1:]]},
            {"id": "ylt", "books": []},
        ]:
            with self.subTest(case=str(broken.keys())):
                with self.assertRaises(DanMekYLTError):
                    _validate_ylt_document(json.dumps(broken).encode(), original_pin=False)

    def test_invalid_json_and_duplicate_keys_are_refused(self):
        for content in [
            '{"id":"ylt","id":"ylt"}',
            '{"books":NaN}',
            "[1,2,3]",
        ]:
            with self.subTest(length=len(content)), self.assertRaises(DanMekYLTError):
                _validate_ylt_document(content.encode().ljust(120, b" "), original_pin=False)

    def test_noun_portal_becomes_door_only_if_ylt_says_door_in_same_verse(self):
        source = tiny_source(["A portal is here", "An unrelated wording",
                              "A portal in this village"])
        result, counter = propose_ylt_verse_overrides(
            source, prefix="gen", chapter=1, ylt=self.ylt,
        )
        self.assertEqual(result, {("gen.1.1", 1): "A door is here"})
        self.assertEqual(counter["noun_changes"], 1)
        self.assertEqual(counter["tense_changes"], 0)
        self.assertEqual(source["verses"][0][
            "source_ches_spans_NOT_OLT_TRANSLATION"][0][
                "original_ches_line_text"], "A portal is here")
        self.assertNotIn(("gen.1.3", 1), result)  # YLT says gate here, not door.

    def test_ylt_tense_overrides_must_be_verse_specific_not_global(self):
        source = tiny_source(["A portal is here", "And he said",
                              "And he said another time"])
        choices, totals = propose_ylt_verse_overrides(
            source, prefix="gen", chapter=1, ylt=self.ylt,
        )
        self.assertEqual(choices[("gen.1.2", 1)], "And he saith")
        self.assertEqual(totals["tense_changes"], 1)
        self.assertNotIn(("gen.1.3", 1), choices)
        self.assertEqual(source["verses"][1][
            "source_ches_spans_NOT_OLT_TRANSLATION"][0]["original_ches_line_text"],
            "And he said")

    def test_ambiguous_parallel_word_mapping_keeps_original_verse(self):
        source = tiny_source(["The portal is here and he says",
                              "And he said", "The portal is here"])
        self.ylt["books"][0]["chapters"][0][0] = "The door is here, and he saith"
        candidate, counts = propose_ylt_verse_overrides(
            source, prefix="gen", chapter=1, ylt=self.ylt
        )
        self.assertNotIn(("gen.1.1", 1), candidate)
        self.assertEqual(counts["ambiguous_verses_left_unchanged"], 1)

    def test_original_qoh_and_can_prefixes_use_specific_ylt_books(self):
        self.assertEqual(
            ylt_verse_for_source(self.ylt, prefix="qoh", chapter=12, verse=1),
            "A door is found here",
        )
        self.assertEqual(
            ylt_verse_for_source(self.ylt, prefix="can", chapter=8, verse=1),
            "A door is found here",
        )
        for prefix, chapter in (("qoh", 13), ("can", 9)):
            self.assertIsNone(ylt_verse_for_source(
                self.ylt, prefix=prefix, chapter=chapter, verse=1,
            ))

    def test_ylt_verse_missing_and_neh7_numerical_dispute_never_guess(self):
        source = invented_chapter("neh", 7, alternate_neh7=True)
        choices, totals = propose_ylt_verse_overrides(
            source, prefix="neh", chapter=7, ylt=self.ylt
        )
        self.assertEqual(choices, {})
        self.assertEqual(totals["unmapped_verses_left_unchanged"], len(NEH7_PRIMARY_VERSES))
        self.assertIsNone(ylt_verse_for_source(
            self.ylt, prefix="neh", chapter=7, verse=69
        ))
        self.assertIsNone(ylt_verse_for_source(
            self.ylt, prefix="gen", chapter=999, verse=1
        ))

    def test_reader_can_apply_ylt_without_source_file_changes_or_network(self):
        raw = tiny_source(["A portal is here", "And he said"])
        path = self.source_root / "gen.1.json"
        write_private_json(raw, path)
        before = path.read_bytes()
        with patch(
            "scripts.ches_015_direct_private_reader.load_private_ylt",
            return_value=(self.ylt, "9"*40)
        ), patch("urllib.request.urlopen", side_effect=AssertionError("NO NETWORK")):
            report = build_private_reader(
                self.source_root, render=True, use_ylt_authority=True
            )
        self.assertEqual(report["ylt_noun_edit_count"], 1)
        self.assertEqual(report["ylt_tense_edit_count"], 1)
        self.assertTrue(report["source_fragment_text_linguistically_modified"])
        self.assertFalse(report["independent_english_olt_translation_produced"])
        self.assertTrue(report["ylt_verse_context_not_word_alignment_certified"])
        self.assertEqual(report["publication_status"], "BLOCKED")
        self.assertNotIn("A portal", json.dumps(report))
        result = (self.base / "ches-direct-reader" / report["snapshot_id"] /
                  "gen.1.html").read_text()
        self.assertIn("A door is here", result)
        self.assertIn("And he saith", result)
        self.assertNotIn("A portal is here", result)
        self.assertIn("YLT 1898 guided", result)
        self.assertEqual(path.read_bytes(), before)

    def test_reader_without_ylt_preserves_original_and_is_separate_snapshot(self):
        raw = tiny_source(["A portal is here", "And he said"])
        write_private_json(raw, self.source_root / "gen.1.json")
        normal = build_private_reader(self.source_root, render=True)
        with patch(
            "scripts.ches_015_direct_private_reader.load_private_ylt",
            return_value=(self.ylt, "9"*40)
        ):
            editor = build_private_reader(
                self.source_root, render=True, use_ylt_authority=True
            )
        self.assertNotEqual(normal["snapshot_id"], editor["snapshot_id"])
        page = (self.base / "ches-direct-reader" / normal["snapshot_id"] /
                "gen.1.html").read_text()
        self.assertIn("A portal is here", page)
        self.assertIn("And he said", page)
        self.assertEqual(normal["ylt_noun_edit_count"], 0)
        self.assertFalse(normal["source_fragment_text_linguistically_modified"])

    def test_ylt_unmapped_diagnostics_by_source_prefix_are_counts_only(self):
        qoh = invented_chapter("qoh", 1)
        can = invented_chapter("can", 1)
        can["original_source_pdf_sha256"] = "f" * 64
        write_private_json(qoh, self.source_root / "qoh.1.json")
        write_private_json(can, self.source_root / "can.1.json")
        with patch(
            "scripts.ches_015_direct_private_reader.load_private_ylt",
            return_value=(self.ylt, "8" * 40)
        ), patch("urllib.request.urlopen", side_effect=AssertionError("NO NETWORK")):
            summary = build_private_reader(
                self.source_root, render=False, use_ylt_authority=True
            )
        self.assertEqual(summary["ylt_verses_unmapped_left_unchanged"], 2)
        self.assertEqual(
            summary["ylt_unmapped_verses_by_source_prefix"],
            {"can": 1, "qoh": 1}
        )
        self.assertNotIn("SYNTHETIC-ONLY", json.dumps(summary))
        self.assertNotIn(str(self.source_root), json.dumps(summary))

    def test_preparation_never_accepts_unpinned_public_domain_json(self):
        fake = json.dumps(self.ylt).encode()
        with self.assertRaises(DanMekYLTError):
            prepare_public_domain_ylt(self.source_root, fetch=lambda: fake)
        self.assertFalse((self.base / "ylt-public-domain").exists())

    def test_missing_ylt_private_authority_fails_without_source_leak(self):
        write_private_json(tiny_source(["A portal is here"]),
                           self.source_root / "gen.1.json")
        with self.assertRaisesRegex(
            Exception, "PINNED_PUBLIC_DOMAIN_YLT_SOURCE_REQUIRED"
        ) as ctx:
            build_private_reader(
                self.source_root, render=True, use_ylt_authority=True
            )
        self.assertNotIn("A portal", str(ctx.exception))
        self.assertFalse((self.base / "ches-direct-reader").exists())


if __name__ == "__main__":
    unittest.main()
