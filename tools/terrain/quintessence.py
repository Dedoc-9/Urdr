# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""quintessence — the ID-0 representation theorem (T3.46, URDRQNT1): the fifth essence. The write
calculus stops expanding and starts CLOSING: every lawful authority in the five landed families
(URDRTFM1 global edits, URDRCMU1 commutation certificates, URDRRAN0 regional edits, URDRLSE1
leases, URDRTST1 testaments) is characterized by its FIVE-AXIS EVIDENCE TUPLE —

    historical  the parent address (what must have come before),
    spatial     the cells claimed, and the claim's scope (global | a named region),
    semantic    the transitions claimed (old -> new), or None for a pure capability,
    temporal    the validity predicate: (scope, address) — under what condition this authority
                still stands,
    identity    the object's own content address (the evidence of intent).

This module mints NOTHING. It is the first rung whose entire content is theorems about existing
objects — extractors, checkers, and their falsifiers.

THE SCOPE FINDING (the tuple's first dividend). Within every family, the historical and temporal
axes carry the SAME address at a SCOPE: a global record's parent IS its validity condition
(world-manifest-current); a regional record's parent IS its lease (chunk-current). Validity is "my
history is still current" — and the SCOPE of that binding is exactly what RAN-0 changed. The tuple
does not merely describe the transport theorem; it PREDICTS it: world-scoped essence refuses on an
elsewhere-moved world, chunk-scoped essence admits, decidable from the tuple before any execution.

CONSERVATION OF AUTHORITY, both halves. Evidence SUFFICES: probate == living admission == the
global reproof (proven piecewise across the arc; behavior is determined by the first four axes —
a record and its testament behave identically on every world). NO EVIDENCE, NO AUTHORITY:
`conservation_check` degrades exactly one axis at a time — a wrong parent (historical), a foreign
region (spatial), a wrong old height (semantic), a moved authority (temporal), a flipped byte
(identity) — and admission must refuse for EVERY axis: each individually load-bearing, one law
across every family. Process lifetime appears on neither side of the ledger: authority is neither
created nor destroyed by death, only by evidence.

ONE LINEAGE (uniqueness modulo certified commutation). `lineage` admits an edit set in a given
order and returns (head, the essence set). Over the corpus: every order — and the parallel path —
carries the SAME essence set to the SAME head (the lineage is the equivalence class, not the
path); a different essence set lands a different head. Heads are in bijection with lineages over
the corpus. Honesty twice over: (1) lawful histories degenerate multisets to sets — an exact
duplicate essence cannot admit twice, because its own admission moved the CAS it binds; (2) the
bijection's injectivity rides on SHA-256 collision-resistance, the one DECLARED pillar under the
whole calculus — stated here, never claimed as proven.

THE CLOSURE LAW (what this rung changes going forward, recorded in the ledger): a future
capability is lawful iff its evidence EMBEDS — `essence_of` extended by one dispatch arm, its
axes checked by the same conservation ablation — rather than by introducing a new kind of
authority. Anything outside the families REFUSES: no essence is ever guessed.

GRADE. Extractor totality and determinism over the five families with typed refusal outside them;
the scope finding and its transport prediction; behavior-determined-by-essence (axes 1-4) over the
world corpus; the five-axis conservation ablation, uniform across families; lineage uniqueness
modulo commutation with the differing-set separation; full-tuple injectivity over the corpus; the
joint essence of certificates; the None-semantic honesty of leases; the lease-from-essence
round-trip; and determinism are MEASURED (exact, reproducible, a defect diverges). DECLARED:
SHA-256 collision-resistance (uniqueness's pillar); the EMBEDDING of future families (the closure
law is a commitment recorded in the ledger, enforced per-family as each lands); axis evidence for
the READ-side families (persist/resurrect/chunkstate windows — their records already obey the same
one-digest law; extending essence_of across them is mechanical future work, stated not begun).
`does_not_show`: authority POLICY of every kind (issuance, scheduling, revocation — `authinput`
territory); wall-clock; cross-placement (Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRQNT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import terraform as _TF
import commute as _CM
import rannull as _RN
import lease as _LS
import testament as _TS
import chunkload as _CK

AX_HISTORICAL, AX_SPATIAL, AX_SEMANTIC, AX_TEMPORAL, AX_IDENTITY = range(5)
AXES = ("historical", "spatial", "semantic", "temporal", "identity")


class QuintessenceError(Exception):
    def __init__(self, message):
        super().__init__(f"QUINTESSENCE-REFUSE: {message}")
        self.code = "QUINTESSENCE-REFUSE"


def _addr(buf):
    return bytes(buf)[-32:].hex()


def essence_of(obj):
    """THE EXTRACTOR: total over the five families, deterministic, typed-refusing outside them.
    Returns the five-axis tuple (historical, spatial, semantic, temporal, identity):
      historical = parent address hex
      spatial    = (claim, cells)  — claim is ("global",) or ("region", kx, ky); cells a tuple
      semantic   = ((old, new), ...) or None (a lease claims no transition)
      temporal   = (scope, address) — scope "world" | "chunk"
      identity   = the object's own content address hex."""
    if not (type(obj) is bytes or type(obj) is bytearray):
        raise QuintessenceError("an authority object must be bytes")
    obj = bytes(obj)
    if obj[:8] == _TF.MAGIC and len(obj) == _TF.EDIT_RECORD_BYTES:
        p, x, y, oh, nh = _TF.restore_edit(obj)
        return (p, (("global",), ((x, y),)), ((oh, nh),), ("world", p), _addr(obj))
    if obj[:8] == _RN.MAGIC and len(obj) == _RN.RAN_RECORD_BYTES:
        p, kx, ky, x, y, oh, nh = _RN.restore_regional(obj)
        return (p, (("region", kx, ky), ((x, y),)), ((oh, nh),), ("chunk", p), _addr(obj))
    if obj[:8] == _LS.MAGIC and len(obj) == _LS.LEASE_BYTES:
        chunk_hex, kx, ky = _LS.restore_lease(obj)
        return (chunk_hex, (("region", kx, ky), ()), None, ("chunk", chunk_hex), _addr(obj))
    if obj[:8] == _TS.MAGIC and len(obj) == _TS.TESTAMENT_BYTES:
        rec = _TS.restore_testament(obj)
        p, kx, ky, x, y, oh, nh = _RN.restore_regional(rec)
        return (p, (("region", kx, ky), ((x, y),)), ((oh, nh),), ("chunk", p), _addr(obj))
    if obj[:8] == _CM.MAGIC and len(obj) == _CM.CERT_BYTES:
        ra, rb, _rank = _CM.restore_cert(obj)
        pa, xa, ya, oa, na = _TF.restore_edit(ra)
        _pb, xb, yb, ob, nb = _TF.restore_edit(rb)
        return (pa, (("global",), ((xa, ya), (xb, yb))), ((oa, na), (ob, nb)),
                ("world", pa), _addr(obj))
    raise QuintessenceError(f"no essence for {obj[:8]!r} ({len(obj)} bytes) — an object outside "
                            f"the five families has no authority here, and none is guessed")


def lease_of_essence(e):
    """The temporal evidence reconstructed as an OBJECT: a chunk-scoped essence's lease,
    bit-for-bit — evidence axes are not commentary; they rebuild the capability they describe."""
    if e[AX_TEMPORAL][0] != "chunk":
        raise QuintessenceError("only a chunk-scoped essence carries a lease")
    claim = e[AX_SPATIAL][0]
    if claim[0] != "region":
        raise QuintessenceError("a chunk-scoped essence must claim a region")
    return _LS.lease_record(e[AX_TEMPORAL][1], claim[1], claim[2])


def conservation_check(field, csize, x, y, dh):
    """NO EVIDENCE, NO AUTHORITY — the five-axis ablation: degrade exactly one axis of a lawful
    regional edit and require admission to REFUSE. Returns {axis: held} — the gate requires every
    axis True. The degradations: historical = a wrong parent digest; spatial = a foreign region
    claim; semantic = a wrong old height; temporal = the authority moved under an otherwise-intact
    record; identity = a flipped byte."""
    key = (x // csize, y // csize)
    chunks = _CK.cut(field, csize)
    chunk = chunks[key]
    old = field[y][x]
    man = _CK.field_manifest(field, csize)
    store = {_CK.address(r): r for r in chunks.values()}

    def _admits(rec, mn=None, st=None):
        try:
            ls = _LS.lease_record(_RN.restore_regional(rec)[0], *_RN.restore_regional(rec)[1:3])
            _LS.admit(mn if mn is not None else man, st if st is not None else store, ls, rec)
            return True
        except Exception:
            return False

    good = _RN.regional_record(_CK.address(chunk), key[0], key[1], x, y, old, old + dh)
    if not _admits(good):
        raise QuintessenceError("the undegraded control must admit — the ablation is void otherwise")
    report = {}
    report["historical"] = not _admits(
        _RN.regional_record("0" * 64, key[0], key[1], x, y, old, old + dh))
    fx, fy = ((x + csize) % len(field[0]), y)                    # a cell in another region
    fkey = (fx // csize, fy // csize)
    report["spatial"] = not _admits(
        _RN.regional_record(_CK.address(chunk), key[0], key[1], fx, fy,
                            field[fy][fx], field[fy][fx] + dh))
    report["semantic"] = not _admits(
        _RN.regional_record(_CK.address(chunk), key[0], key[1], x, y, old + 99, old + dh))
    interloper = _RN.regional_record(_CK.address(chunk), key[0], key[1],
                                     x, (y + 1 if (y + 1) // csize == key[1] else y - 1),
                                     field[(y + 1 if (y + 1) // csize == key[1] else y - 1)][x],
                                     field[(y + 1 if (y + 1) // csize == key[1] else y - 1)][x] + 7)
    man2, ch2 = _LS.admit(man, store, _LS.lease_from_chunk(chunk), interloper)
    store2 = dict(store)
    store2[_CK.address(ch2)] = ch2
    report["temporal"] = not _admits(good, man2, store2)
    bad = bytearray(good)
    bad[40] ^= 0x01
    report["identity"] = not _admits(bytes(bad))
    return report


def lineage(field, csize, records):
    """ONE LINEAGE: admit the edit set in the GIVEN order (each step a lawful leased admission
    against the current head) and return (head_address, the tuple of essences). The theorem lives
    in the falsifiers: every order carries the same essence set to the same head; a different set
    lands a different head."""
    man = _CK.field_manifest(field, csize)
    store = {_CK.address(r): r for r in _CK.cut(field, csize).values()}
    essences = []
    for rec in records:
        essences.append(essence_of(rec))
        p, kx, ky, x, y, oh, nh = _RN.restore_regional(rec)
        _w, _h, _c, grid = _CK.parse_manifest(man)
        cur = store[grid[(kx, ky)]]
        fresh = _RN.regional_record(_CK.address(cur), kx, ky, x, y, oh, nh) \
            if _CK.address(cur) != p else bytes(rec)
        man, ch = _LS.admit(man, store, _LS.lease_from_chunk(cur), fresh)
        store[_CK.address(ch)] = ch
    return _CK.address(man), tuple(essences)


def quintessence_digest(name, head_hex, axes, count, verdict):
    """URDRQNT1 canon — SHA-256(MAGIC | name | head | the axis witnesses | count | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|h:{head_hex}|a:{'/'.join(str(a) for a in axes)}|c:{count}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _family(fld, c, x, y, dh):
    key = (x // c, y // c)
    chunk = _CK.cut(fld, c)[key]
    old = fld[y][x]
    tf = _TF.edit_record(_TF.parent_address(fld, c), x, y, old, old + dh)
    ran = _RN.regional_record(_CK.address(chunk), key[0], key[1], x, y, old, old + dh)
    ls = _LS.lease_from_chunk(chunk)
    t = _TS.testament_record(ran)
    px = (x + c) % len(fld[0])
    partner = _TF.edit_record(_TF.parent_address(fld, c), px, y, fld[y][px], fld[y][px] + 1)
    cert, _h = _CM.certify(fld, c, tf, partner)
    return tf, ran, ls, t, cert


def _scene_distilled():
    """One logical edit, five embodiments, one extractor: the essences agree where the law says
    they agree (cell + transition across forms; axes 1-4 between a record and its testament) and
    differ where the law says they differ (world vs chunk scope — the RAN-0 rebinding, visible)."""
    fld = _blank()
    tf, ran, ls, t, cert = _family(fld, 8, 5, 8, 1000)
    es = [essence_of(o) for o in (tf, ran, ls, t, cert)]
    ok = (es[0][AX_TEMPORAL][0] == "world" and es[1][AX_TEMPORAL][0] == "chunk"
          and es[1][:4] == es[3][:4] and es[1][AX_IDENTITY] != es[3][AX_IDENTITY]
          and es[0][AX_SPATIAL][1][0] == es[1][AX_SPATIAL][1][0]
          and es[0][AX_SEMANTIC][0] == es[1][AX_SEMANTIC][0]
          and es[2][AX_SEMANTIC] is None
          and len(set(es)) == 5)
    wit = hashlib.sha256("|".join(str(e) for e in es).encode()).hexdigest()
    return wit, ("world", "chunk"), 5, ("ADMIT" if ok else "QUINTESSENCE-REFUSE")


def _scene_one_lineage():
    """Three edits, every order, one head, one essence set; a changed transition changes both."""
    import itertools
    fld = _blank()
    recs = []
    for (x, y, dh) in ((5, 8, 1000), (12, 4, 777), (12, 12, 555)):
        key = (x // 8, y // 8)
        chunk = _CK.cut(fld, 8)[key]
        recs.append(_RN.regional_record(_CK.address(chunk), key[0], key[1], x, y,
                                        fld[y][x], fld[y][x] + dh))
    heads, sets_ = set(), set()
    for perm in itertools.permutations(recs):
        h, e = lineage(fld, 8, perm)
        heads.add(h)
        sets_.add(tuple(sorted(str(x) for x in e)))
    other = list(recs)
    key = (0, 1)
    chunk = _CK.cut(fld, 8)[key]
    other[0] = _RN.regional_record(_CK.address(chunk), 0, 1, 5, 8, fld[8][5], fld[8][5] + 999)
    h2, e2 = lineage(fld, 8, other)
    ok = (len(heads) == 1 and len(sets_) == 1 and h2 not in heads
          and tuple(sorted(str(x) for x in e2)) not in sets_)
    return heads.pop(), ("lineage",), 6, ("ADMIT" if ok else "QUINTESSENCE-REFUSE")


def _scene_five_wounds():
    """The conservation ablation: five axes, five degradations, five refusals — no authority
    without evidence, each axis individually load-bearing."""
    fld = _blank()
    report = conservation_check(fld, 8, 5, 8, 1000)
    ok = set(report) == set(AXES) and all(report.values())
    return "0" * 64, tuple(sorted(report)), 5, ("QUINTESSENCE-REFUSE" if ok else "ADMIT")


def _scene_closed_form():
    """Totality + refusal at the boundary: all five families extract; a chunk record, a manifest,
    raw bytes, and a forged magic refuse — the calculus is CLOSED, and nothing outside it is
    granted an essence."""
    fld = _blank()
    objs = _family(fld, 8, 5, 8, 1000)
    total = all(len(essence_of(o)) == 5 for o in objs)
    refused = 0
    chunk = _CK.cut(fld, 8)[(0, 1)]
    for alien in (chunk, _CK.field_manifest(fld, 8), b"\x00" * 96,
                  b"URDRXXX1" + bytes(objs[0][8:])):
        try:
            essence_of(alien)
        except QuintessenceError:
            refused += 1
    ok = total and refused == 4
    return "0" * 64, ("closed",), 9, ("ADMIT" if ok else "QUINTESSENCE-REFUSE")


_SCENES = {"distilled": _scene_distilled, "one_lineage": _scene_one_lineage,
           "five_wounds": _scene_five_wounds, "closed_form": _scene_closed_form}
SCENES = ("distilled", "one_lineage", "five_wounds", "closed_form")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    head, axes, count, verdict = scene_case(name)
    return quintessence_digest(name, head, axes, count, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_quintessence.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise QuintessenceError(f"no golden named {name!r}")
