#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Integration test for the deterministic scheduler (Milestone 7, Step 3).
GREEN (canonical ordering is arrival-order invariant; deterministic) + RED (non-canonical /
speculative branch promotion refused) + non-vacuity (an arrival-order scheduler is order-
DEPENDENT and fails invariance). Exits 0/1."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.world_host.scheduler import (
    commit_tick, commit_arrival_order, canonicalize, promote)
from tools.world_host.transition_history import content_digest, validate, URDRAssert

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond: fails.append(name)
def raises(fn):
    try: fn(); return False
    except URDRAssert: return True

S0 = [3, 1, 4, 1, 5]
D0 = content_digest(S0)
# three actors propose concurrently (distinct ops so order matters for the chain)
P = [(2, [0, 1]), (7, [1, 2]), (5, [4, 3])]
Pshuf = [P[2], P[0], P[1]]                               # a different ARRIVAL order, same multiset

# --- GREEN: canonical order is a pure function of the multiset (arrival-order invariant) ---
seg_a, head_a, st_a = commit_tick(D0, S0, P)
seg_b, head_b, st_b = commit_tick(D0, S0, Pshuf)
check("canonical head is invariant under arrival order", head_a == head_b)
check("canonical final state is invariant under arrival order", st_a == st_b)
check("committed segment is a valid Step-2 history", validate(D0, seg_a) == head_a)
# --- GREEN: determinism ---
check("deterministic: same proposals -> same head twice", commit_tick(D0, S0, P)[1] == head_a)

# --- RED: illegal branch promotion (a non-canonical / speculative ordering) ---
canon_order = canonicalize(P)
noncanon = list(reversed(canon_order))
check("a non-canonical order actually exists (>=2 distinct proposals)", noncanon != canon_order)
_, spec_head, _ = commit_arrival_order(D0, S0, noncanon)  # a speculative branch in another order
check("speculative branch has a DIFFERENT head", spec_head != head_a)
check("promoting the speculative branch is REFUSED", raises(lambda: promote(spec_head, head_a)))
check("promoting the canonical head is allowed", promote(head_a, head_a) == head_a)

# --- NON-VACUITY: an arrival-order scheduler is order-DEPENDENT (fails invariance) ---
broken_a = commit_arrival_order(D0, S0, P)[1]
broken_b = commit_arrival_order(D0, S0, Pshuf)[1]
check("non-vacuity: a broken arrival-order scheduler is NOT arrival-invariant",
      (head_a == head_b) and (broken_a != broken_b))

print("SCHEDULER:", "ALL GREEN" if not fails else f"{len(fails)} RED: {fails}")
sys.exit(0 if not fails else 1)
