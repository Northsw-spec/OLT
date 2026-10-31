# DANMEK-007 — PERMANENT owner cancellation of divine-referent capitalization

**Latest binding owner decision, 2026-10-31. This overrides and cancels DANMEK-006 in full.**

**No special capitalization of pronouns simply because they refer to God/the LORD.** OLT/DanMek must **not** change `he` to `He`, `him` to `Him`, `his` to `His`, or `himself` to `Himself` based on religious referent. For example, a divine subject does **not** require `·he-is-making` to become `·He-is-making`; retain `·he-is-making` unless **ordinary English orthography** (e.g. beginning of a sentence) independently calls for capitalization. This is **permanent** unless the owner explicitly establishes a new policy.

The owner is **not** asking to modify Biblical Hebrew grammar, the CHES private JSON originals, their source order, proper names, the names God/LORD, or ordinary English sentence capitalization. The separate editorial OLT English word-order preference — put a verified explicit subject before its English verb phrase, while preserving the explicit pronoun — remains active and is independent of the **cancelled** reverential capitalization idea.

## Engineering consequences

- `DANMEK-006` (PR #86) is **REVOKED**, including its policy and future wiring request.
- The unused helper `scripts/danmek_006_divine_pronouns.py` and its dedicated tests must be removed from the active codebase. Nothing may call it or infer pronoun referents for special case styling.
- Remove references to the superseded policy in active masterprompt, engine plan, DanMek-005 notes and current status. This cancellation note is the sole current authority on that retired feature. Git history remains an audit trail, not current instructions.
- Do **not** treat the cancelled feature as a blocker, future engineering milestone, TODO, or required crosswalk. Do not reintroduce divine-referent casing automatically in future conversations.
- Keep untouched CHES source JSON; continue ordinary private OLT English view work, word order and separate YLT-1898 noun/tense decisions as already defined. Full Bible publication remains **BLOCKED** by the existing independent rights and approval gates.

## Verification

A GitHub Actions pass demonstrates code and policy consistency, not that every existing English verse was already rewritten. **The DANMEK-006 helper was never wired into the full Old Testament reader**, so its removal does not require regenerating the 929 source chapter JSON files or rebuilding existing source-faithful HTML snapshots.
