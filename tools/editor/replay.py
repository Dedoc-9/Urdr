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
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "physics"))
from rational import Q, Z, RationalError                 # noqa: E402
from vecq import Vec                                     # noqa: E402
from dynamics_nd import Ball, step, state_digest, momentum, two_kinetic  # noqa: E402
from contact_lcp import Contact, delassus, solve_lcp, complementary, lcp_digest  # noqa: E402
from articulated import distance_row, pin_rows, solve as jsolve, satisfied, joint_digest  # noqa: E402
from field import FixedPoint as _FP, ONE as _FPONE, FieldError, _rdiv as _rd  # noqa: E402  frozen Q32.32 substrate

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
    dyn, statics, cons = [], [], []
    for inst in w.get("instances", []):
        o = objs.get(inst.get("object"))
        if not o or not o.get("verts"):
            continue
        xs = [v[0] for v in o["verts"]]
        ys = [v[1] for v in o["verts"]]
        sc = inst.get("scale", 1.0) or 1.0
        r = max(1, int(round(0.5 * max(max(xs) - min(xs), max(ys) - min(ys)) * sc)))
        gx, gz = int(inst.get("ground_x", 0)), int(inst.get("ground_z", 0))
        iid = inst.get("id")
        if inst.get("body", "dynamic") == "dynamic":
            vel = inst.get("vel", {}) or {}
            dyn.append({"id": iid, "x": gx, "z": gz, "r": r,
                        "m": max(1, int(round(inst.get("mass", 1) or 1))),
                        "vx": int(round(vel.get("x", 0) or 0)), "vz": int(round(vel.get("z", 0) or 0))})
        else:
            statics.append({"id": iid, "x": gx, "z": gz, "r": r})
        if inst.get("constraints"):
            cons.append((iid, inst["constraints"]))
    nd = len(dyn)
    idx = {}
    for i, d in enumerate(dyn):
        idx[d["id"]] = i
    for s, st in enumerate(statics):
        idx[st["id"]] = nd + s
    joints = []                                            # (a_body, b_body, type) with resolved indices
    for owner, clist in cons:
        a = idx.get(owner)
        if a is None:
            continue
        for c in clist:
            b = idx.get(c.get("to"))
            if b is not None and b != a and c.get("type") in ("hinge", "rod", "weld", "slider"):
                joints.append((a, b, c.get("type")))
    return dyn, statics, joints


def _joint_rows(joints, pos):
    """Turn resolved joint specs + current positions into articulated constraint rows:
    weld → a pin (rigid coincidence of velocity), hinge/rod → a distance constraint (rigid
    link that can swing), slider → a single row perpendicular to the link (motion along it
    only). spring/motor are soft/driven and stay declared, not solved here."""
    rows = []
    for (a, b, typ) in joints:
        pa, pb = Vec([pos[a][0], pos[a][1]]), Vec([pos[b][0], pos[b][1]])
        if typ == "weld":
            rows += pin_rows(a, b, 2)
        elif typ in ("hinge", "rod"):
            rows.append(distance_row(a, b, pa, pb))
        elif typ == "slider":
            n = pa - pb
            perp = Vec([Z(0) - n.c[1], n.c[0]])
            rows.append([(a, perp), (b, perp.scale(Z(-1)))])
    return rows


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
        g = {k: f.get(k) for k in ("frame", "digest", "px", "py", "e2")}
        g["balls"] = [{"x": mx(b["x"]), "y": my(b["y"]), "r": round(max(2, b["r"] * sc), 2),
                       "vx": round(b["vx"] * sc, 3), "vy": round(b["vy"] * sc, 3), "m": b["m"]}
                      for b in f["raw"]]
        if "contacts" in f:
            g["contacts"] = [{"x": mx(c["x"]), "y": my(c["y"]), "nx": c["nx"], "ny": c["ny"],
                              "imp": round(c["imp"] * sc, 3)} for c in f["contacts"]]
        if "links" in f:
            g["links"] = [{"ax": mx(l["ax"]), "ay": my(l["ay"]), "bx": mx(l["bx"]), "by": my(l["by"]),
                           "type": l["type"]} for l in f["links"]]
        out.append(g)
    dstat = [{"x": mx(s["x"]), "y": my(s["z"]), "r": round(max(2, s["r"] * sc), 2)} for s in statics]
    return out, dstat


