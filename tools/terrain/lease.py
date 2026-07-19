# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lease — the standing lease (T3.43, MMO Stage I, URDRLSE1): the TEMPORAL extension of RAN-0.
`rannull` proved the nullity certificate is bound to its AUTHORITIES, not the world — it transports
across authority-preserving worlds (spatial). The lease makes the INTERVAL first-class: a write
capability minted against one chunk STATE, valid from mint until that authority moves — proof as an
interval, not a moment. Optimistic distributed admission with proofs instead of locks: an authority
hands a client a lease; the client authors edits offline; each edit admits later against ANY head the
interval reaches, and expiry is a typed LEASE-REFUSE — never a lost update, never a silent rebase.

THE LEASE (80 bytes): MAGIC | chunk digest | kx | ky | SHA-256 — it names one authority STATE. An
edit is "under" the lease iff its regional record's parent IS the lease's chunk digest (the binding
is definitional, not administrative — same digest, same state, no registry).

VALIDITY, state-free: valid(manifest, lease) reads ONE manifest slot — no store, no field, no chunk
bytes. O(manifest) to parse, O(1) to decide: the slot for the lease's region still carries the
lease's digest, or the authority has moved. A coordinator can answer "is this lease live?" from the
55 + 32·n manifest alone.

THE LOST-UPDATE LAW (the design decision the anamnesis store forces). The content-addressed store
retains the OLD chunk forever — anamnesis is an address, not an undo — so an admission that fetched
the chunk BY THE LEASE'S DIGEST would find the stale bytes, apply cleanly, and silently REVERT every
edit the interval landed in that chunk: the classic lost update, hiding inside the store's own
virtue. `admit` therefore fetches by the CURRENT manifest slot: the shard CAS (record parent vs the
live chunk's address) is the deep guard, and valid() is the cheap manifest-only pre-check — two
layers, individually redundant, jointly load-bearing (both gutted, the lost update lands; the gate's
plants prove it).

INTERVAL COMMUTATION (the keystone). Over a chain of authority-disjoint leased edits, the leased
edit admits at EVERY insertion position with its bytes UNCHANGED, and every position lands ONE final
head — the history of disjoint authorities is order-free as an INTERVAL, not merely as a pair
(RAN-0's diamond, iterated without re-proving). AMORTIZATION measured: the cheap admission (slot
check + one shard apply + address reunify) EQUALS the full global reproof (terraform lift on the
reassembled world) at every interval head, bit-for-bit — the proof was paid once at mint; admissions
inherit it.

SELF-EXPIRY + RENEWAL: a lease dies at its OWN use — the edit moves the very authority the lease
names — so a lease is single-shot, and renewal is `lease_from_chunk(new_chunk)`: the lease chain IS
the region's write history, each link a content address (the transcript law on write capability).

GRADE. The record closed form, round-trip, and exhaustive corruption refuse; state-free validity
both directions; interval commutation over the corpus; the amortized == reproved equality; the
two-layer lost-update refuse (with the anamnesis trap demonstrated: the stale chunk IS in the store);
self-expiry, renewal, admission honesty (foreign state, region mismatch, missing chunk, tampered
lease); the inherited transport (the leased slot lands the same chunk address on any world sharing
the authority); the split costs and the amortized closed form; and determinism are MEASURED (exact,
reproducible, a defect diverges). DECLARED: lease ISSUANCE policy (who gets a lease for what — an
authority/capability question, `authinput` territory); lease DURATION policy (this lease expires on
authority motion, not wall-clock — a TTL is an operational overlay); n-way lease scheduling and the
independence lattice as a queryable allocator (the arc); and the physical client (offline authoring
is modeled by the record's byte-stability across the interval, not by a process boundary).
`does_not_show`: revocation before expiry (mint a competing edit — the CAS expires the lease
naturally; explicit revocation lists are future work); wall-clock (`bench.py`); cross-placement
(Python reference only until a placement reproduces these digests)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRLSE1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # manifests, chunk records, stores
import rannull as _RN                                           # regional records, shard_apply, reunify

DIGEST_BYTES = 32
COORD_BYTES = 4
LEASE_BYTES = len(MAGIC) + DIGEST_BYTES + 2 * COORD_BYTES + DIGEST_BYTES  # 80


class LeaseError(Exception):
    def __init__(self, message):
        super().__init__(f"LEASE-REFUSE: {message}")
        self.code = "LEASE-REFUSE"


def lease_record(chunk_hex, kx, ky):
    """The lease: MAGIC | the chunk digest it is minted against | kx | ky | SHA-256. It names one
    authority STATE; an edit is under it iff the edit's parent IS this digest."""
    if not (isinstance(chunk_hex, str) and len(chunk_hex) == 64):
        raise LeaseError(f"chunk address must be 64 hex chars, got {chunk_hex!r}")
    try:
        dig = bytes.fromhex(chunk_hex)
    except ValueError:
        raise LeaseError("chunk address is not hex")
    pre = bytearray(MAGIC) + dig
    for v, nm in ((kx, "kx"), (ky, "ky")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise LeaseError(f"{nm} must be uint32, got {v!r}")
        pre += v.to_bytes(COORD_BYTES, "big")
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def restore_lease(buf):
    """The inverse: (chunk_hex, kx, ky) BIT-FOR-BIT or a typed refuse. Digest first; exact length;
    every flip and truncation refuses."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise LeaseError("a lease must be bytes")
    buf = bytes(buf)
    if len(buf) != LEASE_BYTES:
        raise LeaseError(f"a lease must be exactly {LEASE_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise LeaseError("bad magic — not a URDRLSE1 lease")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise LeaseError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    chunk_hex = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
    kx = int.from_bytes(buf[off:off + COORD_BYTES], "big"); off += COORD_BYTES
    ky = int.from_bytes(buf[off:off + COORD_BYTES], "big")
    return chunk_hex, kx, ky


def lease_from_chunk(chunk_rec):
    """Mint (or RENEW) a lease from a chunk record: the lease names exactly this state. Renewal after
    a leased edit is `lease_from_chunk(the new chunk)` — the lease chain is the region's write
    history."""
    try:
        kx, ky, _cells = _CK.restore_chunk(chunk_rec)
        return lease_record(_CK.address(chunk_rec), kx, ky)
    except _CK.ChunkError as exc:
        raise LeaseError(f"cannot lease a refused chunk: {exc}")


def mint_lease(field, csize, kx, ky):
    """The gate/test convenience: lease region (kx, ky) of a full in-memory world at its current
    state."""
    chunks = _CK.cut(field, csize)
    if (kx, ky) not in chunks:
        raise LeaseError(f"region ({kx},{ky}) is outside the world's chunk grid")
    return lease_from_chunk(chunks[(kx, ky)])


def valid(man, ls):
    """STATE-FREE validity: from the manifest ALONE, is the lease's authority unmoved? True iff the
    slot for the lease's region still carries the lease's chunk digest. No store, no field, no chunk
    bytes — a coordinator answers from 55 + 32·n bytes."""
    chunk_hex, kx, ky = restore_lease(ls)
    try:
        _w, _h, _c, grid = _CK.parse_manifest(man)
    except _CK.ChunkError as exc:
        raise LeaseError(f"validity needs a verified manifest: {exc}")
    if (kx, ky) not in grid:
        raise LeaseError(f"lease region ({kx},{ky}) is outside the manifest grid")
    return grid[(kx, ky)] == chunk_hex


def admit(man, store, ls, rec):
    """THE LEASED ADMISSION: the cheap path the mint-time proof licenses — validity (one manifest
    slot), the under-the-lease binding (the record's parent IS the lease's digest), the region tie,
    then ONE shard apply against the CURRENT chunk (fetched by the current slot digest, NEVER the
    lease's — the anamnesis store still holds the stale bytes, and fetching by lease digest would
    silently revert the interval's edits: the lost update) and an address-substituting reunify.
    Returns (new_manifest, new_chunk). Expiry, foreign state, region mismatch, and a missing chunk
    are typed LEASE-REFUSE; the shard CAS underneath refuses independently (two layers)."""
    chunk_hex, kx, ky = restore_lease(ls)
    if not valid(man, ls):
        raise LeaseError(f"expired — the authority of region ({kx},{ky}) has moved from "
                         f"{chunk_hex[:12]}…; a stale admission is refused, never a lost update")
    try:
        parent, rkx, rky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise LeaseError(f"the record refused: {exc}")
    if parent != chunk_hex:
        raise LeaseError(f"the edit was authored under {parent[:12]}…, not this lease's state "
                         f"{chunk_hex[:12]}… — a lease admits only edits under the state it names")
    if (rkx, rky) != (kx, ky):
        raise LeaseError(f"the record claims region ({rkx},{rky}) but the lease names ({kx},{ky})")
    _w, _h, _c, grid = _CK.parse_manifest(man)
    cur_hex = grid[(kx, ky)]
    try:
        cur = store[cur_hex]
    except KeyError:
        raise LeaseError(f"the CURRENT chunk {cur_hex[:12]}… is missing from the store")
    try:
        new_chunk = _RN.shard_apply(cur, rec)                   # the deep guard: the shard CAS
    except _RN.RanError as exc:
        raise LeaseError(f"the shard refused the leased edit: {exc}")
    try:
        new_man = _RN.reunify(man, (new_chunk,))
    except _RN.RanError as exc:
        raise LeaseError(f"reunification refused: {exc}")
    return new_man, new_chunk


def admission_cost_bytes(csize, w, h):
    """The admission increment: the shard's chunk + record, plus the coordinator's manifest."""
    return _RN.shard_cost_bytes(csize) + _CK.manifest_bytes(w, h, csize)


def amortized_cost_bytes(csize, w, h, k):
    """One lease amortizes k admissions: LEASE_BYTES + k * admission — the temporal dividend as a
    closed form under the same budget law."""
    if not (type(k) is int and k >= 0):
        raise LeaseError(f"k must be a non-negative int, got {k!r}")
    return LEASE_BYTES + k * admission_cost_bytes(csize, w, h)


def lease_digest(name, mint_hex, head_hex, count, nbytes, verdict):
    """URDRLSE1 canon — SHA-256(MAGIC | name | mint | head | count | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|m:{mint_hex}|h:{head_hex}|k:{count}|n:{nbytes}|v:{verdict}".encode())
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
    key = (x // c, y // c)
    chunk = store[grid[key]]
    kx, ky, cells = _CK.restore_chunk(chunk)
    old = cells[y - ky * c][x - kx * c]
    return _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)


def _evolve(man, store, x, y, dh, c):
    """One lawful leased step of the world: lease the current state of (x,y)'s region, admit."""
    _w, _h, _c, grid = _CK.parse_manifest(man)
    ls = lease_from_chunk(store[grid[(x // c, y // c)]])
    rec = _rec_under(man, store, x, y, dh, c)
    new_man, ch = admit(man, store, ls, rec)
    store[_CK.address(ch)] = ch
    return new_man


def _scene_long_watch():
    """The interval commutation: a lease minted at t0, three disjoint edits evolve the world, and
    the leased edit (its bytes unchanged) admits at every insertion position — one head."""
    fld = _blank()
    man0, store0 = _state(fld, 8)
    mint = _CK.address(man0)
    ls = mint_lease(fld, 8, 0, 1)
    rec_e = _rec_under(man0, store0, 5, 8, 1000, 8)
    chain = ((2, 2, 11), (12, 4, 22), (12, 12, 33))
    heads = set()
    for pos in range(len(chain) + 1):
        man, store = man0, dict(store0)
        for (x, y, dh) in chain[:pos]:
            man = _evolve(man, store, x, y, dh, 8)
        new_man, ch = admit(man, store, ls, rec_e)
        store[_CK.address(ch)] = ch
        man = new_man
        for (x, y, dh) in chain[pos:]:
            man = _evolve(man, store, x, y, dh, 8)
        heads.add(_CK.address(man))
    ok = len(heads) == 1
    head = heads.pop()
    return mint, head, len(chain) + 1, LEASE_BYTES, ("ADMIT" if ok else "LEASE-REFUSE")


def _scene_relay():
    """Self-expiry + renewal: the lease dies at its own use; the renewal from the new chunk admits —
    three links of the region's write history, each a content address."""
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    ls = mint_lease(fld, 8, 0, 1)
    links = 0
    for dh in (100, 50, -30):
        rec = _rec_under(man, store, 5, 8, dh, 8)
        man2, ch = admit(man, store, ls, rec)
        store[_CK.address(ch)] = ch
        spent = False
        try:
            admit(man2, store, ls, _rec_under(man2, store, 5, 8, 1, 8))
        except LeaseError:
            spent = True
        if not spent:
            break
        ls = lease_from_chunk(ch)
        man = man2
        links += 1
    ok = links == 3
    return mint, _CK.address(man), links, 3 * LEASE_BYTES, ("ADMIT" if ok else "LEASE-REFUSE")


def _scene_amortized():
    """The amortization theorem: at two interval heads, the cheap admission equals the full global
    reproof (terraform lift on the reassembled world), bit-for-bit."""
    import terraform as _TF
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    ls = mint_lease(fld, 8, 0, 1)
    rec_e = _rec_under(man, store, 5, 8, 1000, 8)
    ok = True
    head = mint
    for (x, y, dh) in ((2, 2, 11), (12, 4, 22)):
        man = _evolve(man, store, x, y, dh, 8)
        cheap, _ch = admit(man, store, ls, rec_e)
        world = _CK.reassemble(man, store)
        lifted = _TF.edit_record(_TF.parent_address(world, 8), 5, 8, world[8][5],
                                 world[8][5] + 1000)
        full = _TF.parent_address(_TF.apply_edit(world, 8, lifted), 8)
        ok = ok and _CK.address(cheap) == full
        head = _CK.address(cheap)
    return mint, head, 2, amortized_cost_bytes(8, 16, 16, 2), ("ADMIT" if ok else "LEASE-REFUSE")


def _scene_expired():
    """The lost-update law: an interloper moves the leased chunk at ANOTHER cell (height CAS blind);
    the stale admission refuses in both layers, though the stale chunk still sits in the store."""
    fld = _blank()
    man, store = _state(fld, 8)
    mint = _CK.address(man)
    ls = mint_lease(fld, 8, 0, 1)
    rec_e = _rec_under(man, store, 5, 8, 1000, 8)
    man2 = _evolve(man, store, 6, 8, 77, 8)                     # the interloper, same chunk
    layer1 = valid(man2, ls) is False
    layer2 = trap = False
    try:
        admit(man2, store, ls, rec_e)
    except LeaseError:
        layer2 = True
    trap = restore_lease(ls)[0] in store                        # the stale bytes ARE still there
    ok = layer1 and layer2 and trap
    return mint, _CK.address(man2), 0, 0, ("LEASE-REFUSE" if ok else "ADMIT")


_SCENES = {"long_watch": _scene_long_watch, "relay": _scene_relay,
           "amortized": _scene_amortized, "expired": _scene_expired}
SCENES = ("long_watch", "relay", "amortized", "expired")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    mint, head, count, nbytes, verdict = scene_case(name)
    return lease_digest(name, mint, head, count, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_lease.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LeaseError(f"no golden named {name!r}")
