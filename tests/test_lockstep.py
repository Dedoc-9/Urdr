# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for urdr-netcode (deterministic lockstep spine).

Pins the properties that make peers-exchange-inputs-only actually work:
  * the witness chain is DETERMINISTIC (same twice) and matches its frozen golden;
  * two peers assembling the SAME input union in DIFFERENT arrival orders AGREE
    (identical inputs -> identical digests -- lockstep holds);
  * DELIVERY is robust: reordered or duplicated delivery of one logical log is ABSORBED
    (dedup is load-bearing -- a distinct extra impulse would NOT be absorbed);
  * CORRUPTION diverges detectably: a dropped / modified / tick-moved event DESYNCS, and
    the desync is LOCALIZED to the first mismatching tick (non-vacuity: a clean run does
    NOT desync, so the detector is not always firing).
Not exact (fixed-point rounds); each negative test asserts the wrong outcome would pass."""
import os
import re
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lockstep as L                                       # noqa: E402
import rollback as RB                                      # noqa: E402  N2 vocabulary
import authinput as A                                      # noqa: E402  N3 vocabulary
import worldstep as WS                                     # noqa: E402  N4 vocabulary
from field import FixedPoint, FieldError                   # noqa: E402


def _golden():
    p = os.path.join(_ROOT, "tools", "netcode", "conformance_netcode.txt")
    with open(p, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                if name == "arena3":
                    return dig
    raise AssertionError("golden arena3 missing")


class Lockstep(unittest.TestCase):
    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()
        # peer 0 and peer 1 each own their inputs and assemble the union in different orders
        self.a_view = [e for e in self.log if e[1] == 0] + [e for e in self.log if e[1] == 1]
        self.b_view = [e for e in self.log if e[1] == 1] + [e for e in self.log if e[1] == 0]
        self.chain = L.simulate(self.w, self.a_view)[0]

    def test_deterministic_and_golden(self):
        c1 = L.simulate(self.w, self.a_view)[0]
        c2 = L.simulate(self.w, self.a_view)[0]
        self.assertEqual(c1, c2, "lockstep nondeterministic")
        self.assertEqual(L.trace_digest(c1), _golden(), "trace != frozen golden")

    def test_inputs_only_peers_agree(self):
        # identical input union, different arrival order -> identical witness chain + final
        cb, fb = L.simulate(self.w, self.b_view)
        ca, fa = L.simulate(self.w, self.a_view)
        self.assertEqual(ca, cb, "peers disagree on identical inputs (lockstep broken)")
        self.assertEqual(fa, fb)
        self.assertIsNone(L.first_desync(ca, cb), "clean peers must not desync")

    def test_delivery_reorder_and_duplicate_absorbed(self):
        self.assertEqual(L.simulate(self.w, L.reorder_delivery(self.a_view))[0], self.chain,
                         "reordered delivery changed the result")
        self.assertEqual(L.simulate(self.w, L.duplicate_delivery(self.a_view))[0], self.chain,
                         "duplicated delivery changed the result")

    def test_dedup_is_load_bearing(self):
        # a DISTINCT extra impulse (new seq -> not an exact duplicate) MUST change the chain,
        # proving the absorption above is real dedup, not "impulses do not matter"
        e = self.a_view[1]
        distinct = list(self.a_view) + [(e[0], e[1], 999, e[3], e[4], e[5])]
        self.assertNotEqual(L.simulate(self.w, distinct)[0], self.chain,
                            "a genuinely different input was absorbed (dedup too aggressive)")

    def test_corruption_desyncs_and_localizes(self):
        i = 1                                              # a_view[1] is a peer-0 input at some tick
        tick = self.a_view[i][0]
        for name, faulted, expect in (
            ("drop",   L.drop_event(self.a_view, i),            tick + 1),
            ("modify", L.modify_event(self.a_view, i),          tick + 1),
            ("move",   L.move_event_tick(self.a_view, i, tick - 1), tick),   # min(tick-1,tick)+1
        ):
            fc = L.simulate(self.w, faulted)[0]
            self.assertNotEqual(fc, self.chain, "%s fault did not desync (silent divergence!)" % name)
            self.assertEqual(L.first_desync(self.chain, fc), expect,
                             "%s fault mislocalized" % name)

    def test_substrate_bounded_refuses(self):
        # the frozen substrate underneath refuses rather than wrap on i64 overflow
        with self.assertRaises(FieldError):
            FixedPoint.mul_k(FixedPoint.unit(3, 1), (1 << 62), 1)


class TheSpineHasADoor(unittest.TestCase):
    """The exemption this retires said a refusal here was impossible: one inside `canon`
    would change the frozen contract, so the boundary belonged to callers. That was right
    about `canon` and wrong about the SPINE. The door sits in FRONT of the frozen surface
    — `canon`, `_digest`, `trace_digest` and the tick's absorbing `if` are untouched, and
    `specfreeze/freeze_check.py` cross-checks two of them independently."""

    def setUp(self):
        self.w = L.world()
        self.log = L.sample_log()
        self.golden = L.trace_digest(L.simulate(self.w, self.log)[0])

    def _bad(self, **kw):
        t, p, s, b, dx, dy = self.log[0]
        d = dict(tick=t, peer=p, seq=s, body=b, dvx=dx, dvy=dy)
        d.update(kw)
        return [(d["tick"], d["peer"], d["seq"], d["body"], d["dvx"], d["dvy"])] \
            + list(self.log[1:])

    def test_every_class_the_spine_absorbed_is_now_typed(self):
        for label, lg in (("body == n", self._bad(body=self.w["n"])),
                          ("body < 0", self._bad(body=-1)),
                          ("tick == T", self._bad(tick=self.w["T"])),
                          ("tick < 0", self._bad(tick=-5)),
                          ("float impulse", self._bad(dvx=5.5)),
                          ("string tick", self._bad(tick="3")),
                          ("bool body", self._bad(body=True)),
                          ("wrong arity", [self.log[0][:3]] + list(self.log[1:]))):
            with self.subTest(label):
                with self.assertRaises(L.LockstepError) as ctx:
                    L.simulate(self.w, lg)
                self.assertEqual(ctx.exception.code, "LOCKSTEP-REFUSE")

    def test_the_frozen_surface_is_untouched(self):
        """The claim the retired exemption was protecting, MEASURED rather than argued.
        `canon` still absorbs whatever it is handed, the pinned trace is bit-identical,
        and the tick's absorbing `if` still drops when `step`-level code calls it."""
        self.assertEqual(len(L.canon([(999, 0, 0, 99, 1, 1)])), 1)   # canon: no refusal
        self.assertEqual(L.trace_digest(L.simulate(self.w, self.log)[0]), self.golden)
        self.assertEqual(L.sample_trace(), self.golden)

    def test_the_boundary_is_the_boundary(self):
        L.simulate(self.w, self._bad(body=self.w["n"] - 1))
        L.simulate(self.w, self._bad(tick=self.w["T"] - 1))

    def test_the_corruption_helpers_still_desync_rather_than_refuse(self):
        """NON-VACUITY: the door must not eat the desync fixtures. A dropped, modified or
        tick-moved event is a DIVERGENCE, not malformed input, and must stay one."""
        for lg in (L.drop_event(self.log, 1), L.modify_event(self.log, 1),
                   L.move_event_tick(self.log, 1, self.log[1][0] - 1)):
            d = L.trace_digest(L.simulate(self.w, lg)[0])
            self.assertNotEqual(d, self.golden)

