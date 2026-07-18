# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""crosswarden — cross-region structural anti-cheat (T3.25, MMO Stage E, the D+E synthesis): the seamless
handoff seam (`hand`, URDRHAND1) is made CHEAT-PROOF. A claimed crossing is admitted against the MERGED
authority — `F_A` west of the split, `F_B` east — the SAME merge the handoff itself produces, not against
either shard's stale view of its neighbor. `warden` (URDRWARD1) turned reconstruct-or-refuse against the
cheater on ONE field; `crosswarden` turns it against the cheater who exploits the REGION BOUNDARY.

THE EXPLOIT CLASS. A shard holds only its own field and a stale copy of its neighbor's. Shard A, checking a
crossing against `F_A` alone, ADMITS a move that is only legal because A's copy of the east region is stale
(flat where B has since raised a wall). The cheat lives exactly in the disagreement between a shard's local
view and the merged truth.

THE HEADLINE (measured): A SHARD-LOCAL WARDEN IS INSUFFICIENT. On the pinned world, the exploit trajectory
(a sprint east across the seam and through B's wall) and the exploit position (a cell beyond B's wall,
claimed reachable from a west anchor) BOTH ADMIT under `warden.admit_trajectory(F_A, ...)` / `admit_position(
F_A, ...)` — the shard-local check passes the cheat — while `crosswarden.admit_crossing(F_A, F_B, ...)` /
`admit_crossing_position(...)` REFUSE both with their typed `WARD-TUNNEL` / `WARD-UNREACH`, because the merge
carries B's real wall. Only the merged-authority warden catches it.

THE TWO CERTIFICATES, against the merge (both exact, division-free):
  * KINEMATIC — each claimed step must be legal under `F_merged` (`Δground ≤ MAX_STEP`); a step that climbs
    B's wall is a `WARD-TUNNEL`, a diagonal or > 2-cell jump a `WARD-TELEPORT`. An honest `hand.handoff`
    trajectory always admits — and it equals `hand.merged_glide` bit-for-bit, so the warden certifies against
    exactly the world the handoff traverses (the Stage D <-> Stage E tie).
  * TOPOLOGICAL — β₀ = rank H₀ of the MERGED walkable graph. B's wall raises the merged component count above
    the stale shard's (β₀(F_merged) = 3 vs β₀(F_A) = 1 on the pinned world), so a position beyond the wall is
    in a DIFFERENT component from the west anchor — `WARD-UNREACH`, from the merged field alone.

Precondition: the shards must be SYNCED on the boundary band `[split-band, split+band)` (`hand.seam_ok`); a
desynced band has no canonical merge to certify against and is a `WARD-SEAM` refusal.

GRADE. The merged-authority admission/refusal (tunnel, teleport, unreach), the shard-local INSUFFICIENCY
witness, the merged-topology non-vacuity (β₀ genuinely rises across the merge), the honest-handoff-admits-and-
equals-merged tie, and their determinism are MEASURED (exact, reproducible, a defect diverges).
`does_not_show`: DIRECTED reachability (this uses UNDIRECTED components, as URDRWARD1 does — a follow-on);
the network TRANSPORT of the neighbor field (who ships `F_B` to whom); the URDRPD1 homology CROSS-PLACEMENT
(β₀ computed directly here, as in URDRWARD1); NON-MONOTONE crossings (this certifies the east crossing, as
`hand` does); and any WALL-CLOCK cost (`NOT_MEASURED` until a sealed bench, Stage H). Refusals are typed
`WARD-REFUSE` with a sub-code (`WARD-TUNNEL`, `WARD-TELEPORT`, `WARD-UNREACH`, `WARD-SEAM`, or a malformed
`WARD-MALFORMED`): refuse, never admit a cheat that hides in the seam."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWARD2"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import warden as _W                                              # single-field anti-cheat (URDRWARD1)
import hand as _H                                                # cross-region handoff + merge (URDRHAND1)
import glide as _GL                                              # the continuous mover (for honest handoffs)


def merged_field(field_a, field_b, split):
    """The canonical merged world the crossing is certified against — IDENTICAL to `hand.merge` (Stage D):
    `field_a` west of `split`, `field_b` at/east of it. The single-authority reference, reused verbatim."""
    return _H.merge(field_a, field_b, split)


def _require_synced(field_a, field_b, split, band):
    """The shards must agree on the boundary band, else there is no canonical merge to certify against."""
    lo, hi = split - band, split + band
    if not _H.seam_ok(field_a, field_b, lo, hi):
        raise _W.WardError("WARD-SEAM", f"shards disagree on the sync band [{lo},{hi}) — no canonical merge")
    return lo, hi


def admit_crossing(field_a, field_b, split, band, cells, max_step):
    """ADMIT a claimed cross-region trajectory iff every step is legal against the MERGED authority (not either
    shard's stale view). Requires a synced seam band. Raises the warden's typed `WardError` (`WARD-TUNNEL` /
    `WARD-TELEPORT`) on the first illegal move, or `WARD-SEAM` when the shards are desynced. Pure."""
    _require_synced(field_a, field_b, split, band)
    return _W.admit_trajectory(merged_field(field_a, field_b, split), cells, max_step)


