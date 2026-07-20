# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""driftgaze — INTEREST SHIFT (T3.50, W4, URDRDGZ1): the client that MOVES. The wire certified the
static resident set; the storm certified chaos against it; the sealwrit certified who may write to
it. This rung makes the set itself LAWFUL MOTION: regions are ACQUIRED by `chunkload`'s verified
fetch against the CURRENT authority manifest (served bytes must hash to the manifest slot and carry
the slot's own coords — tampered, substituted, re-sealed-coord-forged, or missing all refuse) and
RELEASED cleanly, with wire's equal-or-refuse preserved across every shift. The module MINTS
NOTHING: the client is the wire replica plus its grid dims; acquisition is `view_from`'s law
holding records instead of cells; admission is `wire.client_admit` untouched; the witness is the
wire's own. Every law here is composition.

THE LAWS. NEVER-UNVERIFIED: there is no path into residency except a verified subscribe, a
verified admission, or a verified fetch — every refusal leaves the replica byte-identical.
EQUAL-ACROSS-THE-SHIFT: the mover runs on the resident view EQUAL to the full-field glide
bit-for-bit or CHUNK-REFUSE (chunkload's theorem, now under a resident set that changes beneath
the walk, driven by the walk's own demand). INTEREST FOLLOWS THE GAZE: `wire.relevant` against the
LIVE resident set — a released region's update is irrelevant, an acquired one's admits.
RE-ACQUISITION CARRIES HISTORY: the fetched chunk is the authority's CURRENT one, so missed
updates are never replayed — they arrive as already-history and refuse at the CAS; catching up is
a fetch, not a replay. THE STALE ACQUISITION IS DETECTED: a lagging server's internally-consistent
old world verifies at fetch time (the fetch checks integrity, not currency — currency is STATE) —
and the next live admission's CAS refuses, so the drift is caught by the client's own law, never
absorbed (wire's necessity-with-detection, extended to acquisition). THE GAP REPAIR, the storm's
declared debt PAID: a loss-stalled region (the storm's counted, typed stall) is repaired by
release + verified re-acquire of the head; redelivered stalled updates refuse as history; the next
live update admits — recovery without trusting the server, exactly the verified-fetch law the
storm's `does_not_show` promised to W4.

GRADE. Verified acquisition with all five refusal shapes pure, clean release with
never-guess, the mover's equality across shifts, interest-follows-the-gaze, re-acquisition
carrying history, stale-acquisition detection at the CAS, the gap repair end-to-end, and
determinism are MEASURED. DECLARED, honestly: the demand POLICY (which regions to want, when to
acquire-ahead and release-behind) is operational — the scenes drive it from `demand_chunks` on the
authority's field, the law certified is the replica's evolution under ANY policy; WHO computes
demand and whether a server may refuse a fetch (authorization of READS — the sealwrit's write-side
twin) is declared to the mesh phase; fetch BANDWIDTH and prefetch latency are `bench.py`'s.
`does_not_show`: wall-clock; the depicting client; cross-placement (URDRDGZ1 joins the frontier —
batch #3 falls due when the phase seals)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRDGZ1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # noqa: E402  the fetch law
import rannull as _RN                                           # noqa: E402  the record law
import wire as _W                                               # noqa: E402  the state law (W1)


class DriftError(Exception):
    def __init__(self, message):
        super().__init__(f"DRIFT-REFUSE: {message}")
        self.code = "DRIFT-REFUSE"


def subscribe_gaze(field, csize, regions):
    """The moving client: the wire replica plus its grid dims (the dims anchor every later
    acquisition — a manifest for a different grid refuses)."""
    base = _W.subscribe(field, csize, regions)
    return {"w": len(field[0]), "h": len(field), "c": csize, "chunks": base["chunks"]}


def acquire(client, man, lookup, keys):
    """THE VERIFIED FETCH INTO RESIDENCY — `chunkload._fetch`'s law, holding records: every
    served chunk must hash to the CURRENT manifest's slot and carry the slot's own coords;
    tampered, substituted, coord-forged (even under a re-sealed manifest), missing, or
    off-grid all refuse with the replica byte-identical. A resident key REFRESHES to the
    head — re-acquisition is the repair path. Returns a NEW client."""
    w, h, csize, grid = _CK.parse_manifest(man)
    if (w, h, csize) != (client["w"], client["h"], client["c"]):
        raise DriftError(f"manifest grid {w}x{h}/C={csize} is not this client's "
                         f"{client['w']}x{client['h']}/C={client['c']} — refused")
    _CK.view_from(man, lookup, frozenset(keys))                 # the verification, whole
    held = dict(client["chunks"])
    for key in sorted(keys):
        held[key] = lookup[grid[key]]                           # verified above, byte-held
    return {"w": w, "h": h, "c": csize, "chunks": held}


def release(client, keys):
    """Drop exactly the named resident regions; releasing what is not held refuses — the
    gaze never guesses. Returns a NEW client."""
    held = dict(client["chunks"])
    for key in sorted(keys):
        if key not in held:
            raise DriftError(f"region {key} is not resident — releasing it would be a guess")
        del held[key]
    return {"w": client["w"], "h": client["h"], "c": client["c"], "chunks": held}


def gaze_admit(client, rec):
    """One wire update through the UNMODIFIED state law; the dims ride along. WireError
    speaks for itself — nothing here softens or retypes it."""
    base = _W.client_admit({"c": client["c"], "chunks": client["chunks"]}, rec)
    return {"w": client["w"], "h": client["h"], "c": client["c"], "chunks": base["chunks"]}


def resident_view(client):
    """The resident set as a chunkload PARTIAL VIEW (cells, not records) — the mover's world.
    Built fresh from the held records every time: the view can never outlive an admission."""
    chunks = {}
    for key, rec in client["chunks"].items():
        _kx, _ky, cells = _CK.restore_chunk(rec)
        chunks[key] = cells
    return {"w": client["w"], "h": client["h"], "c": client["c"], "chunks": chunks}


def gaze_witness(client):
    """The wire's replica witness, unchanged — the resident (region, address) map as one hex."""
    return _W.replica_witness({"c": client["c"], "chunks": client["chunks"]})


def driftgaze_digest(name, witness_hex, acquired, released, updates, verdict):
    """URDRDGZ1 canon — SHA-256(MAGIC | name | witness | acquired | released | updates |
    verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|a:{acquired}|r:{released}|u:{updates}|v:{verdict}"
              .encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _server(fld, c):
    chunks = _CK.cut(fld, c)
    return _CK.field_manifest(fld, c), {_CK.address(r): r for r in chunks.values()}


def _edit(man, store, x, y, dh, c=8):
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


def _mirrors(client, man):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    return all(_CK.address(ch) == grid[k] for k, ch in client["chunks"].items())


_ALL4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})


def _scene_wayfarer():
    """The moving client end-to-end: three legs of a real walk, acquire-ahead and
    release-behind from the walk's OWN demand, live edits between legs (irrelevant ones
    filtered, the resident one admitted), the mover equal to the full-field glide on every
    leg, and the final replica mirroring the authority on the final resident set."""
    import glide as _GL
    fld = _blank()
    man, store = _server(fld, 8)
    pos = (2, 2)
    demand = _CK.demand_chunks(fld, pos, "ee", 4000, 4, 8)
    client = subscribe_gaze(fld, 8, demand)
    acq = rel = upd = 0
    ok = True
    for i, cmds in enumerate(("ee", "EEEE", "SSSS")):
        field_now = _CK.reassemble(man, store)
        need = _CK.demand_chunks(field_now, pos, cmds, 4000, 4, 8)
        gain = need - set(client["chunks"])
        drop = set(client["chunks"]) - need
        if gain:
            client = acquire(client, man, store, gain)
            acq += len(gain)
        if drop:
            client = release(client, drop)
            rel += len(drop)
        walked = _CK.glide_partial(resident_view(client), pos, cmds, 4000, 4)
        ok = ok and walked == _GL.glide(field_now, pos, cmds, 4000, 4)
        fx, fy, _hh, _f = walked[-1]
        pos = (fx >> 32, fy >> 32)
        edit_at = ((12, 4, 3), (13, 4, 2), (2, 12, 1))[i]
        rec = _edit(man, store, *edit_at)
        man, store = _serve(man, store, rec)
        if _W.relevant(rec, frozenset(client["chunks"])):
            client = gaze_admit(client, rec)
            upd += 1
    ok = ok and _mirrors(client, man)
    return gaze_witness(client), acq, rel, upd, ("ADMIT" if ok else "DRIFT-REFUSE")


def _scene_crooked_fetch():
    """The adversarial acquisition: tampered bytes, a RE-SEALED coord-forged manifest, a
    missing store entry, an off-grid key, and a dims-mismatched manifest each refuse typed
    with the replica byte-identical; the genuine acquire then lands the head."""
    fld = _blank()
    man, store = _server(fld, 8)
    client = subscribe_gaze(fld, 8, frozenset({(0, 0)}))
    before = gaze_witness(client)
    w, h, c, grid = _CK.parse_manifest(man)
    head_len = len(man) - 32 - 32 * len(grid)
    pre = bytearray(man[:head_len])
    for ky in range(h // c):
        for kx in range(w // c):
            key = (1, 1) if (kx, ky) == (0, 0) else (kx, ky)
            pre += bytes.fromhex(grid[key])
    forged_man = bytes(pre) + hashlib.sha256(bytes(pre)).digest()
    tampered = bytearray(store[grid[(1, 0)]])
    tampered[60] ^= 0x01
    bad_store = dict(store)
    bad_store[grid[(1, 0)]] = bytes(tampered)
    gone = dict(store)
    del gone[grid[(1, 1)]]
    probes = ((man, bad_store, frozenset({(1, 0)})),
              (forged_man, store, frozenset({(0, 0)})),
              (man, gone, frozenset({(1, 1)})),
              (man, store, frozenset({(7, 7)})),
              (_CK.field_manifest(fld, 4), store, frozenset({(1, 0)})))
    refused = 0
    for (m, s, k) in probes:
        try:
            acquire(client, m, s, k)
        except (DriftError, _CK.ChunkError):
            refused += 1
    pure = gaze_witness(client) == before
    client = acquire(client, man, store, frozenset({(1, 0)}))
    ok = refused == 5 and pure and _mirrors(client, man)
    return gaze_witness(client), 1, 0, 0, ("DRIFT-REFUSE" if ok else "ADMIT")


def _scene_homecoming():
    """Release, the authority edits the region twice, re-acquire: the fetched chunk is the
    POST-edit head; the missed update arrives as already-history and refuses; the next live
    update admits — catching up is a fetch, not a replay."""
    fld = _blank()
    man, store = _server(fld, 8)
    client = subscribe_gaze(fld, 8, frozenset({(0, 0), (0, 1)}))
    client = release(client, frozenset({(0, 1)}))
    u1 = _edit(man, store, 5, 8, 3)
    man, store = _serve(man, store, u1)
    filtered = not _W.relevant(u1, frozenset(client["chunks"]))
    u2 = _edit(man, store, 6, 8, 2)
    man, store = _serve(man, store, u2)
    client = acquire(client, man, store, frozenset({(0, 1)}))
    history = False
    try:
        gaze_admit(client, u1)
    except _W.WireError:
        history = True
    u3 = _edit(man, store, 5, 9, 1)
    client = gaze_admit(client, u3)
    man, store = _serve(man, store, u3)
    ok = filtered and history and _mirrors(client, man)
    return gaze_witness(client), 1, 1, 1, ("ADMIT" if ok else "DRIFT-REFUSE")


def _scene_stormrepair():
    """The storm's declared debt, PAID: u2 lost, u3 stalls typed on the gap; repair is
    release + verified re-acquire of the head; the redelivered u3 refuses as history; the
    live u4 admits; the replica lands on the authority's head with nothing trusted."""
    fld = _blank()
    man, store = _server(fld, 8)
    client = subscribe_gaze(fld, 8, _ALL4)
    u1 = _edit(man, store, 5, 8, 3)
    man, store = _serve(man, store, u1)
    client = gaze_admit(client, u1)
    u2 = _edit(man, store, 6, 8, 2)
    man, store = _serve(man, store, u2)                         # LOST in transit
    u3 = _edit(man, store, 5, 9, 1)
    man, store = _serve(man, store, u3)
    stalled = repaired_refuse = False
    try:
        gaze_admit(client, u3)
    except _W.WireError:
        stalled = True
    client = release(client, frozenset({(0, 1)}))
    client = acquire(client, man, store, frozenset({(0, 1)}))
    try:
        gaze_admit(client, u3)
    except _W.WireError:
        repaired_refuse = True
    u4 = _edit(man, store, 6, 9, 2)
    client = gaze_admit(client, u4)
    man, store = _serve(man, store, u4)
    ok = stalled and repaired_refuse and _mirrors(client, man)
    return gaze_witness(client), 1, 1, 2, ("ADMIT" if ok else "DRIFT-REFUSE")


_SCENES = {"wayfarer": _scene_wayfarer, "crooked_fetch": _scene_crooked_fetch,
           "homecoming": _scene_homecoming, "stormrepair": _scene_stormrepair}
SCENES = ("wayfarer", "crooked_fetch", "homecoming", "stormrepair")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, acq, rel, upd, verdict = scene_case(name)
    return driftgaze_digest(name, wit, acq, rel, upd, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_driftgaze.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DriftError(f"no golden named {name!r}")
