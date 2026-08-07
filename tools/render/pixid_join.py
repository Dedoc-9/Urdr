# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""THE JOIN (URDRPIDJ1) — `pixid` and `view_witness` agree on the visible world.

The narrow claim, and nothing wider: **the pixel-level witness and the scene-level witness
line up on which world is visible, and that agreement is sealed structurally.** Not that
`pixid` is correct, not that the renderer is correct, not any thesis about visual fidelity.

## What could not be built, and why

The requested law was "the visible instance set reported by `pixid` matches what
`view_witness` says is present, and removing the occluder makes the hidden instance appear
in BOTH". `view_witness` has no instance vocabulary. It parses `terrain_view3d.html` for an
embedded blob citing two authority digests — `hf_witness` (the URDRHF1 island heightfield)
and `wave_witness` (URDRWAV1 swell@0) — and checks the citation is live and the knob
namespace is disjoint from it. There is no set of instances on that side to compare against,
and inventing one here would be a join to a thing I had just written.

So the join binds **worlds**, not instance sets, and the occluder-reveal stays a `pixid`-side
property where it already lives. Removing a derived instance does not change the heightfield,
so it cannot move `hf_witness`; a test asserting it did would be measuring the fixture.

## What the join actually is

A CHAIN, and every link is recomputed rather than asserted:

    the view cites  hf_witness
      -> which must equal the LIVE heightfield digest        (link 1)
      -> which regenerates the SAME height array             (link 2)
      -> which derives the primitive list, purely            (link 3)
      -> which pixid renders into an ownership buffer        (link 4)

`pixid`'s scene is therefore a function of the world the HTML cites, not merely co-located
with it. Break any link — flip a hex in the citation, move one height, forge one primitive,
forge the ownership buffer — and the join fails. That is the whole rung.

## does_not_show

