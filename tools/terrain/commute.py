# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""commute — the commutation certificate (T3.41, MMO Stage I, URDRCMU1): the proof-object turn.
`terraform` closed the mutable-world boundary with a total refusal: two edits racing one parent, the
loser is refused — DETECTED, never arbitrated. This rung converts detection into a CALCULUS: two sibling
edits either carry a first-class, content-addressed, independently re-verifiable PROOF that order cannot
matter, or they refuse. Concurrency stops being a policy bolted beside the data laws and becomes a
theorem derived FROM them — terraform's exactly-one-slot locality, chunkload's demand sets, and the CAS
are the premises; the certificate is the composed conclusion.

THE CERTIFICATE. cert = MAGIC(8) | rec_a(96) | rec_b(96) | rank(1) | SHA-256(32) — CERT_BYTES = 233, a
closed form. The two embedded edit records keep their OWN digests (defense in depth: the outer digest
catches transport corruption; the inner digests catch a forger who re-seals the outside around a
tampered inside). The certificate is EVIDENCE, not authority: `check_certificate` re-derives the entire
proof from the parent world and requires the presented bytes to reproduce bit-for-bit — a forged rank,
a tampered record, or a wrong world refuses. Proofs are checked, never trusted.

THE DIAMOND (the theorem the certificate records). For sibling edits A, B on DISTINCT cells:
apply(A) then rebased-B EQUALS apply(B) then rebased-A — field and manifest address — and both equal the
direct two-cell mutation. The proof obligation is discharged CONSTRUCTIVELY: `certify` builds both paths
and refuses if they diverge; nothing is assumed from the geometry that isn't re-checked in bytes.

THE RANK (the graded conflict dimension). rank 0 — different chunks: fields commute AND the manifests
touch disjoint slots AND the blast radii are demand-disjoint (parallel execution certified — every
serial order provably equivalent). rank 1 — same chunk, distinct cells: the world still commutes exactly
(one manifest slot rewritten twice, same final digest) but the blast radii OVERLAP, so parallel
consumers of that chunk must serialize. The SAME cell twice is no rank at all: COMMUTE-REFUSE — the
certified conflict, caught in two independent layers (certify's cell law; the old-height CAS on the
rebased loser).

PREDICTION (scheduled concurrency, not repaired concurrency). `predict` is PURE chunk geometry — no
field, no records, no editing: rank is decidable BEFORE either edit exists, so an authority can schedule
writers in advance; the certificate then confirms in bytes what the geometry promised. Predict proposes,
certify disposes.

THE EXPLICIT REBASE. terraform's law stands unweakened: an edit is NEVER silently rebased. `rebase_edit`
is a MINTING act — a new record, new parent binding, new digest, same claimed cell transition — and the
old-height CAS still guards it (a contested rebase dies there). The refusal law and the certificate law
compose; neither subsumes the other.

CLOSURE (the batch theorem). For n pairwise-distinct sibling edits, `closure` mints every pairwise
certificate and replays EVERY permutation via explicit rebases, requiring one head manifest. A batch
with a contested pair refuses WHOLE — reject whole, never repair. The permutation sweep is the proof
obligation, not a formality: a closure that skipped orders, or repaired around a refusing pair, is a
planted-defect target and reddens.

