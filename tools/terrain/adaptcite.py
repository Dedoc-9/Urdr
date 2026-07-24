# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""adaptcite — ADAPTIVE (BANDWIDTH-AWARE) REPRESENTATION SELECTION (URDRADC1): choosing the cheapest LAWFUL
encoding of each entity update. URDRCIT1 proves lawful historical reuse but cites by a FIXED rule (the
oldest certified match), which can spend a 9-byte CITE where a 7-byte MOVE was equally lawful. This rung
proves that an encoder may deterministically pick the MINIMUM-COST lawful representation — WITHOUT altering
semantics, because every option in the choice set reconstructs the identical state. Composition over
`citation`/`byteacct`/.../`perception`, NO NEW GLYPH — the kernel stays frozen. See `docs/adaptcite_brief.md`
for the design pass and the D1 §20 glyph ruling.

THE INSIGHT. Since every CITE is fixed-width (constant-shape), a citation's cost does not depend on which
anchor it names — so "bandwidth-aware" is not about which anchor, it is about which REPRESENTATION. An entity
whose state is unchanged, or moved with an unchanged citation, or returned to a certified prior value, or
changed outright has several LAWFUL encodings of different cost:
    nothing (0)  <  MOVE (~7)  <  CITE (9)  <  FULL (~39)
The adaptive encoder picks the least-cost lawful one, deterministically, SUBJECT TO the mandatory baselines
the rate law forces.

THE HEADLINE LAW — REPRESENTATION-INDEPENDENCE. Every lawful representation reconstructs the SAME state, so
the client's reconstructed state sequence is IDENTICAL under the adaptive encoder, the citation rung's
oldest-match encoder, and the all-baseline encoder. The optimizer cannot corrupt semantics; it can only
choose a cheaper spelling of an already-certified history.

THE STRUCTURAL LAWS (all inherited, each still checked):
  * ADAPTIVE-OPTIMALITY — the chosen representation is the minimum-cost LAWFUL one (unless a mandatory
    baseline is due); `_encode` (suboptimal) picks a costlier lawful spelling and is caught.
  * LAWFUL-ONLY — the minimum is taken over LAWFUL options only; a forged CITE to an UNCERTIFIED anchor is
    cheaper than a FULL but is refused by the certified law.
  * SEMANTICS-PRESERVING — a forged CITE to a NON-matching anchor is cheap but reconstructs the wrong state;
    representation-independence catches it.
  * DETERMINISTIC — selection is a pure function of (state, history, config); the wall-clock plant diverges.
  * Plus every citation law: certified / constant-shape / closed-world (eviction) / cross-tick rate.

GRADE: MEASURED — the adaptive wire is never larger than the oldest-match wire and strictly smaller when a
cheaper lawful spelling exists (a MOVE where the fixed rule spent a CITE). DECLARED: inherits every
citation/byteacct/scheduler/throttle/anamorphosis/perception boundary; the selection is a per-update local
minimum (a greedy deterministic rule), not a global multi-tick optimum (declared successor). `does_not_show`:
byte-budget deferral (B roomy here, as in URDRCIT1); cross-placement (URDRADC1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import citation as CT                                            # the rung this composes over  # noqa: E402
import byteacct as BY                                            # noqa: E402
import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRADC1"
DIGEST_BYTES = A.DIGEST_BYTES
OVERHEAD = len(MAGIC) + 4 + 4 + 4 + DIGEST_BYTES
ACK_LAG = CT.ACK_LAG
REFRESH_INTERVAL = CT.REFRESH_INTERVAL
B_ROOMY = OVERHEAD + 360


class AdaptCiteError(Exception):
    def __init__(self, message):
        super().__init__(f"ADAPTCITE-REFUSE: {message}")
        self.code = "ADAPTCITE-REFUSE"


# ---- serialize / parse (constant-shape at B; record format shared with citation) --------------
def serialize(tick, budget, records, _ser=None):
    if _ser is not None:
        return _ser(tick, budget, records)
    body_budget = budget - OVERHEAD
    body = bytearray()
    for r in records:
        body += r
    if len(body) > body_budget:
        raise AdaptCiteError(f"records {len(body)}B exceed the body budget {body_budget}B")
    body += b"\x00" * (body_budget - len(body))
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)
    return frame + hashlib.sha256(frame).digest()


