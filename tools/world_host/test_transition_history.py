#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Integration test for the transition-history reference (Milestone 7, Step 2).
GREEN (replay reproduces the chain head; two observers agree) + RED (reorder / missing / fork
refused) + non-vacuity (a broken accept-any-history host fails the harness). Exits 0/1."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.world_host.transition_history import (
    build_history, validate, authoritative, content_digest, URDRAssert)
from tools.world_host.world_host import Atlas, Chart, digest as cdigest

fails = []
def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond: fails.append(name)
def raises(fn):
    try: fn(); return False
    except URDRAssert: return True

S0 = [3, 1, 4, 1, 5]
OPS = [[0, 1], [1, 2]]                                   # S0 -> S1 -> S2
D0 = content_digest(S0)
hist, head, sfinal = build_history(S0, OPS)

# --- GREEN: replay reproduces the authoritative chain head ---
check("replay-validate reaches the authoritative head", validate(D0, hist) == head)
hist2, head2, sfinal2 = build_history(S0, OPS)          # a second observer, same transitions
check("second observer replaying the same list reaches the SAME head", head2 == head)
# views may differ, but both observers' reconstructed final state binds to one content digest:
atlasA = Atlas([Chart([0, 1]), Chart([2, 3]), Chart([4])])
atlasB = Atlas([Chart([4, 3]), Chart([2, 1]), Chart([0])])
imgA, imgB = atlasA.image(sfinal), atlasB.image(sfinal2)
check("views differ but final-state authority agrees",
      imgA != imgB and cdigest(atlasA.recon(imgA, 5)) == cdigest(atlasB.recon(imgB, 5)))

# --- RED: reordered history (parent no longer links) ---
check("reordered history REFUSED", raises(lambda: validate(D0, [hist[1], hist[0]])))
# --- RED: missing transition (broken parent) ---
check("missing transition REFUSED", raises(lambda: validate(D0, [hist[1]])))
# --- RED: fork (two candidate heads, no merge rule) ---
head_a = build_history(S0, [[0, 1]])[1]
head_b = build_history(S0, [[1, 1]])[1]
check("fork is a real digest divergence", head_a != head_b)
check("fork REFUSED as authority (no merge rule)", raises(lambda: authoritative([head_a, head_b])))
check("non-fork resolves to one authority", authoritative([head_a, head_a]) == head_a)

# --- NON-VACUITY: a broken accept-any-history host must FAIL this harness ---
def accept_any_history(genesis, history):               # broken: never checks the chain
    return history[-1].result if history else genesis
real_refuses = raises(lambda: validate(D0, [hist[1], hist[0]]))
broken_admits = (accept_any_history(D0, [hist[1], hist[0]]) is not None)  # does not raise
check("non-vacuity: the reorder test distinguishes a correct validator from a broken one",
      real_refuses and broken_admits)

print("TRANSITION-HISTORY:", "ALL GREEN" if not fails else f"{len(fails)} RED: {fails}")
sys.exit(0 if not fails else 1)
