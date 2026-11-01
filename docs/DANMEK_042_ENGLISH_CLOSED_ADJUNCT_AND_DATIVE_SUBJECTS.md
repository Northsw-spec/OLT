# DANMEK-042 — English subject after a complete adjunct or dative object frame

**2026-11-01.** This is a real-English corpus study using the owner's PRIVATE CHES ZIP, **929 chapters and 23,144 verse records**. Neither this audit nor the active grammar engine compares CHES with Hebrew, Aramaic, Greek, OSHB/WLC, morphology or lemmas. Only aggregate findings and invented English fixtures appear in PUBLIC GitHub.

## Why the general clause parser needed another role

An English subject can occur after a *complete, already closed prepositional adjunct* rather than immediately after the finite predicate. For example, in wholly synthetic tokens:

`and·he-is-reigning instead-of·him Rowan son-of Oren`

English clause structure supports `Rowan son-of Oren - ·he-is-reigning instead-of·him`; the closed `instead-of·him` phrase is not the subject and does not consume `Rowan`. This is a **whole-subject structural move**, not a special case for an actual biblical proper name.

A second frame has a finite *dative/transmission verb*, a closed pronominal recipient, a complete named English subject, and **another, explicitly separate object** introduced by standalone `»`. An invented example:

`and·he-is-telling to·her Mira » all-of matters`

The possible grammatical agent is `Mira`, not the earlier `to·her` recipient or the object introduced by `»`. The final derived reader places the complete subject before the finite verb while retaining the original recipient and object.

## Real CHES English source census

A **conservative private original English fragment audit** scanned 929 chapters. The candidate classifier distinguished incomplete subjects, coordinated person groups and already-preposed subjects:

| Observed category | Raw contexts matching initial frame | Complete candidate noun phrases after safety guards |
|---|---:|---:|
| Intransitive motion/reign/appearance/dwelling + one closed adjunct + following name-shaped English subject | 107 | **9** |
| Finite verb + English closed recipient + name-shaped nominal + standalone marked object | 2,004 | **12** |

These are **21 structured source candidates**, not 21 verified new edits. The initial counts include many contexts with no following name or incomplete phrase, so they are **not** evidence of 2,111 grammatical defects. Actual new subject moves in the derived reader, including interactions with earlier v3 rules, require executing the active `build_current_english` pipeline over the private source ZIP; counts must not be invented.

Both grammar classes are expressed as **lexical-class and syntactic-frame constraints**, not case-by-case biblical person overrides. No fixed token distance is imposed across the *whole verse*, but this stage recognizes **one independently complete adjunct/recipient phrase** before the subject. Arbitrary multiple interposed clauses remain unresolved.

## Engineering and safety constraints

- Upgrade **the single active** `scripts/danmek_039_english_only.py` to revision v4, not a new v9 snapshot or older reader.
- `CLOSED_INTRANSITIVE_ADJUNCT_FRAMES` groups English intransitive predicates with *complete* adjuncts (`instead-of·him`, `from·there`, compatible `to·him` etc.). An unclosed `from` or `to` never authorizes moving the next name.
- `DATIVE_PREDICATES_WITH_MARKED_OBJECT` permits a complete nominal between pronominal recipient and standalone `»` where a compatible English transmission/reporting verb supplies a dative/agent/object frame. Without the marker, keep the earlier DANMEK-041 explicit quotation-opening requirement, or **abstain**.
- If `NAME - finite verb` already identifies an **embedded clause**, do not take the embedded subject for an outer verb. Reject subjects with missing title/kinship continuation or a PDF marker between an apparent name and its role phrase.
- Recognize only complete, non-coordinated subject phrases. Ambiguous transitive objects, preposed subjects and interrupted names are unchanged; the marker `»` is not removed or duplicated.
- No older DANMEK, CHES-bridge or `olt_core` imports; original private CHES JSON is never changed. One current local English HTML/TXT reader can be regenerated atomically.
- Extend the dedicated GitHub Ubuntu gate with **synthetic positive and negative** tests for each class, multiple clauses, incomplete/coordinate phrase, double-claiming an embedded subject, marker retention, private source integrity and single-current-reader behavior.

## Next development / known limit

The 21 candidate source structures provide a controlled real-corpus basis for extending subject identification past **one complete intervening English phrase**. This is still not a complete English dependency parser capable of inferring every subject through multiple embedded clauses, distant relative phrases, free adjunct sequences, appositives or quotation boundaries. No global grammar certification or public publication is claimed.
