# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the field-level desync localizer (`tools/netcode/observe.py`).

`first_desync` names the first mismatching TICK from two witness chains; `first_field_desync`
names the exact BODY and FIELD, scanned in `URDRLST1` serialization order, from the two state
chains. The two must agree on the tick by construction (the field it returns is the first byte
group of the first differing digest). Pinned laws:

  * IDENTITY — identical chains localize to `None` (no false positive);
  * SEAM2 GOLDEN — the D16 dropped-ghost divergence localizes to (tick 11, body 0, vel.x), and
    that tick equals `first_desync` on the digest chains;
  * FIRST-DIFFERENCE — every field strictly before the named one (in witness order) is equal in
    both chains (it is really the *first*, not merely *a*, divergence);
  * GENERAL — it localizes a plain worldstep (dropped-input) divergence too, not only seam2;
  * NON-VACUITY — a position-only scan MISSES the velocity-only divergence at its true tick
    (detection slips a tick later), proving the velocity scan is load-bearing;
  * COMPOSITION AT FIELD GRANULARITY — the clean region state chain equals the monolith's."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import lockstep as L                                        # noqa: E402
import worldstep as WS                                      # noqa: E402
import worldregion as R                                     # noqa: E402
from observe import first_field_desync, FIELDS              # noqa: E402


def _pos_only(states_a, states_b):
    """A DEFECT localizer that scans only position fields — used to prove the velocity scan
    in the real localizer is load-bearing."""
    for t in range(min(len(states_a), len(states_b))):
        pa, _ = states_a[t]
        pb, _ = states_b[t]
        for i in range(min(len(pa), len(pb))):
            for ax in (0, 1):
                if pa[i][ax] != pb[i][ax]:
                    return (t, i, "pos", ax)
    return None


class FieldDesync(unittest.TestCase):
    def _seam2(self, drop):
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        return R.region_simulate_trace(w, log, seams, defect_drop_ghost=drop)

    def test_identity_is_none(self):
        _, st = self._seam2(False)
        self.assertIsNone(first_field_desync(st, st), "identical chains reported a desync")

    def test_seam2_localizes_to_body0_velx(self):
        cf, cst = self._seam2(False)
        df, dst = self._seam2(True)
        fd = first_field_desync(cst, dst)
        self.assertIsNotNone(fd, "the dropped-ghost divergence was not localized")
        t, i, kind, ax, a, b = fd
        self.assertEqual((t, i, kind, ax), (11, 0, "vel", 0),
                         f"seam2 field-desync moved: {(t, i, kind, ax)}")
        self.assertNotEqual(a, b, "the named field does not actually differ")
        self.assertEqual(t, L.first_desync(cf, df),
                         "field-desync tick disagrees with the witness-chain first_desync")

    def test_it_is_the_first_difference(self):
        _, cst = self._seam2(False)
        _, dst = self._seam2(True)
        t, i, kind, ax, _, _ = first_field_desync(cst, dst)
        target = (kind, ax)
        # every (body, field) strictly before (i, target) at tick t — and all earlier ticks —
        # must be equal in both chains.
        for tt in range(t):
            self.assertEqual(cst[tt], dst[tt], f"an earlier tick {tt} already differed")
        pa, va = cst[t]; pb, vb = dst[t]
        for bi in range(i + 1):
            for (k, a2) in FIELDS:
                if bi == i and (k, a2) == target:
                    break
                wa = (pa if k == "pos" else va)[bi][a2]
                wb = (pb if k == "pos" else vb)[bi][a2]
                self.assertEqual(wa, wb, f"a field before the named one differed: body {bi} {k}{a2}")

    def test_general_over_worldstep_dropped_input(self):
        w = WS.arena_world()
        full = WS.simulate_trace(w, L.sample_log())
        dropped = WS.simulate_trace(w, L.sample_log()[1:])
        fd = first_field_desync(full[1], dropped[1])
        self.assertIsNotNone(fd, "a dropped input produced no field desync")
        self.assertEqual(fd[0], L.first_desync(full[0], dropped[0]),
                         "field-desync tick disagrees with first_desync on a worldstep run")

    def test_position_only_scan_misses_velocity_divergence(self):
        _, cst = self._seam2(False)
        _, dst = self._seam2(True)
        full = first_field_desync(cst, dst)
        pos_only = _pos_only(cst, dst)
        self.assertEqual(full[2], "vel", "the true first divergence is not a velocity field")
        self.assertIsNotNone(pos_only, "position eventually differs; the defect found nothing")
        self.assertLess(full[0], pos_only[0],
                        "position-only detection did NOT slip later — the velocity scan is vacuous")

    def test_region_states_reunify_to_monolith(self):
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        _, region_states = R.region_simulate_trace(w, log, seams)
        _, mono_states = WS.simulate_trace(w, log)
        self.assertEqual(region_states, mono_states,
                         "the reunified region states differ from the monolith (composition broke)")


if __name__ == "__main__":
    unittest.main()
