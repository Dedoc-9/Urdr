# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the KERNEL CROSS-CHECK (T3.13) — the terrain-local observers (`gaze`, `traj`) run the
SAME admit-or-refuse law the kernel `tools/world_host` runs on the kernel's own content digest.

The terrain observers carry a terrain-local canon (URDRGAZE1/URDRTRAJ1 over a hashlib SHA-256) so they
are standalone; `world_host` anchors on `urdr.canon.digest` — the very digest the reference kernel and
the `urdr-core-rs` Rust placement already agree on (D8 conformance). This suite proves the terrain law
is NOT a divergent reimplementation: on every scene the terrain verdict equals the kernel verdict, over
DIFFERENT content-addressing — so `gaze`/`traj` are kernel-verified, not merely terrain-verified.

  * GAZE ≡ KERNEL — the four gaze scenes (genuine/noncover/forged/stale) get the same ADMIT/REFUSE from
    `world_host.admit` as from `gaze.admit`;
  * TRAJ ≡ KERNEL on covering frames — every covering frame of a traj witness gets the same verdict from
    the kernel snapshot as traj's own innovation (image == the pose the dynamics predict there);
  * TRAJ EXTENDS KERNEL — a non-covering (position-only) witness is ADMITTED by the horizon observer while
    the kernel snapshot REFUSES every frame (`non-covering`): an extension of the law, not a divergence;
  * DIFFERENT BYTES, SAME VERDICT — the terrain digest ≠ the kernel digest for the same pose, yet the
    verdict is identical: the shared object is the LAW, not the canonical bytes;
  * ANCHOR BINDING LOAD-BEARING — on the kernel side too, the same frame ADMITS against its own anchor and
    REFUSES against a shifted one (the digest binding is what refuses laundering — non-vacuity);
  * COVERING LAW ≡ — the kernel's covering/injectivity test agrees with the terrain one, chart-for-chart.

Requires the `urdr` kernel package (world_host imports `urdr.canon`); skipped nowhere — the gate always
runs with the kernel present."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "tools", "terrain"), os.path.join(_ROOT, "tools", "world_host")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unittest
import gaze as GZ                                                  # noqa: E402
import traj as TR                                                 # noqa: E402
import drive as DR                                                # noqa: E402
import world_host as WH                                           # noqa: E402  (imports urdr.canon)


def _kernel_verdict(pose, axes_list, image):
    """The kernel world_host's verdict on a frame: build the same axis-selection atlas over the kernel
    state = the pose vector, anchored on urdr.canon.digest. Returns 'ADMIT' | 'REFUSE'."""
    host = WH.WorldHost(list(pose))
    atlas = WH.Atlas([WH.Chart(list(ax)) for ax in axes_list])
    return host.admit(atlas, list(image))[0]


def _terrain_traj():
    return DR.drive(TR._heights(TR._HF_SCENE), TR._START, TR._CMDS, TR._MS)


class KernelCrossCheck(unittest.TestCase):
    def test_gaze_agrees_with_kernel(self):
        for name in GZ.SCENES:
            authority, atlas, image = GZ.SCENES[name]()
            terrain = GZ.admit(authority, atlas, image)[0]
            kernel = _kernel_verdict(authority.pose, [ch.axes for ch in atlas.charts], image)
            self.assertEqual(terrain, kernel, f"gaze scene {name}: terrain {terrain} != kernel {kernel}")

    def test_traj_covering_frames_agree_with_kernel(self):
        true = _terrain_traj()
        for scene in ("honest_full", "replay", "teleport"):
            _hf, _s, _c, _m, frames = TR.SCENES[scene]()
            for k, (axes, image) in enumerate(frames):
                if not TR.covers(axes):
                    continue                                       # non-covering handled separately
                traj_v = "ADMIT" if tuple(image) == tuple(true[k][i] for i in axes) else "REFUSE"
                kernel_v = _kernel_verdict(true[k], [axes], image)
                self.assertEqual(traj_v, kernel_v,
                                 f"{scene} frame {k}: traj {traj_v} != kernel {kernel_v}")

    def test_traj_extends_kernel_on_noncovering(self):
        true = _terrain_traj()
        frames = TR.honest_partial()[4]
        seq = TR.observe(TR._heights(TR._HF_SCENE), TR._START, TR._CMDS, TR._MS, frames)[0]
        self.assertEqual(seq, "ADMIT", "the horizon observer must admit the honest position-only sequence")
        kernel = {_kernel_verdict(true[k], [axes], image) for k, (axes, image) in enumerate(frames)}
        self.assertEqual(kernel, {"REFUSE"},
                         "the kernel SNAPSHOT must refuse every non-covering frame (traj extends, not diverges)")

    def test_different_bytes_same_verdict(self):
        t = GZ.trajectory("ridge_clear")
        pose = t[8]
        terrain_digest = GZ.pose_digest(pose)                     # URDRGAZE1 hashlib hex
        kernel_digest = WH.digest(list(pose)).hex()               # urdr.canon -> SHA-256, as hex
        self.assertNotEqual(terrain_digest, kernel_digest, "the two content-addressings must differ")
        # ...yet the verdict on the same honest covering frame is identical (ADMIT)
        image = [pose[i] for i in (0, 1, 2, 3)]
        terrain_v = GZ.admit(GZ.Authority(pose), GZ.full_atlas(), image)[0]
        self.assertEqual(terrain_v, _kernel_verdict(pose, [(0, 1, 2, 3)], image),
                         "different bytes, same verdict: the shared object is the law, not the digest")

    def test_kernel_anchor_binding_load_bearing(self):
        t = GZ.trajectory("ridge_clear")
        pose = t[8]
        image = [pose[i] for i in (0, 1, 2, 3)]                   # honest covering frame of `pose`
        right = _kernel_verdict(pose, [(0, 1, 2, 3)], image)
        wrong = _kernel_verdict((pose[0] + 1,) + tuple(pose[1:]), [(0, 1, 2, 3)], image)  # anchor shifted
        self.assertEqual(right, "ADMIT", "the frame must admit against its own anchor")
        self.assertEqual(wrong, "REFUSE", "the SAME frame must refuse against a shifted anchor (binding bites)")

    def test_covering_law_agrees(self):
        # the kernel's covering/injectivity test agrees with the terrain one, chart-for-chart
        for axes in [(0, 1, 2, 3), (0, 1, 2), (0, 1), (3,), (0, 1, 3)]:
            terrain = GZ.Atlas([GZ.Chart(axes)]).covers(GZ.POSE_N)
            kernel = WH.Atlas([WH.Chart(list(axes))]).covers(GZ.POSE_N)
            self.assertEqual(terrain, kernel, f"covering disagreement on axes {axes}")


if __name__ == "__main__":
    unittest.main()
