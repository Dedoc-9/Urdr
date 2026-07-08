#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""transition_history -- the world-runtime transition chain (Milestone 7, Step 2).

Step 1 fixed the STATIC invariant (many views -> one authoritative digest). Step 2 adds the
runtime dimension: many views of one EVOLVING history -> one authoritative digest CHAIN.

The chain digest is path-dependent:   D_{n+1} = H(D_n, op_n)
computed with the kernel's canon -> SHA-256 (a DigestV carrying the parent, plus the operation
as a value). It is STRONGER than the content digest: a reordering that lands on the same final
state value still breaks the chain, because each step is bound to its parent. Genesis
D_0 = content_digest(S_0). No networking, no actors, no persistence, no renderer -- those are
Steps 3-5. `the runtime consumes the theorem; it does not re-prove it`.
"""
from urdr import values as V, canon as C


class URDRAssert(Exception):
    """A transition-integrity breach: refused, never repaired (the runtime's URDR-ASSERT)."""


def _state(vec):
    return V.ListV([V.Int(int(n)) for n in vec])


def content_digest(vec):
    return C.digest(_state(vec))                      # genesis anchor = kernel content digest


def _op_value(op):
    return V.ListV([V.Int(int(op[0])), V.Int(int(op[1]))])


def chain_step(parent_digest, op):
    """D_{n+1} = H(D_n, op) -- parent bound in via DigestV, op as a value, kernel digest."""
    return C.digest(V.ListV([V.DigestV(parent_digest), _op_value(op)]))


def apply_op(vec, op):
    """op = [axis, delta] : deterministic integer state transition."""
    out = list(vec)
    out[op[0]] = out[op[0]] + op[1]
    return out


class Transition:
    def __init__(self, parent_digest, operation, resulting_digest, seq):
        self.parent = parent_digest
        self.op = operation
        self.result = resulting_digest
        self.seq = seq


def build_history(s0, ops):
    """Honest builder: a well-formed chain from s0 and an op list.
    Returns (history, authoritative_head_digest, final_state)."""
    d = content_digest(s0)
    st = list(s0)
    hist = []
    for i, op in enumerate(ops):
        r = chain_step(d, op)
        hist.append(Transition(d, op, r, i))
        d = r
        st = apply_op(st, op)
    return hist, d, st


def validate(genesis_digest, history):
    """Replay-validate a submitted history. Raises URDRAssert on ANY breach -- out-of-order
    sequence, broken/reordered parent, or forged resulting digest. Returns the chain head."""
    cur = genesis_digest
    for i, t in enumerate(history):
        if t.seq != i:
            raise URDRAssert(f"out-of-order transition at index {i} (seq {t.seq})")
        if t.parent != cur:
            raise URDRAssert(f"broken parent at seq {t.seq}: chain does not link")
        if t.result != chain_step(cur, t.op):
            raise URDRAssert(f"forged resulting digest at seq {t.seq}")
        cur = t.result
    return cur


def authoritative(heads):
    """One authoritative head. Multiple DISTINCT candidate heads = a fork with no defined merge
    rule -> refused. `fork != authority`."""
    if len(set(heads)) != 1:
        raise URDRAssert("fork: multiple candidate heads, no merge rule defined")
    return heads[0]
