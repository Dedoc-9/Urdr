# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rannull — RAN-0, the authority-nullity certificate (T3.42, MMO Stage I, URDRRAN0): the composition
of the two proof domains. `chunkstate` certifies OWNERSHIP (which region owns which state); `commute`
certifies SEMANTIC INDEPENDENCE (order cannot matter). Neither alone certifies distributed execution:
ownership without independence still serializes on the semantics; independence without ownership still
serializes on the WORLD BINDING — and that is the find this rung is built around: terraform's global
CAS binds every edit to the world's MANIFEST address, which is itself a shared authority touching
every chunk (the reason even rank-0 commute pairs needed explicit rebases: the shared binding moved).

THE REGIONAL EDIT RECORD re-binds the CAS to the edit's own authority: MAGIC(8) | parent CHUNK
digest(32) | kx(4) | ky(4) | x(4) | y(4) | old_h(8) | new_h(8) | SHA-256(32) — RAN_RECORD_BYTES = 104.
The record names exactly what it binds: one chunk's content address, one cell transition. Nothing
global appears in it, so nothing global can be held by it.

THE AUTHORITY (first-class, certified, minimal). authority(E) = the closure of region(E) (chunkstate's
floor law), blast(E) (MEASURED by lifting E to the global law and diffing manifest slots — terraform's
exactly-one-slot theorem re-derived per edit, never assumed from geometry), and demand(E) (the cells
the regional CAS reads). At this rung's granularity the three sources must AGREE on one chunk —
misalignment (a record claiming a region its cell is not in) is RAN-REFUSE, the annexation law applied
to writes. Authorities are frozensets of chunk keys; disjointness, union — the algebra's first two
operations — are exactly what the certificate consumes.

THE NULLITY (a proof of absence). RAN-0: if authority(EA) ∩ authority(EB) = ∅, then
Execute(EA || EB) == Execute(EA; EB) == Execute(EB; EA) — with TRUE concurrency modeled honestly at
three levels of informational absence: (1) the SHARD — `shard_apply(chunk_record, record)` is a pure
function whose inputs do not contain the world (the frame property: the same chunk embedded in two
different worlds yields byte-identical outputs, because influence from outside the authority has no
channel to arrive by); (2) the COORDINATOR — `parallel_head` runs from the parent MANIFEST plus the
two parent chunk records alone (addresses, not state: a store lacking every other chunk's bytes still
yields the head); (3) the PROVER — `nullity` discharges the equivalence obligation against the global
law (terraform lift + explicit rebases, both serial orders) AND the commute-domain diamond head, all
four heads equal bit-for-bit, and the certificate embeds the ORIGINAL records unchanged — zero
rebases, because no shared authority moved. Synchronization is not omitted; it is shown to be
unnecessary by construction.

OVERLAP: same chunk → RAN-REFUSE, in two layers proven individually redundant and jointly
load-bearing (the authority-disjointness check; the head comparison, which catches a slot written
twice). The commute fallback still certifies the lifted pair at rank 1 — nullity is STRICTLY stronger
than commutation; refusing it contradicts nothing.

THE CERTIFICATE. cert = MAGIC | rec_a(104) | rec_b(104) | SHA-256 — CERT_BYTES = 248; evidence, never
authority: `check_nullity` re-derives the entire proof from the parent world and requires the
presented bytes to reproduce bit-for-bit. THE COSTS split honestly along the roles: the SHARD's
increment is one chunk + one record (no manifest — it never mints one); the COORDINATOR's is one
manifest + one certificate; both under `storecost`'s budget law.

THE ARC THIS COMPLETES A STEP OF: persistence proves replay; terraform proves locality; commutation
proves semantic independence; chunkstate proves ownership; RAN-0 proves authority nullity — and
distributed execution becomes a theorem obtained by composing proofs, not a new subsystem.

