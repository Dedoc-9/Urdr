# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""session (URDRSES1) — membership is a property of the event, not of the room."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "netcode"))
sys.path.insert(0, os.path.join(_ROOT, "tools", "physics"))

import authinput as A                                            # noqa: E402
import session as SE                                             # noqa: E402
import worldpeer as WP                                           # noqa: E402
import worldstep as WS                                           # noqa: E402
from rollback import RollbackError                               # noqa: E402


class TheCalendar(unittest.TestCase):
    def test_membership_is_half_open_at_both_ends(self):
        """Off-by-one lives at boundaries, so both ends are asserted rather than one."""
        for peer, join, leave in SE.CALENDAR:
            with self.subTest(peer=peer):
                self.assertTrue(SE.member_at(SE.CALENDAR, peer, join))
                self.assertTrue(SE.member_at(SE.CALENDAR, peer, leave - 1))
                self.assertFalse(SE.member_at(SE.CALENDAR, peer, leave))
                if join:
                    self.assertFalse(SE.member_at(SE.CALENDAR, peer, join - 1))

    def test_membership_reads_the_tick_and_nothing_else(self):
        """The law's signature cannot receive a session, so it cannot consult one."""
        import inspect
        args = inspect.signature(SE.member_at).parameters
        self.assertEqual(tuple(args), ("calendar", "peer", "tick"))

    def test_a_peer_outside_the_calendar_is_never_a_member(self):
        for t in (0, 8, 64, 119):
            self.assertFalse(SE.member_at(SE.CALENDAR, 9, t))

    def test_the_corpus_carries_a_join_a_departure_and_a_permanent_member(self):
        joins = [j for _p, j, _l in SE.CALENDAR if j > 0]
        leaves = [lv for _p, _j, lv in SE.CALENDAR if lv < 120]
        self.assertEqual(len(joins), 2)
        self.assertEqual(len(leaves), 1)
        self.assertIn((0, 0, 120), SE.CALENDAR)

    def test_every_in_window_event_is_in_window_and_every_other_is_not(self):
        for e in SE.IN_WINDOW:
            with self.subTest(event=e):
                self.assertTrue(SE.member_at(SE.CALENDAR, e[1], e[0]))
        for e in SE.OUT_OF_WINDOW:
            with self.subTest(event=e):
                self.assertFalse(SE.member_at(SE.CALENDAR, e[1], e[0]))

    def test_identities_are_unique_so_the_one_time_signature_stays_one_time(self):
        idents = [(e[1], e[2]) for e in SE.EVENTS]
        self.assertEqual(len(idents), len(set(idents)))


class TheConvergenceLaw(unittest.TestCase):
    def test_every_schedule_lands_on_one_chain(self):
        distinct, equals_oracle, rollbacks, refusals = SE.the_convergence_law()
        self.assertEqual(distinct, 1)
        self.assertTrue(equals_oracle)
        self.assertEqual(refusals, 0)
        self.assertGreater(rollbacks, 0)

    def test_the_oracle_is_independent_of_the_session(self):
        """`worldstep.simulate` in batch, on a log filtered by nothing but the calendar. It is an
        oracle only because it cannot see the machinery it adjudicates."""
        import inspect
        src = inspect.getsource(WS.simulate) + inspect.getsource(WS.simulate_trace)
        self.assertNotIn("session", src)
        self.assertNotIn("calendar", src)
        self.assertNotIn("member", src)

    def test_the_oracle_reproduces_the_live_run(self):
        self.assertEqual(SE.run("departed")[0], SE.oracle_trace())

    def test_the_schedules_really_do_differ(self):
        """A convergence law over schedules that agree step for step proves nothing."""
        self.assertEqual(len({SE.SCHEDULES[n] for n in SE.IN_HORIZON}), 4)
        rolls = {SE.run(n)[2] for n in SE.IN_HORIZON}
        self.assertIn(0, rolls, "no schedule takes the no-rollback path")
        self.assertTrue([r for r in rolls if r > 0], "no schedule rolls back at all")

    def test_every_schedule_delivers_the_same_envelopes(self):
        for name in SE.SCHEDULES:
            with self.subTest(schedule=name):
                delivered = sorted(a for k, a in SE.SCHEDULES[name] if k == "deliver")
                self.assertEqual(delivered, sorted(range(len(SE.IN_WINDOW))))

    def test_the_run_is_deterministic(self):
        self.assertEqual(SE.run("interleaved")[0], SE.run("interleaved")[0])


