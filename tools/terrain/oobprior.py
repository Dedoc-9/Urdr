# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""oobprior — THE OUT-OF-BAND PRIOR (URDROOB1): close URDRPNG1's declared COLD-START residual with evidence
the judged client does not control. Composition over `pingpolicy` (over `latencyest`, `clockauth`, `lagcomp`,
`hitbox`, `perception`), NO NEW GLYPH — the kernel stays frozen. See `docs/oobprior_brief.md` for the design
pass and the D1 §20 glyph ruling.

THE PROBLEM URDRPNG1 LEFT DECLARED. URDRPNG1's monotone-disadvantage theorem is CONDITIONAL on a session
floor founded on a window the client did not pad. A client that pads EVERY ack from the moment it CONNECTS
never founds an honest floor: it records an inflated one and keeps a permanently wider band. URDRPNG1 named
why it could not close this itself — a cold-start padder is INDISTINGUISHABLE, FROM TIMING ALONE, from a
client on a genuinely slow path, because at connect the server holds no prior for that client and refusing the
padded one would refuse the honest laggy one identically. The missing ingredient is not more timing evidence;
it is evidence OF A DIFFERENT KIND.

THE THESIS — A RULER THE JUDGED PARTY CANNOT TOUCH. Other clients on the same route have already founded
honest session floors. Their floors are a reference for what that route costs, and the client being judged
does not control them. So the founding floor of a new client is capped by its COHORT: `admissible =
min(claimed, cohort_reference + TOLERANCE)`. A padder can still claim what it likes; the claim is simply not
believed past what its peers demonstrate.

THE NEUTRAL-RULER RULE IS THE WHOLE DESIGN, AND IT IS STRUCTURAL. `cohort_reference(observations, cohort_key,
exclude_client)` CANNOT RECEIVE the judged client's own observation — the exclusion is in the function, not in
a comment. If a client's own samples fed the baseline it is then measured against, the metric would be built
from the very quantity the adversary optimises: circular, and the cap would be theatre.

EXACTLY WHAT THE EXCLUSION BUYS, MEASURED (and NOT more — this rung's first draft assumed more and was
corrected before landing). Against a SINGLE inflated self-observation the exclusion is belt-and-braces: the
robust median already absorbs it, and reference and plant agree. Where the exclusion is LOAD-BEARING is
SELF-SYBIL — a client flooding the pool with many inflated observations under its OWN id: the exclusion drops
every one of them and the reference is UNMOVED, while `_reference_including_self` is dragged from 6 to 16 on
the reference cohort. What the exclusion does NOT buy is protection from OTHER-SYBIL (many DISTINCT fake
identities), which moves the median exactly as an honest majority would — that is the declared residual below,
and it needs an identity layer, not a better statistic.

WHY A ROBUST STATISTIC, AND WHY A COHORT RATHER THAN A CONSTANT. The reference is the lower MEDIAN of peer
floors, so a MINORITY of padded peers cannot move it (the breakdown point is measured, not assumed — the
`_reference_by_mean` plant shows a single extreme outlier moving a mean). And it is per-ROUTE rather than one
global number precisely so that an HONEST SLOW client whose peers are also slow is NOT capped: the cohort
encodes what that path costs, so slowness corroborated by peers is believed. That is the property that keeps
the prior from becoming a tax on distant players.