def _simulate_world(dyn, statics, steps, grav=0):
    """Contact-resolving world step. Dynamic bodies collide against each other AND the static
    colliders; ALL simultaneous contacts are resolved together by the exact frictionless LCP
    (contact_lcp — a static body is one with inverse mass 0). Optional gravity. Momentum is
    conserved among the dynamic bodies except where a static anchor absorbs it. Honest scope:
    frictionless and inelastic at the normal (the LCP model), discrete overlap (no CCD),
    restitution/elastic multi-contact a later rung. Records per-frame contacts + impulse."""
    nd, ns = len(dyn), len(statics)
    pos = [[Q(d["x"]), Q(d["z"])] for d in dyn] + [[Q(s["x"]), Q(s["z"])] for s in statics]
    vel = [[Q(d["vx"]), Q(d["vz"])] for d in dyn] + [[Z(0), Z(0)] for _ in statics]
    rad = [Q(d["r"]) for d in dyn] + [Q(s["r"]) for s in statics]
    invm = [Q(1, d["m"]) for d in dyn] + [Z(0) for _ in statics]
    mass = [d["m"] for d in dyn]
    frames, refused, used = [], None, False
    for k in range(steps + 1):
        try:
            contacts, info = [], []
            for i in range(nd):                                   # i is always a dynamic body
                for j in range(i + 1, nd + ns):
                    dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
                    rr = rad[i] + rad[j]
                    approaching = (vel[j][0] - vel[i][0]) * dx + (vel[j][1] - vel[i][1]) * dy < Z(0)
                    if dx * dx + dy * dy <= rr * rr and approaching:
                        contacts.append(Contact(i, j, Vec([dx, dy]))); info.append((i, j, dx, dy))
            craw = None
            if contacts:
                used = True
                velv = [Vec([vel[b][0], vel[b][1]]) for b in range(nd + ns)]
                newv, lam, w = resolve(velv, invm, contacts)      # exact simultaneous LCP; refuses if degenerate
                for b in range(nd + ns):
                    vel[b][0], vel[b][1] = newv[b].c[0], newv[b].c[1]
                craw = []
                for t, (i, j, dx, dy) in enumerate(info):
                    fx, fy = _f(dx), _f(dy); L = (fx * fx + fy * fy) ** 0.5 or 1.0
                    ri, rj = _f(rad[i]), _f(rad[j]); tt = ri / (ri + rj) if (ri + rj) else 0.5
                    craw.append({"x": _f(pos[i][0]) + tt * fx, "y": _f(pos[i][1]) + tt * fy,
                                 "nx": fx / L, "ny": fy / L, "imp": _f(lam[t]) * L})
        except RationalError as e:
            refused = {"after_frame": k, "code": getattr(e, "code", "PHYS-REFUSE"), "message": str(e)}
            break
        bodies = [Ball(Vec([pos[i][0], pos[i][1]]), rad[i], Vec([vel[i][0], vel[i][1]]), mass[i]) for i in range(nd)]
        p = momentum(bodies)
        snap = {"frame": k, "digest": state_digest(bodies), "px": _f(p.c[0]), "py": _f(p.c[1]), "e2": _f(two_kinetic(bodies)),
                "raw": [{"x": _f(pos[i][0]), "y": _f(pos[i][1]), "r": _f(rad[i]),
                         "vx": _f(vel[i][0]), "vy": _f(vel[i][1]), "m": mass[i]} for i in range(nd)]}
        if craw:
            snap["contacts"] = craw
        frames.append(snap)
        if k == steps:
            break
        try:
            for i in range(nd):                                   # integrate; static bodies are anchors
                pos[i][0] = pos[i][0] + vel[i][0]; pos[i][1] = pos[i][1] + vel[i][1]
                if grav:
                    vel[i][1] = vel[i][1] + Q(grav)
        except RationalError as e:
            refused = {"after_frame": k, "code": getattr(e, "code", "PHYS-REFUSE"), "message": str(e)}
            break
    return frames, refused, used


def world_doc(path, steps=90, grav=0, W=460, H=280, margin=30):
    dyn, statics, joints = _load_world(path)
    if not dyn:
        # nothing to simulate — still emit a valid (single-frame) doc so the editor shows the statics
        _, dstat = _fit([{"raw": []}], statics, W, H, margin)
        return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "lcp": False,
                "note": "no dynamic bodies — add a dynamic object with an initial velocity to see motion",
                "refused": None, "frames": [], "chain": []}
    frames, refused, used = _simulate_world(dyn, statics, steps, grav)
    dframes, dstat = _fit(frames, statics, W, H, margin)
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "lcp": used,
            "has_joints": bool(joints),
            "note": "authored world — dynamic bodies collide against each other and statics via the exact LCP",
            "refused": refused, "frames": dframes, "chain": [f["digest"] for f in dframes]}


