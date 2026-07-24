# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for tools/terrain/byteacct.py — PROOF-CARRYING BYTE ACCOUNTING (URDRBYT1): the wire-level
refinement of the scheduler under a real BYTE budget, where updates have different serialized costs. The
byte budget B IS the constant packet size (records + anonymous padding to B), so byte-accounting composes
with the constant-shape hardening. Composition over `schedule`, NO new glyph.

  BYTE BUDGET — every packet is exactly B; records fit the body budget; `_serialize_nopad`/`_pack_overrun`
    exceed B and are caught.
  MAXIMAL PREFIX / FRAGMENTATION — the admitted discretionary set is the priority PREFIX, independent of
    packing; `_pack_firstfit` (gap-fill) admits a different set.
  VARIABLE-SIZE STARVATION-FREEDOM — a large update, when oldest, is admitted before smaller newer ones;
    `_pack_smallest_first` starves the large FULL forever.
  SERIALIZATION — canonical zigzag-varints; `_serialize_noncanonical` (non-minimal) is rejected on parse;
    identical worlds serialize identically.
  ACCOUNTING FIDELITY — a packet equals the canonical re-serialization of its own records (nothing hidden
    in padding); `_serialize_hidden` is caught.
  CLOSED-WORLD FROM THE WIRE — the client reconstructs exactly the manifested set; `_run_drop_departure`
    leaves a ghost.
  DETERMINISTIC — a run is a pure function of (ticks, lens, byte budget); the wall-clock plant diverges.
  REDUCES TO THE SCHEDULE at a roomy budget — no byte pressure, nothing defers.

Every test can go red (L5); the plants bite before the goldens pin (L15)."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "tools", "terrain"))

import byteacct as B                                            # noqa: E402
import anamorphosis as A                                        # noqa: E402
import perception as PC                                         # noqa: E402


def _cw_run(ticks, cl, L, budget):
    rep = B.run(ticks, cl, L, budget)
    cstate = {}
    ok = True
    for t, (e, w) in enumerate(ticks):
        if not B.is_closed_world(e, w, cl, L, rep["packets"][t], cstate):
            ok = False
        cstate = B.client_apply(cstate, rep["packets"][t])
    return rep, ok


class TheByteBudget(unittest.TestCase):
    def test_scene_goldens_and_determinism(self):
        for name in B.SCENES:
            self.assertEqual(B.scene_result(name), B.golden(name), name)
            self.assertEqual(B.scene_result(name), B.scene_result(name), name)

    def test_every_packet_is_exactly_B(self):
        ticks, cl = B._contended()
        rep = B.run(ticks, cl, A.lens(0, 0), B._SB)
        self.assertTrue(B.byte_budget_ok(rep))
        for p in rep["packets"]:
            self.assertEqual(len(p), B._SB)
        self.assertGreater(rep["deferrals"], 0, "the byte budget never bound — no contention")

    def test_overrun_plant_bites(self):
        """A serializer that neither caps nor pads emits a packet whose length is not B — caught."""
        recs = [B.rec_full(4, 3, 0, B._d(4)), B.rec_full(5, 4, 0, B._d(5)), B.rec_move(1, 1, 1)]
        over = B._serialize_nopad(0, B._SB, recs)                # records exceed the body budget
        self.assertNotEqual(len(over), B._SB)
        with self.assertRaises(B.ByteAcctError):
            B.serialize(0, B._SB, recs)                          # the honest serializer refuses to overrun

    def test_refuses_when_mandatory_cannot_fit(self):
        """If the mandatory records alone exceed the body budget, the tick REFUSES (typed), never silently
        drops a membership record."""
        with self.assertRaises(B.ByteAcctError):
            B._pack([B.rec_full(1, 0, 0, B._d(1)), B.rec_full(2, 0, 0, B._d(2))], [], 40)


class ThePrefixPacking(unittest.TestCase):
    def test_prefix_correct(self):
        ticks, cl = B._contended()
        self.assertTrue(B.prefix_correct(ticks, cl, A.lens(0, 0), B._SB))

    def test_fragmentation_plant_bites(self):
        """The admitted set is the priority PREFIX; a first-fit packer that skips a non-fitting record and
        fills the gap admits a DIFFERENT (non-prefix) set."""
        disc = [B.rec_full(4, 3, 0, B._d(4)), B.rec_full(5, 4, 0, B._d(5)), B.rec_move(1, 1, 1)]
        honest, _ = B._pack([], disc, 46)
        firstfit, _ = B._pack_firstfit([], disc, 46)
        self.assertNotEqual(firstfit, honest, "first-fit must diverge from the maximal prefix")
        self.assertEqual(honest, disc[:1], "the prefix stops at the first non-fitting record")

    def test_variable_size_starvation(self):
        """Smallest-first packing starves a large update (a cite-change FULL) that age-first keeps bounded
        — the variable-size hazard the byte model introduces (L15)."""
        ticks, cl = B._starve(20)
        honest = B.run(ticks, cl, A.lens(0, 0), B._SB)["max_stale"]
        smallest = B.run(ticks, cl, A.lens(0, 0), B._SB, _pack_fn=B._pack_smallest_first)["max_stale"]
        self.assertLessEqual(honest, B.OVERHEAD)                # bounded and small
        self.assertGreater(smallest, honest * 3, "smallest-first did not starve the large update")


