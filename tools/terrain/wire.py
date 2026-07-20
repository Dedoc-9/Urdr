# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""wire — EQUAL-OR-REFUSE REPLICATION (T3.47, THE WIRE PHASE OPENER, URDRWIR1): the ratified phase
slice, landed. Production replication ships derived state and asks the client to trust it; the
academic alternative (CRDTs) designs types whose merges cannot conflict. This wire does neither:
every update IS the essence-bearing object — the 104-byte URDRRAN0 regional record, verbatim — and
the receiving client ADMITS it under the same laws the authority used, against its OWN replica. The
client is a verifier, not a believer: a malicious or buggy server produces a typed WIRE-REFUSE with
the replica byte-unchanged, never a silent desync.

THE MODULE MINTS NOTHING (the quintessence discipline): no new record format, no wire envelope, no
sequence numbers. It is pure composition, and each absence is a theorem already paid for:

  NO SNAPSHOTS ON THE WIRE — the client DERIVES the new chunk by `rannull.shard_apply`: 104 bytes
  per edit regardless of chunk size, because derived state is recomputed, never shipped (the frame
  property makes the recomputation exact: the shard function's inputs are the chunk and the record,
  both of which the client verifiably holds).

  NO SEQUENCE NUMBERS — within a region, order is STRUCTURAL: each record's parent is the previous
  chunk state's address (terraform's chain law on the wire), so an out-of-order update refuses on
  the stale parent and admits on in-order retry, and an exact duplicate refuses (at-most-once free:
  its own admission moved the parent it binds). Across regions, order is provably IRRELEVANT: every
  interleaving of disjoint-authority updates lands the identical replica — RAN-0's nullity is the
  wire's cross-region ordering law.

  THE INTEREST FILTER, sufficient and necessary — `relevant(rec, regions)` is one frozenset test
  against the record's own claimed region (the essence's spatial axis doing protocol work).
  SOUND: an irrelevant edit touches no resident chunk (exactly-one-slot), so the unsent client
  stays byte-equal. NECESSARY, with the violation DETECTED: a withheld relevant update leaves the
  client's chunk stale, and the next in-region update refuses on the CAS — drift is caught by the
  client's own admission law, never absorbed.

