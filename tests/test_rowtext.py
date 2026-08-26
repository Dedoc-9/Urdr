#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rowtext (URDRRWT1) — the gate's own transcript is a certified artefact, so its defects are defects.

Two detectors, both pure functions over source text so every case can be planted without touching
disk. `%%` is the escape a `%`-formatted string uses to emit one per cent sign; in a string that is
never the left operand of a `%` it is not an escape, it is two characters, and five gate rows said
`93%%` and `20.1%%` for four rungs. And a stage docstring that names a module identity is naming
which module the row measures — `voxlat`'s claimed URDRVXF1, which is `voxref`'s magic, sent a
reader to the wrong file.

Both live populations are now EMPTY, which is exactly why every test here plants: a detector with
nothing to find is indistinguishable from one that cannot find.
"""
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import verify  # noqa: E402

_BARE = ('class P:\n'
         '    def stage(self):\n'
         '        self.record("plant-a", True, "coverage is 93%% of the frame")\n')
_FORMAT = ('class P:\n'
           '    def stage(self):\n'
           '        self.record("plant-b", True, "ok %d%% here" % 5)\n')
_BRANCH = ('class P:\n'
           '    def stage(self):\n'
           '        self.record("plant-c", True, "green" if x else "red at 90%%")\n')
_KEYWORD = ('class P:\n'
            '    def stage(self):\n'
            '        self.record("plant-d", True, detail="held at 5%% margin")\n')


class TheLiteralPercentDetector(unittest.TestCase):
    def test_a_bare_literal_reddens(self):
        self.assertEqual(verify.literal_percent_rows(_BARE), [("plant-a", "literal-percent")])

    def test_a_genuine_format_string_does_not(self):
        """The control. Without it the detector is just 'contains two per cent signs'."""
        self.assertEqual(verify.literal_percent_rows(_FORMAT), [])

    def test_an_untaken_branch_reddens_on_its_own(self):
        """The branch not taken today is taken the moment the row reddens."""
        self.assertEqual(verify.literal_percent_rows(_BRANCH), [("plant-c", "literal-percent")])

    def test_a_keyword_detail_is_reached(self):
        self.assertEqual(verify.literal_percent_rows(_KEYWORD), [("plant-d", "literal-percent")])

    def test_the_live_gate_is_clean(self):
        with io.open(os.path.join(ROOT, "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertEqual(verify.literal_percent_rows(src), [])

    def test_a_record_with_no_detail_is_not_a_defect(self):
        self.assertEqual(verify.literal_percent_rows(
            'class P:\n    def stage(self):\n        self.record("bare", True)\n'), [])


class TheIdentityDetector(unittest.TestCase):
    def test_the_retired_defect_is_caught(self):
        self.assertEqual(verify.identity_mismatches({"voxlat": "URDRVXF1"},
                                                    {"voxlat": "URDRVOX1"}),
                         [("voxlat", "URDRVXF1", "URDRVOX1")])

    def test_the_corrected_form_is_the_control(self):
        self.assertEqual(verify.identity_mismatches({"voxlat": "URDRVOX1"},
                                                    {"voxlat": "URDRVOX1"}), [])

    def test_a_stage_with_no_module_of_its_name_is_not_checked(self):
        """Narrow on purpose: `pixid_join` names URDRPIDJ1 and there is no pixid_join.py."""
        self.assertEqual(verify.identity_mismatches({"nosuch": "URDRZZZ1"}, {}), [])

    def test_only_the_first_parenthesised_identity_is_read(self):
        claims = verify.stage_identity_claims(
            'class P:\n'
            '    def voxcand(self):\n'
            '        """A rung (URDRVXD1) that transcribes (URDRVXF1) faithfully."""\n')
        self.assertEqual(claims, {"voxcand": "URDRVXD1"})

    def test_the_live_gate_is_clean(self):
        with io.open(os.path.join(ROOT, "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
        claims = verify.stage_identity_claims(src)
        magics = verify.module_magics()
        self.assertEqual(verify.identity_mismatches(claims, magics), [])

    def test_the_detector_has_something_to_check(self):
        """A narrow rule that checked nothing would be green by vacuity."""
        with io.open(os.path.join(ROOT, "verify.py"), encoding="utf-8") as fh:
            src = fh.read()
        claims = verify.stage_identity_claims(src)
        magics = verify.module_magics()
        self.assertGreater(len([s for s in claims if s in magics]), 90)

    def test_module_magics_finds_the_tool_tree(self):
        m = verify.module_magics()
        self.assertEqual(m.get("voxref"), "URDRVXF1")
        self.assertEqual(m.get("voxfate"), "URDRVXS1")


if __name__ == "__main__":
    unittest.main()
