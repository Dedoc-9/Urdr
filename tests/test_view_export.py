# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for D15 — the view-export contract (layer 2: authority → renderer).

The bridge between the authoritative simulation and ANY presentation renderer
(three.js, Unreal, Godot, a Vulkan renderer, Blender). A view frame is derived from
the authoritative frame plus declared static scene metadata, and it CARRIES the
authoritative witness — so the view is bound to, and subordinate to, the authority it
depicts. The load-bearing invariant, made falsifiable:

    PRESENTATION OUTPUTS ARE OBSERVATIONAL ONLY. Any gameplay-affecting data must
    enter the authority layer as explicit inputs or be deterministically recomputed
    within it.

Pinned laws:
  * deterministic: the same (authoritative frame, scene) → the same view digest, and
    it matches a pinned golden (cross-host reproducible export);
  * BINDING: a view frame's `witness` equals the authoritative frame's digest — the
    view can never outrun or misrepresent the authority it claims to depict;
  * OBSERVATIONAL-ONLY: changing a PRESENTATION field (a material id) changes the
    VIEW digest (presentation is visible in the view) but leaves the carried witness
    UNCHANGED (presentation cannot touch authority);
  * NON-VACUITY: a defect exporter that folds a presentation field INTO the witness is
    detectable — the invariant is real, not incidental;
  * VIEW-REFUSE: a scene that depicts a different body count than the authoritative
    frame is refused, never fabricated."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "frontend")
if _p not in sys.path:
    sys.path.insert(0, _p)

import view_export as VE                                   # noqa: E402


def _auth():
    # a minimal AUTHORITATIVE frame: its witness digest + integer body positions (the
    # state the witness commits to) + a tick.
    return {"digest": "a" * 64, "tick": 5,
            "bodies": [{"x": 100, "y": 200}, {"x": 300, "y": 150}]}


def _scene(mat0="steel"):
    return {"bodies": [{"obj": "veh", "material": mat0}, {"obj": "veh", "material": "steel"}],
            "lights": [{"kind": "sun", "dir": [0, -1, 0]}],
            "cameras": [{"pos": [0, 60, -240], "yaw": 0}]}


def _golden():
    path = os.path.join(_ROOT, "tools", "frontend", "conformance_view.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                if name == "canonical":
                    return dig
    raise AssertionError("golden canonical missing")


class ViewExport(unittest.TestCase):
    def test_deterministic_and_pinned(self):
        d1 = VE.view_digest(VE.view_frame(_auth(), _scene()))
        d2 = VE.view_digest(VE.view_frame(_auth(), _scene()))
        self.assertEqual(d1, d2, "view export is nondeterministic")
        self.assertEqual(d1, _golden(), "view digest drifted from its pinned golden")

    def test_view_is_bound_to_authority(self):
        vf = VE.view_frame(_auth(), _scene())
        self.assertEqual(vf["witness"], _auth()["digest"],
                         "the view frame does not carry the authoritative witness")
        self.assertTrue(VE.verify_binding(vf, _auth()))
        # a view claiming a different authoritative frame fails the binding
        other = dict(_auth()); other["digest"] = "b" * 64
        self.assertFalse(VE.verify_binding(vf, other))

    def test_observational_only(self):
        """Changing a material changes the VIEW but never the carried witness."""
        vf_a = VE.view_frame(_auth(), _scene("steel"))
        vf_b = VE.view_frame(_auth(), _scene("chrome"))
        self.assertNotEqual(VE.view_digest(vf_a), VE.view_digest(vf_b),
                            "a material change was invisible to the view (presentation not observable)")
        self.assertEqual(vf_a["witness"], vf_b["witness"],
                         "a presentation change moved the authoritative witness — authority touched")

    def test_defect_folds_presentation_into_witness(self):
        """Non-vacuity: the defect exporter mixes material into the witness, so a
        presentation change DOES move its (fake) witness — the invariant is checkable."""
        wa = VE.view_frame_defect_fold_material(_auth(), _scene("steel"))["witness"]
        wb = VE.view_frame_defect_fold_material(_auth(), _scene("chrome"))["witness"]
        self.assertNotEqual(wa, wb,
                            "the defect did not leak presentation into the witness — probe vacuous")
        # and the real witness is exactly the authority digest, unlike the defect
        self.assertEqual(VE.view_frame(_auth(), _scene())["witness"], _auth()["digest"])

    def test_body_count_mismatch_refused(self):
        scene = _scene()
        scene["bodies"] = scene["bodies"][:1]              # depicts fewer bodies than authority has
        with self.assertRaises(VE.ViewError) as ctx:
            VE.view_frame(_auth(), scene)
        self.assertEqual(ctx.exception.code, "VIEW-REFUSE")

    def test_transform_read_from_authority_not_scene(self):
        """Body transforms come from the authoritative frame, not the scene — a scene
        cannot relocate a body the authority placed."""
        vf = VE.view_frame(_auth(), _scene())
        xs = [(b["x"], b["y"]) for b in vf["bodies"]]
        self.assertEqual(xs, [(100, 200), (300, 150)])


if __name__ == "__main__":
    unittest.main()
