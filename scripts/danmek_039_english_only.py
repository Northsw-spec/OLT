"""DANMEK-039 — the single ACTIVE CHES English-only grammar entrypoint.

Independent stdlib-only pipeline. No original-language files, morphology,
lexicons, translations or historical DANMEK reader imports. It reads private
CHES English JSON (directory or ZIP) and emits a single derived English
reading; never edits source JSON. Public GitHub contains only code/tests.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
import zipfile

REVISION = "DANMEK-039-ENGLISH-ONLY-SUBJECT-VERB-v5"
CHAPTER = re.compile(r"([a-z0-9]{3})\.([1-9]\d*)\.json\Z")
REFERENCE = re.compile(r"([a-z0-9]{3})\.([1-9]\d*)\.([1-9]\d*)\Z")
FINITE = re.compile(
    r"(?:(?:and|And)·)?(?:he|she|they|we|you|ye|thou)-"
    r"(?:[a-z]+-)*[a-z]+-?\Z"
)
NAME = re.compile(
    r"(?!And\Z|Then\Z|When\Z|That\Z|The\Z|But\Z|For\Z|If\Z|"
    r"He\Z|She\Z|They\Z|His\Z|Her\Z|It\Z|"
    r"I-[a-z]|You-[a-z]|We-[a-z]|They-[a-z]|He-[a-z]|She-[a-z])"
    r"[A-Z][A-Za-z'’-]{1,49}(?:-[A-Za-z'’-]+)*\Z"
)
LOWER_LEXICAL = re.compile(r"[a-z]+(?:-[a-z]+)*\Z")
PREDICATE_STEM = re.compile(r"[a-z]{2,8}\Z")
ING_TAIL = re.compile(r"ing(?:-[a-z]+)*\Z")
# The outer verb and the embedded finite clause have separate subjects.
# A preceding relative marker alone must NOT make the embedded subject the
# subject of the main clause.
SPLIT_PRONOUN = re.compile(r"(?:(?:and|And)·)?(?:he|she|they|we|you|ye|thou)-\Z")
SPLIT_PREFIX = re.compile(r"[a-z]+-\Z")
ATTACHED_OBJECT_PRONOUN = re.compile(r"»·(?:him|her|them|me|you|us|thee)\Z")
SPEECH = frozenset({"said", "says", "saying", "speaking", "spoke"})
# These extra predicates are used ONLY when the recipient is an explicitly
# marked English pronoun and the post-recipient phrase opens demonstrable
# direct speech. Do not broaden the existing nominal-adjacent rules.
REPORTING_WITH_RECIPIENT = SPEECH | frozenset({
    "responding", "responded", "answering", "answered", "telling", "told",
})
PRONOMINAL_RECIPIENT = frozenset({
    "to·him", "to·her", "to·them",
})
CLOSED_ENGLISH_RECIPIENT = frozenset({
    "to·him", "to·her", "to·them", "to·me", "to·you", "to·us",
})
# Closed English adjuncts are complete without consuming the next nominal.
# They support a delayed subject ONLY for compatible intransitive predicates.
# This is a grammatical frame, not a biblical name/verse exception.
CLOSED_INTRANSITIVE_ADJUNCT_FRAMES = {
    "reigning": frozenset({"instead-of·him", "instead-of·her", "instead-of·them"}),
    "reigned": frozenset({"instead-of·him", "instead-of·her", "instead-of·them"}),
    "came": frozenset(CLOSED_ENGLISH_RECIPIENT),
    "coming": frozenset(CLOSED_ENGLISH_RECIPIENT),
    "appeared": frozenset(CLOSED_ENGLISH_RECIPIENT),
    "appearing": frozenset(CLOSED_ENGLISH_RECIPIENT),
    "went": frozenset({"from·there", "from·here"} | CLOSED_ENGLISH_RECIPIENT),
    "going": frozenset({"from·there", "from·here"} | CLOSED_ENGLISH_RECIPIENT),
    "dwelt": frozenset({"in·them", "in·him", "in·her"}),
    "dwelling": frozenset({"in·them", "in·him", "in·her"}),
}
# Recipient + named nominal + separate marked object establishes an English
# dative/agent/object frame, absent any already-preposed overt subject.
DATIVE_PREDICATES_WITH_MARKED_OBJECT = frozenset({
    "giving", "gave", "gives", "taking", "took",
    "telling", "told", "relating", "related",
    "saying", "said", "says", "speaking", "spoke",
})
# PDF fragment markers are NOT grammatical suffixes of a noun phrase.
# Refuse moving a name ahead of an unseen title after such markers.
INTERPOSED_SOURCE_MARKERS = frozenset({"c", "m", "n", "(p)", "(s)", "(n)"})
# English "called it Sheba" can have a name COMPLEMENT, not a new agent.
# A name after the object is not sufficient proof of subjecthood.
NAMING_PREDICATES = frozenset({
    "call", "calls", "called", "calling", "name", "names", "named", "naming",
    "identified", "identifies", "identifying",
})
QUOTE_OPENERS = frozenset({"must-not", "thus"})
IMPERATIVE_YOU = re.compile(r"[a-z]+(?:-[a-z]+)*-you(?:\s*!|!)?\Z")
INTRANSITIVE = frozenset({
    "came", "come", "coming", "went", "going", "arose", "rose",
    "standing", "stood", "resting", "lived", "dwelt", "dying",
    "reigned", "reigning", "sitting", "sat", "appeared", "encamped", "encamping",
    "sojourned", "dwelling", "rejoicing", "fell",
})
SUBJECT_TITLES = frozenset({
    "the·king", "the·prophet", "the·priest", "the·queen", "the·servant",
})
PREPOSITIONS = ("in·", "from·", "to·", "at·", "with·", "before·", "after·")
MAX_JSON_BYTES = 2_000_000
MAX_VERSE_CHARS = 50_000
MAX_FRAGMENTS = 5000
MAX_CHAPTERS = 1200
MAX_VERSES = 35_000


class DanMekEnglishError(ValueError):
    """No private source text in errors."""


def _source_english_chapters(source: Path):
    """Yield (book, chapter, JSON) from private English JSON only.

    Strict shape, no extraction, no symlinks, no path traversal.
    """
    if source.is_symlink() or not source.exists():
        raise DanMekEnglishError("SOURCE_UNAVAILABLE_OR_SYMLINK")
    if source.is_file():
        if source.suffix.lower() != ".zip":
            raise DanMekEnglishError("SOURCE_MUST_BE_PRIVATE_DIR_OR_ZIP")
        try:
            with zipfile.ZipFile(source) as archive:
                members = [
                    m for m in archive.infolist() if not m.is_dir()
                ]
                if not 1 <= len(members) <= MAX_CHAPTERS:
                    raise DanMekEnglishError("INVALID_CHAPTER_FILE_COUNT")
                seen = set()
                for member in sorted(members, key=lambda m: m.filename):
                    chunks = member.filename.split("/")
                    if not (len(chunks) == 1 or
                            len(chunks) == 2 and chunks[0] == "ches"):
                        raise DanMekEnglishError("UNSAFE_ARCHIVE_ENTRY")
                    if member.is_dir() or stat.S_IFMT(member.external_attr >> 16) == stat.S_IFLNK:
                        raise DanMekEnglishError("UNSAFE_ARCHIVE_ENTRY")
                    m = CHAPTER.fullmatch(chunks[-1])
                    if not m or member.file_size > MAX_JSON_BYTES:
                        raise DanMekEnglishError("INVALID_PRIVATE_CHAPTER_ENTRY")
                    identity = (m.group(1), int(m.group(2)))
                    if identity in seen:
                        raise DanMekEnglishError("DUPLICATE_CHAPTER")
                    seen.add(identity)
                    raw = archive.read(member)
                    yield identity[0], identity[1], _read_chapter(raw, *identity)
        except (zipfile.BadZipFile, RuntimeError):
            raise DanMekEnglishError("SOURCE_ZIP_INVALID") from None
    elif source.is_dir():
        files = sorted(source.iterdir(), key=lambda x: x.name)
        if not 1 <= len(files) <= MAX_CHAPTERS:
            raise DanMekEnglishError("INVALID_CHAPTER_FILE_COUNT")
        seen = set()
        for path in files:
            if path.is_symlink() or not path.is_file():
                raise DanMekEnglishError("UNSAFE_SOURCE_ENTRY")
            m = CHAPTER.fullmatch(path.name)
            if not m or path.stat().st_size > MAX_JSON_BYTES:
                raise DanMekEnglishError("INVALID_PRIVATE_CHAPTER_ENTRY")
            identity = (m.group(1), int(m.group(2)))
            if identity in seen:
                raise DanMekEnglishError("DUPLICATE_CHAPTER")
            seen.add(identity)
            yield identity[0], identity[1], _read_chapter(
                path.read_bytes(), *identity,
            )
    else:
        raise DanMekEnglishError("INVALID_SOURCE_TYPE")


def _read_chapter(raw: bytes, book: str, chapter: int) -> dict:
    if len(raw) > MAX_JSON_BYTES:
        raise DanMekEnglishError("CHAPTER_TOO_LARGE")
    try:
        data = json.loads(raw)
        if (type(data) is not dict or data.get("book") != book
                or data.get("chapter") != chapter
                or type(data.get("verses")) is not list):
            raise DanMekEnglishError("CHAPTER_IDENTITY_INVALID")
        if data.get("full_source_text_in_public_git_permitted") is not False:
            raise DanMekEnglishError("SOURCE_PUBLICATION_BOUNDARY_INVALID")
        if not 1 <= len(data["verses"]) <= 300:
            raise DanMekEnglishError("CHAPTER_VERSES_INVALID")
        indexes = []
        for v in data["verses"]:
            if type(v) is not dict or not REFERENCE.fullmatch(str(v.get("reference", ""))):
                raise DanMekEnglishError("VERSE_REFERENCE_INVALID")
            a, b, c = REFERENCE.fullmatch(v["reference"]).groups()
            if (a, int(b)) != (book, chapter):
                raise DanMekEnglishError("VERSE_CHAPTER_MISMATCH")
            indexes.append(int(c))
            spans = v.get("source_ches_spans_NOT_OLT_TRANSLATION")
            if (type(spans) is not list or len(spans) > MAX_FRAGMENTS or
                any(type(x) is not dict or
                    type(x.get("original_ches_line_text")) is not str
                    for x in spans)):
                raise DanMekEnglishError("PRIVATE_VERSE_FRAGMENTS_INVALID")
        if len(set(indexes)) != len(indexes):
            raise DanMekEnglishError("DUPLICATE_VERSE_REFERENCE")
        return data
    except (UnicodeError, json.JSONDecodeError, TypeError):
        raise DanMekEnglishError("PRIVATE_CHAPTER_JSON_INVALID") from None


def _predicates(tokens: list[str]):
    """English finite groups including *all* source-split predicate fragments.

    The CHES English line may split one progressive verb into three PDF
    fragments: "and·he-is-" / "go" / "ing-up". The old parser consumed
    "go" first, thereby leaving "ing-up" outside the predicate. Recognize
    the two-fragment lexical continuation BEFORE the one-word case.
    """
    for i, token in enumerate(tokens):
        whole = FINITE.fullmatch(token) is not None
        split = SPLIT_PRONOUN.fullmatch(token) is not None
        if not (whole or split):
            continue
        end = i + 1
        if not token.endswith("-"):
            yield i, end
            continue
        if end >= len(tokens):
            if whole:
                yield i, end
            continue
        if (end + 1 < len(tokens)
                and LOWER_LEXICAL.fullmatch(tokens[end])
                and ING_TAIL.fullmatch(tokens[end + 1])):
            # e.g. is- go ing-forth / is- be ing-hot.
            end += 2
        elif LOWER_LEXICAL.fullmatch(tokens[end]):
            end += 1
        elif (end + 1 < len(tokens)
              and SPLIT_PREFIX.fullmatch(tokens[end])
              and LOWER_LEXICAL.fullmatch(tokens[end + 1])):
            end += 2
        elif split:
            # An unattached "he-" by itself is not a complete verb.
            continue
        yield i, end


def _english_intransitive_lemma(lemma: str) -> bool:
    """English-only motion and state predicates; exclude transitive 'bring'."""
    return lemma in INTRANSITIVE or lemma.startswith(("going-", "coming-"))


CLOSED_LOCATION_ADVERBS = frozenset({"there", "here"})
CLOSED_DEICTIC_ADJUNCTS = frozenset({
    "to·him", "to·her", "to·them", "to·me", "to·you", "to·us",
    "from·him", "from·her", "from·them", "from·there", "from·here",
    "in·him", "in·her", "in·them", "with·him", "with·her", "with·them",
    "after·him", "after·her", "after·them",
    "before·him", "before·her", "before·them",
    "instead-of·him", "instead-of·her", "instead-of·them",
})


def _complete_english_adjunct_end(tokens: list[str], at: int,
                                  lemma: str) -> int:
    """Skip independently CLOSED English adjuncts without a distance cap.

    Never consume a free-standing 'from' / 'to' / 'in' whose complement
    may be the following name. Never traverse a finite verb or a clause
    boundary; each accepted piece already contains its own complement.
    """
    if not _english_intransitive_lemma(lemma):
        return at
    pos = at
    while pos < len(tokens):
        tok = tokens[pos]
        if tok in (CLOSED_LOCATION_ADVERBS | CLOSED_DEICTIC_ADJUNCTS |
                   CLOSED_INTRANSITIVE_ADJUNCT_FRAMES.get(lemma, frozenset())):
            pos += 1
            continue
        if (lemma in {"going-up", "coming-up"}
                and tokens[pos:pos+2] == ["in·", "·first"]):
            pos += 2
            continue
        break
    return pos


def _subject_phrase(tokens: list[str], i: int) -> int | None:
    """End-exclusive for a COMPLETE bounded English nominal, else None.

    Never silently truncate a coordinated name+title+and+second-person
    nominal, a possessive "-of" head, or a following family/role modifier.
    This guard also applies to nominal subjects after explicit object marks.
    """
    if i >= len(tokens) or not NAME.fullmatch(tokens[i]):
        return None
    head = tokens[i]
    if head.endswith("-of"):
        # e.g. a "name-of hosts" source phrase: head alone is not complete.
        return None
    end = i + 1
    if end < len(tokens):
        nxt = tokens[end]
        if nxt in SUBJECT_TITLES:
            end += 1
        elif nxt in {"son-of", "daughter-of", "king-of", "servant-of",
                     "prophet-of", "priest-of"}:
            if end + 1 >= len(tokens) or not NAME.fullmatch(tokens[end + 1]):
                return None
            end += 2
        elif nxt == "Elohim-of":
            if end + 1 >= len(tokens) or not NAME.fullmatch(tokens[end + 1]):
                return None
            end += 2
    if end < len(tokens):
        next_part = tokens[end]
        if (next_part in INTERPOSED_SOURCE_MARKERS
                and end + 1 < len(tokens)
                and (tokens[end + 1].startswith((
                    "son-of", "daughter-of", "king-of", "servant-of",
                    "priest-of", "prophet-of", "the·", "woman-of"
                )) or NAME.fullmatch(tokens[end + 1]))):
            return None
        if (NAME.fullmatch(next_part)
                or next_part.startswith((
                    "the·", "son-of", "daughter-of", "king-of",
                    "servant-of", "prophet-of", "priest-of",
                    "woman-of", "father-of", "brother-of",
                    "sister-of", "grandee-of", "sons-of", "daughters-of"
                ))
                or next_part.endswith("-of")
                or (
                    next_part.startswith("and·")
                    and not (FINITE.fullmatch(next_part)
                             or SPLIT_PRONOUN.fullmatch(next_part))
                )):
            return None
    return end


def _predicate_lemma(tokens: list[str], start: int, end: int) -> str:
    if (end >= start + 3 and
            ING_TAIL.fullmatch(tokens[end - 1]) and
            LOWER_LEXICAL.fullmatch(tokens[end - 2])):
        # Only classify the lexical English phrase; never rewrite the source.
        return tokens[end - 2] + tokens[end - 1]
    return tokens[end - 1].rsplit("-", 1)[-1]


def _explicit_direct_speech_start(tokens: list[str], i: int) -> bool:
    """Conservative ENGLISH evidence that a speaker's quotation begins.

    This is a necessary *additional* cue, not a proof from name adjacency.
    For example, after "said to them Ahab he-served", Ahab can be the
    subject inside the quotation, not the person who said it.
    """
    if i >= len(tokens):
        return False
    head = tokens[i]
    if head in QUOTE_OPENERS or IMPERATIVE_YOU.fullmatch(head):
        return True
    if head in {"what", "why", "who", "how", "where"}:
        return i + 1 < len(tokens) and tokens[i + 1] in {"?", "? !"}
    return False


def _candidate_slots(tokens: list[str]):
    """English-only subject evidence for each separate finite predicate.

    Roles may be supported by marked objects and recipient phrases. A named
    noun in a DIFFERENT relative/embedded clause is NEVER borrowed as the
    subject of the first predicate. The independent clause can be found
    anywhere in the verse; no arbitrary character-distance window is used.
    """
    for first, predicate_end in _predicates(tokens):
        if first > 0 and tokens[first - 1] == "-":
            continue  # an explicitly preposed subject with a boundary
        lemma = _predicate_lemma(tokens, first, predicate_end)
        prior_named_subject_in_same_clause = (
            first > 0 and NAME.fullmatch(tokens[first - 1]) is not None
            and not tokens[first].startswith(("and·", "And·"))
        )
        subject_at = predicate_end
        post_object = False
        post_recipient = False
        closed_adjunct = False
        locative_marked_object = False
        if (subject_at < len(tokens) and
                ATTACHED_OBJECT_PRONOUN.fullmatch(tokens[subject_at])):
            # This source-English marked object can precede a delayed
            # subject. The predicate's semantic frame must ALSO allow an
            # agent here; naming/identification verbs do not automatically.
            subject_at += 1
            post_object = True
        elif (subject_at < len(tokens) and
              tokens[subject_at] in CLOSED_ENGLISH_RECIPIENT and
              lemma in (REPORTING_WITH_RECIPIENT |
                        DATIVE_PREDICATES_WITH_MARKED_OBJECT)):
            # A reporter after "to·them" can be the quoted-clause subject.
            # Dative verbs also permit NAME + standalone » as strong English
            # role evidence. Both require independent subsequent cues.
            subject_at += 1
            post_recipient = True
        elif (adjunct_end := _complete_english_adjunct_end(
                tokens, subject_at, lemma)) > subject_at:
            # One or several complete adjuncts; no maximum subject
            # distance, but every traversed piece must itself be closed.
            subject_at = adjunct_end
            closed_adjunct = True
        elif (subject_at < len(tokens)
              and tokens[subject_at] in CLOSED_LOCATION_ADVERBS
              and lemma not in NAMING_PREDICATES):
            # A transitively acting agent may follow "there" only when
            # a DIFFERENT object is explicitly marked AFTER its entire
            # nominal phrase. No such guess for "serve there God other..."
            subject_at += 1
            locative_marked_object = True

        subject_end = _subject_phrase(tokens, subject_at)
        if subject_end is None:
            if (subject_at < len(tokens) and
                    NAME.fullmatch(tokens[subject_at])):
                yield None
            continue
        following = tokens[subject_end] if subject_end < len(tokens) else None
        if (following == "-" and subject_end + 1 < len(tokens)
                and (FINITE.fullmatch(tokens[subject_end + 1])
                     or SPLIT_PRONOUN.fullmatch(tokens[subject_end + 1]))):
            # NAME - finite predicate is already a complete *different*
            # subject–verb clause. Do not steal NAME for an outer predicate.
            yield None
            continue
        if post_object:
            # "he called »·her Sheba" may mean that the OBJECT was given
            # the name Sheba: the name is a predicate complement, not an
            # agent. Likewise identification clauses can be ambiguous.
            if (lemma in NAMING_PREDICATES or
                    prior_named_subject_in_same_clause):
                yield None
                continue
            role = "POSTPOSED_AGENT_AFTER_PRONOMINAL_OBJECT"
        elif post_recipient:
            # A following standalone » marks a DIFFERENT object after the
            # entire named nominal. That licenses a dative/agent/object
            # frame for compatible English verbs. Otherwise, require a
            # distinct quotation-opening cue for reporting verbs.
            if (lemma in DATIVE_PREDICATES_WITH_MARKED_OBJECT
                    and following == "»"
                    and not prior_named_subject_in_same_clause):
                role = "DATIVE_AGENT_BEFORE_MARKED_OBJECT"
            elif (lemma in REPORTING_WITH_RECIPIENT
                  and tokens[predicate_end] in PRONOMINAL_RECIPIENT
                  and _explicit_direct_speech_start(tokens, subject_end)):
                role = "REPORTING_SPEAKER_AFTER_PRONOMINAL_RECIPIENT"
            else:
                yield None
                continue
        elif closed_adjunct:
            # No automatic move when a named subject already precedes
            # this same predicate; the post-adjunct name can be an appositive.
            if prior_named_subject_in_same_clause:
                yield None
                continue
            role = "INTRANSITIVE_AGENT_AFTER_CLOSED_ADJUNCT"
        elif locative_marked_object:
            if (following != "»" or prior_named_subject_in_same_clause):
                yield None
                continue
            role = "LOCATIVE_AGENT_BEFORE_SEPARATE_MARKED_OBJECT"
        elif following == "»":
            role = "FINITE_NOMINAL_EXPLICIT_OBJECT"
        elif (lemma in SPEECH and following is not None and (
            following == "to" or (
                following.startswith("to·") and
                not following.startswith("to·to-")
            )
        )):
            role = "SPEAKER_WITH_RECIPIENT"
        elif (lemma in SPEECH and following is not None and
              following.startswith(("and·he-", "and·she-", "he-", "she-"))):
            role = "SPEAKER_BEFORE_NEXT_FINITE_CLAUSE"
        elif lemma in INTRANSITIVE and (
            following is None or
            following.startswith(PREPOSITIONS) or
            following in {"and·he-came", "and·he-went"}
        ):
            role = "INTRANSITIVE_SUBJECT_BOUNDARY"
        elif (first > 0 and tokens[first - 1] == "thus"
              and lemma in SPEECH):
            role = "REPORTING_FORMULA_SUBJECT"
        else:
            yield None
            continue
        yield (first, predicate_end, subject_at, subject_end, role)


def reorder_english_subjects(fragments: list[str]) -> tuple[str, dict]:
    """Return derived private English and aggregate counters, not source edits.

    Each valid edit moves exactly the evidence-backed *complete* subject
    phrase before its related English predicate. Uncertain roles stay intact.
    """
    if (type(fragments) is not list or
            len(fragments) > MAX_FRAGMENTS or
            any(type(x) is not str for x in fragments) or
            len(" ".join(fragments)) > MAX_VERSE_CHARS):
        raise DanMekEnglishError("PRIVATE_ENGLISH_VERSE_INVALID")
    tokens = list(fragments)
    original = " ".join(tokens)
    changes = []
    counts = Counter()
    # Corpus-wide counters distinguish observed English finite structures
    # from grammatically supported and actually moved subjects.
    identified_finite = list(_predicates(tokens))
    counts["english_finite_predicates_seen"] = len(identified_finite)
    counts["english_split_finite_predicates_seen"] = sum(
        SPLIT_PRONOUN.fullmatch(tokens[first]) is not None
        for first, _ in identified_finite
    )
    for match in _candidate_slots(tokens):
        counts["reviewed_finite_noun_contexts"] += 1
        if match is None:
            counts["unresolved_subject_roles"] += 1
            continue
        start, end_pred, start_name, end_name, role = match
        if (start_name < end_pred or
            any(not (end_name <= a or start >= b) for a, b, _, _ in changes)):
            counts["unresolved_subject_roles"] += 1
            continue
        predicate = tokens[start:end_pred]
        nominal = tokens[start_name:end_name]
        if not nominal:
            counts["unresolved_subject_roles"] += 1
            continue
        if predicate[0].startswith(("and·", "And·")):
            conj, head = predicate[0].split("·", 1)
            lead = [conj, " ".join(nominal)]
            # Exact owner-specific glyph placement for a split generating.
            verb = ["·" + head] + predicate[1:]
            dash = [] if (head == "he-is-" and
                          predicate[1:2] == ["generating"]) else ["-"]
            result = " ".join(lead + dash + verb)
        else:
            result = " ".join(nominal) + " - " + " ".join(predicate)
        # A delayed source subject can follow a *marked object pronoun*.
        # Preserve intervening English source fragments AFTER the predicate
        # without deleting, flattening, or reinterpreting their meaning.
        interior = tokens[end_pred:start_name]
        if interior:
            result += " " + " ".join(interior)
        source_end = end_name
        begin = start
        old = " ".join(tokens[begin:source_end])
        if old == result:
            continue
        changes.append((begin, source_end, result, role))
        counts["recognized_subject_roles"] += 1
    # Token-range, not arbitrary substring replacement. Any overlapping
    # clause is rejected, never coalesced or double-moved.
    changes.sort(key=lambda x: x[0])
    if any(a[1] > b[0] for a, b in zip(changes, changes[1:])):
        raise DanMekEnglishError("GRAMMAR_EDITS_OVERLAP")
    display = list(tokens)
    for first, last, replacement, role in reversed(changes):
        display[first:last] = [replacement]
        counts["applied_subject_moves"] += 1
        counts["rule_" + role] += 1
    output = " ".join(display)
    if output.count("»") != original.count("»"):
        raise DanMekEnglishError("OBJECT_MARKER_INTEGRITY_FAILED")
    if not output and original:
        raise DanMekEnglishError("GRAMMAR_OUTPUT_EMPTY")
    return output, dict(sorted(counts.items()))


def _safe_output(path: Path, source: Path) -> None:
    if path.is_symlink() or path.absolute() == source.absolute():
        raise DanMekEnglishError("OUTPUT_PATH_NOT_SAFE")
    if source.is_dir() and source.absolute() in path.absolute().parents:
        raise DanMekEnglishError("OUTPUT_WITHIN_SOURCE_FORBIDDEN")
    if path.exists() and not path.is_dir():
        raise DanMekEnglishError("OUTPUT_NOT_A_DIRECTORY")


def build_current_english(
    source: Path, *, render_current: bool = False,
    output: Path | None = None, require_full_ot: bool = False,
) -> dict:
    """Audit whole private CHES English corpus or create one current OT reader."""
    if type(render_current) is not bool or type(require_full_ot) is not bool:
        raise DanMekEnglishError("INVALID_READER_OPTIONS")
    source = Path(source)
    output = Path(output) if output is not None else (
        source.parent / "ches-english-current"
    )
    if render_current:
        _safe_output(output, source)
    pages = []
    books = defaultdict(list)
    counts = Counter()
    chapter_ids = set()
    source_fingerprint = hashlib.sha256(REVISION.encode("ascii"))
    for book, chap, chapter in _source_english_chapters(source):
        if (book, chap) in chapter_ids:
            raise DanMekEnglishError("DUPLICATE_SOURCE_CHAPTER")
        chapter_ids.add((book, chap))
        lines = []
        for verse in chapter["verses"]:
            spans = verse["source_ches_spans_NOT_OLT_TRANSLATION"]
            raw = [s["original_ches_line_text"] for s in spans]
            source_fingerprint.update(
                (verse["reference"] + "\0" + "\0".join(raw) + "\n").encode("utf-8")
            )
            english, stats = reorder_english_subjects(raw)
            number = int(verse["reference"].rsplit(".", 1)[1])
            lines.append((number, english))
            for k, v in stats.items():
                counts[k] += v
            counts["verses_scanned"] += 1
            if counts["verses_scanned"] > MAX_VERSES:
                raise DanMekEnglishError("VERSES_LIMIT_EXCEEDED")
        counts["chapters_scanned"] += 1
        books[book].append((chap, lines))
        pages.append((f"{book}.{chap}.html", book, chap, lines))
    if require_full_ot and not (
        len(books) == 39 and counts["chapters_scanned"] == 929
        and counts["verses_scanned"] == 23144
    ):
        raise DanMekEnglishError("EXPECTED_CHES_OT_INVENTORY_CHANGED")
    if render_current:
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Do not chmod an existing parent such as /tmp or the user's home.
        temp = Path(tempfile.mkdtemp(
            prefix=".danmek039-", dir=str(output.parent)
        ))
        os.chmod(temp, 0o700)
        previous = output.parent / (output.name + ".previous-private")
        try:
            if previous.exists():
                raise DanMekEnglishError("UNRESOLVED_PREVIOUS_OUTPUT_BACKUP")
            for name, book, chap, lines in pages:
                body = "\n".join(
                    f"<p><sup>{num}</sup> {html.escape(english, quote=True)}</p>"
                    for num, english in lines
                )
                page = (
                    '<!doctype html><html lang="en"><head>'
                    '<meta charset="utf-8">'
                    '<meta http-equiv="Content-Security-Policy" '
                    'content="default-src \'none\';style-src \'unsafe-inline\'">'
                    '<title>Private English reading</title>'
                    '<style>body{max-width:850px;margin:3rem auto;'
                    'font:19px/1.8 Georgia,serif;padding:0 2rem}'
                    'sup{font:12px system-ui;color:#555;margin-right:.5em}'
                    'p{margin:1rem 0}</style></head><body>'
                    '<h1>' + html.escape(book) + ' ' + str(chap) + '</h1>' +
                    body + '</body></html>\n'
                )
                (temp / name).write_text(page, encoding="utf-8")
                (temp / name).chmod(0o600)
            index = [
                "<!doctype html><html lang='en'><meta charset='utf-8'>",
                "<title>Private CHES English OT</title><h1>English OT</h1>",
                "<p>Private reading; not authorized for public distribution.</p>",
            ]
            for book in sorted(books):
                index.append("<h2>" + html.escape(book) + "</h2>")
                for chap, lines in sorted(books[book]):
                    fname = f"{book}.{chap}.html"
                    index.append(
                        f'<a href="{fname}">{chap}</a> '
                    )
                (temp / (book + ".txt")).write_text(
                    "\n\n".join(
                        f"{book.upper()} {chap}\n" +
                        "\n".join(f"{num}. {value}" for num, value in lines)
                        for chap, lines in sorted(books[book])
                    ) + "\n", encoding="utf-8"
                )
                (temp / (book + ".txt")).chmod(0o600)
            index.append("</html>")
            (temp / "index.html").write_text("\n".join(index), encoding="utf-8")
            (temp / "index.html").chmod(0o600)
            (temp / "MANIFEST.json").write_text(
                json.dumps({
                    "revision": REVISION,
                    "source_english_digest": source_fingerprint.hexdigest(),
                    "book_count": len(books),
                    "chapter_count": len(pages),
                    "verse_count": counts["verses_scanned"],
                    "publication_status": "BLOCKED",
                }, sort_keys=True, indent=2) + "\n", encoding="utf-8",
            )
            (temp / "MANIFEST.json").chmod(0o600)
            if output.exists():
                os.replace(output, previous)
            try:
                os.replace(temp, output)
            except Exception:
                if previous.exists():
                    os.replace(previous, output)
                raise
            if previous.exists():
                shutil.rmtree(previous)
        finally:
            if temp.exists():
                shutil.rmtree(temp)
    return {
        "revision": REVISION,
        "mode": "CURRENT_PRIVATE_ENGLISH_OT" if render_current else "AUDIT_ONLY",
        "source_books": len(books),
        "source_chapters": counts["chapters_scanned"],
        "source_verses": counts["verses_scanned"],
        "subject_role_candidates": counts["recognized_subject_roles"],
        "subject_moves_applied": counts["applied_subject_moves"],
        "english_finite_predicates_seen":
            counts["english_finite_predicates_seen"],
        "english_split_finite_predicates_seen":
            counts["english_split_finite_predicates_seen"],
        "unresolved_subject_roles": counts["unresolved_subject_roles"],
        "subject_rule_counts": {
            k.removeprefix("rule_"): v for k, v in sorted(counts.items())
            if k.startswith("rule_")
        },
        "source_ches_modified": False,
        "older_danmek_code_imported": False,
        "original_language_code_imported": False,
        "original_language_comparison_performed": False,
        "publication_status": "BLOCKED",
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="DANMEK-039: CHES English only, subject-before-verb"
    )
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--render-current", action="store_true")
    p.add_argument("--confirm-private-machine-readable-use",
                   action="store_true")
    p.add_argument("--require-full-ot", action="store_true")
    args = p.parse_args()
    if not args.confirm_private_machine_readable_use:
        p.error("Private CHES use permission must be confirmed")
    try:
        result = build_current_english(
            args.source, output=args.output,
            render_current=args.render_current,
            require_full_ot=args.require_full_ot,
        )
    except DanMekEnglishError as e:
        p.exit(2, "DANMEK_039_" + str(e) + "\n")
    except Exception:
        p.exit(2, "DANMEK_039_PRIVATE_READER_FAILED\n")
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
