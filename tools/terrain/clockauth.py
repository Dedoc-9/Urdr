# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""clockauth — CLOCK-AUTHORITY for the lag-compensated hit channel (URDRCLK1): bound the VIEW-TICK a client
may assert to its server-ATTESTED latency, closing the backdating-within-the-window abuse URDRLAG1 left
declared. Composition over `lagcomp` (over `hitbox`, over `perception`), NO NEW GLYPH — the kernel stays
frozen. See `docs/clockauth_brief.md` for the design pass and the D1 §20 glyph ruling.

THE PROBLEM URDRLAG1 LEFT DECLARED. Lag-compensation rewinds the target to the shooter's view-tick `vt` and
bounds `vt` to the compensable window `[now − MAX_REWIND, now]`. But `vt` is TAKEN AS GIVEN — the client
asserts it. A cheater can therefore pick, anywhere in the window, the tick MOST favourable to them (the tick a
target was exposed / on their crosshair), regardless of when they actually rendered. The window bound alone
cannot catch this: the backdated tick is inside the window and geometrically valid there. Clock-authority
closes it — the admissible `vt` is bounded to what the client's MEASURED latency justifies.

THE THESIS. The server holds, per client, an ATTESTED latency `(lat, jitter)` in ticks — derived from the
acknowledgment / round-trip stream, NOT from the claim (a client cannot assert its own latency to widen its
band; that would just move the cheat). The admissible view-tick band at server tick `now` is `[now − lat −
jitter, now − lat + jitter]`, clamped inside the lag-comp window. A claim whose `vt` falls OUTSIDE that band —
too old (backdated) or too recent (claiming a fresher view than the latency allows) — is REFUSED with
R_CLOCK, BEFORE any rewind. A clock-consistent `vt` is then handed to URDRLAG1, whose window+rewind and
URDRHIT1's geometry compose through UNCOMPROMISED.

