# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""migrate — AUTHORITY MIGRATION AS LEASE TRANSFER (Phase M, rung M2, URDRMIG1): the witness-carrying
migration certificate (WCMC). `lease` proved the INTERVAL (write capability as proof-from-state);
`nway` (M1) proved the SCHEDULE (N disjoint authorities execute as one theorem). Neither can see a
HANDOFF — and that blindness is this rung's born-red motivation, kept as a permanent falsifier: a
lease is minted from STATE (`lease_from_chunk`), and a migration moves NO state, so the old steward's
retained lease is BYTE-IDENTICAL to the new steward's fresh one; `lease.admit` alone ADMITS the
usurper. Standing authority (WHO keeps writing) is therefore a different object from write capability
(MAY this edit land), and M2 makes it first-class: authority over a region moves by expiring the
steward's standing on one node and minting it on another, and THE TRANSFER ITSELF IS A
PROOF-PRODUCING OPERATION — it emits a content-addressed MIGRATION CERTIFICATE, and admission on the
destination requires the CONJUNCTION: a valid lease AND a custody chain of valid certificates naming
the writer. Migration is lawful iff its certificate exists and re-derives; no certificate, no
authority — the equal-or-refuse discipline extended from edits and commutation to the distributed
handoff protocol.

THE CERTIFICATE (128 bytes): MAGIC | parent cert digest (zeros at genesis) | kx | ky | src steward |
dst steward | the region's CHUNK digest at handoff | SHA-256. The design decision, RAN-0's lesson
applied to custody: the certificate binds the AUTHORITY (one chunk digest — its minimal dependency
closure), never the world manifest. Nothing global appears in it, so nothing global can be held by
it — and the dependency theorem comes out STRUCTURAL: a write certified disjoint from the region
leaves the certificate bytes valid UNCHANGED (dependency_set ∩ changed = ∅ needs no revalidation),
proven in the migration diamond as byte-identical certificate transport across orders. Witness
preservation is likewise structural: `migrate` never returns a world — pre/post manifest equality is
a theorem checked in bytes, not a pair of certificate fields; a migration that moved state is
unrepresentable, not merely refused.

THE STEWARD MANIFEST: STEWARD_MAGIC | W | H | C | per-region (steward tag | custody cert digest) |
SHA-256 — custody's counterpart of the chunk manifest, content-addressed, total (every region has
exactly one steward). Custody moves the STEWARD digest, never the witness: the world manifest is
untouched by migration (the D15 lesson above the witness instead of below it — authority ⊥ witness).

THE CUSTODY CHAIN: each certificate's parent is the region's previous certificate digest — the
custody chain IS the region's authority history, each link a content address (the transcript law on
standing authority, exactly as the lease chain is the write history). Order is STRUCTURAL: a
reordered, duplicated, or forked transfer refuses on the parent CAS alone, no sequence numbers to
forge. THE MIGRATION CAS: adoption requires the certificate's chunk binding to equal the region's
LIVE slot — a migration authored against a moved authority is refused, never rebased.

