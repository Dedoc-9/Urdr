# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""persist — the persistent snapshot checkpoint (T3.36, MMO Stage H, URDRLAT5): the DURABLE realization of
`storecost`'s space bound. The Stage-H arc certified the rollback window's TIME (`opcost`/`govern`/`priogov`/
`horizon`/`slo`/`clslo`) and then its SPACE (`storecost`: the exact bytes a depth-H window retains, with a
`STORAGE-REFUSE` past a budget). But those bytes lived only in RAM — `rollback` keeps its canonical snapshots
in memory, and a process that dies loses the window the whole guarantee priced. `persist` closes that gap:
the SAME window, as durable content-addressed checkpoint records under the membrane's own identity law
(`digest = SHA-256(content)`; the record's ADDRESS — and on disk its FILENAME — is the digest of what it
stores, the `registry/pin.py` / `urdr/snapshot.py` discipline), so a rollback window survives the process
that wrote it and is reconstructed BIT-FOR-BIT or refused, never repaired.

THE RECORD (canonical, fixed-width, big-endian). checkpoint(state, boundary) wraps `storecost.serialize`'s
canonical payload:
    record = MAGIC(8) | boundary(8, unsigned) | payload(4 + 25*n) | SHA-256(preceding bytes)(32)
so record_bytes(n) = 48 + snapshot_bytes(n) = 52 + 25*n is a CLOSED FORM the gate checks EQUALS
len(checkpoint(real glide state)) over a corpus. `restore` re-derives the digest and compares — a tampered
record is a typed `PERSIST-REFUSE` (EVERY single-byte flip and EVERY truncation of a pinned record is checked
to refuse — reconstruct-or-refuse with no undetected byte). The one digest plays three roles: integrity check,
content address, and (on disk) the filename.

THE MANIFEST (the window as one durable object). A depth-H window is `retained_snapshots(H) = H+1` consecutive
boundary records; `manifest(records)` binds (boundary, record-digest) pairs IN ORDER:
    manifest = WIN_MAGIC(11) | count(4) | (boundary(8) | digest(32))*count | SHA-256(preceding)(32)
so manifest_bytes(H) = 47 + 40*(H+1). A swapped, missing, gapped, or substituted record moves or refuses the
manifest; `restore_window` verifies every record against its manifest entry (digest AND boundary) before any
state is returned. `save_window`/`load_window` are the explicit līmes: files named by their digests in a given
directory, `load` verifying that served bytes hash to their name (a renamed or tampered file refuses).

THE ENVELOPE (the realization identity). durable_window_bytes(H, n) = (H+1)*record_bytes(n) +
manifest_bytes(H) EQUALS storecost.window_storage(H, n) + envelope_overhead(H) — the durable checkpoint costs
exactly what `storecost` bounded plus a CLOSED-FORM integrity premium (48 bytes per record + the manifest),
monotone in H and N, and `storecost.within_storage_budget` gates the durable total under the same
`STORAGE-REFUSE` law. The space bound was the prerequisite; this is what it priced.

