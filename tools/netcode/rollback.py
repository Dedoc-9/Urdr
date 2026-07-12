# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode N2 — ROLLBACK: late inputs as a deterministic replay primitive.

N1 (lockstep.py, FROZEN at 0.1) proved: peers exchanging inputs only reproduce one
witness chain, and corruption desyncs detectably. Its honest limitation: an input that
arrives AFTER its tick was simulated could only desync. N2 removes that limitation
without touching the frozen module:

  A peer keeps CANONICAL SNAPSHOTS of its Q32.32 state every K ticks (retaining the
  last H). A LATE-BUT-VALID input rewinds to the newest snapshot at-or-before the
  input's tick, re-simulates to the present with the enlarged input set, and the
  corrected witness chain CONVERGES — bit-identical to the canonical timeline
  (`lockstep.simulate` over the full log). Everything else is typed:

    ROLLBACK-REFUSE    the input is older than the oldest retained snapshot (beyond
                       the rollback horizon) — refused whole; the chain is untouched.
    ROLLBACK-CONFLICT  a second event with the same (peer, seq) identity but a
                       different payload (a forgery, or a tick-moved replay) —
                       refused, naming the identity. An EXACT duplicate is absorbed.

  An input that simply never arrives still desyncs against the canonical chain,
  localized by `lockstep.first_desync` — same law as N1.

Design rulings (freeze-respecting, drift-guarded):
  * `lockstep.py` is consumed, never edited: this module reuses its `_digest`
    (URDRLST1), `trace_digest` (URDRLSTT), `event`, and `first_desync`. The per-tick
    physics is REIMPLEMENTED here, and the gate pins every converged chain EQUAL to
    `lockstep.simulate`'s — so any drift between the two ticks reddens the gate on
    every vector. The convergence invariant IS the anti-drift detector.
  * K (snapshot cadence) and H (snapshots retained) are OPERATIONAL parameters, not
    semantics: the admitted chain is identical for every K, H — only the refusal
    horizon moves. The gate checks K-invariance explicitly.
  * The snapshot contract: a restored snapshot must reproduce the URDRLST1 witness
    pinned at its tick (restore is exact, or the gate reddens).
  * Determinism: no float, no clock, no RNG; the frozen Q32.32 substrate rounds
    identically everywhere and REFUSES (FIELD-REFUSE) on overflow.

