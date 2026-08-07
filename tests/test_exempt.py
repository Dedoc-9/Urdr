# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the EXEMPTION REGISTER (URDREXM1).

The register's job is to make a silently-growing exempt set finite, named, reasoned and
expiring. Every test here is written so that a register which had rotted in one of the
ways registers actually rot would fail it: an unreasoned entry, an entry for a module the
law now covers, an entry for a module that no longer exists, a class that matches nothing,
a debt list that grew, or a module covered by nothing at all.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_S = os.path.join(ROOT, "tools", "specfreeze")
if _S not in sys.path:
    sys.path.insert(0, _S)

import exempt as EX                                                       # noqa: E402


class TheRegisterIsDerivedNotDeclared(unittest.TestCase):
    def test_the_enforced_set_is_read_from_verify_not_restated(self):
        """A membership list written in two places is a list that can disagree with
        itself. The register reads `BRIEFS_REQUIRING_A_FALSIFIER` out of verify.py."""
        enf = EX.enforced()
        self.assertGreater(len(enf), 50)
        self.assertIn("voxlat", enf)
        self.assertIn("pixid", enf)
        self.assertNotIn("bench", enf)

    def test_membership_is_a_predicate_over_the_live_tree(self):
        """Classes derive membership by walking the tree, so the world can empty a class
        without anyone editing the register. Only DEBT is enumerated, deliberately."""
        live = EX.modules()
        self.assertGreater(len(live), 200)
        self.assertIn("raster3d", live)
        self.assertTrue(live["raster3d"].startswith("tools/render/"))

    def test_the_register_covers_the_module_set_exactly(self):
        """CLOSURE, as an arithmetic identity rather than a claim: enforced + classed +
        debt equals the number of modules, with nothing double-counted."""
        total, per = EX.census()
        self.assertEqual(sum(per.values()), total)
        self.assertEqual(EX.uncovered(), [])
        self.assertEqual(EX.ambiguous(), [])


class TheRegisterHolds(unittest.TestCase):
    def test_it_holds_on_the_live_tree(self):
        self.assertTrue(EX.register_holds())

    def test_every_class_has_a_reason_long_enough_to_be_a_contract(self):
        """A reason short enough to be a label is not a contract — the 40-character floor
        is lifted from `authority.every_exemption_has_a_reason`."""
        self.assertEqual(EX.unreasoned(), [])
        for e in EX.EXEMPTIONS:
            self.assertGreaterEqual(len(e.reason.strip()), EX.REASON_FLOOR, e.name)

    def test_the_register_is_non_vacuous(self):
        """L61. Closure is trivially satisfiable by a catch-all, so every class must
        cover something no other class covers, and DEBT must be non-empty."""
        self.assertTrue(EX.the_register_is_non_vacuous())
        self.assertGreater(len(EX.DEBT), 0)

    def test_debt_is_enumerated_never_predicated(self):
        """A predicated debt bucket would absorb every future module and closure would be
        satisfied forever without meaning anything."""
        self.assertIsInstance(EX.DEBT, frozenset)
        self.assertTrue(all(isinstance(m, str) for m in EX.DEBT))
        self.assertLessEqual(len(EX.DEBT), EX.DEBT_HIGH_WATER)


class TheRotIsCaught(unittest.TestCase):
    """Six plants, one per way a register actually rots."""

    def test_a_new_module_is_UNCOVERED_by_default(self):
        """THE POINT OF THE RUNG. `BRIEFS_REQUIRING_A_FALSIFIER` is opt-in, so before this
        register a new module joined the exempt set silently. Now it lands in no bucket
        and reddens, forcing its author to brief it, class it, or take on debt."""
        real = EX.modules
        EX.modules = lambda: dict(real(), brand_new_thing="tools/terrain/brand_new_thing.py")
        try:
            self.assertIn("brand_new_thing", EX.uncovered())
            self.assertFalse(EX.register_holds())
        finally:
            EX.modules = real
        self.assertTrue(EX.register_holds())

    def test_a_class_that_matches_nothing_is_UNFULFILLED(self):
        """`#[expect]` semantics: a suppression that is no longer needed must warn, not
        sit silent like `#[allow]`."""
        dead = EX.Exemption("brief", "matches-nothing",
                            "a class deliberately written to cover no module at all, so "
                            "the unfulfilled clause has something to catch.",
                            lambda m, p: False)
        real = EX.EXEMPTIONS
        EX.EXEMPTIONS = real + (dead,)
        try:
            self.assertIn("brief/matches-nothing", EX.unfulfilled())
            self.assertFalse(EX.register_holds())
        finally:
            EX.EXEMPTIONS = real
        self.assertEqual(EX.unfulfilled(), [])

    def test_an_exemption_for_a_module_the_law_now_COVERS_is_stale(self):
        """The expiry direction. `voxlat` is enforced; carrying debt for it would be an
        excuse for a law already satisfied. This is the clause that caught the register's
        own `test`-prefix predicate swallowing `testament` on its first run."""
        real = EX.DEBT
        EX.DEBT = real | {"voxlat"}
        try:
            self.assertIn("voxlat", EX.stale())
            self.assertFalse(EX.register_holds())
        finally:
            EX.DEBT = real
        self.assertEqual(EX.stale(), [])

    def test_an_exemption_for_a_module_that_no_longer_exists_is_UNKNOWN(self):
        """A rename or a deletion leaves the entry behind; nothing else would notice."""
        real = EX.DEBT
        EX.DEBT = real | {"a_module_that_was_deleted"}
        try:
            self.assertIn("a_module_that_was_deleted", EX.unknown())
            self.assertFalse(EX.register_holds())
        finally:
            EX.DEBT = real
        self.assertEqual(EX.unknown(), [])

    def test_an_unreasoned_class_reddens(self):
        real = EX.EXEMPTIONS
        victim = next(e for e in real if e._members is not None)
        EX.EXEMPTIONS = tuple(EX.Exemption(e.law, e.name, "because.", e._members)
                              if e is victim else e for e in real)
        try:
            self.assertTrue(EX.unreasoned())
            self.assertFalse(EX.register_holds())
        finally:
            EX.EXEMPTIONS = real
        self.assertEqual(EX.unreasoned(), [])

    def test_debt_that_GREW_reddens(self):
        """Shrink-only. Paying debt down is free; taking more on means editing
        DEBT_HIGH_WATER, which shows up in a diff — the only place it should show up."""
        real = EX.DEBT
        EX.DEBT = real | {"%s_pad" % i for i in range(EX.DEBT_HIGH_WATER + 1)}
        try:
            self.assertFalse(EX.debt_only_shrank())
            self.assertFalse(EX.register_holds())
        finally:
            EX.DEBT = real
        self.assertTrue(EX.debt_only_shrank())

    def test_a_module_in_two_classes_is_AMBIGUOUS(self):
        """Two reasons is no reason: a reader could not tell which contract applies."""
        dup = EX.Exemption("brief", "second-claim-on-the-scenes",
                           "a class deliberately overlapping scene-corpus so the ambiguity "
                           "clause has something to catch.",
                           lambda m, p: m in ("scenes", "scenes3d"))
        real = EX.EXEMPTIONS
        EX.EXEMPTIONS = real + (dup,)
        try:
            self.assertIn("scenes3d", EX.ambiguous())
            self.assertFalse(EX.register_holds())
        finally:
            EX.EXEMPTIONS = real
        self.assertEqual(EX.ambiguous(), [])


