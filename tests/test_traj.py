# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED trajectory observer (`tools/terrain/traj.py`, T3.12) — a *sequence* of
partial views is admitted iff every frame reconstructs to the pose the exact-integer dynamics predict
at that tick (innovation ν = y − H·Φ·x̂ is the zero vector), else refused.

  * REFERENCE — the four pinned witnesses reproduce their URDRTRAJ1 digests ×2;
  * DETERMINISM — re-observing the same (inputs, witness) reproduces the verdict bit-for-bit;
  * RECONSTRUCTION — the observer's reconstruction is exactly `drive.drive` (the Φ-fold of the inputs);
  * PARTIAL COVERAGE — position-only frames (non-covering) are ADMITTED by the horizon observer while
    `gaze` REFUSES each of them (`GAZE-NONCOVER`) — the observability the snapshot cannot express;
  * FACING FROM MOTION — facing is recovered from the position delta when the actor moves, and is
    honestly None when it is BLOCKED (the stationary `does_not_show`);
  * REPLAY — a covering frame replayed at the wrong tick is REFUSED even though every frame is
    content-valid (a pose the actor genuinely holds) — the same-where-different-WHEN gap gaze deferred;
  * TELEPORT — an unreachable pose is REFUSED (and, unlike replay, is content-INVALID: caught by both);
  * INNOVATION — ν is a real exact residual (zero on a match, nonzero on a forgery), not a boolean;
  * TAMPER-EVIDENCE — a forged / replayed / reordered frame moves the URDRTRAJ1 digest;
  * REFUSAL — bad dynamics inputs and a malformed witness are typed `TRAJ-REFUSE`;
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import traj as T                                                  # noqa: E402
import gaze as GZ                                                 # noqa: E402
import drive as DR                                                # noqa: E402


def _traj():
    return DR.drive(T._heights(T._HF_SCENE), T._START, T._CMDS, T._MS)


