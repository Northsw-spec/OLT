"""Avoid brand-forward OLT landing pages without suppressing source provenance."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BRAND = "scripture" + "4all"
SOURCE_HOST = "www." + SOURCE_BRAND + ".org"


class TestPublicDiscoverability(unittest.TestCase):
    def test_public_readme_is_exactly_zero_bytes(self):
        self.assertEqual((ROOT / "README.md").read_bytes(), b"")

    def test_public_project_landing_pages_do_not_advertise_source_provider(self):
        for name in ("README.md", "docs/STATUS_CURRENT.md"):
            with self.subTest(path=name):
                content = (ROOT / name).read_text(encoding="utf-8").lower()
                self.assertNotIn(SOURCE_BRAND, content.replace(" ", ""))
                self.assertNotIn(SOURCE_HOST, content)

    def test_technical_source_provenance_and_rights_remain_traceable(self):
        doc = (ROOT / "docs/OLT_CHES_PRIVATE_INGEST.md").read_text(encoding="utf-8").lower()
        manifest = (ROOT / "data/engine/olt_ches_source_manifest.json").read_text(encoding="utf-8").lower()
        self.assertIn(SOURCE_HOST, doc)
        self.assertIn(SOURCE_HOST, manifest)
        self.assertIn("public_redistribution_rights_confirmed", manifest)
        self.assertIn("false", manifest)


if __name__ == "__main__":
    unittest.main()
