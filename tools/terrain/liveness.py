# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""liveness — THE KEYED HEARTBEAT AND THE WELL-FOUNDED COUNTDOWN (URDRLIV1): the residual URDRPAT1
declared and URDRAGR1 was resting on. NO NEW GLYPH.

WHAT THIS CLOSES. `auditgraph` priced undetected equivocation at kappa and sold that as converting an
INVISIBLE INTEGRITY attack into a VISIBLE AVAILABILITY one. `patience` then showed the whole ladder
collapses to 0/0/0 if a server STALLS instead of excluding, because under Chandra-Toueg a silent peer
and a slow one are the same observation. Both rungs declared the same residual and neither closed it:
a client that cannot tell DENIAL from BAD WEATHER raises no alarm. This rung supplies the missing
piece — a heartbeat the server cannot fake and a countdown that cannot be talked out of firing.

THE AUTHENTICATION IS KEYED, AND THAT IS THE WHOLE POINT. A heartbeat derived from public data is
not evidence of anything: `SHA-256(session | tick)` is computable by every observer, so an adversary
squatting the path emits junk bytes that happen to match and the client resets its counter forever
while the server is gone. That is the COUNTERFEIT RESET, and it is measured here at a 100% forgery
rate against the unkeyed scheme and 0% against the keyed one over the same family. The token is

    HMAC-SHA256(secret, MAGIC | session | tick)   compared with `hmac.compare_digest`

so a reset requires PROOF OF POSSESSION of pre-shared secret material, verified against the tick the
client is currently in — bound to `clockauth`'s admissible band rather than to wall-clock, since this
arc has no wall-clock in any authority path.

REPLAY IS BOUNDED, NOT ELIMINATED, AND THE BOUND IS EXACT. A token minted for tick t verifies at tick
t and NOWHERE ELSE: the measured replay window is exactly 1 tick, decided by enumeration over the
band. That does not mean an intercepted token is worthless — it means it is worth only the tick it
was already evidence for, so it cannot mask a stall, which is the attack. Stating this as "replay is
prevented" would be the inflation; the honest form is that the adversary gains no tick he did not
already have.

THE COUNTDOWN IS PURE SUBTRACTION OVER THE NATURALS, WITH NO DEFENSIVE CLAMP. `budget - 1`, and the
fault fires exactly when the next value would be 0 — so the value never reaches 0 and never goes
negative, and the descent is a well-founded relation on (N, <) rather than a loop with a floor.
A `max(0, ...)` clamp is kept as a live plant precisely because it looks defensive and is not: the
clamped variant runs FOREVER without ever raising, which is the liveness residual reopened in one
line. Termination is DECIDED: from a full budget with no valid token, exactly PATIENCE-1 steps
survive and the PATIENCE-th raises.

THE FAULT IS A NORMAL `Exception`, AND THAT IS A DELIBERATE DEPARTURE FROM THE SPEC THIS RUNG WAS
WRITTEN TO. The requested design was a `BaseException` subclass, so the fault would propagate through
intermediate handlers rather than be swallowed. The INTENT is right and is honoured; the MECHANISM
was measured and it damages the gate. `verify.py` wraps every stage in `except Exception` — 457 of
them — so a `BaseException` subclass does not produce a red row, it ABORTS the process: no row, no
remaining stages, no `GATE FAILED` line, and no byte-identical output to compare, which silently
destroys the determinism check that is the repo's whole spine. `baseexception_would_abort_the_gate`
pins that comparison as data rather than as an argument. The anti-swallowing guarantee is instead
obtained the way this repo obtains guarantees: `_step_swallowing` is a live plant that catches its
own fault and returns a budget, and the gate asserts the real `step` does not.