class TheSharpCase(unittest.TestCase):
    def test_the_corpus_actually_contains_departed_peer_deliveries(self):
        """NON-VACUITY: a law about departed peers proved on a corpus with none is a law about
        nothing."""
        census = dict(SE.the_departed_peer_census())
        self.assertEqual(sum(census[n] for n in SE.IN_HORIZON), 5)
        self.assertGreater(census["departed"], 0)
        self.assertEqual(census["ordered"], 0, "the control schedule should have none")

    def test_a_departed_peers_in_window_event_is_still_admitted(self):
        keys, roster = SE.keys_and_roster()
        w = WS.arena_world()
        s = SE.Session(w, roster, WP.world_pin(w), SE.CALENDAR)
        s.advance(84)                                            # peer 1 left at 64
        e = (60, 1, 2, 1, 4, 0)
        self.assertIn(e, SE.IN_WINDOW)
        out = s.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
        self.assertEqual(out[0], "rolled")

    def test_the_same_peers_out_of_window_event_is_not(self):
        keys, roster = SE.keys_and_roster()
        w = WS.arena_world()
        s = SE.Session(w, roster, WP.world_pin(w), SE.CALENDAR)
        s.advance(84)
        e = (70, 1, 4, 1, 5, 0)
        self.assertIn(e, SE.OUT_OF_WINDOW)
        with self.assertRaises(SE.SessionError):
            s.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))


class TheDefects(unittest.TestCase):
    def test_head_time_membership_breaks_convergence(self):
        distinct, equals_oracle, _codes = SE.the_head_time_defect()
        self.assertGreater(distinct, 1)
        self.assertFalse(equals_oracle)

    def test_roster_eviction_breaks_convergence(self):
        distinct, equals_oracle, _codes = SE.the_eviction_defect()
        self.assertGreater(distinct, 1)
        self.assertFalse(equals_oracle)

    def test_the_two_defects_reach_the_same_wrong_world(self):
        schedules, equal, differ, silent = \
            SE.the_two_defects_agree_on_the_world_and_differ_on_the_reason()
        self.assertEqual(equal, schedules)
        self.assertEqual(differ + silent, schedules)
        self.assertGreater(differ, 0)

    def test_only_the_typed_refusal_tells_them_apart(self):
        _d, _e, head = SE.the_head_time_defect()
        _d2, _e2, evict = SE.the_eviction_defect()
        self.assertNotEqual(head, evict)
        for (_n, codes) in head:
            self.assertTrue(set(codes) <= {"SESSION-REFUSE"})
        for (_n, codes) in evict:
            self.assertTrue(set(codes) <= {"AUTH-REFUSE"})

    def test_the_defect_is_not_a_strawman(self):
        law, defect, equal = SE.the_defect_differs_by_one_expression()
        self.assertTrue(equal)
        self.assertNotEqual(law, defect)
        self.assertIn("self._gate", law)
        self.assertIn("self._gate", defect)

    def test_the_gate_only_adds_a_precondition(self):
        self.assertTrue(SE.the_gate_only_adds_a_precondition())

    def test_the_subject_is_untouched(self):
        self.assertTrue(SE.the_subject_is_untouched())
        self.assertTrue(issubclass(SE.Session, WP.WorldPeer))
        self.assertIs(SE.Session.deliver_envelope, WP.WorldPeer.deliver_envelope)


