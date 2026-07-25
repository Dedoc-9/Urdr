# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""latencyest — THE LATENCY-ESTIMATOR that feeds clock-authority (URDRLES1): measure the attested clock
`(lat, jitter)` URDRCLK1 consumes from the acknowledgment / round-trip stream, and DEFEND that measurement
against a slow-drip latency forge. Composition over `clockauth` (over `lagcomp`, `hitbox`, `perception`), NO
NEW GLYPH — the kernel stays frozen. See `docs/latencyest_brief.md` for the design pass and the D1 §20 glyph
ruling.

THE PROBLEM URDRCLK1 LEFT DECLARED. Clock-authority bounds the client's asserted view-tick to a
server-ATTESTED latency `(lat, jitter)` — but takes that latency as given. It does not say HOW the server
measures it, nor how it resists a client that gradually inflates its apparent ping to widen its clock band
over time (the slow-drip latency forge), eventually legalising a backdate. This rung closes it: `(lat,
jitter)` is derived deterministically from the ack stream, and the derivation is built to resist inflation.

THE THESIS — WHY THE MINIMUM. The server periodically sends a tick-stamped ping; the client echoes it; the
server measures `RTT = recv_tick − sent_tick`. A cheater can DELAY an echo (inflating that sample's RTT) but
can NEVER make it arrive faster than the true network path — so the MINIMUM RTT over a window is the honest
floor, immune to inflation as long as one true-timed ack lands in the window. The one-way latency is
`min_rtt // 2`. Two further defenses: the estimate may RISE by at most `MAX_RISE` ticks per update (a drip is
rate-limited and bounded) but FALLS freely (a genuinely improved ping immediately tightens the band — fair
play, never a cheat); and the jitter is the bounded spread, CAPPED at `MAX_JITTER`, so a few delayed acks
cannot widen the band without limit. An implausible RTT — negative (an echo before its ping) or beyond
`MAX_RTT` — is REJECTED, never folded into the estimate.

GRADE. The honest convergence (a steady ack stream yields the true one-way latency), the MIN-FLOOR
(inflating some acks does not move `lat` off the minimum — the mean-based plant is admitted a backdate the
min-floored law refuses), the RATE-LIMITED rise (a drip cannot jump the estimate — the no-rate-limit plant
is), the FREE fall (an improved ping tightens immediately), the jitter cap, the plausibility rejection, the
END-TO-END composition (an inflation that a defective estimator would let widen the clock band enough to
admit a backdate is REFUSED by the honest estimator feeding URDRCLK1), determinism, and the PROOF-CARRYING
published record (bound to the ack window; a forged higher latency fails verification) are MEASURED.
DECLARED, honestly: this BOUNDS and SLOWS band-widening — it does not make inflation impossible. A patient
cheater who delays EVERY ack in the window can raise the min, and the estimate can still rise `MAX_RISE` per
update; the rung caps the RATE and forces the inflation to be total (every ack delayed) and visible, it does
not prove a cheater can never widen their band at all. does_not_show: the ping SCHEDULING / sample selection
policy (this rung consumes a given window); clock-skew between server and client beyond the jitter model;
real network transport; cross-placement (URDRLES1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # noqa: E402  (LCG + cite helpers)
import clockauth as CK                                             # noqa: E402  (the clock this rung produces)

MAGIC = b"URDRLES1"
DIGEST_BYTES = CK.DIGEST_BYTES

WINDOW = 8                                                        # max ack samples per estimate
MAX_RISE = 1                                                     # ticks the estimate may RISE per update (anti-drip)
MAX_JITTER = 2                                                   # the jitter cap (bounds band width)
MAX_RTT = 2 * CK.MAX_REWIND                                      # an RTT beyond this is implausible

# record: MAGIC(8) | prev_lat(4) | lat(4) | jitter(4) | n(4) | samples_digest(32) | sha(32) = 88
_HEADER = len(MAGIC)
RECORD_BYTES = _HEADER + 4 * 4 + DIGEST_BYTES + DIGEST_BYTES


class LatencyestError(Exception):
    def __init__(self, message):
        super().__init__(f"LATENCYEST-REFUSE: {message}")
        self.code = "LATENCYEST-REFUSE"


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the ack stream (the witness — server-stamped ping / client echo) -------------------------
def sample(sent_tick, recv_tick):
    """One round-trip sample: the server stamped `sent_tick` on a ping and received the echo at
    `recv_tick`."""
    for v in (sent_tick, recv_tick):
        if type(v) is not int:
            raise LatencyestError(f"sample fields must be int, got {v!r}")
    return (sent_tick, recv_tick)


def _rtt(s):
    return s[1] - s[0]


def _plausible(s):
    r = _rtt(s)
    return 0 <= r <= MAX_RTT


def _validate_window(samples):
    if not samples or len(samples) > WINDOW:
        raise LatencyestError(f"an ack window must hold 1..{WINDOW} samples, got {len(samples)}")
    for s in samples:
        if not (isinstance(s, tuple) and len(s) == 2):
            raise LatencyestError("each sample must be (sent_tick, recv_tick)")


# ---- the estimator (deterministic, min-floored, rate-limited — the law) -----------------------
def _raw_lat(samples):
    """The MIN-floored one-way latency: `min RTT // 2`. Module scope so the falsifiers can plant a mean-based
    (inflatable) estimator and prove the composition reddens."""
    return min(_rtt(s) for s in samples) // 2


def estimate(prev_lat, samples):
    """THE ATTESTED-CLOCK DERIVATION: from the ack window, the one-way latency is the MINIMUM RTT // 2 (the
    inflation-proof floor); the published estimate RISES by at most MAX_RISE per update (anti-drip) and FALLS
    freely (an improved ping tightens immediately); the jitter is the bounded spread capped at MAX_JITTER. An
    implausible RTT is REFUSED. Returns a `clockauth.clock` (lat, jitter) — exactly what URDRCLK1 consumes."""
    if type(prev_lat) is not int or prev_lat < 0:
        raise LatencyestError("prev_lat must be a non-negative int")
    _validate_window(samples)
    for s in samples:
        if not _plausible(s):
            raise LatencyestError(f"implausible RTT {_rtt(s)} (must be 0..{MAX_RTT}) — refuse, never fold in")
    lat_raw = _raw_lat(samples)
    lat = min(lat_raw, prev_lat + MAX_RISE)                       # rate-limited RISE, free FALL
    rtts = [_rtt(s) for s in samples]
    jitter = min((max(rtts) - min(rtts)) // 2, MAX_JITTER)
    return CK.clock(lat, jitter)


# ---- the falsifier tools (NOT laws — each a distinct estimator defect) -------------------------
def _estimate_by_mean(prev_lat, samples):
    """THE INFLATION MISTAKE: use the MEAN RTT instead of the minimum — a cheater who delays SOME acks
    inflates the mean (and thus the latency), widening the clock band. The min-floored law does not move."""
    rtts = [_rtt(s) for s in samples]
    lat_raw = (sum(rtts) // len(rtts)) // 2
    lat = min(lat_raw, prev_lat + MAX_RISE)
    jitter = min((max(rtts) - min(rtts)) // 2, MAX_JITTER)
    return CK.clock(lat, jitter)


def _estimate_no_ratelimit(prev_lat, samples):
    """THE DRIP MISTAKE: publish the raw latency with no bound on how fast it may RISE — a client that delays
    every ack jumps its band open in one update. The law clamps the rise to MAX_RISE."""
    rtts = [_rtt(s) for s in samples]
    return CK.clock(min(rtts) // 2, min((max(rtts) - min(rtts)) // 2, MAX_JITTER))


def _estimate_no_plausibility(prev_lat, samples):
    """THE NO-PLAUSIBILITY MISTAKE: fold an implausible RTT (beyond MAX_RTT) straight into the estimate
    instead of refusing it — a single bogus huge sample inflates the latency. The law rejects it."""
    rtts = [max(_rtt(s), 0) for s in samples]
    lat_raw = min(rtts) // 2
    lat = min(lat_raw, prev_lat + MAX_RISE)
    return CK.clock(lat, min((max(rtts) - min(rtts)) // 2, MAX_JITTER))


# ---- the proof-carrying published record (bound to the ack window) ----------------------------
def record_bytes_len():
    return RECORD_BYTES


def samples_digest(samples):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for (sent, recv) in samples:
        hh.update(f"|{sent}:{recv}".encode())
    return hh.hexdigest()


def publish(prev_lat, samples):
    """SEAL the attested clock: a CONSTANT-SHAPE record carrying prev_lat, the derived (lat, jitter), the
    sample count, and a digest BINDING the record to the exact ack window it was derived from. Raises on an
    implausible window (a record is never issued from garbage samples)."""
    lat, jitter = estimate(prev_lat, samples)
    body = bytearray(MAGIC)
    body += _u32(prev_lat) + _u32(lat) + _u32(jitter) + _u32(len(samples))
    body += bytes.fromhex(samples_digest(samples))
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(record):
    if not (type(record) is bytes or type(record) is bytearray):
        raise LatencyestError("a record must be bytes")
    t = bytes(record)
    if len(t) != RECORD_BYTES:
        raise LatencyestError(f"a record must be exactly {RECORD_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise LatencyestError("bad magic — not a URDRLES1 record")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise LatencyestError("digest mismatch — tampered or truncated")
    off = _HEADER
    prev_lat = int.from_bytes(t[off:off + 4], "big"); off += 4
    lat = int.from_bytes(t[off:off + 4], "big"); off += 4
    jitter = int.from_bytes(t[off:off + 4], "big"); off += 4
    n = int.from_bytes(t[off:off + 4], "big"); off += 4
    sdig = t[off:off + DIGEST_BYTES].hex()
    return (prev_lat, lat, jitter, n, sdig)


def read_record(record):
    """The client's view: (prev_lat, lat, jitter, n, samples_digest)."""
    return _parse(record)


def clock_of(record):
    """The attested clock a valid record publishes — feed straight to URDRCLK1."""
    prev_lat, lat, jitter, _n, _s = _parse(record)
    return CK.clock(lat, jitter)


def verify_record(prev_lat, samples, record):
    """THE PROOF-CARRYING CONTRACT: a record is lawful iff it is BYTE-IDENTICAL to a fresh honest publish over
    the SAME ack window. A forged higher latency, or a record presented against a different ack window (whose
    digest differs), fails."""
    try:
        _parse(record)
    except LatencyestError:
        return False
    try:
        return bytes(record) == publish(prev_lat, samples)
    except LatencyestError:
        return False


def forge_clock(record, new_lat):
    """A falsifier tool: rewrite the sealed latency to a larger value (a widened band) and re-seal the
    self-digest. `verify_record` must STILL refuse it — a fresh honest publish over the ack window disagrees.
    Never a law."""
    t = bytearray(record[:-DIGEST_BYTES])
    off = _HEADER + 4                                             # past MAGIC | prev_lat
    t[off:off + 4] = _u32(new_lat)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests ----------------------------------------------------------------------------------
def input_digest(prev_lat, samples):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|prev{prev_lat}".encode())
    hh.update(samples_digest(samples).encode())
    return hh.hexdigest()


def latencyest_digest(name, in_hex, prev_lat, lat, jitter, status):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|i:{in_hex}|p:{prev_lat}|l:{lat}|j:{jitter}|s:{status}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------------
def _win(rtts, base=0):
    """A window of samples with the given RTTs (sent ticks spread so no two collide in the digest)."""
    return [sample(base + i, base + i + r) for i, r in enumerate(rtts)]


def _scene(name, prev_lat, samples):
    try:
        lat, jitter = estimate(prev_lat, samples)
        status = "OK"
    except LatencyestError:
        lat, jitter, status = -1, -1, "REJECT"
    return latencyest_digest(name, input_digest(prev_lat, samples), prev_lat, lat, jitter, status)


def _scene_honest():
    """A steady ack stream (RTT 6) yields the true one-way latency (3) with no jitter."""
    return _scene("honest", 3, _win([6, 6, 6, 6]))


def _scene_inflate():
    """THE MIN-FLOOR: a cheater delays half the acks (RTT 12) but the minimum stays 6, so the latency stays
    at its honest floor (3) — the inflation does not move it (jitter widens to its cap, bounded)."""
    return _scene("inflate", 3, _win([6, 12, 6, 12]))


def _scene_drip():
    """THE RATE LIMIT: every ack is delayed (RTT 10-12, raw latency 5) but from a low prior (2) the published
    estimate may only RISE by MAX_RISE — so it is clamped to 3, not 5."""
    return _scene("drip", 2, _win([10, 10, 10, 12]))


def _scene_improve():
    """FREE FALL: a genuinely improved ping (RTT 4) drops the latency immediately from a high prior (5) to 2 —
    a tighter band is never a cheat, so the fall is not rate-limited."""
    return _scene("improve", 5, _win([4, 4]))


def _scene_implausible():
    """An implausible RTT (100, beyond the max) is REFUSED — never folded into the estimate."""
    return _scene("implausible", 3, _win([6, 100, 6]))


_SCENES = {"honest": _scene_honest, "inflate": _scene_inflate, "drip": _scene_drip,
           "improve": _scene_improve, "implausible": _scene_implausible}
SCENES = ("honest", "inflate", "drip", "improve", "implausible")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_latencyest.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LatencyestError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260725
SWEEP_COUNT = 120


def gen_scenario(r):
    """A random arena: a true one-way latency, an honest and an inflated ack window over it, a drip window,
    and the URDRCLK1 timeline the estimated clock will gate. The static target is hittable at every tick, so
    (as in clockauth) the clock band is the sole discriminator between a legitimate and a backdated view-tick."""
    now = 100
    x1 = r.rng(5, 7)
    true_lat = r.rng(2, 4)                                        # true one-way latency in ticks
    base_rtt = true_lat * 2                                       # the honest round-trip
    honest = _win([base_rtt + r.rng(0, 1) for _ in range(4)])    # RTT ~ base (min stays base_rtt)
    # inflated: minimum stays base_rtt, but half the acks are delayed by +6 (mean rises, min does not)
    inflated = _win([base_rtt, base_rtt + 6, base_rtt, base_rtt + 6])
    drip = _win([base_rtt + 6, base_rtt + 6, base_rtt + 6, base_rtt + 7])   # every ack delayed
    tl = CK._static_timeline(now, x1)
    walls = frozenset({(10, 0)})
    return tl, walls, HB_shooter(), now, x1, true_lat, honest, inflated, drip


def HB_shooter():
    return CK.HB.shooter(0, 0, 1, 0, 400)


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random arenas asserting the MIN-FLOOR (an inflated window's
    estimate equals the honest floor while the mean-based plant inflates it), the RATE LIMIT (a drip window's
    estimate rises at most MAX_RISE while the no-rate-limit plant jumps), the jitter cap, the plausibility
    rejection, the END-TO-END composition (the honest estimator feeding URDRCLK1 REFUSES a backdate that a
    defective estimator's widened band would admit), determinism, and the proof-carrying record. RAISES on the
    first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    floor_seen = drip_seen = implausible_seen = compose_seen = 0
    for s in range(count):
        tl, walls, sh, now, x1, true_lat, honest, inflated, drip = gen_scenario(r)
        # honest convergence + determinism + proof-carrying
        clk = estimate(true_lat, honest)
        if clk != estimate(true_lat, honest):
            raise LatencyestError(f"scenario {s}: estimate is not deterministic")
        rec = publish(true_lat, honest)
        if len(rec) != record_bytes_len():
            raise LatencyestError(f"scenario {s}: the record is not constant-shape")
        if not verify_record(true_lat, honest, rec):
            raise LatencyestError(f"scenario {s}: an honest record failed its own contract")
        if verify_record(true_lat, honest, forge_clock(rec, clk[0] + 2)):
            raise LatencyestError(f"scenario {s}: a forged higher latency verified")
        if clk[1] > MAX_JITTER:
            raise LatencyestError(f"scenario {s}: jitter exceeded its cap")
        # MIN-FLOOR — the inflated window's latency equals the honest floor; the mean plant inflates it
        inflated_lat = estimate(true_lat, inflated)[0]
        if inflated_lat != true_lat:
            raise LatencyestError(f"scenario {s} (seed {seed}): an inflated ack window moved the latency off "
                                  f"the min floor ({inflated_lat} != {true_lat}) — inflation defense broken")
        if _estimate_by_mean(true_lat, inflated)[0] <= inflated_lat:
            raise LatencyestError(f"scenario {s}: the mean plant did not inflate (vacuous)")
        floor_seen += 1
        # RATE LIMIT — the drip window rises at most MAX_RISE from a low prior; the no-ratelimit plant jumps
        low_prior = 0
        drip_lat = estimate(low_prior, drip)[0]
        if drip_lat > low_prior + MAX_RISE:
            raise LatencyestError(f"scenario {s}: the drip rose faster than MAX_RISE")
        if _estimate_no_ratelimit(low_prior, drip)[0] <= drip_lat:
            raise LatencyestError(f"scenario {s}: the no-ratelimit plant did not jump (vacuous)")
        drip_seen += 1
        # PLAUSIBILITY — a garbage RTT is refused by the law, accepted by the plant
        bad = _win([true_lat * 2, MAX_RTT + 5, true_lat * 2])
        try:
            estimate(true_lat, bad)
            raise LatencyestError(f"scenario {s}: an implausible RTT was folded into the estimate")
        except LatencyestError as exc:
            if "implausible" not in str(exc):
                raise
        _estimate_no_plausibility(true_lat, bad)                  # the plant tolerates it (no raise)
        implausible_seen += 1
        # END-TO-END — the honest clock REFUSES a backdate the mean plant's inflated clock ADMITS
        honest_clk = estimate(true_lat, inflated)                 # (true_lat, capped jitter)
        mean_clk = _estimate_by_mean(true_lat, inflated)          # inflated latency
        backdate = (1, x1, 0, now - honest_clk[0] - MAX_JITTER - 1)
        if CK.admit(tl, walls, sh, honest_clk, backdate):
            raise LatencyestError(f"scenario {s} (seed {seed}): the honest estimator admitted a backdate — "
                                  f"the min floor failed to keep the clock band tight")
        if not CK.admit(tl, walls, sh, mean_clk, backdate):
            raise LatencyestError(f"scenario {s}: the mean-inflated clock did not admit the backdate "
                                  f"(vacuous — the composition teeth are toothless)")
        compose_seen += 1
        hh.update(f"|{s}:{samples_digest(honest)}:{inflated_lat}:{drip_lat}".encode())
    if floor_seen == 0 or drip_seen == 0 or implausible_seen == 0 or compose_seen == 0:
        raise LatencyestError(f"NON-VACUITY: floor {floor_seen}, drip {drip_seen}, implausible "
                              f"{implausible_seen}, compose {compose_seen}")
    return {"scenarios": count, "floor_seen": floor_seen, "drip_seen": drip_seen,
            "implausible_seen": implausible_seen, "compose_seen": compose_seen, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_latencyest.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise LatencyestError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except LatencyestError as exc:
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
    print(f"SWEEP: {rep['scenarios']} arenas, floor_seen {rep['floor_seen']}, drip_seen {rep['drip_seen']}, "
          f"implausible_seen {rep['implausible_seen']}, compose_seen {rep['compose_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
