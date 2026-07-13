# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for D16 — regional authority over the authored runtime.

The Phase-3 milestone (D13 §C8): one authoritative simulation, partitioned in space,
must compose back to the SAME witness. A world is cut by integer x-seams into regions;
each region advances its interior by the FROZEN N4/N4.1 tick from an admitted boundary
condition (read-only ghosts) and writes only what it owns. The reunification of the
regional interiors must reproduce the monolithic URDRLST1/URDRLSTT chain bit-for-bit.

Pinned laws (each a falsifier):
  * SEAM COMPOSITION THEOREM — reunify(regions) == monolith, bit-for-bit, and equal to
    the pinned seam2 golden; deterministically twice;
  * PARTITION INVARIANCE — several DIFFERENT valid partitions (incl. the trivial one
    region and a three-region cut) all compose to the one monolithic witness;
  * BOUNDARY IS LOAD-BEARING — dropping the ghost exchange makes cross-seam contact
    silently vanish, so the chain DIVERGES, localized to the first coupled tick;
  * MALFORMED PARTITION REFUSED — a float / non-monotone / non-integer seam is
    REGION-REFUSEd before a single tick is stepped (never a silent guess);
  * NON-VACUITY — the scene really straddles the seam at contact (cross-seam contact is
    exercised, not a same-region collision) AND a body really hands off across it."""
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


def _golden(name):
    path = os.path.join(_ROOT, "tools", "netcode", "conformance_region.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AssertionError(f"golden {name} missing")


def _contact_tick(w, log):
    """The first tick the two bodies are within contact range (r0+r1), from the monolith."""
    _, states = WS.simulate_trace(w, log)
    rr = (w["rs"][0] + w["rs"][1])
    for t, (p, v) in enumerate(states):
        dx = (p[1][0] - p[0][0]) / (1 << 32)
        dy = (p[1][1] - p[0][1]) / (1 << 32)
        if (dx * dx + dy * dy) ** 0.5 < rr:
            return t
    return None


class SeamComposition(unittest.TestCase):
    def test_composition_equals_monolith_and_golden(self):
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        comp = R.region_simulate(w, log, seams)
        self.assertEqual(comp, WS.simulate(w, log),
                         "reunified regional witness != monolith (composition broke)")
        self.assertEqual(L.trace_digest(comp), _golden("seam2"),
                         "seam2 composed trace drifted from its golden")

    def test_deterministic_twice(self):
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        self.assertEqual(R.compose(w, log, seams), R.compose(w, log, seams),
                         "regional composition is nondeterministic")

    def test_partition_invariance(self):
        w, log = R.seam2_world(), R.seam2_log()
        mono = WS.simulate(w, log)
        for seams in ([], [176], [185], [191], [195], [206], [185, 205]):
            self.assertEqual(R.region_simulate(w, log, seams), mono,
                             f"partition {seams} did not compose to the monolith")


class BoundaryIsLoadBearing(unittest.TestCase):
    def test_dropped_boundary_diverges_at_contact_tick(self):
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        mono = WS.simulate(w, log)
        defect = R.region_simulate(w, log, seams, defect_drop_ghost=True)
        self.assertNotEqual(defect, mono, "dropping the ghost changed nothing (boundary vacuous)")
        self.assertEqual(L.first_desync(defect, mono), _contact_tick(w, log),
                         "dropped-boundary divergence was not localized to the contact tick")


class MalformedPartitionRefused(unittest.TestCase):
    def _code(self, seams):
        try:
            R.region_simulate(R.seam2_world(), R.seam2_log(), seams)
            return None
        except R.RegionError as exc:
            return exc.code

    def test_float_seam_refused(self):
        self.assertEqual(self._code([191.5]), "REGION-REFUSE", "float seam not refused")

    def test_non_monotone_refused(self):
        self.assertEqual(self._code([200, 150]), "REGION-REFUSE", "non-monotone seams not refused")

    def test_bool_seam_refused(self):
        self.assertEqual(self._code([True]), "REGION-REFUSE", "bool masquerading as int not refused")

    def test_valid_partition_accepted(self):
        self.assertIsNone(self._code([191]), "a valid partition was wrongly refused")


class NonVacuity(unittest.TestCase):
    def test_collision_straddles_the_seam(self):
        """At the contact tick the two bodies MUST be owned by different regions — else
        the seam is not participating in the physics and the ghost path is untested."""
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        sw = [WS.FP.unit(s, 1) for s in seams]
        _, states = WS.simulate_trace(w, log)
        p, _v = states[_contact_tick(w, log)]
        o0, o1 = R.owner(p[0][0], sw), R.owner(p[1][0], sw)
        self.assertNotEqual(o0, o1, "bodies share a region at contact — cross-seam contact untested")

    def test_a_body_hands_off_across_the_seam(self):
        """Some body MUST change owner during the run — else the handoff is untested."""
        w, log, seams = R.seam2_world(), R.seam2_log(), R.seam2_seam()
        sw = [WS.FP.unit(s, 1) for s in seams]
        _, states = WS.simulate_trace(w, log)
        owners = [[R.owner(p[b][0], sw) for b in range(w["n"])] for (p, _v) in states]
        changed = any(owners[t][b] != owners[t - 1][b]
                      for t in range(1, len(owners)) for b in range(w["n"]))
        self.assertTrue(changed, "no body crossed the seam — handoff untested")


if __name__ == "__main__":
    unittest.main()