class TheRefusals(unittest.TestCase):
    def test_every_out_of_window_event_refuses_whenever_it_arrives(self):
        total, refused, codes = SE.the_membership_refusals()
        self.assertEqual(refused, total)
        self.assertEqual(codes, ("SESSION-REFUSE",))

    def test_the_three_refusals_are_distinct_and_each_reachable(self):
        """AUTH-REFUSE, SESSION-REFUSE and ROLLBACK-REFUSE answer three different questions, and no
        one of them can stand in for another."""
        keys, roster = SE.keys_and_roster()
        w = WS.arena_world()
        pin = WP.world_pin(w)
        seen = set()
        s = SE.Session(WS.arena_world(), roster, pin, SE.CALENDAR)
        with self.assertRaises(A.AuthError) as cm:
            s.deliver_envelope(A.envelope((5, 7, 0, 0, 1, 0),
                                          A.keygen(A.fixture_seed(7, 0))))
        seen.add(cm.exception.code)
        s = SE.Session(WS.arena_world(), roster, pin, SE.CALENDAR)
        e = SE.OUT_OF_WINDOW[1]
        with self.assertRaises(SE.SessionError) as cm:
            s.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
        seen.add(cm.exception.code)
        s = SE.Session(WS.arena_world(), roster, pin, SE.CALENDAR)
        s.advance(119)
        e = SE.IN_WINDOW[0]
        with self.assertRaises(RollbackError) as cm:
            s.deliver_envelope(A.envelope(e, keys[(e[1], e[2])]))
        seen.add(cm.exception.code)
        self.assertEqual(seen, {"AUTH-REFUSE", "SESSION-REFUSE", "ROLLBACK-REFUSE"})

    def test_the_typed_refusal_lives_in_code_and_not_in_prose(self):
        """`authority` reads `code_only`, so a code that lives only in a docstring is not a code."""
        import inspect
        self.assertIn("SESSION-REFUSE", inspect.getsource(SE.SessionError.__init__))
        self.assertEqual(SE.SessionError("x").code, "SESSION-REFUSE")

    def test_an_unknown_schedule_refuses(self):
        with self.assertRaises(SE.SessionError):
            SE.run("wishful")

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(SE.SessionError):
            SE.scene_result("wishful")

    def test_an_unknown_golden_refuses(self):
        with self.assertRaises(SE.SessionError):
            SE.golden("wishful")

    def test_a_mismatched_world_pin_refuses_before_any_tick(self):
        _keys, roster = SE.keys_and_roster()
        with self.assertRaises(WS.WorldError):
            SE.Session(WS.arena_world(), roster, "0" * 64, SE.CALENDAR)


class TheSegmentationLaw(unittest.TestCase):
    def test_no_cut_of_any_schedule_diverges(self):
        law = SE.the_segmentation_law()
        self.assertEqual(len(law), len(SE.IN_HORIZON))
        for name, bad, cuts in law:
            with self.subTest(schedule=name):
                self.assertEqual(bad, 0)
                self.assertGreater(cuts, 0)

    def test_the_sweep_covers_every_step(self):
        law = dict((n, (b, c)) for n, b, c in SE.the_segmentation_law())
        for name in SE.IN_HORIZON:
            self.assertEqual(law[name][1], len(SE.SCHEDULES[name]) - 1)


class ThePlants(unittest.TestCase):
    def test_every_plant_bites(self):
        for name, bad, cuts in SE.the_plants():
            with self.subTest(plant=name):
                self.assertGreater(bad, 0, f"{name} never bit")
                self.assertEqual(cuts, 53)

    def test_the_unerasable_perturbation_bites_everywhere(self):
        """If a plant that damages every copy of the state does NOT diverge at every cut, the
        comparison is not comparing what it claims to."""
        plants = dict((n, (b, c)) for n, b, c in SE.the_plants())
        self.assertEqual(plants["perturb_all"], (53, 53))

    def test_the_live_only_perturbation_is_erased_by_rollback(self):
        """Weaker than `perturb_all` BY MECHANISM rather than by accident: a rollback restores from
        a retained snapshot the plant never touched."""
        plants = dict((n, (b, c)) for n, b, c in SE.the_plants())
        self.assertLess(plants["perturb_live"][0], plants["perturb_all"][0])
        self.assertGreater(plants["perturb_live"][0], 0)

    def test_no_two_plants_report_the_same_exposure(self):
        counts = [b for _n, b, _c in SE.the_plants()]
        self.assertEqual(len(counts), len(set(counts)))

    def test_the_admitted_set_is_load_bearing_in_both_directions(self):
        qb, qt, ab, at = SE.the_admitted_set_is_load_bearing_in_both_directions()
        self.assertEqual(qb, qt, "a queued admitted event must always be lost")
        self.assertGreater(qt, 0)
        self.assertGreater(ab, 0, "the replay direction never bit")
        self.assertLess(ab, at, "the replay direction is contingent, not certain")

    def test_the_two_directions_partition_the_sweep(self):
        qb, qt, ab, at = SE.the_admitted_set_is_load_bearing_in_both_directions()
        plants = dict((n, (b, c)) for n, b, c in SE.the_plants())
        self.assertEqual(qt + at, plants["drop_known"][1])
        self.assertEqual(qb + ab, plants["drop_known"][0])


