# OLT-PUBLIC-DISCOVERABILITY-001 — Public landing-page hygiene

**Goal:** reduce incidental search-engine association between the OLT project landing pages and a separately licensed source provider. This is a best-effort discoverability reduction, **not** a guarantee of search engine exclusion.

## Rules

- Keep `README.md` **completely empty (zero bytes)** at the owner's explicit request. Keep `docs/STATUS_CURRENT.md` project-centered and provider-neutral. Source origin is retained in the provenance documentation and source manifest.
- Do **not** remove or falsify full bibliographic provenance, original URL, applicable terms, permission limitations, copyright attribution or safety checks from `docs/OLT_CHES_PRIVATE_INGEST.md`, the pinned source manifest, the importer's strict approved-host allowlist, CI integration or private chapter output.
- CHES text and PDFs remain untracked and non-public. These landing-page edits are not a grant of redistribution, derived-language rights or release approval.
- Do not attempt to evade source attribution obligations or misrepresent authorship. Anyone following source manifest references can still identify the provider.
- Public GitHub repository code, file views, pull requests, historic commits, external links, and cached search engine pages can all remain discoverable. **Only changing the repository's GitHub visibility to private, with proper review of forks and copies, meaningfully restricts public visibility.** Even that cannot erase old public archives or existing indexing immediately.
- A local `robots.txt` committed to a GitHub repository does **not** control indexing of GitHub-hosted pages; do not rely on it.

## Maintenance guard

`tests/test_public_landing_discoverability.py` detects a new direct source-provider brand or hostname on the two public landing pages while ensuring the detailed third-party provenance and usage restrictions remain in the public technical records. Future changes to source identity, rights, and security contracts must continue to be verified independently.
