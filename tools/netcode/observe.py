# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode observability — field-level desync localization (Phase-2, gated core).

`lockstep.first_desync` localizes a divergence to the first mismatching TICK by comparing
two witness (digest) chains. This goes one level finer: given the two per-tick STATE chains
(the `(pos, vel)` snapshots that `simulate_trace` / `region_simulate_trace` already carry
for display), it localizes the divergence to the exact **body and field** — the first byte
group, in `URDRLST1` serialization order, at which the two runs disagree.

The scan order is EXACTLY the witness serialization order (`lockstep._digest`): for each body
`i` in global index order, `pos.x, pos.y, vel.x, vel.y` as signed Q32.32 words. So the field
this returns is, byte-for-byte, the cause of the first digest divergence `first_desync` sees —
the two diagnostics agree by construction, and this one names the field.

The honest diagnostic (why this is stronger than a gamedev "desync hint"): the authority tick
is **exact integer arithmetic and deterministic**. There is no floating-point accumulation in
the witnessed state, so two chains cannot "drift apart." A field-level divergence is therefore
a PROOF that exactly one of two things happened upstream of that tick:

  (1) the admitted INPUTS differed (a dropped / added / altered event), or
  (2) one run used a NON-CONFORMING implementation (a different tick law — a defect placement).

It is never rounding. The inspector should say so: this points at an input or a placement, not
a line of numerical code.

Compare the EXACT Q32.32 words, never float display coordinates — the words are what the
witness hashes; display coords are fitted for a canvas and would show phantom or hidden diffs.
"""

# fields per body, in URDRLST1 serialization order (lockstep._digest)
FIELDS = (("pos", 0), ("pos", 1), ("vel", 0), ("vel", 1))
_LABEL = {("pos", 0): "pos.x", ("pos", 1): "pos.y", ("vel", 0): "vel.x", ("vel", 1): "vel.y"}


def first_field_desync(states_a, states_b):
    """The first field at which two per-tick state chains disagree, scanned in witness
    serialization order (tick, then body, then pos.x/pos.y/vel.x/vel.y).

    Each state is a `(pos, vel)` pair as produced by `simulate_trace` — `pos`/`vel` are lists
    of `[x, y]` Q32.32 words, one per body. Returns a tuple
    `(tick, body, kind, axis, word_a, word_b)` with `kind in {"pos","vel"}` and `axis in {0,1}`,
    or a typed marker for a structural mismatch, or `None` if the chains are identical up to the
    shorter length:
      * `(tick, body, "count", 0, n_a, n_b)` — the two runs have a different body count at `tick`
        (a body appeared/vanished — an authority-level divergence, not a field value);
      * `(tick, -1, "length", 0, len_a, len_b)` — the chains ran for different tick counts.
    Pure and total; reads only the two chains, writes nothing (observational-only)."""
    m = min(len(states_a), len(states_b))
    for t in range(m):
        pa, va = states_a[t]
        pb, vb = states_b[t]
        nb = min(len(pa), len(pb))
        for i in range(nb):
            for (kind, ax) in FIELDS:
                wa = (pa if kind == "pos" else va)[i][ax]
                wb = (pb if kind == "pos" else vb)[i][ax]
                if wa != wb:
                    return (t, i, kind, ax, wa, wb)
        if len(pa) != len(pb):
            return (t, nb, "count", 0, len(pa), len(pb))
    if len(states_a) != len(states_b):
        return (m, -1, "length", 0, len(states_a), len(states_b))
    return None


def describe(fd):
    """A one-line, honest human summary of a `first_field_desync` result (for a CLI / the
    inspector). Names the field and states the categorical cause — never 'rounding'."""
    if fd is None:
        return "no field desync: the two state chains are identical"
    t, i, kind, ax, a, b = fd
    if kind == "length":
        return f"chains have different lengths at tick {t}: {a} vs {b}"
    if kind == "count":
        return f"tick {t}: body count differs ({a} vs {b}) — a body appeared/vanished"
    return (f"tick {t}, body {i}, {_LABEL[(kind, ax)]}: {a} != {b} "
            f"(Q32.32 words) — deterministic exact tick, so the cause is upstream: "
            f"a differing admitted input at/before tick {t}, or a non-conforming placement")
