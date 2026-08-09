# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""urdr-netcode N3 — AUTHENTICATED INPUTS: Lamport one-time signatures over the frozen
transcript. `digest != MAC` is finally answered with an actual signature.

The separation this module enforces STRUCTURALLY:

    authentication decides WHO may submit an input (this module);
    the deterministic authority decides WHAT state results (rollback.Peer, N2);
    witnesses prove WHAT HAPPENED (URDRLST1/URDRLSTT, N1 — both frozen).

An `AuthedPeer` wraps a rollback peer and admits an event into the transcript ONLY
after its envelope verifies; a failed verification is a typed AUTH-REFUSE, rejected
WHOLE — nothing reaches the authority, the chain is untouched. A correctly signed log
therefore produces the SAME canonical chain as N1/N2: authentication changes
eligibility, never state law.

The scheme (hash-based, no new primitive — the same SHA-256 every placement already
hand-rolls):

  message   d = SHA-256("URDRAIN1" | tick,peer,seq,body,dvx,dvy as signed i64 BE)
  secret    sk[i][b] = SHA-256("URDRKEY1" | seed | u32BE(i) | u8(b)),  i in 0..255
  public    pub = "URDRPUB1" | SHA-256(sk[0][0]) | SHA-256(sk[0][1]) | ... (16,392 B)
  roster    pin(peer,seq) = SHA-256(pub)  — committed BEFORE the session
  sign      reveal sk[i][bit_i(d)] for each of the 256 digest bits (MSB-first)
  verify    pub hashes to the roster pin, then SHA-256(revealed_i) == pub[i][bit_i(d)]

Why this is a signature and not a MAC: the verifier holds only HASHES of the secret
preimages, so no verifier — including a malicious fellow peer — can forge a signature
it has not seen. The commit-then-reveal pin makes pubkey substitution refuse before
the signature is even considered.

The ONE-TIME rule is load-bearing: signing two different messages under one keypair
reveals preimages for both bit values and leaks forgeability. The rule is enforced at
admission by N2's identity-uniqueness law — a second distinct envelope under a used
(peer, seq) is ROLLBACK-CONFLICT — so one keypair per (peer, seq) is structural, not
advisory.

