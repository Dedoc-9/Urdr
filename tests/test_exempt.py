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


class TheInvariantGeneralises(unittest.TestCase):
    """`tools/frontfps` is the authority boundary's FIRST promotion. The invariant was read
    off `tools/terrain`; this asks whether it holds unchanged somewhere it was not derived."""

    def test_frontfps_is_enforced_and_no_longer_reported(self):
        import authority as AU
        self.assertIn("tools/frontfps", AU.ENFORCED)
        self.assertNotIn("tools/frontfps", AU.REPORTED)
        self.assertGreaterEqual(len(AU.ENFORCED), 2, "one subsystem is not a generalisation")

    def test_frontend_was_EARNED_not_exempted(self):
        """The third promotion differs in kind from the second. frontfps was completed by
        DECLARING an exemption for a harness; frontend was completed by FIXING a module —
        `rigidity_verdict` gained the content address it was missing, which closed a stale
        certificate. No new exemption was spent on it."""
        import authority as AU
        self.assertIn("tools/frontend", AU.ENFORCED)
        self.assertNotIn("tools/frontend", AU.REPORTED)
        for r in AU.census("tools/frontend"):
            self.assertTrue(AU.satisfies(r), "%s is exempt-free and must satisfy" % r[0])
            self.assertNotIn(r[0], AU.EXEMPT)

    def test_both_enforced_subsystems_have_the_same_shape(self):
        """terrain: 101 AUTHORITY + 3 exempt PURE. frontfps: 6 AUTHORITY + 1 exempt PURE.
        Same shape, different subsystem — which is what generalising means here. Terrain moved
        102/2 -> 101/3 when the predicates were corrected to read code instead of docstrings:
        `commuteprop` joined the property-falsifier class, which already existed."""
        import authority as AU
        for sub in AU.ENFORCED:
            rows = AU.census(sub)
            self.assertTrue(rows, sub)
            for r in rows:
                self.assertTrue(AU.satisfies(r) or r[0] in AU.EXEMPT,
                                "%s/%s neither satisfies nor is exempt" % (sub, r[0]))

    def test_the_contract_holds_over_both(self):
        import authority as AU
        self.assertTrue(AU.contract_holds())
        self.assertEqual(AU.violations(), [])
        self.assertEqual(AU.stale_exemptions(), [])
        self.assertEqual(AU.unknown_exemptions(), [])

    def test_frontbench_really_is_PURE_measured_not_assumed(self):
        """The exemption claims it admits no state and issues no verdict. Checked against
        the census rather than trusted: neither half of the invariant is present."""
        import authority as AU
        row = next(r for r in AU.census("tools/frontfps") if r[0] == "frontbench")
        self.assertFalse(row[1], "frontbench has a typed refusal; the exemption is wrong")
        self.assertFalse(row[2], "frontbench has a content address; the exemption is wrong")
        self.assertEqual(AU.classify(row), "PURE")

    def test_the_exemption_is_LOAD_BEARING(self):
        """THE PLANT. The promotion is not free: withdraw frontbench's exemption and the
        subsystem must go into violation. If it did not, the exemption was decoration."""
        import authority as AU
        real = EX.EXEMPTIONS
        EX.EXEMPTIONS = tuple(EX.Exemption(e.law, e.name, e.reason,
                                           names=tuple(n for n in e.names if n != "frontbench"))
                              if e.names else e for e in real)
        try:
            import importlib
            importlib.reload(AU)
            self.assertIn("frontbench", [v[1] for v in AU.violations()],
                          "withdrawing the exemption did not put frontfps in violation")
            self.assertFalse(AU.contract_holds())
        finally:
            EX.EXEMPTIONS = real
            importlib.reload(AU)
        self.assertTrue(AU.contract_holds())

    def test_one_reason_is_shared_never_copied(self):
        """`bench` and `frontbench` cite the SAME string object, not two copies that can
        drift — the register's whole purpose, exercised for the first time."""
        import authority as AU
        self.assertIn("bench", AU.EXEMPT)
        self.assertIn("frontbench", AU.EXEMPT)
        self.assertIs(AU.EXEMPT["bench"], AU.EXEMPT["frontbench"])


