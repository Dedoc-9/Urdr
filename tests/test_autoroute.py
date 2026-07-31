# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/autoroute.py — DECIDE AT THE CHEAPEST LEVEL (URDRAUT1).

  THE MENGER SCREEN CANNOT PRECEDE THE PAYLOAD — the divergence is a function of the peer's CELL SET
    and the certificate carries no cells, so the saving is FLOOD FILLS (2 against 7), never bytes.
  MY OWN FIRST CORRECTION WAS WRONG — k(subregion) <= k(occupancy) always, 160 tested, 0 violations,
    so the subregion is CONSERVATIVE not unsound. What it costs is the whole saving: 0 of 5 peers
    screened against 5 of 5.
  THE LAW GENERALIZES from wall cells to the whole lattice, additions included, 2144 tried, 0 flips.
  THE SCREEN IS VACUOUS ON A BREACHED BASE — 0 of 6 against 5 of 6 — and that is exactly where one
    cell does flip the verdict, so the router recomputes rather than reporting 0 over an empty set.
  THE CHAIN OVER-FETCHES ON ONE ROW AND MY ENUMERATION INVENTED A SECOND — a family built to separate
    3 chain pairs cannot settle a lattice of 12 covering pairs.
  PEER-FAULT NEEDS A CLAIMED VERDICT to fire at all, and then costs 0 fills against 1.

Every test can go red (L5); the plants bite before any golden pins (L15)."""
import inspect
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import autoroute as AR                                              # noqa: E402
import cohort as CO                                                 # noqa: E402


class TheRouteIsMeasuredNotTabulated(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for n in AR.SCENES:
            self.assertEqual(AR.scene_result(n), AR.golden(n), n)
            self.assertEqual(AR.scene_result(n), AR.scene_result(n), n)
        self.assertTrue(AR.emitted_matches_pinned())

    def test_the_route_census(self):
        self.assertEqual(AR.route_census(), (
            ("exclusion_membership", ("own_cert",), "CERT", ()),
            ("prefix_disjointness", ("own_cert",), "CERT", ()),
            ("liveness_horizon", ("own_cert",), "CERT", ()),
            ("occupancy_defect", ("own_tile",), "LATTICE", ("own_cert",)),
            ("ledger_remainder", ("own_log",), "HISTORY", ("own_cert", "own_tile")),
            ("quorum_agreement", ("own_tile", "peer_tiles"), "COHORT",
             ("own_cert", "own_log")),
        ))

    def test_routing_changes_inputs_never_the_answer(self):
        """The one property a router must not break, asserted rather than promised."""
        rows, bad = AR.routing_agrees_with_cohort()
        self.assertEqual(bad, 0)
        self.assertEqual(len(rows), 3)
        for _label, a, b in rows:
            self.assertEqual(a, b)

    def test_an_unknown_fetch_atom_refuses(self):
        s = AR._IS.family()[0]
        with self.assertRaises(AR.RouteError):
            AR._subproj(("own_galaxy",), s)

    def test_a_missing_golden_refuses(self):
        with self.assertRaises(AR.RouteError):
            AR.golden("no_such_scene")


class TheScreenIsPostPayload(unittest.TestCase):
    def test_the_certificate_carries_no_cells(self):
        """cohort's refutation (3) restated: no digest of a lattice can stand in for the lattice."""
        fields, has_cells, needs = AR.subgap_needs_the_payload()
        self.assertEqual(fields, ("tile_prefix", "jurisdiction_region", "liveness_token"))
        self.assertFalse(has_cells, "the divergence cannot be computed from the certificate")
        self.assertTrue(needs)

    def test_the_saving_is_fills_and_the_byte_saving_is_zero(self):
        with_s, without, peers, screened = AR.flood_fill_census()
        self.assertEqual((with_s, without, peers, screened), (2, 7, 6, 5))
        self.assertLess(with_s, without, "the screen does save work")
        self.assertEqual(AR.the_screen_saves_fills_not_bytes(), (5, 0),
                         "and it saves exactly zero bytes, which is the correction")

    def test_the_bytes_move_either_way(self):
        """Structural: `fetched` increments before any screening decision."""
        src = inspect.getsource(AR.verify_routed)
        fetched_at = src.index("fetched += 1")
        screen_at = src.index("len(mine ^ p[\"occupancy\"]) < k")
        self.assertLess(fetched_at, screen_at, "the payload is charged for before the screen runs")