GRADE. The record and certificate closed forms, round-trips, and exhaustive corruption refuses; the
authority alignment (region == measured blast == demand) and its misalignment refuse; the frame
property and the minimal-knowledge coordinator; the four-way head equality (parallel, both serials,
the commute diamond); the zero-rebase witness; the two-layer overlap refuse; the regional CAS refuses
(stale chunk, wrong height, wrong region, cross-magic both directions); forgery refusal under full
re-derivation; the recovery composition (a disjoint-region actor revives green across the pair; an
edit under the actor still refuses); the split costs; and determinism are MEASURED (exact,
reproducible, a defect diverges). DECLARED: the full authority ALGEBRA (difference, projection,
closure over transcripts and actor demand — the operations beyond disjointness/union), n-way nullity
beyond pairwise, LIVE authority migration mid-window (which shard SIMULATES which actor — the C8
attempt-#1 live half; this rung answers the WRITE-admission half), and scheduling policy. The shard
isolation is INFORMATIONAL (the inputs do not contain the world), not physical — cross-process
transport, failures mid-parallel-apply, and wall-clock are `bench.py`/future territory.
`does_not_show`: eviction/prefetch (chunkload's boundary stands); WHO may author (`authinput`);
cross-placement (Python reference only until a placement reproduces these digests)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRRAN0"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunk records, manifests — ownership
import terraform as _TF                                         # the global lift — the serial law
import commute as _CM                                           # the diamond domain — independence

DIGEST_BYTES = 32
COORD_BYTES = 4
RAN_RECORD_BYTES = len(MAGIC) + DIGEST_BYTES + 4 * COORD_BYTES + 8 + 8 + DIGEST_BYTES  # 104
CERT_BYTES = len(MAGIC) + 2 * RAN_RECORD_BYTES + DIGEST_BYTES                          # 248


class RanError(Exception):
    def __init__(self, message):
        super().__init__(f"RAN-REFUSE: {message}")
        self.code = "RAN-REFUSE"


def regional_record(parent_chunk_hex, kx, ky, x, y, old_h, new_h):
    """The regional edit record: CAS-bound to its CHUNK's content address, not the world's manifest —
    the record names exactly the authority it holds. MAGIC | parent chunk digest | kx | ky | x | y |
    old_h | new_h | SHA-256."""
    if not (isinstance(parent_chunk_hex, str) and len(parent_chunk_hex) == 64):
        raise RanError(f"parent must be a 64-hex chunk address, got {parent_chunk_hex!r}")
    try:
        parent = bytes.fromhex(parent_chunk_hex)
    except ValueError:
        raise RanError("parent chunk address is not hex")
    pre = bytearray(MAGIC) + parent
    for v, nm in ((kx, "kx"), (ky, "ky"), (x, "x"), (y, "y")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise RanError(f"{nm} must be uint32, got {v!r}")
        pre += v.to_bytes(COORD_BYTES, "big")
    for v, nm in ((old_h, "old height"), (new_h, "new height")):
        if not (type(v) is int and -(1 << 63) <= v < (1 << 63)):
            raise RanError(f"{nm} {v!r} does not fit signed int64 — refuse, never truncate")
        pre += (v & ((1 << 64) - 1)).to_bytes(8, "big")
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def restore_regional(buf):
    """The inverse: (parent_hex, kx, ky, x, y, old_h, new_h) BIT-FOR-BIT or a typed refuse. Digest
    first; exact length; every flip and truncation refuses."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise RanError("a regional record must be bytes")
    buf = bytes(buf)
    if len(buf) != RAN_RECORD_BYTES:
        raise RanError(f"a regional record must be exactly {RAN_RECORD_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise RanError("bad magic — not a URDRRAN0 regional record")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise RanError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    parent = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
    kx, ky, x, y = (int.from_bytes(buf[off + i * COORD_BYTES:off + (i + 1) * COORD_BYTES], "big")
                    for i in range(4))
    off += 4 * COORD_BYTES
    old_h = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
    new_h = int.from_bytes(buf[off:off + 8], "big", signed=True)
    return parent, kx, ky, x, y, old_h, new_h


def shard_apply(chunk_rec, rec):
    """THE SHARD: a pure function of (one chunk record, one regional record) — the world is
    informationally absent, so influence from outside the authority has no channel to arrive by (the
    frame property). Verifies the regional CAS (the chunk's content address), the region claim (the
    record's chunk must BE this chunk, and the cell must lie inside it — the annexation law on
    writes), and the old height; mints the new chunk record through chunkload's own constructor, so
    the output is a law-abiding chunk any manifest can bind."""
    parent, kx, ky, x, y, old_h, new_h = restore_regional(rec)
    try:
        ckx, cky, cells = _CK.restore_chunk(chunk_rec)
        live = _CK.address(chunk_rec)
    except _CK.ChunkError as exc:
        raise RanError(f"the shard's chunk refused: {exc}")
    if parent != live:
        raise RanError(f"stale chunk {parent[:12]}… (the chunk is {live[:12]}…) — a regional edit "
                       f"authored against another chunk state is refused, never rebased")
    if (ckx, cky) != (kx, ky):
        raise RanError(f"the record claims region ({kx},{ky}) but was applied to chunk "
                       f"({ckx},{cky}) — refused")
    cw, ch = len(cells[0]), len(cells)
    lx, ly = x - kx * cw, y - ky * ch
    if not (0 <= lx < cw and 0 <= ly < ch):
        raise RanError(f"cell ({x},{y}) lies outside claimed region ({kx},{ky}) — a write may not "
                       f"annex a cell it does not own")
    if cells[ly][lx] != old_h:
        raise RanError(f"old height {old_h} does not match the live cell {cells[ly][lx]} — refused")
    new_cells = tuple(tuple(new_h if (xx, yy) == (lx, ly) else v for xx, v in enumerate(row))
                      for yy, row in enumerate(cells))
    return _CK.chunk_record(kx, ky, new_cells)


def authority(field, csize, rec):
    """The certified minimal authority of a regional edit: the closure of REGION (chunkstate's floor
    law), BLAST (measured — the edit lifted to the global law, manifest slots diffed; terraform's
    exactly-one-slot theorem re-derived per edit, never assumed), and DEMAND (the cells the regional
    CAS reads). The three sources must AGREE on one chunk; misalignment refuses. Returns a frozenset
    of chunk keys — the object the nullity predicate consumes."""
    parent, kx, ky, x, y, old_h, new_h = restore_regional(rec)
    region = (x // csize, y // csize)
    if region != (kx, ky):
        raise RanError(f"authority misalignment: cell ({x},{y}) floors to region {region} but the "
                       f"record claims ({kx},{ky}) — a claim must match the placement law")
    try:
        lifted = _TF.edit_record(_TF.parent_address(field, csize), x, y, old_h, new_h)
        new_fld = _TF.apply_edit(field, csize, lifted)
    except _TF.TerraformError as exc:
        raise RanError(f"the blast measurement refused: {exc}")
    old_slots = {k: _CK.address(r) for k, r in _CK.cut(field, csize).items()}
    new_slots = {k: _CK.address(r) for k, r in _CK.cut(new_fld, csize).items()}
    blast = frozenset(k for k in old_slots if old_slots[k] != new_slots[k])
    demand = frozenset({(x // csize, y // csize)})
    if not (blast == demand == frozenset({region})):
        raise RanError(f"authority misalignment: region {region}, measured blast {sorted(blast)}, "
                       f"demand {sorted(demand)} must agree at this granularity")
    return frozenset({region})


def _seal(preamble):
    """Append the outer digest. Exposed for the forgery falsifiers: a re-sealed tamper must still fail
    `check_nullity`'s re-derivation."""
    return preamble + hashlib.sha256(preamble).digest()


def reunify(man, new_chunks):
    """THE COORDINATOR: the parent manifest's digest grid with each new chunk's slot substituted —
    a new manifest minted from ADDRESSES, not state (no other chunk's bytes are consulted). Each new
    chunk must be a verified record whose key lies in the grid."""
    w, h, csize, grid = _CK.parse_manifest(man)
    for rec in new_chunks:
        try:
            kx, ky, cells = _CK.restore_chunk(rec)
        except _CK.ChunkError as exc:
            raise RanError(f"a reunified chunk refused: {exc}")
        if (kx, ky) not in grid:
            raise RanError(f"chunk ({kx},{ky}) is outside the manifest grid")
        if len(cells) != csize or len(cells[0]) != csize:
            raise RanError(f"chunk ({kx},{ky}) is {len(cells[0])}x{len(cells)}, the grid is C={csize}")
        grid[(kx, ky)] = bytes(rec)[-DIGEST_BYTES:].hex()
    pre = bytearray(_CK.MAP_MAGIC)
    for v in (w, h, csize):
        pre += v.to_bytes(COORD_BYTES, "big")
    for ky in range(h // csize):
        for kx in range(w // csize):
            pre += bytes.fromhex(grid[(kx, ky)])
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def parallel_head(man, store, rec_a, rec_b):
    """The parallel execution path, minimal-knowledge: fetch ONLY the two parent chunks from the
    store (by the addresses the records bind), shard-apply each independently, reunify by address
    substitution. A store lacking every other chunk's bytes suffices — the coordinator holds
    addresses, not state. Returns the head manifest address."""
    pa = restore_regional(rec_a)[0]
    pb = restore_regional(rec_b)[0]
    try:
        ca, cb = store[pa], store[pb]
    except KeyError as exc:
        raise RanError(f"parent chunk {exc} missing from the shard store")
    new_a = shard_apply(ca, rec_a)
    new_b = shard_apply(cb, rec_b)
    return _CK.address(reunify(man, (new_a, new_b)))


def nullity(field, csize, rec_a, rec_b):
    """THE RAN-0 PREDICATE, discharged constructively: certified disjoint authorities, then the
    four-way head equality — the PARALLEL head (shards + address-substituting coordinator), BOTH
    global serial heads (terraform lift + explicit rebases), and the commute-domain diamond head —
    all bit-for-bit. Returns (certificate, head_hex); any failure is RAN-REFUSE. The certificate
    embeds the ORIGINAL records unchanged: zero rebases, because no shared authority moved."""
    auth_a = authority(field, csize, rec_a)
    auth_b = authority(field, csize, rec_b)
    if auth_a & auth_b:
        raise RanError(f"authorities intersect at {sorted(auth_a & auth_b)} — a shared authority "
                       f"exists, so nullity cannot be certified (commutation at rank 1 may still "
                       f"hold; that is `commute`'s law, not this one)")
    _pa, _ka, _kya, xa, ya, oa, na = restore_regional(rec_a)
    _pb, _kb, _kyb, xb, yb, ob, nb = restore_regional(rec_b)
    man = _CK.field_manifest(field, csize)
    chunks = _CK.cut(field, csize)
    store = {_CK.address(r): r for r in chunks.values()}
    par_head = parallel_head(man, store, rec_a, rec_b)
    la = _TF.edit_record(_TF.parent_address(field, csize), xa, ya, oa, na)
    lb = _TF.edit_record(_TF.parent_address(field, csize), xb, yb, ob, nb)
    wa = _TF.apply_edit(field, csize, la)
    wab = _TF.apply_edit(wa, csize, _CM.rebase_edit(lb, _TF.parent_address(wa, csize)))
    wb = _TF.apply_edit(field, csize, lb)
    wba = _TF.apply_edit(wb, csize, _CM.rebase_edit(la, _TF.parent_address(wb, csize)))
    try:
        _cmcert, cm_head = _CM.certify(field, csize, la, lb)
    except _CM.CommuteError as exc:
        raise RanError(f"the commute domain refused the lifted pair: {exc}")
    heads = {par_head, _TF.parent_address(wab, csize), _TF.parent_address(wba, csize), cm_head}
    if len(heads) != 1:
        raise RanError(f"the four-way head equality failed ({len(heads)} distinct heads) — parallel, "
                       f"both serials, and the diamond must agree bit-for-bit")
    return _seal(MAGIC + bytes(rec_a) + bytes(rec_b)), par_head


def restore_nullity(buf):
    """The certificate inverse: (rec_a, rec_b) BIT-FOR-BIT or a typed refuse — outer digest first,
    then the embedded records under their own digests (defense in depth against a re-sealed
    forgery)."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise RanError("a nullity certificate must be bytes")
    buf = bytes(buf)
    if len(buf) != CERT_BYTES:
        raise RanError(f"a nullity certificate must be exactly {CERT_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise RanError("bad magic — not a URDRRAN0 nullity certificate")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise RanError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    rec_a = buf[off:off + RAN_RECORD_BYTES]; off += RAN_RECORD_BYTES
    rec_b = buf[off:off + RAN_RECORD_BYTES]
    restore_regional(rec_a)
    restore_regional(rec_b)
    return rec_a, rec_b


def check_nullity(field, csize, buf):
    """Independent re-verification — evidence, never authority: restore, re-derive the ENTIRE proof
    from the parent world, require the presented bytes to reproduce bit-for-bit. Returns head_hex."""
    rec_a, rec_b = restore_nullity(buf)
    cert2, head = nullity(field, csize, rec_a, rec_b)
    if cert2 != bytes(buf):
        raise RanError("re-derivation does not reproduce the presented certificate — forged")
    return head


def shard_cost_bytes(csize):
    """The SHARD's durable increment: one new chunk + one regional record. No manifest — the shard
    never mints one; that is the point."""
    return _CK.chunk_bytes(csize) + RAN_RECORD_BYTES


def coordinator_cost_bytes(csize, w, h):
    """The COORDINATOR's durable increment: one new manifest + one nullity certificate. No chunk —
    the coordinator never touches state; that is the point."""
    return _CK.manifest_bytes(w, h, csize) + CERT_BYTES


def rannull_digest(name, parent_hex, head_hex, nshards, nbytes, verdict):
    """URDRRAN0 canon — SHA-256(MAGIC | name | parent | head | shards | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|h:{head_hex}|s:{nshards}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _rrec(fld, c, x, y, dh):
    key = (x // c, y // c)
    chunk = _CK.cut(fld, c)[key]
    return regional_record(_CK.address(chunk), key[0], key[1], x, y, fld[y][x], fld[y][x] + dh)


def _scene_twin_shards():
    """Two regional edits in disjoint chunks of blank at C=8: the nullity certified — parallel ==
    both serials == the diamond, and the certificate independently re-verifies."""
    fld = _blank()
    p = _TF.parent_address(fld, 8)
    ra, rb = _rrec(fld, 8, 5, 8, 1000), _rrec(fld, 8, 12, 4, 777)
    cert, head = nullity(fld, 8, ra, rb)
    ok = check_nullity(fld, 8, cert) == head
    return p, head, 2, CERT_BYTES, ("ADMIT" if ok else "RAN-REFUSE")


def _scene_frame_witness():
    """The proof of absence: the SAME chunk embedded in two DIFFERENT worlds, the same regional
    record — byte-identical shard outputs. The witness is the new chunk's own content address."""
    fld = _blank()
    p = _TF.parent_address(fld, 8)
    far = _TF.edit_record(p, 12, 4, fld[4][12], fld[4][12] + 777)
    world2 = _TF.apply_edit(fld, 8, far)
    c1, c2 = _CK.cut(fld, 8)[(0, 0)], _CK.cut(world2, 8)[(0, 0)]
    rec = _rrec(fld, 8, 2, 2, 50)
    out1, out2 = shard_apply(c1, rec), shard_apply(c2, rec)
    ok = c1 == c2 and out1 == out2
    return p, _CK.address(out1), 1, shard_cost_bytes(8), ("ADMIT" if ok else "RAN-REFUSE")


def _scene_annexed():
    """Overlapping authority — same chunk, distinct cells: RAN-REFUSE, while the commute fallback
    still certifies the lifted pair at rank 1 (nullity strictly stronger, contradicting nothing)."""
    fld = _blank()
    p = _TF.parent_address(fld, 8)
    ra, rb = _rrec(fld, 8, 5, 8, 7), _rrec(fld, 8, 6, 8, -3)
    refused = fallback = False
    try:
        nullity(fld, 8, ra, rb)
    except RanError:
        refused = True
    la = _TF.edit_record(p, 5, 8, fld[8][5], fld[8][5] + 7)
    lb = _TF.edit_record(p, 6, 8, fld[8][6], fld[8][6] - 3)
    cmcert, _h = _CM.certify(fld, 8, la, lb)
    fallback = _CM.restore_cert(cmcert)[2] == 1
    ok = refused and fallback
    return p, p, 0, 0, ("RAN-REFUSE" if ok else "ADMIT")


def _scene_healed_region():
    """Recovery inherits the nullity: an actor parked in a region disjoint from both authorities
    revives green across the parallel pair; an edit under the actor still refuses."""
    import persist as _PS
    import resurrect as _RS
    fld = _blank()
    p = _TF.parent_address(fld, 8)
    records, man_w = _PS.checkpoint_window(fld, ((2, 8),), "eeee", 40, 4, 4)
    window = _RS.revive_mem(fld, man_w, {_PS.address(r): r for r in records})
    ra, rb = _rrec(fld, 8, 12, 4, 777), _rrec(fld, 8, 12, 12, 555)
    _cert, head = nullity(fld, 8, ra, rb)
    chunks = _CK.cut(fld, 8)
    new_a, new_b = shard_apply(chunks[(1, 0)], ra), shard_apply(chunks[(1, 1)], rb)
    new_man = reunify(_CK.field_manifest(fld, 8), (new_a, new_b))
    store = {_CK.address(r): r for r in chunks.values()}
    store.update({_CK.address(new_a): new_a, _CK.address(new_b): new_b})
    world = _CK.reassemble(new_man, store)
    green = under_refused = False
    try:
        green = _RS.check_states(world, window) == window and _CK.address(new_man) == head
    except _RS.ResurrectError:
        green = False
    under = _rrec(fld, 8, 2, 8, 3)
    new_u = shard_apply(chunks[(0, 1)], under)
    u_store = dict(store); u_store[_CK.address(new_u)] = new_u
    u_world = _CK.reassemble(reunify(_CK.field_manifest(fld, 8), (new_u,)), u_store)
    try:
        _RS.check_states(u_world, window)
    except _RS.ResurrectError:
        under_refused = True
    ok = green and under_refused
    return p, head, 2, coordinator_cost_bytes(8, 16, 16), ("ADMIT" if ok else "RAN-REFUSE")


_SCENES = {"twin_shards": _scene_twin_shards, "frame_witness": _scene_frame_witness,
           "annexed": _scene_annexed, "healed_region": _scene_healed_region}
SCENES = ("twin_shards", "frame_witness", "annexed", "healed_region")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, head, nshards, nbytes, verdict = scene_case(name)
    return rannull_digest(name, p, head, nshards, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_rannull.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RanError(f"no golden named {name!r}")