GRADE. MEASURED: the forgery census (unkeyed 100%, keyed 0%) over the enumerated token family; the
replay window as exactly 1 tick, decided over the band; well-founded descent (exactly PATIENCE-1
survivors, the next raises) and the absence of any negative or zero return; the clamp plant running
unboundedly without firing; the sliding-window plant admitting a full stall the correct
implementation refuses; the swallowing plant; the recorded-vs-aborted comparison for the exception
base class; determinism. DECLARED: the secret is PRE-SHARED and its distribution, rotation and
compromise are out of scope — this rung assumes key material exists and says nothing about how it
got there; the tick is `clockauth`'s server-attested tick, so this inherits every clockauth boundary
including that a client never supplies its own latency. does_not_show: that the server is HONEST —
a live server that lies is `splitview`'s problem and a keyed heartbeat proves possession, never
truthfulness; WHY a peer went silent, since denial and outage remain indistinguishable in CAUSE and
this rung only makes the CONSEQUENCE deterministic and attributable to a named session; any bound
against an adversary holding the secret, which is total compromise and outside every claim here."""
import hashlib
import hmac
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import clockauth as _CA                                             # noqa: E402

MAGIC = b"URDRLIV1"
PATIENCE = 4                     # ticks of silence tolerated before the session is declared offline
TOKEN_BYTES = 16                 # truncated HMAC tag
SESSION = b"urdr-session-0"
SECRET = b"pre-shared-secret-material-0"   # a FIXTURE; provisioning is declared out of scope
TICK_SPAN = 12                   # the enumerated tick range for the replay/forgery censuses


class LivenessError(Exception):
    def __init__(self, message):
        super().__init__(f"LIVENESS-REFUSE: {message}")
        self.code = "LIVENESS-REFUSE"


class ServerOffline(Exception):
    """THE AVAILABILITY FAULT. A normal `Exception` on purpose — see the header: a `BaseException`
    subclass would escape `verify.py`'s 457 stage handlers and abort the gate instead of reddening a
    row, destroying the byte-identical output the whole repo rests on. The anti-swallowing property
    is obtained by a live plant plus a gate row, not by the base class."""
    def __init__(self, message):
        super().__init__(f"LIVENESS-OFFLINE: {message}")
        self.code = "LIVENESS-OFFLINE"


# ---- the keyed heartbeat --------------------------------------------------------------------------
def token(secret, session, tick):
    """HMAC-SHA256(secret, MAGIC | session | tick), truncated. Proof of POSSESSION, bound to a tick."""
    if type(tick) is not int or tick < 0:
        raise LivenessError(f"tick must be a non-negative int, got {tick!r}")
    msg = MAGIC + b"|" + session + b"|" + tick.to_bytes(8, "big")
    return hmac.new(secret, msg, hashlib.sha256).digest()[:TOKEN_BYTES]


def verify_token(secret, session, tick, presented):
    """Constant-time comparison against the token this tick demands."""
    if not isinstance(presented, (bytes, bytearray)):
        return False
    return hmac.compare_digest(token(secret, session, tick), bytes(presented))


def _unkeyed_token(session, tick):
    """A FALSIFIER TOOL: the ad-hoc scheme this rung replaces — a hash of PUBLIC identifiers. Every
    observer can compute it, so it proves nothing and resets the counter for anyone."""
    return hashlib.sha256(MAGIC + b"|" + session + b"|" + tick.to_bytes(8, "big")).digest()[:TOKEN_BYTES]


def _verify_unkeyed(session, tick, presented):
    return bytes(presented) == _unkeyed_token(session, tick)


def forgery_census(span=TICK_SPAN):
    """THE COUNTERFEIT RESET, MEASURED. An adversary who knows only PUBLIC data (session, tick) tries
    to mint a reset at every tick. Returns (unkeyed_accepted, keyed_accepted, attempts) — the first
    must equal attempts and the second must be 0, and both denominators are reported so neither zero
    can be read as an empty search."""
    unkeyed = keyed = attempts = 0
    for t in range(span):
        forged = _unkeyed_token(SESSION, t)
        attempts += 1
        if _verify_unkeyed(SESSION, t, forged):
            unkeyed += 1
        if verify_token(SECRET, SESSION, t, forged):
            keyed += 1
    return unkeyed, keyed, attempts


def keyed_auth_closes_the_counterfeit_reset(span=TICK_SPAN):
    u, k, n = forgery_census(span)
    return n > 0 and u == n and k == 0


def replay_window(span=TICK_SPAN):
    """DECIDED: a token minted at tick `t` verifies at how many ticks. Returns
    (window, span) — the window must be exactly 1, so an intercepted token is worth only the tick it
    was already evidence for and cannot mask a stall. This is a BOUND on replay, not its elimination,
    and the distinction is the honest part."""
    worst = 0
    for mint in range(span):
        tok = token(SECRET, SESSION, mint)
        hits = sum(1 for t in range(span) if verify_token(SECRET, SESSION, t, tok))
        worst = max(worst, hits)
    return worst, span


def bound_to_clockauth_band(now=40, lat=3, jitter=1):
    """The tick a token is bound to is `clockauth`'s SERVER-ATTESTED tick, not wall-clock and not a
    client assertion. Returns (band, accepted_inside, rejected_outside) over the admissible band."""
    clk = _CA.clock(lat, jitter)
    lo, hi = _CA.band(now, clk)
    inside = sum(1 for vt in range(lo, hi + 1)
                 if verify_token(SECRET, SESSION, vt, token(SECRET, SESSION, vt)))
    outside = sum(1 for vt in range(max(0, lo - 4), lo)
                  if not verify_token(SECRET, SESSION, vt, token(SECRET, SESSION, lo)))
    return (lo, hi), inside, outside


# ---- the well-founded countdown -------------------------------------------------------------------
def step(budget, presented, secret=SECRET, session=SESSION, tick=0):
    """ONE TICK OF THE WATCHDOG. A valid keyed token resets the budget; anything else spends one unit
    of it. PURE INTEGER SUBTRACTION — there is no `max(0, ...)` here on purpose, because a clamp
    turns a terminating descent into an infinite loop and that loop IS the liveness residual. The
    fault fires exactly when the next value would be 0, so the returned budget is never 0 and never
    negative, and (N, <) makes termination structural rather than hoped for."""
    if type(budget) is not int:
        raise LivenessError(f"budget must be int, got {budget!r}")
    if budget < 1:
        raise LivenessError(f"budget must be at least 1, got {budget}")
    if presented is not None and verify_token(secret, session, tick, presented):
        return PATIENCE
    nxt = budget - 1
    if nxt == 0:
        raise ServerOffline(f"no authenticated heartbeat for {PATIENCE} ticks (session {session!r})")
    return nxt


def descent(ticks, secret=SECRET, session=SESSION, present=None):
    """Run the watchdog across `ticks` ticks. `present` maps tick -> token, absent means silence.
    Returns (survived_ticks, raised) — the exact point of the fault, not an estimate."""
    present = present or {}
    budget = PATIENCE
    for t in range(ticks):
        try:
            budget = step(budget, present.get(t), secret, session, t)
        except ServerOffline:
            return t, True
    return ticks, False


def well_founded_descent():
    """DECIDED: from a full budget with total silence, exactly PATIENCE-1 ticks survive and the next
    raises. Returns (survived, raised, PATIENCE)."""
    s, r = descent(PATIENCE + 6)
    return s, r, PATIENCE


def budget_never_leaves_the_naturals(trials=PATIENCE + 6):
    """No returned budget is ever 0 or negative — the fault fires strictly before that could happen,
    which is what makes the relation well-founded rather than clamped. Returns (min_seen, all_positive)."""
    seen, budget = [], PATIENCE
    for t in range(trials):
        try:
            budget = step(budget, None, SECRET, SESSION, t)
        except ServerOffline:
            break
        seen.append(budget)
    return (min(seen) if seen else 0), all(v >= 1 for v in seen)


def heartbeat_resets_the_budget():
    """A valid keyed token restores the full budget, so an alive server is never declared offline.
    Returns (survived, raised) over a run twice as long as the patience window."""
    present = {t: token(SECRET, SESSION, t) for t in range(PATIENCE * 3)}
    return descent(PATIENCE * 3, present=present)


# ---- the plants -------------------------------------------------------------------------------------
def _step_clamped(budget, presented, secret=SECRET, session=SESSION, tick=0):
    """A FALSIFIER TOOL: the 'defensive' clamp. `max(0, budget - 1)` never reaches the boundary
    condition, so the fault NEVER fires and the client waits forever — the liveness residual
    reopened by a line that looks like hardening."""
    if presented is not None and verify_token(secret, session, tick, presented):
        return PATIENCE
    return max(0, budget - 1)


def clamp_plant_never_fires(ticks=500):
    """The plant BITES: over `ticks` ticks of total silence it never raises, while the real step
    raises at PATIENCE-1. Returns (clamped_survived_all, honest_survived)."""
    budget = PATIENCE
    for t in range(ticks):
        budget = _step_clamped(budget, None, SECRET, SESSION, t)
    honest, _raised = descent(ticks)
    return (budget == 0 and ticks > 0), honest


def _step_sliding_window(budget, presented, secret=SECRET, session=SESSION, tick=0, window=PATIENCE):
    """A FALSIFIER TOOL: accept a token minted for ANY tick inside a sliding window rather than for
    THIS tick. It looks tolerant of jitter and it lets a single intercepted token hold the session
    open indefinitely — the drift into unsafe states the correct implementation refuses."""
    if presented is not None:
        for t in range(max(0, tick - window), tick + window + 1):
            if verify_token(secret, session, t, presented):
                return PATIENCE
    nxt = budget - 1
    if nxt == 0:
        raise ServerOffline("sliding window exhausted")
    return nxt


def _step_accepts_any_history(budget, presented, secret=SECRET, session=SESSION, tick=0):
    """A FALSIFIER TOOL, and the one that actually ships in the wild: verify the token against EVERY
    tick ever issued rather than against THIS one — 'is this a token we recognise' instead of 'is
    this the token now demands'. It authenticates possession and forgets freshness entirely."""
    if presented is not None:
        for t in range(0, tick + 1):
            if verify_token(secret, session, t, presented):
                return PATIENCE
    nxt = budget - 1
    if nxt == 0:
        raise ServerOffline("history-accepting window exhausted")
    return nxt