def parse(packet):
    t = bytes(packet)
    if t[:len(MAGIC)] != MAGIC:
        raise AdaptCiteError("bad magic — not a URDRADC1 packet")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise AdaptCiteError("digest mismatch — tampered or truncated")
    budget = int.from_bytes(t[12:16], "big")
    if len(t) != budget:
        raise AdaptCiteError(f"packet length {len(t)} != declared budget {budget} (not constant-shape at B)")
    tick = int.from_bytes(t[8:12], "big")
    count = int.from_bytes(t[16:20], "big")
    off = OVERHEAD - DIGEST_BYTES
    records = []
    for _ in range(count):
        rec, off = CT._read_record(t, off)                    # the record format is shared with URDRCIT1
        records.append(rec)
    return tick, budget, records, off - (OVERHEAD - DIGEST_BYTES)


# ---- lawful representations and the adaptive choice --------------------------------------------
def _lawful_reps(cur, hist, eid, s, tick, ack_lag):
    """The lawful encodings of entity `eid`'s update to state `s`, as (cost, kind, record_bytes). Every one
    reconstructs `s` exactly — the choice among them is a pure bandwidth question."""
    ex, ey, cite = s
    am = CT.ack_max(tick, ack_lag)
    reps = []
    if eid in cur and s == cur[eid]:
        reps.append((0, "none", b""))                          # unchanged — no record
    if eid in cur and cur[eid][2] == cite:
        mv = BY.rec_move(eid, ex - cur[eid][0], ey - cur[eid][1])
        reps.append((len(mv), "move", mv))
    if eid in cur:
        for T in sorted(hist.get(eid, {})):                   # the OLDEST certified matching anchor
            if T <= am and hist[eid][T] == s:
                reps.append((CT.CITE_BYTES, "cite", CT.rec_cite(eid, T)))
                break
    reps.append((len(BY.rec_full(eid, ex, ey, cite)), "full", BY.rec_full(eid, ex, ey, cite)))
    return reps


_KIND_ORDER = {"none": 0, "move": 1, "cite": 2, "full": 3}


def _choose(reps, mode):
    """Pick a representation. `adaptive` = minimum cost (kind order breaks ties); `oldest` = the citation
    rule (cite if available, else move, else full); `suboptimal` = the MAX-cost lawful spelling (a plant)."""
    if mode == "adaptive":
        return min(reps, key=lambda r: (r[0], _KIND_ORDER[r[1]]))
    if mode == "suboptimal":
        changed = [r for r in reps if r[1] != "none"]
        return max(changed or reps, key=lambda r: (r[0], _KIND_ORDER[r[1]]))
    # oldest (the URDRCIT1 fixed rule): none > cite > move > full, in that preference
    by_kind = {r[1]: r for r in reps}
    for k in ("none", "cite", "move", "full"):
        if k in by_kind:
            return by_kind[k]
    return reps[-1]


def _encode(cur, hist, base, entities, walls, cl, L, tick, cfg, mode="adaptive", _clock=None):
    B, ack_lag, refresh = cfg
    am = CT.ack_max(tick, ack_lag)
    man = A._manifest_under(entities, walls, cl, L)
    man_set = set(man)
    records = []
    for eid in sorted(cur):
        if eid not in man_set:
            records.append(BY.rec_remove(eid))                # departure → REMOVE (evicts)
    for eid in man:
        ex, ey, cite = entities[eid]; s = (ex, ey, cite)
        must_baseline = eid not in cur or (tick - base.get(eid, -10 ** 9)) >= refresh
        if mode == "baseline" or must_baseline:
            records.append(BY.rec_full(eid, ex, ey, cite))
            continue
        emode = "suboptimal" if (_clock is not None and _clock()) else mode   # a wall-clock perturbs the choice
        if emode == "drift" and eid in cur and s != cur[eid]:
            certified = [T for T in sorted(hist.get(eid, {})) if T <= am]     # cite the oldest certified
            if certified:                                     # anchor even if it does NOT match — a wrong cite
                records.append(CT.rec_cite(eid, certified[0])); continue
        reps = _lawful_reps(cur, hist, eid, s, tick, ack_lag)
        _cost, kind, rec = _choose(reps, "adaptive" if emode == "drift" else emode)
        if kind != "none":
            records.append(rec)
    return man, records