class Traj(unittest.TestCase):
    def test_scene_goldens(self):
        for name in T.SCENES:
            _v, _c, dig = T.scene_result(name)
            self.assertEqual(dig, T.golden(name), f"{name}: verdict digest drifted")
            self.assertEqual(T.scene_result(name)[2], dig, f"{name}: nondeterministic")

    def test_determinism_replay(self):
        hf, start, cmds, ms, frames = T.honest_full()
        H = T._heights(hf)
        self.assertEqual(T.observe(H, start, cmds, ms, frames),
                         T.observe(H, start, cmds, ms, frames),
                         "re-observing the same witness must reproduce the verdict")

    def test_reconstruction_is_drive_fold(self):
        H = T._heights(T._HF_SCENE)
        self.assertEqual(T.reconstruct(H, T._START, T._CMDS, T._MS),
                         DR.drive(H, T._START, T._CMDS, T._MS),
                         "the observer's reconstruction must be exactly the Φ-fold drive.drive")

    def test_partial_coverage_admitted_but_gaze_refuses(self):
        hf, start, cmds, ms, frames = T.honest_partial()
        H = T._heights(hf)
        traj = _traj()
        self.assertEqual(T.observe(H, start, cmds, ms, frames), ("ADMIT", "TRAJ-OK"),
                         "position-only honest frames must be admitted over the horizon")
        for k, (axes, image) in enumerate(frames):
            self.assertFalse(T.covers(axes), "the position-only atlas must be non-covering")
            verdict, code = GZ.admit(GZ.Authority(traj[k]), T._atlas(axes), image)
            self.assertEqual((verdict, code), ("REFUSE", "GAZE-NONCOVER"),
                             "snapshot gaze must refuse each non-covering frame the horizon admits")

    def test_facing_observable_from_motion(self):
        traj = _traj()
        for k in range(1, len(traj)):
            self.assertEqual(T.facing_from_motion(traj[k - 1][:2], traj[k][:2]), traj[k][3],
                             "facing must be recoverable from the position delta when the actor moves")

    def test_facing_unobservable_when_blocked(self):
        blocked = ((0, 0), (0, 9))                                # (0,1)->(1,1) rise 9 > max_step: stays put
        bt = DR.drive(blocked, (0, 1), "e", 4)
        self.assertEqual(bt[0][:2], bt[1][:2], "the blocked actor must stay put")
        self.assertIsNone(T.facing_from_motion(bt[0][:2], bt[1][:2]),
                          "facing is NOT observable from a stationary step (the does_not_show)")

    def test_replay_refused_though_content_valid(self):
        hf, start, cmds, ms, frames = T.replay()
        H = T._heights(hf)
        traj = _traj()
        self.assertTrue(all(T.content_valid(a, i, traj) for a, i in frames),
                        "every replay frame must be content-valid (a pose the actor genuinely holds)")
        self.assertEqual(T.observe(H, start, cmds, ms, frames), ("REFUSE", "TRAJ-INNOVATE"),
                         "a content-valid frame at the WRONG tick must still be refused")

    def test_teleport_refused_and_content_invalid(self):
        hf, start, cmds, ms, frames = T.teleport()
        H = T._heights(hf)
        traj = _traj()
        self.assertFalse(T.content_valid(frames[2][0], frames[2][1], traj),
                         "the teleport pose must be content-INVALID (unlike replay)")
        self.assertEqual(T.observe(H, start, cmds, ms, frames), ("REFUSE", "TRAJ-INNOVATE"),
                         "an unreachable pose must be refused")

    def test_innovation_is_exact_residual(self):
        traj = _traj()
        honest = T._project(traj[1], (0, 1, 2, 3))
        self.assertEqual(T.innovation(honest, honest), (0, 0, 0, 0), "ν must be zero on a match")
        nu = T.innovation(T._project(traj[0], (0, 1, 2, 3)), T._project(traj[2], (0, 1, 2, 3)))
        self.assertTrue(any(v != 0 for v in nu), "ν must be a nonzero residual when past≠future")
        self.assertEqual(len(nu), 4, "ν is one component per observed axis")

    def test_tamper_evidence(self):
        traj = _traj()
        frames = tuple(T.frame_of(traj[k], (0, 1, 2, 3)) for k in range(len(traj)))
        base = T.traj_digest("w", "ADMIT", "TRAJ-OK", frames)
        reordered = T.traj_digest("w", "ADMIT", "TRAJ-OK", frames[:1] + frames[2:3] + frames[1:2] + frames[3:])
        forged = T.traj_digest("w", "ADMIT", "TRAJ-OK", (T.frame_of(traj[1], (0, 1, 2, 3)),) + frames[1:])
        self.assertNotEqual(base, reordered, "reordering frames must move the transcript digest")
        self.assertNotEqual(base, forged, "forging frame 0 (pose[0]→pose[1]) must move the transcript digest")

    def test_typed_refusals_total(self):
        H = T._heights(T._HF_SCENE)
        good = tuple(T.frame_of(p, (0, 1, 2, 3)) for p in _traj())
        cases = [
            (H, (-1, 0), "eeee", 16, good),                       # off-grid start (dynamics reject)
            (H, T._START, "", 16, good),                          # empty input log
            (H, T._START, "eeee", -1, good),                      # negative max_step
            (H, T._START, "eeee", 16, good[:-1]),                 # witness too short
            (H, T._START, "eeee", 16, good[:-1] + ((( 0, 1), (1, True)),)),  # bool in image
            (H, T._START, "eeee", 16, good[:-1] + (((0, 9), (1, 2)),)),      # axis out of range
        ]
        for args in cases:
            with self.assertRaises(T.TrajError) as cm:
                T.observe(*args)
            self.assertEqual(cm.exception.code, "TRAJ-REFUSE", f"wrong code for {args[1:4]!r}")

    def test_no_division_operators(self):
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(T.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in traj.py: {bad}")


if __name__ == "__main__":
    unittest.main()