class TheSeedIsMeasuredNotAsserted(unittest.TestCase):
    def test_every_prose_brief_entry_really_lacks_a_marker(self):
        """The `prose-brief` class claims 16 briefs assert no falsifiable claim. Checked
        against the files rather than trusted: a marker present would mean the brief DOES
        claim a row, and the module belongs in enforcement instead."""
        live, enf = EX.modules(), EX.enforced()
        prose = [m for m, p in live.items()
                 if m not in enf and "prose-brief" in EX.classes_of(m, p)]
        self.assertGreater(len(prose), 0)
        for m in prose:
            self.assertIsNone(EX.brief_marker(m), "%s cites a row but is not enforced" % m)

    def test_every_enforced_module_really_has_a_marker(self):
        """The other direction, so the split is a partition and not a coincidence."""
        for m in sorted(EX.enforced()):
            self.assertIsNotNone(EX.brief_marker(m), "%s is enforced with no marker" % m)


class TheLawFieldIsLoadBearing(unittest.TestCase):
    """Until `authority.EXEMPT` was folded in, every entry said `law="brief"` and the
    field was decorative — a distinction that cannot vary is not a distinction (L61)."""

    def test_the_register_carries_more_than_one_law(self):
        self.assertGreaterEqual(len(EX.laws()), 2)
        self.assertIn("brief", EX.laws())
        self.assertIn("authority", EX.laws())

    def test_one_module_can_satisfy_one_law_and_be_excused_from_another(self):
        """`stormprop` is what made the field real: ENFORCED under the brief law and
        EXEMPT under the authority law. A law-blind clause reports it stale and is wrong."""
        live = EX.modules()
        self.assertIn("stormprop", EX.enforced())
        self.assertEqual(EX.classes_of("stormprop", live["stormprop"], "brief"), ())
        self.assertEqual(EX.classes_of("stormprop", live["stormprop"], "authority"),
                         ("property-falsifier",))
        self.assertEqual(EX.stale(), [])

    def test_bench_holds_two_exemptions_under_two_laws_without_being_ambiguous(self):
        """Ambiguity is two reasons for the SAME law. Two laws, two reasons is the point."""
        live = EX.modules()
        self.assertEqual(EX.classes_of("bench", live["bench"], "brief"), ("harness",))
        self.assertEqual(EX.classes_of("bench", live["bench"], "authority"),
                         ("measurement-harness",))
        self.assertEqual(EX.ambiguous(), [])

    def test_an_exemption_filed_under_the_WRONG_law_does_not_excuse(self):
        """THE PLANT. Refile the authority exemption for `bench` under the brief law and
        authority's contract must break — the reason is unchanged, only the law moved."""
        import authority as AU
        real = EX.EXEMPTIONS
        moved = tuple(EX.Exemption("brief", e.name, e.reason, names=e.names)
                      if e.law == "authority" else e for e in real)
        EX.EXEMPTIONS = moved
        try:
            self.assertEqual(EX.for_law("authority"), ())
            self.assertFalse(EX.register_holds())
        finally:
            EX.EXEMPTIONS = real
        self.assertTrue(EX.register_holds())
        self.assertTrue(AU.contract_holds())

    def test_there_is_ONE_register_not_two(self):
        """`authority.EXEMPT` is DERIVED, so a reason cannot be written twice and drift."""
        import authority as AU
        names = {n for e in EX.for_law("authority") for n in e.names}
        self.assertEqual(set(AU.EXEMPT), names)
        for e in EX.for_law("authority"):
            for n in e.names:
                self.assertIs(AU.EXEMPT[n], e.reason)

    def test_an_exemption_is_predicated_or_enumerated_never_both(self):
        with self.assertRaises(ValueError):
            EX.Exemption("brief", "both", "x" * 50, lambda m, p: True, names=("a",))
        with self.assertRaises(ValueError):
            EX.Exemption("brief", "neither", "x" * 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