class MyOwnCorrectionWasWrong(unittest.TestCase):
    def test_the_subregion_is_conservative_not_unsound(self):
        """The first draft of this module claimed a soundness defect. There is none."""
        tested, viol, strict = AR.subregion_k_is_conservative_not_unsound()
        self.assertEqual((tested, viol), (160, 0), "k(subregion) <= k(occupancy) always")
        self.assertGreater(tested, 0, "an empty sweep would pass vacuously")
        self.assertGreater(strict, 0, "and the two numbers do genuinely come apart")
        self.assertEqual(strict, 67)

    def test_but_the_subregion_costs_the_whole_saving(self):
        ks, ko, strictly, at_sub, at_occ = AR.the_subregion_costs_the_whole_saving()
        self.assertEqual((ks, ko), (1, 2))
        self.assertTrue(strictly)
        self.assertEqual((at_sub, at_occ), (0, 5),
                         "at the smaller k the sub-gap range is empty and nothing is screened")

    def test_the_sweep_uses_no_stdlib_rng(self):
        """`random.sample`'s internals are not a cross-version contract, and this repo's determinism
        claim crosses Python minor versions."""
        for fn in (AR._sweep_corpus, AR.subregion_k_is_conservative_not_unsound,
                   AR.screening_law_generalizes, AR.flood_fill_census):
            src = inspect.getsource(fn)
            self.assertNotIn("random", src, fn.__name__)
        self.assertNotIn("import random", inspect.getsource(AR).split('"""', 2)[2])


class TheLawGeneralizes(unittest.TestCase):
    def test_whole_lattice_perturbations_below_k_never_flip(self):
        bases, tested, flips = AR.screening_law_generalizes()
        self.assertEqual((bases, tested, flips), (2, 2144, 0))
        self.assertGreater(bases, 0)
        self.assertGreater(tested, 0, "an empty census would pass vacuously")
        self.assertEqual(flips, 0)

    def test_the_census_actually_contains_additions(self):
        """Otherwise it is cohort's wall-cell census wearing a larger name."""
        adds, removes = AR.the_law_covers_additions()
        self.assertEqual((adds, removes), (1056, 3104))
        self.assertGreater(adds, 0, "additions are what the generalization adds")
        self.assertGreater(removes, 0)


class TheScreenIsVacuousWhenBreached(unittest.TestCase):
    def test_a_breached_base_screens_nothing(self):
        bd, bt, idc, it, kb, ki = AR.screen_is_vacuous_when_breached()
        self.assertEqual((bd, bt), (0, 6), "k=0 leaves the sub-gap range empty")
        self.assertEqual((idc, it), (5, 6), "where an INTACT base screens five of six")
        self.assertEqual((kb, ki), (0, 2))
        self.assertLess(bd, idc)

    def test_and_that_is_where_one_cell_matters(self):
        """The vacuity is not benign — it abandons exactly the regime with the smallest margin."""
        tested, flips = AR.a_breached_verdict_flips_at_one_cell()
        self.assertEqual((tested, flips), (64, 4))
        self.assertGreater(flips, 0, "a single cell does flip a breached verdict")

    def test_the_router_recomputes_instead_of_screening(self):
        mine = frozenset()
        out = AR.verify_routed(mine, CO.peer_population(), 20)
        _o, _a, fetched, _r, screened, recomputed = out
        self.assertEqual(screened, 0, "nothing is screened on a breached base")
        self.assertEqual(recomputed, fetched, "every peer is recomputed instead")


