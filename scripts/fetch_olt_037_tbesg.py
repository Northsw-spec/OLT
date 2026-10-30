"""Read-only fetch of pinned STEPBible TBESG, never from moving 'master'.

Run in CI, or locally with network. The resulting source file is not added to Git.
Strict source-byte checks must pass BEFORE parsing. The original lexicon remains
CC BY 4.0; this script does not license or approve any translated Bible verse.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from olt_core.greek_lexicon import read_tbesg_manifest, verify_tbesg_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch exact pinned STEP TBESG source")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = read_tbesg_manifest(ROOT)
    commit = manifest["pinned_commit"]
    path = manifest["pinned_source_path"]
    url = "https://raw.githubusercontent.com/STEPBible/STEPBible-Data/" + (
        commit + "/" + quote(path, safe="/")
    )
    expected = manifest["expected_byte_length"]
    with urlopen(url, timeout=90) as response:
        raw = response.read(expected + 1)
    # Refuse changed or truncated source and leave no unverified file on disk.
    verify_tbesg_bytes(raw, manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print("OLT-037 pinned TBESG source VERIFIED; "
          f"bytes={len(raw)} git_blob_sha1={manifest['original_source_git_blob_sha1']}; "
          "CC BY 4.0; NO lemma/translation approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