def admit_crossing_position(field_a, field_b, split, band, anchor, claim, max_step):
    """ADMIT a bare claimed position iff it is REACHABLE from the anchor in the MERGED world. Catches the
    boundary-exploit teleport — a cell reachable in a shard's stale view but unreachable once the neighbor
    region's real terrain is merged in — `WARD-UNREACH`, from the merged field alone, no trajectory."""
    _require_synced(field_a, field_b, split, band)
    return _W.admit_position(merged_field(field_a, field_b, split), anchor, claim, max_step)


def shard_admits_trajectory(field, cells, max_step):
    """Does a SHARD-LOCAL warden (one field, no merge) admit this claim? True/False. The witness that a
    shard-local warden is INSUFFICIENT: it returns True for the exploit the cross-region warden refuses."""
    try:
        _W.admit_trajectory(field, cells, max_step)
        return True
    except _W.WardError:
        return False


def shard_admits_position(field, anchor, claim, max_step):
    """Does a SHARD-LOCAL warden admit this bare position? True/False (the position half of the witness)."""
    try:
        _W.admit_position(field, anchor, claim, max_step)
        return True
    except _W.WardError:
        return False


def cross_betti0(field_a, field_b, split, max_step):
    """β₀ = rank H₀ of the MERGED walkable graph — the component structure the cross-region check certifies
    against. Rises above a stale shard's when the neighbor region adds a wall."""
    return _W.betti0(merged_field(field_a, field_b, split), max_step)


def crosswarden_digest(name, field_a, field_b, split, band, max_step, verdict):
    """The URDRWARD2 canon — SHA-256(MAGIC | name | β₀(merged) | seam-digest | verdict). Binds the MERGED
    topology, the synced-seam bytes (a desync moves the digest), and the verdict, so a changed neighbor region
    or a changed verdict is a different certificate."""
    merged = merged_field(field_a, field_b, split)
    lo, hi = split - band, split + band
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|b0:{_W.betti0(merged, max_step)}".encode())
    hh.update(f"|seam:{_H.seam_digest(field_a, field_b, lo, hi)}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
# Two shards of a 16x16 world, synced on the band [6,10) around split=8. Shard A is FLAT everywhere (its stale
# view of the east region). Shard B has raised an impassable wall (height 200) at x=12 — EAST of the band, so
# the shards still agree on the seam, but the MERGE carries B's wall. That wall is the whole game: it is
# invisible to a shard-local A-warden and decisive to the cross-region warden.
_MS = 40
_SPLIT = 8
_BAND = 2
_WALLX = 12


def _shards():
    w = h = 16
    field_a = tuple(tuple(0 for _x in range(w)) for _y in range(h))
    field_b = tuple(tuple(200 if x == _WALLX else 0 for x in range(w)) for _y in range(h))
    return field_a, field_b


def _desynced_shards():
    """Shard B disagrees with A on a band cell (x=7) — an unsynced seam, no canonical merge."""
    fa, fb = _shards()
    fb2 = tuple(tuple(v + 5 if (x == 7 and y == 8) else v for x, v in enumerate(row))
                for y, row in enumerate(fb))
    return fa, fb2


# the pinned exploit claims (reused by the gate + tests as the shard-local-insufficiency witness)
_HONEST_CELLS = tuple((2 + i, 8) for i in range(10))            # (2,8)->(11,8): crosses split, stops < wall
_TUNNEL_CELLS = tuple((6 + i, 8) for i in range(8))            # (6,8)->(13,8): sprints across seam THROUGH wall
_ANCHOR, _BEYOND = (2, 8), (14, 8)                             # west anchor; a cell east of B's wall


def honest_cross():
    """An honest actor crosses the seam (west -> east of split) and stops before B's wall -> ADMIT vs merge."""
    fa, fb = _shards()
    v = admit_crossing(fa, fb, _SPLIT, _BAND, _HONEST_CELLS, _MS)
    return "honest_cross", fa, fb, v


def seam_tunnel():
    """A cheat crosses the seam and steps through B's wall — legal on A's flat stale view, `WARD-TUNNEL` vs the
    merge (the wall B raised is carried by the merged authority)."""
    fa, fb = _shards()
    try:
        v = admit_crossing(fa, fb, _SPLIT, _BAND, _TUNNEL_CELLS, _MS)
    except _W.WardError as exc:
        v = exc.sub
    return "seam_tunnel", fa, fb, v


SCENES = {"honest_cross": honest_cross, "seam_tunnel": seam_tunnel}


def scene_result(name):
    """Run a named cross-region scenario -> its URDRWARD2 digest. Same host, same bytes."""
    nm, fa, fb, verdict = SCENES[name]()
    return crosswarden_digest(nm, fa, fb, _SPLIT, _BAND, _MS, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_crosswarden.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise _W.WardError("WARD-MALFORMED", f"no golden named {name!r}")
