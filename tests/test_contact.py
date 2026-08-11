# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for `contact` (URDRCON1) — ground contact as a certified state.

The useful certificate is not `grounded == True`. It is the COMPLETE CYCLE — ground -> jump ->
airborne -> fall -> ground — read as a state SEQUENCE, because a boolean at the end passes for a
run that never left the ground. Everything else here is that discipline applied to one seam at a
time: the transitions, the witness that says WHY support holds, the reserved third state nothing
can produce yet, the refusals, the exact lookup counts, and the measured disagreement between the
2D walk and this law.

Each planted defect below was run RED before its golden was pinned."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ("terrain", "physics", "netcode"):
    _p = os.path.join(_ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import contact as C                                          # noqa: E402
import heightfield as HF                                     # noqa: E402


class _Planted:
    """Swap a module attribute for the duration of a block. The plants are how a green result
    here means anything (L23): every claim below is paired with a defect proved to redden it."""

    def __init__(self, name, value):
        self.name, self.value = name, value

    def __enter__(self):
        self.old = getattr(C, self.name)
        setattr(C, self.name, self.value)
        return self

    def __exit__(self, *exc):
        setattr(C, self.name, self.old)
        return False


class TheTransitionLaws(unittest.TestCase):
    """The six the operator named, plus the cycle that subsumes them."""

    def setUp(self):
        self.f = C._demo_field()                              # flat, height 5
        self.s = C._step_field()                              # rise 2 / wall 5 / drop 11
        self.rev = "rev-0"

    def test_landing_enters_terrain_grounded(self):
        y, vy, st, w = C.step_vertical(self.f, (2, 2), 6, -4, self.rev)
        self.assertEqual(st, C.TERRAIN_GROUNDED)
        self.assertEqual((y, vy), (5, 0), "a landing must settle ON the ground with vy zeroed")
        self.assertIsNotNone(w, "a grounded actor without a witness is the bool this rung retires")

    def test_jump_exits_terrain_grounded(self):
        y, vy, st, w = C.step_vertical(self.f, (2, 2), 5, 0, self.rev, jump=4)
        self.assertEqual(st, C.AIRBORNE)
        self.assertEqual((y, vy), (9, 4))
        self.assertIsNone(w, "an airborne actor carrying a support witness is a stale support")

    def test_gravity_does_not_accumulate_while_grounded(self):
        """Ten grounded ticks in a row leave vy at zero. Were gravity integrating underneath, the
        actor would LAUNCH on the tick it stepped off a ledge — with the sign this law uses it
        would sink instead, which is worse, because it looks like terrain."""
        y, vy = 5, 0
        for _ in range(10):
            y, vy, st, _w = C.step_vertical(self.f, (2, 2), y, vy, self.rev)
            self.assertEqual((y, vy, st), (5, 0, C.TERRAIN_GROUNDED))

    def test_gravity_accumulation_would_be_caught(self):
        """RED-FIRST for the row above: a supported branch that integrated gravity anyway."""
        def leaky(heights, cell, y, vy, revision, grav=1, jump=0):
            g = C.ground_height(heights, cell)
            if y == g and jump == 0:
                return y, vy - grav, C.TERRAIN_GROUNDED, C.witness("TERRAIN", cell, revision, g)
            return real(heights, cell, y, vy, revision, grav, jump)
        real = C.step_vertical
        with _Planted("step_vertical", leaky):
            y, vy = 5, 0
            for _ in range(10):
                y, vy, _st, _w = C.step_vertical(self.f, (2, 2), y, vy, self.rev)
            self.assertNotEqual(vy, 0, "the plant did not accumulate — the test above is vacuous")

    def test_step_within_max_step_remains_grounded(self):
        out, cell, y, vy, st, w = C.step_horizontal(self.s, (1, 2), 5, self.rev, (2, 2))
        self.assertEqual((out, cell, y, vy), (C.ADMITTED, (2, 2), 7, 0))
        self.assertEqual(st, C.TERRAIN_GROUNDED)
        self.assertEqual(w[4], 7, "the witness must record the height support was found AT")

    def test_step_above_max_step_becomes_blocked_or_airborne(self):
        """A rise of 5 against MAX_STEP 2. BLOCKED, and — the half that matters — the actor is
        still where it was and still supported, not quietly nudged."""
        out, cell, y, _vy, st, _w = C.step_horizontal(self.s, (2, 2), 7, self.rev, (3, 2))
        self.assertEqual(out, C.BLOCKED)
        self.assertEqual((cell, y), ((2, 2), 7))
        self.assertEqual(st, C.TERRAIN_GROUNDED)

    def test_terrain_support_loss_enters_airborne(self):
        """Stepping off a ledge. The actor KEEPS its height and loses its witness — no snap-down,
        because teleporting it to the lower ground is the authority moving an actor with no
        record. `glide` snaps; this law does not, and `TheWalkContactSeam` measures the gap."""
        out, cell, y, _vy, st, w = C.step_horizontal(self.s, (3, 2), 12, self.rev, (4, 2))
        self.assertEqual((out, cell, y), (C.ADMITTED, (4, 2), 12))
        self.assertEqual(st, C.AIRBORNE)
        self.assertIsNone(w)

    def test_the_complete_cycle_is_the_certificate(self):
        """ground -> jump -> airborne... -> fall -> ground, read as a SEQUENCE. A final-state
        assertion would pass for a run that never left the ground; this cannot."""
        seq, y, vy = C.run_cycle(self.f, (2, 2), self.rev, jump=4, grav=1)
        self.assertEqual(seq[0], C.TERRAIN_GROUNDED)
        self.assertEqual(seq[-1], C.TERRAIN_GROUNDED)
        self.assertEqual(seq[1], C.AIRBORNE, "the jump did not leave the ground")
        self.assertEqual(set(seq), {C.TERRAIN_GROUNDED, C.AIRBORNE})
        self.assertGreater(seq.count(C.AIRBORNE), 1, "one airborne tick is a stumble, not a jump")
        self.assertEqual((y, vy), (5, 0), "the cycle must CLOSE on the ground it left")

    def test_a_grounded_actor_that_never_jumps_never_leaves(self):
        """NON-VACUITY for the cycle: with jump 0 the sequence is all-grounded, so the assertion
        that AIRBORNE appears is a real discriminator rather than a property of `run_cycle`."""
        seq, y, vy = C.run_cycle(self.f, (2, 2), self.rev, jump=0)
        self.assertEqual(set(seq), {C.TERRAIN_GROUNDED})
        self.assertEqual((y, vy), (5, 0))


class TheSupportWitness(unittest.TestCase):
    """Support records WHY, not THAT — which is what makes rollback a COMPARISON."""

    def setUp(self):
        self.f = C._demo_field()

    def test_the_witness_records_the_reason(self):
        _st, w = C.contact_of(self.f, (2, 2), 5, "rev-0")
        self.assertEqual(w, ("TERRAIN", 2, 2, "rev-0", 5))

    def test_the_witness_is_reproducible_under_replay(self):
        a = C.contact_of(self.f, (3, 1), 5, "rev-7")[1]
        b = C.contact_of(self.f, (3, 1), 5, "rev-7")[1]
        self.assertEqual(C.witness_digest(a), C.witness_digest(b))

    def test_an_edit_underneath_changes_the_witness(self):
        """`resurrect`'s stale-snapshot law arriving here for free: a terraform under a parked
        actor bumps the revision, so the witness a replay produces DIFFERS."""
        self.assertTrue(C.the_witness_binds_the_revision(self.f, (2, 2), "rev-0", "rev-1"))

    def test_a_revision_blind_witness_would_be_caught(self):
        """RED-FIRST: a witness that dropped the revision field would make the row above pass by
        being unable to fail — the exact shape L23 forbids."""
        with _Planted("witness", lambda src, cell, rev, h: (src, cell[0], cell[1], "", h)):
            self.assertFalse(C.the_witness_binds_the_revision(self.f, (2, 2), "rev-0", "rev-1"))

    def test_an_airborne_actor_has_no_witness(self):
        st, w = C.contact_of(self.f, (2, 2), 9, "rev-0")
        self.assertEqual(st, C.AIRBORNE)
        self.assertIsNone(w, "a witness in the air is a support that is not there")


class TheReservedState(unittest.TestCase):
    """GEOMETRY_SUPPORTED is declared and unproduced. The distinction is reserved so that the
    first platform does not have to un-collapse a contract."""

    def test_geometry_support_is_declared(self):
        self.assertIn(C.GEOMETRY_SUPPORTED, C.STATES)
        self.assertIn(C.GEOMETRY_SUPPORTED, C.SUPPORTED_STATES)
        self.assertNotEqual(C.SOURCES[C.GEOMETRY_SUPPORTED], C.SOURCES[C.TERRAIN_GROUNDED])

    def test_geometry_support_is_unproduced(self):
        self.assertTrue(C.geometry_support_is_unproduced(C._demo_field(), (2, 2), "rev-0"))

    def test_the_reservation_gates_nothing(self):
        """The distinction from L65's unsatisfiable law, MEASURED. `GEOMETRY_SUPPORTED` appears in
        no admission test — the vertical and horizontal laws branch on MEMBERSHIP in
        SUPPORTED_STATES, so a producer arriving later needs no edit to either. Checked by
        emptying that membership and confirming the supported branch stops running at all: were
        the code testing the NAME `TERRAIN_GROUNDED`, this would change nothing."""
        y, vy, _st, _w = C.step_vertical(C._demo_field(), (2, 2), 5, 0, "rev-0", jump=4)
        self.assertEqual((y, vy), (9, 4))
        with _Planted("SUPPORTED_STATES", ()):
            y, vy, _st, _w = C.step_vertical(C._demo_field(), (2, 2), 5, 0, "rev-0", jump=4)
            self.assertEqual((y, vy), (5, 0), "the law branches on a NAME, not on membership")
        y, vy, _st, _w = C.step_vertical(C._demo_field(), (2, 2), 5, 0, "rev-0", jump=4)
        self.assertEqual((y, vy), (9, 4), "the plant leaked past its block")


class TheRefusals(unittest.TestCase):
    """Every decision this law declines to make silently."""

    def setUp(self):
        self.f = C._demo_field()

    def _refuses(self, fn, needle):
        with self.assertRaises(C.ContactError) as ctx:
            fn()
        self.assertEqual(ctx.exception.code, "CONTACT-REFUSE")
        self.assertIn(needle, str(ctx.exception))

    def test_penetration_refuses_rather_than_clamps(self):
        self._refuses(lambda: C.contact_of(self.f, (2, 2), 3, "rev-0"), "below the ground")

    def test_an_off_field_ground_query_refuses(self):
        self._refuses(lambda: C.ground_height(self.f, (99, 2)), "outside the field")
        self._refuses(lambda: C.ground_height(self.f, (-1, 2)), "outside the field")

    def test_a_float_vertical_refuses(self):
        self._refuses(lambda: C.contact_of(self.f, (2, 2), 5.0, "rev-0"), "exact integer")
        self._refuses(lambda: C.step_vertical(self.f, (2, 2), 5, 0, "rev-0", grav=0.5),
                      "exact integer")

    def test_a_bool_is_not_an_integer_here(self):
        self._refuses(lambda: C.contact_of(self.f, (2, 2), True, "rev-0"), "exact integer")

    def test_a_non_adjacent_step_refuses(self):
        self._refuses(lambda: C.step_horizontal(self.f, (1, 1), 5, "rev-0", (5, 1)),
                      "not a single step")

    def test_an_airborne_horizontal_step_refuses(self):
        """Air control is a different law. Answering it here would give the wall a second,
        different meaning without anyone deciding to."""
        self._refuses(lambda: C.step_horizontal(self.f, (1, 1), 9, "rev-0", (2, 1)),
                      "AIRBORNE actor")

    def test_the_boundary_is_the_boundary(self):
        """NON-VACUITY: one step inside each refused edge must SUCCEED, or the refusals above are
        just a function that always raises."""
        C.contact_of(self.f, (2, 2), 5, "rev-0")
        C.ground_height(self.f, (0, 0))
        C.step_horizontal(self.f, (1, 1), 5, "rev-0", (2, 2))       # diagonal is adjacent


class TheCostDenominator(unittest.TestCase):
    """Terrain lookups as EXACT COUNTS, established BEFORE any cache is argued for. A count is not
    a cost — it is the denominator a cost claim would have to be divided by."""

    def setUp(self):
        self.f = C._demo_field()

    def test_the_counts_are_exact(self):
        self.assertTrue(C.the_lookup_counts_are_exact(self.f, (2, 2), "rev-0"))

    def test_the_vertical_tick_reads_the_terrain_once(self):
        """This was written RED and caught the first `step_vertical`, which read the same cell
        twice — once inside `contact_of` and once for the landing test. Found by counting."""
        c = C.tick_lookups(self.f, (2, 2), "rev-0")
        self.assertEqual(c["step_vertical"], 1)
        self.assertEqual(c["step_horizontal"], 2, "a step prices the cell it leaves AND the one "
                                                  "it enters — two is correct, not a defect")
        self.assertEqual(c["run_cycle"], c["run_cycle_ticks"])

    def test_a_double_read_would_be_caught(self):
        """RED-FIRST: the very defect the counter found, replanted."""
        real = C.ground_height
        with _Planted("ground_height", lambda h, cell: (real(h, cell), real(h, cell))[0]):
            self.assertFalse(C.the_lookup_counts_are_exact(self.f, (2, 2), "rev-0"))

    def test_the_counter_is_not_a_constant(self):
        c = C.tick_lookups(self.f, (2, 2), "rev-0")
        self.assertEqual(len({c["step_vertical"], c["step_horizontal"], c["run_cycle"]}), 3,
                         "three operations reporting the same count is a stuck counter")


class TheWalkContactSeam(unittest.TestCase):
    """The 2D walk and the 3D contact law disagree, and it is measured here rather than discovered
    by an actor sinking into a hillside later. `stance`/`glide` cannot fall — there is no axis to
    fall along — so downhill is instantaneous for them and a loss of support for this law."""

    def setUp(self):
        self.island = HF.generate(**HF.island())

    def test_the_admission_decisions_agree_everywhere(self):
        """`walk_contact_divergence` REFUSES if any admission differs, so reaching a result at all
        is the claim: this law restates `stance`'s wall rather than replacing it."""
        d = C.walk_contact_divergence(self.island)
        self.assertEqual(d["agree"] + d["differ_on_drop"], d["steps"])
        self.assertGreater(d["blocked_both"], 0, "a corpus with no walls tests no wall")

    def test_the_states_differ_exactly_on_the_drops(self):
        """The sharp form. A count alone would be a number; this is the characterization."""
        self.assertTrue(C.the_divergence_is_exactly_the_drops(self.island))

    def test_the_divergence_is_reported_with_its_denominator(self):
        """L44: never a bare number. 7 337 disagreements is meaningless without the 16 128."""
        d = C.walk_contact_divergence(self.island)
        self.assertEqual(d["steps"], 16128)
        self.assertGreater(d["differ_on_drop"], d["steps"] // 3)
        self.assertLess(d["differ_on_drop"], d["steps"])
        self.assertIsNotNone(d["first_drop"], "a divergence with no witness cell is not evidence")

    def test_a_flat_world_diverges_nowhere(self):
        """NON-VACUITY in the other direction: with no drops the two laws AGREE completely, so the
        divergence above is a property of terrain rather than of the comparison."""
        d = C.walk_contact_divergence(C._demo_field())
        self.assertEqual(d["differ_on_drop"], 0)
        self.assertEqual(d["agree"], d["steps"])
        self.assertFalse(C.the_divergence_is_exactly_the_drops(C._demo_field()))

    def test_a_snap_down_would_be_caught(self):
        """RED-FIRST: the obvious 'fix' — make the contact law snap to the lower ground like the
        walk does — erases the distinction this rung exists to hold, and reddens."""
        real = C.step_horizontal

        def snapping(heights, cell, y, revision, to_cell, max_step=C.MAX_STEP):
            out, c2, y2, vy, st, w = real(heights, cell, y, revision, to_cell, max_step)
            if st == C.AIRBORNE:
                g = heights[c2[1]][c2[0]]
                return out, c2, g, vy, C.TERRAIN_GROUNDED, C.witness("TERRAIN", c2, revision, g)
            return out, c2, y2, vy, st, w
        with _Planted("step_horizontal", snapping):
            self.assertFalse(C.the_divergence_is_exactly_the_drops(self.island))


class ThePinnedScenes(unittest.TestCase):
    """The four goldens, pinned AFTER every plant above was proved to bite."""

    def test_the_scenes_match_their_goldens(self):
        for name in C.SCENES:
            with self.subTest(name):
                self.assertEqual(C.scene_result(name), C.golden(name))

    def test_the_scenes_are_deterministic(self):
        self.assertEqual([C.scene_result(n) for n in C.SCENES],
                         [C.scene_result(n) for n in C.SCENES])
        self.assertEqual(C.contact_digest(), C.contact_digest())

    def test_the_payload_is_readable(self):
        """A golden nobody can read is a golden nobody checks: each scene's digest addresses a
        TEXT record, and the text is asserted to still say what the scene is about."""
        self.assertIn("AIRBORNE", C.scene_case("cycle"))
        self.assertIn("BLOCKED", C.scene_case("steps"))
        self.assertIn("step_vertical=1", C.scene_case("lookups"))
        self.assertIn("differ_on_drop=", C.scene_case("seam"))

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(C.ContactError):
            C.scene_case("nope")
        with self.assertRaises(C.ContactError):
            C.golden("nope")


if __name__ == "__main__":
    unittest.main()
