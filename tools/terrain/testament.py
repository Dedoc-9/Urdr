# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""testament — durable intent (T3.44, MMO Stage I, URDRTST1): the write that survives its writer.
`resurrect` proved the READ side of death — a successor process replays a saved world from the store
alone. This rung proves the WRITE side: a client authors an edit under a lease and may DIE holding
it; the intent survives as a TESTAMENT — the name is exact twice over: a last WILL (written intent
surviving its author, executed by a successor only under the conditions it names) and TESTIMONY (the
record as evidence, content-addressed, corruption-refusing).

THE TESTAMENT (144 bytes): MAGIC | regional edit record (104) | SHA-256. Nothing more — the lease it
was authored under is DERIVABLE (the record's parent digest + region ARE the lease; carrying it
would invite incoherence, and derived data is checkable data). The one digest is integrity check,
content address, and on-disk filename — the persist law, now covering intent.

PROBATE (the execution). A successor who knows nothing but the store presents the testament:
`probate` derives the lease and runs the LEASED ADMISSION — so everything the lease law proved is
inherited: the lost-update impossibility, the amortized == reproved equality, interval transport.
EXACTLY-ONCE is free: the admission moves the very authority the testament names, so a second
probate refuses. And the refusal SPEAKS: the two flavors are DISTINGUISHED — "executed" (the current
chunk state IS the state this intent produces: the will was carried out; the successor may rest) vs
"distributed" (a foreign edit moved the authority: the intent conflicted; re-author against the new
world) — adjudicated by deriving the expected child chunk from the RETAINED parent state (the
anamnesis store read-only, doing honest work) and comparing content addresses. A store that no
longer retains the parent refuses as "unadjudicable" — no flavor is ever guessed from missing
evidence.

THE DEATH BOUNDARY IS REAL (the resurrect discipline): this file is its own successor —
`python testament.py <store_dir> <testament_addr> <manifest_addr>` reads everything by address from
the directory (each object verified to hash to its filename — the SUBSTITUTION refuse: intact bytes
under the wrong address are not that address), performs probate, and prints the head or the typed
refusal. The gate runs it twice; the outputs must be bit-identical and equal the never-died
admission. THE EXECUTOR IS PURE: a refused probate writes nothing — the store is byte-identical
after.

