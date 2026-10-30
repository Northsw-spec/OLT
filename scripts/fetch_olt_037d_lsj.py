"""Fetch immutable independent LSJ XML evidence from Perseus, never unpinned master.

Research use only: source lexicon metadata is NOT approval of word sense,
inflected Greek forms, homonyms, morphology, or target English Bible text.
Perseus Digital Library LSJ source data CC BY-SA 4.0 with attribution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request

from olt_core.engine import SourceContractError
from olt_core.sources import ROOT

MANIFEST_PATH = "data/engine/olt_037d_perseus_lsj_source_manifest.json"
_COMMIT = "1c34cdf756c63cf37db61bd366d733431dbd7aa0"
_FILES = {
    "3004": (
        "CTS_XML_TEI/perseus/pdllex/grc/lsj/grc.lsj.perseus-eng12.xml",
        6753569, "0cc4c1906a4f8a0e696002dc83728d55b9cd9806"
    ),
    "3754": (
        "CTS_XML_TEI/perseus/pdllex/grc/lsj/grc.lsj.perseus-eng16.xml",
        12280021, "b8a1ba605424c2df3b67f04190bde804664441c8"
    ),
}


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def read_lsj_source_manifest(root: Path = ROOT) -> dict:
    manifest = json.loads((root / MANIFEST_PATH).read_text(encoding="utf-8"))
    required = {
        "checkpoint": "OLT-037D",
        "source_project": "PerseusDL/lexica",
        "upstream_pinned_commit": _COMMIT,
        "source_data_license": "CC BY-SA 4.0",
        "original_license_file": "license.md",
        "original_license_git_blob_sha1": "033217724f8631eeb12987b30d76e8a62f275ceb",
        "original_source_data_not_vendored": True,
        "record_lexicon_entry_keys_as_source_evidence_only": True,
        "no_lsj_entry_word_sense_auto_assignment": True,
        "no_cross_lexicon_same_spelling_implies_same_contextual_sense": True,
        "independent_classical_lexicon_does_not_replace_koine_specialist_review": True,
        "independent_lexicon_human_review": "NOT_DONE",
        "english_master_lexicon_approval": "NOT_DONE",
        "greek_lemma_approval": "NOT_DONE",
        "publication_status": "BLOCKED",
    }
    if any(manifest.get(k) != v for k, v in required.items()):
        raise SourceContractError("Independent original LSJ source licensing or review contract changed")
    specs = manifest.get("file_specs")
    if not isinstance(specs, list) or len(specs) != 2:
        raise SourceContractError("Required two LSJ source shards missing")
    by_target = {x.get("research_editor_strong"): x for x in specs}
    if set(by_target) != set(_FILES):
        raise SourceContractError("LSJ source target file mapping changed")
    for target, expected in _FILES.items():
        row = by_target[target]
        if (row["upstream_path"], row["original_byte_length"],
                row["original_git_blob_sha1"]) != expected:
            raise SourceContractError("LSJ source Git blob, size or file path is not pinned")
    return manifest


def verify_original_lsj(raw: bytes, spec: dict) -> None:
    if (len(raw) != spec["original_byte_length"] or
        git_blob_sha1(raw) != spec["original_git_blob_sha1"]):
        raise SourceContractError("LSJ TEI XML original Git blob or byte length mismatch")
    try:
        txt = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SourceContractError("LSJ original source file not UTF-8") from exc
    if ("<TEI.2>" not in txt or "<entryFree" not in txt
        or "Perseus" not in txt[:20000]):
        raise SourceContractError("Original LSJ TEI/XML structure/header not recognized")


def download_one_source(spec: dict, commit: str) -> bytes:
    url = ("https://raw.githubusercontent.com/PerseusDL/lexica/" +
           commit + "/" + spec["upstream_path"])
    request = urllib.request.Request(url, headers={
        "User-Agent": "OLT-037D-source-evidence-fetch/1.0",
        "Accept": "application/octet-stream",
    })
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            if response.status != 200:
                raise SourceContractError("LSJ source server did not return HTTP 200")
            raw = response.read(spec["original_byte_length"] + 1)
    except (OSError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise SourceContractError("Original Perseus LSJ source fetch failed") from exc
    verify_original_lsj(raw, spec)
    return raw


def fetch_lsj_source_shards(dest: Path, root: Path = ROOT) -> list[Path]:
    manifest = read_lsj_source_manifest(root)
    if not dest.is_dir():
        raise SourceContractError("LSJ source destination must be an existing temporary directory")
    files = []
    for spec in manifest["file_specs"]:
        destination = dest / spec["filename"]
        if destination.exists():
            raise SourceContractError("Refusing to overwrite an existing LSJ source file")
        raw = download_one_source(spec, manifest["upstream_pinned_commit"])
        destination.write_bytes(raw)
        if destination.read_bytes() != raw:
            raise SourceContractError("Original source bytes altered on local write")
        files.append(destination)
        print(json.dumps({
            "source": "Perseus Digital Library LSJ CC BY-SA 4.0",
            "original_upstream_commit": manifest["upstream_pinned_commit"],
            "source_path": spec["upstream_path"],
            "original_git_blob_sha1": spec["original_git_blob_sha1"],
            "verified_bytes": len(raw),
            "source_status": "ORIGINAL_SOURCE_VALIDATED_NOT_LEMMA_APPROVAL"
        }, ensure_ascii=False, sort_keys=True))
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch exact Perseus LSJ source bytes, research only")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    fetch_lsj_source_shards(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
