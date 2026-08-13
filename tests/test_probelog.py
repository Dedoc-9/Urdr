# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""probelog (URDRPBL1) — the first §3 log becomes evidence, through the door that already existed.

The tests import BOTH sides and inject sealframe's machinery into the leaf, the same wiring the
gate stage uses — probelog itself imports nothing from the tree (the lattice taught that to
`confound`, `pedigree` and `rehearse` before it; this module was born a leaf)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import probelog as PB                                        # noqa: E402
import sealframe as SF                                       # noqa: E402

DEPS = {"make_log": SF.make_segment_log, "ledger": SF.ledger_from_log,
        "budget": SF.budget_verdict, "segments": SF.SEGMENTS}


def _parsed():
    return PB.parse(PB.load())


class TheRecord(unittest.TestCase):
    def test_the_committed_bytes_hash_to_the_pin(self):
        self.assertTrue(PB.load())

    def test_a_flipped_byte_refuses(self):
        raw = PB.load()
        bad = raw[:100] + ("0" if raw[100] != "0" else "1") + raw[101:]
        with self.assertRaises(PB.ProbelogError):
            PB.load(text=bad)

    def test_a_v0_log_refuses(self):
        """v0's pacing was defective and its only chain-bearing run was anonymous — version
        discipline keeps that log from ever graduating anything."""
        with self.assertRaises(PB.ProbelogError):
            PB.parse(PB.load().replace("present_probe v0.1", "present_probe v0"))

    def test_an_empty_click_table_refuses(self):
        """The protocol's completeness line, enforced: a chainless run measured only the frame
        loop and grades nothing."""
        raw = PB.load()
        head_only = "\n".join(raw.split("\n")[:6]) + "\n"
        with self.assertRaises(PB.ProbelogError):
            PB.parse(head_only)

    def test_a_malformed_chain_row_refuses(self):
        with self.assertRaises(PB.ProbelogError):
            PB.parse(PB.load() + "1 2 3\n")
        with self.assertRaises(PB.ProbelogError):
            PB.parse(PB.load() + "a b c d e f\n")

    def test_the_bands_are_derived_and_conservative(self):
        """floor(min)..ceil(max) at 1e-4 ms — a floor may not round up nor a ceiling down."""
        b = PB.bands(_parsed()["chains"])
        for name, (lo, med, hi) in b.items():
            self.assertLessEqual(lo, med, name)
            self.assertLessEqual(med, hi, name)
        self.assertEqual(PB._floor4(47900), 0.0479)
        self.assertEqual(PB._ceil4(426000), 0.4260)
        self.assertEqual(PB._ceil4(100), 0.0001)
        self.assertEqual(PB._floor4(199), 0.0001)


class TheDoor(unittest.TestCase):
    def test_the_new_segments_graduate_with_the_derived_bands(self):
        ok, why = PB.the_new_segments_graduate(_parsed(), SF.make_segment_log, SF.ledger_from_log)
        self.assertTrue(ok, why)

    def test_the_floor_cannot_be_lowered_by_lighter_work(self):
        """THE DEMONSTRATION: the probe's trivial tick reads under §4b's 100-biped floor; the door
        keeps the old floor and cites both sources."""
        ok, why = PB.the_floor_cannot_be_lowered(_parsed(), SF.make_segment_log,
                                                 SF.ledger_from_log, SF.SEGMENTS)
        self.assertTrue(ok, why)

    def test_the_strict_door_refuses_naming_what_is_missing(self):
        """power and scheduler — and NOT machine, which the probe did record. This red assertion
        is probe v0.2's specification."""
        ok, msg = PB.the_strict_door_refuses(_parsed(), SF.make_segment_log, SF.ledger_from_log)
        self.assertTrue(ok, msg)

    def test_an_anonymous_log_refuses(self):
        self.assertTrue(PB.an_anonymous_log_refuses(_parsed(), SF.make_segment_log,
                                                    SF.ledger_from_log))

    def test_a_software_timer_cannot_claim_the_panel(self):
        self.assertTrue(PB.a_wrong_instrument_refuses(_parsed(), SF.make_segment_log,
                                                      SF.ledger_from_log))

    def test_the_verdict_is_undetermined_and_names_whose_task_remains(self):
        ok, v = PB.the_verdict_is_honest(_parsed(), SF.make_segment_log, SF.ledger_from_log,
                                         SF.budget_verdict, 40.0)
        self.assertTrue(ok, v)
        self.assertEqual(v["pending"], ())
        self.assertEqual(v["pending_platform"], ("present_wait",))
        self.assertEqual(v["needs_hardware"], ("input_transport", "panel"))

    def test_the_bound_rose_and_is_derived_not_typed(self):
        """Before this record the bound was the tick floor alone; after, it is the sum of every
        graduated floor — computed from the ledger, compared against the static table."""
        led = PB.graduate(_parsed(), SF.make_segment_log, SF.ledger_from_log)
        before = SF.lower_bound_ms(SF.SEGMENTS)
        after = SF.lower_bound_ms(led)
        self.assertGreater(after, before)
        b = PB.bands(_parsed()["chains"])
        self.assertAlmostEqual(after - before,
                               b["frame_render"][0] + b["present_queue"][0],
                               places=12)


class ThePinnedScenes(unittest.TestCase):
    def test_the_record_scene_matches_its_golden(self):
        self.assertEqual(PB.scene_result("record"), PB.golden("record"))

    def test_the_ledger_scene_matches_its_golden(self):
        self.assertEqual(PB.scene_result("ledger", DEPS), PB.golden("ledger"))

    def test_the_ledger_scene_refuses_without_the_door(self):
        """A scene that silently skipped the door would pin a digest of nothing (L61)."""
        with self.assertRaises(PB.ProbelogError):
            PB.scene_case("ledger")

    def test_an_unknown_scene_refuses(self):
        with self.assertRaises(PB.ProbelogError):
            PB.scene_case("no-such-scene")


if __name__ == "__main__":
    unittest.main(verbosity=2)