class TheSerialization(unittest.TestCase):
    def test_zigzag_varint_roundtrip_and_canonical(self):
        for n in (0, 1, -1, 63, -64, 128, -1000, 65535, -70000):
            self.assertEqual(B._unzz(B._zz(n)), n)
        self.assertEqual(B._uvarint(0), b"\x00")
        self.assertEqual(B._uvarint(300), bytes([0xAC, 0x02]))  # minimal 2-byte encoding
        with self.assertRaises(B.ByteAcctError):
            B._read_uvarint(bytes([0x80, 0x00]), 0)             # non-minimal → rejected

    def test_identical_worlds_identical_bytes(self):
        ticks, cl = B._contended()
        self.assertEqual(B.run(ticks, cl, A.lens(0, 0), B._SB)["packets"],
                         B.run(ticks, cl, A.lens(0, 0), B._SB)["packets"])

    def test_noncanonical_serializer_rejected(self):
        packet = B._serialize_noncanonical(0, B._SB, [B.rec_move(1, 3, 4)])
        with self.assertRaises(B.ByteAcctError):
            B.parse(packet)


class TheAccounting(unittest.TestCase):
    def test_accounting_fidelity(self):
        ticks, cl = B._contended()
        rep = B.run(ticks, cl, A.lens(0, 0), B._SB)
        self.assertTrue(B.accounting_fidelity(rep))
        self.assertTrue(B.client_matches_server(rep))

    def test_hidden_padding_plant_bites(self):
        """Smuggling non-zero bytes into the anonymous padding (a byte the header does not account for) is
        caught by the canonical re-serialization check."""
        honest = B.serialize(0, B._SB, [B.rec_full(1, 3, 0, B._d(1))])
        hidden = B._serialize_hidden(0, B._SB, [B.rec_full(1, 3, 0, B._d(1))])
        self.assertTrue(B.accounting_fidelity({"packets": [honest], "used_total": B.parse(honest)[3]}))
        self.assertFalse(B.accounting_fidelity({"packets": [hidden], "used_total": B.parse(hidden)[3]}))


class TheClosedWorld(unittest.TestCase):
    def test_closed_world_from_the_wire(self):
        ticks, cl = B.gen_sequence(PC._LCG(B.SWEEP_SEED))
        _rep, ok = _cw_run(ticks, cl, A.lens(0, 0), B.OVERHEAD + 120)
        self.assertTrue(ok, "the client reconstruction diverged from the manifested set")

    def test_drop_departure_ghost_plant_bites(self):
        """Never emitting a REMOVE leaves a departed entity addressable in the client's reconstruction —
        a ghost the closed-world law catches."""
        ticks, cl = B.gen_sequence(PC._LCG(B.SWEEP_SEED))
        _packets, cstates = B._run_drop_departure(ticks, cl, A.lens(0, 0), B.OVERHEAD + 120)
        bit = any(set(cstates[t]) != set(A._manifest_under(e, w, cl, A.lens(0, 0)))
                  for t, (e, w) in enumerate(ticks))
        self.assertTrue(bit, "the ghost was not caught")


class TheDeterminism(unittest.TestCase):
    def test_wallclock_plant_diverges(self):
        ticks, cl = B._contended()
        L = A.lens(0, 0)
        pure = B.run(ticks, cl, L, B._SB)["packets"]
        self.assertEqual(pure, B.run(ticks, cl, L, B._SB, _clock=lambda: 0)["packets"])
        self.assertNotEqual(pure, B.run(ticks, cl, L, B._SB, _clock=lambda: 1)["packets"])

    def test_reduces_to_schedule_at_roomy_budget(self):
        ticks, cl = B._contended()
        self.assertEqual(B.run(ticks, cl, A.lens(0, 0), B.OVERHEAD + 400)["deferrals"], 0)


class TheSweep(unittest.TestCase):
    def test_sweep_matches_golden_and_non_vacuous(self):
        d1 = B.sweep_digest()
        self.assertEqual(d1, B.sweep_digest(), "deterministic")
        self.assertEqual(d1, B.sweep_golden(), "sweep drifted from golden")
        rep = B.sweep()
        self.assertGreater(rep["deferrals"], 0, "the byte budget never bound")
        self.assertGreater(rep["departures"], 0, "no entity ever departed")
        self.assertGreater(rep["stale_seen"], 0, "staleness was never exercised")

    def test_sweep_bites_leaked_hidden(self):
        orig = A._manifest_under
        A._manifest_under = lambda entities, walls, cl, L: sorted(entities)   # leak EVERYTHING
        try:
            with self.assertRaises(B.ByteAcctError):
                B.sweep()
        finally:
            A._manifest_under = orig
        self.assertEqual(B.sweep_digest(), B.sweep_golden(), "clean after revert")


if __name__ == "__main__":
    unittest.main()