# ---- joints: the exact equality (articulated) solve, with links + certificate --------
def joints_doc(world_path=None, N=4, W=460, H=280, margin=30):
    """Solve an articulated system's constraints exactly (velocity-level equality) and
    certify J·v = 0 with a URDRJNT1 witness. From an authored URDR-WORLD-3 export (its
    Inspector constraint list), or a built-in chain of N balls linked by rods with the left
    end pushed. Iterated joint DYNAMICS overflow i64 in ~2 exact steps (the ℚ substrate
    limit), so this is surfaced as a single CERTIFIED solve, not a time-stepped animation."""
    if world_path and os.path.exists(world_path):
        dyn, statics, joints = _load_world(world_path)
        authored = True
    else:
        dyn = [{"id": k, "x": 60 + k * 60, "z": 140, "r": 20, "m": 1,
                "vx": (4 if k == 0 else 0), "vz": 0} for k in range(N)]
        statics = []
        joints = [(k, k + 1, "rod") for k in range(N - 1)]
        authored = False
    nd, ns = len(dyn), len(statics)
    if not joints:
        _, dstat = _fit([{"raw": [{"x": d["x"], "y": d["z"], "r": d["r"], "vx": d["vx"], "vy": d["vz"], "m": d["m"]} for d in dyn]}],
                        [{"x": s["x"], "z": s["z"], "r": s["r"]} for s in statics], W, H, margin)
        return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "joints": False,
                "note": "no constraints authored — add a hinge/rod/weld in the Inspector, or omit --world for the chain demo",
                "refused": None, "frames": [], "chain": []}
    pos = [[Q(d["x"]), Q(d["z"])] for d in dyn] + [[Q(s["x"]), Q(s["z"])] for s in statics]
    vels = [Vec([Q(d["vx"]), Q(d["vz"])]) for d in dyn] + [Vec([Z(0), Z(0)]) for _ in statics]
    invm = [Q(1, d["m"]) for d in dyn] + [Z(0) for _ in statics]
    rows = _joint_rows(joints, pos)
    refused, cert, jdig = None, False, ""
    newv = vels
    try:
        newv, lam = jsolve(vels, invm, rows)
        cert, jdig = satisfied(newv, rows), joint_digest(newv, lam)
    except RationalError as e:
        refused = {"after_frame": 0, "code": getattr(e, "code", "PHYS-REFUSE"), "message": str(e)}
    raw = [{"x": _f(pos[i][0]), "y": _f(pos[i][1]), "r": float(dyn[i]["r"]),
            "vx": _f(newv[i].c[0]), "vy": _f(newv[i].c[1]), "m": dyn[i]["m"]} for i in range(nd)]
    links = [{"ax": _f(pos[a][0]), "ay": _f(pos[a][1]), "bx": _f(pos[b][0]), "by": _f(pos[b][1]), "type": t}
             for (a, b, t) in joints]
    frame = {"frame": 0, "digest": jdig or "n/a", "px": 0.0, "py": 0.0, "e2": 0.0, "raw": raw, "links": links}
    dframes, dstat = _fit([frame], [{"x": s["x"], "z": s["z"], "r": s["r"]} for s in statics], W, H, margin)
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "joints": True,
            "authored": authored, "certified": cert, "joint_digest": jdig,
            "note": "articulated constraints — certified equality solve (URDRJNT1), J·v = 0",
            "refused": refused, "frames": dframes, "chain": ([jdig] if jdig else [])}


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


# ---- fixed-point time-stepping: BOUNDED, deterministic, no overflow ------------------
def _fp_digest(cols, magic=b"URDRFPB1"):
    out = bytearray(magic)
    for arr in cols:
        for a in arr:
            out += _FP.ser(a)
    return hashlib.sha256(bytes(out)).hexdigest()


def _fm(a, b):
    return _FP._g(_rd(a * b, _FPONE))                     # fixed × fixed (rounds)


def _fdiv(a, b):
    return _FP._g(_rd(a * _FPONE, b))                     # fixed ÷ fixed (rounds)


