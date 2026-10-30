"""Fail-closed layout regression for the OLT-022 owner-selected underword."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from render_genesis_1_1_html import build_html, VERSE, POLICY, OUTPUT, MAIN


class TestOLT023(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verse = json.loads(VERSE.read_text(encoding='utf-8'))
        cls.policy = json.loads(POLICY.read_text(encoding='utf-8'))

    def test_layout_is_derived_and_blocked(self):
        html = build_html(self.verse, self.policy)
        self.assertEqual(html, OUTPUT.read_text(encoding='utf-8'))
        self.assertIn('data-primary-source-token="01xeN"', html)
        self.assertIn('class="primary">In</span><span class="secondary">with', html)
        self.assertIn('--main-link: #5B277D; --under-link: #2463A6;', html)
        self.assertEqual(html.count('class="linked-word"'), 1)
        self.assertIn('class="supplement">[of His Power]<sup>', html)
        self.assertIn('lang="he" dir="rtl"', html)
        self.assertIn('Release BLOCKED', html)
        self.assertIn('NOT APPROVED BIBLE TEXT', html)
        self.assertIn('NOT a proven lexical identification', html)
        self.assertIn('ABSENT from Genesis 1:1', html)
        self.assertEqual(MAIN, self.verse['main_english_proposal'])

    def test_reject_wrong_primary_verse(self):
        verse = copy.deepcopy(self.verse)
        verse['main_english_proposal'] = 'With the Beginning God created.'
        with self.assertRaisesRegex(ValueError, 'changed English main line'):
            build_html(verse, self.policy)

    def test_reject_unverified_published_status(self):
        verse = copy.deepcopy(self.verse)
        verse['publication_status'] = 'PUBLISHED'
        with self.assertRaises(ValueError):
            build_html(verse, self.policy)

    def test_reject_other_verse_or_global_link(self):
        policy = copy.deepcopy(self.policy)
        policy['underwords'][0]['reference'] = 'Gen.1.2'
        with self.assertRaisesRegex(ValueError, 'source-to-display'):
            build_html(self.verse, policy)
        policy = copy.deepcopy(self.policy)
        policy['automatically_generalize_to_other_bet'] = True
        with self.assertRaisesRegex(ValueError, 'globally'):
            build_html(self.verse, policy)

    def test_reject_false_grammar_or_homonym_signoff(self):
        for key in ('this_verse_instrumental_bet_independently_established',
                    'underword_is_verified_homonym', 'source_lexeme_means_jesus'):
            with self.subTest(key=key):
                policy = copy.deepcopy(self.policy)
                policy['underwords'][0][key] = True
                with self.assertRaisesRegex(ValueError, 'lexical fact'):
                    build_html(self.verse, policy)

    def test_reject_missing_original_source_identity(self):
        verse = copy.deepcopy(self.verse)
        verse['source_alignment'][0]['source_token_id'] = 'WRONG'
        with self.assertRaisesRegex(ValueError, 'seven Genesis'):
            build_html(verse, self.policy)
        verse = copy.deepcopy(self.verse)
        verse['source_alignment'][0]['source_morphology'] = 'INVALID'
        with self.assertRaisesRegex(ValueError, 'bet source anchor'):
            build_html(verse, self.policy)

    def test_reject_lost_power_note_or_scholarly_boundary(self):
        verse = copy.deepcopy(self.verse)
        verse['footnote_drafts'] = []
        with self.assertRaisesRegex(ValueError, 'Power footnote'):
            build_html(verse, self.policy)
        policy = copy.deepcopy(self.policy)
        policy['underwords'][0]['footnote']['english'] = 'With is definitely literal.'
        with self.assertRaisesRegex(ValueError, 'established Hebrew grammar'):
            build_html(self.verse, policy)

    def test_reject_missing_evidence_and_colors(self):
        policy = copy.deepcopy(self.policy)
        policy['underwords'][0]['footnote']['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'scholarly evidence'):
            build_html(self.verse, policy)
        policy = copy.deepcopy(self.policy)
        policy['underwords'][0]['primary_word_color'] = '#000000'
        with self.assertRaisesRegex(ValueError, 'colors'):
            build_html(self.verse, policy)


if __name__ == '__main__':
    unittest.main()
