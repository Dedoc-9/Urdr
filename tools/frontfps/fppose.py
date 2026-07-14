#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fppose — posed world transforms & hitbox capsules (frontfps Stage 4, URDRPSE1).

The bridge from animation to collision: a sampled pose (fpclip) applied to a rig
(frontfps) yields WORLD-space bone transforms by hierarchy composition, and the
posed skeleton yields the capsule set that hit registration consumes. All Stage-2
arithmetic; no new rounding law.

The composition recipe (the written order IS the spec, one bone at a time,
parents strictly before children — guaranteed by the rig topology law):

    world_q[0] = qnormalize(pose[0])
    world_p[0] = off[0]
    world_q[i] = qnormalize(qmul(world_q[parent], pose[i]))     # parent FIRST
    world_p[i] = world_p[parent] + vrotate(world_q[parent], off[i])

Normalization per compose keeps every bone's rotation within the Stage-2 unit
bound regardless of chain depth — drift cannot accumulate down a skeleton. The
classic port bug — `qmul(pose[i], world_q[parent])`, operands swapped — ships as
a defect and MUST diverge on the pinned corpus (`quaternions do not commute` is
a fact the gate enforces, not a comment).

Posed capsules: one per non-root bone, the segment from the parent's WORLD joint
to the bone's WORLD joint, radius authored per bone (integer ≥ 1, refused
otherwise). The certificate — `capsules_cover_joints` — checks EXACTLY (integer
point-to-segment comparison, no floats: |ap|²·(d·d) − (ap·d)² ≤ r²·(d·d) on the
interior branch) that every world joint lies inside at least one capsule. The
second defect — capsules built from LOCAL offsets instead of world positions —
passes on the identity pose and MUST fail coverage AND diverge on the posed
corpus (a defect that only bites when the skeleton actually moves is exactly the
kind an eyeball misses).

THE ONE-TICK-LATE IK CONTRACT (DECLARED here, red-first when physics wires in):
IK reads tick T−1's RESOLVED contact state, writes tick T's bone transforms, and
the one-tick lag is part of the witness — never hidden. Falsifier when built:
a fixture where same-tick IK would differ from lagged IK, with the lag visible
to `first_field_desync` as authority content, not as divergence. Until that
fixture exists this paragraph is a contract, not a capability.