def fp_bounce_doc(N=4, steps=240, W=380, H=300):
    """Gravity + bounce in a box on the FROZEN Q32.32 fixed-point substrate
    (`../physics/field.py` FixedPoint: round-to-nearest, ties away). This is the scene
    exact-ℚ REFUSED (its denominators explode) — fixed-point is BOUNDED and ROUNDS, so it
    time-steps as long as you like, deterministically and reproducibly (bit-identical across
    placements). Not exact; the honest real-time path, with a per-frame URDRFPB1 witness."""
    R = 16
    floor, ceil, left, right = H - 28, 22, 22, W - 22
    Rf = _FP.unit(R, 1)
    floorf, ceilf, leftf, rightf = (_FP.unit(v, 1) for v in (floor, ceil, left, right))
    GDT = _FP.unit(3, 10)                                 # gravity·dt per step
    span = max(1, (W - 120) // max(1, N - 1))
    bx = [_FP.unit(60 + i * span, 1) for i in range(N)]
    by = [_FP.unit(40 + (i % 3) * 22, 1) for i in range(N)]
    bvx = [_FP.unit(-2 if i % 2 else 2, 1) for i in range(N)]
    bvy = [0] * N
    fl = lambda a: round(a / _FPONE, 2)                   # fixed-point → decimal (drawing only)
    frames, refused = [], None
    for k in range(steps + 1):
        frames.append({"frame": k, "digest": _fp_digest((bx, by, bvx, bvy)),
                       "px": 0.0, "py": 0.0, "e2": 0.0,
                       "balls": [{"x": fl(bx[i]), "y": fl(by[i]), "r": R,
                                  "vx": fl(bvx[i]), "vy": fl(bvy[i]), "m": 1} for i in range(N)]})
        try:
            for i in range(N):
                bvy[i] = _FP.add(bvy[i], GDT)             # gravity
                bx[i] = _FP.add(bx[i], bvx[i]); by[i] = _FP.add(by[i], bvy[i])  # integrate
                if by[i] + Rf > floorf and bvy[i] > 0:
                    by[i] = _FP.sub(floorf, Rf); bvy[i] = _FP.mul_k(bvy[i], -3, 4)   # bounce (e=3/4)
                if by[i] - Rf < ceilf and bvy[i] < 0:
                    by[i] = _FP.add(ceilf, Rf); bvy[i] = _FP.mul_k(bvy[i], -3, 4)
                if bx[i] + Rf > rightf and bvx[i] > 0:
                    bx[i] = _FP.sub(rightf, Rf); bvx[i] = _FP.mul_k(bvx[i], -3, 4)
                if bx[i] - Rf < leftf and bvx[i] < 0:
                    bx[i] = _FP.add(leftf, Rf); bvx[i] = _FP.mul_k(bvx[i], -3, 4)
        except FieldError as e:
            refused = {"after_frame": k, "code": getattr(e, "code", "FIELD-REFUSE"), "message": str(e)}
            break
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": [], "fp": True,
            "ground": floor,
            "note": "bounded Q32.32 fixed-point (frozen round-to-nearest) — deterministic, no overflow",
            "refused": refused, "frames": frames, "chain": [f["digest"] for f in frames]}


def fp_stack_doc(N=3, steps=240, K=20, W=360, H=300):
    """The exact contact LCP, PORTED to fixed-point: a vertical stack falls and SETTLES on
    the ground via bounded sequential-impulse (PGS) contacts + ground-up position projection.
    All normals are axis-aligned (no sqrt). Bounded, deterministic, no overflow — the animated
    counterpart to `--stack`'s certified single-solve λ. Contacts carry their accumulated λ."""
    R = 20
    yg = H - 40
    Rf, ygf, twoR = _FP.unit(R, 1), _FP.unit(yg, 1), _FP.unit(2 * R, 1)
    GDT, SLEEP, cx = _FP.unit(4, 10), _FP.unit(5, 2), W / 2
    py = [_FP.unit(50 + i * 44, 1) for i in range(N)]
    vy = [0] * N
    fl = lambda a: round(a / _FPONE, 2)
    frames, refused = [], None
    for t in range(steps + 1):
        lf, lb = {}, {}
        try:
            for i in range(N):
                vy[i] = _FP.add(vy[i], GDT)
            for i in range(N):
                py[i] = _FP.add(py[i], vy[i])
            order = sorted(range(N), key=lambda i: -py[i])          # bottom (max y) first
            for _ in range(K):                                      # PGS sweeps
                for i in order:                                     # floor: effmass = invm(1)
                    if _FP.add(py[i], Rf) > ygf and vy[i] > 0:
                        acc = lf.get(i, 0); newl = acc + vy[i]; lf[i] = newl
                        vy[i] = _FP.sub(vy[i], newl - acc)
                for k in range(len(order) - 1):                     # ball-ball: effmass = 2
                    lo, up = order[k], order[k + 1]
                    if _FP.sub(py[lo], py[up]) < twoR and _FP.sub(vy[lo], vy[up]) < 0:
                        acc = lb.get((lo, up), 0)
                        dl = _FP.mul_k(_FP.sub(vy[up], vy[lo]), 1, 2)
                        newl = acc + dl; d = newl - acc; lb[(lo, up)] = newl
                        vy[up] = _FP.sub(vy[up], d); vy[lo] = _FP.add(vy[lo], d)
            for i in order:                                         # ground-up position projection
                if _FP.add(py[i], Rf) > ygf:
                    py[i] = _FP.sub(ygf, Rf)
            for k in range(len(order) - 1):
                lo, up = order[k], order[k + 1]
                if _FP.sub(py[lo], py[up]) < twoR:
                    py[up] = _FP.sub(py[lo], twoR)
            resting = set(lf) | {up for (lo, up) in lb}             # sleep supported + slow bodies
            for i in resting:
                if -SLEEP < vy[i] < SLEEP:
                    vy[i] = 0
        except FieldError as e:
            refused = {"after_frame": t, "code": getattr(e, "code", "FIELD-REFUSE"), "message": str(e)}
            break
        cpts = [{"x": cx, "y": yg, "nx": 0, "ny": -1, "lam": fl(l)} for i, l in lf.items()]
        cpts += [{"x": cx, "y": fl(_FP.sub(py[lo], Rf)), "nx": 0, "ny": -1, "lam": fl(l)} for (lo, up), l in lb.items()]
        frames.append({"frame": t, "digest": _fp_digest((py, vy), b"URDRFPS1"),
                       "px": 0.0, "py": 0.0, "e2": 0.0,
                       "balls": [{"x": cx, "y": fl(py[i]), "r": R, "vx": 0.0, "vy": fl(vy[i]), "m": 1} for i in range(N)],
                       "contacts": cpts})
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": [], "fp": True, "showlam": True,
            "ground": yg,
            "note": "fixed-point settling stack — bounded PGS contacts + ground-up projection, deterministic (no overflow)",
            "refused": refused, "frames": frames, "chain": [f["digest"] for f in frames]}


