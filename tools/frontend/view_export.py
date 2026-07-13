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

GRADE: MEASURED for the contract's checkable core (`view_export` gate stage,
`tests/test_view_export.py`). The contract freezes once an INDEPENDENT consumer (the
three.js viewer, `view_viewer.html`) reproduces the exported state — its viewDigest is
confirmed byte-identical to this reference in node. Renderer quality is out of scope —
this layer says WHAT to draw, never how well.
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
    moves — exactly the authority-contamination the observational-only invariant forbids."""
    vf = view_frame(auth, scene)
    mat = scene["bodies"][0].get("material", "") if scene.get("bodies") else ""
    vf["witness"] = hashlib.sha256((auth["digest"] + "|" + mat).encode("utf-8")).hexdigest()
    return vf


def export(replay, scene, frame_index):
    """A URDR-VIEW-1 frame from a URDR-REPLAY-1 doc's frame (recorded positions)."""
    fr = replay["frames"][frame_index]
    balls = fr.get("balls") or fr.get("raw") or []
    auth = {"digest": fr["digest"], "tick": frame_index,
            "bodies": [{"x": _i(round(b["x"])), "y": _i(round(b["y"]))} for b in balls]}
    return view_frame(auth, scene)


VIEW_VERSION = "1"


def export_doc(auth_frames, scene, view_version=VIEW_VERSION):
    """A viewer-loadable URDR-VIEW-1 document: every frame annotated with its own
    `view_digest`, so an INDEPENDENT consumer (the three.js viewer) recomputes and
    verifies each frame — reproducing the exported state, the D15 placement claim."""
    frames = []
    for af in auth_frames:
        vf = view_frame(af, scene)
        vf["view_digest"] = view_digest(vf)
        frames.append(vf)
    return {"format": "URDR-VIEW-1", "view_version": view_version,
            "count": len(frames), "frames": frames}


def doc_from_replay(replay, scene=None):
    """Build a viewer document from a URDR-REPLAY-1 doc. Body transforms are the
    recorded (authoritative) positions; the scene supplies presentation metadata."""
    frames = replay.get("frames", [])
    n = len(frames[0].get("balls") or frames[0].get("raw") or []) if frames else 0
    if scene is None:
        pal = ["steel", "chrome", "rubber", "glass", "brass", "matte"]
        scene = {"bodies": [{"obj": "body%d" % i, "material": pal[i % len(pal)]} for i in range(n)],
                 "lights": [{"kind": "sun", "dir": [0, -1, 0]}],
                 "cameras": [{"pos": [0, 60, -240], "yaw": 0}]}
    auth_frames = []
    for k, fr in enumerate(frames):
        balls = fr.get("balls") or fr.get("raw") or []
        auth_frames.append({"digest": fr["digest"], "tick": k,
                            "bodies": [{"x": _i(round(b["x"])), "y": _i(round(b["y"]))} for b in balls]})
    return export_doc(auth_frames, scene)


def main(argv):
    if len(argv) < 2:
        print("usage: view_export.py replay.json [out.json]   (writes a URDR-VIEW-1 viewer doc)")
        print("       view_export.py replay.json --frame K     (prints one frame's digest)")
        return 2
    import json
    with open(argv[1], "r", encoding="utf-8") as fh:
        replay = json.load(fh)
    if "--frame" in argv:
        idx = int(argv[argv.index("--frame") + 1])
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
        return 0
    out = argv[2] if len(argv) > 2 and not argv[2].startswith("--") else \
        os.path.splitext(argv[1])[0] + "_view.json"
    doc = doc_from_replay(replay)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    print("URDR-VIEW-1 doc   :", doc["count"], "frames · view_version", doc["view_version"])
    if doc["frames"]:
        print("frame 0 witness   :", doc["frames"][0]["witness"][:20], "…")
        print("frame 0 view dig  :", doc["frames"][0]["view_digest"][:20], "…")
    print("wrote             :", out, "(open in view_viewer.html)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
