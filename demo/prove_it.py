#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""demo/prove_it.py — a one-command proof that the engine's authority is reproducible.

The claim the whole project rests on: *every admitted output is either bit-identical
across independent runs / implementations, or explicitly refused.* This script makes
that claim executable in ~1 second. It runs three things and CHECKS them (it exits
nonzero if any check fails, so a green run means something):

  1. HEADLINE (MEASURED, gated rung 5). The bounded fixed-point steppers reproduce their
     frozen URDRFPT1 trace goldens bit-for-bit, deterministically. Those same goldens are
     reproduced by an independent std-only Rust placement (tools/physics/fp_dynamics_rs)
     on Windows/rustc, and by the CI gate on Linux+Windows — so the digests printed below
     are cross-host AND cross-language, not just "the same on my machine."

  2. AUTHOR -> EXPORT -> REPLAY (the game workflow). An authored world
     (demo/world_highway.json, the shape urdr_designer.html exports) is time-stepped by the
     bounded fixed-point runtime; its per-tick *witness chain* is identical across
     independent re-runs. The built-in exact "Newton's-cradle" cascade is likewise
     deterministic and conserves momentum + 2*KE exactly.

  3. EXACT CERTIFIED SOLVES (a witness or a refusal, never a guess). The resting-stack
     contact LCP returns lambda = [3, 2, 1] (each contact carries the weight above it) with a
     complementarity-certified URDRLCP1 witness — the SAME digest the CI gate pins as
     physics-lcp:rest3. The articulated chain solves J.v = 0 with a URDRJNT1 witness.

Why this is convincing: it is not a rendering of a game. It is the authoritative
simulation reproducing itself, on demand, with cryptographic witnesses you can diff.

Run:   python3 demo/prove_it.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "physics"))   # gated physics modules
sys.path.insert(0, os.path.join(REPO, "tools", "editor"))    # replay runtime (consumer)

_FAILS = []


def check(name, ok, detail=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + name + (("   " + detail) if detail else ""))
    if not ok:
        _FAILS.append(name)


def _goldens():
    g = {}
    with open(os.path.join(REPO, "tools", "physics", "conformance_fp.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                n, d = ln.split()
                g[n] = d
    return g


def headline():
    print("=" * 72)
    print("1. HEADLINE — the bounded fixed-point rung reproduces its frozen goldens")
    print("   MEASURED: gated in CI + cross-placed in Rust; digests are cross-host & cross-language")
    print("=" * 72)
    import fp_dynamics as D
    gold = _goldens()
    for name, fn in (("stack3", D.run_stack), ("swing", D.run_swing)):
        t1, _ = fn()
        t2, _ = fn()
        print("    %-7s URDRFPT1 %s" % (name, t1))
        check("%s: deterministic (same digest twice)" % name, t1 == t2)
        check("%s: == frozen golden" % name, t1 == gold.get(name),
              "(also reproduced by fp_dynamics_rs on Windows/rustc)")


def workflow():
    print()
    print("=" * 72)
    print("2. AUTHOR -> EXPORT -> REPLAY — the authored world replays identically")
    print("=" * 72)
    import replay as R
    world = os.path.join(REPO, "demo", "world_highway.json")
    d1 = R.fp_world_doc(world, grav=4)
    d2 = R.fp_world_doc(world, grav=4)
    c1, c2 = d1["chain"], d2["chain"]
    ncontacts = sum(len(f.get("contacts", [])) for f in d1["frames"])
    print("    highway   ticks=%d   contacts_resolved=%d   (2 vehicles + 1 static barrier)"
          % (len(c1), ncontacts))
    print("    highway   chain head %s" % (c1[0] if c1 else "-"))
    print("    highway   chain tail %s" % (c1[-1] if c1 else "-"))
    check("highway: bounded run, no overflow (engine did not refuse)", d1["refused"] is None,
          "%d ticks on the Q32.32 substrate" % len(c1))
    check("highway: witness chain reproduces bit-for-bit across independent re-runs", c1 == c2)

    cd1 = R.cascade_doc()
    cd2 = R.cascade_doc()
    f0, fN = cd1["frames"][0], cd1["frames"][-1]
    print("    cascade   ticks=%d   (built-in exact Newton's-cradle momentum transfer)"
          % len(cd1["frames"]))
    check("cascade: deterministic", cd1["chain"] == cd2["chain"])
    check("cascade: total momentum conserved exactly", (f0["px"], f0["py"]) == (fN["px"], fN["py"]))
    check("cascade: total 2*KE conserved exactly", f0["e2"] == fN["e2"])


def exact_solves():
    print()
    print("=" * 72)
    print("3. EXACT CERTIFIED SOLVES — a witness or a refusal, never a guess")
    print("=" * 72)
    import replay as R
    sd = R.stack_doc(3)
    lam = [c["lam"] for c in sd["frames"][0]["contacts"]]
    print("    stack     lambda (bottom->top) = %s   URDRLCP1 %s" % (lam, sd["lcp_digest"]))
    check("stack: LCP complementarity certified", sd["certified"])
    check("stack: lambda = [3, 2, 1] (each contact carries the weight above it)",
          lam == [3.0, 2.0, 1.0])
    check("stack: URDRLCP1 matches the gated physics-lcp:rest3 digest",
          sd["lcp_digest"].startswith("89666457617a17e0"))
    jd = R.joints_doc(N=4)
    print("    joints    URDRJNT1 %s   (4-ball rod chain)" % jd["joint_digest"])
    check("joints: J.v = 0 certified (rigid links held)", jd["certified"])


def main():
    print()
    headline()
    workflow()
    exact_solves()
    print()
    print("=" * 72)
    if _FAILS:
        print("RESULT: %d CHECK(S) FAILED -> %s" % (len(_FAILS), ", ".join(_FAILS)))
        return 1
    print("RESULT: ALL CHECKS PASSED")
    print("A green run proves THESE runs reproduce on THIS host. The fixed-point goldens")
    print("additionally match an independent Rust placement and the CI gate (Linux+Windows).")
    print("Scope: the editor/replay layer is exploratory; the gated authority is rung 5 +")
    print("the exact solvers. admitted != trusted — the witnesses are what you diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