class TheFourVocabularies(unittest.TestCase):
    """ONE law, FOUR codes — and an honest boundary on what that buys.

    The prose said "merging the codes would destroy attribution". Nothing in the repo
    pays that cost: searched for consumers that branch on WHICH netcode admission code
    they caught, there are exactly two, both in `verify.py` (ROLLBACK-REFUSE vs
    ROLLBACK-CONFLICT, and the AUTH-MALFORMED projection check). The split is for a
    READER and for the GATE. This class measures both halves, so the GRADE in
    `lockstep.event_fault` reddens if either stops being true — including if the claim
    becomes too MODEST because a consumer starts branching."""

    #: shape-malformed, so all four layers can judge it — N3 has no world and can only
    #: ask the world-free half of the law.
    BAD = (3, 0, 0, 0, 5.5, 0)

    def setUp(self):
        self.w = L.world()
        self.ww = WS.arena_world()

    def _refusal(self, fn):
        try:
            fn()
        except Exception as exc:                           # noqa: BLE001  the code is the point
            return getattr(exc, "code", type(exc).__name__), str(exc)
        raise AssertionError("no refusal — the door is not there")

    def test_one_predicate_four_distinct_codes(self):
        """The checkable half. Each entry path refuses the SAME event with its OWN code,
        and the REASON text is identical across all four, which is what "written once"
        means operationally: a copy that drifted would change one message."""
        seen = {}
        for layer, fn in (
                ("N1 spine", lambda: L.simulate(self.w, [self.BAD])),
                ("N2 time", lambda: RB.Peer(self.w).deliver(self.BAD)),
                ("N3 wire", lambda: A.admit_event(self.BAD)),
                ("N4 world", lambda: WS.admit_event_for_world(self.ww, self.BAD))):
            with self.subTest(layer):
                code, msg = self._refusal(fn)
                seen[layer] = (code, msg.split(": ", 1)[1])
        codes = [c for c, _ in seen.values()]
        self.assertEqual(sorted(codes), ["AUTH-MALFORMED", "LOCKSTEP-REFUSE",
                                         "ROLLBACK-REFUSE", "WORLD-REFUSE"])
        self.assertEqual(len(set(codes)), 4, "a merged code: %r" % (seen,))
        self.assertEqual(len({m for _, m in seen.values()}), 1,
                         "the reason text drifted between layers: %r" % (seen,))

    def test_no_consumer_branches_on_which_layer_refused(self):
        """The `does_not_show` half, MEASURED rather than asserted in prose. `tools/`
        contains no code that changes behaviour based on which of the four it caught. If
        that ever stops being true this reddens, and the honest response is to UPGRADE
        the grade in `event_fault` — a falsifier that fires when a claim becomes too
        modest is as load-bearing as one that fires when it becomes too generous."""
        codes = ("LOCKSTEP-REFUSE", "ROLLBACK-REFUSE", "AUTH-MALFORMED", "WORLD-REFUSE")
        pat = re.compile(r"\.code\s*(?:==|!=|\bin\b)[^\n]*?(%s)" % "|".join(codes))
        hits = []
        for base, _dirs, files in os.walk(os.path.join(_ROOT, "tools")):
            for fn in files:
                if not fn.endswith(".py"):
                    continue
                p = os.path.join(base, fn)
                with open(p, encoding="utf-8") as fh:
                    for i, ln in enumerate(fh, 1):
                        if pat.search(ln):
                            hits.append("%s:%d" % (os.path.relpath(p, _ROOT), i))
        self.assertEqual(hits, [], "a consumer now branches on the layer: %r" % (hits,))


if __name__ == "__main__":
    unittest.main()
