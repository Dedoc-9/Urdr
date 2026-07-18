# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for continuous client-prediction reconcile (`tools/terrain/cpredict.py`, T3.20, MMO Stage A ×
Stage B) — `predict` on `glide`. Reconcile a client's guessed inputs against the authority on the CONTINUOUS
sub-cell trajectory, rolling back via `splice`'s resumption.

  * REFERENCE — the three pinned scenes reproduce their URDRCPRED1 digests;
  * CONTINUOUS ROLLBACK-REPLAY EQUIVALENCE (the keystone) — reconstruct == glide_cells(auth) bit-for-bit,
    for every prediction;
  * REFINES THE DISCRETE RECONCILE — the continuous mispredict tick precedes-or-equals `predict`'s discrete
    tick, and is STRICTLY earlier on a sub-cell misprediction the grid cannot see (non-vacuity: a witness
    where continuous catches what drive misses);
  * FLOORS TO DRIVE (the commutation) — the floored continuous reconstruction equals drive(auth), the
    discrete reconcile `predict` already certified;
  * REUSES THE KERNEL LOCALIZER — the tick IS `lockstep.first_desync` over the continuous pose chains;
  * REUSABLE PREFIX IS AUTHORITATIVE — the kept prefix is bit-identical to the authoritative glide;
  * CORRECT PREDICTION — an exact guess needs no rollback (k None, full prefix);
  * LAZY-RECONCILE DEFECT — keeping one mispredicted pose too many makes the replay diverge (non-vacuity);
  * REFUSAL — a window mismatch / empty window / bad transcript is a typed `CPRED-REFUSE`.