class TheLatticeEnumerationOverreached(unittest.TestCase):
    def test_the_chain_is_not_tight(self):
        off, total = AR.the_chain_is_not_tight()
        self.assertEqual((off, total), (4, 6))
        self.assertGreater(off, 0, "else the lattice adds nothing and this module is pointless")

    def test_both_real_savings_hold_by_witness_and_by_syntax(self):
        self.assertEqual(AR.the_real_savings(), (
            ("occupancy_defect", "own_cert"),
            ("ledger_remainder", "own_cert"), ("ledger_remainder", "own_tile"),
            ("quorum_agreement", "own_cert"), ("quorum_agreement", "own_log")))
        for name, atom in AR.the_real_savings():
            self.assertTrue(AR.syntactically_independent(name, atom), (name, atom))

    def test_the_other_saving_was_an_artifact(self):
        """L19/L24 — a positive determination result is only as strong as the family's separating
        power, and this one nearly shipped a fetch reduction that does not exist."""
        said, cert_same, coh_same, occ_same, va, vb, refuted = \
            AR.the_lattice_enumeration_overreached()
        # Was (("peer_tiles",),) — a SINGLE-atom overreach. With `_subproj` honouring `own_cert` the
        # enumeration names two two-atom sets: {own_tile, peer_tiles} is genuinely minimal, while
        # {own_cert, peer_tiles} is still an overreach for the original reason — the certificate does
        # not carry the occupancy, and the witness below proves it.
        self.assertEqual(said, (("own_cert", "peer_tiles"), ("own_tile", "peer_tiles")))
        # `cert_same` is a REAL check again. It was established by `_subproj((), a) == _subproj((), b)`,
        # which only compared certificates BECAUSE of the defect; once the empty projection became
        # genuinely empty it compared two empty tuples and could not fail. Fixing the defect made this
        # premise vacuous before anyone noticed, which is its own small lesson about repairs.
        self.assertTrue(cert_same, "identical certificate")
        self.assertTrue(coh_same, "identical cohort")
        self.assertFalse(occ_same, "different occupancy")
        self.assertEqual((va, vb), (1, 0), "and different agreement")
        self.assertTrue(refuted)

    def test_the_family_was_built_for_a_chain(self):
        chain_pairs, nodes, covers = AR.the_family_was_built_for_a_chain()
        self.assertEqual((chain_pairs, nodes, covers), (3, 16, 32))
        self.assertGreater(covers, chain_pairs,
                           "a family separating a chain cannot settle a lattice")

    def test_the_adopted_route_drops_only_two_route_agreements(self):
        """The discipline: an atom leaves a fetch plan only where search AND syntax agree."""
        adopted = set(AR.the_real_savings())
        for name, plan, tier, dropped in AR.route_census():
            self.assertEqual(frozenset(plan) | frozenset(dropped), AR.CHAIN_SET[tier])
            for atom in dropped:
                self.assertIn((name, atom), adopted)


class OnlySyntaxGivesAUniversalPositive(unittest.TestCase):
    def test_the_search_alone_would_over_skip(self):
        """Nash-Segoufin-Vianu determinacy is UNDECIDABLE for UCQs, so a search positive is forever
        family-relative. Measured: it drops an atom the quantity provably reads."""
        search_only, both, over = AR.search_alone_would_over_skip()
        self.assertEqual(len(search_only), 7)
        self.assertEqual(len(both), 5)
        # Was 1, then 4, now 2. The 4 was an ARTIFACT: `_subproj` stapled a certificate derived from
        # the occupancy onto every projection and never consulted `own_cert`, so the empty projection
        # carried the very field `exclusion_membership` returns. Two of the four were that bug. The
        # two that remain are honest — `liveness_horizon` is CONSTANT across all 54 family members,
        # so projecting onto nothing really does determine it.
        self.assertEqual(over, (("liveness_horizon", "own_cert"),
                                ("quorum_agreement", "own_tile")))

    def test_the_scorecard(self):
        s_pos, y_pos, silent = AR.only_syntax_gives_a_universal_positive()
        self.assertEqual((s_pos, y_pos, silent), (7, 5, 2))
        self.assertLess(y_pos, s_pos, "syntax is sound and weaker — that is the trade")
        self.assertGreater(silent, 0, "and it is silent where a cert already exposes the input")

    def test_the_census_rows(self):
        self.assertEqual(AR.syntax_versus_search_census(), (
            ("exclusion_membership", "own_cert", False, False),
            ("prefix_disjointness", "own_cert", False, False),
            ("liveness_horizon", "own_cert", True, False),
            ("occupancy_defect", "own_cert", True, True),
            ("occupancy_defect", "own_tile", False, False),
            ("ledger_remainder", "own_cert", True, True),
            ("ledger_remainder", "own_log", False, False),
            ("ledger_remainder", "own_tile", True, True),
            ("quorum_agreement", "own_cert", True, True),
            ("quorum_agreement", "own_log", True, True),
            ("quorum_agreement", "own_tile", True, False),
            ("quorum_agreement", "peer_tiles", False, False),
        ))

    def test_the_syntactic_checker_follows_calls(self):
        """L23 applied to this module's own checker — a check whose failure mode has never been
        observed is a hypothesis."""
        shallow_clears, deep_catches = AR.the_syntactic_check_follows_calls()
        self.assertTrue(shallow_clears, "a scan that does not follow calls misses the helper")
        self.assertTrue(deep_catches, "and one that does, catches it")

    def test_the_digests_do_not_depend_on_the_invocation(self):
        """A first draft filtered call-following on `__module__`, which is '__main__' when the module
        is run as a script — so the verdict changed with how it was invoked."""
        import subprocess
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env = dict(os.environ, PYTHONHASHSEED="0", PYTHONUTF8="1")
        out = subprocess.run([sys.executable, os.path.join(root, "tools", "terrain", "autoroute.py"),
                              "--emit"], capture_output=True, text=True, env=env, check=True)
        self.assertEqual(tuple(out.stdout.strip().split("\n")), AR.conformance_lines())

    def test_an_unknown_atom_refuses_in_the_syntactic_route_too(self):
        with self.assertRaises(AR.RouteError):
            AR.syntactically_independent("ledger_remainder", "own_galaxy")