GRADE. Update-is-the-record, the per-step byte equality of replica and authority, structural
in-region ordering with at-most-once, cross-region interleaving invariance, interest soundness and
detected-necessity, the verifier refusals (tamper / unheld region / foreign state) each leaving the
replica byte-identical, verified subscription, and determinism are MEASURED (exact, reproducible, a
defect diverges). DECLARED, honestly: TRANSPORT itself (loss, reordering, and duplication are
MODELED by the delivery-order falsifiers, not carried over sockets — the laws are transport's
obligations, stated where a transport must meet them); WHO may send (authenticity of the sender is
`authinput`'s Lamport-signature territory — this rung certifies STATE LAW: a lawful update admits
whoever relays it, an unlawful one refuses whoever signs it); interest SHIFT (acquiring/releasing
regions mid-session — chunkload's verified fetch is the mechanism, the policy is operational);
server-side fan-out scheduling (`govern`'s territory). `does_not_show`: wall-clock and bandwidth
(`bench.py`); the depicting client; cross-placement (URDRWIR1 joins the placement frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRWIR1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, demand sets — the interest
import rannull as _RN                                           # the record + shard law — the admission


class WireError(Exception):
    def __init__(self, message):
        super().__init__(f"WIRE-REFUSE: {message}")
        self.code = "WIRE-REFUSE"


def subscribe(field, csize, regions):
    """A client replica: exactly the subscribed regions, each chunk the VERIFIED authority chunk
    (the chunkload fetch law — this models the initial verified stream-in). The replica is a plain
    mapping; admission returns a NEW replica (the membrane way — nothing mutates in place)."""
    chunks = _CK.cut(field, csize)
    held = {}
    for key in sorted(regions):
        if key not in chunks:
            raise WireError(f"region {key} is outside the world's chunk grid")
        held[key] = chunks[key]
    return {"c": csize, "chunks": held}


def relevant(rec, regions):
    """THE INTEREST FILTER: one frozenset test against the record's own claimed region — the
    essence's spatial axis doing protocol work. Sound (an irrelevant edit cannot touch a resident
    chunk) and necessary (a withheld relevant update is detected by the next admission's CAS)."""
    try:
        _p, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise WireError(f"an update must be a verified regional record: {exc}")
    return (kx, ky) in regions


def client_admit(client, rec):
    """THE VERIFIER: admit one wire update against the replica under the authority's own laws —
    the record verifies (identity), the claimed region is HELD (never guessed at), and the shard
    CAS binds it to the client's current chunk state (a stale, reordered, duplicated, or foreign
    update refuses). Returns a NEW replica; every refuse leaves the old one byte-identical."""
    try:
        _p, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise WireError(f"the update refused verification: {exc}")
    if (kx, ky) not in client["chunks"]:
        raise WireError(f"region ({kx},{ky}) is not resident — an unheld update is refused, "
                        f"never guessed at")
    cur = client["chunks"][(kx, ky)]
    try:
        new_chunk = _RN.shard_apply(cur, rec)                   # the same law the authority used
    except _RN.RanError as exc:
        raise WireError(f"the replica refused the update: {exc}")
    held = dict(client["chunks"])
    held[(kx, ky)] = new_chunk
    return {"c": client["c"], "chunks": held}


def replica_witness(client):
    """The replica's witness: SHA-256 over the held (region, chunk-address) pairs in region order —
    what 'byte-equal on the resident set' pins down to one hex."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for key in sorted(client["chunks"]):
        hh.update(f"|{key[0]},{key[1]}:{_CK.address(client['chunks'][key])}".encode())
    return hh.hexdigest()


def wire_digest(name, witness_hex, updates, regions, verdict):
    """URDRWIR1 canon — SHA-256(MAGIC | name | witness | updates | regions | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|u:{updates}|r:{regions}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _server(fld, c):
    chunks = _CK.cut(fld, c)
    return _CK.field_manifest(fld, c), {_CK.address(r): r for r in chunks.values()}


def _edit(man, store, x, y, dh, c):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    key = (x // c, y // c)
    chunk = store[grid[key]]
    kx, ky, cells = _CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)


def _serve(man, store, rec):
    new_chunk = _RN.shard_apply(store[_RN.restore_regional(rec)[0]], rec)
    new_man = _RN.reunify(man, (new_chunk,))
    store2 = dict(store)
    store2[_CK.address(new_chunk)] = new_chunk
    return new_man, store2


def _scene_faithful_mirror():
    """Five updates across four regions to a full-resident client: after every admission the
    replica equals the authority byte-for-byte (witnessed by the resident address map)."""
    fld = _blank()
    man, store = _server(fld, 8)
    client = subscribe(fld, 8, frozenset({(0, 0), (0, 1), (1, 0), (1, 1)}))
    ok = True
    for (x, y, dh) in ((5, 8, 1000), (2, 2, 11), (12, 4, 22), (5, 8, -30), (12, 12, 33)):
        rec = _edit(man, store, x, y, dh, 8)
        man, store = _serve(man, store, rec)
        client = client_admit(client, rec)
        _w, _h, _c, grid = _CK.parse_manifest(man)
        ok = ok and all(_CK.address(chunk) == grid[key] for key, chunk in client["chunks"].items())
    wit = replica_witness(client)
    return wit, 5, 4, ("ADMIT" if ok else "WIRE-REFUSE")


def _scene_narrow_gaze():
    """A client resident on a walk's certified demand set: the relevant update admits, the
    irrelevant one is filtered — and the unsent client is provably still byte-equal on its set."""
    fld = _blank()
    man, store = _server(fld, 8)
    demand = _CK.demand_chunks(fld, (2, 8), "eeee", 40, 4, 8)
    client = subscribe(fld, 8, demand)
    near = _edit(man, store, 6, 8, 77, 8)
    man, store = _serve(man, store, near)
    sent = relevant(near, demand)
    if sent:
        client = client_admit(client, near)
    far = _edit(man, store, 12, 12, 555, 8)
    man, store = _serve(man, store, far)
    filtered = not relevant(far, demand)
    _w, _h, _c, grid = _CK.parse_manifest(man)
    ok = (sent and filtered
          and all(_CK.address(chunk) == grid[key] for key, chunk in client["chunks"].items()))
    wit = replica_witness(client)
    return wit, 2, len(demand), ("ADMIT" if ok else "WIRE-REFUSE")


def _scene_crooked_wire():
    """The adversarial server: a tampered update, an out-of-order update, and an unheld-region
    update each refuse with the replica byte-identical; the in-order retry then admits."""
    fld = _blank()
    man, store = _server(fld, 8)
    client = subscribe(fld, 8, frozenset({(0, 1)}))
    before = replica_witness(client)
    r1 = _edit(man, store, 5, 8, 100, 8)
    man2, store2 = _serve(man, store, r1)
    r2 = _edit(man2, store2, 6, 8, 50, 8)
    refused = 0
    bad = bytearray(r1)
    bad[50] ^= 0x01
    for update in (bytes(bad), r2, _edit(man, store, 12, 12, 5, 8)):
        try:
            client_admit(client, update)
        except WireError:
            refused += 1
    pure = replica_witness(client) == before
    c1 = client_admit(client, r1)                               # the in-order retry admits
    c2 = client_admit(c1, r2)
    dup_refused = False
    try:
        client_admit(c2, r2)
    except WireError:
        dup_refused = True
    ok = refused == 3 and pure and dup_refused
    wit = replica_witness(c2)
    return wit, 3, 1, ("WIRE-REFUSE" if ok else "ADMIT")


def _scene_silent_drift():
    """The necessity witness: a relevant update WITHHELD, then the next in-region update refuses
    on the client — the drift is detected by the client's own admission law, never absorbed."""
    fld = _blank()
    man, store = _server(fld, 8)
    demand = _CK.demand_chunks(fld, (2, 8), "eeee", 40, 4, 8)
    client = subscribe(fld, 8, demand)
    near = _edit(man, store, 6, 8, 77, 8)
    man2, store2 = _serve(man, store, near)                     # admitted by the server, withheld
    stale_next = _edit(man2, store2, 5, 8, 9, 8)
    detected = False
    try:
        client_admit(client, stale_next)
    except WireError:
        detected = True
    ok = relevant(near, demand) and detected
    wit = replica_witness(client)
    return wit, 1, len(demand), ("ADMIT" if ok else "WIRE-REFUSE")


_SCENES = {"faithful_mirror": _scene_faithful_mirror, "narrow_gaze": _scene_narrow_gaze,
           "crooked_wire": _scene_crooked_wire, "silent_drift": _scene_silent_drift}
SCENES = ("faithful_mirror", "narrow_gaze", "crooked_wire", "silent_drift")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, updates, regions, verdict = scene_case(name)
    return wire_digest(name, wit, updates, regions, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_wire.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise WireError(f"no golden named {name!r}")
