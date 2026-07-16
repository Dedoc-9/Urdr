#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""verify_complex.py - the real authority bridge for calculationViz.

Reads a URDR-COMPLEX-1 JSON exported by the Topology editor and runs the GATED
homology module on its `maximal` simplices, printing the AUTHORITATIVE Betti
numbers + Euler characteristic. This is the MEASURED path the in-app
"Verify with Engine" button stands in for (the browser shows an exact 𝔽₂
PREVIEW; this reproduces it through the reference module under the repo's gate).

Usage:
  PYTHONHASHSEED=0 PYTHONUTF8=1 python3 tools/calculationViz/verify_complex.py complex.urdr.json
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "homology"))
import urdr_homology as H

def main(path):
    j = json.load(open(path, encoding="utf-8"))
    maximal = j.get("maximal")
    if not isinstance(maximal, list):
        print("VIZ-REFUSE: no `maximal` simplex list in", path); return 2
    cx = H.close_faces([tuple(int(v) for v in s) for s in maximal])
    betti = H.betti(cx)
    from collections import Counter
    dims = Counter(len(s) - 1 for s in cx)
    chi = sum(((-1) ** k) * n for k, n in dims.items())
    prev = (j.get("preview") or {}).get("betti")
    print("authority (urdr_homology.betti o close_faces):")
    print("  betti =", betti)
    print("  euler chi =", chi)
    print("  V/E/F =", dims.get(0,0), dims.get(1,0), dims.get(2,0))
    if prev is not None:
        print("  browser PREVIEW betti =", prev, "->", "AGREE" if list(prev)==betti else "DISAGREE")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: verify_complex.py <complex.urdr.json>"); sys.exit(2)
    sys.exit(main(sys.argv[1]))