class PeerFaultNeedsAClaim(unittest.TestCase):
    def test_it_cannot_fire_in_cohort_as_built(self):
        """cohort recomputes both verdicts, so sub-gap disagreement is a property of the FUNCTION and
        a detector for it would be a test that our own arithmetic works."""
        recomputes, has_claim = AR.fault_needs_a_claimed_verdict()
        self.assertTrue(recomputes, "both verdicts are recomputed locally")
        self.assertFalse(has_claim, "and no peer record carries a claimed verdict")

    def test_the_lie_is_caught_by_a_count(self):
        raised, fills_on_peer, recompute_fills = AR.fault_is_caught_by_a_count()
        self.assertTrue(raised)
        self.assertEqual(fills_on_peer, 0, "zero flood fills on the peer's lattice")
        self.assertLess(fills_on_peer, recompute_fills)

    def test_an_honest_claim_is_accepted(self):
        """Validity-not-outcome: a detector that rejects the honest claim is not a detector."""
        ok, outcome = AR.an_honest_claim_is_not_a_fault()
        self.assertTrue(ok, "no fault is raised on a truthful claim")
        self.assertEqual(outcome, CO.UNAVAILABLE, "one agreeing peer is coverage, not integrity")

    def test_the_fault_is_a_distinct_code(self):
        fault, refuse, subclass = AR.fault_is_a_distinct_code()
        self.assertEqual(fault, "AUTOROUTE-PEERFAULT")
        self.assertEqual(refuse, "AUTOROUTE-REFUSE")
        self.assertFalse(subclass, "a proven Byzantine peer is not a malformed request")

    def test_a_threshold_below_one_refuses(self):
        with self.assertRaises(AR.RouteError):
            AR.verify_routed(CO.submitter(), CO.peer_population(), 20, min_peers=0)