GRADE (Stage 4 authority core, reference placement): maturity IMPLEMENTED;
evidence MEASURED via the `frontfps_pose` gate stage + `tests/test_fppose.py`.
Cross-placement: SPECULATIVE (queued, gates Stage 5). IK: DECLARED contract
only. `does_not_show`: contact response, root motion, ragdoll, any wall-clock
property. Falsifier: any independent implementation of this docstring
disagreeing with the pinned corpus digest.
"""
import hashlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PHYS = os.path.join(os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fpquat as FQ  # noqa: E402
import fpclip as FC  # noqa: E402
import frontfps as FW  # noqa: E402
from field import ONE, _rdiv  # noqa: E402

MAGIC = b"URDRPSE1"


class PoseError(Exception):
    def __init__(self, message):
        super().__init__(f"PSE-REFUSE: {message}")
        self.code = "PSE-REFUSE"


def _off3(bone):
    """Rig offsets are AUTHORING-GRID integers (frontfps law); the pose boundary
    converts them to Q32.32 raw exactly: ·ONE, no rounding. One conversion, one
    place, stated — never implicit."""
    off = bone.get("off", {"x": 0, "y": 0, "z": 0})
    return (off["x"] * ONE, off["y"] * ONE, off.get("z", 0) * ONE)


def pose_world(rig, pose, _div=_rdiv):
    """WORLD transforms for one rig + one pose (quats in rig bone order).
    Returns (world_q tuple, world_p tuple). PSE-REFUSE on shape mismatch."""
    bones = rig["bones"]
    if len(pose) != len(bones):
        raise PoseError(f"pose has {len(pose)} quats for {len(bones)} bones")
    wq = []
    wp = []
    for i, bone in enumerate(bones):
        q = tuple(pose[i])
        if i == 0:
            if bone["parent"] != -1:
                raise PoseError("bone 0 must be the root")
            wq.append(FQ.qnormalize(q, _div))
            wp.append(_off3(bone))
        else:
            p = bone["parent"]
            if not (0 <= p < i):
                raise PoseError(f"bone {i} parent {p} not topological")
            wq.append(FQ.qnormalize(FQ.qmul(wq[p], q, _div), _div))
            moved = FQ.vrotate(wq[p], _off3(bone), _div)
            wp.append(tuple(FQ._fg(a + b) for a, b in zip(wp[p], moved)))
    return tuple(wq), tuple(wp)


def _pose_world_defect_swapped_compose(rig, pose):
    """THE DEFECT: qmul(pose[i], world_q[parent]) — operands swapped. Quaternions
    do not commute; MUST diverge on any pose with two successive rotations."""
    bones = rig["bones"]
    wq = []
    wp = []
    for i, bone in enumerate(bones):
        q = tuple(pose[i])
        if i == 0:
            wq.append(FQ.qnormalize(q))
            wp.append(_off3(bone))
        else:
            p = bone["parent"]
            wq.append(FQ.qnormalize(FQ.qmul(q, wq[p])))          # swapped
            moved = FQ.vrotate(wq[p], _off3(bone))
            wp.append(tuple(a + b for a, b in zip(wp[p], moved)))
    return tuple(wq), tuple(wp)


def posed_capsules(rig, world_p, radii):
    """One capsule per non-root bone: parent world joint → bone world joint,
    authored integer radius ≥ 1 per bone name (PSE-REFUSE if missing/invalid)."""
    bones = rig["bones"]
    caps = []
    for i in range(1, len(bones)):
        name = bones[i]["name"]
        r = radii.get(name)
        if not isinstance(r, int) or isinstance(r, bool) or r < 1:
            raise PoseError(f"capsule radius for bone {name!r} missing or < 1 ({r!r})")
        p = bones[i]["parent"]
        caps.append({"bone": name, "a": world_p[p], "b": world_p[i], "r": r})
    return caps


def _posed_capsules_defect_local_offsets(rig, radii):
    """THE DEFECT: capsules from LOCAL offsets (rest skeleton), pose ignored.
    Identical on the identity pose; MUST fail coverage + diverge when posed."""
    bones = rig["bones"]
    lp = []
    for i, bone in enumerate(bones):
        if i == 0:
            lp.append(_off3(bone))
        else:
            p = bone["parent"]
            lp.append(tuple(a + b for a, b in zip(lp[p], _off3(bone))))
    return posed_capsules(rig, tuple(lp), radii)


def _in_capsule(pt, cap):
    """EXACT integer point-in-capsule: perpendicular/endpoint distance² vs r²,
    compared by cross-multiplication — no division, no float, no rounding."""
    a, b, r = cap["a"], cap["b"], cap["r"]
    d = tuple(bb - aa for aa, bb in zip(a, b))
    ap = tuple(pp - aa for aa, pp in zip(a, pt))
    dd = sum(c * c for c in d)
    if dd == 0:
        return sum(c * c for c in ap) <= r * r
    tn = sum(x * y for x, y in zip(ap, d))
    if tn <= 0:
        return sum(c * c for c in ap) <= r * r
    if tn >= dd:
        bp = tuple(pp - bb for bb, pp in zip(b, pt))
        return sum(c * c for c in bp) <= r * r
    ap2 = sum(c * c for c in ap)
    return ap2 * dd - tn * tn <= r * r * dd


def capsules_cover_joints(world_p, caps):
    """The certificate: every world joint inside at least one capsule."""
    return all(any(_in_capsule(pt, c) for c in caps) for pt in world_p)


def posed_digest(rig, pose, radii):
    wq, wp = pose_world(rig, pose)
    caps = posed_capsules(rig, wp, radii)
    h = hashlib.sha256()
    h.update(MAGIC)
    for q in wq:
        for c in q:
            h.update(int(c).to_bytes(8, "big", signed=True))
    for p in wp:
        for c in p:
            h.update(int(c).to_bytes(8, "big", signed=True))
    for cap in caps:
        h.update(cap["bone"].encode("ascii"))
        for pt in (cap["a"], cap["b"]):
            for c in pt:
                h.update(int(c).to_bytes(8, "big", signed=True))
        h.update(int(cap["r"]).to_bytes(8, "big", signed=True))
    return h.hexdigest()


def count_pose_world_ops(rig, pose):
    """Budget proxy: exact frozen-division count for one world-transform pass."""
    n = [0]

    def cdiv(p, d):
        n[0] += 1
        return _rdiv(p, d)
    pose_world(rig, pose, cdiv)
    return n[0]


# ---- the pinned corpus ------------------------------------------------------------------
RADII = {"spine": 12 * ONE, "head": 8 * ONE, "arm_l": 6 * ONE, "arm_r": 6 * ONE}


def demo_rig():
    return FW.demo_arena_duel()["rigs"]["biped"]


def demo_pose():
    """The Stage-3 corpus pose: demo_walk sampled at _rdiv(ONE, 3) — rotations
    live, so the swapped-compose defect diverges."""
    return FC.sample_pose(FC.demo_walk(), _rdiv(ONE, 3))


def demo_pose_reach():
    """The defect-arming pose: spine rotated 90° about z ((ONE,0,0,ONE) before
    normalization). Arm world joints swing ~14–24 authoring units away from
    their rest positions — far beyond the 6-unit arm radii — so LOCAL-offset
    capsules MUST fail coverage against the true world joints. Walk-pose
    rotations are deliberately subtle; this pose exists because a defect that
    only bites when the skeleton really moves needs a corpus pose that really
    moves."""
    return ((ONE, 0, 0, 0), (ONE, 0, 0, ONE), (ONE, 0, 0, 0),
            (ONE, 0, 0, 0), (ONE, 0, 0, 0))


if __name__ == "__main__":
    rig, pose = demo_rig(), demo_pose()
    d = posed_digest(rig, pose, RADII)
    print("posed_biped digest:", d)
    wq, wp = pose_world(rig, pose)
    caps = posed_capsules(rig, wp, RADII)
    print("coverage certificate:", capsules_cover_joints(wp, caps))
    dq, dp = _pose_world_defect_swapped_compose(rig, pose)
    print("swapped-compose defect diverges:", (dq, dp) != (wq, wp))
    _, wp_reach = pose_world(rig, demo_pose_reach())
    bad = _posed_capsules_defect_local_offsets(rig, RADII)
    print("local-offset defect fails coverage on the reach pose:",
          not capsules_cover_joints(wp_reach, bad))
    print("real capsules cover the reach pose:",
          capsules_cover_joints(wp_reach, posed_capsules(rig, wp_reach, RADII)))
    print("ops per world-transform pass:", count_pose_world_ops(rig, pose))