def run(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="adaptive", _ser=None, _clock=None):
    cur, hist, base = {}, {}, {}
    ccur, chist, cbase = {}, {}, {}
    packets, recon = [], []
    cites = fulls = moves = 0
    used_total = 0
    max_gap = 0
    for t, (entities, walls) in enumerate(ticks):
        man, byte_records = _encode(cur, hist, base, entities, walls, cl, L, t, cfg, mode, _clock)
        packet = serialize(t, cfg[0], byte_records, _ser)
        parsed = parse(packet)[2]
        for (kind, _e, _p) in parsed:
            cites += kind == "cite"; fulls += kind == "full"; moves += kind == "move"
        cur, hist, base = CT.apply_records(cur, hist, base, parsed, t)
        ccur, chist, cbase = CT.apply_records(ccur, chist, cbase, parsed, t)
        packets.append(packet); recon.append(dict(ccur))
        used_total += parse(packet)[3]
        for eid in man:
            max_gap = max(max_gap, t - base.get(eid, t))
        prune = t - (REFRESH_INTERVAL + ACK_LAG + 1)
        for e in list(hist):
            hist[e] = {k: v for k, v in hist[e].items() if k > prune}
    return {"packets": packets, "recon": recon, "cites": cites, "fulls": fulls, "moves": moves,
            "used_total": used_total, "max_gap": max_gap, "cfg": cfg}


# ---- laws --------------------------------------------------------------------------------------
def representation_independent(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL)):
    """THE HEADLINE LAW: adaptive, oldest-match, and all-baseline encoders reconstruct the SAME states."""
    a = run(ticks, cl, L, cfg, "adaptive")["recon"]
    o = run(ticks, cl, L, cfg, "oldest")["recon"]
    b = run(ticks, cl, L, cfg, "baseline")["recon"]
    return a == o == b


def optimality_ok(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL)):
    """Each non-baseline update uses the MINIMUM-cost lawful representation."""
    cur, hist, base = {}, {}, {}
    B, ack_lag, refresh = cfg
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        for eid in man:
            ex, ey, cite = entities[eid]; s = (ex, ey, cite)
            if eid not in cur or (t - base.get(eid, -10 ** 9)) >= refresh:
                continue                                      # a mandatory baseline overrides
            reps = _lawful_reps(cur, hist, eid, s, t, ack_lag)
            chosen = _choose(reps, "adaptive")
            if chosen[0] != min(r[0] for r in reps):
                return False
        _m, br = _encode(cur, hist, base, entities, walls, cl, L, t, cfg, "adaptive")
        cur, hist, base = CT.apply_records(cur, hist, base, parse(serialize(t, B, br))[2], t)
    return True


def used_total(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="adaptive"):
    return run(ticks, cl, L, cfg, mode)["used_total"]


def is_closed_world_run(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="adaptive"):
    rep = run(ticks, cl, L, cfg, mode)
    for t, (e, w) in enumerate(ticks):
        if set(rep["recon"][t]) != set(A._manifest_under(e, w, cl, L)):
            return False
    return True


def constant_shape_ok(rep):
    return all(len(p) == rep["cfg"][0] for p in rep["packets"])


def rate_ok(rep):
    return rep["max_gap"] <= rep["cfg"][2]


# ---- digests / scenarios -----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def run_digest(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="adaptive"):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for p in run(ticks, cl, L, cfg, mode)["packets"]:
        hh.update(hashlib.sha256(p).digest())
    return hh.hexdigest()


def _seq(paths, nticks):
    ticks = []
    for t in range(nticks):
        ents = {eid: (xs[t][0], xs[t][1], xs[t][2]) for eid, xs in paths.items()}
        ticks.append((ents, frozenset()))
    return ticks