class TheStatePopulation(unittest.TestCase):
    def test_the_population_is_closed(self):
        closed, size, undeclared, invented = SE.the_state_population_is_closed()
        self.assertTrue(closed, f"undeclared={undeclared} invented={invented}")
        self.assertEqual(undeclared, ())
        self.assertEqual(invented, ())
        self.assertGreater(size, 0)

    def test_the_population_is_derived_and_not_a_list(self):
        """It is read from the AST of two `__init__` bodies, so a field added to either and to
        neither tuple reddens without anyone editing a list."""
        self.assertEqual(set(SE.state_population()),
                         set(SE.RESUMABLE) | set(SE.CONFIGURATION))
        self.assertTrue(set(SE.state_population()) >= {"pos", "vel", "known"})

    def test_it_reaches_across_the_inheritance_seam(self):
        base = set(SE._init_targets(WP.WorldPeer))
        own = set(SE._init_targets(SE.Session))
        self.assertTrue(base - own, "the base class contributes nothing — the walk is not reaching")
        self.assertTrue(own - base, "the subclass contributes nothing — the walk is not reaching")

    def test_the_naive_walk_would_miss_the_fields_the_law_is_about(self):
        only, all_in, state_fields = \
            SE.the_walk_would_miss_the_fields_the_law_is_about()
        self.assertTrue(state_fields, "pos and vel are not tuple-only — the trap is not live")
        self.assertTrue(all_in)
        self.assertIn("pos", only)
        self.assertIn("vel", only)

    def test_every_configuration_exemption_carries_a_reason(self):
        for name, why in SE.CONFIGURATION.items():
            with self.subTest(field=name):
                self.assertTrue(why.strip())
                self.assertGreater(len(why), 20)

    def test_resumable_and_configuration_are_disjoint(self):
        self.assertFalse(set(SE.RESUMABLE) & set(SE.CONFIGURATION))

    def test_dropping_a_resumable_field_is_what_the_plants_measure(self):
        self.assertIn("known", SE.RESUMABLE)
        self.assertIn("pos", SE.RESUMABLE)


class TheHorizon(unittest.TestCase):
    def test_the_scope_boundary_is_exhibited_rather_than_hidden(self):
        admitted, refused, codes, differs = \
            SE.the_horizon_bounds_the_convergence_claim()
        self.assertGreater(refused, 0)
        self.assertEqual(codes, ("ROLLBACK-REFUSE",))
        self.assertTrue(differs)
        self.assertGreater(admitted, refused)

    def test_the_refused_events_are_admitted_by_every_in_horizon_schedule(self):
        """The witness pair: the SAME event, admitted under one schedule and ROLLBACK-REFUSED under
        another, which is what makes the composed sentence conditional."""
        _tr, ref, _rb, _q = SE.run("past_horizon")
        refused = {i for i, _c in ref}
        self.assertTrue(refused)
        for name in SE.IN_HORIZON:
            with self.subTest(schedule=name):
                self.assertEqual(SE.run(name)[1], ())

    def test_past_horizon_is_excluded_from_the_law_on_purpose(self):
        self.assertIn("past_horizon", SE.SCHEDULES)
        self.assertNotIn("past_horizon", SE.IN_HORIZON)


class TheRecord(unittest.TestCase):
    def test_the_scenes_match_their_goldens(self):
        for n in SE.SCENES:
            with self.subTest(scene=n):
                self.assertEqual(SE.scene_result(n), SE.golden(n))

    def test_the_emitted_corpus_is_the_pinned_one(self):
        self.assertTrue(SE.emitted_matches_pinned())

    def test_no_wall_clock_enters(self):
        self.assertTrue(SE.no_wall_clock_enters_this_rung())

    def test_the_memo_cannot_change_an_answer(self):
        """A cache over a pure sweep changes how often, never what."""
        first = SE.the_plants()
        SE._MEMO.clear()
        self.assertEqual(SE.the_plants(), first)


if __name__ == "__main__":
    unittest.main(verbosity=2)
