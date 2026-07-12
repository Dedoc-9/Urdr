# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Falsifiers for the editor→exact-render seam — the consumer-side smoke test.

The last unwatched seam in the authoring pipeline: a canonical URDR-WORLD-3 export
(demo/world_highway.json) rendered through `load_world.render` — float authoring
snapped to integers, then the EXACT floor-division perspective projector — into a
URDRFB1 framebuffer whose digest is pinned (tools/editor/conformance_editor.txt).

Why the golden is solid ground: the canonical scene carries NO rotations, so scene
composition is IEEE-double add/multiply/round only (bit-deterministic on every
conforming platform), and everything after the integer snap is the cross-placed
exact projector. `change is cheap; a certified transition is the scarce resource` —
this pin makes the editor→render transition certified in miniature.

Non-vacuity: moving one instance and perturbing one vertex must each change the
digest — the pin is load-bearing, not decorative. Honest scope: this certifies the
PIPELINE on the canonical export; the browser editor itself remains SPECULATIVE."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_p = os.path.join(_ROOT, "tools", "editor")
if _p not in sys.path:
    sys.path.insert(0, _p)

import load_world as LW                                    # noqa: E402

_HIGHWAY = os.path.join(_ROOT, "demo", "world_highway.json")


def _doc():
    with open(_HIGHWAY, encoding="utf-8") as fh:
        return json.load(fh)


def _golden():
    path = os.path.join(_ROOT, "tools", "editor", "conformance_editor.txt")
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                name, dig = ln.split()
                if name == "highway_frame":
                    return dig
    raise AssertionError("golden highway_frame missing")


class EditorRenderSeam(unittest.TestCase):
    def test_highway_frame_reproduces_golden_twice(self):
        """The canonical export renders to its pinned URDRFB1 digest, twice."""
        d1 = LW.render(_doc()).digest()
        d2 = LW.render(_doc()).digest()
        self.assertEqual(d1, d2, "NONDETERMINISTIC — the seam is not solid ground")
        self.assertEqual(d1, _golden(), "frame digest drifted from the pinned golden")

    def test_moved_instance_diverges(self):
        """Moving the median must change the frame — the pin sees the scene."""
        doc = _doc()
        for i in doc["instances"]:
            if i.get("body") == "static":
                i["ground_x"] += 40
        self.assertNotEqual(LW.render(doc).digest(), _golden(),
                            "a moved instance left the digest unchanged (pin vacuous)")

    def test_vertex_perturbation_diverges(self):
        """Perturbing one object vertex must change the frame — geometry is content."""
        doc = _doc()
        doc["objects"][0]["verts"][0][0] += 2
        self.assertNotEqual(LW.render(doc).digest(), _golden(),
                            "a perturbed vertex left the digest unchanged (pin vacuous)")


if __name__ == "__main__":
    unittest.main()
