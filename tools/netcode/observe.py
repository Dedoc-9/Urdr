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

THAT SENTENCE WAS A WARNING WITH NOTHING BEHIND IT, and the failure it names was reachable.
`first_field_desync` admitted anything and compared with `!=`, so a float display coordinate
whose value happens to equal the word — `5.0` against `5` — compared EQUAL and the localizer
returned `None`: **the hidden diff, produced by the exact input the docstring told the reader
to avoid.** The two chains hash differently and this module said they were identical. Two more
shapes were admitted untyped: a chain whose `pos` and `vel` carry different body counts raised
a bare `IndexError`, and a non-chain argument raised a bare `ValueError` from tuple unpacking.
`claim != code` — the prose was correct and load-bearing and enforced nowhere.

`OBSERVE-REFUSE` now enforces it, and the admission runs over the WHOLE input before any
comparison. Validating lazily inside the scan would make the boundary depend on the ANSWER: a
malformed body sitting past the first divergence would be ADMITTED (the scan returns before
reaching it) and REFUSED when the chains agree. An admission decision that depends on where
the difference is, is not an admission decision — so both chains are admitted in full, then
scanned, and `refusal_is_independent_of_divergence` pins that.

What is NOT refused, deliberately: `length` and `count`. Different chain lengths and different
per-tick body counts are the module's documented VERDICTS — the diagnostics it exists to
report — not malformed input. Converting them to exceptions would delete the answer.
"""

# fields per body, in URDRLST1 serialization order (lockstep._digest)
FIELDS = (("pos", 0), ("pos", 1), ("vel", 0), ("vel", 1))
_LABEL = {("pos", 0): "pos.x", ("pos", 1): "pos.y", ("vel", 0): "vel.x", ("vel", 1): "vel.y"}


class ObserveError(Exception):
    """A typed refusal from the localizer. `code` mirrors the tree's URDR-* discipline: a
    refusal is a STOP that carries a code, never a silently-absorbed comparison."""

    def __init__(self, code, message):
        super().__init__("%s: %s" % (code, message))
        self.code = code
        self.message = message


def _seq(v):
    return isinstance(v, (list, tuple)) and not isinstance(v, (str, bytes))


def admit(name, chain):
    """THE ADMISSION BOUNDARY, stated as the exact inputs this module must reject.

    A chain is a sequence of per-tick `(pos, vel)` states; `pos` and `vel` are equal-length
    sequences of `[x, y]` pairs; every word is an exact Q32.32 `int`. `bool` is excluded on
    purpose — `True == 1` is the same silent-equality trap the float word is.

    Total over the input and independent of the other chain, so refusal is a function of what
    was handed in and of nothing else. Returns the chain so callers can bind it."""
    if not _seq(chain):
        raise ObserveError("OBSERVE-REFUSE",
                           "%s must be a sequence of per-tick states, got %s"
                           % (name, type(chain).__name__))
    for t, st in enumerate(chain):
        if not _seq(st) or len(st) != 2:
            raise ObserveError("OBSERVE-REFUSE",
                               "%s[%d] must be a (pos, vel) pair, got %r" % (name, t, st))
        pos, vel = st
        for kind, side in (("pos", pos), ("vel", vel)):
            if not _seq(side):
                raise ObserveError("OBSERVE-REFUSE",
                                   "%s[%d].%s must be a sequence of bodies, got %s"
                                   % (name, t, kind, type(side).__name__))
            for i, body in enumerate(side):
                if not _seq(body) or len(body) != 2:
                    raise ObserveError("OBSERVE-REFUSE",
                                       "%s[%d].%s[%d] must be an [x, y] word pair, got %r"
                                       % (name, t, kind, i, body))
                for ax, word in enumerate(body):
                    if not isinstance(word, int) or isinstance(word, bool):
                        raise ObserveError(
                            "OBSERVE-REFUSE",
                            "%s[%d].%s[%d][%d] must be an exact Q32.32 integer word, got %r — "
                            "a float display coordinate compares EQUAL to the word it was "
                            "fitted from and would hide the divergence"
                            % (name, t, kind, i, ax, word))
        if len(pos) != len(vel):
            raise ObserveError("OBSERVE-REFUSE",
                               "%s[%d] carries %d pos bodies and %d vel bodies — a body count "
                               "differing WITHIN one chain is malformed input, not the `count` "
                               "verdict (which reports a difference BETWEEN the two chains)"
                               % (name, t, len(pos), len(vel)))
    return chain


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

    Input that is not a pair of state chains is a typed `OBSERVE-REFUSE` (see `admit`), taken
    over BOTH chains in full before the first comparison. `length` and `count` stay results.
    Reads only the two chains, writes nothing (observational-only)."""
    admit("states_a", states_a)
    admit("states_b", states_b)
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


def refusal_is_independent_of_divergence(good, bad):
    """RED-FIRST, and it pins the one thing lazy validation would break: a malformed chain is
    refused whether or not the two chains diverge BEFORE the malformed part is reached.

    `bad` must be a chain that `admit` rejects. It is scanned against itself (no divergence
    anywhere) and against `good` (divergence at tick 0 if they differ there) — both must
    refuse with the same code. If validation ran inside the scan, the second call would return
    a result and this would be False."""
    codes = []
    for other in (bad, good):
        try:
            first_field_desync(bad, other)
        except ObserveError as exc:
            codes.append(exc.code)
        else:
            return False
    return len(codes) == 2 and codes[0] == codes[1] == "OBSERVE-REFUSE"


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
