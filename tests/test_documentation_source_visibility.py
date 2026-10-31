"""Provider-neutral prose docs; source attribution stays in technical metadata.

This explicitly avoids modifying source allowlists, importer URLs, copyright
records, Git history or other functional dependencies to manipulate SEO.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROSE_EXTENSIONS = {".md", ".markdown", ".rst", ".txt", ".adoc", ".html", ".tex"}
PROVIDER_PATTERN = re.compile(r"scripture[\s_-]*4[\s_-]*all", re.IGNORECASE)


class TestDocumentationSourceVisibility(unittest.TestCase):
    def test_all_prose_documentation_is_provider_name_and_domain_neutral(self):
        docs = sorted(
            p for p in ROOT.rglob("*")
            if p.is_file() and p.suffix.lower() in PROSE_EXTENSIONS
            and ".git" not in p.relative_to(ROOT).parts
        )
        self.assertGreaterEqual(len(docs), 66, "Unexpected loss of documentation scan coverage")
        failures = []
        for file in docs:
            data = file.read_text(encoding="utf-8")
            if PROVIDER_PATTERN.search(data):
                failures.append(file.relative_to(ROOT).as_posix())
        self.assertEqual(failures, [], "Provider identity exposed in prose docs")
        self.assertEqual((ROOT / "README.md").read_bytes(), b"")

    def test_original_provider_identity_and_terms_are_preserved_in_pinned_manifest(self):
        manifest = json.loads(
            (ROOT / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8")
        )
        host = "scripture" + "4all.org"
        self.assertIn(host, manifest["source_index_url"])
        self.assertIn(host, manifest["source_reference"]["original_pdf_url"])
        self.assertIn(host, manifest["source_terms_url"])
        self.assertIn("Scripture" + "4All", manifest["source"])
        self.assertIs(manifest["public_redistribution_rights_confirmed"], False)
        self.assertIs(manifest["downstream_amharic_derivative_rights_confirmed"], False)
        self.assertEqual(manifest["publication_status"], "BLOCKED")

    def test_document_links_to_manifest_instead_of_deleting_attribution(self):
        doc = (ROOT / "docs/OLT_CHES_PRIVATE_INGEST.md").read_text(encoding="utf-8")
        self.assertIn("../data/engine/olt_ches_source_manifest.json", doc)
        self.assertIn("source_index_url", doc)
        self.assertIn("source_reference.original_pdf_url", doc)
        self.assertIn("copyright", doc.lower())
        self.assertIn("terms", doc.lower())
        self.assertIn("NOT", doc)


if __name__ == "__main__":
    unittest.main()
