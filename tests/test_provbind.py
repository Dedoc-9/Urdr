# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/provbind.py — BOUND ADMISSIBILITY (URDRPRV1), slice S3.

  THE LIFT ATTACK — a detachable certificate travels between blocks. MEASURED succeeding against the
    metadata-only plant and failing against the bound digest.
  THE LOOKUP IS UNSTABLE — a serve-time lookup gives different verdicts for the same block, which
    refutes the "decidable at serve time, no external lookup" claim the design made about itself.
  THREE REFUSAL CLASSES — UNBOUND is integrity, CONSENT is absolute, JURISDICTION is a property of
    the REQUEST. All reachable; none share a counter.

Every test can go red (L5); both plants bite before any golden pins (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import provbind as PV                                              # noqa: E402


class TheBinding(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in PV.SCENES:
            self.assertEqual(PV.scene_result(n), PV.golden(n), n)
            self.assertEqual(PV.scene_result(n), PV.scene_result(n), n)

    def test_binding_defeats_the_lift(self):
        """Stated so it can be false: the lift must SUCCEED against the plant AND fail against the
        law. Requiring only the second half would pass vacuously for any digest whatsoever."""
        self.assertTrue(PV.binding_defeats_the_lift())

    def test_the_plant_admits_the_stolen_certificate(self):
        """L15 — the handed-down form hashes only metadata, so the certificate travels."""
        matches, verdict = PV.lift_attack(_digest=PV._digest_metadata_only)
        self.assertTrue(matches, "the metadata-only digest matches a different block's geometry")
        self.assertEqual(verdict, PV.R_ADMIT, "and therefore admits the lie")

    def test_the_law_refuses_it(self):
        matches, verdict = PV.lift_attack()
        self.assertFalse(matches)
        self.assertEqual(verdict, PV.R_UNBOUND)
        self.assertEqual(PV._REASON_NAME[PV.R_UNBOUND], "PROVBIND-UNBOUND")

    def test_binding_commits_to_every_field(self):
        """Changing any carried field must change the commitment — including the buffer, which is
        what makes capture-time evaluation meaningful."""
        lat = PV.lattices()["block_a"]
        base = PV.corpus()["public_domain"]
        b = PV.bound_digest(base, lat)
        for i, alt in ((0, "FR"), (1, "k12_school"), (2, "ODbL"), (3, 5), (4, False)):
            c = list(base); c[i] = alt
            self.assertNotEqual(PV.bound_digest(tuple(c), lat), b, f"field {PV._FIELDS[i]}")


class TheLookup(unittest.TestCase):
    def test_serve_time_lookup_is_unstable(self):
        """The design claimed 'decidable at serve time, no external lookup' and then looked up. The
        carried-field path gives one verdict across serves; the lookup path does not."""
        self.assertTrue(PV.live_lookup_is_unstable())

    def test_carried_fields_are_stable(self):
        cert, lat = PV.corpus()["public_domain"], PV.lattices()["block_a"]
        b = PV.bound_digest(cert, lat)
        self.assertEqual(len({PV.adjudicate(cert, lat, b, "US") for _ in range(8)}), 1)


class TheRefusalClasses(unittest.TestCase):
    def test_all_three_are_reachable_and_distinct(self):
        """A class no input can produce is decoration; a shared counter conflates an integrity event
        with a lawful geography."""
        self.assertTrue(PV.classes_are_distinct())
        self.assertEqual(len({PV.R_ADMIT, PV.R_UNBOUND, PV.R_CONSENT, PV.R_JURISDICTION}), 4)

    def test_consent_is_absolute_and_jurisdiction_is_not(self):
        """CONSENT refuses everywhere; JURISDICTION is a property of the REQUEST, so the same block
        legitimately admits for one viewer and refuses for another."""
        lat = PV.lattices()["block_a"]
        res = PV.corpus()["residence"]
        bres = PV.bound_digest(res, lat)
        for region in ("US", "FR", "XX"):
            self.assertEqual(PV.adjudicate(res, lat, bres, region), PV.R_CONSENT, region)
        pub = PV.corpus()["public_domain"]
        bpub = PV.bound_digest(pub, lat)
        self.assertEqual(PV.adjudicate(pub, lat, bpub, "US"), PV.R_ADMIT)
        self.assertEqual(PV.adjudicate(pub, lat, bpub, "FR"), PV.R_JURISDICTION)

    def test_unknown_region_refuses_rather_than_defaults_open(self):
        lat = PV.lattices()["block_a"]
        pub = PV.corpus()["public_domain"]
        self.assertEqual(PV.adjudicate(pub, lat, PV.bound_digest(pub, lat), "XX"),
                         PV.R_JURISDICTION, "an unlisted region must not default to permitted")


class TheGuards(unittest.TestCase):
    def test_rejects_malformed_certificates(self):
        for bad in (("", "public_space", "PD", 50, True), ("US", "", "PD", 50, True),
                    ("US", "public_space", "PD", -1, True), ("US", "public_space", "PD", 1.0, True),
                    ("US", "public_space", "PD", 50, 1)):
            with self.assertRaises(PV.ProvbindError):
                PV.certificate(*bad)

    def test_rejects_a_malformed_lattice_digest(self):
        cert = PV.corpus()["public_domain"]
        for bad in ("", "abc", 7, "z" * 63):
            with self.assertRaises(PV.ProvbindError):
                PV.bound_digest(cert, bad)

    def test_corpus_and_lattices_are_pinned(self):
        self.assertEqual(PV.corpus(), PV.corpus())
        self.assertEqual(PV.lattices(), PV.lattices())


if __name__ == "__main__":
    unittest.main()