Requires the continuous mover (`glide`), resumption (`splice`), the discrete reconcile (`predict`, for the
refinement comparison), and the kernel localizer (`lockstep`); the gate runs with them."""
import itertools
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "physics"),
           os.path.join(_ROOT, "tools", "netcode")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import cpredict as CP                                             # noqa: E402
import glide as GL                                                # noqa: E402
import drive as DR                                                # noqa: E402
import predict as PR                                              # noqa: E402
import lockstep as N1                                             # noqa: E402

_START, _MS, _SUB = (2, 8), 16, 4


def _le(kc, kd):
    """Continuous tick precedes-or-equals discrete; None = never diverges = latest."""
    return True if kd is None else (kc is not None and kc <= kd)


class CPredict(unittest.TestCase):
    def test_scene_goldens(self):
        for name in CP.SCENES:
            dig = CP.scene_result(name)
            self.assertEqual(dig, CP.golden(name), f"{name}: cpredict digest drifted")
            self.assertEqual(CP.scene_result(name), dig, f"{name}: nondeterministic")

    def test_continuous_equivalence(self):
        H = GL._heights("blank")
        auth = "eeee"
        auth_traj = GL.glide_cells(H, _START, auth, _MS, _SUB)
        checked = 0
        for pred in ("".join(p) for p in itertools.product("eEnNsw", repeat=4)):
            self.assertEqual(CP.reconstruct(H, _START, auth, pred, _MS, _SUB), auth_traj,
                             f"reconstruct must equal the full continuous re-sim for prediction {pred!r}")
            checked += 1
        self.assertEqual(checked, 6 ** 4, "the equivalence must sweep the whole prediction grid")

    def test_refines_discrete_with_witness(self):
        Hb, Hm = GL._heights("blank"), GL._heights("mountains")
        strict = 0
        # blank: continuous and discrete agree on the tick (no sub-cell walls)
        for pred in ("".join(p) for p in itertools.product("eEnw", repeat=3)):
            kc, _ = CP.reconcile(Hb, _START, "eee", pred, _MS, _SUB)
            kd, _ = PR.reconcile(Hb, _START, "eee", pred, _MS)
            self.assertTrue(_le(kc, kd), f"continuous tick must precede-or-equal discrete for {pred!r}")
        # mountains east wall: a walk guessed where the authority sprinted into the wall
        kc, _ = CP.reconcile(Hm, (2, 0), "E", "e", 20, _SUB)
        kd, _ = PR.reconcile(Hm, (2, 0), "E", "e", 20)
        self.assertTrue(_le(kc, kd), "the witness must still satisfy the refinement order")
        if kc is not None and kd is None:
            strict += 1
        self.assertGreater(strict, 0, "NON-VACUITY: continuous must STRICTLY refine on a sub-cell mispredict")

    def test_subcell_witness(self):
        H = GL._heights("mountains")
        kc, _ = CP.reconcile(H, (2, 0), "E", "e", 20, _SUB)
        kd, _ = PR.reconcile(H, (2, 0), "E", "e", 20)
        self.assertIsNotNone(kc, "the continuous reconcile must catch the sub-cell misprediction")
        self.assertIsNone(kd, "the discrete reconcile cannot see it (same cell)")
        self.assertEqual(CP.reconstruct(H, (2, 0), "E", "e", 20, _SUB), GL.glide_cells(H, (2, 0), "E", 20, _SUB),
                         "even the sub-cell rollback must reconstruct the authority exactly")

    def test_floors_to_drive(self):
        H = GL._heights("blank")
        auth = "eeee"
        for pred in ("eeee", "eene", "neee", "eesw", "EEEE"):
            recon = CP.reconstruct(H, _START, auth, pred, _MS, _SUB)
            self.assertEqual(GL.floored(recon), DR.drive(H, _START, auth, _MS),
                             f"floored continuous reconstruction must equal drive(auth) for {pred!r}")
            self.assertEqual(GL.floored(recon), PR.reconstruct(H, _START, auth, pred, _MS),
                             f"...and equal the discrete reconcile predict certified for {pred!r}")

    def test_reuses_kernel_localizer(self):
        H = GL._heights("blank")
        auth, pred = "eeee", "eeNe"
        k, _r = CP.reconcile(H, _START, auth, pred, _MS, _SUB)
        direct = N1.first_desync(CP._chain(GL.glide_cells(H, _START, pred, _MS, _SUB)),
                                 CP._chain(GL.glide_cells(H, _START, auth, _MS, _SUB)))
        self.assertEqual(k, direct, "the tick must BE lockstep.first_desync, not a private reimplementation")

    def test_reusable_prefix_is_authoritative(self):
        H = GL._heights("blank")
        auth = "eeee"
        auth_traj = GL.glide_cells(H, _START, auth, _MS, _SUB)
        for pred in ("eeee", "eeNe", "neee", "nnnn"):
            _k, reusable = CP.reconcile(H, _START, auth, pred, _MS, _SUB)
            self.assertEqual(reusable, tuple(auth_traj[:len(reusable)]),
                             f"the reusable prefix must be bit-identical to the authoritative glide for {pred!r}")

    def test_correct_prediction_no_rollback(self):
        H = GL._heights("blank")
        k, reusable = CP.reconcile(H, _START, "eeee", "eeee", _MS, _SUB)
        self.assertIsNone(k, "a correct prediction has no misprediction tick")
        self.assertEqual(len(reusable), 5, "a correct prediction keeps the full trajectory")
        self.assertEqual(CP.replay(H, _START, reusable, "eeee", _MS, _SUB), reusable, "replay is the identity")

    def test_lazy_reconcile_defect_diverges(self):
        H = GL._heights("blank")
        auth, pred = "eeee", "eeNe"
        auth_traj = GL.glide_cells(H, _START, auth, _MS, _SUB)
        k, _r = CP.reconcile(H, _START, auth, pred, _MS, _SUB)
        lazy = tuple(GL.glide_cells(H, _START, pred, _MS, _SUB)[:k + 1])   # one mispredicted pose too many
        self.assertNotEqual(CP.replay(H, _START, lazy, auth, _MS, _SUB), auth_traj,
                            "over-claiming the reusable prefix must make the replay diverge (non-vacuity)")

    def test_typed_refusals(self):
        H = GL._heights("blank")
        for auth, pred in (("ee", "eee"), ("", ""), ("eXe", "eee")):
            with self.assertRaises(CP.CPredError) as cm:
                CP.reconcile(H, _START, auth, pred, _MS, _SUB)
            self.assertEqual(cm.exception.code, "CPRED-REFUSE", f"wrong code for {(auth, pred)!r}")


if __name__ == "__main__":
    unittest.main()
