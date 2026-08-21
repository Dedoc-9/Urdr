#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fibre_build — regenerate the headless observation harness from fpsdemo.rs.

THE HARNESS IS DERIVED, NEVER A SECOND COPY. It slices `fpsdemo.rs` between the exact-integer
helpers and the entry door — every renderer, the clipper, the digest, the trace loader — and
appends a replay main that emits THE OBJECT beside the digest at every frame instead of every
sixtieth. Nothing in the slice is edited, so the harness cannot drift from the demo it observes:
if it did, it would stop reproducing the committed host checkpoints, which is the one thing the
gate checks.

    python3 hainuwele/parallel/fibre_build.py > /tmp/obs.rs
    rustc -O -o /tmp/obs /tmp/obs.rs
    /tmp/obs spec/attest/fpsdemo-castle-walk.txt 60 --third --sky

The main below is the ONLY authored code, and it is a transcription of fpsdemo's own per-frame
sequence — boom, ring raster, castle, avatar, sky, digest — in that order. A transcription is a
second implementation and could drift; the 43-checkpoint reproduction is what catches it.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "hainuwele", "parallel", "fpsdemo.rs")
START = "// ---- exact integer helpers"
END = "// ---- the entry door"


def slice_source(text=None):
    lines = (text if text is not None else io.open(SRC, encoding="utf-8").read()).splitlines(True)
    i = next(n for n, l in enumerate(lines) if l.startswith(START))
    j = next(n for n, l in enumerate(lines) if l.startswith(END))
    body = "".join(lines[i:j])
    k = next(n for n, l in enumerate(lines) if l.startswith("struct TraceIn {"))
    m = next(n for n, l in enumerate(lines[k:], k) if l.startswith("}") and n > k + 30)
    return body, "".join(lines[k:m + 1])


if __name__ == "__main__":                                       # pragma: no cover
    body, trace = slice_source()
    sys.stdout.write("#![allow(dead_code)]\n#![allow(unused_mut)]\n" + body +
                     "\nconst AV_BOOM8: i64 = 12 * 256;\n" + trace +
                     io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "fibre_main.rs"), encoding="utf-8").read())