GRADE (honest, D5): MEASURED (both placements) — the `netcode_auth` gate stage pins the
goldens, refusals, and the first-byte defect probe; the std-only Rust placement
(authinput_rs/, ADMITTED on Windows/rustc) reproduces the roster root and signed chain
2/2 with all refusal shapes typed, and its --defect finds the SAME tail-collision
forgery (dvx offset 423) as the independent C99 cross-check. Contracts FROZEN at
urdr-netcode-auth 0.1 (spec/D12). Honest scope: the gate pins the MECHANISM —
verification gates admission — on fixture keys derived from PUBLISHED seeds
(deterministic on purpose). Operational key secrecy, key distribution, and
replay-across-sessions are OUT of scope and never claimed."""
import hashlib
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "physics"))
import lockstep as _L                                      # noqa: E402  the ONE event law
import rollback as _rollback                               # noqa: E402  N2 authority

MSG_MAGIC = b"URDRAIN1"
KEY_MAGIC = b"URDRKEY1"
PUB_MAGIC = b"URDRPUB1"
ROSTER_MAGIC = b"URDRROS1"
SEED_MAGIC = b"URDRSEED"
PUB_LEN = 8 + 256 * 64                                     # magic + 256 hash pairs
SIG_LEN = 256 * 32                                         # one revealed preimage per bit

# The canonical FIXTURE session (PUBLISHED — the gate pins mechanism, not secrecy).
SESSION = hashlib.sha256(b"URDR-N3-canonical-session-1").digest()


class AuthError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _h(b):
    return hashlib.sha256(b).digest()


def _i64(v):
    """THE SERIALIZER, AND IT WAS PROJECTING RATHER THAN SERIALIZING. `int(v)` here
    meant `msg_digest` committed to `int(x)` of each component instead of to the
    component, so the signature bound a PROJECTION of the message and not the message:
    measured, `4`, `4.0`, `4.9` and `"4"` all produce the IDENTICAL message digest, and
    an honest signature over `dvx=4` verifies against a delivered payload of `4.9` or
    `"4"`. A wire tamperer could therefore alter the bytes that arrive without
    invalidating the signature — N3's headline is that a signature catches a forging
    PEER, and this is a non-peer altering an authenticated payload.

    The outcome did not diverge, because `worldpeer.deliver_envelope` ran the SAME
    silent `int()` on delivery, so the two projections agreed. That agreement is what
    hid it: two coercions that happen to match look exactly like no coercion at all,
    and if they had ever rounded differently it would have been a desync.

    A malformed word is `AUTH-MALFORMED`, a DISTINCT code from `AUTH-REFUSE` and not a
    subclass of it: "this is not a well-formed event" and "this signature is invalid"
    are different facts, and merging them destroys attribution exactly as tilemin's
    integrity/policy split showed one arc over. No digest changes for integer input."""
    if not isinstance(v, int) or isinstance(v, bool):
        raise AuthError("AUTH-MALFORMED",
                        "an event word must be an exact integer, got %r (%s) — a silent "
                        "int() here would make the signature commit to a projection of "
                        "the message rather than to the message" % (v, type(v).__name__))
    return v.to_bytes(8, "big", signed=True)


def admit_event(e):
    """THE DOOR: an event is a 6-tuple of exact integers, or it is not an event.

    The PREDICATE is `lockstep.event_shape_fault` — one law, written once. This module
    carried its own copy because `event_fault` demanded a WORLD and the wire layer has
    none; splitting the shape half out of the range half removed the obstacle, and the
    import was already there transitively (authinput -> rollback -> lockstep). The CODE
    stays AUTH-MALFORMED: N3 answers in N3's vocabulary, and it can only ask the
    world-free half, because a wire does not know how many bodies a world has.

    Called BEFORE identity, signature and the time law, and the order is structural
    rather than preferred — `msg_digest` is undefined on a malformed event, so there is
    no signature question to ask about one. Returns the event unchanged, never a
    normalized copy, which is the whole point."""
    why = _L.event_shape_fault(e)
    if why is not None:
        raise AuthError("AUTH-MALFORMED", why)
    return e


def msg_digest(e):
    """The signed message: SHA-256(MSG_MAGIC | the event's six signed i64 BE words)."""
    return _h(MSG_MAGIC + b"".join(_i64(x) for x in e))


def _bit(d, i):
    """Bit i of digest d, MSB-first within each byte (the frozen indexing law)."""
    return (d[i // 8] >> (7 - (i % 8))) & 1


def fixture_seed(peer, seq):
    """Deterministic PUBLISHED per-identity seed for the canonical fixtures."""
    return _h(SEED_MAGIC + _i64(peer) + _i64(seq) + SESSION)


def keygen(seed):
    """One Lamport keypair from a 32-byte seed: 256 preimage pairs."""
    return [(_h(KEY_MAGIC + seed + i.to_bytes(4, "big") + b"\x00"),
             _h(KEY_MAGIC + seed + i.to_bytes(4, "big") + b"\x01"))
            for i in range(256)]


def pubkey_bytes(sk):
    """Canonical public key: PUB_MAGIC | H(x_i,0) | H(x_i,1) for i = 0..255."""
    out = bytearray(PUB_MAGIC)
    for (x0, x1) in sk:
        out += _h(x0) + _h(x1)
    return bytes(out)


def roster_pin(pub):
    """The pre-session commitment for one identity: SHA-256(pubkey), hex."""
    return _h(pub).hex()


def roster_root(roster):
    """One digest over the whole roster, identities in canonical (peer, seq) order."""
    h = hashlib.sha256()
    h.update(ROSTER_MAGIC)
    for (peer, seq) in sorted(roster):
        h.update(_i64(peer) + _i64(seq) + bytes.fromhex(roster[(peer, seq)]))
    return h.hexdigest()


def sign(sk, e):
    """Reveal one preimage per digest bit. ONE-TIME: never sign two messages with
    one keypair (reuse leaks preimages — see the module docstring)."""
    d = msg_digest(e)
    return b"".join(sk[i][_bit(d, i)] for i in range(256))


def envelope(e, sk):
    """(event, pubkey, signature) — everything a verifier needs besides the pin.

    The SENDER's coercion is gone too. `tuple(int(x) for x in e)` quietly normalized
    the event it published while `sign` hashed the raw one, so the sender was shipping
    a payload it had silently rewritten — the same act on the other end of the wire,
    and the reason the honest path never carried a float for anyone to notice."""
    e = admit_event(e)
    return (tuple(e), pubkey_bytes(sk), sign(sk, e))


def verify(env, pin):
    """Total, pure verification against a roster pin. True iff the pubkey hashes to
    the pin AND every one of the 256 revealed preimages hashes to the committed
    value selected by the message digest's bits."""
    e, pub, sig = env
    if len(pub) != PUB_LEN or len(sig) != SIG_LEN or pub[:8] != PUB_MAGIC:
        return False
    if _h(pub).hex() != pin:
        return False
    d = msg_digest(e)
    for i in range(256):
        b = _bit(d, i)
        off = 8 + i * 64 + b * 32
        if _h(sig[i * 32:(i + 1) * 32]) != pub[off:off + 32]:
            return False
    return True


def verify_defect_first_byte(env, pin):
    """THE DEFECT (gate non-vacuity): a verifier that checks only the first digest
    byte (bits 0..7). Must ACCEPT a tail-collision forgery the real verifier refuses
    — proving all 256 bits are load-bearing."""
    e, pub, sig = env
    if len(pub) != PUB_LEN or len(sig) != SIG_LEN or pub[:8] != PUB_MAGIC:
        return False
    if _h(pub).hex() != pin:
        return False
    d = msg_digest(e)
    for i in range(8):                                     # DEFECT: 8 bits, not 256
        b = _bit(d, i)
        off = 8 + i * 64 + b * 32
        if _h(sig[i * 32:(i + 1) * 32]) != pub[off:off + 32]:
            return False
    return True


def forge_tail_collision(e, sk):
    """Fixture forgery: a DIFFERENT event whose message digest shares the FIRST BYTE
    with `e`'s, carrying `e`'s signature. The defect verifier accepts it; the real
    one refuses. Deterministic search (expected ~256 probes)."""
    d = msg_digest(e)
    pub, sig = pubkey_bytes(sk), sign(sk, e)
    for delta in range(1, 1 << 20):
        e2 = (e[0], e[1], e[2], e[3], e[4] + delta, e[5])
        d2 = msg_digest(e2)
        if d2[0] == d[0] and d2 != d:
            return (e2, pub, sig)
    raise AuthError("AUTH-REFUSE", "no tail collision found (fixture exhausted)")


class AuthedPeer:
    """N3 in front of N2: only a VERIFIED envelope reaches the deterministic
    authority. The wrapper holds the roster; the inner rollback peer holds state —
    authentication cannot touch state except by admitting a valid input."""

    def __init__(self, w, roster, K=8, H=8):
        self.roster = dict(roster)
        self._peer = _rollback.Peer(w, K=K, H=H)

    def deliver_envelope(self, env):
        """Admit-shape, then verify, then delegate. `AUTH-MALFORMED` on an event that is
        not six exact integers; `AUTH-REFUSE` (typed, whole) on an unregistered identity,
        a pubkey not matching the pin, or an invalid signature; on success the N2
        authority's returns and refusals apply unchanged.

        THE THIRD LAUNDERING SITE, and it is the one that shows the defect was a habit
        rather than an oversight: the same `tuple(int(x) for x in e)` appeared at the
        SENDER (`envelope`), at the SERIALIZER (`_i64`), and at BOTH receivers — N3 here
        and N5 in `worldpeer`. Four silent quantizations that all agreed, which is
        exactly why nothing ever diverged and nothing ever refused."""
        e, pub, sig = env
        e = admit_event(e)
        ident = (e[1], e[2])
        pin = self.roster.get(ident)
        if pin is None:
            raise AuthError("AUTH-REFUSE", f"identity {ident} not in the roster")
        if not verify((e, pub, sig), pin):
            raise AuthError("AUTH-REFUSE",
                            f"envelope for identity {ident} failed verification")
        return self._peer.deliver(e)

    def advance(self, until_tick):
        self._peer.advance(until_tick)

    def chain(self):
        return self._peer.chain()

    def trace(self):
        return self._peer.trace()

    @property
    def snapshots(self):
        return self._peer.snapshots
