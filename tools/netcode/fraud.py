#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fraud — optimistic verification: settle a witness-chain dispute by re-executing ONE tick.

Reference for the core law of `docs/fraud_proof.md` (DECLARED). A LIGHT referee adjudicates a
dispute between two witness chains over a FIXED world + input log by re-executing exactly the
single tick where they first diverge — never the whole run. It reuses the frozen surface
entirely: `lockstep._digest` / `first_desync` / `canon` and `worldstep.step_tick` /
`simulate_trace`. The only NEW logic is the adjudicator and the no-fabrication (pre-state
digest) check.

SCOPE (honest — this is increment 1). The single-round referee reuses the flat `URDRLSTT`
commitment: both parties reveal full chains; the referee runs an O(T) comparison plus ONE tick.
The O(log T) Merkle-bisection data-efficiency layer (reveal only log T states, for the thin-
client / on-chain case) is increment 2. This settles COMPUTATION correctness given an agreed
input log; INPUT legitimacy (aimbots) is out of scope by law — `integrity != truth`.

WHY IT'S DECISIVE. `frames[k]` is the state after tick k-1, and `first_desync` gives the first
frame index where two chains differ, so both chains AGREE on the pre-state `frames[k-1]`. The
referee binds a provided pre-state to that agreed digest (a fabricated state would need a
SHA-256 collision), re-executes the one disputed tick from it, and whichever chain's `frames[k]`
matches the true re-execution is honest. This works only because the tick is bit-exact
reproducible — the same exactness the gate already proves.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PHYS = os.path.join(os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L    # noqa: E402  frozen N1 laws (_digest, first_desync, canon, trace_digest)
import worldstep as W   # noqa: E402  frozen N4 tick (step_tick, simulate_trace, arena_world)


class FraudError(Exception):
    """Typed refusal: FRAUD-REFUSE — a malformed dispute the referee will not adjudicate."""

    def __init__(self, code, message=""):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def disputed_tick(chain_a, chain_b):
    """The tick under dispute. `frames[k]` is the state AFTER tick k-1, so the first frame index
    k where the chains differ pins tick t = k-1. Returns None if the chains are identical."""
    k = L.first_desync(chain_a, chain_b)
    if k is None:
        return None
    return k - 1


def adjudicate(w, log, chain_a, chain_b, pre_state):
    """Referee verdict over a dispute. Inputs: the world `w`, the agreed input `log`, the two
    witness chains, and the `pre_state` (pos, vel) claimed to be the AGREED frame just before the
    disputed tick. Re-executes exactly ONE tick and returns:

        'IDENTICAL'  — the chains do not diverge (no dispute)
        'A' / 'B'    — that chain matches the true re-execution; the other lied about this tick
        'NEITHER'    — both chains diverge from the truth (both lied about this tick)

    Raises FRAUD-REFUSE on a malformed dispute: chains that disagree before the located tick, an
    initial-state dispute (adjudicate the setup, not a tick), or a fabricated pre-state that does
    not hash to the agreed frame."""
    n = w["n"]
    k = L.first_desync(chain_a, chain_b)
    if k is None:
        return "IDENTICAL"
    if k == 0:
        raise FraudError("FRAUD-REFUSE", "initial-state dispute — adjudicate the setup, not a tick")
    if chain_a[k - 1] != chain_b[k - 1]:
        raise FraudError("FRAUD-REFUSE", "chains disagree before the located tick (bad divergence)")
    agreed = chain_a[k - 1]
    pos, vel = pre_state
    if L._digest(pos, vel, n) != agreed:
        raise FraudError("FRAUD-REFUSE", "pre-state does not hash to the agreed frame (fabricated)")
    # --- the ONE tick the referee runs (never the whole run) ---
    p = [list(x) for x in pos]
    v = [list(x) for x in vel]
    events = L.canon(log).get(k - 1, [])
    W.step_tick(w, p, v, events)
    true_next = L._digest(p, v, n)
    a_ok = chain_a[k] == true_next
    b_ok = chain_b[k] == true_next
    if a_ok and not b_ok:
        return "A"
    if b_ok and not a_ok:
        return "B"
    return "NEITHER"


# ---- demo scenario + dispute builders (validity, not outcome) ------------------------
def demo_run():
    """An honest arena run: (world, log, frames, states) — the shared, agreed ground truth."""
    w = W.arena_world()
    log = W.sample_world_log()
    frames, states = W.simulate_trace(w, log)
    return w, log, frames, states


def doctor(frames, m, forged="0" * 64):
    """A doctored chain: honest frames with ONE post-state (frame m) replaced by a lie."""
    bad = list(frames)
    bad[m] = forged if bad[m] != forged else "f" * 64
    return bad


def demo_dispute(m=None):
    """(w, log, honest, doctored, pre, m): honest chain vs a chain doctored at frame m, with the
    AGREED pre-state states[m-1] the referee will bind + re-execute from."""
    w, log, frames, states = demo_run()
    if m is None:
        m = len(frames) // 2
    return w, log, frames, doctor(frames, m), states[m - 1], m


if __name__ == "__main__":
    w, log, honest, bad, pre, m = demo_dispute()
    print("doctored at frame m =", m, "-> disputed tick", disputed_tick(honest, bad))
    print("A honest / B doctored  ->", adjudicate(w, log, honest, bad, pre), "(expect A)")
    print("A doctored / B honest  ->", adjudicate(w, log, bad, honest, pre), "(expect B)")
    print("A honest / B honest    ->", adjudicate(w, log, honest, list(honest), pre), "(expect IDENTICAL)")
    both = doctor(bad, m, forged="1" * 64)
    print("both lie (differently) ->", adjudicate(w, log, bad, both, pre), "(expect NEITHER)")
    try:
        _, _, frames, states = demo_run()
        adjudicate(w, log, honest, bad, states[m])   # wrong pre-state (states[m], not m-1)
        print("fabricated pre-state   -> NOT REFUSED  <-- BUG")
    except FraudError as e:
        print("fabricated pre-state   ->", e.code, "(expect FRAUD-REFUSE)")
