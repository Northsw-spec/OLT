"""DANMEK-009: reviewed subject-before-verb order in PRIVATE OLT English.

Never guess syntax from CHES PDF glyph fragments. A rule applies only to an
exact source-JSON SHA and original verse/fragment text with an explicit private
review attestation. Rules, source glosses and derived output stay off public Git.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat

REVISION = "DANMEK-009-REVIEWED-SUBJECT-FIRST-v1"
SCHEMA = "DANMEK-009-private-reviewed-order-v1"
MAX_RULES_BYTES = 4_000_000
_SHA = re.compile(r"[a-f0-9]{64}\Z")
_REF = re.compile(r"[a-zA-Z0-9_-]{1,20}\.[1-9][0-9]*\.[1-9][0-9]*\Z")


class DanMek009Error(ValueError):
    """Fixed error messages; never include private input text or paths."""


def _unique(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            raise DanMek009Error("DUPLICATE_ORDER_MANIFEST_JSON_KEY")
        out[key] = value
    return out


def _required_text(rule: dict, key: str) -> str:
    value = rule.get(key)
    if type(value) is not str or not value or len(value) > 16_000:
        raise DanMek009Error("INVALID_REVIEWED_ORDER_RULE_TEXT")
    return value


def load_private_order_rules(source_folder: Path) -> tuple[dict[str, dict], str]:
    """Read a single fixed private file, with strict permissions and schema."""
    private_dir = source_folder.parent / "olt-english-order"
    path = private_dir / "approved.json"
    if (private_dir.is_symlink() or not private_dir.is_dir()
            or stat.S_IMODE(private_dir.stat().st_mode) & 0o077
            or path.is_symlink() or not path.is_file()
            or stat.S_IMODE(path.stat().st_mode) & 0o077):
        raise DanMek009Error("PRIVATE_ORDER_MANIFEST_MISSING_OR_UNSAFE")
    size = path.stat().st_size
    if not 0 < size <= MAX_RULES_BYTES:
        raise DanMek009Error("INVALID_PRIVATE_ORDER_MANIFEST_SIZE")
    raw = path.read_bytes()
    if len(raw) != size:
        raise DanMek009Error("PRIVATE_ORDER_MANIFEST_CHANGED_DURING_READ")
    try:
        data = json.loads(
            raw.decode("utf-8"), object_pairs_hook=_unique,
            parse_constant=lambda _x: (_ for _ in ()).throw(
                DanMek009Error("INVALID_NONFINITE_ORDER_MANIFEST_VALUE")
            ),
        )
    except (ValueError, UnicodeError) as exc:
        raise DanMek009Error("INVALID_PRIVATE_ORDER_MANIFEST_JSON") from exc
    if (type(data) is not dict or set(data) != {"schema", "rules"}
            or data["schema"] != SCHEMA or type(data["rules"]) is not list):
        raise DanMek009Error("INVALID_PRIVATE_ORDER_MANIFEST_SCHEMA")
    if not 0 < len(data["rules"]) <= 20_000:
        raise DanMek009Error("PRIVATE_ORDER_MANIFEST_MUST_HAVE_REVIEWED_RULES")
    rules: dict[str, dict] = {}
    for rule in data["rules"]:
        if type(rule) is not dict:
            raise DanMek009Error("INVALID_REVIEWED_ORDER_RULE")
        common = {"reference", "chapter_json_sha256", "mode",
                  "source_syntax_reviewed", "review_note",
                  "verb_fragment_index", "original_verb", "original_subject"}
        if rule.get("mode") == "adjacent":
            allowed = common | {"subject_fragment_index"}
        elif rule.get("mode") == "inline":
            allowed = common | {"original_fragment"}
        else:
            raise DanMek009Error("INVALID_REVIEWED_ORDER_MODE")
        if set(rule) != allowed:
            raise DanMek009Error("INVALID_REVIEWED_ORDER_RULE_FIELDS")
        reference = _required_text(rule, "reference")
        sha = _required_text(rule, "chapter_json_sha256")
        if (not _REF.fullmatch(reference) or not _SHA.fullmatch(sha)
                or rule["source_syntax_reviewed"] is not True):
            raise DanMek009Error("UNREVIEWED_OR_UNPINNED_ORDER_RULE")
        note = _required_text(rule, "review_note")
        if not note.strip():
            raise DanMek009Error("EMPTY_ORDER_REVIEW_EVIDENCE")
        for field in ("original_verb", "original_subject"):
            _required_text(rule, field)
        i = rule["verb_fragment_index"]
        if type(i) is not int or not 1 <= i <= 100_000:
            raise DanMek009Error("INVALID_REVIEWED_ORDER_SPAN_INDEX")
        if rule["mode"] == "adjacent":
            j = rule["subject_fragment_index"]
            if type(j) is not int or j != i + 1:
                raise DanMek009Error("ORDER_SUBJECT_NOT_ADJACENT_TO_VERB")
        else:
            _required_text(rule, "original_fragment")
        if reference in rules:
            raise DanMek009Error("DUPLICATE_REVIEWED_ORDER_VERSE")
        rules[reference] = rule
    return rules, hashlib.sha256(raw).hexdigest()


def _subject_first(verb: str, subject: str) -> tuple[str, str]:
    """Move only a literal initial conjunction, never change pronoun casing."""
    for conjunction in ("and·", "And·", "and ", "And "):
        if verb.startswith(conjunction):
            return conjunction[:3] + " " + subject + " — ", verb[len(conjunction):]
    return subject + " — ", verb


def apply_reviewed_order(
    *, reference: str, chapter_sha256: str,
    original: list[str], visible: list[str],
    rules: dict[str, dict],
) -> tuple[list[str], int]:
    """Move one exactly pinned/reviewed phrase; retain all other source text."""
    if reference not in rules:
        return list(visible), 0
    rule = rules[reference]
    if (rule["chapter_json_sha256"] != chapter_sha256
            or len(original) != len(visible)):
        raise DanMek009Error("REVIEWED_ORDER_SOURCE_SHA_OR_SPAN_COUNT_CHANGED")
    i = rule["verb_fragment_index"] - 1
    if not 0 <= i < len(original):
        raise DanMek009Error("REVIEWED_ORDER_FRAGMENT_INDEX_NOT_FOUND")
    result = list(visible)
    verb, subject = rule["original_verb"], rule["original_subject"]
    before_subject, after_subject = _subject_first(verb, subject)
    if not after_subject or not subject.strip():
        raise DanMek009Error("REVIEWED_ORDER_EMPTY_VERB_OR_SUBJECT")
    if rule["mode"] == "adjacent":
        j = i + 1
        if (j >= len(original) or original[i] != verb
                or original[j] != subject or visible[i] != verb
                or visible[j] != subject):
            raise DanMek009Error("REVIEWED_ORDER_FRAGMENT_CONTENT_MISMATCH")
        result[i], result[j] = before_subject, after_subject
    else:
        source = rule["original_fragment"]
        if original[i] != source or visible[i] != source:
            raise DanMek009Error("REVIEWED_ORDER_FRAGMENT_CONTENT_MISMATCH")
        # The verb and explicit subject must occur as one *adjacent* pair,
        # exactly once in the attested source fragment; no fuzzy matching.
        pair = re.compile(re.escape(verb) + r"([ \t]*)" + re.escape(subject))
        matches = list(pair.finditer(source))
        if len(matches) != 1:
            raise DanMek009Error("REVIEWED_ORDER_INLINE_PAIR_NOT_UNIQUE")
        m = matches[0]
        result[i] = source[:m.start()] + before_subject + after_subject + source[m.end():]
    return result, 1
