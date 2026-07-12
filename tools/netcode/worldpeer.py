# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode N5 — AUTHENTICATED ROLLBACK OVER AUTHORED WORLDS: the platform
sentence, composed and falsifiable.

    Given the same authored world, the same authenticated input transcript, and the
    same initial snapshot, every conforming implementation either CONVERGES to the
    identical witness chain or produces the SAME TYPED REFUSAL; no intermediate
    divergence silently persists.

N5 builds NOTHING new below the interface line — it composes the four admitted
rungs and adds exactly one law:

  * the WORLD PIN (`URDRWPN1`, the one new law): SHA-256 over the canonical
    runtime-world serialization — body count, per-body pos/vel, radii, static
    AABBs, bounds, gravity, restitution, T, each signed i64 BE. A peer REFUSES a
    world whose pin mismatches BEFORE any tick runs (`WORLD-REFUSE`). frames[0]
    cannot do this job: two worlds differing only in a static share their initial
    witness; the pin covers everything the tick reads.
  * N3 gates admission: a Lamport envelope must verify against the roster pin, or
    AUTH-REFUSE — nothing reaches the authority (authinput.verify, frozen).
  * N2's law handles time: canonical snapshots every K (retain H); a late-but-valid
    input rewinds to the newest snapshot at-or-before its tick and replays;
    ROLLBACK-REFUSE beyond the horizon; ROLLBACK-CONFLICT on a same-(peer,seq)-
    different-payload envelope — the SAME frozen exception type (rollback.RollbackError).
  * N4's tick is the authority: worldstep.step_tick (0.3 additive — one tick law,
    shared with simulate/simulate_trace, digest-preservation gated).
  * N1's laws witness everything: URDRLST1 per tick, URDRLSTT for the run, and the
    convergence oracle is `worldstep.simulate` — on the canonical scenario the
    converged golden IS the N4 highway golden.

GRADE (honest, D5): MEASURED (both placements) — the `netcode_worldpeer` gate stage
pins the world pin, roster root, convergence at two cadences, refusals, and the
verified apply-at-head defect; the std-only Rust placement (worldpeer_rs/, ADMITTED
on Windows/rustc) reproduces all five anchors including the defect's exact divergent
digest (d5bc484b…, shared with the C99 cross-check). Contracts FROZEN at
urdr-netcode-worldpeer 0.1 (spec/D12) — complete by AGENTS rule 11. Honest scope
inherited whole: fixture keys from published seeds (mechanism, not key secrecy);
regime B rounding; N4's inert mass; K/H operational."""
import hashlib
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "physics"))

import lockstep as L                                       # noqa: E402  frozen N1 laws
import worldstep as WS                                     # noqa: E402  N4 tick (0.3)
import authinput as A                                      # noqa: E402  frozen N3 verify
from rollback import RollbackError                         # noqa: E402  frozen N2 vocabulary


def _i64(v):
    return int(v).to_bytes(8, "big", signed=True)


def world_pin(w):
    """URDRWPN1 — the runtime world's full identity, one digest. Everything the
    tick reads is covered; nothing the tick ignores is."""
    out = bytearray(b"URDRWPN1")
    out += _i64(w["n"])
    for p in w["pos"]:
        out += _i64(p[0]) + _i64(p[1])
    for v in w["vel"]:
        out += _i64(v[0]) + _i64(v[1])
    for r in w["rs"]:
        out += _i64(r)
    out += _i64(len(w["statics"]))
    for (x0, y0, x1, y1) in w["statics"]:
        out += _i64(x0) + _i64(y0) + _i64(x1) + _i64(y1)
    for k in ("floor", "ceil", "left", "right"):
        out += _i64(w[k])
    out += _i64(w["grav"][0]) + _i64(w["grav"][1])
    out += _i64(w["e"][0]) + _i64(w["e"][1]) + _i64(w["T"])
    return hashlib.sha256(bytes(out)).hexdigest()


def _copy(pos, vel):
    return [list(p) for p in pos], [list(v) for v in vel]


