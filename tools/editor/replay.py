#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Deterministic replay runtime — the engine is the sole authority; the editor only
draws what it records.

Runs the EXACT nD dynamics (`tools/physics/dynamics_nd.py` — the gated, cross-placed
physics) forward for N ticks and records, per tick, the canonical **state digest**
(`URDRPN1`) — a cryptographic witness of the exact `(X, V)` state, plus the exact
momentum and 2·KE invariants. The chain of digests IS the replay: frame k is restored
*by its digest*, bit-identical on every conforming host. Ball positions are carried as
decimals for DRAWING ONLY; the digest (not the decimals) is the authority.

Two modes:
  python3 replay.py [out.json]                 # built-in integer-exact demo cascade
  python3 replay.py --world urdr_world.json [out.json]
      simulate the AUTHORED scene: every `body:"dynamic"` instance in a URDR-WORLD-3
      export becomes an exact ball (position from ground_x/z, radius from the object's
      bounding box × scale, mass + initial velocity from the inspector). Static /
      kinematic instances are recorded as fixed markers (drawn, not simulated). The
      output `urdr_replay.json` loads unchanged in the editor's ▷ Replay mode.

Honest boundary: exact-ℚ iterated dynamics can overflow i64 (denominators grow after
collisions) — the documented substrate limit. When a step overflows, the runtime
records the frames up to that point and an honest `refused` marker — the exact engine
STOPS rather than approximate; the editor shows the refusal at the end of the timeline.
Current scope (declared, not yet simulated): static COLLIDERS (statics are drawn, not
collided against), constraints/joints, per-material restitution (a single global value
is used), gravity and walls. Those are later rungs. The browser never re-simulates.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics"))
from rational import Q, Z, RationalError                 # noqa: E402
from vecq import Vec                                     # noqa: E402
from dynamics_nd import Ball, step, state_digest, momentum, two_kinetic  # noqa: E402
from contact_lcp import Contact, delassus, solve_lcp, complementary, lcp_digest  # noqa: E402

DT, REST = Q(1), Q(1)          # tick length; global restitution (elastic)


def _f(q):
    return q.n / q.d           # decimal, for drawing ONLY (the digest is the authority)


def _ball(b):   # exact-state fields carried for DRAWING (position, radius, velocity, mass)
    return {"x": _f(b.x.c[0]), "y": _f(b.x.c[1]), "r": _f(b.r),
            "vx": _f(b.v.c[0]), "vy": _f(b.v.c[1]), "m": b.m}


def _snap(bodies, k, raw=False):
    p = momentum(bodies)
    d = {"frame": k, "digest": state_digest(bodies),
         "px": _f(p.c[0]), "py": _f(p.c[1]), "e2": _f(two_kinetic(bodies))}
    d["raw" if raw else "balls"] = [_ball(b) for b in bodies]
    return d


def _veq(a, b):
    return all(a.c[i] == b.c[i] for i in range(a.dim()))


def _contact(before, after, i, j):
    """A contact WITNESS derived from the engine's own before/after state (not recomputed
    physics): contact point on the touching surface, unit normal, and impulse magnitude
    |m·Δv| taken from the exact velocity change the engine applied."""
    c1, c2, r1, r2 = before[i].x, before[j].x, _f(before[i].r), _f(before[j].r)
    x1, y1, x2, y2 = _f(c1.c[0]), _f(c1.c[1]), _f(c2.c[0]), _f(c2.c[1])
    dx, dy = x2 - x1, y2 - y1
    L = (dx * dx + dy * dy) ** 0.5 or 1.0
    t = r1 / (r1 + r2) if (r1 + r2) else 0.5
    dvx = _f(after[i].v.c[0]) - _f(before[i].v.c[0]); dvy = _f(after[i].v.c[1]) - _f(before[i].v.c[1])
    imp = before[i].m * ((dvx * dvx + dvy * dvy) ** 0.5)
    return {"x": x1 + t * dx, "y": y1 + t * dy, "nx": dx / L, "ny": dy / L, "imp": imp, "i": i, "j": j}


def _simulate(bodies, steps, raw):
    frames, refused = [], None
    zero = [Vec([Z(0), Z(0)]) for _ in bodies]
    for k in range(steps + 1):
        snap = _snap(bodies, k, raw); frames.append(snap)
        try:
            nb = step(bodies, zero, DT, REST, ())
        except RationalError as e:                        # exact engine refuses to approximate
            refused = {"after_frame": k, "code": getattr(e, "code", "PHYS-REFUSE"), "message": str(e)}
            break
        ch = [i for i in range(len(bodies)) if not _veq(bodies[i].v, nb[i].v)]
        if len(ch) >= 2:                                  # a ball-ball contact resolved this step
            snap["contacts"] = [_contact(bodies, nb, ch[0], ch[1])]
        bodies = nb
    return frames, refused