def fp_swing_doc(steps=220, W=380, H=300):
    """The articulated equality solve, PORTED to fixed-point: a ball on a rod swings under
    gravity. The distance constraint holds each step (velocity-level) with Baumgarte feedback
    on the SQUARED length (d·d − L² — no sqrt, so it stays in i64), which removes the drift
    exact-ℚ couldn't sustain past 2 steps. Bounded, deterministic, no overflow."""
    ax, ay, R = W / 2, 60, 16
    axf, ayf = _FP.unit(int(ax), 1), _FP.unit(ay, 1)
    px, py, vx, vy = _FP.unit(int(ax) + 90, 1), _FP.unit(ay, 1), 0, 0
    GDT = _FP.unit(3, 10)
    fl = lambda a: round(a / _FPONE, 2)
    L2_0, frames, refused = None, [], None
    for t in range(steps + 1):
        try:
            vy = _FP.add(vy, GDT)
            nx, ny = _FP.sub(px, axf), _FP.sub(py, ayf)
            dd = _FP.add(_fm(nx, nx), _fm(ny, ny))
            if L2_0 is None:
                L2_0 = dd
            Jv = _FP.add(_fm(nx, vx), _fm(ny, vy))
            if dd > 0:
                bias = _FP.mul_k(_FP.sub(dd, L2_0), 1, 6)           # feedback on squared length
                lam = _fdiv(_FP.sub(_FP.sub(0, bias), Jv), dd)
                vx = _FP.add(vx, _fm(lam, nx)); vy = _FP.add(vy, _fm(lam, ny))
            px = _FP.add(px, vx); py = _FP.add(py, vy)
        except FieldError as e:
            refused = {"after_frame": t, "code": getattr(e, "code", "FIELD-REFUSE"), "message": str(e)}
            break
        frames.append({"frame": t, "digest": _fp_digest(([px], [py], [vx], [vy]), b"URDRFPP1"),
                       "px": 0.0, "py": 0.0, "e2": 0.0,
                       "balls": [{"x": fl(px), "y": fl(py), "r": R, "vx": fl(vx), "vy": fl(vy), "m": 1}],
                       "links": [{"ax": ax, "ay": ay, "bx": fl(px), "by": fl(py), "type": "rod"}]})
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "fp": True,
            "statics": [{"x": ax, "y": ay, "r": 6}],
            "note": "fixed-point pendulum — articulated distance constraint, squared-length Baumgarte (no drift, no overflow)",
            "refused": refused, "frames": frames, "chain": [f["digest"] for f in frames]}