GRADE (honest, D5): MEASURED (both placements) — the `netcode_rollback` gate stage pins
convergence, K-invariance, snapshot exactness, both refusals, desync localization, and
the apply-at-head defect; the std-only Rust placement (rollback_rs/, ADMITTED on
Windows/rustc) reproduces the converged golden at K=4 and K=8 with both refusals typed,
and its --defect diverges to the SAME digest as the independent C99 cross-check.
Contracts FROZEN at urdr-netcode-rollback 0.1 (spec/D12, in the mechanically-checked
freeze manifest). `digest != MAC` still: identity conflicts are detected; signatures
are not claimed — authenticated inputs are the declared successor."""
import sys as _sys
import os as _os

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "physics"))

from field import FixedPoint as FP                         # noqa: E402  frozen Q32.32
import lockstep as L                                       # noqa: E402  frozen N1


class RollbackError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _copy_state(pos, vel):
    return [[c for c in p] for p in pos], [[c for c in v] for v in vel]


class Peer:
    """A rollback-capable lockstep peer. `deliver` events in ANY order; `advance`
    the simulation; the witness chain converges to the canonical timeline for every
    delivery schedule of one logical log (or refuses / desyncs, typed and localized)."""

    def __init__(self, w, K=8, H=8):
        if K < 1 or H < 1:
            raise RollbackError("ROLLBACK-REFUSE", f"K and H must be >= 1 (got {K}, {H})")
        self.w = w
        self.K, self.H = int(K), int(H)
        self.n, self.r = w["n"], w["r"]
        self.pos, self.vel = _copy_state(w["pos"], w["vel"])
        self._Rf = FP.unit(self.r, 1)
        self._floorf, self._ceilf, self._leftf, self._rightf = (
            FP.unit(w[k], 1) for k in ("floor", "ceil", "left", "right"))
        self._GDT = FP.unit(*w["grav"])
        self._en, self._ed = w["e"]
        self.head = 0
        self.frames = [L._digest(self.pos, self.vel, self.n)]
        self.known = {}                                    # (peer, seq) -> event
        self.snapshots = []                                # (tick, pos, vel), oldest first
        self._take_snapshot()                              # tick 0 is always snapshotted

    # -- snapshots ---------------------------------------------------------------
    def _take_snapshot(self):
        p, v = _copy_state(self.pos, self.vel)
        self.snapshots.append((self.head, p, v))
        if len(self.snapshots) > self.H:
            self.snapshots.pop(0)                          # the horizon moves forward

    def _newest_snapshot_at_or_before(self, tick):
        best = None
        for s in self.snapshots:
            if s[0] <= tick and (best is None or s[0] > best[0]):
                best = s
        return best

    # -- the tick (mirrors lockstep.simulate exactly; the gate pins the equality) --
    def _events_at(self, t):
        evs = [e for e in self.known.values() if e[0] == t]
        evs.sort(key=lambda e: (e[1], e[2]))               # canonical (peer, seq)
        return evs

    def _step_one_tick(self):
        t = self.head
        for (_, _, _, b, dvx, dvy) in self._events_at(t):
            if 0 <= b < self.n:
                self.vel[b][0] = FP.add(self.vel[b][0], FP.unit(dvx, 1))
                self.vel[b][1] = FP.add(self.vel[b][1], FP.unit(dvy, 1))
        for i in range(self.n):
            self.vel[i][1] = FP.add(self.vel[i][1], self._GDT)
            self.pos[i][0] = FP.add(self.pos[i][0], self.vel[i][0])
            self.pos[i][1] = FP.add(self.pos[i][1], self.vel[i][1])
            if self.pos[i][1] + self._Rf > self._floorf and self.vel[i][1] > 0:
                self.pos[i][1] = FP.sub(self._floorf, self._Rf)
                self.vel[i][1] = FP.mul_k(self.vel[i][1], -self._en, self._ed)
            if self.pos[i][1] - self._Rf < self._ceilf and self.vel[i][1] < 0:
                self.pos[i][1] = FP.add(self._ceilf, self._Rf)
                self.vel[i][1] = FP.mul_k(self.vel[i][1], -self._en, self._ed)
            if self.pos[i][0] + self._Rf > self._rightf and self.vel[i][0] > 0:
                self.pos[i][0] = FP.sub(self._rightf, self._Rf)
                self.vel[i][0] = FP.mul_k(self.vel[i][0], -self._en, self._ed)
            if self.pos[i][0] - self._Rf < self._leftf and self.vel[i][0] < 0:
                self.pos[i][0] = FP.add(self._leftf, self._Rf)
                self.vel[i][0] = FP.mul_k(self.vel[i][0], -self._en, self._ed)
        self.head += 1
        self.frames.append(L._digest(self.pos, self.vel, self.n))
        if self.head % self.K == 0:
            self._take_snapshot()

    def advance(self, until_tick):
        """Simulate forward until `until_tick` ticks have been applied."""
        while self.head < min(int(until_tick), self.w["T"]):
            self._step_one_tick()

    # -- delivery ------------------------------------------------------------------
    def deliver(self, e):
        """Accept one input event, in any arrival order.
        Returns "duplicate" | "queued" | ("rolled", snapshot_tick).
        Raises RollbackError: ROLLBACK-CONFLICT (same identity, different payload),
        ROLLBACK-REFUSE (older than the rollback horizon). A refused event is
        rejected WHOLE — no partial state change, the chain is untouched."""
        e = tuple(int(x) for x in e)
        if len(e) != 6:
            raise RollbackError("ROLLBACK-REFUSE", f"malformed event {e!r}")
        identity = (e[1], e[2])
        if identity in self.known:
            if self.known[identity] == e:
                return "duplicate"                         # exact duplicate: absorbed
            raise RollbackError(
                "ROLLBACK-CONFLICT",
                f"identity (peer={e[1]}, seq={e[2]}) already bound to "
                f"{self.known[identity]!r}, refused {e!r}")
        if e[0] >= self.head:
            self.known[identity] = e
            return "queued"
        snap = self._newest_snapshot_at_or_before(e[0])    # late: need a rewind point
        if snap is None:
            raise RollbackError(
                "ROLLBACK-REFUSE",
                f"input at tick {e[0]} is older than the rollback horizon "
                f"(oldest retained snapshot: tick {self.snapshots[0][0]})")
        self.known[identity] = e
        target = self.head
        s_tick, s_pos, s_vel = snap
        self.pos, self.vel = _copy_state(s_pos, s_vel)     # restore (exact by contract)
        self.head = s_tick
        del self.frames[s_tick + 1:]                       # the provisional suffix is void
        self.snapshots = [s for s in self.snapshots if s[0] <= s_tick]
        self.advance(target)                               # re-simulate to the present
        return ("rolled", s_tick)

    def deliver_defect_apply_at_head(self, e):
        """THE DEFECT (gate non-vacuity): the wrong implementation applies a late
        input at the CURRENT head instead of rewinding. Must diverge from the
        canonical timeline — if it converges, the invariant is vacuous."""
        e = tuple(int(x) for x in e)
        self.known[(e[1], e[2])] = (self.head, e[1], e[2], e[3], e[4], e[5])
        return "defect-applied"

    # -- witnesses -------------------------------------------------------------------
    def chain(self):
        return list(self.frames)

    def trace(self):
        return L.trace_digest(self.frames)