# ---- built-in demo: a horizontal Newton's-cradle momentum-transfer cascade ---------
def cascade_doc(steps=72):
    YLINE, R, MASS = Q(120), Q(14), 1
    spec = [(40, 6), (150, 0), (214, 0), (278, 0)]        # (x, vx)
    bodies = [Ball(Vec([Q(x), YLINE]), R, Vec([Q(vx), Z(0)]), MASS) for (x, vx) in spec]
    frames, refused = _simulate(bodies, steps, raw=False)
    return {"format": "URDR-REPLAY-1", "w": 380, "h": 240, "rail": True, "statics": [],
            "note": "built-in demo — the digest per frame is the exact-state witness (URDRPN1)",
            "refused": refused, "frames": frames, "chain": [f["digest"] for f in frames]}


# ---- authored world: simulate a URDR-WORLD-3 export --------------------------------
def _load_world(path):
    with open(path, "r", encoding="utf-8") as fh:
        w = json.load(fh)
    objs = {o["digest"]: o for o in w.get("objects", [])}
    dyn, statics = [], []
    for inst in w.get("instances", []):
        o = objs.get(inst.get("object"))
        if not o or not o.get("verts"):
            continue
        xs = [v[0] for v in o["verts"]]
        ys = [v[1] for v in o["verts"]]
        sc = inst.get("scale", 1.0) or 1.0
        r = max(1, int(round(0.5 * max(max(xs) - min(xs), max(ys) - min(ys)) * sc)))
        gx, gz = int(inst.get("ground_x", 0)), int(inst.get("ground_z", 0))
        if inst.get("body", "dynamic") == "dynamic":
            vel = inst.get("vel", {}) or {}
            dyn.append({"x": gx, "z": gz, "r": r,
                        "m": max(1, int(round(inst.get("mass", 1) or 1))),
                        "vx": int(round(vel.get("x", 0) or 0)), "vz": int(round(vel.get("z", 0) or 0))})
        else:
            statics.append({"x": gx, "z": gz, "r": r})
    return dyn, statics


def _fit(frames, statics, W, H, margin):
    """Map raw plane coords (over ALL frames + statics) into a W×H draw box, uniform."""
    xs, zs = [], []
    for f in frames:
        for b in f["raw"]:
            xs += [b["x"] - b["r"], b["x"] + b["r"]]; zs += [b["y"] - b["r"], b["y"] + b["r"]]
    for s in statics:
        xs += [s["x"] - s["r"], s["x"] + s["r"]]; zs += [s["z"] - s["r"], s["z"] + s["r"]]
    if not xs:
        xs, zs = [0, 1], [0, 1]
    xmin, xmax, zmin, zmax = min(xs), max(xs), min(zs), max(zs)
    sc = min((W - 2 * margin) / max(1, xmax - xmin), (H - 2 * margin) / max(1, zmax - zmin))
    mx = lambda x: round(margin + (x - xmin) * sc, 2)
    my = lambda z: round(margin + (z - zmin) * sc, 2)
    out = []
    for f in frames:
        g = {k: f[k] for k in ("frame", "digest", "px", "py", "e2")}
        g["balls"] = [{"x": mx(b["x"]), "y": my(b["y"]), "r": round(max(2, b["r"] * sc), 2),
                       "vx": round(b["vx"] * sc, 3), "vy": round(b["vy"] * sc, 3), "m": b["m"]}
                      for b in f["raw"]]
        if "contacts" in f:
            g["contacts"] = [{"x": mx(c["x"]), "y": my(c["y"]), "nx": c["nx"], "ny": c["ny"],
                              "imp": round(c["imp"] * sc, 3), "i": c["i"], "j": c["j"]} for c in f["contacts"]]
        out.append(g)
    dstat = [{"x": mx(s["x"]), "y": my(s["z"]), "r": round(max(2, s["r"] * sc), 2)} for s in statics]
    return out, dstat


def world_doc(path, steps=90, W=460, H=280, margin=30):
    dyn, statics = _load_world(path)
    if not dyn:
        # nothing to simulate — still emit a valid (single-frame) doc so the editor shows the statics
        _, dstat = _fit([{"raw": []}], statics, W, H, margin)
        return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat,
                "note": "no dynamic bodies — add a dynamic object with an initial velocity to see motion",
                "refused": None, "frames": [], "chain": []}
    bodies = [Ball(Vec([Q(d["x"]), Q(d["z"])]), Q(d["r"]), Vec([Q(d["vx"]), Q(d["vz"])]), d["m"]) for d in dyn]
    frames, refused = _simulate(bodies, steps, raw=True)
    dframes, dstat = _fit(frames, statics, W, H, margin)
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat,
            "note": "authored world simulated by the exact engine (dynamics_nd); digest per frame = URDRPN1 witness",
            "refused": refused, "frames": dframes, "chain": [f["digest"] for f in dframes]}


