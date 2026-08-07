# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Red-first falsifiers for the JOINED WITNESS (URDRJOIN1) — the granularity seal.

The happy join and the forged-witness case ship as `pixid-view-join` /
`pixid-view-join-forgery` and are NOT restated here. What this suite adds is the one thing
those could not express: a MINTED record, and a verifier whose verdict says which LEVEL it
checked, so a world-level agreement can never silently stand in for a pixel-level one.
"""
import ast
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(ROOT, "tools", "render"), os.path.join(ROOT, "tools", "terrain")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pixid_join as PJ                                                   # noqa: E402
import view_witness as VW                                                 # noqa: E402
from raster import RenderError                                            # noqa: E402


class TheRecordIsMinted(unittest.TestCase):
    def test_the_record_is_recomputable_from_shipped_code(self):
        """The acceptance condition: a holder can rebuild it byte-for-byte. No clock, no
        randomness, no hidden state — mint twice and every field agrees."""
        a, b = PJ.joined_witness(), PJ.joined_witness()
        self.assertEqual(a, b)
        self.assertEqual(len(a["digest"]), 64)
        self.assertEqual(a["digest"], PJ.join_digest(a))

    def test_the_honest_record_verifies_at_both_levels(self):
        self.assertEqual(PJ.verify_joined(PJ.joined_witness()),
                         (PJ.WORLD_OK, PJ.PIXEL_OK))

    def test_the_digest_commits_to_every_field(self):
        """A digest decided by the world alone would let two different renders of the same
        world share one identity — the widening this rung exists to prevent."""
        self.assertTrue(PJ.the_record_commits_to_both_levels())

    def test_a_malformed_record_is_a_typed_refusal_not_a_mismatch(self):
        """'This record is wrong' and 'this is not a record' are different facts. A join
        that returned MISMATCH for both would report a forgery where there was a typo."""
        self.assertTrue(PJ.a_malformed_record_is_refused())
        with self.assertRaises(RenderError) as ctx:
            PJ.verify_joined({**PJ.joined_witness(), "digest": "0" * 64})
        self.assertEqual(ctx.exception.code, "JOIN-REFUSE")


class TheGranularityIsSealed(unittest.TestCase):
    def test_granularity_is_sealed(self):
        """FALSIFIER 3. Both halves independently reachable, in both directions."""
        pixel_forged, world_forged, honest = PJ.granularity_is_sealed()
        self.assertEqual(pixel_forged, (PJ.WORLD_OK, PJ.PIXEL_BAD))
        self.assertEqual(world_forged, (PJ.WORLD_BAD, PJ.PIXEL_OK))
        self.assertEqual(honest, (PJ.WORLD_OK, PJ.PIXEL_OK))

    def test_neither_half_implies_the_other(self):
        """Stated as the property rather than as three literals: WORLD-OK occurs with both
        pixel verdicts and PIXEL-OK occurs with both world verdicts, so neither level's
        result can be inferred from the other's."""
        seen = set(PJ.granularity_is_sealed())
        self.assertIn((PJ.WORLD_OK, PJ.PIXEL_BAD), seen)
        self.assertIn((PJ.WORLD_BAD, PJ.PIXEL_OK), seen)
        self.assertEqual({w for w, _p in seen}, {PJ.WORLD_OK, PJ.WORLD_BAD})
        self.assertEqual({p for _w, p in seen}, {PJ.PIXEL_OK, PJ.PIXEL_BAD})

    def test_a_SCALAR_verifier_would_have_accepted_the_pixel_forgery(self):
        """WHY THE PAIR EXISTS, measured rather than argued. Collapse the verdict to the
        world half — the natural thing to write, and what a single boolean amounts to —
        and the record whose frame is forged passes. The pixel ownership was never
        examined and nothing in the result says so."""
        pixel_forged, _world_forged, _honest = PJ.granularity_is_sealed()
        scalar_world_only = pixel_forged[0] == PJ.WORLD_OK
        self.assertTrue(scalar_world_only,
                        "fixture invalid: the world half was supposed to hold")
        self.assertEqual(pixel_forged[1], PJ.PIXEL_BAD,
                         "the pair failed to catch what the scalar missed")

    def test_verify_joined_returns_a_PAIR_and_has_no_boolean_sibling(self):
        """STRUCTURAL, on the syntax: every `return` in `verify_joined` is a 2-tuple, and
        no module-level function returns `world == ... and pixel == ...`. A behavioural
        test cannot stop someone adding a convenience wrapper that collapses the pair,
        which is the exact shape this rung is guarding against."""
        tree = ast.parse(open(PJ.__file__, "r", encoding="utf-8").read())
        fn = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == "verify_joined")
        returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value]
        self.assertTrue(returns)
        for r in returns:
            self.assertIsInstance(r.value, ast.Tuple, "verify_joined returned a scalar")
            self.assertEqual(len(r.value.elts), 2)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name != "verify_joined":
                for r in ast.walk(node):
                    if isinstance(r, ast.Return) and isinstance(r.value, ast.Compare):
                        src = ast.dump(r.value)
                        self.assertNotIn("WORLD_OK", src,
                                         f"{node.name} collapses the pair to a boolean")


if __name__ == "__main__":
    unittest.main(verbosity=2)