class ThePlanIsEnforcedNotMerelyComputed(unittest.TestCase):
    def test_the_unguarded_evaluation_is_silently_wrong(self):
        """Why this exists: an under-populated situation yields a confident number, and it is wrong in
        the DANGEROUS direction — the full shard budget, i.e. 'the ledger is pristine'."""
        with_log, without, budget, dangerous = AR.unguarded_evaluation_is_silently_wrong()
        self.assertEqual((with_log, without), (2, 6))
        self.assertEqual(without, budget)
        self.assertTrue(dangerous)

    def test_the_representation_had_to_change(self):
        """A check could not have fixed this: `history=()` was BOTH fetched-and-empty and
        never-fetched, so the type could not express the distinction the gate needs."""
        old_equal, new_distinct = AR.the_representation_conflated_absent_and_empty()
        self.assertTrue(old_equal, "inputset.situation conflates absent with empty")
        self.assertTrue(new_distinct, "fetched_situation separates them")

    def test_the_right_answer_and_the_wrong_one_are_the_same_number(self):
        """The sharpest form, and the reason no value-level check could have caught it."""
        refused, on_empty, on_full = AR.the_guard_refuses_absence_and_admits_emptiness()
        self.assertTrue(refused, "an absent log refuses")
        self.assertEqual(on_empty, 6, "an EMPTY log honestly evaluates to the full budget")
        self.assertEqual(on_full, 2)
        _wl, fabricated, _b, _d = AR.unguarded_evaluation_is_silently_wrong()
        self.assertEqual(fabricated, on_empty,
                         "the fabricated answer equals the honest one — only the type separates them")

    def test_the_guard_census(self):
        self.assertEqual(AR.guard_census(), (
            ("exclusion_membership", ("own_cert",), True, True, True),
            ("prefix_disjointness", ("own_cert",), True, True, True),
            ("liveness_horizon", ("own_cert",), True, True, True),
            ("occupancy_defect", ("own_tile",), True, True, True),
            ("ledger_remainder", ("own_log",), True, True, True),
            ("quorum_agreement", ("own_tile", "peer_tiles"), True, True, True),
        ))
        for _n, plan, refused, evaluated, unchanged in AR.guard_census():
            if plan:
                self.assertTrue(refused, "a missing atom must refuse")
            self.assertTrue(evaluated, "an empty atom must evaluate")
            self.assertTrue(unchanged, "the guard changes inputs required, never the answer")

    def test_the_cert_hole_is_closed(self):
        """WAS `test_the_cert_hole_is_asserted_not_hidden`, and the rename is the result. Half the
        census used to test nothing, because the three CERT rows had an EMPTY plan and the guard had
        nothing to check. The certificate is a designated atom now, so every row is exercised."""
        cert, real, total = AR.cert_rows_are_not_exercised_by_this_gate()
        self.assertEqual((cert, real, total), (0, 6, 6))
        self.assertEqual(cert, 0, "an unexercised row is a row whose plan forgot what it reads")
        self.assertEqual(real, total, "every row must now be exercised, not merely most")

    def test_projection_and_checking_now_agree_and_that_costs_a_witness(self):
        """THE ASSERTION THAT USED TO LIVE HERE WAS `assertLess(p, g)`, AND THE FIX INVALIDATED IT.
        Projection admitted strictly fewer than checking ONLY because of the ambient-reader defect;
        with the certificate designated, both admit 6 of 6 and the inequality is false.

        Re-pinning (6, 6, 6) and deleting the inequality would leave a test that cannot distinguish
        'the defect is fixed' from 'projection stopped projecting'. So the inequality moves to where
        it is still true — a PLANTED ambient reader — and this test asserts the corpus agreement and
        the plant together. The property was never 'p < g on this corpus'; it was 'projection refuses
        what checking admits, whenever such a thing exists'."""
        g, p, total = AR.projection_is_stricter_than_checking()
        self.assertEqual((g, p, total), (6, 6, 6))
        caught, planted, clean = AR.the_detector_still_catches_an_ambient_reader()
        self.assertEqual((caught, planted, clean), ("planted_ambient", 1, 0))
        self.assertGreater(planted, clean,
                           "projection must still refuse what checking admits, or it is checking "
                           "with extra steps after all")

    def test_there_are_no_ambient_readers_left(self):
        """It named `exclusion_membership` and `prefix_disjointness`; it names nobody now. An empty
        result from a detector is worth exactly as much as the detector's ability to be non-empty, so
        the control is asserted in the same test rather than in a neighbouring one that could be
        deleted separately (L23)."""
        names, ambient, total = AR.the_ambient_readers()
        self.assertEqual(names, ())
        self.assertEqual((ambient, total), (0, 6))
        self.assertEqual(AR.the_detector_still_catches_an_ambient_reader()[1], 1,
                         "the detector must still find a planted ambient reader, or this zero "
                         "means nothing at all")

    def test_the_projection_census(self):
        self.assertEqual(AR.projection_census(), (
            ("exclusion_membership", ("own_cert",), True, 1),
            ("prefix_disjointness", ("own_cert",), True, True),
            ("liveness_horizon", ("own_cert",), True, True),
            ("occupancy_defect", ("own_tile",), True, 1),
            ("ledger_remainder", ("own_log",), True, 2),
            ("quorum_agreement", ("own_tile", "peer_tiles"), True, 1),
        ))

    def test_the_quantity_follows_the_certificate_not_the_occupancy(self):
        """The rewiring changed no value, which is what makes it safe and equally what makes it
        invisible: two functions agreeing on every input in the corpus is L23's shape and could just
        as well mean the edit never took. Force them apart — hold the occupancy FIXED and forge the
        certificate's region — and the quantity must follow the certificate."""
        honest, forged, differ, followed = \
            AR.the_quantity_follows_the_certificate_not_the_occupancy()
        self.assertEqual((honest, forged), (1, 1001))
        self.assertTrue(differ, "same occupancy, different certificate, same answer => still reading "
                                "the occupancy")
        self.assertTrue(followed, "the value must be the CERTIFICATE's region, not occupancy's")

    def test_an_absent_certificate_refuses(self):
        """A peer who sent no certificate is an ordinary protocol event that was INEXPRESSIBLE before
        the certificate became an atom, because `proj` manufactured one from occupancy. Three typed
        refusals — an exception is not a refusal."""
        codes = AR.an_absent_certificate_refuses()
        self.assertEqual(codes, ("AUTOROUTE-MISSING-ATOM",) * 3)
        for c in codes:
            self.assertFalse(c.startswith("UNTYPED"), "a crash is not a refusal")

    def test_the_sentinel_refuses_typed_rather_than_crashing(self):
        """Inert, it died as a TypeError from inside tilemin — untyped, naming neither atom nor
        caller, indistinguishable from a genuine bug."""
        self.assertEqual(AR.the_sentinel_refuses_typed_not_crashes(),
                         ("AUTOROUTE-MISSING-ATOM",) * 4)

    def test_identity_still_works_on_the_sentinel(self):
        """Validity-not-outcome: the gate must ASK whether an atom is the sentinel without triggering
        the refusal it is asking about."""
        self.assertEqual(AR.identity_still_works_on_the_sentinel(), (True, True, True))

    def test_missing_atom_is_a_distinct_code(self):
        missing, refuse, subclass = AR.missing_atom_is_a_distinct_code()
        self.assertEqual(missing, "AUTOROUTE-MISSING-ATOM")
        self.assertEqual(refuse, "AUTOROUTE-REFUSE")
        self.assertFalse(subclass, "under-populated is not malformed")

    def test_an_unknown_quantity_or_atom_refuses(self):
        s = AR.fetched_situation({(33, 33, 33)}, 6, (), ())
        with self.assertRaises(AR.RouteError):
            AR.guarded("no_such_quantity", s)
        with self.assertRaises(AR.RouteError):
            AR.atom_is_present(s, "own_galaxy")