GRADE. The record closed form and its equality to real encodings, the bit-exact restore (including negative
grounds and near-int64 positions), the exhaustive corruption/truncation `PERSIST-REFUSE`, the content-address
law (address == embedded digest == filename, verified on load), the manifest's order/membership binding, the
window-count tie to `horizon.worst_case_window(H)+1`, the durable closed form and the realization identity,
the budget `STORAGE-REFUSE`, and determinism (a re-save is byte-identical, same names same bytes) are MEASURED
(exact, reproducible, a defect diverges). The RETENTION COUNT (H+1) remains the DECLARED buffer-sizing policy
`storecost` declared; the STORE MEDIUM (a directory of digest-named files) is a DECLARED demonstration līmes —
the certified object is the BYTES, and any content-addressed medium serving the same bytes inherits the
guarantee. `does_not_show`: WALL-CLOCK or bandwidth of the writes (`bench.py` territory,
MEASURED-on-named-host); CRASH-ATOMICITY of the filesystem (a torn or partial write is DETECTED on load —
refused, not repaired — never PREVENTED; fsync/rename ordering is the OS's, not certified here); COMPRESSION
or delta-encoding (the raw canonical size, the honest upper bound); CONCURRENT writers; and the FIELD's own
storage (static and shared — until live world edits)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLAT5"
WIN_MAGIC = b"URDRLAT5WIN"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import storecost as _SC                                         # the space bound this realizes (payload law)
import horizon as _HZ                                           # the rollback window the count ties to

# ---- canonical record / manifest layout --------------------------------------------------
BOUND_BYTES = 8                                                 # boundary index, unsigned big-endian
DIGEST_BYTES = 32                                               # SHA-256, the one digest (integrity = address)
REC_OVERHEAD = len(MAGIC) + BOUND_BYTES + DIGEST_BYTES          # 48
COUNT_BYTES = 4                                                 # manifest entry count, big-endian
ENTRY_BYTES = BOUND_BYTES + DIGEST_BYTES                        # 40 per (boundary, digest) pair
WIN_OVERHEAD = len(WIN_MAGIC) + COUNT_BYTES + DIGEST_BYTES      # 47


class PersistError(Exception):
    def __init__(self, message):
        super().__init__(f"PERSIST-REFUSE: {message}")
        self.code = "PERSIST-REFUSE"


def record_bytes(n_actors):
    """The EXACT durable size of an N-actor checkpoint record: 48 + snapshot_bytes(n) = 52 + 25*n. The closed
    form the gate checks EQUALS len(checkpoint(state, boundary)) for real glide states."""
    return REC_OVERHEAD + _SC.snapshot_bytes(n_actors)


def checkpoint(state, boundary):
    """The canonical durable record of a snapshot at a command boundary: MAGIC | boundary | payload | SHA-256.
    The payload is `storecost.serialize`'s canonical encoding (its refusals apply); the trailing digest is the
    record's integrity check AND its content address."""
    if not (type(boundary) is int and 0 <= boundary < (1 << (8 * BOUND_BYTES))):
        raise PersistError(f"boundary must be an int in 0..2^64-1, got {boundary!r}")
    pre = MAGIC + boundary.to_bytes(BOUND_BYTES, "big") + _SC.serialize(state)
    return pre + hashlib.sha256(pre).digest()


def _verified(buf, magic, floor):
    """The shared verify: type, minimum length, magic, and the digest law (SHA-256 of everything before the
    trailing digest EQUALS the trailing digest). Returns the buffer as bytes, or a typed PERSIST-REFUSE."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise PersistError("a record must be bytes")
    buf = bytes(buf)
    if len(buf) < floor:
        raise PersistError(f"buffer of {len(buf)} bytes is shorter than the {floor}-byte minimum")
    if buf[:len(magic)] != magic:
        raise PersistError(f"bad magic — not a {magic.decode()} object")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise PersistError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    return buf


def address(buf):
    """The content address of a verified record or manifest: the hex of its embedded digest. Identity is
    content — this is the filename on disk. Refuses an object that does not verify (no address for corrupt
    bytes)."""
    if (type(buf) is bytes or type(buf) is bytearray) and bytes(buf[:len(WIN_MAGIC)]) == WIN_MAGIC:
        return _verified(buf, WIN_MAGIC, WIN_OVERHEAD)[-DIGEST_BYTES:].hex()
    return _verified(buf, MAGIC, REC_OVERHEAD + _SC.HEADER)[-DIGEST_BYTES:].hex()


def restore(buf):
    """The inverse of `checkpoint`: (boundary, state), reconstructed BIT-FOR-BIT — or a typed PERSIST-REFUSE.
    Verifies the digest first (every flipped byte and every truncation refuses), then the payload under
    `storecost.deserialize`'s own exact-length law (a well-digested but malformed payload still refuses)."""
    buf = _verified(buf, MAGIC, REC_OVERHEAD + _SC.HEADER)
    boundary = int.from_bytes(buf[len(MAGIC):len(MAGIC) + BOUND_BYTES], "big")
    try:
        state = _SC.deserialize(buf[len(MAGIC) + BOUND_BYTES:-DIGEST_BYTES])
    except _SC.StoreError as exc:
        raise PersistError(f"payload does not deserialize: {exc}")
    return boundary, state


def manifest(records):
    """The window as ONE durable object: WIN_MAGIC | count | (boundary | record-digest)* | SHA-256, over
    records whose boundaries are strictly consecutive (a depth-H window is boundaries b..b+H — a gap, swap, or
    duplicate refuses). Each record is fully verified before it is bound."""
    if not ((type(records) is tuple or type(records) is list) and len(records) >= 1):
        raise PersistError("a window must be a non-empty tuple of records")
    entries = []
    for rec in records:
        boundary, _state = restore(rec)
        entries.append((boundary, bytes(rec)[-DIGEST_BYTES:]))
    for i in range(1, len(entries)):
        if entries[i][0] != entries[i - 1][0] + 1:
            raise PersistError(f"boundaries must be strictly consecutive, got {entries[i - 1][0]} then "
                               f"{entries[i][0]} — a window with a gap or swap is refused")
    pre = WIN_MAGIC + len(entries).to_bytes(COUNT_BYTES, "big")
    for boundary, dig in entries:
        pre += boundary.to_bytes(BOUND_BYTES, "big") + dig
    return pre + hashlib.sha256(pre).digest()


def parse_manifest(man):
    """A verified manifest → its ((boundary, record-address-hex), ...) entries. Structural length and
    consecutiveness are re-checked (defense in depth against a crafted-but-digested manifest)."""
    man = _verified(man, WIN_MAGIC, WIN_OVERHEAD)
    count = int.from_bytes(man[len(WIN_MAGIC):len(WIN_MAGIC) + COUNT_BYTES], "big")
    if len(man) != WIN_OVERHEAD + ENTRY_BYTES * count or count < 1:
        raise PersistError(f"manifest length {len(man)} does not match its count {count}")
    out = []
    off = len(WIN_MAGIC) + COUNT_BYTES
    for _ in range(count):
        boundary = int.from_bytes(man[off:off + BOUND_BYTES], "big"); off += BOUND_BYTES
        out.append((boundary, man[off:off + DIGEST_BYTES].hex())); off += DIGEST_BYTES
    for i in range(1, len(out)):
        if out[i][0] != out[i - 1][0] + 1:
            raise PersistError("manifest boundaries must be strictly consecutive")
    return tuple(out)


def restore_window(man, lookup):
    """The whole window back, or one typed refuse: for each manifest entry, fetch the record from `lookup`
    (any address-hex → bytes mapping), verify it, and require its embedded digest AND boundary to equal the
    manifest's. A missing, substituted, or tampered record refuses — the manifest is the authority over
    membership and order. Returns ((boundary, state), ...) BIT-FOR-BIT."""
    out = []
    for boundary, dig in parse_manifest(man):
        try:
            rec = lookup[dig]
        except KeyError:
            raise PersistError(f"record {dig[:12]}… missing from the store")
        got_boundary, state = restore(rec)
        if bytes(rec)[-DIGEST_BYTES:].hex() != dig:
            raise PersistError(f"record served for {dig[:12]}… does not hash to it — substituted bytes refused")
        if got_boundary != boundary:
            raise PersistError(f"record {dig[:12]}… carries boundary {got_boundary}, manifest says {boundary}")
        out.append((boundary, state))
    return tuple(out)


def checkpoint_window(field, starts, cmds, max_step, sub, horizon):
    """The REAL depth-H window, checkpointed: the last H+1 command-boundary states of an N-actor glide
    (`storecost.boundary_state` at boundaries L-H .. L), each a durable record, bound by one manifest. Requires
    a transcript of at least H boundaries — a window deeper than its transcript is refused, not padded.
    Returns (records, manifest)."""
    if not (type(horizon) is int and horizon >= 0):
        raise PersistError(f"horizon must be a non-negative int, got {horizon!r}")
    last = len(cmds)
    if last < horizon:
        raise PersistError(f"a depth-{horizon} window needs at least {horizon} boundaries, transcript has {last}")
    records = tuple(
        checkpoint(_SC.boundary_state(field, starts, cmds, max_step, sub, b), b)
        for b in range(last - horizon, last + 1))
    return records, manifest(records)


# ---- the durable envelope (closed forms) -------------------------------------------------
def manifest_bytes(horizon):
    """The EXACT manifest size for a depth-H window: 47 + 40*(H+1)."""
    return WIN_OVERHEAD + ENTRY_BYTES * _SC.retained_snapshots(horizon)


def envelope_overhead(horizon):
    """The closed-form integrity premium the durable window pays over storecost's in-memory bound: 48 bytes
    per retained record (magic + boundary + digest) plus the manifest."""
    return _SC.retained_snapshots(horizon) * REC_OVERHEAD + manifest_bytes(horizon)


def durable_window_bytes(horizon, n_actors):
    """The EXACT durable cost of a depth-H, N-actor checkpointed window: (H+1)*record_bytes(n) +
    manifest_bytes(H) == storecost.window_storage(H, n) + envelope_overhead(H) — the realization identity.
    Gate-checked EQUAL to the real bytes written; `storecost.within_storage_budget` gates it under the same
    STORAGE-REFUSE law."""
    return _SC.retained_snapshots(horizon) * record_bytes(n_actors) + manifest_bytes(horizon)


# ---- the līmes: digest-named files in a directory ---------------------------------------
def save_window(dirpath, records):
    """Write a checkpointed window to a directory, every file named BY ITS CONTENT DIGEST (the
    `registry/pin.py` law: the filename IS the SHA-256). Deterministic — a re-save writes the identical file
    set with identical bytes. Returns the manifest's address (the one name a caller must keep)."""
    man = manifest(records)
    for rec in tuple(records) + (man,):
        with open(_os.path.join(dirpath, address(rec)), "wb") as fh:
            fh.write(bytes(rec))
    return address(man)


def load_window(dirpath, manifest_address):
    """The durable round-trip back: read the manifest by its address, require its bytes to HASH TO THEIR NAME,
    then fetch and verify every record the same way. A missing, renamed, tampered, or torn file is a typed
    PERSIST-REFUSE — detected on load, never repaired. Returns ((boundary, state), ...) BIT-FOR-BIT."""
    def _read(name):
        try:
            with open(_os.path.join(dirpath, name), "rb") as fh:
                return fh.read()
        except OSError as exc:
            raise PersistError(f"cannot read {name[:12]}… from the store: {exc.__class__.__name__}")
    man = _read(manifest_address)
    if address(man) != manifest_address:
        raise PersistError("manifest bytes do not hash to their name — a renamed or forged file is refused")
    store = {}
    for _boundary, dig in parse_manifest(man):
        rec = _read(dig)
        if address(rec) != dig:
            raise PersistError(f"record bytes for {dig[:12]}… do not hash to their name — refused")
        store[dig] = rec
    return restore_window(man, store)


def persist_digest(name, n_actors, horizon, rec_bytes, durable_bytes, verdict):
    """URDRLAT5 canon — SHA-256(MAGIC | name | n | horizon | record_bytes | durable_bytes | verdict). Binds
    the durable envelope and its verdict, so a changed retention, record width, or budget/integrity outcome
    moves it."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|n:{n_actors}|h:{horizon}|rec:{rec_bytes}|dur:{durable_bytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_MS, _SUB = 40, 4
_STARTS = ((2, 4), (2, 6), (2, 8), (2, 10), (2, 12))


# (n_actors, horizon, budget_bytes) -> durable = (H+1)*(52 + 25*n) + 47 + 40*(H+1)
_SCENES = {
    "one_h4_durable":  (1, 4, 10000),   # 5*77 + 247  = 632  <= 10000 -> ADMIT
    "five_h8_durable": (5, 8, 10000),   # 9*177 + 407 = 2000 <= 10000 -> ADMIT
    "tampered":        (1, 4, 10000),   # one flipped payload byte    -> PERSIST-REFUSE
}
SCENES = ("one_h4_durable", "five_h8_durable", "tampered")


def scene_case(name):
    """(record_bytes, durable_bytes, verdict) for a named config — verdict ADMIT, STORAGE-REFUSE, or (for the
    tampered scene, one deterministic flipped byte in a REAL record) PERSIST-REFUSE."""
    n, hz, budget = _SCENES[name]
    records, _man = checkpoint_window(_SC._flat16(), _STARTS[:n], "e" * hz, _MS, _SUB, hz)
    rec_b, dur_b = record_bytes(n), durable_window_bytes(hz, n)
    if name == "tampered":
        bad = bytearray(records[2])
        bad[40] ^= 0xFF
        try:
            restore(bytes(bad))
            verdict = "ADMIT"                                    # unreachable if the integrity law holds
        except PersistError:
            verdict = "PERSIST-REFUSE"
        return rec_b, dur_b, verdict
    try:
        _SC.within_storage_budget(dur_b, budget)
        verdict = "ADMIT"
    except _SC.StoreError:
        verdict = "STORAGE-REFUSE"
    return rec_b, dur_b, verdict


def scene_result(name):
    n, hz, _budget = _SCENES[name]
    rec_b, dur_b, verdict = scene_case(name)
    return persist_digest(name, n, hz, rec_b, dur_b, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_persist.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PersistError(f"no golden named {name!r}")
