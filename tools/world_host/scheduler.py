#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""scheduler -- deterministic multi-actor scheduling (Milestone 7, Step 3).

Steps 1-2 fixed authority for one world and one linear history. Step 3 lets MANY actors
propose transitions concurrently, and turns those proposals into ONE authoritative history --
deterministically, without networking, actors-as-threads, or persistence.

The canonical order is a pure function of the proposal MULTISET, not of arrival/submission
order: sort by the proposal's content digest (the kernel's `weave` rule -- canonical order =
sort by digest, D5). So every host that sees the same proposals commits the same history,
and a client that applied its own optimistic (non-canonical) order cannot promote that branch.

This CONSUMES the measured convergence property (kernel `weave` / `parallel_runtime`: commuting
transitions converge, order is a chart; non-commuting order is identity). It does not re-prove
it -- it is the host loop around it. Chain digests come from Step 2 (`transition_history`).
`the runtime consumes the theorem; it does not re-prove it`.
"""
from urdr import values as V, canon as C
from tools.world_host.transition_history import (
    chain_step, apply_op, Transition, URDRAssert)


def proposal_digest(actor, op):
    """Content digest of a proposal (actor + operation) -- the canonical sort key."""
    return C.digest(V.ListV([V.Int(int(actor)), V.ListV([V.Int(int(op[0])), V.Int(int(op[1]))])]))


def canonicalize(proposals):
    """Deterministic canonical order: sort by proposal content digest. A pure function of the
    proposal multiset -- independent of the order the proposals arrived in."""
    return sorted(proposals, key=lambda p: proposal_digest(p[0], p[1]))


def commit_tick(head_digest, head_state, proposals):
    """Canonicalize a batch of actor proposals and extend the chain by that ONE ordering.
    Returns (segment, new_head_digest, new_state). The segment is a valid Step-2 history."""
    ordered = canonicalize(proposals)
    d, st, seg = head_digest, list(head_state), []
    for i, (_actor, op) in enumerate(ordered):
        r = chain_step(d, op)
        seg.append(Transition(d, op, r, i))
        d, st = r, apply_op(st, op)
    return seg, d, st


def commit_arrival_order(head_digest, head_state, proposals):
    """A DELIBERATELY BROKEN scheduler: commits in arrival order (no canonicalization). Used
    only to prove the order-invariance test is non-vacuous."""
    d, st, seg = head_digest, list(head_state), []
    for i, (_actor, op) in enumerate(proposals):
        r = chain_step(d, op)
        seg.append(Transition(d, op, r, i))
        d, st = r, apply_op(st, op)
    return seg, d, st


def promote(candidate_head, canonical_head):
    """Only the canonical committed head is authoritative. A speculative or non-canonically
    ordered branch head cannot be promoted -- `fork/branch != authority`."""
    if candidate_head != canonical_head:
        raise URDRAssert("illegal branch promotion: non-canonical / speculative head")
    return candidate_head
