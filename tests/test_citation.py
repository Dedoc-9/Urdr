# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/citation.py — the DETERMINISTIC CROSS-TICK CITATION PROTOCOL (URDRCIT1):
lawful historical reuse on the byte layer. A large entity update that returns to a previously-acknowledged
value is re-expressed as a compact fixed-width CITE, reconstructing exactly the uncited baseline.
Composition over `byteacct`, NO new glyph.

  CITED == BASELINE — the headline: the client reconstructs the SAME state sequence whether the server cites
    history or always sends baselines; compression never alters semantics.
  CERTIFIED — a CITE anchor must be <= tick - ACK_LAG; the unack plant (cite tick-1) is refused.
  CLOSED-WORLD — citation history is evicted on departure; a forged CITE for a departed entity is an
    unresolvable ghost.
  CROSS-TICK RATE — a mandatory baseline within REFRESH_INTERVAL ticks; the no-baseline plant exceeds it.
  CONSTANT-SHAPE — a fixed-width CITE and every packet padded to exactly B; the shape-drift plant varies it.
  COMPRESSION IS REAL — cites are used and fewer useful bytes than the all-baseline reference.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import citation as C                                            # noqa: E402
import anamorphosis as A                                        # noqa: E402
import perception as PC                                         # noqa: E402

_CFG = (C.B_ROOMY, C.ACK_LAG, C.REFRESH_INTERVAL)


def _certified_of_mode(ticks, cl, L, mode):
    cur, hist, base = {}, {}, {}
    for t, (e, w) in enumerate(ticks):
        _m, br = C._encode(cur, hist, base, e, w, cl, L, t, _CFG, mode)
        parsed = C.parse(C.serialize(t, C.B_ROOMY, br))[2]
        if not C.verify_records(parsed, t, _CFG, hist):
            return False
        cur, hist, base = C.apply_records(cur, hist, base, parsed, t)
    return True


class TheCitedEqualsBaseline(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in C.SCENES:
            self.assertEqual(C.scene_result(name), C.golden(name), name)
            self.assertEqual(C.scene_result(name), C.scene_result(name), name)

    def test_cited_equals_baseline(self):
        ticks, cl = C._toggle()
        self.assertTrue(C.cited_equals_baseline(ticks, cl, A.lens(0, 0)),
                        "citation altered the reconstructed semantics")

    def test_compression_is_real(self):
        ticks, cl = C._toggle()
        rep = C.run(ticks, cl, A.lens(0, 0))
        base = C.run(ticks, cl, A.lens(0, 0), mode="baseline")
        self.assertGreater(rep["cites"], 0, "no citation was ever used")
        self.assertLess(rep["used_total"], base["used_total"], "citation saved no bytes")

    def test_client_reconstructs_from_the_wire(self):
        ticks, cl = C.gen_sequence(PC._LCG(C.SWEEP_SEED))
        self.assertTrue(C.is_closed_world_run(ticks, cl, A.lens(0, 0)))


class TheCertifiedLaw(unittest.TestCase):
    def test_honest_is_certified(self):
        ticks, cl = C._toggle()
        self.assertTrue(C.certified_ok(ticks, cl, A.lens(0, 0)))

    def test_unacknowledged_citation_refused(self):
        """A citation to an un-acknowledged anchor (tick-1, inside the ack-lag window) is refused — the
        protocol refuses uncertainty rather than speculating about receiver state."""
        ticks, cl = C._toggle()
        self.assertFalse(_certified_of_mode(ticks, cl, A.lens(0, 0), "unack"),
                         "an un-acknowledged citation was admitted")


class TheClosedWorldLaw(unittest.TestCase):
    def test_departure_evicts_history(self):
        cl = PC.client(0, 0, 1, 0, 1, 2, 400, 0)
        ticks = C._seq({1: [(5, t * 3, C._d(500 + t % 2)) for t in range(6)]}, 6)   # drifts off → departs
        self.assertTrue(C.is_closed_world_run(ticks, cl, A.lens(0, 0)))

    def test_historical_ghost_refused(self):
        """A citation resolving the history of an entity already removed from the manifested set is a ghost:
        the evicted history is unresolvable, and both verify and apply refuse it."""
        cur = {5: (3, 0, C._d(5))}
        hist = {5: {0: (3, 0, C._d(5))}}
        cur2, hist2, base2 = C.apply_records(cur, hist, {5: 0}, [("remove", 5, None)], 1)   # depart + evict
        self.assertNotIn(5, hist2)
        self.assertFalse(C.verify_records([("cite", 5, 0)], 2, _CFG, hist2))
        with self.assertRaises(C.CitationError):
            C.apply_records(cur2, hist2, base2, [("cite", 5, 0)], 2)


class TheRateLaw(unittest.TestCase):
    def test_honest_refreshes_within_interval(self):
        ticks, cl = C._toggle()
        self.assertTrue(C.rate_ok(C.run(ticks, cl, A.lens(0, 0))))

    def test_no_baseline_starves_freshness(self):
        """Suppressing the mandatory baseline lets a constant-cite entity go longer than REFRESH_INTERVAL
        without a baseline — the rate law catches it, while the honest encoder keeps it bounded (L15)."""
        cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
        ticks = C._seq({1: [(4, 0, C._d(999)) for _ in range(12)]}, 12)   # constant cite
        self.assertTrue(C.rate_ok(C.run(ticks, cl, A.lens(0, 0))))
        self.assertFalse(C.rate_ok(C.run(ticks, cl, A.lens(0, 0), mode="no_baseline")))


class TheConstantShapeLaw(unittest.TestCase):
    def test_honest_is_constant_shape(self):
        ticks, cl = C._toggle()
        self.assertTrue(C.constant_shape_ok(C.run(ticks, cl, A.lens(0, 0))))

    def test_cite_is_fixed_width(self):
        self.assertEqual(len(C.rec_cite(7, 0)), C.CITE_BYTES)
        self.assertEqual(len(C.rec_cite(7, 999999)), C.CITE_BYTES, "the CITE width must not vary with age")

    def test_shape_drift_plant_bites(self):
        """A variable-width (varint) anchor makes the packet size drift with citation age — the packet is no
        longer exactly B, so parse refuses it (the constant-shape law enforced on the wire)."""
        recs = [C.rec_cite(1, 5)]
        honest = C.serialize(0, C.B_ROOMY, recs)
        drift = C._serialize_shape_drift(0, C.B_ROOMY, recs)
        self.assertEqual(len(honest), C.B_ROOMY)
        self.assertNotEqual(len(drift), C.B_ROOMY, "the shape-drift packet must not be exactly B")
        with self.assertRaises(C.CitationError):
            C.parse(drift)


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = C.sweep_digest()
        self.assertEqual(d1, C.sweep_digest(), "deterministic")
        self.assertEqual(d1, C.sweep_golden(), "sweep drifted from golden")
        rep = C.sweep()
        self.assertGreater(rep["cite_seen"], 0, "citation was never exercised")
        self.assertGreater(rep["evict_seen"], 0, "baselines were never exercised")
        self.assertGreater(rep["base_seen"], 0, "the rate bound was never met")

    def test_sweep_bites_leaked_hidden(self):
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(C.CitationError):
                C.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(C.sweep_digest(), C.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