# ---- resting stack: the exact contact LCP, with per-contact λ surfaced ---------------
def stack_doc(N=3, W=360, H=320, R=26, GRAV=1, MASS=1):
    """A vertical stack of N equal balls resting on the ground under gravity. One gravity
    impulse gives each ball a downward velocity; the exact frictionless LCP (contact_lcp)
    solves the normal impulses λ that hold the stack in equilibrium — larger toward the
    bottom (each contact carries the weight above it). The certified (λ, w) has a URDRLCP1
    witness. Emitted as a single-frame replay whose contacts carry their λ."""
    down = Vec([Z(0), Q(GRAV)])                          # gravity impulse (down = +y)
    up = Vec([Z(0), Z(-1)])                              # contact normal a→b (points up)
    vels = [Vec([Z(0), Z(0)])] + [down for _ in range(N)]        # body 0 = static ground
    invm = [Z(0)] + [Q(1, MASS) for _ in range(N)]
    contacts = [Contact(0, 1, up)] + [Contact(k, k + 1, up) for k in range(1, N)]
    A, b = delassus(vels, invm, contacts)
    lam, w = solve_lcp(A, b)                             # exact; refuses if degenerate
    cert, dig = complementary(lam, w), lcp_digest(lam, w)
    cx, yg = W / 2, H - 44                               # ground line
    balls = [{"x": cx, "y": yg - (2 * k - 1) * R, "r": R, "vx": 0, "vy": 0, "m": MASS}
             for k in range(1, N + 1)]
    cpts = [{"x": cx, "y": yg, "nx": 0, "ny": -1, "lam": _f(lam[0])}]
    for k in range(1, N):
        cpts.append({"x": cx, "y": yg - 2 * k * R, "nx": 0, "ny": -1, "lam": _f(lam[k])})
    frame = {"frame": 0, "digest": dig, "px": 0.0, "py": 0.0, "e2": 0.0, "balls": balls, "contacts": cpts}
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": [], "stack": True,
            "ground": yg, "lcp_digest": dig, "certified": cert,
            "note": "resting stack — contact λ certified by the exact LCP (URDRLCP1)",
            "refused": None, "frames": [frame], "chain": [dig]}


def main(argv):
    if len(argv) > 1 and argv[1] == "--world":
        if len(argv) < 3:
            print("usage: python3 replay.py --world urdr_world.json [out.json]")
            return 2
        world_path = argv[2]
        out_path = argv[3] if len(argv) > 3 else os.path.join(HERE, "urdr_replay.json")
        if not os.path.exists(world_path):
            print("no world file at %s — export one from urdr_designer.html (▸ Export world JSON)" % world_path)
            return 1
        doc = world_doc(world_path)
        label = "authored world"
    elif len(argv) > 1 and argv[1] == "--stack":
        n = int(argv[2]) if len(argv) > 2 and argv[2].lstrip("-").isdigit() else 3
        n = max(1, min(10, n))
        out_path = argv[3] if len(argv) > 3 else os.path.join(HERE, "urdr_replay.json")
        doc = stack_doc(n)
        label = "resting stack (N=%d)" % n
    else:
        out_path = argv[1] if len(argv) > 1 else os.path.join(HERE, "urdr_replay.json")
        doc = cascade_doc()
        label = "demo cascade"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh)
    frames = doc["frames"]
    print("scene         :", label)
    print("dynamic bodies:", (len(frames[0]["balls"]) if frames else 0), " statics:", len(doc["statics"]))
    print("ticks         :", len(frames))
    if doc.get("stack"):
        print("contact λ     :", [c["lam"] for c in frames[0]["contacts"]], "(bottom → top)")
        print("LCP certified :", doc["certified"], " URDRLCP1:", doc["lcp_digest"][:24], "…")
    elif frames:
        print("frame 0 digest:", frames[0]["digest"][:24], "…")
        print("frame N digest:", frames[-1]["digest"][:24], "…")
        print("momentum      :", "conserved" if (frames[0]["px"], frames[0]["py"]) == (frames[-1]["px"], frames[-1]["py"]) else "changed")
        print("2*KE          :", "conserved" if frames[0]["e2"] == frames[-1]["e2"] else "changed")
    print("witness chain :", len(doc["chain"]), "digests")
    if doc["refused"]:
        print("engine        : REFUSED after frame %d — %s (exact, not approximate)"
              % (doc["refused"]["after_frame"], doc["refused"]["code"]))
    print("wrote         :", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