class ThePredicatesReadCodeNotProse(unittest.TestCase):
    """The census was matching the RAW FILE TEXT, so a module was certified by the words
    `REFUSE` and `digest` appearing anywhere in it — including in prose about what it does
    NOT do. That is `claim != code` inside the checker that enforces `claim != code`."""

    def test_prose_cannot_talk_a_module_into_passing(self):
        import authority as AU
        self.assertTrue(AU.reads_code_not_prose())
        self.assertFalse(AU.has_typed_refusal(
            '"""Admission failures raise A-REFUSE."""\ndef admit(x):\n    return int(x)\n'))
        self.assertFalse(AU.has_typed_refusal(
            "def admit(x):\n    return int(x)  # raise A-REFUSE on bad input\n"))
        self.assertFalse(AU.has_content_address(
            '"""Identity is the sha256 digest of the canonical bytes."""\ndef n(x):\n    return x\n'))

    def test_a_hash_in_a_string_survives_comment_stripping(self):
        """The reason comments come out through the TOKENIZER and not a regex: `#` inside a
        string literal is not a comment, and cutting the line there would silently change what
        the predicate sees."""
        import authority as AU
        self.assertTrue(AU.has_content_address(
            "import hashlib\ndef tag(x):\n    return '#' + hashlib.sha256(x).hexdigest()\n"))

    def test_the_inherited_route_requires_the_RAISE_not_the_import(self):
        """`govern` really does refuse — `raise _OC.OpcostError(...)`, a typed class defined in
        `opcost`. The old predicate knew this by reading the COMMENT that said so. Crediting the
        import alone would make the route a free pass every module could take (L61)."""
        import authority as AU
        local = {"opcost": True, "prettyprint": False}
        self.assertTrue(AU.inherited_refusal(
            "import opcost as _OC\ndef a(x):\n    raise _OC.OpcostError('over')\n", local))
        self.assertTrue(AU.inherited_refusal(
            "from opcost import OpcostError\ndef a(x):\n    raise OpcostError('over')\n", local))
        self.assertFalse(AU.inherited_refusal(
            "import opcost as _OC\ndef c(x):\n    return _OC.cost(x)\n", local))
        self.assertFalse(AU.inherited_refusal(
            "import prettyprint as _PP\ndef a(x):\n    raise _PP.PrettyError('b')\n", local))
        for m in ("govern", "priogov"):
            self.assertEqual(AU.refusal_route(m), "inherited:opcost", m)

    def test_the_correction_changed_real_verdicts_on_the_live_tree(self):
        """Non-vacuity against the tree, not the mechanism: if stripping prose demoted nobody,
        `code_only` would be decoration. Every demoted module inside an ENFORCED subsystem must
        be declared exempt — otherwise the correction left a hole rather than closing one."""
        import authority as AU
        carried = AU.prose_carried()
        self.assertGreater(len(carried), 0, "the strip demoted nothing — it is decoration")
        names = {m for _s, m, _p, _c in carried}
        self.assertIn("observe", names, "observe was content-addressed on the WORD 'digest'")
        self.assertIn("renderbound", names)
        for sub, m, _prose, _code in carried:
            if sub in AU.ENFORCED:
                self.assertIn(m, AU.EXEMPT, "%s/%s was demoted and left undeclared" % (sub, m))


class TheExemptionsWrittenBeforeThePromotion(unittest.TestCase):
    """`lockstep` and `regionprop` are in `tools/netcode`, which is REPORTED. Their reasons are
    written NOW so that if the subsystem is ever promoted, the excuse is one that already existed
    rather than one invented to make the promotion land."""

    def test_the_property_falsifier_class_grew_without_a_new_reason(self):
        """Three modules, ONE reason object. `commuteprop` and `regionprop` joined the class
        `stormprop` defined — the register did not gain an excuse, the tree filled one."""
        import authority as AU
        entry = next(e for e in EX.for_law("authority") if e.name == "property-falsifier")
        self.assertEqual(entry.names, ("stormprop", "commuteprop", "regionprop"))
        for n in entry.names:
            self.assertIs(AU.EXEMPT[n], entry.reason)

    def test_lockstep_is_no_longer_exempt_because_the_reason_EXPIRED(self):
        """THE REGISTER WORKING, NOT FAILING. The exemption said a refusal inside `canon`
        would change the frozen contract, so the boundary belonged to lockstep's callers.
        True of `canon` and FALSE of the SPINE: a door in front of `simulate` leaves
        `canon`, `_digest`, `trace_digest` and the tick's absorbing `if` untouched. The
        reason expired, so the entry went — which is the `#[expect]` semantics the whole
        register is built on, exercised for the first time on an entry of its own."""
        import authority as AU
        self.assertNotIn("lockstep", AU.EXEMPT)
        self.assertEqual([e.name for e in EX.for_law("authority")
                          if "lockstep" in e.names], [])
        row = next(r for r in AU.census("tools/netcode") if r[0] == "lockstep")
        self.assertTrue(r_ok := AU.satisfies(row), "lockstep does not satisfy; the "
                        "exemption was removed too early")
        self.assertEqual(AU.classify(row), "AUTHORITY")
        self.assertTrue(r_ok)

    def test_netcode_is_NOT_promoted_and_observe_is_exactly_why(self):
        """THE PROMOTION THAT DID NOT HAPPEN, recorded so it cannot be quietly forgotten.
        `observe` now refuses (typed OBSERVE-REFUSE) but mints no identity, so it is
        GUARDED-COMPUTATION — a read-only diagnostic. Giving it a digest purely to clear the
        census is the gaming the register already refused for `frontbench`."""
        import authority as AU
        self.assertNotIn("tools/netcode", AU.ENFORCED)
        self.assertIn("tools/netcode", AU.REPORTED)
        row = next(r for r in AU.census("tools/netcode") if r[0] == "observe")
        self.assertTrue(row[1], "observe gained no typed refusal")
        self.assertFalse(row[2], "observe minted an identity it does not need")
        self.assertEqual(AU.classify(row), "GUARDED-COMPUTATION")

    def test_the_pre_registered_exemptions_WOULD_bite(self):
        """THE PLANT for a promotion that has not happened. Enforce `tools/netcode` for the
        length of this test: the violation set must be exactly `observe`, and withdrawing
        `lockstep`'s exemption must add it. A pre-registered reason that would not bite on
        promotion is decoration written early."""
        import authority as AU
        real_enf, real_ex = AU.ENFORCED, AU.EXEMPT
        try:
            AU.ENFORCED = real_enf + ("tools/netcode",)
            AU.reset_caches()
            self.assertEqual([v[1] for v in AU.violations()], ["observe"])
            AU.EXEMPT = {k: v for k, v in real_ex.items() if k != "regionprop"}
            self.assertIn("regionprop", [v[1] for v in AU.violations()],
                          "withdrawing regionprop's exemption did not put netcode in violation")
        finally:
            AU.ENFORCED, AU.EXEMPT = real_enf, real_ex
            AU.reset_caches()
        self.assertTrue(AU.contract_holds())


if __name__ == "__main__":
    unittest.main(verbosity=2)