GRADE. The CLOCK-CONSISTENT admit (a `vt` matching the attested latency, geometrically valid, admits), the
BACKDATING TEETH (a cherry-picked older `vt` — inside the window and geometrically valid at that tick — is
REFUSED, while the no-clock adjudicator admits it), the FORWARD-SKEW refusal (a `vt` fresher than the latency
allows), the ATTESTATION property (a client-asserted latency cannot widen the band — the plant that trusts one
admits a backdate the attested latency refuses), latency-proportionality (a higher-latency client legitimately
gets an older band), composition (URDRLAG1 / URDRHIT1 refusals hold), determinism, the constant-shape verdict,
and the PROOF-CARRYING contract (the verdict carries the attested latency and the admissible band; a re-sealed
forged ADMIT still fails) are MEASURED. DECLARED, honestly: the JITTER tolerance is a real, BOUNDED leak — a
band of width `2·jitter+1` ticks the client may legitimately claim within, because network jitter is real
(fair play); the rung bounds it, it does not eliminate it, and a zero-jitter band would false-refuse honest
laggy players. does_not_show: the ACCURACY of the latency estimate itself (this rung takes `(lat, jitter)` as
the attested truth — how the ack-stream MEASURES it, and defends that measurement against a slow-drip latency
forge, is the declared successor); sub-tick timing; real network transport; cross-placement (URDRCLK1 Python
reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # noqa: E402  (LCG for the sweep, cite helpers)
import hitbox as HB                                                # noqa: E402  (geometric reasons)
import lagcomp as LC                                               # noqa: E402  (the rewind + window, which we bound)

MAGIC = b"URDRCLK1"
DIGEST_BYTES = HB.DIGEST_BYTES
MAX_REWIND = LC.MAX_REWIND                                         # the clock band is clamped inside this window

R_CLOCK = 9                                                       # vt outside the attested-latency band — refuse
_REASON_NAME = dict(LC._REASON_NAME)
_REASON_NAME.update({R_CLOCK: "CLOCK"})

VERDICT_ADMIT = 1
VERDICT_REFUSE = 0

# MAGIC(8)|eid|hx|hy|vt|lat|jitter|lo|hi|vcode|reason|rex|rey (12×4) | cite(32) | sha(32) = 120
_HEADER = len(MAGIC)
_NFIELDS = 12
VERDICT_BYTES = _HEADER + 4 * _NFIELDS + DIGEST_BYTES + DIGEST_BYTES
_ZERO_CITE = "00" * DIGEST_BYTES


class ClockauthError(Exception):
    def __init__(self, message):
        super().__init__(f"CLOCKAUTH-REFUSE: {message}")
        self.code = "CLOCKAUTH-REFUSE"


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the attested clock (server-measured, never client-asserted — the witness) ----------------
def clock(lat, jitter):
    """A per-client ATTESTED latency in ticks + a jitter tolerance. Server-measured from the ack/RTT stream;
    a client never supplies its own (that is the `_admit_client_latency` cheat)."""
    for v in (lat, jitter):
        if type(v) is not int:
            raise ClockauthError(f"clock fields must be int, got {v!r}")
    if lat < 0 or jitter < 0:
        raise ClockauthError("latency and jitter must be non-negative")
    return (lat, jitter)


def band(now, clk):
    """The admissible view-tick band `[lo, hi]` for a client of attested latency `clk` at server tick `now`,
    clamped inside the lag-compensation window `[now − MAX_REWIND, now]`."""
    lat, jitter = clk
    lo = max(now - lat - jitter, now - MAX_REWIND)
    hi = min(now - lat + jitter, now)
    return lo, hi


def _clock_ok(now, clk, vt):
    lo, hi = band(now, clk)
    return lo <= vt <= hi


def _reason(tl, walls, sh, clk, claim):
    """Clock-consistency FIRST (a `vt` outside the attested band is R_CLOCK, before any rewind), then
    delegation to URDRLAG1's lag-compensated admission. The single source of truth. `claim = (eid, hx, hy,
    vt)`."""
    _eid, _hx, _hy, vt = claim
    now = LC.timeline_now(tl)
    if not _clock_ok(now, clk, vt):
        return R_CLOCK
    return LC._reason(tl, walls, sh, claim)


def admit(tl, walls, sh, clk, claim):
    """CLOCK-BOUNDED, LAG-COMPENSATED ADMISSION: True iff the claim's view-tick is consistent with the
    client's attested latency AND the rewound geometry admits. A pure function of (timeline, walls, shooter,
    clock, claim)."""
    return _reason(tl, walls, sh, clk, claim) == HB.R_ADMIT


# ---- the proof-carrying verdict (constant-shape; carries the attested latency + the admissible band) ----
def verdict_bytes_len():
    return VERDICT_BYTES


def adjudicate(tl, walls, sh, clk, claim):
    """SERVER-AUTHORITATIVE, CLOCK-BOUNDED, LAG-COMPENSATED ADJUDICATION: emit the sealed, CONSTANT-SHAPE
    verdict — the verdict code, the reason, the view-tick, the ATTESTED latency and jitter, the admissible
    band `[lo, hi]` the server enforced (auditable: an observer sees WHY the view-tick was accepted or
    refused), the exact rewound position, and the target's citation on ADMIT. Witness-blind; a pure function
    of the timeline + clock + claim."""
    eid, hx, hy, vt = claim
    lat, jitter = clk
    now = LC.timeline_now(tl)
    lo, hi = band(now, clk)
    reason = _reason(tl, walls, sh, clk, claim)
    admitted = reason == HB.R_ADMIT
    rex, rey, rcite = LC._rewound_pos(tl, claim)
    cite_hex = rcite if admitted else _ZERO_CITE
    body = bytearray(MAGIC)
    body += _u32(eid) + _u32(hx) + _u32(hy) + _u32(vt)
    body += _u32(lat) + _u32(jitter) + _u32(lo) + _u32(hi)
    body += _u32(VERDICT_ADMIT if admitted else VERDICT_REFUSE) + _u32(reason)
    body += _u32(rex) + _u32(rey)
    body += PC._cite_bytes(cite_hex)
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(verdict):
    if not (type(verdict) is bytes or type(verdict) is bytearray):
        raise ClockauthError("a verdict must be bytes")
    t = bytes(verdict)
    if len(t) != VERDICT_BYTES:
        raise ClockauthError(f"a verdict must be exactly {VERDICT_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise ClockauthError("bad magic — not a URDRCLK1 verdict")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise ClockauthError("digest mismatch — tampered or truncated")
    off = _HEADER
    f = []
    for _ in range(_NFIELDS):
        f.append(int.from_bytes(t[off:off + 4], "big", signed=True)); off += 4
    eid, hx, hy, vt, lat, jitter, lo, hi, vcode, reason, rex, rey = f
    cite = t[off:off + DIGEST_BYTES].hex()
    return (eid, hx, hy, vt, lat, jitter, lo, hi, vcode, reason, rex, rey, cite)


def read_verdict(verdict):
    """The client's view: (eid, hx, hy, vt, lat, jitter, lo, hi, admitted, reason, rex, rey, cite)."""
    (eid, hx, hy, vt, lat, jitter, lo, hi, vcode, reason, rex, rey, cite) = _parse(verdict)
    return (eid, hx, hy, vt, lat, jitter, lo, hi, vcode == VERDICT_ADMIT, reason, rex, rey, cite)


def verify_verdict(tl, walls, sh, clk, verdict):
    """THE PROOF-CARRYING CONTRACT: a verdict is lawful iff it is BYTE-IDENTICAL to the authoritative
    clock-bounded adjudication of its own claim under the SERVER's attested clock. A re-sealed forged ADMIT
    fails, because a fresh adjudication (clock band + rewind + geometry) disagrees."""
    try:
        eid, hx, hy, vt = _parse(verdict)[:4]
    except ClockauthError:
        return False
    return bytes(verdict) == adjudicate(tl, walls, sh, clk, (eid, hx, hy, vt))


# ---- the falsifier tools (NOT laws — each a distinct forgery the clock-authority law refuses) ----------
def _admit_no_clock(tl, walls, sh, clk, claim):
    """THE NO-CLOCK MISTAKE (the core teeth): skip the attested-latency band entirely and delegate straight
    to lag-compensation — admits a CHERRY-PICKED backdated (or forward-skewed) view-tick the client's measured
    latency does not justify. Clock-authority refuses it with R_CLOCK."""
    return LC.admit(tl, walls, sh, claim)


def _admit_client_latency(tl, walls, sh, claimed_clk, claim):
    """THE CLIENT-LATENCY MISTAKE: trust a CLIENT-ASSERTED latency instead of the server-attested one — a
    cheater claims to be laggier than they are to widen their band and legalise a backdate. The law reads only
    the ATTESTED clock, so it refuses where this admits."""
    _eid, _hx, _hy, vt = claim
    now = LC.timeline_now(tl)
    if not _clock_ok(now, claimed_clk, vt):                       # the CLIENT's inflated band, the bug
        return False
    return LC.admit(tl, walls, sh, claim)


def forge_admit(verdict):
    """A falsifier tool: rewrite a REFUSE verdict into a sealed ADMIT (flip the code and reason, re-seal the
    self-digest). `verify_verdict` must STILL refuse it — the forgery disagrees with the authoritative
    adjudication. Never a law."""
    t = bytearray(verdict[:-DIGEST_BYTES])
    off = _HEADER + 4 * 8                                         # past MAGIC | eid hx hy vt lat jitter lo hi
    t[off:off + 4] = _u32(VERDICT_ADMIT)
    t[off + 4:off + 8] = _u32(HB.R_ADMIT)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests ----------------------------------------------------------------------------------
def world_digest(tl, walls, clk):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(LC.world_digest(tl, walls).encode())
    hh.update(f"|clk{clk[0]}:{clk[1]}".encode())
    return hh.hexdigest()


def verdict_digest(verdict):
    return hashlib.sha256(MAGIC + bytes(verdict)).hexdigest()


def clockauth_digest(name, world_hex, verdict_hex, reason, verdict_name):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|w:{world_hex}|v:{verdict_hex}|r:{reason}|d:{verdict_name}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _d(i):
    return PC._d(i)


def _static_timeline(now, x):
    """A target (id 1) static on the +x axis at every buffered tick — hittable at ANY tick, so the ONLY thing
    that distinguishes a legitimate view-tick from a backdated one is the clock. A far wall-shadowed target
    (id 2) lives in every snapshot for the composition scene."""
    tl = {}
    for t in range(now - MAX_REWIND - 2, now + 1):
        tl[t] = {1: (x, 0, 1, 1, _d(1)), 2: (14, 0, 1, 1, _d(2))}
    return tl


def _scene(name, tl, walls, sh, clk, claim):
    v = adjudicate(tl, walls, sh, clk, claim)
    reason = _reason(tl, walls, sh, clk, claim)
    return clockauth_digest(name, world_digest(tl, walls, clk), verdict_digest(v), reason, _REASON_NAME[reason])


def _scene_consistent():
    """A view-tick matching the attested latency (lat 3, band [96,98] at now=100) on a hittable target ADMITS."""
    tl = _static_timeline(100, 7)
    return _scene("consistent", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), clock(3, 1), (1, 7, 0, 97))


def _scene_backdate():
    """THE TEETH: a cherry-picked older view-tick (95, below the band [96,98]) — inside the lag window and
    geometrically valid on the static target — is REFUSED with R_CLOCK; the client's latency does not justify
    seeing that far back."""
    tl = _static_timeline(100, 7)
    return _scene("backdate", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), clock(3, 1), (1, 7, 0, 95))


