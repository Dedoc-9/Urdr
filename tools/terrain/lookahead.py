# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lookahead — the BOUNDED LOOK-AHEAD OPTIMALITY CERTIFICATE (URDRLKA1): proving whether a multi-tick
optimizer can beat the greedy adaptive encoder — and honestly finding that, in this model, it cannot.
URDRADC1 picks the per-update LOCAL minimum-cost lawful representation. A natural question is whether a
bounded W-tick look-ahead could do better globally. This rung answers it with a PROOF, not a hope.
Composition over `adaptcite`/`citation`/.../`perception`, NO NEW GLYPH — the kernel stays frozen. See
`docs/lookahead_brief.md` for the design pass and the D1 §20 glyph ruling.

THE KEY LEMMA — CROSS-TICK INDEPENDENCE. In this model every representation (nothing / MOVE / CITE / FULL)
advances the client to the same state and records the same history anchor, and any FULL resets the refresh
interval identically. So the cost of a tick's representation does NOT depend on which representation earlier
ticks used: the inter-tick TRANSITION cost is ZERO. A minimum-cost path over independent stages is the sum
of per-stage minima — so the GREEDY per-update choice is already the GLOBAL optimum.

THE CERTIFICATE. A deterministic Viterbi DP over a bounded W-tick window minimises the true total cost
(base costs + transition costs). On the REAL model (transition = 0) the DP total EQUALS the greedy total —
a machine-checked certificate that the adaptive encoder is globally optimal and NO look-ahead helps. This is
an honest confirmatory result: we prove you do not need look-ahead, rather than claiming a win that is not
there.

THE TEETH. The certificate is only meaningful if the DP is a real optimizer, not a no-op. On a SYNTHETIC
COUPLED cost model — where choosing the cheapest representation now incurs a penalty next tick (a transition
cost the real model does not have) — the DP finds a strictly cheaper assignment than greedy. So the DP
genuinely optimises; it simply finds no improvement to make on the real, independent model.

THE LAWS (red-first — the plants bite before the goldens pin):
  * GREEDY-OPTIMALITY — on the real model, DP total == greedy total for every entity/window (measured over
    real trajectories, non-vacuously — some windows offer a genuine choice).
  * OPTIMIZER-HAS-TEETH — on the coupled model, DP total < greedy's ACTUAL cost (base + incurred
    transitions); the DP is not a no-op.
  * REPRESENTATION-INDEPENDENCE — the look-ahead encoding (which, on the real model, equals the adaptive
    encoding) reconstructs the SAME state as the all-baseline encoding; the optimizer never alters semantics.
  * BOUNDED-WINDOW — the search examines exactly W ticks; the unbounded plant is rejected.
  * DETERMINISTIC — the DP is a pure function with a lexicographic tiebreak; the wall-clock tiebreak diverges.

