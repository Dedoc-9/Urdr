#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""demo/lockstep_demo.py — deterministic lockstep in one command (inputs only, no state).

The architecture's unusual advantage, made executable and self-checking (nonzero exit on any
failure). It stages a two-peer session and proves the three things a lockstep netcode lives or
dies on:

  1. AGREEMENT. Peer A and Peer B start from the same canonical world and exchange ONLY their
     timestamped inputs — never state. Each assembles the input UNION in a different arrival
     order, steps the deterministic authority, and independently emits a witness chain. Identical
     inputs -> identical per-tick witnesses and identical final digest.

  2. DELIVERY ROBUSTNESS. The same logical inputs delivered REORDERED or DUPLICATED produce the
     same chain (exact-duplicate dedup + additive-impulse commutativity) — the network being
     lossy/re-ordering is not a desync.

  3. FAULT DETECTION. A DROPPED, MODIFIED, or TICK-MOVED input changes the logical log, so the
     chains diverge — and the desync is DETECTED and EXPLAINED by the FIRST mismatching witness
     (which tick, and the two differing digests), never silently. A genuinely different-but-valid
     input is not mistaken for a fault.

Run:   python3 demo/lockstep_demo.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "physics"))   # frozen fixed-point substrate
sys.path.insert(0, os.path.join(REPO, "tools", "netcode"))   # lockstep authority

import lockstep as L                                         # noqa: E402

_FAILS = []


def check(name, ok, detail=""):
    print(("  [PASS] " if ok else "  [FAIL] ") + name + (("   " + detail) if detail else ""))
    if not ok:
        _FAILS.append(name)


def short(chain):
    return chain[-1][:16] + "…"


def main():
    w = L.world()
    log = L.sample_log()
    a_inputs = [e for e in log if e[1] == 0]        # peer 0's own inputs
    b_inputs = [e for e in log if e[1] == 1]        # peer 1's own inputs

    print()
    print("=" * 72)
    print("1. AGREEMENT — two peers exchange inputs only, never state")
    print("=" * 72)
    # each peer holds its own inputs first, then the ones it received — different orders
    peerA = a_inputs + b_inputs
    peerB = b_inputs + a_inputs
    chainA, finA = L.simulate(w, peerA)
    chainB, finB = L.simulate(w, peerB)
    print("    peer A assembled %d inputs; peer B assembled the same %d in a different order"
          % (len(peerA), len(peerB)))
    print("    peer A final digest %s" % finA)
    print("    peer B final digest %s" % finB)
    check("both peers produce the identical %d-tick witness chain" % len(chainA), chainA == chainB)
    check("both peers agree on the final state digest", finA == finB)
    check("no desync between honest peers", L.first_desync(chainA, chainB) is None)

    print()
    print("=" * 72)
    print("2. DELIVERY ROBUSTNESS — reordered / duplicated delivery is absorbed")
    print("=" * 72)
    reordered = L.simulate(w, L.reorder_delivery(peerA))[0]
    duplicated = L.simulate(w, L.duplicate_delivery(peerA))[0]
    check("reordered delivery of the same inputs -> same chain", reordered == chainA)
    check("duplicated delivery of the same inputs -> same chain (deduped)", duplicated == chainA)
    # and a genuinely different input is NOT absorbed (dedup is real, not "nothing matters")
    e = peerA[1]
    distinct = list(peerA) + [(e[0], e[1], 999, e[3], e[4], e[5])]
    check("a genuinely new input DOES change the chain (dedup is load-bearing)",
          L.simulate(w, distinct)[0] != chainA)

    print()
    print("=" * 72)
    print("3. FAULT DETECTION — a corrupted input desyncs, and the first witness explains it")
    print("=" * 72)
    faults = (
        ("dropped  input #1", L.drop_event(peerA, 1)),
        ("modified input #1", L.modify_event(peerA, 1)),
        ("mis-timed input #1", L.move_event_tick(peerA, 1, peerA[1][0] - 1)),
    )
    for label, corrupted in faults:
        fc = L.simulate(w, corrupted)[0]
        t = L.first_desync(chainA, fc)
        desynced = fc != chainA and t is not None
        check("%s -> desync detected" % label, desynced,
              "first divergent witness at tick %s" % t)
        if desynced:
            print("           tick %-3d  honest  %s" % (t, chainA[t][:24] + "…"))
            print("           tick %-3d  faulted %s   <- explained, not silent" % (t, fc[t][:24] + "…"))

    print()
    print("=" * 72)
    if _FAILS:
        print("RESULT: %d CHECK(S) FAILED -> %s" % (len(_FAILS), ", ".join(_FAILS)))
        return 1
    print("RESULT: ALL CHECKS PASSED")
    print("Peers exchanged inputs, not state; identical inputs produced identical cryptographic")
    print("witnesses; every injected fault was caught and localized to the first mismatching tick.")
    print("Scope: MEASURED reproducibility on the cross-placed fixed-point substrate; a second-")
    print("language placement of this loop and authenticated inputs (digest != MAC) are declared next.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