Any new rendering law: `pixid`'s permutation invariance, oracle agreement, subset behaviour
and structural firewall are certified by `pixid-*` and are not restated here. Any
performance claim. That the derived primitives RESEMBLE the terrain — the derivation is a
deterministic tiling chosen to produce occlusion, not a terrain renderer, and a different
derivation would give a different scene digest and an equally valid join. That
`wave_witness` participates: the join binds the heightfield only, because that is the
authority the derivation reads. Cross-placement: single-implementation, like `pixid`.
`integrity != truth`.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (_HERE, os.path.join(_HERE, "..", "terrain")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import heightfield as HF                                                  # noqa: E402
import pixid as PX                                                        # noqa: E402
import view_witness as VW                                                 # noqa: E402
from raster import SUB, RenderError                                       # noqa: E402

#: The join's view. Deliberately small and fixed: this rung is about the binding, not
#: about resolution. Admitted by `renderbound` through `pixid.IdFramebuffer`.
JOIN_VIEW = (16, 16, 0, 1000)

#: A 4x4 tile grid at stride 4 with 6-pixel tiles, so adjacent tiles overlap by two.
GRID, STRIDE, TILE = 4, 4, 6

#: Each cell emits an OUTER tile and a strictly smaller INNER one, offset in depth. With
#: the offset POSITIVE the inner tile is strictly farther and strictly inside, so it is
#: hidden by construction and the visible set is a PROPER subset of the submitted set on
#: any heightfield. The first derivation relied on neighbouring tiles happening to cover
#: each other, and on the island they did not: every one of the 16 instances stayed
#: visible, so `visible < submitted` was false and the join correctly refused. Occlusion
#: has to be a property of the derivation, not a hope about the data.
INNER_DEPTH_OFFSET = 1


def _sample(heights, w, h):
    """The GRID*GRID heights this derivation reads, in canonical order. `heights` is
    row-major NESTED (`heights[y][x]`), 64x64 for the island."""
    return [heights[min(h - 1, gy * max(1, h // GRID))][min(w - 1, gx * max(1, w // GRID))]
            for gy in range(GRID) for gx in range(GRID)]


def primitives_from_heights(heights, w, h):
    """Derive a primitive list from a heightfield, PURELY — link 3 of the chain.

    Each of the GRID*GRID tiles becomes one instance of two triangles, and TALLER terrain
    is NEARER, so it occludes its shorter neighbours through the overlap. The depth map is
    derived from the SAMPLED RANGE rather than from `VMAX`: the island's heights occupy a
    narrow band far below the 16-bit ceiling, and a VMAX-relative map collapsed every tile
    onto the same depth — every equality in the join would still have held while nothing
    occluded anything. Integer throughout; no float touches this."""
    vals = _sample(heights, w, h)
    lo, hi = min(vals), max(vals)
    span = hi - lo
    prims = []
    for gy in range(GRID):
        for gx in range(GRID):
            v = vals[gy * GRID + gx]
            # taller -> smaller z -> nearer. A flat field gives every tile z=1, which
            # `the_overlap_is_load_bearing` is there to notice.
            z = 1 if span == 0 else 1 + (hi - v) * 998 // span
            cell = gy * GRID + gx
            x0, y0 = gx * STRIDE, gy * STRIDE
            for iid, inset, zz in ((cell, 0, z),
                                   (GRID * GRID + cell, 1, z + INNER_DEPTH_OFFSET)):
                ax, ay = x0 + inset, y0 + inset
                bx, by = x0 + TILE - inset, y0 + TILE - inset
                prims.append(((ax * SUB, ay * SUB), (bx * SUB, ay * SUB),
                              (ax * SUB, by * SUB), (zz, zz, zz), iid, 0))
                prims.append(((bx * SUB, ay * SUB), (bx * SUB, by * SUB),
                              (ax * SUB, by * SUB), (zz, zz, zz), iid, 1))
    return tuple(prims)


def join(html_text, scene="island"):
    """Walk the chain and return every link, so a failure names which one broke."""
    blob, _knobs = VW.parse_view(html_text)
    live = VW.live_witnesses()
    params = HF.SCENES[scene]()
    world, heights = HF.scene_digest(params)
    prims = primitives_from_heights(heights, params["w"], params["h"])
    fb = PX.IdFramebuffer(*JOIN_VIEW).render(prims)
    return {
        "cited": blob["hf_witness"],        # what the view says the world is
        "live": live["hf_witness"],         # what view_witness recomputes it to be
        "world": world,                     # what the heightfield module computes
        "scene": PX.scene_digest(prims),    # the pixel witness's citation
        "frame": fb.digest(),
        "visible": fb.instances(),
        "submitted": frozenset(p[4] for p in prims),
        "oob": fb.oob,
    }


def pixid_view_join_agrees(html_text=None, scene="island"):
    """THE POSITIVE. Every link holds and the pixel side is non-vacuous.

    Links 1 and 2 are digest equalities across three independently-computed values.
    Link 3 is purity: deriving twice from the same heights gives the same citation.
    Link 4 is that the buffer actually occluded something — a visible set equal to the
    submitted set would satisfy every equality above while proving the render never ran."""
    html = VW.read_view(VW.VIEWS[0][0]) if html_text is None else html_text
    j = join(html, scene)
    if not (j["cited"] == j["live"] == j["world"]):
        return False
    params = HF.SCENES[scene]()
    _w2, heights2 = HF.scene_digest(params)
    again = PX.scene_digest(primitives_from_heights(heights2, params["w"], params["h"]))
    return (again == j["scene"]
            and j["oob"] == 0
            and len(j["visible"]) > 0
            and j["visible"] < j["submitted"])


def pixid_view_join_rejects_forgery(scene="island"):
    """THE PLANT. Four forgeries, one per link. Each must break the join, and the join
    must be green again afterwards — otherwise the reds are leakage, not detection.

    Returns the tuple of per-forgery verdicts so a partial failure is legible."""
    html = VW.read_view(VW.VIEWS[0][0])
    out = []

    # link 1 — the view cites a world that is not the live one (one hex char flipped)
    out.append(not pixid_view_join_agrees(VW.forge_citation(html), scene))

    # link 2 — the world moves under a citation that does not: one height changed, so
    # the derived scene must no longer be the scene this world produces
    params = HF.SCENES[scene]()
    _w, heights = HF.scene_digest(params)
    honest = PX.scene_digest(primitives_from_heights(heights, params["w"], params["h"]))
    # one CELL, not one row: `heights` is nested, so `moved[0] = ...` would replace a
    # whole scanline and overstate what a single-cell change proves.
    rows = [list(r) for r in heights]
    gy0 = min(params["h"] - 1, 0)
    gx0 = min(params["w"] - 1, 0)
    rows[gy0][gx0] = rows[gy0][gx0] + 1
    moved = tuple(tuple(r) for r in rows)
    forged = PX.scene_digest(primitives_from_heights(moved, params["w"], params["h"]))
    out.append(forged != honest)

    # link 3 — one primitive forged: the citation must move even though the world did not
    prims = list(primitives_from_heights(heights, params["w"], params["h"]))
    v0, v1, v2, zs, iid, pid = prims[0]
    prims[0] = (v0, v1, v2, zs, iid + 1, pid)
    out.append(PX.scene_digest(prims) != honest)

    # link 4 — the ownership buffer forged: swap one pixel's owner and the frame must move
    fb = PX.IdFramebuffer(*JOIN_VIEW).render(
        primitives_from_heights(heights, params["w"], params["h"]))
    before = fb.digest()
    idx = next(i for i, v in enumerate(fb.iid) if v != PX.EMPTY)
    fb.iid[idx] = fb.iid[idx] + 1
    out.append(fb.digest() != before)

    # and the instrument returns to green: the reds above are the plants
    out.append(pixid_view_join_agrees(html, scene))
    return tuple(out)


def the_occlusion_is_load_bearing(scene="island"):
    """NON-VACUITY of the derivation itself (L61). The subset clause is evidence only if
    something can fail it, so the control flips `INNER_DEPTH_OFFSET` negative — putting
    the inner tile in FRONT — and requires **every instance the positive hides to become
    visible**. Positive and control differ in that one integer and nowhere else.

    The obvious stronger law, "the control hides NOTHING", is FALSE and was measured to
    be: with the inner tiles in front, 30 of 32 instances are visible, not 32, because two
    outer tiles are then hidden by nearer neighbours. Asserting 32 would have been a claim
    about the island's heights dressed as a claim about the derivation.

    (At offset 0 — an exact tie between inner and outer — all 16 inner tiles stay hidden,
    because ownership goes to the smaller `(instance, primitive)` pair and the outer ids
    are lower. That is `raster3d`'s tie-break law showing up here unbidden; it is not
    asserted as this rung's evidence.)"""
    params = HF.SCENES[scene]()
    _w, heights = HF.scene_digest(params)
    global INNER_DEPTH_OFFSET
    prims = primitives_from_heights(heights, params["w"], params["h"])
    fb = PX.IdFramebuffer(*JOIN_VIEW).render(prims)
    submitted = frozenset(p[4] for p in prims)
    hidden = submitted - fb.instances()
    if not (fb.instances() < submitted and hidden):
        return False
    saved, INNER_DEPTH_OFFSET = INNER_DEPTH_OFFSET, -1
    try:
        front = primitives_from_heights(heights, params["w"], params["h"])
        revealed = PX.IdFramebuffer(*JOIN_VIEW).render(front).instances()
    finally:
        INNER_DEPTH_OFFSET = saved
    return hidden <= revealed


# =====================================================================================
# THE JOINED WITNESS (URDRJOIN1) — minting the record, and sealing the granularity.
#
# Everything above RECOMPUTES the chain at check time and returns booleans. Nothing is
# MINTED: there is no artifact a third party could hold and verify. That gap is what this
# section closes, and it is the whole of this rung — the happy join and the forged-witness
# case already ship as `pixid-view-join` / `pixid-view-join-forgery`.
#
# THE FAILURE MODE BEING SEALED. A verifier that returns ONE boolean cannot say which
# level it checked. World-correct/pixel-forged and pixel-correct/world-forged both come
# back False, so a caller reading a green result cannot tell whether the pixel ownership
# was ever examined — and a world-level agreement silently stands in for a pixel-level
# one. `verify_joined` therefore returns a PAIR of named verdicts and there is no
# single-boolean sibling. `granularity_is_sealed` proves both halves are independently
# reachable; if they were not, the pair would be decoration on a scalar.
# =====================================================================================
import hashlib                                                            # noqa: E402

JOIN_MAGIC = b"URDRJOIN1"

WORLD_OK, WORLD_BAD = "WORLD-OK", "WORLD-MISMATCH"
PIXEL_OK, PIXEL_BAD = "PIXEL-OK", "PIXEL-MISMATCH"


def joined_witness(html_text=None, scene="island"):
    """MINT the record. A pure function of shipped code plus the view HTML: no clock, no
    randomness, no hidden state, so any holder can recompute it byte-for-byte.

    `digest` commits to BOTH levels. That is the point — a record whose digest were a
    function of the world alone would let two different renders of the same world share
    an identity, which is exactly the widening this rung exists to prevent."""
    html = VW.read_view(VW.VIEWS[0][0]) if html_text is None else html_text
    j = join(html, scene)
    rec = {
        "world": j["cited"],
        "scene": j["scene"],
        "frame": j["frame"],
        "visible": tuple(sorted(j["visible"])),
    }
    rec["digest"] = join_digest(rec)
    return rec


def join_digest(rec):
    """The record's identity. Order-fixed and length-prefixed so no two distinct records
    can collide by re-partitioning the same bytes."""
    h = hashlib.sha256()
    h.update(JOIN_MAGIC)
    for key in ("world", "scene", "frame"):
        v = rec[key].encode("ascii")
        h.update(len(v).to_bytes(2, "big"))
        h.update(v)
    vis = rec["visible"]
    h.update(len(vis).to_bytes(4, "big"))
    for i in vis:
        h.update(int(i).to_bytes(4, "big"))
    return h.hexdigest()


def verify_joined(rec, html_text=None, scene="island"):
    """Recompute both levels from shipped code and return `(world_verdict, pixel_verdict)`.

    NEVER a single boolean. The two levels are checked against independently derived
    values — the world against `view_witness`'s live recomputation, the pixel side against
    a fresh render — and reported separately, so a caller can never mistake one for the
    other. A malformed record is a typed refusal rather than a mismatch, because "this
    record is wrong" and "this is not a record" are different facts."""
    for key in ("world", "scene", "frame", "visible", "digest"):
        if key not in rec:
            raise RenderError("JOIN-REFUSE", f"record is missing {key!r}")
    if join_digest(rec) != rec["digest"]:
        raise RenderError("JOIN-REFUSE", "record digest does not commit to its own fields")
    html = VW.read_view(VW.VIEWS[0][0]) if html_text is None else html_text
    j = join(html, scene)
    world = WORLD_OK if (rec["world"] == j["cited"] == j["live"] == j["world"]) else WORLD_BAD
    pixel = PIXEL_OK if (rec["scene"] == j["scene"] and rec["frame"] == j["frame"]
                         and rec["visible"] == tuple(sorted(j["visible"]))) else PIXEL_BAD
    return (world, pixel)


def _reseal(rec, **changes):
    out = dict(rec)
    out.update(changes)
    out["digest"] = join_digest(out)
    return out


def granularity_is_sealed(scene="island"):
    """FALSIFIER 3. Both halves must be INDEPENDENTLY reachable, or the pair is decoration
    on a scalar and the join can silently widen a world-level pass into a pixel-level
    claim. Returns the three verdict pairs so a failure names which half collapsed.

      world-correct / pixel-forged  -> (WORLD-OK,       PIXEL-MISMATCH)
      world-forged  / pixel-correct -> (WORLD-MISMATCH, PIXEL-OK)
      both honest                   -> (WORLD-OK,       PIXEL-OK)

    The second case is the one that could not be built without minting a record: it needs
    a pixel side that is genuinely correct while the cited world is wrong, which no
    recompute-at-check-time chain can express."""
    html = VW.read_view(VW.VIEWS[0][0])
    honest = joined_witness(html, scene)

    # world-correct, pixel-forged: one flipped hex in the frame the record claims
    f = honest["frame"]
    pixel_forged = _reseal(honest, frame=("1" if f[0] != "1" else "2") + f[1:])

    # world-forged, pixel-correct: the record cites a world the view does not
    w = honest["world"]
    world_forged = _reseal(honest, world=("1" if w[0] != "1" else "2") + w[1:])

    return (verify_joined(pixel_forged, html, scene),
            verify_joined(world_forged, html, scene),
            verify_joined(honest, html, scene))


def the_record_commits_to_both_levels(scene="island"):
    """The digest is a function of every field, so no component can be swapped silently.
    Without this the pair of verdicts could be honest while the record's identity was
    decided by the world alone."""
    honest = joined_witness(None, scene)
    moved = []
    for key in ("world", "scene", "frame"):
        v = honest[key]
        moved.append(join_digest({**honest, key: ("1" if v[0] != "1" else "2") + v[1:]})
                     != honest["digest"])
    moved.append(join_digest({**honest, "visible": honest["visible"][:-1]})
                 != honest["digest"])
    return all(moved) and len(moved) == 4


def a_malformed_record_is_refused():
    """"This record is wrong" and "this is not a record" are different facts, and a join
    that returned MISMATCH for both would report a forgery where there was a typo."""
    honest = joined_witness()
    for bad in ({k: v for k, v in honest.items() if k != "frame"},
                {**honest, "digest": "0" * 64},
                {}):
        try:
            verify_joined(bad)
            return False
        except RenderError as exc:
            if exc.code != "JOIN-REFUSE":
                return False
    return True