class TheInvariants(unittest.TestCase):
    """Stated so they could be checked against a DIFFERENT implementation of this module."""

    def test_provenance(self):
        """No fetched state is representable as NOT_FETCHED, and NOT_FETCHED is never produced by a
        successful fetch."""
        values, collisions, built, produced = AR.provenance_invariant()
        self.assertEqual(collisions, 0, "no legitimate value identifies or compares as the sentinel")
        self.assertEqual(produced, 0, "a successful build never yields the sentinel")
        self.assertGreater(values, 0)
        self.assertGreater(built, 0, "an empty sweep would pass vacuously")

    def test_guard_transparency(self):
        """For any fully populated input, guarded and unguarded evaluation agree."""
        pairs, bad = AR.guard_transparency_invariant()
        self.assertEqual(bad, 0)
        self.assertEqual(pairs, 24, "quantified over a family, not one fixture")

    def test_error_partition(self):
        """Missing-input and policy-refusal errors are disjoint and exhaust all router failures.
        THIS is the invariant that would have caught the inert sentinel: an undesignated read escaped
        as a TypeError from inside tilemin, which is neither class."""
        att, missing, refuse, escaped, disjoint, succeeded = AR.error_partition_invariant()
        self.assertTrue(disjoint, "neither refusal class subclasses the other")
        self.assertEqual(escaped, 0, "no third exception type escapes")
        self.assertGreater(missing, 0, "the missing-input arm is exercised")
        self.assertGreater(refuse, 0, "and so is the policy-refusal arm")
        self.assertEqual(att, missing + refuse + escaped + succeeded)

    def test_all_three_hold(self):
        self.assertEqual(AR.the_invariants(),
                         (("provenance", True), ("guard-transparency", True),
                          ("error-partition", True)))


if __name__ == "__main__":
    unittest.main()