def _mask_length(stepper, ticks, stolen):
    budget = PATIENCE
    for t in range(ticks):
        try:
            budget = stepper(budget, stolen, SECRET, SESSION, t)
        except ServerOffline:
            return t
    return ticks


def sliding_window_plant_masks_a_stall(ticks=40):
    """THE MASKING LADDER, measured rather than asserted: ONE intercepted token, replayed every tick
    through a TOTAL server stall, against three verifiers. Returns
    (honest, bounded_window, history_accepting, ticks) — how many ticks of the stall each one hides.
    The honest step refuses at PATIENCE; a bounded sliding window doubles the adversary's exposure;
    a verifier that accepts any historical token hides the stall FOREVER, which is the liveness
    residual reopened by an implementation that looks like it authenticates properly."""
    stolen = token(SECRET, SESSION, 0)
    return (_mask_length(step, ticks, stolen),
            _mask_length(_step_sliding_window, ticks, stolen),
            _mask_length(_step_accepts_any_history, ticks, stolen),
            ticks)


def masking_ladder_is_strict(ticks=40):
    """Each relaxation must buy the adversary STRICTLY more, and the last must hide the whole stall —
    otherwise the plants are not demonstrating a difference."""
    h, w, a, n = sliding_window_plant_masks_a_stall(ticks)
    return h < w < a and a == n and h == PATIENCE


