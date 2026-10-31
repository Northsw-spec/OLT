# OLT-PUBLIC-DISCOVERABILITY-001 — Public landing-page hygiene

**Goal:** reduce incidental search-engine association between the OLT project landing pages and a separately licensed source provider. This is a best-effort discoverability reduction, **not** a guarantee of search engine exclusion.

## Rules

- Keep `README.md` **completely empty (zero bytes)** at the owner's explicit request. All public prose documentation (Markdown, HTML, RST, text and similar documentation files) remains provider-name- and provider-domain-neutral. Retain full origin in the machine-readable pinned provenance manifest and importer's source constraints.
- Do **not** remove or falsify full bibliographic provenance, original URLs, the original provider's terms URL, permission limitations, copyright attribution or safety checks from the **pinned source manifest**, the importer's strict approved-host allowlist, CI integration or private chapter output. In prose documentation, use links to the manifest rather than repeating the provider's name and direct URLs. Preserve legal cautions in `docs/OLT_CHES_PRIVATE_INGEST.md`.
- CHES text and PDFs remain untracked and non-public. These landing-page edits are not a grant of redistribution, derived-language rights or release approval.
- Do not attempt to evade source attribution obligations or misrepresent authorship. Anyone following source manifest references can still identify the provider.
- Public GitHub repository code, file views, pull requests, historic commits, external links, and cached search engine pages can all remain discoverable. **Only changing the repository's GitHub visibility to private, with proper review of forks and copies, meaningfully restricts public visibility.** Even that cannot erase old public archives or existing indexing immediately.
- A local `robots.txt` committed to a GitHub repository does **not** control indexing of GitHub-hosted pages; do not rely on it.

## Maintenance guard

`tests/test_public_landing_discoverability.py` checks provider-neutral public entry points and full technical provenance. `tests/test_documentation_source_visibility.py` scans **all tracked checkout documentation** for provider names/domain fragments while ensuring the machine-readable manifest retains original identity, URLs and permission boundaries. Future changes to source identity, rights, and security contracts must continue to be verified independently.
