# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""sealwrit — THE SIGNED WIRE (T3.49, W3, URDRSWT1): WHO may write, composed onto WHAT may change.
The landed wire (URDRWIR1) certified state law and DECLARED authenticity away; this rung pays that
declaration. The 104-byte regional record rides VERBATIM inside a writ sealed by `authinput`'s
Lamport one-time signature (N3's own scheme — the same SHA-256 every placement hand-rolls, no new
primitive) against a roster of pins committed BEFORE the session. The client verifies BOTH: still a
verifier, now of provenance too.

ELIGIBILITY PRECEDES ADMISSION (N3's own ordering, kept): parse -> roster -> pin -> the 256-bit
verify -> the seal ledger -> and ONLY THEN the state law — `wire.client_admit` UNMODIFIED. An
unsigned, mis-signed, unregistered, or seal-broken writ refuses SEAL-REFUSE before the state law
runs; a valid signature can never launder an unlawful record (that refusal is WIRE-REFUSE, the
state law's own voice, and it consumes nothing).

THE ONE-TIME RULE, RETOOLED. authinput enforced one-keypair-one-message through N2's
identity-uniqueness law: a second envelope under a used (peer, seq) was ROLLBACK-CONFLICT, so reuse
was structurally impossible. A retry-friendly transport (the storm's loom) breaks that anchor —
the SAME writ must be redeliverable for free. The replacement law:

  THE FIRST ADMISSION SEALS THE KEYPAIR TO ITS DIGEST. The ledger binds each (writer, seq) to the
  message digest it first ADMITTED. An identical redelivery passes eligibility and dies at the CAS
  (at-most-once, the wire's own theorem, unchanged). A verified-DISTINCT record under a sealed
  keypair — the exact exploit a reuse leak enables, state-lawful by construction — refuses on the
  ledger. Eligibility is consumed by ADMISSION, never by attempt: a state-refused writ leaves the
  keypair unsealed, so reordering costs nothing. And the ledger records only VERIFIED admissions,
  so a garbage signature can never block the honest writ — no poisoning by anyone who cannot sign.

GRADE. The writ format (every byte load-bearing: writer, seq, record, pubkey, and signature flips
each refuse with the replica byte-identical), eligibility-precedes-admission (the both-bad writ
refuses as SEAL, proving the ordering), sign-cannot-launder, first-admission-seals with free
identical retry, the tail-collision forgery refused by the real verifier and ACCEPTED by the
first-byte defect verifier (all 256 bits load-bearing), and determinism are MEASURED. DECLARED,
honestly: the fixture keys derive from PUBLISHED seeds (the gate pins MECHANISM, not secrecy —
authinput's own scope); a writer who signs two distinct messages has leaked forgeability and the
ledger only BOUNDS the damage (at most one admission per keypair — if a forger lands first, the
honest writ refuses; that is the writer's violation, contained); the 24,712-byte writ does not fit
a datagram (Lamport is the house scheme, not the wire-efficient one — the LAW certified here is
scheme-independent, and W5's attestation may carry a compact signature under the same law).
`does_not_show`: key distribution and rotation; wall-clock; the depicting client; cross-placement
(URDRSWT1 joins the placement frontier — batch #3 falls due when the phase seals)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSWT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_HERE, "..", "netcode")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import authinput as _AI                                         # noqa: E402  N3: the key law
import chunkload as _CK                                         # noqa: E402  chunks + demand
import rannull as _RN                                           # noqa: E402  the record law
import wire as _W                                               # noqa: E402  the state law (W1)

REC_LEN = 104
WRIT_LEN = 8 + 8 + 8 + REC_LEN + _AI.PUB_LEN + _AI.SIG_LEN      # 24,712 bytes
_REC_OFF = 24
_PUB_OFF = _REC_OFF + REC_LEN
_SIG_OFF = _PUB_OFF + _AI.PUB_LEN


class SealError(Exception):
    def __init__(self, message):
        super().__init__(f"SEAL-REFUSE: {message}")
        self.code = "SEAL-REFUSE"


def _i64(v):
    return int(v).to_bytes(8, "big", signed=True)


def writ_message(writer, seq, rec):
    """The signed message: SHA-256(MAGIC | "|msg|" | i64 writer | i64 seq | rec). The digest
    STATES ITS SPEAKER — a writ is meaningful in isolation, bound to one identity and one seq."""
    return hashlib.sha256(MAGIC + b"|msg|" + _i64(writer) + _i64(seq) + rec).digest()


def seal(writer, seq, rec, sk):
    """Sign one well-FORMED regional record under one keypair. The signer is not a notary for
    garbage (a non-record refuses), but it does not judge state-lawfulness — that is the
    receiving replica's job, by its own laws. ONE-TIME: never seal two distinct records with
    one keypair (reuse leaks preimages — authinput's own warning, unchanged)."""
    try:
        _RN.restore_regional(rec)
    except _RN.RanError as exc:
        raise SealError(f"only a verified regional record may be sealed: {exc}")
    d = writ_message(writer, seq, rec)
    sig = b"".join(sk[i][_AI._bit(d, i)] for i in range(256))
    return MAGIC + _i64(writer) + _i64(seq) + rec + _AI.pubkey_bytes(sk) + sig


def parse_writ(writ):
    """(writer, seq, rec, pub, sig) from the exact 24,712-byte layout; anything else refuses."""
    if len(writ) != WRIT_LEN or writ[:8] != MAGIC:
        raise SealError(f"a writ is exactly {WRIT_LEN} bytes under {MAGIC!r}")
    writer = int.from_bytes(writ[8:16], "big", signed=True)
    seq = int.from_bytes(writ[16:24], "big", signed=True)
    return (writer, seq, writ[_REC_OFF:_PUB_OFF], writ[_PUB_OFF:_SIG_OFF], writ[_SIG_OFF:])


def verify_writ(writ, roster):
    """Total, pure provenance verification: parse, roster membership, pubkey-to-pin, then all
    256 revealed preimages against the digest's bits. Returns (writer, seq, rec, digest);
    every failure is a typed SEAL-REFUSE. State law is NOT consulted here."""
    writer, seq, rec, pub, sig = parse_writ(writ)
    pin = roster.get((writer, seq))
    if pin is None:
        raise SealError(f"identity ({writer},{seq}) is not in the pre-committed roster")
    if pub[:8] != _AI.PUB_MAGIC or hashlib.sha256(pub).hexdigest() != pin:
        raise SealError(f"the presented pubkey does not hash to identity "
                        f"({writer},{seq})'s roster pin")
    d = writ_message(writer, seq, rec)
    for i in range(256):
        b = _AI._bit(d, i)
        off = 8 + i * 64 + b * 32
        if hashlib.sha256(sig[i * 32:(i + 1) * 32]).digest() != pub[off:off + 32]:
            raise SealError(f"signature bit {i} does not open identity "
                            f"({writer},{seq})'s committed preimage")
    return writer, seq, rec, d


def verify_writ_defect_first_byte(writ, roster):
    """THE DEFECT (gate non-vacuity): a verifier that checks only the first digest byte —
    authinput's own defect probe, lifted to the writ. Must ACCEPT a tail-collision forgery
    the real verifier refuses, proving all 256 bits are load-bearing."""
    try:
        writer, seq, rec, pub, sig = parse_writ(writ)
    except SealError:
        return False
    pin = roster.get((writer, seq))
    if pin is None or pub[:8] != _AI.PUB_MAGIC or hashlib.sha256(pub).hexdigest() != pin:
        return False
    d = writ_message(writer, seq, rec)
    for i in range(8):                                          # DEFECT: 8 bits, not 256
        b = _AI._bit(d, i)
        off = 8 + i * 64 + b * 32
        if hashlib.sha256(sig[i * 32:(i + 1) * 32]).digest() != pub[off:off + 32]:
            return False
    return True


def forge_tail_collision_writ(writer, seq, rec, sk):
    """Fixture forgery: a DIFFERENT (valid-format) record whose writ digest shares its FIRST
    BYTE with the genuine one, carrying the genuine signature. Deterministic search."""
    d = writ_message(writer, seq, rec)
    genuine = seal(writer, seq, rec, sk)
    parent, kx, ky, x, y, oh, nh = _RN.restore_regional(rec)
    for delta in range(1, 1 << 20):
        rec2 = _RN.regional_record(parent, kx, ky, x, y, oh, nh + delta)
        d2 = writ_message(writer, seq, rec2)
        if d2[0] == d[0] and d2 != d:
            return genuine[:_REC_OFF] + rec2 + genuine[_PUB_OFF:]
    raise SealError("no tail collision found (fixture exhausted)")


def subscribe_sealed(field, csize, regions, roster):
    """A sealed client: the wire replica plus the roster and the (empty) seal ledger. The
    ledger maps (writer, seq) -> the hex digest of the message it first ADMITTED."""
    return {"wire": _W.subscribe(field, csize, regions), "roster": dict(roster), "seal": {}}


def client_admit_sealed(client, writ):
    """ELIGIBILITY, THEN ADMISSION. Provenance verifies (SEAL-REFUSE otherwise), the seal
    ledger permits (a verified-distinct record under a sealed keypair refuses), and only then
    the state law runs — `wire.client_admit`, unmodified; its WIRE-REFUSE speaks for itself
    and consumes nothing. Returns a NEW client; every refusal leaves replica AND ledger
    byte-identical (the ledger is written on admission alone)."""
    writer, seq, rec, d = verify_writ(writ, client["roster"])
    sealed = client["seal"].get((writer, seq))
    if sealed is not None and sealed != d.hex():
        raise SealError(f"keypair ({writer},{seq}) is sealed to a different record — one "
                        f"keypair, one admitted message; a distinct reuse is a leak, refused")
    new_wire = _W.client_admit(client["wire"], rec)             # the state law, untouched
    ledger = dict(client["seal"])
    ledger[(writer, seq)] = d.hex()
    return {"wire": new_wire, "roster": client["roster"], "seal": ledger}


def sealed_witness(client):
    """One hex over the whole sealed replica: the wire witness plus the seal ledger in
    identity order — what 'replica AND ledger byte-identical' pins down to."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(_W.replica_witness(client["wire"]).encode())
    for (w, s) in sorted(client["seal"]):
        hh.update(f"|{w},{s}:{client['seal'][(w, s)]}".encode())
    return hh.hexdigest()


def sealwrit_digest(name, witness_hex, writs, refusals, verdict):
    """URDRSWT1 canon — SHA-256(MAGIC | name | witness | writs | refusals | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|n:{writs}|r:{refusals}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- fixtures (PUBLISHED seeds — the gate pins mechanism, not secrecy) -------------------
def fixture_keys(writer, seq):
    return _AI.keygen(_AI.fixture_seed(writer, seq))


def fixture_roster(idents):
    return {(w, s): _AI.roster_pin(_AI.pubkey_bytes(fixture_keys(w, s))) for (w, s) in idents}


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


_ALL4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})


def _scene_signet():
    """Three writers, six sealed writs across four regions: every writ admits, the replica
    mirrors the authority byte-for-byte, and the ledger seals all six keypairs."""
    fld = _blank()
    man, store = _server(fld, 8)
    roster = fixture_roster([(w, s) for w in (1, 2, 3) for s in (0, 1)])
    client = subscribe_sealed(fld, 8, _ALL4, roster)
    ok = True
    for (w, s, x, y, dh) in ((1, 0, 5, 8, 1000), (2, 0, 2, 2, 11), (3, 0, 12, 4, 22),
                             (1, 1, 6, 8, 50), (2, 1, 12, 12, 33), (3, 1, 3, 2, -4)):
        rec = _edit(man, store, x, y, dh, 8)
        man, store = _serve(man, store, rec)
        client = client_admit_sealed(client, seal(w, s, rec, fixture_keys(w, s)))
        _w2, _h2, _c2, grid = _CK.parse_manifest(man)
        ok = ok and all(_CK.address(ch) == grid[k] for k, ch in client["wire"]["chunks"].items())
    ok = ok and len(client["seal"]) == 6
    return sealed_witness(client), 6, 0, ("ADMIT" if ok else "SEAL-REFUSE")


def _scene_impostor():
    """Five forgery shapes — unregistered identity, another identity's genuine keypair, a
    flipped record byte, a flipped signature byte, and the tail-collision forgery — each
    refuse with replica and ledger byte-identical; the genuine writ then admits."""
    fld = _blank()
    man, store = _server(fld, 8)
    roster = fixture_roster([(1, 0)])
    client = subscribe_sealed(fld, 8, _ALL4, roster)
    before = sealed_witness(client)
    rec = _edit(man, store, 5, 8, 100, 8)
    genuine = seal(1, 0, rec, fixture_keys(1, 0))
    bad_rec = bytearray(genuine)
    bad_rec[_REC_OFF + 50] ^= 0x01
    bad_sig = bytearray(genuine)
    bad_sig[WRIT_LEN - 100] ^= 0x01
    probes = (seal(9, 0, rec, fixture_keys(9, 0)), seal(1, 0, rec, fixture_keys(2, 0)),
              bytes(bad_rec), bytes(bad_sig), forge_tail_collision_writ(1, 0, rec, fixture_keys(1, 0)))
    refused = 0
    for probe in probes:
        try:
            client_admit_sealed(client, probe)
        except SealError:
            refused += 1
    pure = sealed_witness(client) == before
    client = client_admit_sealed(client, genuine)
    ok = refused == 5 and pure and len(client["seal"]) == 1
    return sealed_witness(client), 6, refused, ("SEAL-REFUSE" if ok else "ADMIT")


def _scene_burnt_seal():
    """The retooled one-time law: the identical redelivery dies at the CAS (never the seal);
    the verified-DISTINCT record under a sealed keypair — state-lawful by construction —
    refuses on the ledger; the writer's next keypair admits that same record."""
    fld = _blank()
    man, store = _server(fld, 8)
    roster = fixture_roster([(1, 0), (1, 1)])
    client = subscribe_sealed(fld, 8, _ALL4, roster)
    r1 = _edit(man, store, 5, 8, 100, 8)
    man, store = _serve(man, store, r1)
    w1 = seal(1, 0, r1, fixture_keys(1, 0))
    client = client_admit_sealed(client, w1)
    cas_refused = seal_refused = False
    try:
        client_admit_sealed(client, w1)
    except _W.WireError:
        cas_refused = True
    r2 = _edit(man, store, 6, 8, 50, 8)
    try:
        client_admit_sealed(client, seal(1, 0, r2, fixture_keys(1, 0)))
    except SealError:
        seal_refused = True
    client = client_admit_sealed(client, seal(1, 1, r2, fixture_keys(1, 1)))
    ok = cas_refused and seal_refused and len(client["seal"]) == 2
    return sealed_witness(client), 4, 2, ("SEAL-REFUSE" if ok else "ADMIT")


def _scene_precedence():
    """Eligibility precedes admission: the both-bad writ refuses SEAL (the ordering proof);
    the perfectly signed stale record refuses WIRE and seals nothing; after its parent lands,
    the identical retry admits — reordering costs nothing."""
    fld = _blank()
    man, store = _server(fld, 8)
    roster = fixture_roster([(1, 0), (1, 1)])
    client = subscribe_sealed(fld, 8, _ALL4, roster)
    r1 = _edit(man, store, 5, 8, 100, 8)
    man2, store2 = _serve(man, store, r1)
    stale = _edit(man2, store2, 6, 8, 50, 8)
    both_bad = bytearray(seal(1, 1, stale, fixture_keys(1, 1)))
    both_bad[WRIT_LEN - 1] ^= 0x01
    seal_first = wire_voice = False
    try:
        client_admit_sealed(client, bytes(both_bad))
    except SealError:
        seal_first = True
    except _W.WireError:
        seal_first = False
    w2 = seal(1, 1, stale, fixture_keys(1, 1))
    try:
        client_admit_sealed(client, w2)
    except _W.WireError:
        wire_voice = True
    unsealed = client["seal"] == {}
    client = client_admit_sealed(client, seal(1, 0, r1, fixture_keys(1, 0)))
    client = client_admit_sealed(client, w2)
    ok = seal_first and wire_voice and unsealed and len(client["seal"]) == 2
    return sealed_witness(client), 4, 2, ("SEAL-REFUSE" if ok else "ADMIT")


_SCENES = {"signet": _scene_signet, "impostor": _scene_impostor,
           "burnt_seal": _scene_burnt_seal, "precedence": _scene_precedence}
SCENES = ("signet", "impostor", "burnt_seal", "precedence")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, writs, refusals, verdict = scene_case(name)
    return sealwrit_digest(name, wit, writs, refusals, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_sealwrit.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SealError(f"no golden named {name!r}")
