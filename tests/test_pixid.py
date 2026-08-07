# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for `pixid` (URDRPID1) — the primitive-ID buffer.

Every test asserts the apparatus. The refusal tests are the plants — a buffer that admits
everything cites nothing — and the firewall tests are stated in BOTH directions, because
a `scene_digest` that ignored the scene would satisfy the interesting half perfectly.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_R = os.path.join(ROOT, "tools", "render")
if _R not in sys.path:
    sys.path.insert(0, _R)

import pixid as PX                                                        # noqa: E402
from raster import SUB, RenderError                                       # noqa: E402


class OwnershipIsAFunctionOfTheSet(unittest.TestCase):
    def test_permutation_invariance_on_the_pinned_scene(self):
        self.assertTrue(PX.digest_is_permutation_invariant())

    def test_permutation_invariance_survives_an_added_exact_tie(self):
        """The hard case: two primitives at the SAME depth covering the same pixels. The
        tie-break key is the written `(instance, primitive)` datum, so the winner does
        not depend on which arrived first."""
        tied = PX.SCENE + (PX._t(2, 2, 9, 2, 2, 9, (4, 4, 4), 2, 5),)
        self.assertTrue(PX.digest_is_permutation_invariant(tied))
        self.assertTrue(PX.digest_is_permutation_invariant(tuple(reversed(tied))))

    def test_a_tie_goes_to_the_smaller_id_pair(self):
        """Direction pinned by reading the OWNED PIXEL, not a digest: a digest says the
        frame changed, never who won."""
        lo = PX._t(2, 2, 9, 2, 2, 9, (4, 4, 4), 1, 0)
        hi = PX._t(2, 2, 9, 2, 2, 9, (4, 4, 4), 8, 0)
        fb = PX.IdFramebuffer(*PX.VIEW).render([hi, lo])
        self.assertEqual(fb.owner(4, 4), (1, 0))
        fb2 = PX.IdFramebuffer(*PX.VIEW).render([lo, hi])
        self.assertEqual(fb2.owner(4, 4), (1, 0))

    def test_the_buffer_is_not_empty(self):
        """L61: every invariance law above holds trivially of a buffer that emits
        nothing."""
        fb = PX.IdFramebuffer(*PX.VIEW).render(PX.SCENE)
        self.assertGreater(sum(1 for v in fb.iid if v != PX.EMPTY), 0)
        self.assertEqual(fb.oob, 0)


class AgainstTheOracle(unittest.TestCase):
    def test_agreement_is_bidirectional_over_the_pinned_view(self):
        """The oracle scans ALL primitives against ALL pixels with NO bounding box — the
        traversal the rasterizer does not use, which is where `voxin`'s 20% under-report
        lived. Both directions: no covered pixel empty, no emitted id that misses."""
        self.assertTrue(PX.agrees_with_oracle())

    def test_agreement_holds_on_a_second_scene(self):
        """One scene proves nothing (L20)."""
        other = (PX._t(0, 0, 15, 0, 0, 15, (3, 3, 3), 1, 0),
                 PX._t(15, 15, 0, 15, 15, 0, (2, 2, 2), 2, 0))
        self.assertTrue(PX.agrees_with_oracle(other))

    def test_a_dropped_pixel_is_caught(self):
        """THE PLANT. A traversal that misses a cell must fail agreement; if it did not,
        the oracle would be comparing the rasterizer against itself."""
        real = PX.IdFramebuffer.draw

        def lazy(self, primitive):                     # shrink the box by one column
            p = PX._check_primitive(primitive)
            (v0, v1, v2, zs, iid, pid) = p
            shifted = ((v0[0] + SUB, v0[1]), v1, v2, zs, iid, pid)
            return real(self, shifted)

        PX.IdFramebuffer.draw = lazy
        try:
            self.assertFalse(PX.agrees_with_oracle())
        finally:
            PX.IdFramebuffer.draw = real
        self.assertTrue(PX.agrees_with_oracle())


class OcclusionOnlyRemoves(unittest.TestCase):
    def test_visible_instances_are_a_subset_of_submitted(self):
        self.assertTrue(PX.occlusion_only_removes())

    def test_the_subset_is_proper_on_the_pinned_scene(self):
        """NON-VACUITY: subset-of holds trivially when nothing is ever hidden. Instance
        9 sits entirely behind instance 7 and must vanish from the buffer while staying
        in the submitted set."""
        self.assertTrue(PX.the_subset_is_proper())
        fb = PX.IdFramebuffer(*PX.VIEW).render(PX.SCENE)
        self.assertEqual(fb.instances(), frozenset({3, 7}))
        self.assertEqual(frozenset(p[4] for p in PX.SCENE), frozenset({3, 7, 9}))

    def test_removing_the_occluder_reveals_the_hidden_instance(self):
        """The other direction — instance 9 is hidden, not absent."""
        without = tuple(p for p in PX.SCENE if p[4] != 7)
        self.assertIn(9, PX.IdFramebuffer(*PX.VIEW).render(without).instances())