ADMISSION (the conjunctive predicate) in layers proven individually redundant and jointly
load-bearing: (1) the steward SLOT names the writer (state-free, one slot — `valid()`'s idiom);
(2) the custody CHAIN re-derives from genesis and its head names the writer (evidence, never
authority — a forged manifest whose slot contradicts its own cited chain refuses on the derived-data
check); (3) SUCCESSION — the anamnesis trap, custody edition: old manifests and old certificates sit
in the store FOREVER, integral; integrity != truth, so a presented custody head with a known
successor certificate refuses (retention turned into evidence); then (4) the leased admission,
inheriting every lease law unchanged (lost-update impossibility, self-expiry, interval transport).
THE HANDOFF PREFIX LAW: every prefix of the handoff admits AT MOST ONE writer — minted-only: src
still writes; TORN (certificate adopted, manifest not advanced): NOBODY writes, the region freezes
(the CP posture executable at one region: refuse rather than guess); committed: dst writes, src
refuses.

PRIOR ART, reviewed honestly (web, at design time): every ingredient exists — leases (Gray &
Cheriton 1989), authority handoff carrying a state-digest certificate (PBFT stable checkpoints,
Castro & Liskov 1999), transfer-mints-a-certificate (FastPay, Baudet et al. 2020), lease
disjointness as a proven invariant (CockroachDB leader leases, TLA+), fencing tokens (Kleppmann
2016), dependency-closure caching (Bazel action cache; Adapton). The claim here is the COMPOSITION
only: the lease transfer itself as a certifying operation in the SAME content-addressed
replay/authority/lease/witness calculus as every other law in this repository, with typed refusal —
never a novelty claim on any ingredient.

GRADE (Phase M rung M2). The certificate and steward-manifest closed forms, round-trips, and
exhaustive corruption refuses; the lease-blindness demonstration; witness neutrality and custody
locality (exactly one slot); single-writer refusal in the layered admission (individually redundant,
jointly load-bearing — all gutted, the double-write lands and the falsifier detects it); the
succession refuse with the stale-manifest trap demonstrated; custody replay determinism with
structural order (reordered / duplicated / forked refuse); the migration CAS; the handoff prefix
law; the migration diamond with byte-identical certificate transport; the migration-blind monolithic
oracle agreement; and a seeded randomized-schedule property sweep (layouts, schedules, expiries,
usurpers, duplicated and forked transfers) are MEASURED (exact, reproducible, a defect diverges).
DECLARED: steward IDENTITY binding (tags are opaque 8-byte names; signatures are `sealwrit`
territory, keys and distribution out of scope — the brief's keyless pattern); SEMANTIC dependency
witnesses (obligation sets, pending-revalidation, transport proofs that rewrite certificates across
dependency evolution — the named successor arc; M2 ships the structural form only); custody-head
currency (the coordinator must admit against the CURRENT steward manifest, the same trust anchor the
world manifest already is; a partitioned custody store is M4's territory); LIVE meshed simulation
(M3). `does_not_show`: WHO may be a steward (issuance is fiat at genesis — `authinput`); revocation
other than by migration; cross-process transport and wall-clock (`bench.py`); cross-placement
(URDRMIG1 is Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRMIG1"
STEWARD_MAGIC = b"URDRMIG1MAP"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, manifests, addresses
import rannull as _RN                                           # regional records, shard_apply
import lease as _LS                                             # the leased admission (inherited whole)
import terraform as _TF                                         # the global lift — the migration-blind oracle
import nway as _NW                                              # M1: flat worlds + regional records

DIGEST_BYTES = 32
COORD_BYTES = 4
STEWARD_BYTES = 8
GENESIS_HEX = "00" * DIGEST_BYTES
CERT_BYTES = (len(MAGIC) + DIGEST_BYTES + 2 * COORD_BYTES + 2 * STEWARD_BYTES
              + DIGEST_BYTES + DIGEST_BYTES)                    # 128
_SMAN_OVERHEAD = len(STEWARD_MAGIC) + 3 * COORD_BYTES + DIGEST_BYTES  # 55


class MigrateError(Exception):
    def __init__(self, message):
        super().__init__(f"MIGRATE-REFUSE: {message}")
        self.code = "MIGRATE-REFUSE"


def steward_tag(name):
    """An opaque 8-byte steward tag from a short ASCII name (NUL-padded). Identity BINDING (who may
    hold a tag, signatures) is `sealwrit` territory — DECLARED, the brief's keyless pattern."""
    if not (isinstance(name, str) and 0 < len(name) <= STEWARD_BYTES):
        raise MigrateError(f"a steward name must be 1..{STEWARD_BYTES} ASCII chars, got {name!r}")
    try:
        raw = name.encode("ascii")
    except UnicodeEncodeError:
        raise MigrateError(f"a steward name must be ASCII, got {name!r}")
    if b"\x00" in raw:
        raise MigrateError("a steward name may not contain NUL")
    return raw + b"\x00" * (STEWARD_BYTES - len(raw))


def _tag_str(tag):
    return tag.rstrip(b"\x00").decode("ascii", "replace")


def _check_tag(tag, nm):
    if not ((type(tag) is bytes) and len(tag) == STEWARD_BYTES and tag.rstrip(b"\x00")):
        raise MigrateError(f"{nm} must be a non-empty {STEWARD_BYTES}-byte steward tag, got {tag!r}")
    return tag


def _check_hex(h, nm):
    if not (isinstance(h, str) and len(h) == 2 * DIGEST_BYTES):
        raise MigrateError(f"{nm} must be {2 * DIGEST_BYTES} hex chars, got {h!r}")
    try:
        return bytes.fromhex(h)
    except ValueError:
        raise MigrateError(f"{nm} is not hex")


def migration_certificate(parent_hex, kx, ky, src, dst, chunk_hex):
    """THE WITNESS-CARRYING MIGRATION CERTIFICATE: MAGIC | parent cert digest (zeros at genesis) |
    kx | ky | src | dst | the region's chunk digest at handoff | SHA-256. It binds the AUTHORITY
    (one chunk digest — the minimal dependency closure), never the world; a vacuous transfer
    (src == dst) is refused at mint, not merely discouraged."""
    parent = _check_hex(parent_hex, "parent certificate digest")
    chunk = _check_hex(chunk_hex, "chunk digest")
    _check_tag(src, "src"); _check_tag(dst, "dst")
    if src == dst:
        raise MigrateError(f"a migration must MOVE authority — src == dst == {_tag_str(src)!r} "
                           f"is vacuous and refused")
    pre = bytearray(MAGIC) + parent
    for v, nm in ((kx, "kx"), (ky, "ky")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise MigrateError(f"{nm} must be uint32, got {v!r}")
        pre += v.to_bytes(COORD_BYTES, "big")
    pre += src + dst + chunk
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def restore_certificate(buf):
    """The inverse: (parent_hex, kx, ky, src, dst, chunk_hex) BIT-FOR-BIT or a typed refuse. Exact
    length; digest first; every flip and truncation refuses."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise MigrateError("a migration certificate must be bytes")
    buf = bytes(buf)
    if len(buf) != CERT_BYTES:
        raise MigrateError(f"a migration certificate must be exactly {CERT_BYTES} bytes, "
                           f"got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC or buf[len(MAGIC):len(MAGIC) + 3] == b"MAP":
        raise MigrateError("bad magic — not a URDRMIG1 migration certificate")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise MigrateError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    parent = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
    kx = int.from_bytes(buf[off:off + COORD_BYTES], "big"); off += COORD_BYTES
    ky = int.from_bytes(buf[off:off + COORD_BYTES], "big"); off += COORD_BYTES
    src = buf[off:off + STEWARD_BYTES]; off += STEWARD_BYTES
    dst = buf[off:off + STEWARD_BYTES]; off += STEWARD_BYTES
    chunk = buf[off:off + DIGEST_BYTES].hex()
    return parent, kx, ky, src, dst, chunk


def address(buf):
    """The content address of a verified certificate or steward manifest: the hex of its embedded
    digest. Identity is content; no address for corrupt bytes."""
    if (type(buf) is bytes or type(buf) is bytearray) \
            and bytes(buf[:len(STEWARD_MAGIC)]) == STEWARD_MAGIC:
        parse_steward(buf)
        return bytes(buf)[-DIGEST_BYTES:].hex()
    restore_certificate(buf)
    return bytes(buf)[-DIGEST_BYTES:].hex()


# ---- the steward manifest (custody's counterpart of the chunk manifest) ------------------
def steward_manifest_bytes(w, h, csize):
    """The EXACT steward-manifest size: 55 + 40·n over the n-region grid — the custody closed form."""
    n = (w // csize) * (h // csize)
    return _SMAN_OVERHEAD + (STEWARD_BYTES + DIGEST_BYTES) * n


def _mint_steward(w, h, csize, grid):
    pre = bytearray(STEWARD_MAGIC)
    for v in (w, h, csize):
        pre += v.to_bytes(COORD_BYTES, "big")
    for ky in range(h // csize):
        for kx in range(w // csize):
            tag, cert_hex = grid[(kx, ky)]
            pre += tag + bytes.fromhex(cert_hex)
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def steward_genesis(man, assignments):
    """Genesis custody: every region of the world manifest assigned to exactly ONE steward — custody
    is TOTAL (a missing or foreign region refuses). The cert slot is zeros: the first standing is by
    fiat, and issuance policy is DECLARED (`authinput` territory), exactly as lease issuance is."""
    try:
        w, h, csize, grid = _CK.parse_manifest(man)
    except _CK.ChunkError as exc:
        raise MigrateError(f"genesis needs a verified world manifest: {exc}")
    if set(assignments) != set(grid):
        missing = sorted(set(grid) - set(assignments))
        foreign = sorted(set(assignments) - set(grid))
        raise MigrateError(f"custody must be TOTAL over the grid — missing {missing}, "
                           f"foreign {foreign}")
    sgrid = {}
    for key, tag in assignments.items():
        _check_tag(tag, f"steward of {key}")
        sgrid[key] = (tag, GENESIS_HEX)
    return _mint_steward(w, h, csize, sgrid)


def parse_steward(sman):
    """A verified steward manifest -> (W, H, C, ((kx, ky) -> (tag, cert_hex))). Digest first; the
    structural length must match the grid exactly."""
    if not (type(sman) is bytes or type(sman) is bytearray):
        raise MigrateError("a steward manifest must be bytes")
    sman = bytes(sman)
    if len(sman) < _SMAN_OVERHEAD:
        raise MigrateError(f"steward manifest of {len(sman)} bytes is shorter than the "
                           f"{_SMAN_OVERHEAD}-byte minimum")
    if sman[:len(STEWARD_MAGIC)] != STEWARD_MAGIC:
        raise MigrateError("bad magic — not a URDRMIG1MAP steward manifest")
    if hashlib.sha256(sman[:-DIGEST_BYTES]).digest() != sman[-DIGEST_BYTES:]:
        raise MigrateError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(STEWARD_MAGIC)
    w, h, csize = (int.from_bytes(sman[off + i * COORD_BYTES:off + (i + 1) * COORD_BYTES], "big")
                   for i in range(3))
    off += 3 * COORD_BYTES
    if csize == 0 or w % csize or h % csize:
        raise MigrateError(f"steward dims {w}x{h} / C={csize} are not an admissible grid")
    if len(sman) != steward_manifest_bytes(w, h, csize):
        raise MigrateError(f"steward manifest length {len(sman)} does not match its grid")
    grid = {}
    for ky in range(h // csize):
        for kx in range(w // csize):
            tag = sman[off:off + STEWARD_BYTES]; off += STEWARD_BYTES
            grid[(kx, ky)] = (tag, sman[off:off + DIGEST_BYTES].hex()); off += DIGEST_BYTES
    return w, h, csize, grid


def current_steward(sman, kx, ky):
    """STATE-FREE custody: from the steward manifest ALONE, (tag, custody cert digest) for one
    region — one slot, the `valid()` idiom applied to standing authority."""
    _w, _h, _c, grid = parse_steward(sman)
    if (kx, ky) not in grid:
        raise MigrateError(f"region ({kx},{ky}) is outside the steward grid")
    return grid[(kx, ky)]


def _grid_tie(sman, man):
    """The two manifests must describe ONE grid — a custody map for a different world refuses."""
    sw, sh, sc, sgrid = parse_steward(sman)
    try:
        w, h, c, mgrid = _CK.parse_manifest(man)
    except _CK.ChunkError as exc:
        raise MigrateError(f"a verified world manifest is required: {exc}")
    if (sw, sh, sc) != (w, h, c):
        raise MigrateError(f"the steward grid {sw}x{sh}/C={sc} does not match the world grid "
                           f"{w}x{h}/C={c} — custody for another world is refused")
    return w, h, c, sgrid, mgrid


# ---- the custody chain (evidence, never authority) ---------------------------------------
def check_custody(sman, cert_store, kx, ky):
    """Independent re-derivation of a region's custody: walk the slot's chain head → genesis through
    the certificate store (each link fetched BY ADDRESS and verified — a substituted certificate
    refuses on the filename law), require region agreement, src→dst continuity from genesis, and the
    head's dst to equal the slot's tag (derived data is checkable data — a re-minted manifest whose
    slot contradicts its own cited chain refuses). Returns the chain depth (0 at genesis fiat)."""
    tag, head = current_steward(sman, kx, ky)
    if head == GENESIS_HEX:
        return 0                                                # fiat standing — issuance DECLARED
    chain = []
    cur = head
    seen = set()
    while cur != GENESIS_HEX:
        if cur in seen:
            raise MigrateError(f"custody cycle at {cur[:12]}… — refused")
        seen.add(cur)
        try:
            cert = cert_store[cur]
        except KeyError:
            raise MigrateError(f"custody link {cur[:12]}… is missing from the certificate store — "
                               f"an unverifiable chain confers nothing")
        if address(cert) != cur:
            raise MigrateError(f"certificate under address {cur[:12]}… does not hash to it — "
                               f"a substitution, refused")
        parent, ckx, cky, _src, _dst, _chunk = restore_certificate(cert)
        if (ckx, cky) != (kx, ky):
            raise MigrateError(f"custody link {cur[:12]}… names region ({ckx},{cky}), "
                               f"not ({kx},{ky})")
        chain.append(cert)
        cur = parent
    chain.reverse()                                             # genesis-first
    prev_dst = None
    for cert in chain:
        _p, _kx, _ky, src, dst, _chunk = restore_certificate(cert)
        if prev_dst is not None and src != prev_dst:
            raise MigrateError(f"custody discontinuity — {_tag_str(src)!r} succeeded "
                               f"{_tag_str(prev_dst)!r} without a transfer")
        prev_dst = dst
    if prev_dst != tag:
        raise MigrateError(f"the slot claims steward {_tag_str(tag)!r} but its own chain ends at "
                           f"{_tag_str(prev_dst)!r} — a forged manifest, refused")
    return len(chain)


def _steward_ok(sman, kx, ky, writer):
    """ADMISSION LAYER 1 (cheap, state-free): the steward SLOT names the writer."""
    return current_steward(sman, kx, ky)[0] == writer


def _custody_ok(sman, cert_store, kx, ky, writer):
    """ADMISSION LAYER 2 (deep): the custody CHAIN re-derives and its head names the writer.
    Vacuous at genesis (fiat standing — the slot alone carries it, stated not hidden)."""
    _tag, head = current_steward(sman, kx, ky)
    depth = check_custody(sman, cert_store, kx, ky)
    if depth == 0:
        return True
    cert = cert_store[head]
    return restore_certificate(cert)[4] == writer


def _unsuperseded(cert_store, kx, ky, head_hex):
    """ADMISSION LAYER 3 (succession — the anamnesis trap turned into evidence): old manifests and
    certificates are retained FOREVER; integrity != truth. A custody head with a known SUCCESSOR
    certificate in the store is superseded — the handoff has moved on — and refuses."""
    for cert in cert_store.values():
        parent, ckx, cky, _src, _dst, _chunk = restore_certificate(cert)
        if (ckx, cky) == (kx, ky) and parent == head_hex:
            return False
    return True


# ---- the handoff -------------------------------------------------------------------------
def apply_migration(sman, man, cert):
    """ADOPTION — the commit point of a handoff: verify the certificate, require the parent CAS
    (the slot's cert digest IS the certificate's parent — reordered, duplicated, and forked
    transfers refuse structurally), the src continuity (the slot's steward IS the certificate's
    src), and THE MIGRATION CAS (the certificate's chunk binding equals the region's LIVE slot — a
    migration authored against a moved authority is refused, never rebased). Mints the new steward
    manifest: exactly one slot moves; the world manifest is untouched BY SIGNATURE (nothing world
    is returned — witness neutrality is structural)."""
    parent, kx, ky, src, dst, chunk = restore_certificate(cert)
    w, h, c, sgrid, mgrid = _grid_tie(sman, man)
    if (kx, ky) not in sgrid:
        raise MigrateError(f"region ({kx},{ky}) is outside the steward grid")
    tag, head = sgrid[(kx, ky)]
    if head != parent:
        raise MigrateError(f"custody CAS: the certificate's parent {parent[:12]}… is not the "
                           f"region's custody head {head[:12]}… — a reordered, duplicated, or "
                           f"forked transfer is refused, never rebased")
    if tag != src:
        raise MigrateError(f"the certificate transfers from {_tag_str(src)!r} but the slot's "
                           f"steward is {_tag_str(tag)!r} — refused")
    if mgrid[(kx, ky)] != chunk:
        raise MigrateError(f"THE MIGRATION CAS: the certificate binds authority state "
                           f"{chunk[:12]}… but the region's live state is "
                           f"{mgrid[(kx, ky)][:12]}… — a migration authored against a moved "
                           f"authority is refused, never rebased")
    new_grid = dict(sgrid)
    new_grid[(kx, ky)] = (dst, address(cert))
    return _mint_steward(w, h, c, new_grid)


def migrate(sman, cert_store, man, kx, ky, src, dst):
    """THE MIGRATION: expire the standing on `src`, mint it on `dst`, and emit the proof. Refuses:
    theft (src is not the steward), a vacuous transfer (src == dst), a forged manifest (the chain
    does not re-derive), a superseded custody head (the store knows a successor), a foreign region,
    a mismatched grid. Returns (new_steward_manifest, certificate) — the certificate is NOT adopted
    into any store here: adoption is the caller's commit, and the handoff prefix law governs every
    intermediate state (minted-only: src writes; torn: nobody; committed: dst)."""
    _w, _h, _c, sgrid, mgrid = _grid_tie(sman, man)
    if (kx, ky) not in sgrid:
        raise MigrateError(f"region ({kx},{ky}) is outside the steward grid")
    tag, head = sgrid[(kx, ky)]
    _check_tag(src, "src"); _check_tag(dst, "dst")
    if tag != src:
        raise MigrateError(f"theft refused: {_tag_str(src)!r} is not the steward of ({kx},{ky}) "
                           f"(the slot names {_tag_str(tag)!r})")
    check_custody(sman, cert_store, kx, ky)
    if not _unsuperseded(cert_store, kx, ky, head):
        raise MigrateError(f"the custody head {head[:12]}… of ({kx},{ky}) is SUPERSEDED — a "
                           f"migration from a stale manifest would fork custody; refused")
    cert = migration_certificate(head, kx, ky, src, dst, mgrid[(kx, ky)])
    return apply_migration(sman, man, cert), cert


def replay_custody(genesis_sman, certs):
    """REPLAY DETERMINISM: the custody head re-derives BIT-FOR-BIT from genesis plus the ordered
    certificates — order is structural via the parent CAS (a reordered, duplicated, or forked
    replay refuses on the chain alone). Chunk currency was checked at each adoption against the
    then-live world and is carried as evidence in each certificate; replay re-derives the CHAIN and
    the head identity (historical worlds are not required — the anamnesis store retains them for
    whoever wants the deeper audit)."""
    w, h, c, sgrid = parse_steward(genesis_sman)
    grid = dict(sgrid)
    for cert in certs:
        parent, kx, ky, src, dst, _chunk = restore_certificate(cert)
        if (kx, ky) not in grid:
            raise MigrateError(f"replayed region ({kx},{ky}) is outside the steward grid")
        tag, head = grid[(kx, ky)]
        if head != parent:
            raise MigrateError(f"replay CAS: certificate parent {parent[:12]}… is not the custody "
                               f"head {head[:12]}… — a reordered, duplicated, or forked transfer "
                               f"is refused")
        if tag != src:
            raise MigrateError(f"replay continuity: {_tag_str(src)!r} is not the steward "
                               f"({_tag_str(tag)!r} is)")
        grid[(kx, ky)] = (dst, address(cert))
    return _mint_steward(w, h, c, grid)


# ---- the admission (the conjunctive predicate) -------------------------------------------
def admit(sman, cert_store, man, store, writer, ls, rec):
    """THE STEWARDED ADMISSION: a write lands iff the writer HOLDS the region (layers 1–3: slot,
    chain, succession) AND the edit is lease-lawful (layer 4: `lease.admit`, every lease law
    inherited unchanged). The lease alone is BLIND to migration — a lease is minted from state and
    migration moves none — so the conjunction is necessary, not decorative (the born-red fact the
    falsifiers keep). Returns (new_manifest, new_chunk)."""
    try:
        _chunk_hex, kx, ky = _LS.restore_lease(ls)
    except _LS.LeaseError as exc:
        raise MigrateError(f"the lease refused: {exc}")
    _check_tag(writer, "writer")
    _grid_tie(sman, man)
    if not _steward_ok(sman, kx, ky, writer):
        tag, _head = current_steward(sman, kx, ky)
        raise MigrateError(f"{_tag_str(writer)!r} is not the steward of ({kx},{ky}) — the slot "
                           f"names {_tag_str(tag)!r}; a write without standing is refused, however "
                           f"valid its lease (the lease cannot see a handoff)")
    if not _custody_ok(sman, cert_store, kx, ky, writer):
        raise MigrateError(f"the custody chain of ({kx},{ky}) does not end at "
                           f"{_tag_str(writer)!r} — the certificate layer refuses what the slot "
                           f"let pass")
    _tag, head = current_steward(sman, kx, ky)
    if not _unsuperseded(cert_store, kx, ky, head):
        raise MigrateError(f"the presented custody head {head[:12]}… of ({kx},{ky}) is "
                           f"SUPERSEDED — a successor certificate exists; a stale steward "
                           f"manifest is refused, never a double-writer")
    try:
        return _LS.admit(man, store, ls, rec)
    except _LS.LeaseError as exc:
        raise MigrateError(f"the leased admission refused: {exc}")


def migration_cost_bytes(w, h, csize):
    """The handoff's durable increment: one certificate + one steward manifest — custody is priced
    like everything else in the arc."""
    return CERT_BYTES + steward_manifest_bytes(w, h, csize)


def migrate_digest(name, parent_hex, head_hex, nmigs, nbytes, verdict):
    """URDRMIG1 canon — SHA-256(MAGIC | name | parent | head | migrations | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|h:{head_hex}|m:{nmigs}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- forgery constructor (exposed for the falsifiers, the `_seal` precedent) -------------
def _forge_slot_tag(sman, kx, ky, tag):
    """Re-mint a steward manifest with ONE slot's tag replaced (its cert digest kept) — the
    administrative forgery the derived-data check must catch. A falsifier tool, never a law."""
    w, h, c, grid = parse_steward(sman)
    grid = dict(grid)
    grid[(kx, ky)] = (tag, grid[(kx, ky)][1])
    return _mint_steward(w, h, c, grid)


# ---- the world helpers -------------------------------------------------------------------
_C = 8


def _world(side=32):
    fld = _NW.flat_world(side)
    man = _CK.field_manifest(fld, _C)
    store = {_CK.address(r): r for r in _CK.cut(fld, _C).values()}
    return fld, man, store


def _lease_and_rec(man, store, x, y, dh):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    key = (x // _C, y // _C)
    chunk = store[grid[key]]
    _kx, _ky, cells = _CK.restore_chunk(chunk)
    old = cells[y - key[1] * _C][x - key[0] * _C]
    return (_LS.lease_from_chunk(chunk),
            _RN.regional_record(_CK.address(chunk), key[0], key[1], x, y, old, old + dh))


def _all_regions(man, tag):
    _w, _h, _c, grid = _CK.parse_manifest(man)
    return {k: tag for k in grid}


def _refuses(fn, *args):
    try:
        fn(*args)
        return False
    except MigrateError:
        return True


# ---- scenarios (pinned by the gate) ------------------------------------------------------
def _scene_handoff():
    """The lawful handoff: A→B over region (0,1) — the world witness untouched (in bytes), exactly
    one custody slot moved, the chain re-derives, B's write lands and EQUALS the migration-blind
    monolithic oracle, A's write refuses."""
    fld, man, store = _world()
    a, b = steward_tag("alfa"), steward_tag("bravo")
    parent = _CK.address(man)
    sman0 = steward_genesis(man, _all_regions(man, a))
    certs = {}
    sman1, cert = migrate(sman0, certs, man, 0, 1, a, b)
    certs[address(cert)] = cert
    neutral = _CK.address(man) == parent
    g0, g1 = parse_steward(sman0)[3], parse_steward(sman1)[3]
    local = [k for k in g0 if g0[k] != g1[k]] == [(0, 1)]
    ls, rec = _lease_and_rec(man, store, 5, 8, 1000)
    usurped = _refuses(admit, sman1, certs, man, dict(store), a, ls, rec)
    new_man, ch = admit(sman1, certs, man, store, b, ls, rec)
    store[_CK.address(ch)] = ch
    lifted = _TF.edit_record(_TF.parent_address(fld, _C), 5, 8, fld[8][5], fld[8][5] + 1000)
    oracle = _TF.parent_address(_TF.apply_edit(fld, _C, lifted), _C)
    ok = (neutral and local and usurped and check_custody(sman1, certs, 0, 1) == 1
          and _CK.address(new_man) == oracle)
    return parent, _CK.address(new_man), 1, migration_cost_bytes(32, 32, _C), \
        ("ADMIT" if ok else "MIGRATE-REFUSE")


def _scene_relay():
    """The custody chain: A→B→C over one region — replay re-derives the head BIT-FOR-BIT; a
    reordered and a duplicated replay refuse on the parent CAS alone (structural order, no
    sequence numbers)."""
    fld, man, store = _world()
    a, b, c = steward_tag("alfa"), steward_tag("bravo"), steward_tag("charl")
    parent = _CK.address(man)
    sman0 = steward_genesis(man, _all_regions(man, a))
    certs = {}
    sman1, c1 = migrate(sman0, certs, man, 0, 1, a, b)
    certs[address(c1)] = c1
    sman2, c2 = migrate(sman1, certs, man, 0, 1, b, c)
    certs[address(c2)] = c2
    replayed = bytes(replay_custody(sman0, (c1, c2))) == bytes(sman2)
    reordered = _refuses(replay_custody, sman0, (c2, c1))
    duplicated = _refuses(replay_custody, sman0, (c1, c1))
    ok = replayed and reordered and duplicated and check_custody(sman2, certs, 0, 1) == 2
    return parent, _CK.address(man), 2, 2 * CERT_BYTES, ("ADMIT" if ok else "MIGRATE-REFUSE")


def _scene_diamond():
    """THE MIGRATION DIAMOND: a write certified disjoint from the migrating region commutes with
    the migration in BOTH spaces — one world head, one custody head — and the certificate bytes
    are IDENTICAL across orders (the dependency theorem, structural). The overlapping half refuses
    lawfully in both interleavings and serializes."""
    fld, man, store = _world()
    a, b, c = steward_tag("alfa"), steward_tag("bravo"), steward_tag("charl")
    parent = _CK.address(man)
    sman0 = steward_genesis(man, _all_regions(man, a))
    certs = {}
    sman1, cprev = migrate(sman0, certs, man, 0, 1, a, b)
    certs[address(cprev)] = cprev
    ls, rec = _lease_and_rec(man, store, 18, 18, 500)           # region (2,2): disjoint from (0,1)
    disjoint = _RN.authority(fld, _C, rec) & frozenset({(0, 1)}) == frozenset()
    man_w, _ch = _LS.admit(man, dict(store), ls, rec)           # order 1: W then M
    sman_wm, cert_wm = migrate(sman1, dict(certs), man_w, 0, 1, b, c)
    sman_mw, cert_mw = migrate(sman1, dict(certs), man, 0, 1, b, c)  # order 2: M then W
    man_mw, _c2 = _LS.admit(man, dict(store), ls, rec)
    diamond = (_CK.address(man_w) == _CK.address(man_mw)
               and bytes(cert_wm) == bytes(cert_mw)
               and address(sman_wm) == address(sman_mw))
    # the overlapping half: W' on (0,1) itself
    lso, reco = _lease_and_rec(man, store, 5, 8, 300)
    certs1 = dict(certs)
    sman_x, stale = migrate(sman1, certs1, man, 0, 1, b, c)
    man_o, cho = _LS.admit(man, dict(store), lso, reco)
    stale_refused = _refuses(apply_migration, sman1, man_o, stale)
    certs1[address(stale)] = stale
    st2 = dict(store); st2[_CK.address(cho)] = cho
    ls2, rec2 = _lease_and_rec(man_o, st2, 6, 8, 1)
    old_refused = _refuses(admit, sman_x, certs1, man_o, dict(st2), b, ls2, rec2)
    serial, _c3 = admit(sman_x, certs1, man_o, st2, c, ls2, rec2)
    ok = disjoint and diamond and stale_refused and old_refused
    return parent, _CK.address(man_w), 2, CERT_BYTES, ("ADMIT" if ok else "MIGRATE-REFUSE")


def _scene_usurper():
    """The verdict IS the refusal: the lease-blindness trap DEMONSTRATED (the usurper's lease is
    byte-identical and `lease.admit` alone admits it), then the layered custody refusals — the
    usurper, the stale manifest (succession), the torn handoff (nobody writes) — with the lawful
    committed write landing."""
    fld, man, store = _world()
    a, b, c = steward_tag("alfa"), steward_tag("bravo"), steward_tag("charl")
    parent = _CK.address(man)
    sman0 = steward_genesis(man, _all_regions(man, a))
    certs = {}
    sman1, cert = migrate(sman0, certs, man, 0, 1, a, b)
    certs[address(cert)] = cert
    ls, rec = _lease_and_rec(man, store, 5, 8, 1000)
    _w, _h, _c4, grid = _CK.parse_manifest(man)
    blind = (bytes(ls) == bytes(_LS.lease_from_chunk(store[grid[(0, 1)]]))
             and _LS.admit(man, dict(store), ls, rec) is not None)   # the lease law ALONE admits
    usurper = _refuses(admit, sman1, certs, man, dict(store), a, ls, rec)
    stale_man = _refuses(admit, sman0, certs, man, dict(store), a, ls, rec)
    sman2, cert2 = migrate(sman1, certs, man, 0, 1, b, c)       # minted, NOT adopted
    minted_src = admit(sman1, certs, man, dict(store), b, ls, rec) is not None
    minted_dst = _refuses(admit, sman1, certs, man, dict(store), c, ls, rec)
    certs[address(cert2)] = cert2                               # TORN: cert adopted, manifest stale
    torn_src = _refuses(admit, sman1, certs, man, dict(store), b, ls, rec)
    torn_dst = _refuses(admit, sman1, certs, man, dict(store), c, ls, rec)
    committed = admit(sman2, certs, man, dict(store), c, ls, rec) is not None
    ok = (blind and usurper and stale_man and minted_src and minted_dst
          and torn_src and torn_dst and committed)
    return parent, _CK.address(man), 2, 0, ("MIGRATE-REFUSE" if ok else "ADMIT")


_SCENES = {"handoff": _scene_handoff, "relay": _scene_relay,
           "diamond": _scene_diamond, "usurper": _scene_usurper}
SCENES = ("handoff", "relay", "diamond", "usurper")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, head, nmigs, nbytes, verdict = scene_case(name)
    return migrate_digest(name, p, head, nmigs, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_migrate.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MigrateError(f"no golden named {name!r}")


# ---- the seeded property sweep (Tier 2, generalized to migration schedules) --------------
class _LCG:
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


SWEEP_SEED = 20260721
SWEEP_COUNT = 120


def _scenario_rng(seed, s):
    """Per-scenario seeding (Knuth multiplicative spread) so any single scenario REGENERATES
    independently — the property that makes counterexample SHRINKING possible."""
    return _LCG((seed ^ (s * 2654435761)) & 0x7FFFFFFF)


def gen_scenario(r, deep):
    """PURE GENERATION (no execution, no world): a random field, a random total steward layout
    (2..4 stewards over the 16 regions), and a concrete schedule of write/migrate steps (≥1 of
    each forced; `deep` re-migrates the first migrated region — chain depth ≥ 2). The schedule is
    DATA, so a counterexample shrinks by dropping steps."""
    field = tuple(tuple(r.rng(0, 20) for _ in range(32)) for _ in range(32))
    pool = tuple(steward_tag(f"st{i}") for i in range(r.rng(2, 4)))
    assign = {(kx, ky): pool[r.rng(0, len(pool) - 1)] for ky in range(4) for kx in range(4)}
    cust = dict(assign)
    steps = []

    def _mig_step(region):
        others = [t for t in pool if t != cust[region]]
        dst = others[r.rng(0, len(others) - 1)]
        steps.append(("migrate", region, dst))
        cust[region] = dst

    for _i in range(r.rng(3, 6)):
        if r.rng(0, 9) < 6:
            steps.append(("write", (r.rng(0, 3), r.rng(0, 3)),
                          r.rng(0, _C - 1), r.rng(0, _C - 1), r.rng(1, 40)))
        else:
            _mig_step((r.rng(0, 3), r.rng(0, 3)))
    if not any(st[0] == "write" for st in steps):
        steps.append(("write", (r.rng(0, 3), r.rng(0, 3)),
                      r.rng(0, _C - 1), r.rng(0, _C - 1), r.rng(1, 40)))
    if not any(st[0] == "migrate" for st in steps):
        _mig_step((r.rng(0, 3), r.rng(0, 3)))
    if deep:
        first = next(st[1] for st in steps if st[0] == "migrate")
        _mig_step(first)
    return field, pool, assign, tuple(steps)


def run_scenario(field, pool, assign, steps, label="scenario"):
    """EXECUTE one schedule lawfully, then face the adversaries. Asserts, RAISING MigrateError on
    any violation: (a) the final world head equals the MIGRATION-BLIND monolithic oracle (terraform
    lift of the writes alone — the neutral ruler cannot see custody, so a migration that leaked
    into the witness diverges); (b) a non-steward's fully-lease-lawful write REFUSES (the
    double-writer); (c) a spent lease REFUSES on reuse (self-expiry inherited); (d) a duplicated
    transfer REFUSES (parent CAS); (e) a forked transfer minted from a pre-migration snapshot
    REFUSES on the current head. Returns the scenario report dict."""
    man = _CK.field_manifest(field, _C)
    store = {_CK.address(rr): rr for rr in _CK.cut(field, _C).values()}
    sman = steward_genesis(man, assign)
    certs = {}
    writes = []
    spent = None
    snapshot = None
    first_cert = None
    first_migrated = None
    depths = {}
    for st in steps:
        if st[0] == "write":
            _kind, (kx, ky), lx, ly, dh = st
            x, y = kx * _C + lx, ky * _C + ly
            tag = current_steward(sman, kx, ky)[0]
            ls, rec = _lease_and_rec(man, store, x, y, dh)
            old = _RN.restore_regional(rec)[5]
            new_man, ch = admit(sman, certs, man, store, tag, ls, rec)
            store[_CK.address(ch)] = ch
            if spent is None:
                spent = (ls, rec, (kx, ky))
            man = new_man
            writes.append((x, y, old, old + dh))
        else:
            _kind, (kx, ky), dst = st
            src = current_steward(sman, kx, ky)[0]
            if snapshot is None:
                snapshot = (sman, dict(certs), man, (kx, ky), src)
            sman2, cert = migrate(sman, certs, man, kx, ky, src, dst)
            certs[address(cert)] = cert
            sman = sman2
            if first_cert is None:
                first_cert = cert
                first_migrated = ((kx, ky), src)
            depths[(kx, ky)] = depths.get((kx, ky), 0) + 1
    # (a) the migration-blind oracle
    cur = field
    for (x, y, old, new) in writes:
        lifted = _TF.edit_record(_TF.parent_address(cur, _C), x, y, old, new)
        cur = _TF.apply_edit(cur, _C, lifted)
    if _TF.parent_address(cur, _C) != _CK.address(man):
        raise MigrateError(f"{label}: the stewarded world head diverged from the migration-blind "
                           f"monolithic oracle — migration leaked into the witness or a write was "
                           f"lost")
    # (b) the double-writer: a non-steward with a fully-lease-lawful write
    (mkx, mky), old_st = first_migrated
    outsider = old_st if current_steward(sman, mkx, mky)[0] != old_st else \
        next(t for t in pool + (steward_tag("zz"),) if t != current_steward(sman, mkx, mky)[0])
    ls, rec = _lease_and_rec(man, store, mkx * _C + 3, mky * _C + 3, 5)
    try:
        admit(sman, certs, man, dict(store), outsider, ls, rec)
        raise MigrateError(f"{label}: a non-steward write was ADMITTED, not refused — the "
                           f"double-writer landed")
    except MigrateError as exc:
        if "was ADMITTED" in str(exc):
            raise
    # (c) the spent lease
    sls, srec, (skx, sky) = spent
    steward_now = current_steward(sman, skx, sky)[0]
    try:
        admit(sman, certs, man, dict(store), steward_now, sls, srec)
        raise MigrateError(f"{label}: a SPENT lease was ADMITTED on reuse, not refused")
    except MigrateError as exc:
        if "was ADMITTED" in str(exc):
            raise
    # (d) the duplicated transfer
    try:
        apply_migration(sman, man, first_cert)
        raise MigrateError(f"{label}: a DUPLICATED transfer was ADMITTED, not refused")
    except MigrateError as exc:
        if "was ADMITTED" in str(exc):
            raise
    # (e) the forked transfer, minted from the pre-migration snapshot
    snap_sman, snap_certs, snap_man, (fkx, fky), fsrc = snapshot
    fdst = next(t for t in pool + (steward_tag("zz"),) if t != fsrc)
    _s, fork = migrate(snap_sman, snap_certs, snap_man, fkx, fky, fsrc, fdst)
    try:
        apply_migration(sman, man, fork)
        raise MigrateError(f"{label}: a FORKED transfer was ADMITTED, not refused")
    except MigrateError as exc:
        if "was ADMITTED" in str(exc):
            raise
    return {"head": _CK.address(man), "custody": address(sman), "nsteps": len(steps),
            "nwrites": len(writes), "changed": bool(writes),
            "max_depth": max(depths.values()) if depths else 0}


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` scenarios of randomized layouts, migration schedules,
    concurrent lawful writes, and the five adversaries — RAISES on the first violation or on
    NON-VACUITY (every adversary category must refuse every time, schedule lengths must vary, some
    region must re-migrate, the world must change); returns the aggregate dict + digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    lengths = {}
    deep_chains = changed = 0
    for s in range(count):
        r = _scenario_rng(seed, s)
        field, pool, assign, steps = gen_scenario(r, deep=(s % 3 == 0))
        rep = run_scenario(field, pool, assign, steps, label=f"scenario {s} (seed {seed})")
        lengths[rep["nsteps"]] = lengths.get(rep["nsteps"], 0) + 1
        deep_chains += rep["max_depth"] >= 2
        changed += rep["changed"]
        hh.update(f"|{s}:{rep['head']}:{rep['custody']}:{rep['nsteps']}".encode())
    if len(lengths) < 3:
        raise MigrateError(f"NON-VACUITY: only {len(lengths)} distinct schedule lengths — {lengths}")
    if deep_chains == 0:
        raise MigrateError("NON-VACUITY: no scenario re-migrated a region (chain depth < 2 "
                           "everywhere)")
    if changed == 0:
        raise MigrateError("NON-VACUITY: no scenario changed the world")
    return {"scenarios": count, "lengths": lengths, "deep_chains": deep_chains,
            "changed": changed, "double_refused": count, "stale_refused": count,
            "dup_refused": count, "fork_refused": count, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_migrate.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise MigrateError("no golden named 'sweep'")


# ---- the OFF-GATE reseeded explorer + the shrinker (declared; NOT gate-run) --------------
def shrink(field, pool, assign, steps):
    """Greedy schedule shrinking: drop any step whose removal keeps the scenario FAILING, to a
    fixpoint — the minimal counterexample, ready to file as a pinned corpus scene (the
    off-gate → pinned discipline). Returns the minimal step tuple."""
    def fails(ss):
        try:
            run_scenario(field, pool, assign, ss, label="shrink")
            return False
        except MigrateError:
            return True
    if not fails(steps):
        raise MigrateError("shrink was handed a scenario that does not fail")
    cur = tuple(steps)
    done = False
    while not done:
        done = True
        for i in range(len(cur)):
            cand = cur[:i] + cur[i + 1:]
            if cand and fails(cand):
                cur = cand
                done = False
                break
    return cur


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    """Reseed the sweep across `n_seeds` seeds; for each failure, isolate the scenario and SHRINK
    its schedule to the minimal failing form. The law is expected to hold, so the list is normally
    empty — the value is the machinery. OFF-GATE: reseeded, not byte-identical, never gate-run."""
    found = []
    for k in range(n_seeds):
        seed = (base_seed + k * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except MigrateError as exc:
            minimal = None
            for s in range(count):
                r = _scenario_rng(seed, s)
                field, pool, assign, steps = gen_scenario(r, deep=(s % 3 == 0))
                try:
                    run_scenario(field, pool, assign, steps, label=f"scenario {s}")
                except MigrateError:
                    minimal = (s, shrink(field, pool, assign, steps))
                    break
            found.append((seed, str(exc), minimal))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 200
        found = explore(base, n)
        if not found:
            print(f"EXPLORE: no counterexample across {n} reseeded sweeps from base {base} — "
                  f"the migration laws held on every one.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg, minimal in found:
                print(f"  seed={seed}: {msg}\n    minimal={minimal}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} scenarios, lengths {dict(sorted(rep['lengths'].items()))}, "
          f"deep_chains {rep['deep_chains']}, changed {rep['changed']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
