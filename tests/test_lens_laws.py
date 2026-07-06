# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Membrane falsifiers: view is pure, put-get exact, get-put up to lineage with exact
anamnesis recovery (D1 §8 states the deviation honestly)."""
import unittest

from urdr import canon, evaluate
from urdr.errors import UrdrError


def run(src):
    return evaluate.run_program(src)


class TestMembrane(unittest.TestCase):
    def test_view_is_pure(self):
        # Observing must not perturb: digest before view == digest after view.
        src = r"""
s := \st{x: 1, y: 2}
d0 := \di(s)
v := \vw(s, 'x)
=?(\di(s), d0)
"""
        run(src)  # ≟ raises URDR-ASSERT on breach

    def test_put_get_exact(self):
        src = r"""
s := \st{x: 1, y: 2}
=?(\vw(\ed(s, 'x, 5), 'x), 5)
"""
        run(src)

    def test_get_put_up_to_lineage_with_exact_recovery(self):
        # ☿(s,'x,☽(s,'x)) has s's fields; ↩ of it IS s (digest-identical).
        src = r"""
s := \st{x: 1, y: 2}
v := \vw(s, 'x)
same := \ed(s, 'x, v)
f1 := =?(\vw(same, 'x), \vw(s, 'x))
f2 := =?(\vw(same, 'y), \vw(s, 'y))
=?(\di(\am(same)), \di(s))
"""
        run(src)

    def test_anamnesis_returns_digest_identical_prior(self):
        src = r"""
s := \st{x: 1, y: 2}
=?(\di(\am(\ed(s, 'x, 5))), \di(s))
"""
        run(src)

    def test_edit_changes_digest(self):
        # Non-vacuity of the digest itself: an edit MUST move the address.
        src = r"""
s := \st{x: 1}
s2 := \ed(s, 'x, 2)
\di(s2) != \di(s)
"""
        result = run(src)
        self.assertEqual(evaluate.render(result), "1")

    def test_anamnesis_on_root_is_error(self):
        with self.assertRaises(UrdrError) as ctx:
            run(r"\am(\st{x: 1})")
        self.assertEqual(ctx.exception.code, "URDR-ANAMNESIS-ROOT")

    def test_lineage_is_part_of_identity(self):
        # Two stores with equal fields but different histories have different digests;
        # anamnesis distinguishes them. (D1 §8: we choose lineage and say so.)
        src_edited = r"""
s := \st{x: 1}
\ed(\ed(s, 'x, 9), 'x, 1)
"""
        src_root = r"\st{x: 1}"
        d_edited = canon.hexdigest(run(src_edited))
        d_root = canon.hexdigest(run(src_root))
        self.assertNotEqual(d_edited, d_root)


if __name__ == "__main__":
    unittest.main()