GRADE. The certificate closed form and round-trip, the exhaustive corruption/truncation refuse, the
diamond over the corpus (field + manifest + direct-mutation equality, both orders), the two-layer
contested-cell refuse, the rank law and its pure-prediction agreement, the explicit-rebase laws, the
permutation closure and its reject-whole, the rank-0 blast independence (a demand-disjoint probe is
invariant across the composed pair; A's blast is unperturbed by B), forgery refusal under full
re-derivation, determinism, and the priced proof are MEASURED (exact, reproducible, a defect diverges).
DECLARED: the independence LATTICE as a first-class queryable structure, proof-carrying repo commits,
a general region ALGEBRA (union/closure/projection over demand sets), and causal witness-sets are the
arc this rung opens, not the rung itself; WHO may author remains `authinput` territory. `does_not_show`:
n-way simultaneous certificates beyond pairwise + closure (the pairwise set + permutation sweep IS the
batch proof at this scale); cross-process scheduling; wall-clock (`bench.py`); cross-placement (Python
reference only until a placement reproduces these digests)."""
import hashlib
import itertools
import os as _os
import sys as _sys

MAGIC = b"URDRCMU1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import terraform as _TF                                         # records, CAS, apply — the premises
import chunkload as _CK                                         # chunks, manifests, demand sets

DIGEST_BYTES = 32
CERT_BYTES = len(MAGIC) + 2 * _TF.EDIT_RECORD_BYTES + 1 + DIGEST_BYTES  # 233


class CommuteError(Exception):
    def __init__(self, message):
        super().__init__(f"COMMUTE-REFUSE: {message}")
        self.code = "COMMUTE-REFUSE"


def predict(csize, xa, ya, xb, yb):
    """The PURE pre-edit rank: chunk geometry only — no field, no records, no editing. rank 0 =
    different chunks (blast-disjoint, parallel certified); rank 1 = same chunk, distinct cells (the
    world commutes, the chunk consumers serialize); the same cell is refused — the certified
    conflict. Concurrency is SCHEDULED here; `certify` later confirms in bytes."""
    for v, nm in ((xa, "xa"), (ya, "ya"), (xb, "xb"), (yb, "yb")):
        if not (type(v) is int and 0 <= v < (1 << 32)):
            raise CommuteError(f"{nm} must be uint32, got {v!r}")
    if not (type(csize) is int and csize > 0):
        raise CommuteError(f"chunk size must be a positive int, got {csize!r}")
    if (xa, ya) == (xb, yb):
        raise CommuteError(f"the same cell ({xa},{ya}) twice is a CONTESTED write — no rank exists; "
                           f"a conflict is detected, never arbitrated")
    return 0 if (xa // csize, ya // csize) != (xb // csize, yb // csize) else 1


def rebase_edit(rec, new_parent_hex):
    """The EXPLICIT rebase: mint a NEW record claiming the SAME cell transition against a new parent.
    A minting act with its own fresh digest — never a mutation of the original, whose stale-parent
    refusal stands untouched. The old-height CAS still guards the result: a contested rebase dies at
    apply, so this cannot launder a conflict."""
    _p, x, y, old_h, new_h = _TF.restore_edit(rec)
    return _TF.edit_record(new_parent_hex, x, y, old_h, new_h)


def _seal(preamble):
    """Append the outer digest. Exposed for the forgery falsifiers: a forger who re-seals a tampered
    preamble must STILL fail `check_certificate`'s re-derivation — the digest is integrity, not truth."""
    return preamble + hashlib.sha256(preamble).digest()


def certify(field, csize, rec_a, rec_b):
    """The theorem prover: for two SIBLING edits (same parent, which must be THIS world) on distinct
    cells, discharge the diamond constructively — apply A then rebased-B, apply B then rebased-A,
    require field AND manifest-address equality — and mint the certificate. Returns (cert, head_hex).
    Refuses: non-sibling records, a stale world, the contested cell, or a diamond that fails to close
    (nothing is assumed from geometry that isn't re-checked in bytes)."""
    pa, xa, ya, _oa, _na = _TF.restore_edit(rec_a)
    pb, xb, yb, _ob, _nb = _TF.restore_edit(rec_b)
    if pa != pb:
        raise CommuteError(f"certificates certify SIBLINGS — one parent, two edits; got "
                           f"{pa[:12]}… and {pb[:12]}…")
    live = _TF.parent_address(field, csize)
    if pa != live:
        raise CommuteError(f"the certificate's parent {pa[:12]}… is not this world {live[:12]}… — "
                           f"a proof is bound to the world it proves")
    rank = predict(csize, xa, ya, xb, yb)
    wa = _TF.apply_edit(field, csize, rec_a)
    wab = _TF.apply_edit(wa, csize, rebase_edit(rec_b, _TF.parent_address(wa, csize)))
    wb = _TF.apply_edit(field, csize, rec_b)
    wba = _TF.apply_edit(wb, csize, rebase_edit(rec_a, _TF.parent_address(wb, csize)))
    if wab != wba:
        raise CommuteError("the diamond did not close: the two orders produced different worlds")
    head = _TF.parent_address(wab, csize)
    if head != _TF.parent_address(wba, csize):
        raise CommuteError("the diamond did not close at the manifest — two heads, one world claimed")
    return _seal(MAGIC + bytes(rec_a) + bytes(rec_b) + bytes([rank])), head


def restore_cert(buf):
    """The inverse of the certificate mint: (rec_a, rec_b, rank) BIT-FOR-BIT or a typed refuse.
    Outer digest first (transport integrity), then the inner records under their OWN digests
    (defense in depth against a re-sealed forgery). Exact length; every flip and truncation refuses."""
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise CommuteError("a certificate must be bytes")
    buf = bytes(buf)
    if len(buf) != CERT_BYTES:
        raise CommuteError(f"a certificate must be exactly {CERT_BYTES} bytes, got {len(buf)}")
    if buf[:len(MAGIC)] != MAGIC:
        raise CommuteError("bad magic — not a URDRCMU1 certificate")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise CommuteError("digest mismatch — tampered, truncated, or corrupted; refused, not repaired")
    off = len(MAGIC)
    rec_a = buf[off:off + _TF.EDIT_RECORD_BYTES]; off += _TF.EDIT_RECORD_BYTES
    rec_b = buf[off:off + _TF.EDIT_RECORD_BYTES]; off += _TF.EDIT_RECORD_BYTES
    rank = buf[off]
    try:
        _TF.restore_edit(rec_a)
        _TF.restore_edit(rec_b)
    except _TF.TerraformError as exc:
        raise CommuteError(f"embedded edit record refused: {exc}")
    if rank not in (0, 1):
        raise CommuteError(f"rank must be 0 or 1, got {rank}")
    return rec_a, rec_b, rank


def check_certificate(field, csize, buf):
    """Independent re-verification — the certificate is EVIDENCE, never authority: restore, re-derive
    the ENTIRE proof from the parent world, and require the presented bytes to reproduce bit-for-bit.
    A forged rank, a tampered inner record under a fresh outer seal, or the wrong world all refuse.
    Returns (rank, head_hex)."""
    rec_a, rec_b, rank = restore_cert(buf)
    cert2, head = certify(field, csize, rec_a, rec_b)
    if cert2 != bytes(buf):
        raise CommuteError("re-derivation does not reproduce the presented certificate — forged")
    return rank, head


def closure(field, csize, records):
    """The batch theorem: n pairwise-distinct sibling edits → every pairwise certificate is minted and
    EVERY permutation of explicit-rebase replay must land ONE head manifest. Returns (head_hex, certs).
    A contested pair refuses the batch WHOLE — reject whole, never repair around it."""
    records = tuple(records)
    if len(records) < 2:
        raise CommuteError(f"a closure needs at least two edits, got {len(records)}")
    certs = tuple(certify(field, csize, records[i], records[j])[0]
                  for i in range(len(records)) for j in range(i + 1, len(records)))
    heads = set()
    for perm in itertools.permutations(range(len(records))):
        cur = field
        for i in perm:
            cur = _TF.apply_edit(cur, csize, rebase_edit(records[i], _TF.parent_address(cur, csize)))
        heads.add(_TF.parent_address(cur, csize))
    if len(heads) != 1:
        raise CommuteError(f"the permutation sweep found {len(heads)} distinct heads — the batch "
                           f"does not commute")
    return heads.pop(), certs


def commute_digest(name, parent_hex, head_hex, rank, nbytes, verdict):
    """URDRCMU1 canon — SHA-256(MAGIC | name | parent | head | rank | bytes | verdict). The rank slot
    carries the scene's proof witness: the pairwise rank, the verified permutation count for a
    closure, or '-' for a refusal."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|h:{head_hex}|r:{rank}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _island():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["island"]())[1]


def _rec(fld, c, x, y, dh):
    return _TF.edit_record(_TF.parent_address(fld, c), x, y, fld[y][x], fld[y][x] + dh)


def _scene_twin_dig():
    """Two digs in different chunks of the island at C=16: rank 0 — the parallel-certified pair.
    ADMIT iff the diamond closes, the rank is 0, and the certificate independently re-verifies."""
    fld = _island()
    p = _TF.parent_address(fld, 16)
    cert, head = certify(fld, 16, _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30))
    rank, rehead = check_certificate(fld, 16, cert)
    ok = rank == 0 and rehead == head
    return p, head, rank, CERT_BYTES, ("ADMIT" if ok else "COMMUTE-REFUSE")


def _scene_quarry():
    """Two digs in the SAME chunk, distinct cells: rank 1 — the world commutes exactly, the chunk's
    consumers must serialize. ADMIT iff the diamond closes with rank 1 and re-verifies."""
    fld = _island()
    p = _TF.parent_address(fld, 16)
    cert, head = certify(fld, 16, _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 11, 10, -25))
    rank, rehead = check_certificate(fld, 16, cert)
    ok = rank == 1 and rehead == head
    return p, head, rank, CERT_BYTES, ("ADMIT" if ok else "COMMUTE-REFUSE")


def _scene_caravan():
    """Three pairwise-distinct edits (mixed ranks): the closure — every pairwise certificate mints,
    all six permutations land one head. The rank slot carries the verified permutation count."""
    fld = _island()
    p = _TF.parent_address(fld, 16)
    recs = (_rec(fld, 16, 10, 10, 50), _rec(fld, 16, 40, 40, 30), _rec(fld, 16, 11, 10, -25))
    head, certs = closure(fld, 16, recs)
    ok = len(certs) == 3 and all(check_certificate(fld, 16, c)[1] for c in certs)
    import math
    nperm = math.factorial(len(recs))
    return p, head, nperm, len(certs) * CERT_BYTES, ("ADMIT" if ok else "COMMUTE-REFUSE")


def _scene_contested():
    """The same cell twice: the certified conflict. The verdict is the refusal itself, caught in BOTH
    layers — certify's cell law AND the old-height CAS on the rebased loser."""
    fld = _island()
    p = _TF.parent_address(fld, 16)
    ra, rb = _rec(fld, 16, 10, 10, 50), _rec(fld, 16, 10, 10, -999)
    layer1 = layer2 = False
    try:
        certify(fld, 16, ra, rb)
    except CommuteError:
        layer1 = True
    wa = _TF.apply_edit(fld, 16, ra)
    try:
        _TF.apply_edit(wa, 16, rebase_edit(rb, _TF.parent_address(wa, 16)))
    except _TF.TerraformError:
        layer2 = True
    ok = layer1 and layer2
    return p, p, "-", 0, ("COMMUTE-REFUSE" if ok else "ADMIT")


_SCENES = {"twin_dig": _scene_twin_dig, "quarry": _scene_quarry,
           "caravan": _scene_caravan, "contested": _scene_contested}
SCENES = ("twin_dig", "quarry", "caravan", "contested")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, head, rank, nbytes, verdict = scene_case(name)
    return commute_digest(name, p, head, rank, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_commute.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CommuteError(f"no golden named {name!r}")
