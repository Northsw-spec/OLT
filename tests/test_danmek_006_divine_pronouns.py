"""DANMEK-006: synthetic-only divine referent capitalization regressions."""
from __future__ import annotations

from dataclasses import replace
import re
import unittest

from scripts.danmek_006_divine_pronouns import (
    DanMekPronounError, VerifiedDivinePronoun,
    capitalize_verified_divine_pronouns,
)


def pin(text: str, surface: str, index: int = 0, *,
        ref: str = "gen.1.7", referent: str = "GOD",
        evidence: str = "synthetic-source-annotation") -> VerifiedDivinePronoun:
    matches = list(re.finditer(
        r"(?<![A-Za-z])" + re.escape(surface) + r"(?![A-Za-z])",
        text,
    ))
    start = matches[index].start()
    return VerifiedDivinePronoun(
        start=start, surface=surface, referent=referent,
        verse_reference=ref, evidence_id=evidence,
    )


class TestDivinePronouns(unittest.TestCase):
    def test_owner_example_god_subject_he_is_making(self):
        source = "and Elohim ·he-is-making »the·atmosphere"
        annotated = (pin(source, "he", referent="GOD"),)
        rendered = capitalize_verified_divine_pronouns(
            source, verse_reference="gen.1.7", mentions=annotated,
        )
        self.assertEqual(
            rendered,
            "and Elohim ·He-is-making »the·atmosphere",
        )
        self.assertEqual(source, "and Elohim ·he-is-making »the·atmosphere")

    def test_human_pronoun_remains_lowercase_even_near_lord(self):
        verse = "And the LORD He spoke to the servant, and he answered him."
        lower = verse.replace("He spoke", "he spoke")
        changed = capitalize_verified_divine_pronouns(
            lower, verse_reference="gen.1.7",
            mentions=[pin(lower, "he", index=0, referent="LORD")],
        )
        self.assertEqual(changed, verse)
        self.assertIn("he answered him.", changed)

    def test_him_his_himself_refer_to_god_even_if_human_is_subject(self):
        verse = "The servant turned to him and heard his word; he praised himself."
        refs = [
            pin(verse, "him", index=0, referent="LORD"),
            pin(verse, "his", index=0, referent="LORD"),
        ]
        changed = capitalize_verified_divine_pronouns(
            verse, verse_reference="gen.1.7", mentions=refs,
        )
        self.assertEqual(
            changed,
            "The servant turned to Him and heard His word; he praised himself.",
        )

    def test_himself_divine_is_capitalized_without_unrelated_mentions(self):
        verse = "The LORD showed himself, and the man he saw looked away."
        changed = capitalize_verified_divine_pronouns(
            verse, verse_reference="gen.1.7",
            mentions=[pin(verse, "himself", referent="LORD")],
        )
        self.assertEqual(changed, verse.replace("himself", "Himself"))

    def test_no_certified_referent_does_not_change_content(self):
        verse = "And God, he said; a human he answered, and said to him."
        self.assertEqual(
            capitalize_verified_divine_pronouns(
                verse, verse_reference="gen.1.7", mentions=(),
            ), verse,
        )

    def test_invalid_verse_reference_or_annotation_fails_closed(self):
        original = "and Elohim ·he-is-making"
        valid = pin(original, "he")
        invalid = [
            replace(valid, start=True),
            replace(valid, start=-1),
            replace(valid, start=len(original)),
            replace(valid, start=0),
            replace(valid, surface="the"),
            replace(valid, surface="He"),
            replace(valid, referent="HUMAN"),
            replace(valid, verse_reference="gen.1.8"),
            replace(valid, evidence_id=""),
            replace(valid, evidence_id="unsafe/path"),
        ]
        for broken in invalid:
            with self.subTest(broken=broken), self.assertRaises(DanMekPronounError):
                capitalize_verified_divine_pronouns(
                    original, verse_reference="gen.1.7", mentions=[broken]
                )
        with self.assertRaises(DanMekPronounError):
            capitalize_verified_divine_pronouns(
                original, verse_reference="unknown", mentions=[valid],
            )
        with self.assertRaises(DanMekPronounError):
            capitalize_verified_divine_pronouns(
                original, verse_reference="gen.1.7", mentions="he",
            )

    def test_duplicate_mentions_or_substring_matches_rejected(self):
        sample = "the he"
        human = VerifiedDivinePronoun(
            start=1, surface="he", referent="GOD",
            verse_reference="gen.1.7", evidence_id="synthetic-case",
        )
        with self.assertRaises(DanMekPronounError):
            capitalize_verified_divine_pronouns(
                sample, verse_reference="gen.1.7", mentions=[human],
            )
        good = pin(sample, "he", index=0)
        with self.assertRaises(DanMekPronounError):
            capitalize_verified_divine_pronouns(
                sample, verse_reference="gen.1.7", mentions=[good, good],
            )


if __name__ == "__main__":
    unittest.main()
