#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the division-free 𝔽₂ persistent-homology witness
(tools/homology/urdr_homology.py, URDRPD1) and its anti-cheat / OOB layer."""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HOM = os.path.join(ROOT, "tools", "homology")
if _HOM not in sys.path:
    sys.path.insert(0, _HOM)

import urdr_homology as H  # noqa: E402


def _corpus():
    path = os.path.join(_HOM, "conformance_homology.txt")
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                k, v = line.split()
                out[k] = v
    return out


class KnownAnswer(unittest.TestCase):
    """Betti numbers of shapes whose topology is textbook — validity, not outcome."""

    def test_known_shapes_match_pinned(self):
        c = _corpus()
        for name, (fn, _exp) in H.KNOWN.items():
            got = "".join(map(str, H.betti(fn())))
            self.assertEqual(got, c["betti_" + name], name)

    def test_sphere_has_a_void(self):
        self.assertEqual(H.betti(H.demo_sphere()), [1, 0, 1])  # beta2 = the S^2 void


class TwoCountsAgree(unittest.TestCase):
    """The rank-side Betti and the persistence essential-class count must agree —
    two independent computations of the same invariant (non-vacuity)."""

    def test_square_filtration_two_counts(self):
        pts = H.demo_points()
        rank = H.betti(H.final_complex(pts))
        pers = H.betti_from_diagram(H.diagram(pts))
        self.assertEqual(rank, pers)
        self.assertEqual("".join(map(str, pers)), _corpus()["betti_square"])


class BoundaryLemma(unittest.TestCase):
    def test_boundary_squared_is_zero(self):
        for _n, (fn, _e) in H.KNOWN.items():
            self.assertTrue(H.boundary_squared_is_zero(fn()))


class Witness(unittest.TestCase):
    def test_persistence_witness_pinned_and_stable(self):
        pts = H.demo_points()
        w1, w2 = H.witness(H.diagram(pts)), H.witness(H.diagram(pts))
        self.assertEqual(w1, w2)
        self.assertEqual(w1, _corpus()["pd_square"])

    def test_field_is_recorded(self):
        # A witness computed under a different field tag MUST differ (Betti numbers
        # are field-dependent; an untagged diagram would be unfalsifiable).
        pts = H.demo_points()
        self.assertNotEqual(H.witness(H.diagram(pts)),
                            H.witness(H.diagram(pts), field=b"GF3"))


class DefectBites(unittest.TestCase):
    """Each defect MUST diverge from its golden — the gate can redden."""

    def test_dropped_face_changes_betti(self):
        self.assertNotEqual(H.betti(H.demo_sphere_defect_drop_face()),
                            H.betti(H.demo_sphere()))

    def test_map_tamper_changes_static_witness(self):
        c = _corpus()
        good = H.oob_witness(H.demo_arena(), H.DEMO_SPAWN)
        bad = H.oob_witness(H.demo_arena_defect_open_pocket(), H.DEMO_SPAWN)
        self.assertEqual(good, c["oob_arena"])
        self.assertEqual(bad, c["oob_defect"])
        self.assertNotEqual(good, bad)

    def test_clip_changes_occupancy_signature(self):
        c = _corpus()
        ok = H.occupancy_signature(H.demo_arena(), H.DEMO_SPAWN, H.demo_bodies_ok())
        clip = H.occupancy_signature(H.demo_arena(), H.DEMO_SPAWN, H.demo_bodies_clip())
        self.assertEqual(ok, c["occ_ok"])
        self.assertEqual(clip, c["occ_clip"])
        self.assertNotEqual(ok, clip)


class AntiCheat(unittest.TestCase):
    """A clip / OOB position must NEVER score OK (the whole contract)."""

    def setUp(self):
        self.g = H.demo_arena()
        self.L, self.M, self.A = H.label_free_space(self.g, H.DEMO_SPAWN)

    def _loc(self, p):
        return H.locate(self.g, self.L, self.M, self.A, p)

    def test_authorized_is_ok(self):
        self.assertEqual(self._loc((3, 3)), H.OK)

    def test_sealed_pocket_is_clip(self):
        self.assertEqual(self._loc((5, 5)), H.CLIP_POCKET)

    def test_inside_wall_is_clip(self):
        self.assertEqual(self._loc((2, 2)), H.CLIP_WALL)

    def test_exterior_is_oob(self):
        self.assertEqual(self._loc((0, 0)), H.OOB)


class Refusals(unittest.TestCase):
    """Typed TOPOLOGY-REFUSE, never a silent integer wrap."""

    def test_sqdist_overflow_refuses(self):
        with self.assertRaises(H.TopologyError) as cm:
            H.sq_dist((0, 0), (1 << 40, 0))
        self.assertEqual(cm.exception.code, "TOPOLOGY-REFUSE")

    def test_spawn_in_solid_refuses(self):
        with self.assertRaises(H.TopologyError) as cm:
            H.label_free_space(H.demo_arena(), (2, 2))  # (2,2) is a wall
        self.assertEqual(cm.exception.code, "TOPOLOGY-REFUSE")


if __name__ == "__main__":
    unittest.main()