class TheFirewall(unittest.TestCase):
    def test_view_knobs_move_the_frame_and_not_the_citation(self):
        self.assertTrue(PX.knobs_do_not_reach_the_citation())

    def test_every_knob_actually_moves_the_frame(self):
        """An inert knob satisfies the 'citation unchanged' half for free. This caught
        the module's own first fixture: zfar=50 and zfar=10 change nothing on a scene
        whose depths are 4, 9 and 12 with instance 9 already hidden."""
        self.assertEqual(PX.every_knob_is_live(), (True,) * len(PX.KNOBS))

    def test_one_moved_scene_integer_moves_BOTH_digests(self):
        """Without this a `scene_digest` returning a constant would pass the firewall
        perfectly. The firewall is only meaningful if the citation reads the scene."""
        self.assertTrue(PX.the_scene_reaches_the_citation())

    def test_the_citation_is_order_invariant(self):
        """A scene is its MULTISET of primitives; the citation must not encode the order
        the caller happened to submit them in."""
        s = PX.scene_digest(PX.SCENE)
        for i in range(len(PX.SCENE)):
            self.assertEqual(PX.scene_digest(PX.SCENE[i:] + PX.SCENE[:i]), s)

    def test_the_firewall_is_STRUCTURAL_not_behavioural(self):
        """WHERE THE GUARANTEE ACTUALLY LIVES. A plant that mixed a view constant into
        `scene_digest` left every behavioural firewall test green — correctly, because
        the citation still did not VARY with the view. It cannot: the view is not in its
        signature. That is the sealed-observer discipline (enforce structurally, never by
        comment), so it is asserted on the syntax rather than on the output. Adding a
        parameter to `scene_digest`, or handing it anything but the primitives, reddens
        here — which no behavioural check can do."""
        import ast
        tree = ast.parse(open(PX.__file__, "r", encoding="utf-8").read())
        fn = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "scene_digest")
        self.assertEqual([a.arg for a in fn.args.args], ["primitives"])
        self.assertEqual(fn.args.defaults, [])
        self.assertEqual(fn.args.kwonlyargs, [])
        self.assertIsNone(fn.args.vararg)
        self.assertIsNone(fn.args.kwarg)
        # and the witness hands it the primitives alone — never a view integer
        wit = next(n for n in tree.body
                   if isinstance(n, ast.FunctionDef) and n.name == "witness")
        calls = [c for c in ast.walk(wit) if isinstance(c, ast.Call)
                 and isinstance(c.func, ast.Name) and c.func.id == "scene_digest"]
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(calls[0].args), 1)
        self.assertIsInstance(calls[0].args[0], ast.Name)
        self.assertEqual(calls[0].args[0].id, "primitives")
        self.assertEqual(calls[0].keywords, [])

    def test_the_citation_distinguishes_ids_not_just_geometry(self):
        """Same triangles, different instance: a citation blind to the ids would let two
        different scenes share a digest."""
        a = (PX._t(1, 1, 5, 1, 1, 5, (3, 3, 3), 1, 0),)
        b = (PX._t(1, 1, 5, 1, 1, 5, (3, 3, 3), 2, 0),)
        self.assertNotEqual(PX.scene_digest(a), PX.scene_digest(b))


class TheDoorIsTyped(unittest.TestCase):
    def test_three_refusals(self):
        self.assertTrue(PX.the_door_closes())

    def test_the_empty_sentinel_may_not_be_an_id(self):
        """If EMPTY were an admissible id, an occupied pixel and an empty one would
        serialize identically and the buffer could not say what it does not know."""
        with self.assertRaises(RenderError) as ctx:
            PX.scene_digest([PX._t(0, 0, 2, 0, 0, 2, (1, 1, 1), PX.EMPTY, 0)])
        self.assertEqual(ctx.exception.code, "PIXID-REFUSE")
        for bad in (-1, PX.EMPTY + 1, 1 << 40):
            with self.assertRaises(RenderError):
                PX.scene_digest([PX._t(0, 0, 2, 0, 0, 2, (1, 1, 1), bad, 0)])

    def test_the_largest_admissible_id_is_admitted(self):
        """A boundary, not a wall one short of one."""
        self.assertEqual(len(PX.scene_digest([PX._t(0, 0, 2, 0, 0, 2, (1, 1, 1),
                                                    PX.ID_MAX, PX.ID_MAX)])), 64)

    def test_floats_are_refused_never_rounded(self):
        for bad in (((0, 0), (2.0, 0), (0, 2), (1, 1, 1), 0, 0),
                    ((0, 0), (2, 0), (0, 2), (1.0, 1, 1), 0, 0)):
            with self.assertRaises(RenderError):
                PX.scene_digest([bad])

    def test_malformed_primitives_are_typed_refusals(self):
        for bad in ("nope", (1, 2, 3), ((0, 0), (2, 0), (0, 2), (1, 1), 0, 0),
                    ((0, 0), (2, 0), (0, 2, 5), (1, 1, 1), 0, 0)):
            with self.assertRaises(RenderError):
                PX.scene_digest([bad])

    def test_the_i64_bound_is_read_from_renderbound_not_restated(self):
        """A bound written in two places is a bound that can disagree with itself. This
        buffer runs rung 2's depth arithmetic and inherits rung 2's envelope."""
        with self.assertRaises(RenderError) as ctx:
            PX.IdFramebuffer(4096, 2, 0, 1 << 40)
        self.assertEqual(ctx.exception.code, "PIXID-REFUSE")
        import renderbound as RB
        self.assertFalse(RB.admits(4096, 2, 0, 1 << 40))
        self.assertTrue(RB.admits(*PX.VIEW))


class TheBufferIsDeterministic(unittest.TestCase):
    def test_the_digests_are_stable_across_calls(self):
        first = PX.witness(PX.SCENE, *PX.VIEW)
        for _ in range(3):
            again = PX.witness(PX.SCENE, *PX.VIEW)
            self.assertEqual(again["scene"], first["scene"])
            self.assertEqual(again["frame"], first["frame"])

    def test_the_serialization_is_the_only_identity(self):
        fb = PX.IdFramebuffer(*PX.VIEW).render(PX.SCENE)
        self.assertTrue(fb.serialize().startswith(PX.MAGIC))
        self.assertEqual(len(fb.serialize()), len(PX.MAGIC) + 8 + 16 * 16 * 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
