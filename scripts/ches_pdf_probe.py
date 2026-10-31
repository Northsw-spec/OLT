"""Inspect a locally supplied Scripture4All chapter PDF without exporting any CHES text.

This is a safe development diagnostic ONLY. Source PDF, source CHES words,
PDF artwork and extracted full text are NOT persisted in public repository.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
import argparse
from pathlib import Path


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",required=True,type=Path)
    opts=p.parse_args()
    import fitz
    raw=opts.pdf.read_bytes()
    if not raw.startswith(b"%PDF-") or len(raw)<5000 or len(raw)>30_000_000:
        raise ValueError("Unrecognized or unexpectedly sized chapter PDF")
    print("PDF_SHA256",sha256(raw).hexdigest())
    with fitz.open(stream=raw,filetype="pdf") as doc:
        print("PDF_PAGES",len(doc))
        for i,page in enumerate(doc):
            counts=Counter()
            spans=[]
            for blk in page.get_text("dict")["blocks"]:
                if "lines" not in blk: continue
                for line in blk["lines"]:
                    for s in line["spans"]:
                        t=s["text"].strip()
                        if not t: continue
                        col=s["color"]
                        counts[f"{col:06x}"]+=1
                        spans.append((round(s["bbox"][0],1),round(s["bbox"][1],1),
                                      round(s["bbox"][2],1),round(s["bbox"][3],1),
                                      f"{col:06x}",round(s["size"],1),len(t),t))
            print("PAGE",i+1,"SIZE",tuple(round(v) for v in page.rect),"SPAN_COUNT",len(spans),"COLORS",counts.most_common(8))
            for s in spans[:20]:
                # No copyrighted words in logs; only geometry and character counts.
                print("SPAN_GEOMETRY",s[:7])
            for s in spans:
                if s[7].strip() in {"1:1","1:2","1:3","1:4","1:5","1:6","1:7","1:8","1:9","1:10","1:11","1:12","1:13","1:14","1:15","1:16","1:17","1:18","1:19","1:20","1:21","1:22","1:23","1:24","1:25","1:26","1:27","1:28","1:29","1:30","1:31"}:
                    print("CHAPTER_VERSE_MARKER",s[7],s[:6])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
