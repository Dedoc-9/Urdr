# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the MEASURED first-person observer (`tools/terrain/gaze.py`, T3.10) — a view of the
walking actor is admitted iff it reconstructs to the current authoritative pose, else refused.

  * REFERENCE — the four pinned scenes reproduce their URDRGAZE1 verdict digests ×2;
  * ADMIT (non-vacuity) — the genuine covering frame OF THE CURRENT pose is ADMITTED, so the refusals
    below are caused by the fault, not a broken admitter;
  * NON-COVERING — a frame that omits a pose axis is REFUSED (GAZE-NONCOVER): it cannot pin the state;
  * LAUNDERING — a covering frame carrying a *substituted* (fabricated) pose is REFUSED (GAZE-LAUNDER);
  * REPLAY / STALENESS — a once-valid frame replayed after the authority advances is REFUSED; the SAME
    frame ADMITS at its own authority and REFUSES at the advanced one (the anchor is the CURRENT pose);
  * RECONSTRUCT — a covering atlas reconstructs the pose EXACTLY (the observability property);
  * MEMBRANE — `admit` never mutates the authority (pose + anchor) or the frame — presentation cannot
    feed the authority;
  * LOAD-BEARING — an admitter that skips the digest check would LAUNDER the forged frame (so the check
    is the thing that reddens);
  * NO-DIVISION — the source has no `/`, `//`, `%` operator (cross-placement is structural)."""
import copy
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "terrain")
if _p not in sys.path:
    sys.path.insert(0, _p)

import unittest
import gaze as G                                                  # noqa: E402


class Gaze(unittest.TestCase):
    def test_scene_goldens(self):
        for name in G.SCENES:
            v, c, d = G.scene_verdict(name)
            self.assertEqual(d, G.golden(name), f"{name}: verdict digest drifted")
            self.assertEqual(G.scene_verdict(name)[2], d, f"{name}: nondeterministic")

    def test_genuine_admits(self):                                # non-vacuity control
        v, c, _d = G.scene_verdict("genuine")
        self.assertEqual((v, c), ("ADMIT", "GAZE-OK"), "the genuine covering frame must be admitted")

    def test_noncovering_refused(self):
        v, c, _d = G.scene_verdict("noncover")
        self.assertEqual((v, c), ("REFUSE", "GAZE-NONCOVER"), "a non-covering frame must be refused")

    def test_forged_substitution_refused(self):
        v, c, _d = G.scene_verdict("forged")
        self.assertEqual((v, c), ("REFUSE", "GAZE-LAUNDER"), "a substituted pose must be refused")

    def test_replay_refused_and_flips(self):
        # a once-valid frame replayed after the authority advances is refused; the SAME frame admits at
        # its own authority — pinning that the anchor is the CURRENT pose (replay caught by construction).
        t = G.trajectory("ridge_clear")
        j, k = 3, 8
        self.assertNotEqual(t[j], t[k], "the two poses must differ for the replay to be meaningful")
        frame = G.full_atlas().image(t[j])
        self.assertEqual(G.admit(G.Authority(t[j]), G.full_atlas(), frame)[0], "ADMIT", "valid at its own tick")
        self.assertEqual(G.admit(G.Authority(t[k]), G.full_atlas(), frame), ("REFUSE", "GAZE-LAUNDER"),
                         "the stale frame must be refused after the authority advances")
        self.assertEqual(G.scene_verdict("stale")[:2], ("REFUSE", "GAZE-LAUNDER"))

    def test_covering_atlas_reconstructs_exactly(self):
        t = G.trajectory("ridge_clear")
        for pose in (t[0], t[5], t[8]):
            recon = G.full_atlas().recon(G.full_atlas().image(pose), G.POSE_N)
            self.assertEqual(recon, pose, "a covering atlas must reconstruct the pose exactly")
        # a non-covering atlas cannot reconstruct (returns None)
        self.assertIsNone(G.blind_atlas().recon(G.blind_atlas().image(t[8]), G.POSE_N))

    def test_membrane_admit_is_pure(self):
        t = G.trajectory("ridge_clear")
        a = G.Authority(t[8])
        before = (a.pose, a.anchor)
        for atlas, im in [(G.full_atlas(), G.full_atlas().image(t[8])),      # ADMIT
                          (G.blind_atlas(), G.blind_atlas().image(t[8])),    # REFUSE non-cover
                          (G.full_atlas(), G.full_atlas().image(t[3]))]:     # REFUSE launder
            snap = copy.deepcopy(im)
            G.admit(a, atlas, im)
            self.assertEqual((a.pose, a.anchor), before, "admit mutated the authority (membrane leak)")
            self.assertEqual(im, snap, "admit mutated the frame")

    def test_digest_check_is_load_bearing(self):
        # an admitter that reconstructs but SKIPS the digest comparison would admit the forged frame;
        # the real admit refuses it — so the digest check is the load-bearing gate (it can redden).
        a, atlas, image = G.forged()
        self.assertEqual(G.admit(a, atlas, image)[0], "REFUSE", "real admit must refuse the forgery")
        covers = atlas.covers(G.POSE_N) and atlas.recon(image, G.POSE_N) is not None
        would_admit_without_digest = covers                       # the only thing left is the digest check
        self.assertTrue(would_admit_without_digest, "the forged frame is covering + reconstructable — "
                        "only the digest check refuses it, so that check is load-bearing")

    def test_typed_refusal_on_bad_pose(self):
        with self.assertRaises(G.GazeError) as cm:
            G.Authority((1, 2, 3))                                # wrong arity
        self.assertEqual(cm.exception.code, "GAZE-REFUSE")
        with self.assertRaises(G.GazeError) as cm:
            G.Authority((1, 2, 3, True))                          # bool axis
        self.assertEqual(cm.exception.code, "GAZE-REFUSE")

    def test_no_division_operators(self):
        import tokenize
        forbidden = {"/", "//", "%", "/=", "//=", "%="}
        bad = []
        with open(G.__file__, "rb") as fh:
            for tok in tokenize.tokenize(fh.readline):
                if tok.type == tokenize.OP and tok.string in forbidden:
                    bad.append((tok.start, tok.string))
        self.assertEqual(bad, [], f"division/modulo operators found in gaze.py: {bad}")


if __name__ == "__main__":
    unittest.main()
