#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Track 1 -- multi-actor certified structural timeline (urdr-physics x world_host).

Many actors submit structural mutation PROPOSALS against a shared world; the deterministic scheduler
canonicalizes them (weave rule: sort by intent digest), applies each through the urdr-physics
admissibility check, and COMMITS a non-forking transition history or emits a deterministic structural
CONFLICT (↯). Composes the measured parts: scheduler canonical order (world_host Step 3), physics
admissibility (urdr-physics), the transition chain + provenance binding (Milestone 6.5), the kernel
digest (urdr-core). No new foundations. Run -> BATTERY: ALL GREEN.

    Proposal { actor, parent: Digest, mutation: [op, args...] }
    intent digest = ᛝ(canon([actor, parent, mutation]))   -- canonical order + the actor's intent
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "intla"))
sys.path.insert(0, ROOT)
from urdr import canon as C, values as V
import physics                                     # urdr-physics (admit_transition, digest_fw)

ADD, REMOVE = 0, 1


def proposal(actor, parent_digest, mutation):
    return {"actor": actor, "parent": parent_digest, "mutation": mutation}


def intent_digest(p):
    val = V.ListV([V.Int(p["actor"]), V.DigestV(p["parent"]),
                   V.ListV([V.Int(x) for x in p["mutation"]])])
    return C.digest(val)


def apply_mutation(world, mut):
    edges, coords = world
    es = [tuple(sorted(e)) for e in edges]
    e = tuple(sorted((mut[1], mut[2])))
    if mut[0] == ADD:
        return world if e in es else (edges + [e], coords)
    if mut[0] == REMOVE:
        return ([x for x in edges if tuple(sorted(x)) != e], coords)
    return world


def commit_tick(n, d, world, proposals, order="canonical"):
    """Sequence a batch of proposals into one non-forking transition. Returns
    (new_world, committed[(actor, digest)], conflicts[(actor, reason)])."""
    d0 = physics.digest_fw(*world)
    fresh = [p for p in proposals if p["parent"] == d0]
    conflicts = [(p["actor"], "stale parent (provenance)") for p in proposals if p["parent"] != d0]
    seq = sorted(fresh, key=intent_digest) if order == "canonical" else list(fresh)  # arrival = broken
    cur = world
    committed = []
    for p in seq:
        cand = apply_mutation(cur, p["mutation"])
        v, why = physics.admit_transition(n, d, cur, cand)
        if v == "ADMIT":
            committed.append((p["actor"], physics.digest_fw(*cand).hex()[:8]))
            cur = cand
        else:
            conflicts.append((p["actor"], why))     # deterministic structural conflict ↯
    return cur, committed, conflicts


if __name__ == "__main__":
    d, n = 2, 4
    coords = [(0, 0), (2, 0), (2, 2), (0, 2)]
    square = ([(0, 1), (1, 2), (2, 3), (3, 0)], coords)              # flexible base
    braced = ([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)], coords)     # rigid
    d_sq = physics.digest_fw(*square)
    d_br = physics.digest_fw(*braced)
    bad = 0

    # GREEN: two actors add independent braces -> both commit -> arrival-order invariant
    pA = proposal(2, d_sq, [ADD, 0, 2])
    pB = proposal(7, d_sq, [ADD, 1, 3])
    w1, c1, x1 = commit_tick(n, d, square, [pA, pB])
    w2, c2, x2 = commit_tick(n, d, square, [pB, pA])                 # different arrival order
    inv = (physics.digest_fw(*w1) == physics.digest_fw(*w2)) and (c1 == c2) and (len(c1) == 2) and not x1
    print(f"  green: both braces commit, arrival-order invariant = {inv}; committed={c1}")
    bad += 0 if inv else 1

    # CONFLICT (no-op): two actors propose the SAME brace -> one commits, one URDR-DELTA-UNEARNED
    pC = proposal(3, d_sq, [ADD, 0, 2])
    pD = proposal(9, d_sq, [ADD, 0, 2])
    _, c3, x3 = commit_tick(n, d, square, [pC, pD])
    noop = (len(c3) == 1) and (len(x3) == 1) and ("DELTA-UNEARNED" in x3[0][1])
    print(f"  conflict(no-op): committed={c3} conflicts={x3} -> {noop}")
    bad += 0 if noop else 1

    # CONFLICT (structural collapse): remove a brace -> flexible -> inadmissible ↯
    pE = proposal(4, d_br, [REMOVE, 0, 2])
    _, c4, x4 = commit_tick(n, d, braced, [pE])
    collapse = (len(c4) == 0) and (len(x4) == 1) and ("not rigid" in x4[0][1])
    print(f"  conflict(collapse): committed={c4} conflicts={x4} -> {collapse}")
    bad += 0 if collapse else 1

    # STALE: proposal against the wrong parent -> refused
    pF = proposal(8, d_br, [ADD, 1, 3])                              # parent = braced, world = square
    _, c5, x5 = commit_tick(n, d, square, [pF])
    stale = (len(c5) == 0) and (len(x5) == 1) and ("stale" in x5[0][1])
    print(f"  stale: committed={c5} conflicts={x5} -> {stale}")
    bad += 0 if stale else 1

    # NON-VACUITY: an arrival-order scheduler is NOT order-invariant (committed sequence differs)
    ca = commit_tick(n, d, square, [pA, pB], order="arrival")[1]
    cb = commit_tick(n, d, square, [pB, pA], order="arrival")[1]
    nonvac = (c1 == c2) and (ca != cb)
    print(f"  non-vacuity: canonical invariant & arrival-order sequence differs = {nonvac}")
    bad += 0 if nonvac else 1

    print("BATTERY:", "ALL GREEN" if bad == 0 else f"{bad} RED")
    sys.exit(0 if bad == 0 else 1)
