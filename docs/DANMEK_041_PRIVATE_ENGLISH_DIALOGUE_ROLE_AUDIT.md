# DANMEK-041 — English-only dialogue-subject and naming-complement evidence

**2026-11-01.** Scope: the sole active English-only grammar core, `scripts/danmek_039_english_only.py`. The author-supplied CHES ZIP was inspected **locally and privately** in full: 929 JSON chapters, 23,144 verse records. **No original-language comparison, alignment, lemma or morphology verification.** No licensed source verse appears in this public report.

## Why the previous subject rule was insufficient

After a reporting verb and a prepositional recipient such as `to·them`, the next capitalized English token has at least two plausible roles:

1. The **speaker** following the recipient, to be relocated before the English reporting predicate if the clause context supports that role.
2. The **subject of direct quoted speech**, which must not be stolen and reassigned to the preceding reporting verb.

An independent source-English scan found **572** reporting predicates with a third-person pronominal recipient, **132** followed immediately by a name-shaped token. The full phrase and conservative direct-speech cue filters narrowed these to **25** original-fragment candidate positions. All 25 were inspected as compact **private English contexts** and were source-structurally consistent with the reporting-speaker role. **This is 25 candidate source structures, not a claim of 25 proven newly corrected verses:** actual applied edits require execution of the current reader and may overlap with other rules.

The negative evidence is equally important: some named tokens after such recipients were demonstrably opening a **quoted proposition** instead of identifying the reporter; cases with an immediately following independent finite predicate, incomplete noun phrase, quoted subject or bare negation are excluded. Even an English word `not` does **not** independently prove that a quotation starts after a speaker.

A second source-English risk concerns marked-object constructions followed by a capitalized term. In a **naming or identification predicate**, that term can be the **name assigned to the object** rather than the grammatical agent. At least one such construction was found in the private corpus. A blanket post-object-to-agent rule would therefore corrupt correct English. The active engine now refuses it.

## Engineering

- `REPORTING_WITH_RECIPIENT` is a bounded English reporting-predicate class, independent of biblical persons and original-language morphology.
- `PRONOMINAL_RECIPIENT` is limited to clearly marked third-person recipient pronouns. First-/second-person recipient constructions can involve direct address or vocatives and are left unresolved.
- `_explicit_direct_speech_start` requires a separate English speech-opening clue after the **full noun phrase**, such as an explicit imperative or a `thus` / `must-not` opening. **Bare `not` is not sufficient.**
- If no such cue exists, the person-shaped token is **NOT moved**. A quotation containing its own subject and finite predicate is preserved.
- A restricted `NAMING_PREDICATES` class prevents `called/named/identified + marked object pronoun + name` from falsely assigning the object's name as the agent.
- Pre-existing supported nonnaming marked-object agents remain eligible. Complete coordinated noun phrases stay protected by DANMEK-040's safeguards.
- The derived text must preserve the **exact number of `»` object markers**. Violations cause a fixed error, never a silent output corruption.
- No new historical reader/v9 is introduced. Only `scripts/danmek_039_english_only.py` is updated to its v3 revision; the one current private English reading is regenerated from source on request.
- A synthetic-only regression suite `tests/test_danmek_041_dialogue_and_role_guards.py` is mandatory in the dedicated GitHub Ubuntu grammar CI, alongside foundation tests. No CHES text is uploaded to GitHub or Actions.

## Open grammar questions

Other long-distance or embedded subject roles remain ambiguous without stronger **English** phrase/sentence evidence. In particular, more general cases involving reported speech, prepositional complements, partial names, coordinated entities, relative clauses and vocatives cannot be auto-corrected solely by a token adjacency rule. The parser must *abstain* rather than guess.

This stage improves correctness and handles one additional demonstrable nonadjacent subject class. It **does not certify that all 23,144 verses are grammatically corrected**, and does not imply approval to publicly distribute CHES-derived text. Publication is still BLOCKED.
