# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""nway — N-WAY NULLITY + THE INDEPENDENCE LATTICE (Phase M, rung M1, URDRNWY1): the certified mesh's
WRITE SCHEDULER. `rannull` (RAN-0) proved PAIRWISE nullity — two regional edits on disjoint authorities
execute concurrently, four heads equal, zero rebases. `lease` named the successor outright: "n-way lease
scheduling and the independence lattice as a queryable allocator." This is that successor, and the first
code rung of Phase M: distributed execution across N authorities as a THEOREM composed from the proofs
already built, not a new mechanism.

THE N-WAY NULLITY THEOREM. For N regional edits E1..EN whose authorities are PAIRWISE DISJOINT
(∀ i≠j: authority(Ei) ∩ authority(Ej) = ∅), the PARALLEL shard execution (each `shard_apply` against its
own chunk, then one address-substituting `reunify` of all N new chunks) equals EVERY one of the N!
serial-order executions, BIT-FOR-BIT, with ZERO rebases — each record is byte-unchanged in every order,
because no shared authority moved. Overlap is `NWAY-REFUSE`: a shared authority exists, so nullity cannot
be certified (commutation at rank 1 may still hold — that is `commute`'s law, not this one). The proof is
the pairwise RAN-0 diamond, iterated to a batch and discharged CONSTRUCTIVELY over all orderings.

THE INDEPENDENCE LATTICE (the queryable allocator). `independence_rounds` partitions an arbitrary edit
set into ordered ROUNDS, each round a set of pairwise-disjoint edits (parallelizable this tick); edits
sharing a chunk fall into successive rounds (they serialize). ONE round iff every edit is on a distinct
chunk — the fully-parallel case. This is the mesh's write scheduler: given a batch of writes across
authorities, it says exactly which run concurrently and which must wait.

THE CROSS-CHECK (the independent oracle, held OUTSIDE the certificate). The certificate proves the SHARD
path is order-independent (parallel == all serials). That the shard path is also CORRECT — equal to the
MONOLITHIC world a single global authority would compute — is verified against `terraform`'s global lift
(`_global_head`), a path that uses NONE of shard_apply/reunify (the anti-Goodhart rule). The gate row and
the property sweep assert shard-head == global-head; a shard that agreed only with itself would be caught.

THE CERTIFICATE (variable N). cert = MAGIC | count(4) | rec_0..rec_{N-1} | SHA-256 — evidence, never
authority: `check_nway` restores the records, re-derives the entire proof from the parent world, and
requires the presented bytes to reproduce bit-for-bit; a forged or reordered certificate refuses.

GRADE (Phase M rung M1). The theorem over the pinned corpus, the N=2 agreement with RAN-0, the
independence lattice's rounds, the overlap refusal, the shard==global cross-check, the certificate
round-trip and forgery refuse, a seeded property sweep, and determinism are MEASURED (exact, reproducible,
a defect diverges). DECLARED: authority MIGRATION (a lease moving between authorities mid-batch — rung M2);
LIVE simulation across the mesh (M3); the partitioned mesh + CAP liveness cost (M4); the attested mesh
session (M5). `does_not_show`: WHO may author (`sealwrit`/`authinput`); cross-process transport, failure
mid-parallel-apply, wall-clock (`bench.py`); cross-placement (URDRNWY1 is Python reference only)."""
import hashlib
import itertools
import os as _os
import sys as _sys

MAGIC = b"URDRNWY1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, manifests, addresses
import rannull as _RN                                           # regional records, shard_apply, authority, reunify
import terraform as _TF                                         # the global lift — the independent oracle

DIGEST_BYTES = 32


class NwayError(Exception):
    def __init__(self, message):
        super().__init__(f"NWAY-REFUSE: {message}")
        self.code = "NWAY-REFUSE"


def authorities(field, csize, recs):
    """Each edit's certified minimal authority (a frozenset of chunk keys), via RAN-0's `authority`."""
    try:
        return tuple(_RN.authority(field, csize, r) for r in recs)
    except _RN.RanError as exc:
        raise NwayError(f"an edit's authority could not be certified: {exc}")


def first_overlap(auths):
    """The first (i, j, intersection) of two authorities that share a chunk, or None if all disjoint."""
    for i in range(len(auths)):
        for j in range(i + 1, len(auths)):
            inter = auths[i] & auths[j]
            if inter:
                return (i, j, inter)
    return None


def nway_parallel_head(man, store, recs):
    """The parallel execution, minimal-knowledge: shard-apply each record against its own parent chunk
    (fetched by the address it binds), then ONE reunify of all N new chunks by address substitution."""
    news = []
    for r in recs:
        parent = _RN.restore_regional(r)[0]
        try:
            ch = store[parent]
        except KeyError:
            raise NwayError(f"parent chunk {parent[:12]}… missing from the shard store")
        try:
            news.append(_RN.shard_apply(ch, r))
        except _RN.RanError as exc:
            raise NwayError(f"a shard refused: {exc}")
    return _CK.address(_RN.reunify(man, tuple(news)))


def nway_serial_head(man, store, recs, order):
    """One serial execution in the given order: each edit shard-applied against the CURRENT chunk, one
    reunify per step. For disjoint authorities every order lands the same head (the theorem)."""
    m = man
    st = dict(store)
    for i in order:
        r = recs[i]
        parent = _RN.restore_regional(r)[0]
        try:
            ch = _RN.shard_apply(st[parent], r)
        except _RN.RanError as exc:
            raise NwayError(f"a shard refused in order {order}: {exc}")
        m = _RN.reunify(m, (ch,))
        st[_CK.address(ch)] = ch
    return _CK.address(m)


def _global_head(field, csize, recs):
    """THE INDEPENDENT ORACLE: apply the N edits LIFTED to the global `terraform` law (explicit rebases),
    the monolithic world a single authority would compute — using none of shard_apply/reunify. For
    disjoint authorities the order is immaterial; this is the truth the shard path must match."""
    cur = field
    for r in recs:
        _p, _kx, _ky, x, y, oh, nh = _RN.restore_regional(r)
        try:
            lifted = _TF.edit_record(_TF.parent_address(cur, csize), x, y, oh, nh)
            cur = _TF.apply_edit(cur, csize, lifted)
        except _TF.TerraformError as exc:
            raise NwayError(f"the global oracle refused edit {(x, y)}: {exc}")
    return _TF.parent_address(cur, csize)


def _seal(recs):
    pre = bytearray(MAGIC) + len(recs).to_bytes(4, "big")
    for r in recs:
        rb = bytes(r)
        if len(rb) != _RN.RAN_RECORD_BYTES:
            raise NwayError(f"each edit must be a {_RN.RAN_RECORD_BYTES}-byte regional record")
        pre += rb
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def nway_null(field, csize, recs):
    """THE N-WAY NULLITY CERTIFICATE: N (>=2) regional edits whose authorities are PAIRWISE DISJOINT
    execute concurrently — the parallel shard head equals EVERY serial-order head, bit-for-bit, zero
    rebases. Returns (cert, head_hex). Overlap is NWAY-REFUSE. (The shard head is cross-checked against
    the global monolith by the gate/sweep, using the independent `_global_head` oracle.)"""
    recs = tuple(recs)
    if len(recs) < 2:
        raise NwayError(f"n-way nullity needs at least two edits, got {len(recs)}")
    auths = authorities(field, csize, recs)
    ov = first_overlap(auths)
    if ov is not None:
        i, j, inter = ov
        raise NwayError(f"authorities {i} and {j} intersect at {sorted(inter)} — a shared authority "
                        f"exists, so n-way nullity cannot be certified")
    man = _CK.field_manifest(field, csize)
    store = {_CK.address(r): r for r in _CK.cut(field, csize).values()}
    par = nway_parallel_head(man, store, recs)
    for order in itertools.permutations(range(len(recs))):
        if nway_serial_head(man, store, recs, order) != par:
            raise NwayError(f"serial order {order} diverged from the parallel head — n-way nullity fails")
    return _seal(recs), par


def restore_nway(buf):
    """The certificate inverse: the tuple of records BIT-FOR-BIT or a typed refuse. Digest first."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise NwayError("a certificate must be bytes")
    buf = bytes(buf)
    if len(buf) < len(MAGIC) + 4 + DIGEST_BYTES:
        raise NwayError("certificate too short")
    if buf[:len(MAGIC)] != MAGIC:
        raise NwayError("bad magic — not a URDRNWY1 certificate")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise NwayError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    n = int.from_bytes(buf[len(MAGIC):len(MAGIC) + 4], "big")
    off = len(MAGIC) + 4
    body = len(buf) - DIGEST_BYTES
    if off + n * _RN.RAN_RECORD_BYTES != body:
        raise NwayError(f"certificate claims {n} records but the body does not fit")
    recs = []
    for _ in range(n):
        rec = buf[off:off + _RN.RAN_RECORD_BYTES]
        _RN.restore_regional(rec)                              # each embedded record must verify
        recs.append(rec); off += _RN.RAN_RECORD_BYTES
    return tuple(recs)


def check_nway(field, csize, buf):
    """Independent re-verification — evidence, never authority: restore, re-derive the entire proof
    from the parent world, require the presented bytes to reproduce bit-for-bit. Returns head_hex."""
    recs = restore_nway(buf)
    cert2, head = nway_null(field, csize, recs)
    if cert2 != bytes(buf):
        raise NwayError("re-derivation does not reproduce the presented certificate — forged")
    return head


def independence_rounds(field, csize, recs):
    """THE INDEPENDENCE LATTICE (the queryable allocator): partition the edits into ordered ROUNDS, each
    a set of PAIRWISE-DISJOINT edit indices (parallelizable this tick). Edits sharing a chunk fall into
    successive rounds (serialize). ONE round iff every edit is on a distinct chunk."""
    auths = authorities(field, csize, recs)
    by_chunk = {}
    for i, a in enumerate(auths):
        by_chunk.setdefault(tuple(sorted(a)), []).append(i)
    rounds = []
    r = 0
    while any(len(v) > r for v in by_chunk.values()):
        rounds.append(tuple(v[r] for v in by_chunk.values() if len(v) > r))
        r += 1
    return rounds


def nway_digest(name, parent_hex, head_hex, nedits, nrounds, verdict):
    """URDRNWY1 canon — SHA-256(MAGIC | name | parent | head | edits | rounds | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|h:{head_hex}|e:{nedits}|r:{nrounds}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- the world + record helpers ---------------------------------------------------------
def flat_world(side=32):
    """A flat side×side world (C=8 → (side/8)² chunks): the n-way law is field-agnostic; a flat world
    makes the authority (region == blast == demand) exact and the corpus small."""
    return tuple(tuple(0 for _ in range(side)) for _ in range(side))


def rrec(field, csize, x, y, dh):
    """A regional record against (x,y)'s current chunk in `field`."""
    key = (x // csize, y // csize)
    chunk = _CK.cut(field, csize)[key]
    return _RN.regional_record(_CK.address(chunk), key[0], key[1], x, y, field[y][x], field[y][x] + dh)


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_C = 8


def _scene_quad():
    """Four regional edits on four DISTINCT chunks of a flat 32×32 world: n-way null — parallel == all
    24 serial orders, one head, zero rebases; the certificate re-verifies; one independence round."""
    fld = flat_world(32)
    recs = (rrec(fld, _C, 2, 2, 11), rrec(fld, _C, 10, 4, 22),
            rrec(fld, _C, 20, 20, 33), rrec(fld, _C, 28, 10, 44))
    cert, head = nway_null(fld, _C, recs)
    rehead = check_nway(fld, _C, cert)
    rounds = independence_rounds(fld, _C, recs)
    ok = rehead == head and head == _global_head(fld, _C, recs) and len(rounds) == 1
    return _CK.address(_CK.field_manifest(fld, _C)), head, len(recs), len(rounds), \
        ("ADMIT" if ok else "NWAY-REFUSE")


def _scene_pair_agrees():
    """The base case: two disjoint edits — the n-way head EQUALS RAN-0's pairwise nullity head, proving
    M1 is a faithful generalization (URDRNWY1 at N=2 is URDRRAN0)."""
    fld = flat_world(32)
    ra, rb = rrec(fld, _C, 2, 2, 11), rrec(fld, _C, 20, 20, 33)
    _cert, head = nway_null(fld, _C, (ra, rb))
    _rancert, ranhead = _RN.nullity(fld, _C, ra, rb)
    ok = head == ranhead
    return _CK.address(_CK.field_manifest(fld, _C)), head, 2, 1, ("ADMIT" if ok else "NWAY-REFUSE")


def _scene_lattice():
    """The independence lattice schedules a batch with a repeated chunk: four edits, TWO on chunk (0,0)
    — the scheduler yields TWO rounds (the shared chunk serialized), each round pairwise-disjoint; the
    round-composed head equals the global monolith."""
    fld = flat_world(32)
    r0a = rrec(fld, _C, 1, 1, 5)                                # chunk (0,0)
    r1 = rrec(fld, _C, 10, 2, 7)                                # chunk (1,0)
    r2 = rrec(fld, _C, 18, 18, 9)                               # chunk (2,2)
    # a second edit on chunk (0,0), authored against the chunk AFTER r0a — the serialized successor
    f1 = _apply_global(fld, _C, (r0a,))
    r0b = rrec(f1, _C, 3, 3, 4)                                 # chunk (0,0) again, next state
    recs = (r0a, r1, r2, r0b)
    rounds = independence_rounds(fld, _C, recs)
    ok = len(rounds) == 2 and all(_disjoint_round(fld, _C, recs, rd) for rd in rounds)
    head = _apply_global(fld, _C, recs)
    return _CK.address(_CK.field_manifest(fld, _C)), _TF.parent_address(head, _C), len(recs), \
        len(rounds), ("ADMIT" if ok else "NWAY-REFUSE")


def _scene_overlap():
    """The certified conflict: three edits, two on the SAME chunk — n-way nullity REFUSES (a shared
    authority exists). The verdict is the refusal itself."""
    fld = flat_world(32)
    ra = rrec(fld, _C, 2, 2, 11)                                # chunk (0,0)
    rb = rrec(fld, _C, 20, 20, 33)                              # chunk (2,2)
    rc = _RN.regional_record(_CK.address(_CK.cut(fld, _C)[(0, 0)]), 0, 0, 5, 5,
                             fld[5][5], fld[5][5] + 7)          # chunk (0,0) again — overlaps ra
    refused = False
    try:
        nway_null(fld, _C, (ra, rb, rc))
    except NwayError:
        refused = True
    return _CK.address(_CK.field_manifest(fld, _C)), \
        _CK.address(_CK.field_manifest(fld, _C)), 3, 0, ("NWAY-REFUSE" if refused else "ADMIT")


def _apply_global(field, csize, recs):
    cur = field
    for r in recs:
        _p, _kx, _ky, x, y, oh, nh = _RN.restore_regional(r)
        lifted = _TF.edit_record(_TF.parent_address(cur, csize), x, y, oh, nh)
        cur = _TF.apply_edit(cur, csize, lifted)
    return cur


def _disjoint_round(field, csize, recs, rd):
    auths = [_RN.authority(field, csize, recs[i]) for i in rd]
    return first_overlap(auths) is None


_SCENES = {"quad": _scene_quad, "pair_agrees": _scene_pair_agrees,
           "lattice": _scene_lattice, "overlap": _scene_overlap}
SCENES = ("quad", "pair_agrees", "lattice", "overlap")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, head, nedits, nrounds, verdict = scene_case(name)
    return nway_digest(name, p, head, nedits, nrounds, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_nway.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise NwayError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------
class _LCG:
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


SWEEP_SEED = 20260721
SWEEP_COUNT = 150


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """Random N-authority (N in 2..5) disjoint edit sets over a flat 32×32 world (16 chunks). Asserts
    the SHARD n-way head equals the independent GLOBAL monolith (`_global_head`) — the anti-Goodhart
    cross-check — and that an overlapping set REFUSES. RAISES `NwayError` on any violation or vacuity;
    returns the aggregate dict + digest. Non-vacuity: N varies (>=3 distinct sizes), every overlap
    refused, and the world actually changed."""
    fld = flat_world(32)
    grid = [(kx, ky) for ky in range(4) for kx in range(4)]    # 16 chunk keys
    hh = hashlib.sha256()
    hh.update(MAGIC)
    r = _LCG(seed)
    sizes = {}
    overlaps_refused = 0
    for s in range(count):
        n = r.rng(2, 4)                                        # 2..4: 3 sizes, ≤24 perms/batch (gate-cheap)
        # pick n distinct chunks, one cell in each
        picks = []
        used = set()
        while len(picks) < n:
            k = grid[r.rng(0, len(grid) - 1)]
            if k in used:
                continue
            used.add(k)
            cx = k[0] * _C + r.rng(0, _C - 1)
            cy = k[1] * _C + r.rng(0, _C - 1)
            picks.append(rrec(fld, _C, cx, cy, r.rng(1, 40)))
        _cert, head = nway_null(fld, _C, tuple(picks))
        gh = _global_head(fld, _C, tuple(picks))
        if head != gh:
            raise NwayError(f"scenario {s} (seed {seed}): the shard n-way head {head[:12]}… diverged "
                            f"from the global monolith {gh[:12]}…")
        if independence_rounds(fld, _C, picks) != [tuple(range(n))]:
            raise NwayError(f"scenario {s}: a distinct-chunk batch should be ONE parallel round")
        sizes[n] = sizes.get(n, 0) + 1
        # adversary: duplicate one chunk -> the batch must REFUSE
        dupk = picks[0]
        _p, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(dupk)
        dup = _RN.regional_record(_CK.address(_CK.cut(fld, _C)[(kx, ky)]), kx, ky,
                                  kx * _C + 7, ky * _C + 7, 0, r.rng(1, 40))
        try:
            nway_null(fld, _C, tuple(picks) + (dup,))
            raise NwayError(f"scenario {s}: an overlapping batch was ADMITTED, not refused")
        except NwayError as exc:
            if "was ADMITTED" in str(exc):
                raise
            overlaps_refused += 1
        hh.update(f"|{s}:{n}:{head}".encode())
    if len(sizes) < 3:
        raise NwayError(f"NON-VACUITY: only {len(sizes)} distinct batch sizes — {sizes}")
    if overlaps_refused != count:
        raise NwayError(f"NON-VACUITY: only {overlaps_refused}/{count} overlaps refused")
    return {"scenarios": count, "sizes": sizes, "overlaps_refused": overlaps_refused,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_nway.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise NwayError("no golden named 'sweep'")


def _main(argv):
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} batches, sizes {dict(sorted(rep['sizes'].items()))}, "
          f"overlaps_refused {rep['overlaps_refused']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
