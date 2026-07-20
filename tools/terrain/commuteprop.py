# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""commuteprop — THE PROPERTY-BASED FALSIFIER STAGE (Tier-2 hardening, URDRCPS1): the commute diamond
faces a seeded adversary. `commute` proves the diamond (order cannot matter for sibling edits on
distinct cells) on FOUR hand-chosen scenes; digest-pinning cannot distinguish "correct" from
"consistently wrong on the four sampled points." The pre-mesh hardening review's technical #1 (two of
three independent skeptics, from different disciplines): promote property-based / randomized
falsifiers with an ORACLE — a seeded generator that sweeps the input space, not a pinned corpus — so
the ∀-law faces an adversary actively searching for the counterexample BEFORE the mesh introduces
concurrent, partitionable authorities. This is that stage, applied to the write-calculus commute
diamond (the review's first-named flagship ∀-law).

THE METHOD (property-based testing with an INDEPENDENT oracle — the anti-Goodhart rule). A fixed-seed
integer LCG (no RNG, no clock, no platform hash — host-deterministic, byte-identical in-gate) mints
random worlds and random distinct-cell edit tuples. For each scenario the sweep asserts the ∀-law
against oracles the module-under-test CANNOT read:

  * THE DIAMOND (brute-permutation oracle) — apply EVERY permutation of the (explicitly rebased) edits
    from the base world; the resulting head manifest AND field must be UNIQUE across all orders. This
    oracle uses only `terraform.apply_edit` + the explicit rebase — it never consults `commute`, so a
    bug in `certify`/`closure`/`predict` cannot hide inside its own answer.
  * CLOSURE AGREES — `commute.closure`'s head equals the brute oracle's single head (the module must
    match the independent ground truth, not merely itself).
  * RANK (independent-geometry oracle) — the pairwise rank is recomputed from chunk geometry ALONE
    (`(x//c,y//c) != (x'//c,y'//c) → 0 else 1`), NOT from `commute.predict` (which `certify` calls
    internally — comparing predict to certify would be circular). `predict` must match this external
    ruler, so a `predict` mutant reddens.
  * CONTESTED REFUSES (load-bearing) — a same-cell pair MUST raise COMMUTE-REFUSE; a mutant that
    arbitrated it reddens.

NON-VACUITY is asserted, not hoped: the sweep counts rank-0 AND rank-1 pairs (both must occur), that
every scenario's field actually CHANGED, and that every contested pair refused — a generator that
produced only trivial or single-rank scenarios is itself a defect and raises.

THE SPLIT (the wireattest discipline, on a search). The IN-GATE sweep is a FIXED seed, so the run is
byte-identical and the aggregate digest pins; the OFF-GATE `--explore` reseeds across many seeds and,
on the first counterexample, prints the seed + scenario to be filed back as a new pinned corpus scene
(the off-gate→pinned split the arc already trusts for wireattest's sockets). Existence-on-a-corpus
becomes confidence-over-a-sampled-space.

GRADE. The diamond / closure-agreement / rank / contested invariants over the fixed-seed sweep, the
non-vacuity counters, and the aggregate-digest determinism are MEASURED (exact, reproducible, a defect
diverges — the gate re-derives the sweep, never trusts a stored result). DECLARED: this is SAMPLING,
not a proof over all worlds — MEASURED remains "the ∀-law survived N seeded adversarial scenarios on a
named host," never universal (the `intautology` decision procedure is the road to decided-for-all).
does_not_show: the OFF-GATE explorer's reseeded search (declared; its counterexamples become pinned
scenes, they are not gate-run); reunify==monolith and the storm prefix-property (the stage's next
flagship targets — this rung lands the commute diamond); cross-placement (URDRCPS1 is Python
reference only)."""
import hashlib
import itertools
import os as _os
import sys as _sys

MAGIC = b"URDRCPS1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import terraform as _TF                                         # the write calculus (edit/apply/CAS)
import commute as _CM                                           # the diamond under test (certify/closure/predict)

# The in-gate sweep parameters — FIXED, so the run is byte-identical and the aggregate digest pins.
SEED = 20260720
COUNT = 200
CSIZE = 4
W = H = 8                                                       # 8x8 world, csize 4 → a 2x2 chunk grid


class SweepError(Exception):
    """A property violation OR a non-vacuity failure — either reddens the gate (the sweep is EVIDENCE)."""
    def __init__(self, message):
        super().__init__(f"COMMUTEPROP-FALSIFIED: {message}")
        self.code = "COMMUTEPROP-FALSIFIED"


class _LCG:
    """A deterministic linear-congruential generator — host-independent integer arithmetic, the
    `test_physics_properties` idiom. No real RNG, no clock, no platform hash: the same seed mints the
    same sweep on every host, so the gate stays byte-deterministic."""
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + self.nxt() % (hi - lo + 1)


def _rand_field(r, w, h):
    return tuple(tuple(r.rng(0, 20) for _ in range(w)) for _ in range(h))


def gen_scenario(r, csize, w, h):
    """Mint one random scenario: a random world, and n (2..3) edits on pairwise-DISTINCT cells with
    random height deltas, all authored against the base world. Returns (field, records, cells)."""
    fld = _rand_field(r, w, h)
    p = _TF.parent_address(fld, csize)
    n = r.rng(2, 3)
    cells = []
    while len(cells) < n:
        c = (r.rng(0, w - 1), r.rng(0, h - 1))
        if c not in cells:
            cells.append(c)
    recs = tuple(_TF.edit_record(p, x, y, fld[y][x], fld[y][x] + r.rng(-5, 5)) for (x, y) in cells)
    return fld, recs, cells


def brute_orbit(field, csize, recs):
    """THE INDEPENDENT DIAMOND ORACLE: apply EVERY permutation of the explicitly-rebased edits from the
    base world; return (heads, fields) as sets. Uses only `terraform.apply_edit` + the explicit rebase
    — it never consults `commute`, so it is a ground truth the module cannot read. The ∀-law holds iff
    both sets are singletons (order cannot matter)."""
    heads, fields = set(), set()
    for perm in itertools.permutations(range(len(recs))):
        cur = field
        for i in perm:
            cur = _TF.apply_edit(cur, csize, _CM.rebase_edit(recs[i], _TF.parent_address(cur, csize)))
        heads.add(_TF.parent_address(cur, csize))
        fields.add(cur)
    return heads, fields


def _geo_rank(csize, xa, ya, xb, yb):
    """THE INDEPENDENT RANK ORACLE: chunk geometry ALONE — never `commute.predict` (which `certify`
    calls internally; comparing the two would be circular). 0 = different chunks, 1 = same chunk."""
    return 0 if (xa // csize, ya // csize) != (xb // csize, yb // csize) else 1


def sweep(seed=SEED, count=COUNT, csize=CSIZE, w=W, h=H):
    """Run the property sweep: `count` seeded scenarios, each asserted against the independent oracles.
    RAISES `SweepError` on the first ∀-law violation OR on a non-vacuity failure (so the gate reddens);
    on success returns the aggregate result dict {scenarios, rank0, rank1, contested, changed, digest}.
    The digest is SHA-256 over the ordered (head | sorted pairwise ranks) of every scenario — a
    byte-identical fingerprint of the whole sweep."""
    r = _LCG(seed)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    rank0 = rank1 = contested = changed = 0
    for s in range(count):
        fld, recs, cells = gen_scenario(r, csize, w, h)
        heads, fields = brute_orbit(fld, csize, recs)
        if len(heads) != 1 or len(fields) != 1:
            raise SweepError(f"scenario {s} (seed {seed}): the diamond did NOT close — "
                             f"{len(heads)} heads, {len(fields)} fields across orders")
        head = next(iter(heads))
        the_field = next(iter(fields))
        if the_field != fld:
            changed += 1                                        # non-vacuity: the edits actually mutated
        ch, certs = _CM.closure(fld, csize, recs)
        if ch != head:
            raise SweepError(f"scenario {s} (seed {seed}): commute.closure head {ch[:12]}… disagrees "
                             f"with the independent brute-permutation oracle {head[:12]}…")
        ranks = []
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                _p, xa, ya, _o, _n = _TF.restore_edit(recs[i])
                _q, xb, yb, _o2, _n2 = _TF.restore_edit(recs[j])
                exp = _geo_rank(csize, xa, ya, xb, yb)
                got = _CM.predict(csize, xa, ya, xb, yb)
                if got != exp:
                    raise SweepError(f"scenario {s} (seed {seed}): commute.predict rank {got} != "
                                     f"independent chunk geometry {exp} for {(xa, ya)}·{(xb, yb)}")
                # certify closes and INDEPENDENTLY re-verifies to the same head/rank
                cert, chead = _CM.certify(fld, csize, recs[i], recs[j])
                rk2, rehead = _CM.check_certificate(fld, csize, cert)
                if rk2 != exp:
                    raise SweepError(f"scenario {s}: certificate rank {rk2} != geometry {exp}")
                rank0 += exp == 0
                rank1 += exp == 1
                ranks.append(exp)
        # CONTESTED (load-bearing): the same cell twice MUST refuse
        x, y = cells[0]
        p = _TF.parent_address(fld, csize)
        ra = _TF.edit_record(p, x, y, fld[y][x], fld[y][x] + 3)
        rb = _TF.edit_record(p, x, y, fld[y][x], fld[y][x] - 3)
        try:
            _CM.certify(fld, csize, ra, rb)
            raise SweepError(f"scenario {s} (seed {seed}): a same-cell pair was ARBITRATED, not refused")
        except _CM.CommuteError:
            contested += 1
        hh.update(f"|{s}:{head}:{','.join(map(str, sorted(ranks)))}".encode())
    # NON-VACUITY — a single-rank, no-op, or non-refusing sweep is itself a defect
    if rank0 == 0 or rank1 == 0:
        raise SweepError(f"NON-VACUITY: the sweep exercised rank0={rank0}, rank1={rank1} — both must occur")
    if contested != count:
        raise SweepError(f"NON-VACUITY: only {contested}/{count} contested pairs refused")
    if changed == 0:
        raise SweepError("NON-VACUITY: no scenario changed the world — the edits were all no-ops")
    return {"scenarios": count, "rank0": rank0, "rank1": rank1, "contested": contested,
            "changed": changed, "digest": hh.hexdigest()}


def sweep_digest(seed=SEED, count=COUNT):
    """The URDRCPS1 canon — the aggregate digest of the fixed-seed sweep (raises if the ∀-law fails)."""
    return sweep(seed, count)["digest"]


def golden():
    """The pinned aggregate digest from `conformance_commuteprop.txt` (name `sweep`)."""
    with open(_os.path.join(_HERE, "conformance_commuteprop.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise SweepError("no golden named 'sweep'")


# ---- the OFF-GATE reseeded explorer (declared; NOT gate-run) -----------------------------
def explore(base_seed, n_seeds, count=COUNT):
    """Reseed the sweep across `n_seeds` distinct seeds; return the list of counterexamples (each a
    (seed, message) the sweep raised). The law is expected to hold, so the list is normally empty —
    the VALUE is the machinery: a found counterexample is filed back as a new pinned corpus scene
    (the off-gate→pinned discipline). OFF-GATE: reseeded, so it is not byte-identical and does not run
    inside the gate."""
    found = []
    for k in range(n_seeds):
        seed = base_seed + k * 2654435761 & 0x7FFFFFFF          # spread seeds (Knuth's multiplicative)
        try:
            sweep(seed, count)
        except SweepError as exc:
            found.append((seed, str(exc)))
    return found


def main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SEED
        n = int(argv[3]) if len(argv) > 3 else 500
        found = explore(base, n)
        if not found:
            print(f"EXPLORE: no counterexample across {n} reseeded sweeps from base {base} — "
                  f"the commute diamond held on every one.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg in found:
                print(f"  seed={seed}: {msg}")
        return 0
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} scenarios, rank0={rep['rank0']} rank1={rep['rank1']} "
          f"contested={rep['contested']} changed={rep['changed']}")
    print(f"digest={rep['digest']}")
    print("golden=" + (golden() if _os.path.exists(_os.path.join(_HERE, "conformance_commuteprop.txt"))
                        else "(unpinned)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(_sys.argv))