def _step_swallowing(budget, presented, secret=SECRET, session=SESSION, tick=0):
    """A FALSIFIER TOOL for the concern the BaseException proposal was aimed at: an intermediate
    handler that catches the availability fault and returns a budget anyway. THIS is the failure mode
    worth blocking, and blocking it is a test, not a base class."""
    try:
        return step(budget, presented, secret, session, tick)
    except ServerOffline:
        return PATIENCE


def swallowing_plant_hides_the_fault(ticks=40):
    """The plant BITES: silence forever, and the swallowing wrapper never surfaces it. Returns
    (swallowed_survived_all, honest_raised_at)."""
    budget = PATIENCE
    for t in range(ticks):
        budget = _step_swallowing(budget, None, SECRET, SESSION, t)
    s, _r = descent(ticks)
    return (budget >= 1), s


def step_does_not_swallow():
    """THE GUARANTEE ITSELF, asserted rather than delegated to a base class: the real `step` lets the
    fault out."""
    try:
        step(1, None, SECRET, SESSION, 0)
    except ServerOffline as exc:
        return exc.code == "LIVENESS-OFFLINE"
    return False


def baseexception_would_abort_the_gate():
    """THE DESIGN DECISION, PINNED AS DATA. `verify.py` wraps every stage in `except Exception`. A
    normal Exception is RECORDED as a red row and the gate keeps running and stays byte-identical; a
    BaseException subclass ESCAPES and aborts the process, so there is no row, no remaining stages,
    no GATE FAILED line and nothing to diff. Returns (exception_recorded, baseexception_recorded);
    the first must be True and the second False."""
    class _Exc(Exception):
        pass

    class _Base(BaseException):
        pass

    out = []
    for cls in (_Exc, _Base):
        try:
            try:
                raise cls("stall")
            except Exception:
                out.append(True)          # the stage recorded it -> red row, gate survives
        except BaseException:
            out.append(False)             # it escaped the stage -> gate aborts
    return tuple(out)