GRADE. MEASURED: the leave-one-out neutral-ruler invariance; the cold-start cap and the reach reduction it
buys (measured against URDRPNG1 with no prior); the honest-slow-cohort exemption; the insufficient-cohort
refusal to invent a reference; minority-poisoning robustness and the breakdown point; determinism; and the
proof-carrying founding record. Mechanism: a fixed-seed 120-cohort sweep plus pinned scenes, each with a plant
proven to bite first. DECLARED, honestly: (a) THE PRIOR IS ONLY AS HONEST AS THE COHORT — a MAJORITY-poisoned
cohort (sybil or collusion on one route) moves the reference, and this rung does NOT defeat that; it is
measured and witnessed, and the successor is identity/sybil cost, which is again a different KIND of evidence;
(b) COHORT ASSIGNMENT is server-derived from the connection, but a client that can change apparent route (VPN,
relay) chooses which baseline it is judged against — declared, not solved; (c) BOOTSTRAP — below MIN_COHORT
founded peers there is NO prior and the rung falls back to URDRPNG1 alone, cold start and all, rather than
inventing a reference from too little evidence; (d) an honest slow client in a FAST cohort is capped and
under-compensated — the same deliberate fairness trade the session floor makes, favouring the defender.
FALSIFIER: swap in `_reference_including_self` (or `_reference_by_mean`, or `_found_no_cap`) and the sweep must
RAISE; if it does not, these claims are void. does_not_show: the transport; the identity layer that would make
cohorts sybil-resistant; cross-placement (URDROOB1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                            # noqa: E402  (LCG for the sweep)
import clockauth as CK                                             # noqa: E402
import pingpolicy as PP                                            # noqa: E402  (the policy whose cold start we close)

MAGIC = b"URDROOB1"
DIGEST_BYTES = PP.DIGEST_BYTES

MIN_COHORT = 3                                                     # founded peers needed before any prior exists
TOLERANCE = 2                                                      # RTT ticks of slack above the cohort reference
MAX_RTT = PP.MAX_RTT

R_OK = 0
R_NO_COHORT = 1                                                    # too few peers — no prior, fall back honestly
R_CAPPED = 2                                                       # the claim was not believed past the cohort

# record: MAGIC(8) | ref | claimed | admissible | n_peers | reason (5×4) | cohort(32) | sha(32) = 92
_HEADER = len(MAGIC)
_NFIELDS = 5
RECORD_BYTES = _HEADER + 4 * _NFIELDS + DIGEST_BYTES + DIGEST_BYTES


class OobpriorError(Exception):
    def __init__(self, message):
        super().__init__(f"OOBPRIOR-REFUSE: {message}")
        self.code = "OOBPRIOR-REFUSE"


def _u32(v):
    return (v & 0xFFFFFFFF).to_bytes(4, "big")


# ---- the cohort (peers' ESTABLISHED floors — evidence the judged client does not control) ------
def observation(client_id, cohort_key, floor_rtt):
    """One peer's ESTABLISHED session floor on a route. Only clients that have already founded a floor under
    URDRPNG1 contribute; a claim is not an observation."""
    if type(client_id) is not int or type(floor_rtt) is not int:
        raise OobpriorError("client_id and floor_rtt must be int")
    if not isinstance(cohort_key, (bytes, bytearray)):
        raise OobpriorError("cohort_key must be bytes (server-derived from the connection)")
    if not (0 <= floor_rtt <= MAX_RTT):
        raise OobpriorError(f"an observed floor must be plausible (0..{MAX_RTT}), got {floor_rtt}")
    return (client_id, bytes(cohort_key), floor_rtt)


def _peers(observations, cohort_key, exclude_client):
    """THE NEUTRAL RULER, ENFORCED STRUCTURALLY: the peers of a cohort with the JUDGED CLIENT REMOVED. The
    exclusion happens here, in the function that builds the reference — the judged client's own observation
    never reaches the statistic it is measured against."""
    return sorted(o[2] for o in observations
                  if o[1] == bytes(cohort_key) and o[0] != exclude_client)


def cohort_reference(observations, cohort_key, exclude_client):
    """The route's reference floor: the LOWER MEDIAN of the peers' established floors, leave-one-out. Robust —
    a minority of padded peers cannot move it. Returns None when fewer than MIN_COHORT peers exist, because
    inventing a reference from too little evidence would be worse than having none."""
    p = _peers(observations, cohort_key, exclude_client)
    if len(p) < MIN_COHORT:
        return None
    return p[(len(p) - 1) // 2]                                    # lower median — conservative, deterministic


def _reference_including_self(observations, cohort_key, exclude_client):
    """THE GOODHART MISTAKE (a falsifier tool): let the JUDGED CLIENT'S OWN observation into the reference it
    is then measured against. A patient padder drags its own baseline up and then 'conforms' to it — the ruler
    is built from the quantity the adversary optimises, so the cap becomes theatre."""
    p = sorted(o[2] for o in observations if o[1] == bytes(cohort_key))   # <-- no exclusion, the bug
    if len(p) < MIN_COHORT:
        return None
    return p[(len(p) - 1) // 2]


def _reference_by_mean(observations, cohort_key, exclude_client):
    """THE FRAGILE-STATISTIC MISTAKE (a falsifier tool): average the peers instead of taking the median. A
    single extreme padded peer now moves the reference, so a MINORITY suffices to poison the cohort."""
    p = _peers(observations, cohort_key, exclude_client)
    if len(p) < MIN_COHORT:
        return None
    return sum(p) // len(p)


# ---- founding a client's floor against the prior ----------------------------------------------
def found(observations, cohort_key, client_id, claimed_floor, _ref=None):
    """FOUND the client's session floor: believe its claim only up to what its PEERS demonstrate. Returns
    `(admissible_floor, reason, reference)`. With no cohort the claim stands (R_NO_COHORT — the honest
    bootstrap); otherwise the floor is capped at `reference + TOLERANCE` and R_CAPPED records that the claim
    was not believed in full."""
    ref_fn = _ref or cohort_reference
    if not (0 <= claimed_floor <= MAX_RTT):
        raise OobpriorError(f"a claimed floor must be plausible (0..{MAX_RTT}), got {claimed_floor}")
    ref = ref_fn(observations, cohort_key, client_id)
    if ref is None:
        return (claimed_floor, R_NO_COHORT, -1)
    ceiling = ref + TOLERANCE
    if claimed_floor > ceiling:
        return (ceiling, R_CAPPED, ref)
    return (claimed_floor, R_OK, ref)


def _found_no_cap(observations, cohort_key, client_id, claimed_floor):
    """THE NO-PRIOR MISTAKE (a falsifier tool): compute the reference and then ignore it, taking the client's
    claim at face value — URDRPNG1's cold start, left exactly as open as before."""
    return (claimed_floor, R_OK, cohort_reference(observations, cohort_key, client_id) or -1)


# ---- composing with the policy: what the founded floor is WORTH --------------------------------
def reach_from_floor(secret, base_rtt, pad, windows, founding_floor):
    """Run URDRPNG1 from a given founding floor and report the client's reach — so the prior's effect is
    measured in the only currency that matters: how far back URDRCLK1 will let that client claim."""
    st = PP.state(PP.MAX_RATE, base_rtt // 2, founding_floor)
    clk, reason = CK.clock(st[1], 0), PP.R_OK
    for w in range(windows):
        st, clk, reason = PP.step(secret, st, w * PP.WINDOW,
                                  PP.play(secret, w * PP.WINDOW, st[0], base_rtt + pad, "honest"))
    return -1 if reason == PP.R_COVERAGE else PP.reach(clk)


def cohort_of(floors, cohort_key, start_id=100):
    """A cohort of founded peers with the given floors."""
    return [observation(start_id + i, cohort_key, f) for i, f in enumerate(floors)]


# ---- the proof-carrying founding record --------------------------------------------------------
def record_bytes_len():
    return RECORD_BYTES


def cohort_digest(observations, cohort_key):
    hh = hashlib.sha256(); hh.update(MAGIC); hh.update(b"|" + bytes(cohort_key))
    for (cid, ck, f) in sorted(observations):
        if ck == bytes(cohort_key):
            hh.update(f"|{cid}:{f}".encode())
    return hh.hexdigest()


def publish(observations, cohort_key, client_id, claimed_floor):
    """SEAL the founding: the reference used, the claim, the admissible floor, the peer count and the reason,
    bound by digest to the exact cohort it was derived from."""
    adm, reason, ref = found(observations, cohort_key, client_id, claimed_floor)
    n = len(_peers(observations, cohort_key, client_id))
    body = bytearray(MAGIC)
    body += _u32(ref) + _u32(claimed_floor) + _u32(adm) + _u32(n) + _u32(reason)
    body += bytes.fromhex(cohort_digest(observations, cohort_key))
    return bytes(body) + hashlib.sha256(bytes(body)).digest()


def _parse(record):
    if not (type(record) is bytes or type(record) is bytearray):
        raise OobpriorError("a record must be bytes")
    t = bytes(record)
    if len(t) != RECORD_BYTES:
        raise OobpriorError(f"a record must be exactly {RECORD_BYTES} bytes")
    if t[:_HEADER] != MAGIC:
        raise OobpriorError("bad magic — not a URDROOB1 record")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise OobpriorError("digest mismatch — tampered or truncated")
    off = _HEADER
    f = []
    for _ in range(_NFIELDS):
        f.append(int.from_bytes(t[off:off + 4], "big", signed=True)); off += 4
    return tuple(f) + (t[off:off + DIGEST_BYTES].hex(),)


def read_record(record):
    """(reference, claimed, admissible, n_peers, reason, cohort_digest)."""
    return _parse(record)


def verify_record(observations, cohort_key, client_id, claimed_floor, record):
    """THE PROOF-CARRYING CONTRACT: lawful iff BYTE-IDENTICAL to a fresh honest publish over the SAME cohort.
    A raised admissible floor, or the record replayed against a different cohort, fails."""
    try:
        _parse(record)
    except OobpriorError:
        return False
    try:
        return bytes(record) == publish(observations, cohort_key, client_id, claimed_floor)
    except OobpriorError:
        return False


def forge_floor(record, admissible):
    """A falsifier tool: re-seal the record with a HIGHER admissible floor. `verify_record` must still refuse."""
    t = bytearray(record[:-DIGEST_BYTES])
    off = _HEADER + 8
    t[off:off + 4] = _u32(admissible)
    return bytes(t) + hashlib.sha256(bytes(t)).digest()


# ---- digests -----------------------------------------------------------------------------------
def oobprior_digest(name, cohort_hex, claimed, admissible, ref, reason, reach):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|c:{cohort_hex}|q:{claimed}|a:{admissible}|r:{ref}|x:{reason}|h:{reach}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) ------------------------------------------------------------
COHORT = b"route/AS64500"
SECRET = PP.SECRET


def _scene(name, floors, claimed, base_rtt, pad, windows=5, client_id=1):
    obs = cohort_of(floors, COHORT)
    adm, reason, ref = found(obs, COHORT, client_id, claimed)
    r = reach_from_floor(SECRET, base_rtt, pad, windows, adm)
    return oobprior_digest(name, cohort_digest(obs, COHORT), claimed, adm, ref, reason, r)


def _scene_capped():
    """THE TEETH: a cold-start padder on a FAST route claims a floor of 12; its peers demonstrate 6, so the
    claim is believed only to 8 (median 6 + TOLERANCE) and its band shrinks accordingly."""
    return _scene("capped", [6, 6, 6], 12, 6, 6)


def _scene_honest_slow():
    """FAIRNESS PRESERVED: a genuinely slow client whose PEERS ARE ALSO SLOW is NOT capped — the cohort
    encodes what that route costs, so corroborated slowness is believed in full."""
    return _scene("honest_slow", [12, 12, 12], 12, 12, 0)


def _scene_no_cohort():
    """THE HONEST BOOTSTRAP: below MIN_COHORT founded peers there is NO prior. The claim stands and the rung
    falls back to URDRPNG1 alone — refusing to invent a reference from too little evidence."""
    return _scene("no_cohort", [6, 6], 12, 6, 6)


def _scene_minority_poison():
    """ROBUSTNESS: a MINORITY of padded peers (2 of 5) cannot move the lower median, so the cap holds."""
    return _scene("minority_poison", [6, 6, 6, 16, 16], 12, 6, 6)


def _scene_majority_poison():
    """THE DECLARED RESIDUAL: a MAJORITY-poisoned cohort (sybil / collusion on one route) DOES move the
    reference, and this rung does not defeat it — the prior is only as honest as the cohort. Pinned as a scene
    so the boundary is in the record, not a footnote."""
    return _scene("majority_poison", [6, 16, 16, 16, 16], 12, 6, 6)


_SCENES = {"capped": _scene_capped, "honest_slow": _scene_honest_slow, "no_cohort": _scene_no_cohort,
           "minority_poison": _scene_minority_poison, "majority_poison": _scene_majority_poison}
SCENES = ("capped", "honest_slow", "no_cohort", "minority_poison", "majority_poison")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_oobprior.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise OobpriorError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260725
SWEEP_COUNT = 120


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random cohorts asserting the LEAVE-ONE-OUT neutral ruler (the
    reference is identical whether or not the judged client's own observation is in the pool, and the
    including-self plant breaks it), the COLD-START CAP and the reach reduction it buys against URDRPNG1 with
    no prior, the honest-slow-cohort exemption, the no-cohort bootstrap, minority-poisoning robustness (with
    the mean plant shown fragile), determinism, and the proof-carrying record. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    loo_seen = cap_seen = slow_seen = boot_seen = poison_seen = strict_seen = fragile_seen = 0
    for s in range(count):
        base = 2 * r.rng(2, 4)                                     # the route's true RTT
        n = r.rng(MIN_COHORT, 6)
        floors = [base + r.rng(0, 1) for _ in range(n)]            # honest peers on that route
        ck = bytes([r.rng(0, 255) for _ in range(4)])
        obs = cohort_of(floors, ck)
        pad = 2 * r.rng(2, 4)
        claimed = min(base + pad, MAX_RTT)                         # what a cold-start padder would found
        # THE NEUTRAL RULER — leave-one-out invariance: the judged client's own observation cannot move it
        ref_out = cohort_reference(obs, ck, 1)
        # SELF-SYBIL: the padder floods the pool with inflated observations under its OWN id. The exclusion
        # drops every one of them, so the reference is UNMOVED; the including-self plant is dragged up. (A
        # SINGLE self observation moves neither — the robust median absorbs it; the exclusion earns its keep
        # against the flood, which is precisely the case a fragile or self-including ruler would lose.)
        flood = obs + [observation(1, ck, MAX_RTT) for _ in range(len(obs) + 1)]
        if cohort_reference(flood, ck, 1) != ref_out:
            raise OobpriorError(f"scenario {s} (seed {seed}): the judged client's OWN observations moved the "
                                f"reference it is measured against — the neutral ruler is broken")
        if _reference_including_self(flood, ck, 1) <= ref_out:
            raise OobpriorError(f"scenario {s}: the including-self plant was not dragged up by the client's "
                                f"own flood (vacuous)")
        loo_seen += 1
        # THE CAP — and what it is worth, measured against URDRPNG1 with no prior
        adm, reason, ref = found(obs, ck, 1, claimed)
        if adm > ref + TOLERANCE:
            raise OobpriorError(f"scenario {s}: the founded floor escaped the cohort ceiling")
        if reason != R_CAPPED:
            raise OobpriorError(f"scenario {s}: a padded claim was believed in full")
        capped_reach = reach_from_floor(SECRET, base, pad, 5, adm)
        uncapped_reach = reach_from_floor(SECRET, base, pad, 5, _found_no_cap(obs, ck, 1, claimed)[0])
        # THE PRIOR NEVER HURTS — universal. It STRICTLY helps only where the padder's own ceiling is
        # reachable inside the horizon; where URDRPNG1's rate limit binds first, both land on the same reach
        # and the prior is merely redundant, never harmful. (Asserting strictness universally would be false —
        # measured, not assumed.) Non-vacuity is carried by `strict_seen` plus the fixed witness below.
        if capped_reach > uncapped_reach:
            raise OobpriorError(f"scenario {s} (seed {seed}): the prior HURT the client — capped reach "
                                f"{capped_reach} exceeds the un-prior'd {uncapped_reach}")
        if capped_reach < uncapped_reach:
            strict_seen += 1
        cap_seen += 1
        # FAIRNESS — an honest slow client whose peers are also slow is believed in full
        slow_floors = [base + pad] * n
        slow_obs = cohort_of(slow_floors, ck, start_id=200)
        adm_s, reason_s, _rs = found(slow_obs, ck, 1, base + pad)
        if adm_s != base + pad or reason_s == R_CAPPED:
            raise OobpriorError(f"scenario {s}: a corroborated slow client was capped — the prior became a "
                                f"tax on distant players")
        slow_seen += 1
        # BOOTSTRAP — below MIN_COHORT there is no prior, and the claim stands rather than a reference invented
        thin = cohort_of(floors[:MIN_COHORT - 1], ck, start_id=300)
        if cohort_reference(thin, ck, 1) is not None or found(thin, ck, 1, claimed)[1] != R_NO_COHORT:
            raise OobpriorError(f"scenario {s}: a reference was invented from too few peers")
        boot_seen += 1
        # ROBUSTNESS — a minority of padded peers cannot move the median; the mean plant is moved by them
        minority = cohort_of(floors + [MAX_RTT], ck, start_id=400)
        if cohort_reference(minority, ck, 1) > ref_out + 1:
            raise OobpriorError(f"scenario {s}: a single padded peer moved the robust reference")
        # The robust reference holds (universal). The MEAN plant is fragile in general but can COINCIDE with
        # the median under integer division on some distributions, so its inflation is COUNTED and witnessed
        # rather than asserted universally — measured, not assumed.
        if _reference_by_mean(minority, ck, 1) > cohort_reference(minority, ck, 1):
            fragile_seen += 1
        poison_seen += 1
        # proof-carrying
        rec = publish(obs, ck, 1, claimed)
        if len(rec) != record_bytes_len() or not verify_record(obs, ck, 1, claimed, rec):
            raise OobpriorError(f"scenario {s}: an honest founding record failed its own contract")
        if verify_record(obs, ck, 1, claimed, forge_floor(rec, MAX_RTT)):
            raise OobpriorError(f"scenario {s}: a forged higher floor verified")
        hh.update(f"|{s}:{ref}:{adm}:{capped_reach}:{uncapped_reach}".encode())
    # THE TEETH, WITNESSED: a FIXED canonical case where the prior STRICTLY reduces the padder's reach. If
    # this ever stops holding, the rung has stopped buying anything and the claim must be re-graded.
    w_obs = cohort_of([6, 6, 6], b"witness")
    w_adm = found(w_obs, b"witness", 1, 12)[0]
    w_capped = reach_from_floor(SECRET, 6, 6, 5, w_adm)
    w_uncapped = reach_from_floor(SECRET, 6, 6, 5, 12)
    if not w_capped < w_uncapped:
        raise OobpriorError(f"the prior's teeth are no longer witnessed (capped {w_capped} vs un-prior'd "
                            f"{w_uncapped}) — the rung buys nothing and the claim must be re-graded")
    if strict_seen == 0:
        raise OobpriorError("the prior never strictly reduced a padder's reach across the whole sweep — "
                            "the cap is vacuous on this parameter space")
    # THE FRAGILE-STATISTIC WITNESS: a fixed cohort where the mean IS moved by one outlier and the median is
    # not — the reason the reference is a median, kept non-vacuous.
    f_obs = cohort_of([6, 6, 6, MAX_RTT], b"fragile")
    if not _reference_by_mean(f_obs, b"fragile", 1) > cohort_reference(f_obs, b"fragile", 1):
        raise OobpriorError("the fragile-statistic witness no longer holds — the case for a robust reference "
                            "is unwitnessed and the claim must be re-graded")
    if fragile_seen == 0:
        raise OobpriorError("a mean reference was never inflated by an outlier anywhere in the sweep — the "
                            "robustness claim is vacuous on this parameter space")
    # THE DECLARED RESIDUAL, WITNESSED: a MAJORITY-poisoned cohort DOES move the reference. If this ever stops
    # holding, the boundary has gone vacuous (or the rung improved) — either way the claim must be re-graded.
    ck_w = b"witness"
    honest_c = cohort_of([6, 6, 6, 6, 6], ck_w)
    poisoned_c = cohort_of([6, 16, 16, 16, 16], ck_w)
    if not cohort_reference(poisoned_c, ck_w, 1) > cohort_reference(honest_c, ck_w, 1):
        raise OobpriorError("the majority-poisoning residual is no longer witnessed — the declared boundary "
                            "has gone vacuous and the claim must be re-graded")
    if loo_seen == 0 or cap_seen == 0 or slow_seen == 0 or boot_seen == 0 or poison_seen == 0:
        raise OobpriorError(f"NON-VACUITY: loo {loo_seen}, cap {cap_seen}, slow {slow_seen}, boot {boot_seen}, "
                            f"poison {poison_seen}")
    return {"scenarios": count, "loo_seen": loo_seen, "cap_seen": cap_seen, "slow_seen": slow_seen,
            "boot_seen": boot_seen, "poison_seen": poison_seen, "strict_seen": strict_seen,
            "fragile_seen": fragile_seen,
            "witness_capped": w_capped, "witness_uncapped": w_uncapped, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_oobprior.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise OobpriorError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found_ = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except OobpriorError as exc:
            found_.append((seed, str(exc)))
    return found_


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        f = explore(base, n)
        print(f"EXPLORE: {'no counterexample' if not f else str(len(f)) + ' counterexample(s)'} across {n} "
              f"reseeded sweeps from base {base}.")
        for seed, msg in f:
            print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} cohorts, loo {rep['loo_seen']}, cap {rep['cap_seen']}, slow "
          f"{rep['slow_seen']}, boot {rep['boot_seen']}, poison {rep['poison_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
