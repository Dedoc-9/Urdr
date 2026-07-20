# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""panewire — THE WIRED WINDOW (T3.53, V2, URDRPNW1): the whole arc composed in one live loop. V1
`panelight` drove the certified world as a game; this rung makes that world REPLICATED and
STREAMED — movement (panelight's tick), replication (wire's equal-or-refuse admission), and
streaming (driftgaze's verified acquisition) meeting to drive one avatar over a world it does not
hold whole and did not author alone. The first playable NETWORKED world: two windows, one
authority, an edit made in one view appearing in the other, every byte admitted rather than
trusted.

THE MODULE MINTS NOTHING. The avatar folds with `glide`'s exact micro-step law, but through a
RESIDENT getter (`chunkload.height_at`, which refuses on an unloaded chunk) instead of a full
field — so the fold is the certified mover, now reading a replica. Edits admit through
`driftgaze.gaze_admit` = `wire.client_admit` (unmodified). Acquisition is `driftgaze.acquire` =
`chunkload`'s verified fetch. Every law here is composition; the novelty is that the three only
compose correctly under new invariants:

  RESIDENT-OR-REFUSE. The avatar reads the resident REPLICA, not the field. A step into an
  unresident region refuses (CHUNK-REFUSE — never walks on unloaded terrain) until the region is
  ACQUIRED by verified fetch. Interest follows the avatar: the loop streams in the region it is
  about to enter, from the CURRENT authority, so it never holds an unverified chunk.

  LIVE EDIT CHANGES THE WALKED WORLD. A terraform edit admitted mid-play to a resident region
  changes the terrain the avatar THEN walks on — a raised wall stops a walk that would otherwise
  pass. The world is live authority, not a backdrop; the loop reads it fresh each tick.

  TWO WINDOWS, ONE AUTHORITY. The composed witness (avatar transcript + replica) is a pure function
  of (input, edits): two independent runs land the IDENTICAL witness — the edit in one window is
  seen in the other — and a different edit stream lands a different witness (the world is
  authoritative, not cosmetic).

  EQUAL-OR-REFUSE UNDER PLAY. A tampered or foreign edit woven into the stream refuses mid-loop with
  the replica byte-unchanged, and the avatar's walk is UNPERTURBED — malice moves neither the world
  nor the player (wire's verifier discipline, now under a live game).

GRADE. Resident-or-refuse, acquire-on-cross, live-edit-changes-the-walk, the composed-witness
determinism (two windows one authority; different edits diverge), and equal-or-refuse-under-play
are MEASURED (exact, reproducible, a defect diverges). DECLARED, honestly: the demand/acquire
POLICY is operational (the law certified is the loop's evolution under this policy — acquire the
step's demand from the current authority); wall-clock frame timing is `panelight`'s accumulator and
lives OFF-GATE (the window feeds real dt); WHO may edit is `sealwrit`'s signature (composable, not
re-proven here — a lawful edit admits whoever relays it); ghosts (other actors) are `ghostsnap`
(V3). `does_not_show`: fps/latency (bench §3, V4); the depicting client's own correctness (the
`panewire.html` two-window demo is declared); cross-placement (URDRPNW1 joins the frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRPNW1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK
import driftgaze as _DG
import glide as _GL
import rannull as _RN
import wire as _WR
from field import ONE


class PaneWireError(Exception):
    def __init__(self, message):
        super().__init__(f"PANEWIRE-REFUSE: {message}")
        self.code = "PANEWIRE-REFUSE"


# ---- the resident fold: glide's micro-step law, read THROUGH the replica ----------------
def _resident_step(view, pose, cmd, max_step, sub):
    """Fold ONE command from a resumable Q32.32 pose over the RESIDENT view — glide's exact
    micro-step law with `chunkload.height_at` as the getter (a CHUNK-REFUSE on any unloaded read
    aborts the whole step: equal-or-refuse, never unloaded-terrain-as-wall). Returns the new pose."""
    k = sub.bit_length() - 1
    mstep = ONE >> k
    fx, fy, _g, _f = pose
    dl, gait = _GL._parse(cmd)
    dx, dy = _CK._ST.DIRS[dl] if hasattr(_CK, "_ST") else _GL._ST.DIRS[dl]
    facing = _GL._FACE[dl]
    w, h = view["w"], view["h"]
    cx, cy = fx >> 32, fy >> 32
    sfx, sfy = mstep * dx, mstep * dy
    for _ in range(_GL.GAIT[gait] * sub):
        nfx, nfy = fx + sfx, fy + sfy
        ncx, ncy = nfx >> 32, nfy >> 32
        if (ncx, ncy) != (cx, cy):
            if not (0 <= ncx < w and 0 <= ncy < h):
                break
            if _CK.height_at(view, ncx, ncy) - _CK.height_at(view, cx, cy) > max_step:
                break
            cx, cy = ncx, ncy
        fx, fy = nfx, nfy
    return (fx, fy, _CK.height_at(view, cx, cy), facing)


def _server(field, c):
    chunks = _CK.cut(field, c)
    return _CK.field_manifest(field, c), {_CK.address(r): r for r in chunks.values()}


def _edit_record(man, store, x, y, dh, c):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    chunk = store[grid[(x // c, y // c)]]
    kx, ky, cells = _CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)


def _serve(man, store, rec):
    new_chunk = _RN.shard_apply(store[_RN.restore_regional(rec)[0]], rec)
    new_man = _RN.reunify(man, (new_chunk,))
    store2 = dict(store)
    store2[_CK.address(new_chunk)] = new_chunk
    return new_man, store2


def _demand_one(field, cell, cmd, max_step, sub, c):
    """The chunk demand for ONE command from a cell — driftgaze's fetch target for this step."""
    return _CK.demand_chunks(field, cell, cmd, max_step, sub, c)


def run_wired(field, start, input_log, edits, sub, max_step, c=8, acquire=True):
    """THE WIRED LOOP. Drive one avatar over a REPLICATED, STREAMED world: each tick admits any
    scheduled terraform edit (wire law), ACQUIRES the region the step needs (driftgaze verified
    fetch, from the current authority), then folds one command over the resident replica. `edits`
    maps tick index -> ("edit", x, y, dh) | ("malice",). Returns {transcript, client, acquired,
    released, refusals, witness}. With acquire=False the loop never streams — a crossing refuses."""
    if not (isinstance(input_log, str) and 1 <= len(input_log) <= _GL.LOG_MAX):
        raise PaneWireError(f"input log must be a str of 1..{_GL.LOG_MAX} commands, got {input_log!r}")
    man, store = _server(field, c)
    x0, y0 = start
    client = _DG.subscribe_gaze(field, c, frozenset({(x0 // c, y0 // c)}))
    facing0 = _GL._FACE[_GL._parse(input_log[0])[0]] if input_log else _GL._FACE["E"]
    pose = (x0 * ONE, y0 * ONE, field[y0][x0], facing0)
    transcript = [pose]
    acquired = released = refusals = 0
    for i, cmd in enumerate(input_log):
        # 1. LIVE EDIT: admit a scheduled edit through the wire law (or refuse malice)
        if i in edits:
            spec = edits[i]
            if spec[0] == "edit":
                _tag, ex, ey, dh = spec
                rec = _edit_record(man, store, ex, ey, dh, c)
                key = (ex // c, ey // c)
                if key in client["chunks"]:
                    client = _DG.gaze_admit(client, rec)      # replica admits (CAS in lockstep)
                man, store = _serve(man, store, rec)          # authority advances
            elif spec[0] == "malice":
                # a tampered regional record for a resident region — must refuse, replica unchanged
                good = _edit_record(man, store, x0, y0, 1, c)
                bad = bytearray(good)
                bad[50] ^= 0x01
                try:
                    client = _DG.gaze_admit(client, bytes(bad))
                    raise PaneWireError("malice admitted — the verifier failed")
                except _WR.WireError:
                    refusals += 1
            else:
                raise PaneWireError(f"unknown edit spec {spec!r}")
        # 2. ACQUIRE: stream in the region this step needs (verified fetch from the authority)
        if acquire:
            cell = (pose[0] >> 32, pose[1] >> 32)
            field_now = _CK.reassemble(man, store)
            need = _demand_one(field_now, cell, cmd, max_step, sub, c)
            missing = need - set(client["chunks"])
            if missing:
                client = _DG.acquire(client, man, store, missing)
                acquired += len(missing)
        # 3. STEP: fold one command over the resident replica (resident-or-refuse)
        try:
            pose = _resident_step(_DG.resident_view(client), pose, cmd, max_step, sub)
        except _CK.ChunkError as exc:
            raise PaneWireError(f"the avatar stepped onto unloaded terrain: {exc}")
        transcript.append(pose)
    return {"transcript": tuple(transcript), "client": client, "acquired": acquired,
            "released": released, "refusals": refusals,
            "witness": composed_witness(tuple(transcript), client)}


def composed_witness(transcript, client):
    """The composed authority: SHA-256 over BOTH the avatar transcript AND the replica witness —
    the player and the world are one authority in a networked game."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for (fx, fy, g, facing) in transcript:
        hh.update(f"|{fx},{fy},{g},{facing}".encode())
    hh.update(b"|world:")
    hh.update(_DG.gaze_witness(client).encode())
    return hh.hexdigest()


def panewire_digest(name, witness_hex, ticks, acquired, refusals, verdict):
    """URDRPNW1 canon — SHA-256(MAGIC | name | witness | ticks | acquired | refusals | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|t:{ticks}|a:{acquired}|r:{refusals}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    return _GL._heights("blank")


def _scene_crossing():
    """The avatar walks east across a region seam; the loop streams in region (1,1) by verified
    fetch and the walk completes equal to the full-field glide — interest followed the avatar."""
    fld = _blank()
    out = run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
    ok = (out["transcript"] == _GL.glide_cells(fld, (2, 8), "EEEEEE", 4000, 4)
          and out["acquired"] > 0)
    return out["witness"], len(out["transcript"]) - 1, out["acquired"], out["refusals"], \
        ("ADMIT" if ok else "PANEWIRE-REFUSE")


def _scene_reshape():
    """A wall raised mid-play in the avatar's path stops the walk — the live world overrides the
    plan; the avatar halts west of the raised cell."""
    fld = _blank()
    out = run_wired(fld, (2, 8), "EEEEEE", {1: ("edit", 10, 8, 9000)}, 4, 4000)
    base = run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
    ok = (out["transcript"] != base["transcript"] and (out["transcript"][-1][0] >> 32) < 10)
    return out["witness"], len(out["transcript"]) - 1, out["acquired"], out["refusals"], \
        ("ADMIT" if ok else "PANEWIRE-REFUSE")


def _scene_concord():
    """Two windows, one authority: the same (input, edits) run twice lands the identical composed
    witness — the edits made here are seen there, byte-for-byte."""
    fld = _blank()
    edits = {1: ("edit", 12, 12, 30), 3: ("edit", 13, 9, 20)}
    a = run_wired(fld, (2, 8), "EEEEEE", edits, 4, 4000)
    b = run_wired(fld, (2, 8), "EEEEEE", edits, 4, 4000)
    ok = a["witness"] == b["witness"]
    return a["witness"], len(a["transcript"]) - 1, a["acquired"], a["refusals"], \
        ("ADMIT" if ok else "PANEWIRE-REFUSE")


def _scene_besieged():
    """Malice under play: tampered edits woven into the stream refuse mid-loop, the replica is
    byte-unchanged, and the avatar's walk equals the malice-free walk — the game is unperturbed."""
    fld = _blank()
    clean = run_wired(fld, (2, 8), "EEEEEE", {}, 4, 4000)
    out = run_wired(fld, (2, 8), "EEEEEE", {1: ("malice",), 3: ("malice",)}, 4, 4000)
    ok = (out["refusals"] > 0 and out["transcript"] == clean["transcript"]
          and out["witness"] == clean["witness"])
    return out["witness"], len(out["transcript"]) - 1, out["acquired"], out["refusals"], \
        ("ADMIT" if ok else "PANEWIRE-REFUSE")


_SCENES = {"crossing": _scene_crossing, "reshape": _scene_reshape,
           "concord": _scene_concord, "besieged": _scene_besieged}
SCENES = ("crossing", "reshape", "concord", "besieged")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, ticks, acquired, refusals, verdict = scene_case(name)
    return panewire_digest(name, wit, ticks, acquired, refusals, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_panewire.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PaneWireError(f"no golden named {name!r}")