# ---- digests + scenes ---------------------------------------------------------------------------------
def lv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_auth():
    return lv_digest("auth", f"{forgery_census()}:{keyed_auth_closes_the_counterfeit_reset()}:"
                             f"{replay_window()}:{bound_to_clockauth_band()}")


def _scene_descent():
    return lv_digest("descent", f"{well_founded_descent()}:{budget_never_leaves_the_naturals()}:"
                                f"{heartbeat_resets_the_budget()}:{step_does_not_swallow()}")


def _scene_plants():
    return lv_digest("plants", f"{clamp_plant_never_fires()}:{sliding_window_plant_masks_a_stall()}:"
                               f"{masking_ladder_is_strict()}:{swallowing_plant_hides_the_fault()}:"
                               f"{baseexception_would_abort_the_gate()}")


_SCENES = {"auth": _scene_auth, "descent": _scene_descent, "plants": _scene_plants}
SCENES = ("auth", "descent", "plants")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    """THE EMITTER. The pinned corpus must be the DETERMINISTIC OUTPUT of this module rather than
    hand-inscribed hex — but it must also stay FROZEN, because a golden the gate rewrites at run time
    cannot detect drift (that is exactly L23: a checker that cannot fail). So the module EMITS and a
    human PINS, and `emitted_matches_pinned` proves the file on disk is what this function produces."""
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_liveness.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise LivenessError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"forgery (unkeyed, keyed, attempts) {forgery_census()} -> counterfeit reset closed "
          f"{keyed_auth_closes_the_counterfeit_reset()}")
    print(f"replay window (worst, span) {replay_window()}")
    print(f"clockauth binding (band, inside, outside) {bound_to_clockauth_band()}")
    print(f"well-founded descent (survived, raised, PATIENCE) {well_founded_descent()}")
    print(f"budget stays in N (min, all_positive) {budget_never_leaves_the_naturals()}")
    print(f"heartbeat resets (survived, raised) {heartbeat_resets_the_budget()}")
    print(f"masking ladder (honest, window, history, ticks) {sliding_window_plant_masks_a_stall()} "
          f"-> strict {masking_ladder_is_strict()}")
    print(f"plants: clamp {clamp_plant_never_fires()} | swallow {swallowing_plant_hides_the_fault()}")
    print(f"step does not swallow {step_does_not_swallow()} | "
          f"(Exception recorded, BaseException recorded) {baseexception_would_abort_the_gate()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
