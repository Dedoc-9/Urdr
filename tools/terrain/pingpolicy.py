# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""pingpolicy — THE PING POLICY (URDRPNG1): the scheduling and sample-selection layer feeding the latency
estimator's ack window, organised around ONE invariant. Composition over `latencyest` (over `clockauth`,
`lagcomp`, `hitbox`, `perception`), NO NEW GLYPH — the kernel stays frozen. See `docs/pingpolicy_brief.md`
for the design pass and the D1 §20 glyph ruling.

THE PROBLEM URDRLES1 LEFT DECLARED. The min-floor defense rests on one sentence: the minimum RTT is honest
"as long as ONE true-timed ack lands in the window". URDRLES1 cannot guarantee that — it consumes a window
someone else chose. Worse, its residual was open-ended: a client who delays EVERY ack raises the minimum, and
the estimate may climb MAX_RISE per update, so the band widens without bound GIVEN ENOUGH PATIENCE.

THE INVARIANT (the whole design in one line) — CONDITIONAL MONOTONE DISADVANTAGE: *once a session floor is
established, every lever the client can pull resolves against the client.* Such a client may always make
their own clock band TIGHTER; no strategy makes it WIDER than honest behaviour, beyond one declared constant.
This is the dual of URDRLES1's "rises slowly, falls freely", extended from the estimate to the whole
measurement apparatus, and it is stated as a FALSIFIABLE THEOREM over a strategy space, not as a hope:

    GIVEN a session floor established from a window the client did not pad,
    for every client strategy σ:     reach(σ) ≤ reach(honest) + DRIFT_ALLOWANCE
    and for every NON-TOTAL-DELAY σ: reach(σ) ≤ reach(honest)

where `reach = lat + jitter` is exactly how far back into the lag window URDRCLK1 will let that client claim.

THE PRECONDITION IS LOAD-BEARING, AND ITS FAILURE IS THE RUNG'S HONEST RESIDUAL — THE COLD START. The session
floor is only as honest as the window that SET it. A client who pads EVERY ack from the moment it connects
never establishes an honest floor at all: it records an inflated one and keeps a permanently wider band. That
client is NOT covered by the theorem above, and the gap is real — MEASURED, not hypothesised (see
`cold_start_reach`, the `coldstart` scene, and the sweep's cold-start block, which assert the bound that DOES
hold and keep the residual visible so it cannot be silently "fixed" into vacuity).

WHAT STILL BOUNDS A COLD START (measured, and asserted every sweep): padding beyond the plausibility ceiling
`MAX_RTT` is REFUSED outright (the samples never enter the estimate), so the reach is capped at
`cold_start_ceiling() = MAX_RTT//2 + DRIFT_ALLOWANCE + MAX_JITTER`; and URDRCLK1 clamps the admissible band to
the lag window regardless, so backdating can never exceed `MAX_REWIND` however the floor was set. The cold
start therefore buys a BOUNDED constant, not an unbounded one — but a LARGER one than honest play, which is
strictly weaker than the unconditional claim and is stated as such.

WHY IT IS NOT MERELY UNFIXED. A client padding from connect is INDISTINGUISHABLE, from timing alone, from a
client on a genuinely slow path: at connect the server holds no prior for this client, and refusing the
padded one would refuse the honest laggy one identically. Closing it needs an OUT-OF-BAND prior (a population
baseline for the route, a geo/AS expectation, or a trusted first measurement) — that is the declared
successor, and it is a different kind of evidence, not more of this one.