class WorldPeer:
    """An authenticated, rollback-capable peer over an AUTHORED world. Verify, then
    admit, then simulate: authentication decides who may write, the N4 tick decides
    what results, the frozen witness laws prove what happened."""

    def __init__(self, w, roster, expected_pin, K=8, H=8):
        if K < 1 or H < 1:
            raise RollbackError("ROLLBACK-REFUSE", f"K and H must be >= 1 (got {K}, {H})")
        pin = world_pin(w)
        if pin != expected_pin:
            raise WS.WorldError(
                "WORLD-REFUSE",
                f"world pin {pin[:12]}… ≠ expected {str(expected_pin)[:12]}… — "
                f"refused before any simulation")
        self.w = w
        self.roster = dict(roster)
        self.K, self.H = int(K), int(H)
        self.n = w["n"]
        self.pos, self.vel = _copy(w["pos"], w["vel"])
        self.head = 0
        self.frames = [L._digest(self.pos, self.vel, self.n)]
        self.known = {}                                    # (peer, seq) -> event
        self.snapshots = []                                # (tick, pos, vel), oldest first
        self._take_snapshot()

    # -- snapshots (the N2 law over authored state) --------------------------------
    def _take_snapshot(self):
        p, v = _copy(self.pos, self.vel)
        self.snapshots.append((self.head, p, v))
        if len(self.snapshots) > self.H:
            self.snapshots.pop(0)                          # the horizon moves forward

    def _newest_snapshot_at_or_before(self, tick):
        best = None
        for s in self.snapshots:
            if s[0] <= tick and (best is None or s[0] > best[0]):
                best = s
        return best

    # -- stepping (the N4 tick; witnesses by the frozen N1 law) ---------------------
    def _events_at(self, t):
        evs = [e for e in self.known.values() if e[0] == t]
        evs.sort(key=lambda e: (e[1], e[2]))
        return evs

    def advance(self, until_tick):
        while self.head < min(int(until_tick), self.w["T"]):
            WS.step_tick(self.w, self.pos, self.vel, self._events_at(self.head))
            self.head += 1
            self.frames.append(L._digest(self.pos, self.vel, self.n))
            if self.head % self.K == 0:
                self._take_snapshot()

    # -- admission (auth first; then the N2 identity/time law) ----------------------
    def _admit(self, e):
        identity = (e[1], e[2])
        if identity in self.known:
            if self.known[identity] == e:
                return "duplicate"
            raise RollbackError(
                "ROLLBACK-CONFLICT",
                f"identity (peer={e[1]}, seq={e[2]}) already bound to "
                f"{self.known[identity]!r}, refused {e!r}")
        if e[0] >= self.head:
            self.known[identity] = e
            return "queued"
        snap = self._newest_snapshot_at_or_before(e[0])
        if snap is None:
            raise RollbackError(
                "ROLLBACK-REFUSE",
                f"input at tick {e[0]} is older than the rollback horizon "
                f"(oldest retained snapshot: tick {self.snapshots[0][0]})")
        self.known[identity] = e
        target = self.head
        s_tick, s_pos, s_vel = snap
        self.pos, self.vel = _copy(s_pos, s_vel)
        self.head = s_tick
        del self.frames[s_tick + 1:]
        self.snapshots = [s for s in self.snapshots if s[0] <= s_tick]
        self.advance(target)
        return ("rolled", s_tick)

    def deliver_envelope(self, env):
        """Verify-then-admit. AUTH-REFUSE (whole, nothing touched) on an unregistered
        identity or a failed signature; then the N2 admission law applies unchanged."""
        e, pub, sig = env
        e = tuple(int(x) for x in e)
        ident = (e[1], e[2])
        pin = self.roster.get(ident)
        if pin is None:
            raise A.AuthError("AUTH-REFUSE", f"identity {ident} not in the roster")
        if not A.verify((e, pub, sig), pin):
            raise A.AuthError("AUTH-REFUSE",
                              f"envelope for identity {ident} failed verification")
        return self._admit(e)

    def deliver_envelope_defect_apply_at_head(self, env):
        """THE DEFECT (gate non-vacuity): a VERIFIED late envelope applied at the
        current head instead of rewound — auth passes, so a convergence failure is
        rollback's alone. Must diverge from the oracle."""
        e, pub, sig = env
        e = tuple(int(x) for x in e)
        ident = (e[1], e[2])
        pin = self.roster.get(ident)
        if pin is None or not A.verify((e, pub, sig), pin):
            raise A.AuthError("AUTH-REFUSE", "defect path still verifies first")
        self.known[ident] = (self.head, e[1], e[2], e[3], e[4], e[5])
        return "defect-applied"

    # -- witnesses -------------------------------------------------------------------
    def chain(self):
        return list(self.frames)

    def trace(self):
        return L.trace_digest(self.frames)
