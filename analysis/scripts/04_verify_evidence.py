#!/usr/bin/env python3
"""Re-check every row of analysis/evidence.csv against the repository files:
the quoted text must appear verbatim at the stated line and column.
Exit status 1 if any row fails."""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
bad = 0; n = 0
for row in csv.DictReader(open(os.path.join(HERE, "..", "evidence.csv"), encoding="utf-8")):
    n += 1
    if not row["line"]:
        print("UNLOCATED", row["finding_id"], row["file"]); bad += 1; continue
    text = open(os.path.join(ROOT, row["file"]), encoding="utf-8").read()
    lines = text.split("\n")
    line, col = int(row["line"]), int(row["col"])
    quote = row["quote"].replace("\\xa0", "\u00a0").replace("\\n", "\n")
    start = sum(len(l) + 1 for l in lines[:line - 1]) + col - 1
    if text[start:start + len(quote)] != quote:
        bad += 1
        print("MISMATCH", row["finding_id"], row["file"], line, col, repr(quote[:60]), "found:", repr(text[start:start + 60]))
print(f"{n} rows checked, {bad} failures")
sys.exit(1 if bad else 0)