FOUR LAWS COMPOSE TO IT.
  1. AUTHENTICATED ECHO — each ping carries a server-KEYED nonce (a secret the client never holds); an echo
     citing a nonce the server did not send, or re-citing one already used, is REFUSED. Without this, coverage
     is fakeable: a cheater replays cheap echoes to LOOK responsive while withholding the real samples.
  2. COVERAGE OR REFUSAL — fewer than MIN_SAMPLES authenticated echoes FREEZES the band (the latency may not
     rise, the jitter collapses to 0) and, after STARVE_WINDOWS consecutive failures, REFUSES outright. Silence
     is not missing data; it is a refusal. Withholding echoes can never widen.
  3. THE LOWER-HALF RULE — a delay can only push an RTT UP, never down, so only the FAST HALF of the samples
     is trusted: the jitter is the spread of the lower half. A client who delays half their acks pushes those
     into the upper half, where they are not read — the jitter does not move. (URDRLES1's own jitter is the
     FULL spread; the policy's is strictly tighter, and that tightening is the point.)
  4. THE SESSION FLOOR — the published latency may never exceed `session_min_rtt // 2 + DRIFT_ALLOWANCE`,
     where the session floor is the all-time minimum RTT (monotone non-increasing). A client must play
     honestly to play at all, so their own early true-timed samples PIN them for the rest of the session:
     delaying everything thereafter buys a CONSTANT, never a growing advantage. This converts URDRLES1's
     open-ended residual into a bounded one — the elegance of the rung.

GRADE. MEASURED: the four laws; the ping schedule's coverage (evenly spaced, keyed phase); the bandwidth
economy (the rate falls only on demonstrated stability); the CONDITIONAL monotone-disadvantage theorem over
the strategy space {honest, delay_half, delay_all, drop_half, drop_all, replay, forge}; the COLD-START
RESIDUAL and the ceiling that bounds it; determinism; and the proof-carrying published record. Mechanism: a
fixed-seed 120-client sweep plus the pinned scenes, each with a plant proven to bite first. DECLARED,
honestly: (a) the theorem is CONDITIONAL on an unpadded founding window — the COLD START above is its
measured failure mode, bounded by `cold_start_ceiling()` and the lag window but strictly worse than honest,
and closing it needs an out-of-band prior (the declared successor); (b) the `+ DRIFT_ALLOWANCE` is real — a
total, sustained delay still buys that one constant, and the rung bounds it rather than eliminating it;
(c) the SESSION FLOOR assumes the path does not permanently WORSEN mid-session — a genuine sustained route
degradation beyond the allowance is capped, so that honest player receives LESS lag-compensation than their
network deserves (a deliberate, declared fairness cost, favouring the defender); (d) the LOWER-HALF RULE
under-reads genuinely one-sided upward jitter, so an honest client on a bursty path gets a tighter band than
their network deserves — the same deliberate trade. FALSIFIER: swap in `_step_no_floor` (or
`_full_spread_jitter`) and the sweep must RAISE; if it does not, these claims are void. does_not_show: the
transport that carries the pings; a colluding pair of clients; secret rotation / compromise; cross-placement
(URDRPNG1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # noqa: E402  (LCG for the sweep)
import clockauth as CK                                             # noqa: E402  (the clock we ultimately feed)
import latencyest as LE                                            # noqa: E402  (min-floor + rate-limited rise)

MAGIC = b"URDRPNG1"
DIGEST_BYTES = LE.DIGEST_BYTES

WINDOW = LE.WINDOW                                                # 8 ticks per estimation window
MIN_RATE = 3                                                      # pings/window FLOOR — the stream cannot be thinned
MAX_RATE = 6
MIN_SAMPLES = 3                                                   # authenticated echoes needed to widen at all
STARVE_WINDOWS = 3                                                # consecutive coverage failures before refusal
DRIFT_ALLOWANCE = 1                                               # ticks the latency may exceed the session floor
MAX_JITTER = LE.MAX_JITTER
MAX_RTT = LE.MAX_RTT

R_OK = 0
R_COVERAGE = 10                                                   # starved of authenticated echoes — refuse

# record: MAGIC(8) | rate | lat | jitter | floor | starve | n | reason (7×4) | window(32) | sha(32) = 100
_HEADER = len(MAGIC)
_NFIELDS = 7
RECORD_BYTES = _HEADER + 4 * _NFIELDS + DIGEST_BYTES + DIGEST_BYTES


class PingpolicyError(Exception):
    def __init__(self, message):
        super().__init__(f"PINGPOLICY-REFUSE: {message}")
        self.code = "PINGPOLICY-REFUSE"


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the keyed ping schedule (deterministic for the server, unforgeable for the client) --------
def _keyed(secret, tick):
    return int.from_bytes(hashlib.sha256(MAGIC + secret + b"|" + str(tick).encode()).digest()[:4], "big")


def nonce(secret, tick):
    """The ping's authenticator: a keyed function of the tick. The server reproduces it exactly; a client
    without the secret cannot forge one for a tick it was not sent."""
    return _keyed(secret, tick)


def schedule(secret, win_start, rate):
    """The pings for one window: `rate` of them EVENLY SPACED (maximal coverage for minimal bandwidth) with a
    KEYED PHASE inside the first step, so their placement is not a fixed cadence the client can model."""
    if not (MIN_RATE <= rate <= MAX_RATE):
        raise PingpolicyError(f"rate {rate} outside [{MIN_RATE}, {MAX_RATE}]")
    step = max(WINDOW // rate, 1)
    phase = _keyed(secret, win_start) % step
    return tuple((win_start + phase + i * step, nonce(secret, win_start + phase + i * step))
                 for i in range(rate))


def echo(ping_tick, nonce_val, recv_tick):
    """A client's echo of one ping: which ping it answers, the nonce it carries, and when it came back."""
    for v in (ping_tick, nonce_val, recv_tick):
        if type(v) is not int:
            raise PingpolicyError(f"echo fields must be int, got {v!r}")
    return (ping_tick, nonce_val, recv_tick)


# ---- LAW 1: authenticated echo (coverage cannot be faked) --------------------------------------
def authenticate(secret, win_start, rate, echoes):
    """Accept only echoes that cite a ping the server ACTUALLY SENT, with its correct keyed nonce, ONCE (no
    replay), and with a plausible RTT. Returns `latencyest` samples. Module scope so the falsifiers can plant
    a no-authentication policy and prove the theorem reddens."""
    pings = dict(schedule(secret, win_start, rate))
    seen, samples = set(), []
    for (t, n, recv) in echoes:
        if t not in pings or n != pings[t] or t in seen:
            continue                                              # forged, unsent, or replayed — refuse
        rtt = recv - t
        if not (0 <= rtt <= MAX_RTT):
            continue                                              # implausible — refuse
        seen.add(t)
        samples.append(LE.sample(t, recv))
    return samples


def _authenticate_none(secret, win_start, rate, echoes):
    """THE NO-AUTHENTICATION MISTAKE (a falsifier tool): accept any echo shaped like one, without checking the
    keyed nonce or replay. A cheater then FAKES coverage with replayed echoes while withholding real samples."""
    out = []
    for (t, _n, recv) in echoes:
        rtt = recv - t
        if 0 <= rtt <= MAX_RTT:
            out.append(LE.sample(t, recv))
    return out[:WINDOW]


# ---- LAW 3: the lower-half rule (only the fast half is trusted) --------------------------------
def lower_half_jitter(rtts):
    """The jitter read from the FAST HALF only. A delay can only push an RTT up, so the lower half is the
    honest part of the sample; reading the spread there makes partial delay unable to inflate the band."""
    s = sorted(rtts)
    k = (len(s) + 1) // 2                                         # the lower half, rounded up
    return min((s[k - 1] - s[0]) // 2, MAX_JITTER)


def _full_spread_jitter(rtts):
    """THE FULL-SPREAD MISTAKE (a falsifier tool): read the jitter from the WHOLE spread (URDRLES1's own
    rule). A client who delays half their acks now inflates the jitter — and thus their reach."""
    return min((max(rtts) - min(rtts)) // 2, MAX_JITTER)


# ---- the policy state and its step -------------------------------------------------------------
def state(rate, lat, floor_rtt, starve=0):
    """The per-client policy state: the current ping rate, the published latency, the SESSION FLOOR (all-time
    minimum RTT, monotone non-increasing), and the consecutive-coverage-failure counter."""
    for v in (rate, lat, floor_rtt, starve):
        if type(v) is not int:
            raise PingpolicyError(f"state fields must be int, got {v!r}")
    if not (MIN_RATE <= rate <= MAX_RATE):
        raise PingpolicyError(f"rate {rate} outside [{MIN_RATE}, {MAX_RATE}]")
    if lat < 0 or floor_rtt < 0 or starve < 0:
        raise PingpolicyError("latency, floor and starve must be non-negative")
    return (rate, lat, floor_rtt, starve)


def reach(clk):
    """How far back into the lag window this clock lets the client claim — the single scalar the
    monotone-disadvantage theorem is stated over. Larger = more permissive."""
    return clk[0] + clk[1]


def _adapt(rate, stable):
    """LAW behind the bandwidth economy: scrutiny RISES freely and FALLS slowly. Instability jumps the rate to
    its maximum at once; a demonstrably stable window earns back at most ONE step, never below the floor. A
    client can make us ping MORE, never less."""
    return max(rate - 1, MIN_RATE) if stable else MAX_RATE


def step(secret, st, win_start, echoes, _auth=None, _jit=None):
    """ONE WINDOW of the policy. Authenticate the echoes (law 1); on a coverage deficit freeze the band and
    count toward refusal (law 2); else read the latency through `latencyest` (min floor + rate-limited rise),
    the jitter through the lower-half rule (law 3), and clamp the latency to the SESSION FLOOR + allowance
    (law 4). Returns `(new_state, clock, reason)` — the clock is exactly what URDRCLK1 consumes."""
    auth = _auth or authenticate
    jit = _jit or lower_half_jitter
    rate, lat, floor_rtt, starve = st
    samples = auth(secret, win_start, rate, echoes)
    if len(samples) < MIN_SAMPLES:                                # LAW 2 — silence cannot pay
        starve += 1
        frozen = CK.clock(lat, 0)                                 # no rise, jitter collapsed
        if starve >= STARVE_WINDOWS:
            return (state(MAX_RATE, lat, floor_rtt, starve), frozen, R_COVERAGE)
        return (state(MAX_RATE, lat, floor_rtt, starve), frozen, R_OK)
    rtts = [b - a for (a, b) in samples]
    floor_rtt = min(floor_rtt, min(rtts))                         # LAW 4 — the session floor only ever falls
    new_lat = LE.estimate(lat, samples)[0]                        # min floor + rate-limited rise (URDRLES1)
    new_lat = min(new_lat, floor_rtt // 2 + DRIFT_ALLOWANCE)      # LAW 4 — pinned by your own best moment
    new_jit = jit(rtts)                                           # LAW 3 — the fast half only
    stable = new_jit < MAX_JITTER and new_lat <= lat
    return (state(_adapt(rate, stable), new_lat, floor_rtt, 0), CK.clock(new_lat, new_jit), R_OK)


def _step_no_floor(secret, st, win_start, echoes):
    """THE NO-SESSION-FLOOR MISTAKE (a falsifier tool): let the latency climb MAX_RISE per window forever,
    forgetting the client's own honest early samples. A patient total-delay strategy then widens the band
    without bound — exactly URDRLES1's open residual, left open."""
    rate, lat, floor_rtt, starve = st
    samples = authenticate(secret, win_start, rate, echoes)
    if len(samples) < MIN_SAMPLES:
        return (state(MAX_RATE, lat, floor_rtt, starve + 1), CK.clock(lat, 0), R_OK)
    rtts = [b - a for (a, b) in samples]
    new_lat = LE.estimate(lat, samples)[0]                        # NO session-floor clamp — the bug
    new_jit = lower_half_jitter(rtts)
    return (state(_adapt(rate, new_jit < MAX_JITTER and new_lat <= lat), new_lat,
                  min(floor_rtt, min(rtts)), 0), CK.clock(new_lat, new_jit), R_OK)


def _step_rate_free_fall(secret, st, win_start, echoes, _base=step):
    """THE THINNING MISTAKE (a falsifier tool): collapse the ping rate to the floor after a single quiet
    window instead of earning it back one step at a time — a client can drop scrutiny at will. (`_base` binds
    the honest step at definition time, so swapping this in for `step` cannot self-recurse.)"""
    ns, clk, rs = _base(secret, st, win_start, echoes)
    return (state(MIN_RATE, ns[1], ns[2], ns[3]), clk, rs)


# ---- the proof-carrying published record -------------------------------------------------------
def record_bytes_len():
    return RECORD_BYTES


def window_digest(secret, win_start, rate, echoes):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|w{win_start}|r{rate}".encode())
    for (t, n, recv) in echoes:
        hh.update(f"|{t}:{n}:{recv}".encode())
    return hh.hexdigest()


def publish(secret, st, win_start, echoes):
    """SEAL the window's outcome: a CONSTANT-SHAPE record carrying the rate, the published clock, the session
    floor, the starve counter, the authenticated-sample count and the reason, bound by digest to the EXACT
    ack window it was derived from."""
    ns, clk, reason = step(secret, st, win_start, echoes)
    n = len(authenticate(secret, win_start, st[0], echoes))
    body = bytearray(MAGIC)
    body += _u32(ns[0]) + _u32(clk[0]) + _u32(clk[1]) + _u32(ns[2]) + _u32(ns[3]) + _u32(n) + _u32(reason)
    body += bytes.fromhex(window_digest(secret, win_start, st[0], echoes))
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(record):
    if not (type(record) is bytes or type(record) is bytearray):
        raise PingpolicyError("a record must be bytes")
    t = bytes(record)
    if len(t) != RECORD_BYTES:
        raise PingpolicyError(f"a record must be exactly {RECORD_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise PingpolicyError("bad magic — not a URDRPNG1 record")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise PingpolicyError("digest mismatch — tampered or truncated")
    off = _HEADER
    f = []
    for _ in range(_NFIELDS):
        f.append(int.from_bytes(t[off:off + 4], "big")); off += 4
    return tuple(f) + (t[off:off + DIGEST_BYTES].hex(),)


def read_record(record):
    """(rate, lat, jitter, floor, starve, n_samples, reason, window_digest)."""
    return _parse(record)


def verify_record(secret, st, win_start, echoes, record):
    """THE PROOF-CARRYING CONTRACT: lawful iff BYTE-IDENTICAL to a fresh honest publish over the SAME state
    and ack window. A widened clock, or the record replayed against a different window, fails."""
    try:
        _parse(record)
    except PingpolicyError:
        return False
    try:
        return bytes(record) == publish(secret, st, win_start, echoes)
    except PingpolicyError:
        return False


def forge_widen(record, lat, jitter):
    """A falsifier tool: re-seal the record with a WIDER published band. `verify_record` must still refuse it."""
    t = bytearray(record[:-DIGEST_BYTES])
    off = _HEADER + 4
    t[off:off + 4] = _u32(lat)
    t[off + 4:off + 8] = _u32(jitter)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- the client strategy space (the adversary the theorem quantifies over) ---------------------
STRATEGIES = ("honest", "delay_half", "delay_all", "drop_half", "drop_all", "replay", "forge")
NON_TOTAL_DELAY = ("honest", "delay_half", "drop_half", "drop_all", "replay", "forge")
DELAY = 6                                                         # the ticks a delaying strategy adds


def play(secret, win_start, rate, base_rtt, strat):
    """Generate one window of echoes under a client strategy — the adversary, made explicit and enumerable."""
    pings = schedule(secret, win_start, rate)
    out = []
    for i, (t, n) in enumerate(pings):
        if strat == "drop_all":
            continue
        if strat == "drop_half" and i % 2:
            continue
        if strat == "replay":                                     # re-cite the first nonce everywhere
            out.append(echo(t, pings[0][1], t + base_rtt)); continue
        if strat == "forge":                                      # a nonce the server never issued
            out.append(echo(t, n ^ 0x5A5A5A5A, t + base_rtt)); continue
        d = DELAY if (strat == "delay_all" or (strat == "delay_half" and i % 2)) else 0
        out.append(echo(t, n, t + base_rtt + d))
    return out


def run(secret, st, base_rtt, strat, windows, _step=None):
    """Play `windows` consecutive windows under one strategy; return the final (state, clock, reason)."""
    fn = _step or step
    clk, reason = CK.clock(st[1], 0), R_OK
    for w in range(windows):
        st, clk, reason = fn(secret, st, w * WINDOW, play(secret, w * WINDOW, st[0], base_rtt, strat))
    return st, clk, reason


# ---- digests -----------------------------------------------------------------------------------
def policy_digest(name, secret_hex, base_rtt, strat, rate, lat, jitter, reason):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|s:{secret_hex}|b:{base_rtt}|t:{strat}|r:{rate}|l:{lat}|j:{jitter}|x:{reason}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) ------------------------------------------------------------
SECRET = b"\xA1\x1C\xE0\x9E\x37\x79\xB1\x5A"                      # the server's ping key (never the client's)
SWEEP_WITNESS_SECRET = b"\x5A\xB1\x79\x37\x9E\xE0\x1C\xA1"         # a fixed key for the residual witness


def _scene(name, base_rtt, strat, windows, st0=None):
    st = st0 or state(MAX_RATE, base_rtt // 2, base_rtt)
    fs, clk, reason = run(SECRET, st, base_rtt, strat, windows)
    return policy_digest(name, SECRET.hex(), base_rtt, strat, fs[0], clk[0], clk[1], reason)


def _scene_steady():
    """An honest client on a steady path: the band converges and the ping rate DECAYS to the floor — scrutiny
    is earned back one step at a time, and bandwidth is spent only where it is needed."""
    return _scene("steady", 6, "honest", 4)


def _scene_starve():
    """A client that answers nothing: the band FREEZES (no rise, jitter 0) and after STARVE_WINDOWS the policy
    REFUSES. Silence buys nothing and eventually costs lag-compensation entirely."""
    return _scene("starve", 6, "drop_all", 3)


def _scene_replay():
    """A cheater replays one nonce across the window to FAKE liveness while withholding real samples: the
    authentication accepts only the single genuine echo, so the coverage deficit stands."""
    return _scene("replay", 6, "replay", 2)


def _scene_pinned():
    """THE SESSION FLOOR: an honest opening window records the true floor; the client then delays EVERY ack
    forever. The band widens by at most DRIFT_ALLOWANCE and then STOPS — their own best moment pins them."""
    st = state(MAX_RATE, 3, 6)
    fs, clk, reason = run(SECRET, st, 6, "honest", 1)
    fs, clk, reason = run(SECRET, fs, 6, "delay_all", 6)
    return policy_digest("pinned", SECRET.hex(), 6, "delay_all", fs[0], clk[0], clk[1], reason)


def _scene_halfdelay():
    """THE LOWER-HALF RULE: half the acks are delayed, but the fast half is untouched — the jitter does not
    move, so partial delay buys no extra reach at all."""
    return _scene("halfdelay", 6, "delay_half", 3)


def _scene_coldstart():
    """THE RESIDUAL, pinned as a scene so it is part of the record rather than a footnote: a client that pads
    every ack from connect never founds an honest floor, so it keeps a band WIDER than honest play — the
    theorem's precondition failing. It is still bounded (padding past plausibility is refused, and URDRCLK1
    clamps to the lag window), but this rung does not defeat it; an out-of-band prior is the successor."""
    st = state(MAX_RATE, 3, MAX_RTT)
    fs, clk, reason = run(SECRET, st, 6 + 6, "honest", 5)         # honest SHAPE, uniformly padded RTT
    return policy_digest("coldstart", SECRET.hex(), 12, "cold_pad", fs[0], clk[0], clk[1], reason)


_SCENES = {"steady": _scene_steady, "starve": _scene_starve, "replay": _scene_replay,
           "pinned": _scene_pinned, "halfdelay": _scene_halfdelay, "coldstart": _scene_coldstart}
SCENES = ("steady", "starve", "replay", "pinned", "halfdelay", "coldstart")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_pingpolicy.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PingpolicyError(f"no golden named {name!r}")


# ---- THE MONOTONE-DISADVANTAGE THEOREM (the headline) ------------------------------------------
def strategy_reach(secret, base_rtt, strat, windows, _step=None):
    """The reach a strategy achieves after `windows` windows. A REFUSED policy yields −1: maximally
    restrictive, the least permissive outcome there is."""
    _fs, clk, reason = run(secret, state(MAX_RATE, base_rtt // 2, base_rtt), base_rtt, strat, windows, _step)
    return -1 if reason == R_COVERAGE else reach(clk)


def monotone_disadvantage(secret, base_rtt, windows, _step=None):
    """THE THEOREM, evaluated — CONDITIONAL on a session floor established from an unpadded window (the
    initial state below seeds exactly that). No strategy out-reaches honest play by more than
    DRIFT_ALLOWANCE, and no non-total-delay strategy out-reaches it at all. Returns (holds, honest_reach,
    {strat: reach}). It says NOTHING about a client that pads from connect — see `cold_start_reach`."""
    reaches = {s: strategy_reach(secret, base_rtt, s, windows, _step) for s in STRATEGIES}
    h = reaches["honest"]
    holds = all(reaches[s] <= h + DRIFT_ALLOWANCE for s in STRATEGIES) \
        and all(reaches[s] <= h for s in NON_TOTAL_DELAY)
    return holds, h, reaches


# ---- THE COLD-START RESIDUAL (the theorem's precondition failing — measured, not hypothesised) --
def cold_start_ceiling():
    """The bound that DOES hold when no honest founding window ever existed: padding beyond `MAX_RTT` is
    refused outright, so the latency cannot exceed `MAX_RTT//2 + DRIFT_ALLOWANCE` and the reach cannot exceed
    that plus the jitter cap. URDRCLK1 additionally clamps the band to the lag window, so backdating is capped
    at MAX_REWIND however the floor was set."""
    return MAX_RTT // 2 + DRIFT_ALLOWANCE + MAX_JITTER


def cold_start_reach(secret, base_rtt, pad, windows):
    """A client that pads EVERY ack by `pad` from the moment it connects — so the session floor is never
    honestly founded. Returns its reach, or −1 if the padding is implausible and the samples are refused.
    This is the theorem's precondition failing, kept as a first-class MEASUREMENT so the residual stays
    visible and cannot be quietly optimised away."""
    st = state(MAX_RATE, base_rtt // 2, MAX_RTT)                  # no prior: the floor is unknown at connect
    clk, reason = CK.clock(st[1], 0), R_OK
    for w in range(windows):
        st, clk, reason = step(secret, st, w * WINDOW,
                               play(secret, w * WINDOW, st[0], base_rtt + pad, "honest"))
    return -1 if reason == R_COVERAGE else reach(clk)


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260725
SWEEP_COUNT = 120


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random clients (secret, true path RTT, horizon), each asserting
    the MONOTONE-DISADVANTAGE THEOREM over the whole strategy space, the authentication (replay/forge yield no
    coverage), the session-floor pin (total delay is bounded, and the no-floor plant escapes it), the
    lower-half rule (partial delay does not move the jitter, and the full-spread plant lets it), the rate
    floor and its one-step decay (the free-fall plant thins the stream), determinism, and the proof-carrying
    record. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    theorem_seen = auth_seen = floor_seen = half_seen = rate_seen = cold_seen = 0
    for s in range(count):
        secret = bytes([r.rng(0, 255) for _ in range(8)])
        base_rtt = 2 * r.rng(2, 4)                                # an even, plausible true round-trip
        windows = r.rng(3, 6)
        st0 = state(MAX_RATE, base_rtt // 2, base_rtt)
        # THE THEOREM
        holds, h, reaches = monotone_disadvantage(secret, base_rtt, windows)
        if not holds:
            raise PingpolicyError(f"scenario {s} (seed {seed}): MONOTONE DISADVANTAGE FALSIFIED — honest "
                                  f"reach {h}, strategies {reaches}")
        theorem_seen += 1
        # determinism + proof-carrying record
        ech = play(secret, 0, MAX_RATE, base_rtt, "honest")
        if step(secret, st0, 0, ech) != step(secret, st0, 0, ech):
            raise PingpolicyError(f"scenario {s}: the policy step is not deterministic")
        rec = publish(secret, st0, 0, ech)
        if len(rec) != record_bytes_len():
            raise PingpolicyError(f"scenario {s}: the record is not constant-shape")
        if not verify_record(secret, st0, 0, ech, rec):
            raise PingpolicyError(f"scenario {s}: an honest record failed its own contract")
        if verify_record(secret, st0, 0, ech, forge_widen(rec, base_rtt, MAX_JITTER)):
            raise PingpolicyError(f"scenario {s}: a forged widened band verified")
        # LAW 1 — replay and forgery earn no coverage; the no-auth plant hands it to them
        for bad in ("replay", "forge"):
            e = play(secret, 0, MAX_RATE, base_rtt, bad)
            if len(authenticate(secret, 0, MAX_RATE, e)) >= MIN_SAMPLES:
                raise PingpolicyError(f"scenario {s}: {bad} achieved coverage — authentication failed")
            if len(_authenticate_none(secret, 0, MAX_RATE, e)) < MIN_SAMPLES:
                raise PingpolicyError(f"scenario {s}: the no-auth plant did not hand {bad} coverage (vacuous)")
        auth_seen += 1
        # LAW 4 — the session floor pins total delay; the no-floor plant escapes it over the same horizon
        pinned = strategy_reach(secret, base_rtt, "delay_all", windows)
        loose = strategy_reach(secret, base_rtt, "delay_all", windows, _step=_step_no_floor)
        if pinned > h + DRIFT_ALLOWANCE:
            raise PingpolicyError(f"scenario {s}: the session floor failed to pin a total delay")
        if loose <= pinned:
            raise PingpolicyError(f"scenario {s}: the no-floor plant did not escape the pin (vacuous)")
        floor_seen += 1
        # LAW 3 — the lower-half rule holds the jitter; the full-spread plant lets partial delay inflate it
        e = play(secret, 0, MAX_RATE, base_rtt, "delay_half")
        rtts = [b - a for (a, b) in authenticate(secret, 0, MAX_RATE, e)]
        if lower_half_jitter(rtts) != 0:
            raise PingpolicyError(f"scenario {s}: partial delay moved the lower-half jitter")
        if _full_spread_jitter(rtts) <= lower_half_jitter(rtts):
            raise PingpolicyError(f"scenario {s}: the full-spread plant did not inflate (vacuous)")
        half_seen += 1
        # the rate floor and its one-step decay; the free-fall plant thins the stream in one window
        st1, _c, _r = step(secret, state(MAX_RATE, base_rtt // 2, base_rtt), 0, ech)
        if st1[0] < MIN_RATE or st1[0] < MAX_RATE - 1:
            raise PingpolicyError(f"scenario {s}: the ping rate fell faster than one step")
        st2, _c2, _r2 = _step_rate_free_fall(secret, state(MAX_RATE, base_rtt // 2, base_rtt), 0, ech)
        if st2[0] >= st1[0]:
            raise PingpolicyError(f"scenario {s}: the free-fall plant did not thin the stream (vacuous)")
        rate_seen += 1
        # THE COLD-START RESIDUAL — the theorem's precondition failing. Assert the bound that DOES hold:
        # within plausibility the reach is capped by the ceiling; beyond it the samples are refused outright.
        pad = 2 * r.rng(1, 3)
        cs = cold_start_reach(secret, base_rtt, pad, windows)
        if cs > cold_start_ceiling():
            raise PingpolicyError(f"scenario {s} (seed {seed}): a cold start reached {cs}, past the "
                                  f"plausibility ceiling {cold_start_ceiling()}")
        if cold_start_reach(secret, base_rtt, MAX_RTT + 4, windows) != -1:
            raise PingpolicyError(f"scenario {s}: an implausibly padded cold start was not refused")
        cold_seen += 1
        hh.update(f"|{s}:{h}:{pinned}:{loose}:{st1[0]}:{cs}".encode())
    # THE RESIDUAL MUST STAY VISIBLE: a fixed, deterministic witness that a cold start really does out-reach
    # the conditional theorem's bound. If this ever stops holding, the honest boundary has silently become
    # vacuous (or the rung genuinely improved) — either way the claim must be re-graded, not left standing.
    wit_h = strategy_reach(SWEEP_WITNESS_SECRET, 6, "honest", 5)
    wit_cold = cold_start_reach(SWEEP_WITNESS_SECRET, 6, 6, 5)
    if not wit_cold > wit_h + DRIFT_ALLOWANCE:
        raise PingpolicyError(f"the cold-start residual is no longer witnessed (cold {wit_cold} vs honest "
                              f"{wit_h} + {DRIFT_ALLOWANCE}) — the declared boundary has gone vacuous and the "
                              f"claim must be re-graded")
    if theorem_seen == 0 or auth_seen == 0 or floor_seen == 0 or half_seen == 0 or rate_seen == 0 \
            or cold_seen == 0:
        raise PingpolicyError(f"NON-VACUITY: theorem {theorem_seen}, auth {auth_seen}, floor {floor_seen}, "
                              f"half {half_seen}, rate {rate_seen}, cold {cold_seen}")
    return {"scenarios": count, "theorem_seen": theorem_seen, "auth_seen": auth_seen,
            "floor_seen": floor_seen, "half_seen": half_seen, "rate_seen": rate_seen,
            "cold_seen": cold_seen, "witness_cold": wit_cold, "witness_honest": wit_h,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_pingpolicy.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise PingpolicyError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except PingpolicyError as exc:
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
    holds, h, reaches = monotone_disadvantage(SECRET, 6, 5)
    print(f"THEOREM holds={holds} honest={h} {reaches}")
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} clients, theorem {rep['theorem_seen']}, auth {rep['auth_seen']}, "
          f"floor {rep['floor_seen']}, half {rep['half_seen']}, rate {rep['rate_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