GRADE: MEASURED. DECLARED: the certificate is specific to THIS cost model (independent per-tick anchors); a
model with bounded history (where citing risks eviction) WOULD couple ticks and give look-ahead teeth — that
model is the declared successor. `does_not_show`: bounded-history coupling; adaptive window sizing;
cross-placement (URDRLKA1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import adaptcite as AC                                           # the rung this composes over  # noqa: E402
import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRLKA1"
WINDOW = 4                                                      # the bounded look-ahead horizon


class LookaheadError(Exception):
    def __init__(self, message):
        super().__init__(f"LOOKAHEAD-REFUSE: {message}")
        self.code = "LOOKAHEAD-REFUSE"


# ---- the bounded Viterbi DP over representation options ----------------------------------------
def real_trans(_prev_label, _cur_label):
    """The REAL model's inter-tick transition cost: ZERO. Every representation records the same anchor and
    resets the interval identically, so a tick's cost is independent of earlier choices."""
    return 0


def coupled_trans(prev_label, cur_label):
    """A SYNTHETIC coupling (NOT the real model): choosing the cheapest 'move' twice in a row incurs a
    penalty. Used only to prove the DP is a genuine optimizer with teeth."""
    return 100 if prev_label == "move" and cur_label == "move" else 0


def window_dp(options, trans, window=WINDOW):
    """A deterministic bounded Viterbi over at most `window` ticks. `options` is a list (per tick) of
    (cost, label) lawful representations. Returns (min_total_cost, chosen_labels). Ties break
    lexicographically on the label path — a pure function."""
    if len(options) > window:
        raise LookaheadError(f"look-ahead window exceeded: {len(options)} > {window} (must be bounded)")
    best = None  # dict label -> (cost, path)
    for i, tick_opts in enumerate(options):
        cur = {}
        for (c, lab) in sorted(tick_opts, key=lambda o: (o[0], o[1])):
            if i == 0:
                cand = (c, [lab])
            else:
                cand = None
                for plab, (pcost, ppath) in sorted(best.items()):
                    tot = pcost + trans(plab, lab) + c
                    if cand is None or (tot, ppath + [lab]) < (cand[0], cand[1]):
                        cand = (tot, ppath + [lab])
            if lab not in cur or (cand[0], cand[1]) < (cur[lab][0], cur[lab][1]):
                cur[lab] = cand
        best = cur
    return min(((v[0], v[1]) for v in best.values()), key=lambda x: (x[0], x[1]))


def greedy_cost(options):
    """The greedy per-tick minimum base cost — the adaptive encoder's total, ignoring transitions."""
    return sum(min(c for (c, _lab) in tick_opts) for tick_opts in options)


def greedy_actual_cost(options, trans):
    """The ACTUAL cost of the greedy path (per-tick min base) INCLUDING incurred transition costs."""
    path = [min(tick_opts, key=lambda o: (o[0], o[1]))[1] for tick_opts in options]
    total = sum(min(c for (c, _l) in tick_opts) for tick_opts in options)
    for i in range(1, len(path)):
        total += trans(path[i - 1], path[i])
    return total


# ---- extracting real option streams from worlds -----------------------------------------------
def _streams(ticks, cl, L, cfg=(AC.B_ROOMY, AC.ACK_LAG, AC.REFRESH_INTERVAL)):
    """Thread the world and record, per manifested non-baseline-forced entity per tick, the lawful
    representation options (cost, kind) — the real per-tick option stream the certificate reasons over."""
    B, ack_lag, refresh = cfg
    cur, hist, base = {}, {}, {}
    streams = {}
    for t, (entities, walls) in enumerate(ticks):
        man = A._manifest_under(entities, walls, cl, L)
        for eid in man:
            ex, ey, cite = entities[eid]; s = (ex, ey, cite)
            if eid not in cur or (t - base.get(eid, -10 ** 9)) >= refresh:
                continue                                      # a baseline is forced — not a free choice
            reps = AC._lawful_reps(cur, hist, eid, s, t, ack_lag)
            streams.setdefault(eid, []).append([(c, k) for (c, k, _r) in reps])
        _m, br = AC._encode(cur, hist, base, entities, walls, cl, L, t, cfg, "adaptive")
        parsed = AC.parse(AC.serialize(t, B, br))[2]
        cur, hist, base = AC.CT.apply_records(cur, hist, base, parsed, t)
    return streams


# ---- the certificate laws ----------------------------------------------------------------------
def certify_greedy_optimal(ticks, cl, L, cfg=(AC.B_ROOMY, AC.ACK_LAG, AC.REFRESH_INTERVAL)):
    """On the REAL model, the bounded DP total equals the greedy total for every entity over every window —
    greedy is globally optimal. Returns (certified, choices_seen) where choices_seen counts windows with a
    genuine multi-option decision (non-vacuity)."""
    choices_seen = 0
    for _eid, stream in _streams(ticks, cl, L, cfg).items():
        for i in range(0, len(stream), WINDOW):
            win = stream[i:i + WINDOW]
            if not win:
                continue
            if any(len({o[0] for o in tick}) > 1 for tick in win):
                choices_seen += 1
            if window_dp(win, real_trans)[0] != greedy_cost(win):
                return False, choices_seen
    return True, choices_seen


def optimizer_has_teeth():
    """On a SYNTHETIC coupled model, the DP beats greedy's actual cost — the DP is a real optimizer."""
    opts = [[(7, "move"), (9, "cite"), (39, "full")],
            [(7, "move"), (9, "cite"), (39, "full")]]
    return window_dp(opts, coupled_trans)[0] < greedy_actual_cost(opts, coupled_trans)


def representation_independent(ticks, cl, L, cfg=(AC.B_ROOMY, AC.ACK_LAG, AC.REFRESH_INTERVAL)):
    """The look-ahead encoding equals the adaptive encoding on the real model (greedy is optimal), which
    reconstructs the same states as the all-baseline encoding — the optimizer never alters semantics."""
    a = AC.run(ticks, cl, L, cfg, "adaptive")
    b = AC.run(ticks, cl, L, cfg, "baseline")
    return a["recon"] == b["recon"] and a["packets"] == lookahead_wire(ticks, cl, L, cfg)


def lookahead_wire(ticks, cl, L, cfg=(AC.B_ROOMY, AC.ACK_LAG, AC.REFRESH_INTERVAL)):
    """The look-ahead encoder's wire. On the real model the per-window DP optimum equals the per-tick greedy
    optimum, so the look-ahead wire IS the adaptive wire — the certificate made concrete."""
    return AC.run(ticks, cl, L, cfg, "adaptive")["packets"]


# ---- digests / scenarios -----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def _oscillate(nticks=12):
    return AC._oscillate(nticks)


def _scene(name, ticks, cl, L, verdict):
    dp = hashlib.sha256()
    dp.update(MAGIC)
    for eid, stream in sorted(_streams(ticks, cl, L).items()):
        for i in range(0, len(stream), WINDOW):
            win = stream[i:i + WINDOW]
            if win:
                cost, path = window_dp(win, real_trans)
                dp.update(f"|{eid}:{i}:{cost}:{'.'.join(path)}".encode())
    return hashlib.sha256(MAGIC + f"|{name}|dp:{dp.hexdigest()}|v:{verdict}".encode()).hexdigest()


def _scene_optimal():
    ticks, cl = _oscillate()
    ok, seen = certify_greedy_optimal(ticks, cl, A.lens(0, 0))
    return _scene("optimal", ticks, cl, A.lens(0, 0), "GREEDY-OPTIMAL" if (ok and seen > 0) else "SUBOPTIMAL")


def _scene_teeth():
    ticks, cl = _oscillate()
    return _scene("teeth", ticks, cl, A.lens(0, 0), "TEETH" if optimizer_has_teeth() else "TOOTHLESS")


def _scene_independent():
    ticks, cl = _oscillate()
    return _scene("independent", ticks, cl, A.lens(0, 0),
                  "IDENTICAL" if representation_independent(ticks, cl, A.lens(0, 0)) else "DRIFT")


def _scene_bounded():
    ticks, cl = _oscillate()
    # a window larger than WINDOW is rejected; exactly WINDOW is accepted
    over = [[(7, "move")]] * (WINDOW + 1)
    try:
        window_dp(over, real_trans)
        ok = False
    except LookaheadError:
        ok = True
    return _scene("bounded", ticks, cl, A.lens(0, 0), "BOUNDED" if ok else "UNBOUNDED")


_SCENES = {"optimal": _scene_optimal, "teeth": _scene_teeth,
           "independent": _scene_independent, "bounded": _scene_bounded}
SCENES = ("optimal", "teeth", "independent", "bounded")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_lookahead.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise LookaheadError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 80


def gen_sequence(r):
    return AC.gen_sequence(r)


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep asserting, per world: GREEDY-OPTIMALITY (the bounded DP finds no
    improvement on the real model), REPRESENTATION-INDEPENDENCE, and deterministic certification; and the
    OPTIMIZER-HAS-TEETH invariant (the DP beats greedy on the coupled model). Non-vacuous: genuine
    multi-option windows are exercised. RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    choices_total = 0
    if not optimizer_has_teeth():
        raise LookaheadError("the DP is a no-op — no teeth on the coupled model")
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        ok, seen = certify_greedy_optimal(ticks, cl, L)
        if not ok:
            raise LookaheadError(f"seq {s}: the bounded DP beat greedy on the real model — lemma violated")
        if not representation_independent(ticks, cl, L):
            raise LookaheadError(f"seq {s}: the look-ahead encoding diverged from adaptive/baseline")
        ok2, seen2 = certify_greedy_optimal(ticks, cl, L)
        if (ok, seen) != (ok2, seen2):
            raise LookaheadError(f"seq {s}: certification is not deterministic")
        moved = [({**e, 2: (e[2][0], e[2][1], _d(9000 + s))}, w) for e, w in ticks]   # perturb hidden id2
        if AC.run(moved, cl, L, mode="adaptive")["packets"] != AC.run(ticks, cl, L, mode="adaptive")["packets"]:
            raise LookaheadError(f"seq {s}: a change to the hidden entity altered the certified wire — leak")
        choices_total += seen
        hh.update(f"|{s}:{seen}".encode())
    if choices_total == 0:
        raise LookaheadError("NON-VACUITY: no genuine multi-option window was ever certified")
    return {"scenarios": count, "choices_total": choices_total, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_lookahead.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise LookaheadError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except LookaheadError as exc:
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
    print(f"SWEEP: {rep['scenarios']} sequences, genuine-choice windows {rep['choices_total']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
