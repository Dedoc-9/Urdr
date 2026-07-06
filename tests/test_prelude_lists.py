# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R1b falsifiers: the minimal list prelude (push, cat, nth) — strictly what the
graded-algebra rung needs, each with typed failure modes and fuel accounting."""
import unittest

from urdr import evaluate
from urdr.errors import UrdrError


def run(src, **kw):
    return evaluate.run_program(src, **kw)


def code_of(src, **kw):
    try:
        run(src, **kw)
    except UrdrError as err:
        return err.code
    return None


class TestListPrelude(unittest.TestCase):
    def test_push_appends_without_mutating(self):
        out = run("a := [1, 2]\nb := push(a, 3)\n[len(a), len(b), nth(b, 2)]")
        self.assertEqual(evaluate.render(out), "[2, 3, 3]")

    def test_cat_concatenates_by_digest(self):
        run(r"=?(cat([1], [2, 3]), [1, 2, 3])")  # ≟ raises URDR-ASSERT on breach

    def test_cat_empty_identities(self):
        run(r"=?(cat([], [7]), [7])")
        run(r"=?(cat([7], []), [7])")

    def test_nth_reads(self):
        out = run("nth([4, 5, 6], 0) + nth([4, 5, 6], 2)")
        self.assertEqual(evaluate.render(out), "10")

    def test_nth_out_of_range_is_typed_error(self):
        self.assertEqual(code_of("nth([1], 1)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of("nth([1], -1)"), "URDR-TYPE-RUN")

    def test_nth_type_errors(self):
        self.assertEqual(code_of("nth(1, 0)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of("nth([1], [0])"), "URDR-TYPE-RUN")

    def test_push_and_cat_type_errors(self):
        self.assertEqual(code_of("push(1, 2)"), "URDR-TYPE-RUN")
        self.assertEqual(code_of("cat([1], 2)"), "URDR-TYPE-RUN")

    def test_prelude_names_not_rebindable(self):
        self.assertEqual(code_of("push := 1"), "URDR-REBIND")
        self.assertEqual(code_of("cat := 1"), "URDR-REBIND")
        self.assertEqual(code_of("nth := 1"), "URDR-REBIND")

    def test_cat_charges_fuel_for_the_copy(self):
        # Same program: succeeds with room, exhausts when the copy charge lands.
        src = "xs := range(20)\ncat(xs, xs)"
        self.assertIsNone(code_of(src, fuel=200))
        self.assertEqual(code_of(src, fuel=50), "URDR-FUEL")


if __name__ == "__main__":
    unittest.main()
