# CHES NEH7 — Printed source verse-numbering exception (strict and local)

**Scope:** one unusual original source PDF only, `neh7.pdf`, inside the
owner's authorized *private* 929-chapter Old Testament CHES download.
This is **not** a global relaxation of the importer or a remapping to a
different Hebrew edition.

## Observed original source anomaly

The original PDF for Nehemiah 7 prints the primary verse labels
`7:1` through `7:67`, skips primary `7:68`, then prints
`7:69` through `7:73`. On the final source page the last five
primary labels show explicit alternative labels in parentheses:

| Source primary label | Source printed alternative label |
|---|---|
| 7:69 | 7:68 |
| 7:70 | 7:69 |
| 7:71 | 7:70 |
| 7:72 | 7:71 |
| 7:73 | 7:72 |

There are **72 observed primary verse anchors**, but the largest primary
number is **73**. These are different concepts. The missing primary 7:68
must never be fabricated by padding, numbering shifts, duplicate row
creation or by silently borrowing a source text segment from another verse.

This exception is allowed only when the actual PDF text layer contains
all **72 anchors in exact order**, and each of the last five anchors has
its expected literal parenthetical alternative number.
Every earlier verse must lack an alternative number. Reject any other
gap, altered alternative, incomplete anchor or out-of-sequence row.

The private JSON retains the **primary original PDF reference**
(`neh.7.69` etc.) and explicitly stores the alternative as
`original_pdf_alternate_verse_number_not_oshb_crosswalk`.
This is source-layout metadata, **not** an independently validated
Biblical Hebrew/Aramaic → English verse-number crosswalk. Original
OSHB/WLC verse numbering must be independently checked in a later
research checkpoint. The green CHES typography spans remain unaligned
English source evidence and publication remains BLOCKED.

## Scope and tests

The regression suite includes synthetic malformed/missing/duplicated
marker tests for the explicit exception and confirms no general relaxation
for any other book/chapter. The private archive auditor is updated so
a valid `neh.7.json` passes the same exact exception and a forged
or silent-renumbering attempt still fails.

The focused GitHub Actions workflow fetches the real PDF over HTTPS
**with certificate verification enabled**, runs an in-memory true PDF
integration test against the source and checks zero green-fragment loss.
It stores no PDF, licensed glosses, English source words, or private
export as a GitHub commit or Actions artifact. If upstream TLS validation
fails, **investigate the trust chain** instead of using `--insecure`.

This is compatible with the existing importer resume behavior:
successful existing files are not rewritten; the importer proceeds
from `neh.7` if the previous 419 chapters are already present.
The whole 929-chapter download, lexical quality, source crosswalk and
owner signoff are **not** certified by this engineering fix.