def _scene_forward():
    """A view-tick fresher than the latency allows (100, above the band [96,98]) is REFUSED — a laggy client
    cannot claim to have seen the present."""
    tl = _static_timeline(100, 7)
    return _scene("forward", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), clock(3, 1), (1, 7, 0, 100))


def _scene_laggy():
    """Latency-proportional: a higher-latency client (lat 6, band [93,95]) legitimately gets an OLDER band —
    a view-tick of 94 ADMITS. The band tracks the attested latency; you cannot claim a laggy view unless you
    are laggy."""
    tl = _static_timeline(100, 7)
    return _scene("laggy", tl, frozenset(), HB.shooter(0, 0, 1, 0, 400), clock(6, 1), (1, 7, 0, 94))


def _scene_wall():
    """Composition: a clock-consistent view-tick whose rewound target is behind a wall is still REFUSED with
    R_WALL — clock-authority gates WHEN, URDRHIT1 still gates WHERE."""
    tl = _static_timeline(100, 7)
    return _scene("wall", tl, frozenset({(10, 0)}), HB.shooter(0, 0, 1, 0, 400), clock(3, 1), (2, 14, 0, 97))


_SCENES = {"consistent": _scene_consistent, "backdate": _scene_backdate, "forward": _scene_forward,
           "laggy": _scene_laggy, "wall": _scene_wall}
