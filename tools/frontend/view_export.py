#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""view_export — the D15 view-export contract (layer 2: authority → any renderer).

Three layers, one-way: Authority (Urðr, the unique contribution) → View contract
(this bridge) → Presentation renderer (replaceable — three.js, Unreal, Godot, Vulkan,
Blender). A `URDR-VIEW-1` frame is derived from the authoritative frame plus declared
static scene metadata, and it CARRIES the authoritative witness, so the view is bound
to — and subordinate to — the authority it depicts.

THE LOAD-BEARING INVARIANT (D15, normative):

    Presentation outputs are OBSERVATIONAL ONLY. Any gameplay-affecting data must
    enter the authority layer as explicit inputs or be deterministically recomputed
    within it.

Made falsifiable here: a presentation field (material, light, camera) moves the VIEW
digest (presentation is visible to renderers) but NEVER the carried `witness` — the
authoritative digest is a function of authoritative state alone. Body transforms are
READ from the authoritative frame; a scene cannot relocate a body the authority
placed, nor depict a body count the authority does not have (`VIEW-REFUSE`).

What a view frame exposes per frame (extensible; presentation-only):
  witness    the authoritative frame's digest (binds the view to its authority)
  tick       the replay timestamp
  bodies     [{obj: canonical URDROBJ2 id, material: id, x, y}]  (transform from authority)
  lights     declared scene lights   (authoring data — presentation)
  cameras    declared scene cameras  (authoring data — presentation)
  contacts   optional debug witnesses, read from the frame (observational)

GRADE: MEASURED for the contract's checkable core (`view_export` gate stage,
`tests/test_view_export.py`) — deterministic export to a pinned golden, the binding,
the observational-only invariant, its non-vacuity defect, and the refusal. The
contract is NOT yet frozen: per the admission ladder it freezes once an INDEPENDENT
consumer (a three.js reference viewer) reproduces the exported state. Renderer quality
is out of scope — this layer says WHAT to draw, never how well.
"""
import hashlib
import os
import sys


class ViewError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _i(v):
    return int(v)


def view_frame(auth, scene):
    """Build a URDR-VIEW-1 frame from an authoritative frame + a scene. Transforms come
    from `auth`; obj/material/lights/cameras from `scene` (presentation). Refuses a
    scene whose body count differs from the authoritative frame."""
    abodies = auth["bodies"]
    sbodies = scene.get("bodies", [])
    if len(sbodies) != len(abodies):
        raise ViewError("VIEW-REFUSE",
                        f"scene depicts {len(sbodies)} bodies but the authoritative frame "
                        f"has {len(abodies)} — a view cannot add or omit authority")
    bodies = []
    for a, s in zip(abodies, sbodies):
        bodies.append({"obj": s.get("obj", ""), "material": s.get("material", ""),
                       "x": _i(a["x"]), "y": _i(a["y"])})
    return {"format": "URDR-VIEW-1",
            "witness": auth["digest"],                      # bound to authority
            "tick": _i(auth.get("tick", 0)),
            "bodies": bodies,
            "lights": scene.get("lights", []),
            "cameras": scene.get("cameras", [])}


def _canon(vf):
    """Canonical serialization of a view frame — presentation INCLUDED, so a material
    change is visible in the view digest. The witness is included as itself (a bound
    reference), never recomputed from presentation."""
    import json
    parts = ["URDR-VIEW-1", "w" + vf["witness"], "t%d" % vf["tick"], "b%d" % len(vf["bodies"])]
    for b in vf["bodies"]:
        parts.append("%s,%s,%d,%d" % (b["obj"], b["material"], b["x"], b["y"]))
    parts.append("L" + json.dumps(vf["lights"], sort_keys=True, separators=(",", ":")))
    parts.append("C" + json.dumps(vf["cameras"], sort_keys=True, separators=(",", ":")))
    return "|".join(parts)


def view_digest(vf):
    """SHA-256 over the canonical view serialization — moves when presentation moves."""
    return hashlib.sha256(_canon(vf).encode("utf-8")).hexdigest()


def verify_binding(vf, auth):
    """The view is subordinate: its witness must equal the authoritative frame's digest.
    A renderer can check this to refuse depicting a frame it isn't bound to."""
    return vf.get("witness") == auth.get("digest")


def view_frame_defect_fold_material(auth, scene):
    """THE DEFECT (gate non-vacuity): an exporter that folds a presentation field (the
    first body's material) INTO the witness. Its `witness` then MOVES when material
    moves — exactly the authority-contamination the observational-only invariant forbids.
    Must be detectably different from the real (invariant) witness."""
    vf = view_frame(auth, scene)
    mat = scene["bodies"][0].get("material", "") if scene.get("bodies") else ""
    vf["witness"] = hashlib.sha256((auth["digest"] + "|" + mat).encode("utf-8")).hexdigest()
    return vf


def export(replay, scene, frame_index):
    """Convenience: a URDR-VIEW-1 frame from a URDR-REPLAY-1 doc's frame. Reads the
    recorded (authoritative) body positions; the browser draws them, never simulates."""
    fr = replay["frames"][frame_index]
    balls = fr.get("balls") or fr.get("raw") or []
    auth = {"digest": fr["digest"], "tick": frame_index,
            "bodies": [{"x": _i(round(b["x"])), "y": _i(round(b["y"]))} for b in balls]}
    return view_frame(auth, scene)


def main(argv):
    if len(argv) < 2:
        print("usage: view_export.py replay.json [frame_index]  (prints a URDR-VIEW-1 frame + digest)")
        return 2
    import json
    with open(argv[1], "r", encoding="utf-8") as fh:
        replay = json.load(fh)
    idx = int(argv[2]) if len(argv) > 2 else 0
    n = len(replay["frames"][idx].get("balls") or replay["frames"][idx].get("raw") or [])
    scene = {"bodies": [{"obj": "body%d" % i, "material": "default"} for i in range(n)],
             "lights": [{"kind": "sun"}], "cameras": [{"pos": [0, 60, -240]}]}
    try:
        vf = export(replay, scene, idx)
    except ViewError as e:
        print("REFUSED:", e)
        return 1
    print("URDR-VIEW-1 frame", idx, "· witness", vf["witness"][:20], "…")
    print("view digest       :", view_digest(vf))
    print("bound to authority:", verify_binding(vf, {"digest": replay["frames"][idx]["digest"]}))
    print("bodies            :", len(vf["bodies"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
