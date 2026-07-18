# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the client-prediction RECONCILE primitive (`tools/terrain/predict.py`, T3.17, MMO
Stage A) — client-side prediction made reconstruct-or-refuse. Given the authoritative and predicted input
transcripts, localize the first misprediction and prove that keeping the correct prefix and replaying the
true suffix reproduces the authority BIT-FOR-BIT.

  * REFERENCE — the three pinned scenes reproduce their URDRPRED1 digests ×2;
  * ROLLBACK-REPLAY EQUIVALENCE (the keystone) — for EVERY predicted transcript, reconstruct == the full
    authoritative re-simulation `drive(auth)`, bit-for-bit (partial rollback == full re-sim);
  * REUSABLE PREFIX IS AUTHORITATIVE — the kept prefix is bit-identical to the authority's (the client
    kept only correct poses; nothing wrong survives the reconcile);
  * LOCALIZATION — reconcile returns the exact first divergent pose tick (None if pose-correct), agreeing
    with a direct pose comparison;
  * REUSES THE KERNEL LOCALIZER — the tick is `lockstep.first_desync` over the pose-digest chains, not a
    private reimplementation;
  * CORRECT PREDICTION — an exact prediction needs no rollback (tick None, full prefix, replay is identity);
  * POSE-LEVEL NOT INPUT-LEVEL — different inputs that yield identical poses (walk vs sprint into a wall)
    need no rollback (tick None) — reconcile is over state, not commands;
  * LAZY-RECONCILE DEFECT — keeping one mispredicted pose too many makes the replay diverge from the
    authority (non-vacuity: a reconcile that over-claims the reusable prefix is caught);
  * REFUSAL — a reconcile-window mismatch / empty window / bad transcript is a typed `PRED-REFUSE`.

Requires the kernel netcode localizer (`lockstep` → `field`); the full gate runs with it."""
import itertools
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "netcode"),
           os.path.join(_ROOT, "tools", "physics")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import predict as P                                                # noqa: E402
import drive as DR                                                 # noqa: E402
import lockstep as N1                                              # noqa: E402


class Predict(unittest.TestCase):
    def test_scene_goldens(self):
        for name in P.SCENES:
            dig = P.scene_result(name)
            self.assertEqual(dig, P.golden(name), f"{name}: predict digest drifted")
            self.assertEqual(P.scene_result(name), dig, f"{name}: nondeterministic")

    def test_rollback_replay_equivalence(self):
        H = P._heights(P._HF_SCENE)
        auth = "eeee"
        auth_traj = DR.drive(H, P._START, auth, P._MS)
        checked = 0
        for pred in ("".join(p) for p in itertools.product("eEnNsw", repeat=4)):
            self.assertEqual(P.reconstruct(H, P._START, auth, pred, P._MS), auth_traj,
                             f"reconstruct must equal the full authoritative re-sim for prediction {pred!r}")
            checked += 1
        self.assertEqual(checked, 6 ** 4, "the equivalence must be checked over the whole prediction grid")

    def test_reusable_prefix_is_authoritative(self):
        H = P._heights(P._HF_SCENE)
        auth = "eeee"
        auth_traj = DR.drive(H, P._START, auth, P._MS)
        for pred in ("eeee", "eeNe", "Neee", "eesw", "nnnn"):
            _k, reusable = P.reconcile(H, P._START, auth, pred, P._MS)
            self.assertEqual(reusable, tuple(auth_traj[:len(reusable)]),
                             f"the reusable prefix must be bit-identical to the authority for {pred!r}")

    def test_localizes_first_misprediction(self):
        H = P._heights(P._HF_SCENE)
        auth = "eeee"
        auth_traj = DR.drive(H, P._START, auth, P._MS)
        for pred in ("eeee", "eeNe", "Neee", "eeeN"):
            k, _r = P.reconcile(H, P._START, auth, pred, P._MS)
            pred_traj = DR.drive(H, P._START, pred, P._MS)
            expect = next((i for i in range(len(auth_traj)) if auth_traj[i] != pred_traj[i]), None)
            self.assertEqual(k, expect, f"reconcile must localize the exact first divergent pose for {pred!r}")

    def test_reuses_kernel_localizer(self):
        H = P._heights(P._HF_SCENE)
        auth, pred = "eeee", "eeNe"
        k, _r = P.reconcile(H, P._START, auth, pred, P._MS)
        direct = N1.first_desync(P._chain(DR.drive(H, P._START, pred, P._MS)),
                                 P._chain(DR.drive(H, P._START, auth, P._MS)))
        self.assertEqual(k, direct, "the tick must BE lockstep.first_desync, not a private reimplementation")

    def test_correct_prediction_no_rollback(self):
        H = P._heights(P._HF_SCENE)
        k, reusable = P.reconcile(H, P._START, "eeee", "eeee", P._MS)
        self.assertIsNone(k, "a correct prediction has no misprediction tick")
        self.assertEqual(len(reusable), 5, "a correct prediction keeps the full trajectory")
        self.assertEqual(P.replay(H, P._START, reusable, "eeee", P._MS), reusable, "replay is the identity")

    def test_pose_level_not_input_level(self):
        wall = ((0, 0, 9), (0, 0, 9))                              # east: cell 1 ok, cell 2 rise 9 → wall
        self.assertEqual(DR.drive(wall, (0, 0), "e", 4)[-1], DR.drive(wall, (0, 0), "E", 4)[-1],
                         "walk and blocked-sprint must reach the same pose")
        k, _r = P.reconcile(wall, (0, 0), "e", "E", 4)
        self.assertIsNone(k, "different inputs that yield the same poses need no rollback (pose-level)")

    def test_lazy_reconcile_defect_diverges(self):
        H = P._heights(P._HF_SCENE)
        auth, pred = "eeee", "eeNe"
        auth_traj = DR.drive(H, P._START, auth, P._MS)
        k, _r = P.reconcile(H, P._START, auth, pred, P._MS)
        lazy = tuple(DR.drive(H, P._START, pred, P._MS)[:k + 1])   # keep one mispredicted pose too many
        self.assertNotEqual(P.replay(H, P._START, lazy, auth, P._MS), auth_traj,
                            "over-claiming the reusable prefix must make the replay diverge (non-vacuity)")

    def test_typed_refusals(self):
        H = P._heights(P._HF_SCENE)
        for auth, pred in (("ee", "eee"), ("", ""), ("eXe", "eee")):
            with self.assertRaises(P.PredError) as cm:
                P.reconcile(H, P._START, auth, pred, P._MS)
            self.assertEqual(cm.exception.code, "PRED-REFUSE", f"wrong code for {(auth, pred)!r}")


if __name__ == "__main__":
    unittest.main()