SCENES = ("consistent", "backdate", "forward", "laggy", "wall")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_clockauth.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ClockauthError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260725
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random arena with a static on-axis target (id 1), a far wall-shadowed target (id 2), and a random
    ATTESTED latency (lat, jitter). The static target is hittable at every tick, so the clock band is the sole
    discriminator between a legitimate and a backdated view-tick."""
    now = 100
    x1 = r.rng(5, 7)
    lat = r.rng(2, 5)
    jitter = r.rng(0, 1)
    tl = _static_timeline(now, x1)
    walls = frozenset({(10, 0)})
    return tl, walls, HB.shooter(0, 0, 1, 0, 400), clock(lat, jitter), now, x1


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random arenas asserting the clock-consistent admit, the
    BACKDATING TEETH (a cherry-picked older view-tick is refused while the no-clock adjudicator admits it), the
    forward-skew refusal, the ATTESTATION property (a client-asserted latency admits a backdate the attested
    latency refuses), composed geometry (a wall-shadowed clock-consistent shot refused), determinism, the
    constant-shape verdict, and the PROOF-CARRYING contract. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    admit_seen = backdate_seen = forward_seen = attest_seen = wall_seen = 0
    for s in range(count):
        tl, walls, sh, clk, now, x1 = gen_scenario(r)
        lat, jitter = clk
        before = world_digest(tl, walls, clk)
        # CLOCK-CONSISTENT admit — view-tick at the centre of the attested band
        good = (1, x1, 0, now - lat)
        v = adjudicate(tl, walls, sh, clk, good)
        if world_digest(tl, walls, clk) != before:
            raise ClockauthError(f"scenario {s}: adjudication mutated the witness")
        if len(v) != verdict_bytes_len():
            raise ClockauthError(f"scenario {s}: the verdict is not constant-shape")
        if adjudicate(tl, walls, sh, clk, good) != v:
            raise ClockauthError(f"scenario {s}: adjudication is not deterministic")
        if not verify_verdict(tl, walls, sh, clk, v):
            raise ClockauthError(f"scenario {s}: an honest verdict failed its own contract")
        if not admit(tl, walls, sh, clk, good):
            raise ClockauthError(f"scenario {s} (seed {seed}): a clock-consistent shot was refused")
        admit_seen += 1
        # BACKDATING TEETH — a view-tick just below the band; refused by the clock, admitted by the no-clock plant
        back = (1, x1, 0, now - lat - jitter - 1)
        if admit(tl, walls, sh, clk, back):
            raise ClockauthError(f"scenario {s} (seed {seed}): a backdated view-tick was admitted — the clock "
                                 f"bound was bypassed")
        if _reason(tl, walls, sh, clk, back) != R_CLOCK:
            raise ClockauthError(f"scenario {s}: a backdated claim refused for a reason other than the clock")
        if not _admit_no_clock(tl, walls, sh, clk, back):
            raise ClockauthError(f"scenario {s}: the no-clock plant did not admit the backdate (vacuous)")
        backdate_seen += 1
        # FORWARD-SKEW — a view-tick just above the band is refused
        fwd = (1, x1, 0, now - lat + jitter + 1)
        if admit(tl, walls, sh, clk, fwd):
            raise ClockauthError(f"scenario {s}: a forward-skewed view-tick was admitted")
        forward_seen += 1
        # ATTESTATION — a client-asserted (inflated) latency admits the backdate the attested clock refuses
        claimed = clock(lat + jitter + 1, jitter)
        if not _admit_client_latency(tl, walls, sh, claimed, back):
            raise ClockauthError(f"scenario {s}: the client-latency plant did not admit the backdate (vacuous)")
        attest_seen += 1
        # COMPOSED GEOMETRY — a clock-consistent but wall-shadowed shot is refused; a forged ADMIT never verifies
        wall_claim = (2, 14, 0, now - lat)
        vw = adjudicate(tl, walls, sh, clk, wall_claim)
        if admit(tl, walls, sh, clk, wall_claim):
            raise ClockauthError(f"scenario {s}: a wall-shadowed clock-consistent shot was admitted")
        if verify_verdict(tl, walls, sh, clk, forge_admit(vw)):
            raise ClockauthError(f"scenario {s}: a forged ADMIT verified — the proof-carrying contract broke")
        wall_seen += 1
        hh.update(f"|{s}:{verdict_digest(v)}:{verdict_digest(vw)}".encode())
    if admit_seen == 0 or backdate_seen == 0 or forward_seen == 0 or attest_seen == 0 or wall_seen == 0:
        raise ClockauthError(f"NON-VACUITY: admit {admit_seen}, backdate {backdate_seen}, forward "
                             f"{forward_seen}, attest {attest_seen}, wall {wall_seen}")
    return {"scenarios": count, "admit_seen": admit_seen, "backdate_seen": backdate_seen,
            "forward_seen": forward_seen, "attest_seen": attest_seen, "wall_seen": wall_seen,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_clockauth.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise ClockauthError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except ClockauthError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        print(f"EXPLORE: {'no counterexample' if not found else str(len(found)) + ' counterexample(s)'} "
              f"across {n} reseeded sweeps from base {base}.")
        for seed, msg in found:
            print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} arenas, admit_seen {rep['admit_seen']}, backdate_seen "
          f"{rep['backdate_seen']}, forward_seen {rep['forward_seen']}, attest_seen {rep['attest_seen']}, "
          f"wall_seen {rep['wall_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
