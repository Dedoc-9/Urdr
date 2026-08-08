# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode N4 — authored URDR-WORLD-3 worlds in the deterministic
netcode loop.

The claim under test: a user-authored world (the frozen URDR-WORLD-3 export) can be
loaded into a deterministic, input-driven runtime whose witness chains obey the SAME
frozen laws (URDRLST1/URDRLSTT) and the SAME netcode properties (peers agree, faults
localize) — new capability as a new consumer, zero authority semantics changed:

  * EQUIVALENCE PIN (anti-drift): on the canonical arena — same bodies, box, gravity,
    restitution, NO statics — worldstep's chain equals `lockstep.simulate`'s chain
    bit-for-bit over the canonical log. Any divergence between the two ticks reds
    this on every vector;
  * the canonical authored scene (demo/world_highway.json: two closing vehicles, one
    static median) loads deterministically and reproduces its pinned trace golden;
  * STATICS ARE LOAD-BEARING: deleting the median changes the chain (the barrier
    actually deflects — the golden is not vacuously independent of the scene);
  * INSTANCE ORDER IS CONTENT: swapping two dynamic instances permutes body indexing
    and changes the chain (the export's file order is part of world identity);
  * two peers assembling one authored-world input log in different arrival orders
    reproduce ONE chain; a dropped input desyncs, localized by first_desync, and the
    complete run does not;
  * the authoring boundary is typed: a non-integer coordinate in the export is a
    WORLD-REFUSE (never silently rounded — D11 §4b, crossing is explicit);
  * determinism ×2, and the defect (a step that ignores statics) diverges from the
    golden — the gate can redden.
Honest scope: bounded fixed-point (regime B — rounds, refuses on overflow); instance
mass is loaded but inert until body-body contact arrives (DECLARED); cross-placement
of this runtime is DECLARED."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
import worldstep as W                                      # noqa: E402

_HIGHWAY = os.path.join(_ROOT, "demo", "world_highway.json")


def _load_highway():
    with open(_HIGHWAY, encoding="utf-8") as fh:
        return json.load(fh)


class Equivalence(unittest.TestCase):
    def test_arena_equivalence_with_frozen_lockstep(self):
        """No statics + the canonical arena -> worldstep's chain EQUALS the frozen
        N1 chain bit-for-bit. This is the anti-drift pin between the two ticks."""
        lw = L.world()
        ww = W.arena_world()                               # the same arena, worldstep shape
        frames_l, _ = L.simulate(lw, L.sample_log())
        frames_w = W.simulate(ww, L.sample_log())
        self.assertEqual(frames_w, frames_l)


class AuthoredHighway(unittest.TestCase):
    def setUp(self):
        self.doc = _load_highway()
        self.log = W.sample_world_log()

    def test_loads_and_reproduces_golden(self):
        """The canonical authored scene runs deterministically twice and matches the
        pinned golden trace (conformance_world.txt: highway)."""
        w1 = W.world_from_export(self.doc)
        w2 = W.world_from_export(self.doc)
        t1 = W.trace(W.simulate(w1, self.log))
        t2 = W.trace(W.simulate(w2, self.log))
        self.assertEqual(t1, t2)
        self.assertEqual(t1, W.golden("highway"),
                         "highway trace does not match its pinned golden")

    def test_statics_are_load_bearing(self):
        """Deleting the median changes the chain — the barrier deflects for real."""
        doc = _load_highway()
        doc["instances"] = [i for i in doc["instances"] if i.get("body") != "static"]
        w_no = W.world_from_export(doc)
        w_yes = W.world_from_export(self.doc)
        self.assertNotEqual(W.simulate(w_yes, self.log), W.simulate(w_no, self.log),
                            "removing the barrier changed nothing — statics vacuous")

    def test_instance_order_is_content(self):
        """Swapping the two vehicles permutes body indexing -> a different chain."""
        doc = _load_highway()
        dyn = [i for i in doc["instances"] if i.get("body") == "dynamic"]
        rest = [i for i in doc["instances"] if i.get("body") != "dynamic"]
        doc["instances"] = [dyn[1], dyn[0]] + rest
        self.assertNotEqual(
            W.simulate(W.world_from_export(self.doc), self.log),
            W.simulate(W.world_from_export(doc), self.log),
            "instance order did not affect the chain — indexing law untested")

    def test_noninteger_authoring_refused(self):
        """A float coordinate in the export is a typed WORLD-REFUSE, never rounded."""
        doc = _load_highway()
        doc["instances"][0]["ground_x"] = 60.5
        with self.assertRaises(W.WorldError) as ctx:
            W.world_from_export(doc)
        self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_peers_agree_and_faults_localize(self):
        """N1's properties hold on authored state: one union, any arrival order, one
        chain; a dropped input desyncs at its first affected witness; complete run
        does not desync."""
        w = W.world_from_export(self.doc)
        a_view = [e for e in self.log if e[1] == 0] + [e for e in self.log if e[1] == 1]
        b_view = [e for e in self.log if e[1] == 1] + [e for e in self.log if e[1] == 0]
        ca = W.simulate(w, a_view)
        cb = W.simulate(w, b_view)
        self.assertEqual(ca, cb, "peers disagree on identical authored-world inputs")
        dropped = W.simulate(w, self.log[1:])
        d = L.first_desync(dropped, ca)
        self.assertIsNotNone(d, "a dropped input went unnoticed")
        self.assertEqual(d, self.log[0][0] + 1, "desync not localized")
        self.assertIsNone(L.first_desync(W.simulate(w, list(self.log)), ca))

    def test_simulate_trace_is_digest_preserving(self):
        """0.2 additive surface: `simulate_trace` returns (frames, states) where frames
        are BYTE-IDENTICAL to `simulate`'s (the 0.1 frozen surface is untouched) and
        states carry one (pos, vel) snapshot per frame for display-only consumers."""
        w = W.world_from_export(self.doc)
        frames_old = W.simulate(W.world_from_export(self.doc), self.log)
        frames_new, states = W.simulate_trace(w, self.log)
        self.assertEqual(frames_new, frames_old,
                         "simulate_trace drifted from simulate — the additive claim is false")
        self.assertEqual(len(states), len(frames_new),
                         "one state snapshot per frame, including the initial frame")
        n = w["n"]
        for (pos, vel) in (states[0], states[-1]):
            self.assertEqual((len(pos), len(vel)), (n, n))

    def test_defect_ignoring_statics_diverges(self):
        """The gate's defect: a step that skips static collision MUST diverge from
        the golden (if it converges, the highway golden is vacuous)."""
        w = W.world_from_export(self.doc)
        good = W.trace(W.simulate(w, self.log))
        bad = W.trace(W.simulate(w, self.log, defect_no_statics=True))
        self.assertNotEqual(good, bad, "the no-statics defect converged")


class TheCallerOwnedAdmission(unittest.TestCase):
    """`step_tick`'s `if 0 <= b < n:` and `simulate_trace`'s `range(w["T"])` silently
    DROPPED an out-of-range body and an out-of-horizon tick. Not a desync — every
    conforming peer drops identically — but a peer whose input was discarded and one that
    never sent are indistinguishable afterwards, which is the THIN-versus-DEVIATE
    conflation `geoquorum` and `tilemin` refuse. A drop is a decision with no record."""

    def setUp(self):
        self.w = W.arena_world()
        self.log = L.sample_log()
        self.clean = L.trace_digest(W.simulate(self.w, self.log))

    def _bad(self, **kw):
        t, p, s, b, dx, dy = self.log[0]
        d = dict(tick=t, peer=p, seq=s, body=b, dvx=dx, dvy=dy)
        d.update(kw)
        return [(d["tick"], d["peer"], d["seq"], d["body"], d["dvx"], d["dvy"])] \
            + list(self.log[1:])

    def test_an_out_of_range_body_is_refused_not_dropped(self):
        for body in (self.w["n"], self.w["n"] + 50, -1):
            with self.subTest(body=body):
                with self.assertRaises(W.WorldError) as ctx:
                    W.simulate(self.w, self._bad(body=body))
                self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_an_out_of_horizon_tick_is_refused_not_dropped(self):
        for tick in (self.w["T"], self.w["T"] + 1000, -5):
            with self.subTest(tick=tick):
                with self.assertRaises(W.WorldError) as ctx:
                    W.simulate(self.w, self._bad(tick=tick))
                self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_the_boundary_is_the_boundary(self):
        """voxin's law: a refusal one short of the derived bound means the enforced
        bound is not the derived one. The last body and the last tick must ADMIT."""
        W.simulate(self.w, self._bad(body=self.w["n"] - 1))
        W.simulate(self.w, self._bad(tick=self.w["T"] - 1))

    def test_shape_is_refused_here_too_under_the_worlds_own_code(self):
        """The raw-log path never touches the wire, so `authinput`'s AUTH-MALFORMED
        cannot reach it — it crashed untyped instead. N4 must not import N3 to know what
        a world is, and the two answer different questions: 'this is not an event'
        against 'this event is not for this world'."""
        for bad in ([self.log[0][:3]], ["not an event"], [(1, 2, 3, 4, 5, 5.5)],
                    [(1, 2, 3, True, 5, 6)]):
            with self.subTest(repr(bad)[:40]):
                with self.assertRaises(W.WorldError) as ctx:
                    W.simulate(self.w, bad)
                self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_admission_runs_over_the_whole_log_before_any_tick(self):
        """`observe`'s law: lazy validation would make admission depend on the ANSWER,
        since an event past the last tick a run reaches would never be examined. The bad
        event here sits at the END of the log and must still refuse."""
        with self.assertRaises(W.WorldError) as ctx:
            W.simulate(self.w, list(self.log) + [(0, 0, 99, 999, 1, 1)])
        self.assertEqual(ctx.exception.code, "WORLD-REFUSE")

    def test_the_clean_corpus_is_untouched(self):
        """NON-VACUITY THE OTHER WAY: a door that refused everything would pass every
        assertion above. The canonical arena chain must be bit-identical."""
        self.assertEqual(L.trace_digest(W.simulate(self.w, self.log)), self.clean)
        self.assertEqual(self.clean,
                         L.trace_digest(L.simulate(L.world(), self.log)[0]))

    def test_the_frozen_tick_still_absorbs_which_is_why_this_is_a_door(self):
        """The absorbing `if 0 <= b < n:` is deliberately LEFT in `step_tick`: it is the
        frozen tick's behaviour, shared byte-for-byte with `lockstep`, and this rung adds
        a door in FRONT of it rather than changing it. Called directly, it still drops."""
        pos = [[c for c in p] for p in self.w["pos"]]
        vel = [[c for c in v] for v in self.w["vel"]]
        before = L._digest(pos, vel, self.w["n"])
        W.step_tick(self.w, pos, vel, [(0, 0, 0, 999, 5, 5)])   # out of range, absorbed
        pos2 = [[c for c in p] for p in self.w["pos"]]
        vel2 = [[c for c in v] for v in self.w["vel"]]
        W.step_tick(self.w, pos2, vel2, [])                     # no events at all
        self.assertEqual(L._digest(pos, vel, self.w["n"]),
                         L._digest(pos2, vel2, self.w["n"]))
        self.assertNotEqual(before, L._digest(pos, vel, self.w["n"]))


if __name__ == "__main__":
    unittest.main()