def fp_world_doc(path, steps=200, K=14, e_pct=50, grav=0, W=460, H=280, margin=30):
    """An AUTHORED world (URDR-WORLD-3), time-stepped on the fixed-point substrate — the
    bounded long-run counterpart to the exact `--world`. Dynamic instances collide against
    each other and the static colliders via a general 2D fixed-point PGS using UN-NORMALIZED
    normals (the `|d|` cancels via `d·d`, so no sqrt) + squared-penetration Baumgarte + `--e`
    restitution. With `grav`, an implicit box (floor + side walls) and light linear damping are
    added so the scene falls and SETTLES. Runs as long as you like without overflow, where the
    exact LCP would refuse. Deterministic; URDRFPW1 witness per frame."""
    dyn, statics, _joints = _load_world(path)
    sraw = [{"x": s["x"], "z": s["z"], "r": s["r"]} for s in statics]
    if not dyn:
        _, dstat = _fit([{"raw": []}], sraw, W, H, margin)
        return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "fp": True,
                "note": "no dynamic bodies — add a dynamic object with an initial velocity",
                "refused": None, "frames": [], "chain": []}
    nd, ns = len(dyn), len(statics)
    px = [_FP.unit(b["x"], 1) for b in dyn] + [_FP.unit(s["x"], 1) for s in statics]
    pz = [_FP.unit(b["z"], 1) for b in dyn] + [_FP.unit(s["z"], 1) for s in statics]
    vx = [_FP.unit(b["vx"], 1) for b in dyn] + [0] * ns
    vz = [_FP.unit(b["vz"], 1) for b in dyn] + [0] * ns
    rad = [b["r"] for b in dyn] + [s["r"] for s in statics]
    mass = [b["m"] for b in dyn] + [0] * ns                 # 0 marks static
    fl = lambda a: round(a / _FPONE, 2)
    GDT = _FP.unit(grav, 10) if grav else 0                 # gravity·dt (down = +z)
    if grav:                                                # implicit box so the scene settles
        allx = [b["x"] for b in dyn] + [s["x"] for s in statics]
        allz = [b["z"] for b in dyn] + [s["z"] for s in statics]
        rmax = max(rad)
        floorf = _FP.unit(max(allz) + rmax + 50, 1)
        xlo = _FP.unit(min(allx) - rmax - 40, 1)
        xhi = _FP.unit(max(allx) + rmax + 40, 1)
    frames, refused = [], None
    for t in range(steps + 1):
        raw = [{"x": fl(px[i]), "y": fl(pz[i]), "r": rad[i], "vx": fl(vx[i]), "vy": fl(vz[i]), "m": dyn[i]["m"]}
               for i in range(nd)]
        cacc = {}
        try:
            for i in range(nd):
                if grav:
                    vz[i] = _FP.add(vz[i], GDT)
                    vx[i] = _FP.mul_k(vx[i], 97, 100); vz[i] = _FP.mul_k(vz[i], 97, 100)   # light linear damping
                px[i] = _FP.add(px[i], vx[i]); pz[i] = _FP.add(pz[i], vz[i])
            pairs, vnpre, lam = [], {}, {}
            for i in range(nd):                                 # detect contacts + capture approach velocity
                for j in range(i + 1, nd + ns):
                    dx, dz = _FP.sub(px[j], px[i]), _FP.sub(pz[j], pz[i])
                    dd = _FP.add(_fm(dx, dx), _fm(dz, dz))
                    rr = rad[i] + rad[j]; rr2 = _FP.unit(rr * rr, 1)
                    if dd < rr2:                                # penetrating contact (un-normalized normal d)
                        pairs.append((i, j, rr2))
                        vnpre[(i, j)] = _FP.add(_fm(_FP.sub(vx[j], vx[i]), dx), _fm(_FP.sub(vz[j], vz[i]), dz))
            floors, vnf = [], {}
            if grav:                                            # floor contacts (axis-aligned, no sqrt)
                for i in range(nd):
                    if _FP.add(pz[i], _FP.unit(rad[i], 1)) > floorf:
                        floors.append(i); vnf[i] = vz[i]
            for _ in range(K):                                  # velocity-level restitution PGS (no sqrt)
                for (i, j, rr2) in pairs:
                    dx, dz = _FP.sub(px[j], px[i]), _FP.sub(pz[j], pz[i])
                    dd = _FP.add(_fm(dx, dx), _fm(dz, dz))
                    vn = _FP.add(_fm(_FP.sub(vx[j], vx[i]), dx), _fm(_FP.sub(vz[j], vz[i]), dz))
                    vp = vnpre[(i, j)]
                    rest = _FP.mul_k(vp, -e_pct, 100) if vp < 0 else 0   # target = −e·v_approach
                    mi, mj = mass[i], mass[j]
                    num, den = ((mj + mi), (mi * mj)) if (mi and mj) else ((1, mi) if mi else (1, mj))
                    eff = _FP.mul_k(dd, num, den)
                    if eff > 0:
                        dl = _fdiv(_FP.sub(rest, vn), eff)
                        acc = lam.get((i, j), 0); newl = acc + dl
                        if newl < 0:
                            newl = 0
                        d = newl - acc; lam[(i, j)] = newl; cacc[(i, j)] = newl
                        if d != 0:
                            if mi:
                                vx[i] = _FP.sub(vx[i], _FP.mul_k(_fm(d, dx), 1, mi)); vz[i] = _FP.sub(vz[i], _FP.mul_k(_fm(d, dz), 1, mi))
                            if mj:
                                vx[j] = _FP.add(vx[j], _FP.mul_k(_fm(d, dx), 1, mj)); vz[j] = _FP.add(vz[j], _FP.mul_k(_fm(d, dz), 1, mj))
                for i in floors:                                # upward floor impulse λ = vz + e·vz_pre
                    vp = vnf[i]; rest = _FP.mul_k(vp, e_pct, 100) if vp > 0 else 0
                    acc = lam.get(("f", i), 0); newl = acc + _FP.add(vz[i], rest)
                    if newl < 0:
                        newl = 0
                    d = newl - acc; lam[("f", i)] = newl
                    vz[i] = _FP.sub(vz[i], d)
            for (i, j, rr2) in pairs:                            # light position projection (positions only; no energy)
                dx, dz = _FP.sub(px[j], px[i]), _FP.sub(pz[j], pz[i])
                dd = _FP.add(_fm(dx, dx), _fm(dz, dz))
                if 0 < dd < rr2:
                    s = _FP.mul_k(_fdiv(_FP.sub(rr2, dd), _FP.mul_k(dd, 4, 1)), 1, 2)
                    mi, mj = mass[i], mass[j]
                    if mi and mj:
                        h = _FP.mul_k(s, 1, 2)
                        px[i] = _FP.sub(px[i], _fm(h, dx)); pz[i] = _FP.sub(pz[i], _fm(h, dz))
                        px[j] = _FP.add(px[j], _fm(h, dx)); pz[j] = _FP.add(pz[j], _fm(h, dz))
                    elif mi:
                        px[i] = _FP.sub(px[i], _fm(s, dx)); pz[i] = _FP.sub(pz[i], _fm(s, dz))
                    elif mj:
                        px[j] = _FP.add(px[j], _fm(s, dx)); pz[j] = _FP.add(pz[j], _fm(s, dz))
            if grav:                                            # side walls + floor snap + sleep
                for i in range(nd):
                    ri = _FP.unit(rad[i], 1)
                    if _FP.sub(px[i], ri) < xlo and vx[i] < 0:
                        px[i] = _FP.add(xlo, ri); vx[i] = _FP.mul_k(vx[i], -e_pct, 100)
                    if _FP.add(px[i], ri) > xhi and vx[i] > 0:
                        px[i] = _FP.sub(xhi, ri); vx[i] = _FP.mul_k(vx[i], -e_pct, 100)
                    if _FP.add(pz[i], ri) > floorf:
                        pz[i] = _FP.sub(floorf, ri)
                SLEEP = _FP.unit(1, 1)
                for i in set(floors) | {u for (i2, j2, r2) in pairs for u in (i2, j2)}:
                    if i < nd and -SLEEP < vz[i] < SLEEP and -SLEEP < vx[i] < SLEEP:
                        vz[i] = 0; vx[i] = 0
        except FieldError as e:
            refused = {"after_frame": t, "code": getattr(e, "code", "FIELD-REFUSE"), "message": str(e)}
            break
        craw = []
        for (i, j), l in cacc.items():
            mx_, mz_ = fl(_FP.add(px[i], _FP.sub(px[j], px[i]) // 2)), fl(_FP.add(pz[i], _FP.sub(pz[j], pz[i]) // 2))
            craw.append({"x": mx_, "y": mz_, "nx": 0, "ny": -1, "imp": abs(fl(l)) * (rad[i] + rad[j])})
        f = {"frame": t, "digest": _fp_digest((px[:nd], pz[:nd], vx[:nd], vz[:nd]), b"URDRFPW1"),
             "px": 0.0, "py": 0.0, "e2": 0.0, "raw": raw}
        if craw:
            f["contacts"] = craw
        frames.append(f)
    dframes, dstat = _fit(frames, sraw, W, H, margin)
    return {"format": "URDR-REPLAY-1", "w": W, "h": H, "rail": False, "statics": dstat, "fp": True,
            "note": "authored world on the fixed-point substrate — bounded PGS collisions%s with restitution (e=%d%%), deterministic (no overflow)" % (" + gravity (settles in an implicit box)" if grav else "", e_pct),
            "refused": refused, "frames": dframes, "chain": [f["digest"] for f in dframes]}


def main(argv):
    if len(argv) > 1 and argv[1] == "--world":
        if len(argv) < 3:
            print("usage: python3 replay.py --world urdr_world.json [out.json]")
            return 2
        world_path = argv[2]
        out_path = os.path.join(HERE, "urdr_replay.json")
        for a in argv[3:]:
            if a.endswith(".json"):
                out_path = a
        g = 0
        if "--g" in argv:
            gi = argv.index("--g")
            if gi + 1 < len(argv) and argv[gi + 1].lstrip("-").isdigit():
                g = int(argv[gi + 1])
        if not os.path.exists(world_path):
            print("no world file at %s — export one from urdr_designer.html (▸ Export world JSON)" % world_path)
            return 1
        doc = world_doc(world_path, grav=g)
        label = "authored world" + (" + gravity %d" % g if g else "")
    elif len(argv) > 1 and argv[1] == "--stack":
        n = int(argv[2]) if len(argv) > 2 and argv[2].lstrip("-").isdigit() else 3
        n = max(1, min(10, n))
        out_path = argv[3] if len(argv) > 3 else os.path.join(HERE, "urdr_replay.json")
        doc = stack_doc(n)
        label = "resting stack (N=%d)" % n
    elif len(argv) > 1 and argv[1] == "--joints":
        wp = None
        if "--world" in argv:
            wi = argv.index("--world")
            if wi + 1 < len(argv):
                wp = argv[wi + 1]
        n = 4
        for a in argv[2:]:
            if a.lstrip("-").isdigit():
                n = max(2, min(8, int(a)))
        out_path = os.path.join(HERE, "urdr_replay.json")
        doc = joints_doc(world_path=wp, N=n)
        label = "joints (%s)" % ("authored world" if wp else "chain N=%d" % n)
    elif len(argv) > 1 and argv[1] == "--fp":
        scene, n, jsons = "bounce", None, []
        for a in argv[2:]:
            if a in ("bounce", "stack", "swing", "world"):
                scene = a
            elif a.endswith(".json"):
                jsons.append(a)
            elif a.lstrip("-").isdigit():
                n = int(a)
        out_path = os.path.join(HERE, "urdr_replay.json")
        if scene == "world":
            wp = jsons[0] if jsons else os.path.join(HERE, "urdr_world.json")
            if not os.path.exists(wp):
                print("no world file at %s — export one from urdr_designer.html (▸ Export world JSON)" % wp)
                return 1
            ep = 50
            if "--e" in argv:
                ei = argv.index("--e")
                if ei + 1 < len(argv) and argv[ei + 1].lstrip("-").isdigit():
                    ep = max(0, min(100, int(argv[ei + 1])))
            g = 0
            if "--g" in argv:
                gi = argv.index("--g")
                if gi + 1 < len(argv) and argv[gi + 1].lstrip("-").isdigit():
                    g = int(argv[gi + 1])
            doc = fp_world_doc(wp, e_pct=ep, grav=g)
        else:
            if jsons:
                out_path = jsons[0]
            if scene == "stack":
                doc = fp_stack_doc(N=max(2, min(6, n or 3)))
            elif scene == "swing":
                doc = fp_swing_doc()
            else:
                doc = fp_bounce_doc(N=max(1, min(10, n or 4)))
        label = "fixed-point %s" % scene
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
    if doc.get("lcp"):
        nct = sum(len(f.get("contacts", [])) for f in frames)
        print("contacts      : resolved simultaneously by the exact LCP (%d over the run)" % nct)
    if doc.get("has_joints"):
        print("note          : authored constraints present — run  --joints --world <file>  to solve them")
    if doc.get("joints"):
        print("joint links   :", len(frames[0].get("links", [])) if frames else 0)
        print("J·v=0 certified:", doc.get("certified"), " URDRJNT1:", (doc.get("joint_digest") or "")[:24], "…")
    if doc.get("fp"):
        print("substrate     : Q32.32 fixed-point (bounded, frozen round-to-nearest) — %d ticks, no overflow"
              % (len(frames) - 1))
        if frames:
            print("frame 0 digest:", frames[0]["digest"][:24], "…  (fixed-point)")
            print("frame N digest:", frames[-1]["digest"][:24], "…")
        nct = sum(len(f.get("contacts", [])) for f in frames)
        if nct:
            print("contacts      : %d resolved (fixed-point PGS, un-normalized normals)" % nct)
    print("witness chain :", len(doc["chain"]), "digests")
    if doc["refused"]:
        print("engine        : REFUSED after frame %d — %s (exact, not approximate)"
              % (doc["refused"]["after_frame"], doc["refused"]["code"]))
    print("wrote         :", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