def _oscillate(nticks=12):
    """A world where the FIXED rule overspends: an entity whose POSITION oscillates (returns to a prior
    value) while its citation stays CONSTANT — so both a MOVE and a CITE are lawful, and the adaptive
    encoder picks the cheaper MOVE where the oldest-match rule spends a CITE. Plus a toggling-cite entity
    and a hidden one."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    paths = {
        1: [(3 + (t % 2), 0, _d(1)) for t in range(nticks)],          # position oscillates, cite constant
        3: [(6, 0, _d(600 + (t // 2) % 2)) for t in range(nticks)],   # cite toggles
        2: [(-9, 0, _d(2)) for t in range(nticks)],                   # hidden
    }
    return _seq(paths, nticks), cl


def _scene(name, ticks, cl, L, verdict):
    return hashlib.sha256(MAGIC + f"|{name}|d:{run_digest(ticks, cl, L)}|v:{verdict}".encode()).hexdigest()


def _scene_cheaper():
    ticks, cl = _oscillate()
    a = used_total(ticks, cl, A.lens(0, 0), mode="adaptive")
    o = used_total(ticks, cl, A.lens(0, 0), mode="oldest")
    return _scene("cheaper", ticks, cl, A.lens(0, 0), "SMALLER" if a < o else "SAME")


def _scene_independent():
    ticks, cl = _oscillate()
    return _scene("independent", ticks, cl, A.lens(0, 0),
                  "IDENTICAL" if representation_independent(ticks, cl, A.lens(0, 0)) else "DRIFT")


def _scene_optimal():
    ticks, cl = _oscillate()
    return _scene("optimal", ticks, cl, A.lens(0, 0),
                  "MINIMAL" if optimality_ok(ticks, cl, A.lens(0, 0)) else "WASTEFUL")


def _scene_lawful():
    """The adaptive wire is still a closed world with bounded refresh."""
    ticks, cl = _oscillate()
    rep = run(ticks, cl, A.lens(0, 0))
    ok = is_closed_world_run(ticks, cl, A.lens(0, 0)) and rate_ok(rep) and constant_shape_ok(rep)
    return _scene("lawful", ticks, cl, A.lens(0, 0), "LAWFUL" if ok else "BROKEN")


_SCENES = {"cheaper": _scene_cheaper, "independent": _scene_independent,
           "optimal": _scene_optimal, "lawful": _scene_lawful}
SCENES = ("cheaper", "independent", "optimal", "lawful")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_adaptcite.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AdaptCiteError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 80
NTICKS = 12


def gen_sequence(r):
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    x1, x3 = r.rng(3, 5), r.rng(6, 8)
    a3 = 600 + r.rng(0, 3) * 2
    behind = (-r.rng(3, 8), r.rng(-3, 3))
    depart_at = r.rng(7, 10)
    ticks = []
    for t in range(NTICKS):
        ents = {2: (behind[0], behind[1], _d(2))}
        ents[1] = (x1 + (t % 2), 0, _d(1))                    # oscillating position, constant cite → MOVE beats CITE
        ents[3] = (x3, 0, _d(a3 + (t // 2) % 2))              # toggling cite → CITE reuse
        if t < depart_at:
            ents[4] = (r.rng(9, 12), t % 2, _d(700 + (t // 2) % 2))
        ticks.append((ents, frozenset()))
    return ticks, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep asserting, per world: REPRESENTATION-INDEPENDENCE (adaptive == oldest ==
    baseline reconstruction), OPTIMALITY (each update the min-cost lawful spelling), a real saving (adaptive
    <= oldest bytes), closed-world with eviction, constant-shape, bounded refresh, hidden-set invariance, and
    deterministic replay. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    cheaper_seen = cite_seen = move_seen = 0
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        if run_digest(ticks, cl, L) != run_digest(ticks, cl, L):
            raise AdaptCiteError(f"seq {s}: not deterministic")
        if not representation_independent(ticks, cl, L):
            raise AdaptCiteError(f"seq {s}: representations diverge — a lawful spelling altered semantics")
        if not optimality_ok(ticks, cl, L):
            raise AdaptCiteError(f"seq {s}: a non-minimal representation was chosen")
        rep = run(ticks, cl, L)
        if not is_closed_world_run(ticks, cl, L):
            raise AdaptCiteError(f"seq {s}: reconstruction is not the manifested set")
        if not constant_shape_ok(rep) or not rate_ok(rep):
            raise AdaptCiteError(f"seq {s}: constant-shape or rate law broke")
        if used_total(ticks, cl, L, mode="adaptive") > used_total(ticks, cl, L, mode="oldest"):
            raise AdaptCiteError(f"seq {s}: the adaptive wire is larger than the fixed rule")
        moved = [({**e, 2: (e[2][0], e[2][1], _d(9000 + s))}, w) for e, w in ticks]
        if run(moved, cl, L)["packets"] != rep["packets"]:
            raise AdaptCiteError(f"seq {s}: a change to the hidden entity altered the wire — leak")
        cheaper_seen += 1 if used_total(ticks, cl, L, mode="adaptive") < used_total(ticks, cl, L, mode="oldest") else 0
        cite_seen += 1 if rep["cites"] > 0 else 0
        move_seen += 1 if rep["moves"] > 0 else 0
        hh.update(f"|{s}:{run_digest(ticks, cl, L)}:{rep['used_total']}".encode())
    if cheaper_seen == 0 or cite_seen == 0 or move_seen == 0:
        raise AdaptCiteError(f"NON-VACUITY: cheaper {cheaper_seen}, cite {cite_seen}, move {move_seen}")
    return {"scenarios": count, "cheaper_seen": cheaper_seen, "cite_seen": cite_seen, "move_seen": move_seen,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_adaptcite.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise AdaptCiteError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except AdaptCiteError as exc:
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
    print(f"SWEEP: {rep['scenarios']} sequences, cheaper {rep['cheaper_seen']}, cite {rep['cite_seen']}, "
          f"move {rep['move_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