GRADE. The record closed form, round-trip, exhaustive corruption refuse; probate == living
admission == the global reproof; the through-death admission (a REAL successor, disk-only channel,
twice, bit-identical); exactly-once with the refused attempt perturbing nothing; the three refusal
flavors (executed / distributed / unadjudicable) each earned from evidence; the filename law
including the substitution refuse; executor purity; the estate cost; and determinism are MEASURED
(exact, reproducible, a defect diverges). DECLARED: WHO may leave a testament (issuance —
`authinput`/capability territory); retry POLICY after "distributed" (re-authoring is the client's
choice; the law only guarantees the flavors are true); batching of testaments (a will with many
bequests is a chain of these primitives); and garbage collection of executed testaments (the store
keeps everything — anamnesis; compaction is operational). `does_not_show`: a crash DURING probate's
persist-back (the successor prints, the caller persists — torn writes are the caller's
crash-atomicity boundary, persist's law); wall-clock (`bench.py`); cross-placement (Python
reference only — URDRTST1 joins the placement frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRTST1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # manifests, chunk records, stores
import rannull as _RN                                           # regional records, shard_apply
import lease as _LS                                             # the admission law probate inherits

DIGEST_BYTES = 32
TESTAMENT_BYTES = len(MAGIC) + _RN.RAN_RECORD_BYTES + DIGEST_BYTES  # 144


class TestamentError(Exception):
    def __init__(self, message, flavor="refused"):
        super().__init__(f"TESTAMENT-REFUSE: {message}")
        self.code = "TESTAMENT-REFUSE"
        self.flavor = flavor


def testament_record(rec):
    """The intent, sealed: MAGIC | regional edit record | SHA-256. Only a verified URDRRAN0 regional
    record may be a testament — the global (URDRTFM1) form is refused; the two laws never
    interchange."""
    try:
        _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise TestamentError(f"only a regional edit record can be a testament: {exc}")
    pre = MAGIC + bytes(rec)
    return pre + hashlib.sha256(pre).digest()


def restore_testament(buf):
    """The inverse: the embedded regional record BIT-FOR-BIT or a typed refuse. Outer digest first,
    exact length, then the inner record under its OWN digest (defense in depth)."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise TestamentError("a testament must be bytes")
    buf = bytes(buf)
    if len(buf) != TESTAMENT_BYTES:
        raise TestamentError(f"a testament must be exactly {TESTAMENT_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise TestamentError("bad magic — not a URDRTST1 testament")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise TestamentError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    rec = buf[len(MAGIC):len(MAGIC) + _RN.RAN_RECORD_BYTES]
    try:
        _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise TestamentError(f"embedded record refused: {exc}")
    return rec


def address_of(t):
    """The testament's content address: its own trailing digest, hex — integrity check, address, and
    filename in one (the persist law)."""
    return bytes(t)[-DIGEST_BYTES:].hex()


def lease_of(t_or_rec):
    """The lease a testament was authored under, DERIVED — the record's parent digest and region ARE
    the lease; nothing carried, nothing to fall out of coherence."""
    buf = bytes(t_or_rec)
    rec = restore_testament(buf) if len(buf) == TESTAMENT_BYTES else buf
    parent, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
    return _LS.lease_record(parent, kx, ky)


def _adjudicate(man, store, rec):
    """The flavor of a failed validity: derive the expected child chunk from the RETAINED parent
    state (the anamnesis store, read-only) and compare content addresses with the current slot.
    'executed' — the current state IS what this intent produces; 'distributed' — a foreign edit
    landed; 'unadjudicable' — the parent state is no longer retained, and no flavor is guessed."""
    parent, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
    _w, _h, _c, grid = _CK.parse_manifest(man)
    if parent not in store:
        raise TestamentError("cannot adjudicate — the parent state is not retained in the store; "
                             "no flavor is guessed from missing evidence", flavor="unadjudicable")
    expected = _RN.shard_apply(store[parent], rec)
    if grid[(kx, ky)] == _CK.address(expected):
        raise TestamentError("already executed — the intent is in the world; the successor may "
                             "rest", flavor="executed")
    raise TestamentError("the estate was already distributed — a foreign edit moved the authority; "
                         "the intent conflicted and must be re-authored", flavor="distributed")


def probate(man, store, t):
    """THE EXECUTION: derive the lease, run the leased admission — everything the lease law proved
    is inherited, and exactly-once is free (the admission expires the testament's own lease).
    Returns (new_manifest, new_chunk). A failed validity is adjudicated into its true flavor;
    probate WRITES NOTHING (the caller persists results — the executor is membrane-pure)."""
    rec = restore_testament(t)
    ls = lease_of(rec)
    if not _LS.valid(man, ls):
        _adjudicate(man, store, rec)                            # always raises, with the flavor
    try:
        return _LS.admit(man, store, ls, rec)
    except _LS.LeaseError as exc:
        raise TestamentError(f"the admission refused: {exc}")


# ---- the estate on disk (the persist law: digest == filename) ----------------------------
def save_estate(dirpath, man, chunk_records, t):
    """Write the world + the testament to a directory, every object under its own content address.
    Returns (manifest_address, testament_address)."""
    for rec in chunk_records:
        with open(_os.path.join(dirpath, _CK.address(rec)), "wb") as fh:
            fh.write(bytes(rec))
    man_addr = _CK.address(man)
    with open(_os.path.join(dirpath, man_addr), "wb") as fh:
        fh.write(bytes(man))
    t_addr = address_of(t)
    with open(_os.path.join(dirpath, t_addr), "wb") as fh:
        fh.write(bytes(t))
    return man_addr, t_addr


def _load(dirpath, addr):
    try:
        with open(_os.path.join(dirpath, addr), "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise TestamentError(f"object {addr[:12]}… missing from the estate: {exc}")


def load_testament(dirpath, addr):
    """Read a testament by address: bytes must be a verified testament AND hash to the requested
    address — intact bytes under the WRONG filename are a SUBSTITUTION, refused (the inner digest
    cannot see this; the address check carries it alone)."""
    buf = _load(dirpath, addr)
    restore_testament(buf)
    if address_of(buf) != addr:
        raise TestamentError(f"substitution — the object at {addr[:12]}… is a valid testament but "
                             f"its address is {address_of(buf)[:12]}…; the address IS the identity")
    return buf


def probate_from_store(dirpath, t_addr, man_addr):
    """THE SUCCESSOR'S PATH: everything by address from the directory — the manifest, the testament,
    and every chunk object, each verified to hash to its filename — then probate. Read-only: a
    refused probate leaves the directory byte-identical. Returns (head_hex, new_man, new_chunk)."""
    man = _load(dirpath, man_addr)
    try:
        if _CK.address(man) != man_addr:
            raise TestamentError(f"substitution — the manifest at {man_addr[:12]}… addresses "
                                 f"{_CK.address(man)[:12]}…")
    except _CK.ChunkError as exc:
        raise TestamentError(f"the estate's manifest refused: {exc}")
    t = load_testament(dirpath, t_addr)
    store = {}
    for name in _os.listdir(dirpath):
        if name in (man_addr, t_addr):
            continue
        buf = _load(dirpath, name)
        try:
            if _CK.address(buf) != name:
                raise TestamentError(f"substitution — the chunk at {name[:12]}… addresses "
                                     f"{_CK.address(buf)[:12]}…")
        except _CK.ChunkError:
            continue                                            # foreign object types are not chunks
        store[name] = buf
    new_man, new_chunk = probate(man, store, t)
    return _CK.address(new_man), new_man, new_chunk


def estate_cost_bytes(csize, w, h):
    """The durable increment of one testament carried to admission: the testament itself + the
    leased-admission increment."""
    return TESTAMENT_BYTES + _LS.admission_cost_bytes(csize, w, h)


def testament_digest(name, mint_hex, head_hex, flavor, nbytes, verdict):
    """URDRTST1 canon — SHA-256(MAGIC | name | mint | head | flavor | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|m:{mint_hex}|h:{head_hex}|f:{flavor}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _state(fld, c):
    chunks = _CK.cut(fld, c)
    return _CK.field_manifest(fld, c), {_CK.address(r): r for r in chunks.values()}


def _rec_under(man, store, x, y, dh, c):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    chunk = store[grid[(x // c, y // c)]]
    kx, ky, cells = _CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)


def _scene_phoenix_scribe():
    """The through-death shape, in-memory + from-disk-alone: probate equals the living admission,
    and the successor's path (everything by address from a real directory) equals it again."""
    import tempfile
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    t = testament_record(_rec_under(man, store, 5, 8, 1000, 8))
    new_man, _nc = probate(man, store, t)
    live_man, _lc = _LS.admit(man, store, lease_of(t), restore_testament(t))
    with tempfile.TemporaryDirectory(prefix="urdr_tst_scene_") as td:
        man_addr, t_addr = save_estate(td, man, store.values(), t)
        head_disk, _m, _c2 = probate_from_store(td, t_addr, man_addr)
    ok = new_man == live_man and head_disk == _CK.address(new_man)
    return mint, _CK.address(new_man), "willed", TESTAMENT_BYTES, ("ADMIT" if ok else "TESTAMENT-REFUSE")


def _scene_twice_told():
    """Exactly-once: the first probate admits and expires its own lease; the second refuses AS
    'executed' — and the refused attempt perturbs nothing."""
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    t = testament_record(_rec_under(man, store, 5, 8, 1000, 8))
    man2, ch = probate(man, store, t)
    store2 = dict(store)
    store2[_CK.address(ch)] = ch
    flavor = "none"
    try:
        probate(man2, store2, t)
    except TestamentError as exc:
        flavor = exc.flavor
    unperturbed = probate(man, store, t) == (man2, ch)
    ok = flavor == "executed" and unperturbed
    return mint, _CK.address(man2), flavor, TESTAMENT_BYTES, ("ADMIT" if ok else "TESTAMENT-REFUSE")


def _scene_legacy_race():
    """The conflicted estate: a foreign edit lands first; probate refuses AS 'distributed' — the
    successor learns to re-author, never told to rest."""
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    t = testament_record(_rec_under(man, store, 5, 8, 1000, 8))
    alien = _rec_under(man, store, 6, 8, 77, 8)
    man2, ch2 = _LS.admit(man, store, lease_of(testament_record(alien)), alien)
    store2 = dict(store)
    store2[_CK.address(ch2)] = ch2
    flavor = "none"
    try:
        probate(man2, store2, t)
    except TestamentError as exc:
        flavor = exc.flavor
    ok = flavor == "distributed"
    return mint, _CK.address(man2), flavor, 0, ("TESTAMENT-REFUSE" if ok else "ADMIT")


def _scene_sealed_scroll():
    """The filename law on a real directory: bit-exact read-back; a flipped byte refuses; an intact
    SUBSTITUTED testament under the wrong address refuses (only the address check can see it)."""
    import tempfile
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    t = testament_record(_rec_under(man, store, 5, 8, 1000, 8))
    other = testament_record(_rec_under(man, store, 12, 4, 77, 8))
    roundtrip = flip = subst = False
    with tempfile.TemporaryDirectory(prefix="urdr_tst_scene_") as td:
        _ma, t_addr = save_estate(td, man, store.values(), t)
        roundtrip = load_testament(td, t_addr) == t
        path = _os.path.join(td, t_addr)
        raw = bytearray(open(path, "rb").read())
        raw[50] ^= 0x01
        open(path, "wb").write(bytes(raw))
        try:
            load_testament(td, t_addr)
        except TestamentError:
            flip = True
        open(path, "wb").write(other)
        try:
            load_testament(td, t_addr)
        except TestamentError:
            subst = True
    ok = roundtrip and flip and subst
    return mint, address_of(t), "sealed", TESTAMENT_BYTES, ("ADMIT" if ok else "TESTAMENT-REFUSE")


_SCENES = {"phoenix_scribe": _scene_phoenix_scribe, "twice_told": _scene_twice_told,
           "legacy_race": _scene_legacy_race, "sealed_scroll": _scene_sealed_scroll}
SCENES = ("phoenix_scribe", "twice_told", "legacy_race", "sealed_scroll")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    mint, head, flavor, nbytes, verdict = scene_case(name)
    return testament_digest(name, mint, head, flavor, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_testament.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise TestamentError(f"no golden named {name!r}")


if __name__ == "__main__":
    # THE SUCCESSOR: python testament.py <store_dir> <testament_addr> <manifest_addr>
    # Knows nothing but the directory and two addresses; prints the head, or the typed refusal.
    # Writes nothing either way — the caller persists results (executor purity).
    if len(_sys.argv) != 4:
        print("usage: testament.py <store_dir> <testament_addr> <manifest_addr>")
        raise SystemExit(2)
    try:
        head, _nm, _nc = probate_from_store(_sys.argv[1], _sys.argv[2], _sys.argv[3])
        print(head)
    except TestamentError as exc:
        print(f"{exc} [flavor={exc.flavor}]")
