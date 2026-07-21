# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""regionprop — THE PROPERTY-BASED FALSIFIER STAGE for the Seam Composition Theorem (Tier-2, URDRRGP1):
reunify == monolith under a seeded adversary. `worldregion` (D16) proves that ANY valid spatial
partition of an authoritative world reunifies to the monolithic witness bit-for-bit — but the gate
checks it on SIX hand-chosen seams. The pre-mesh hardening review's technical #1: promote the ∀-law
from existence-on-a-corpus to confidence-over-a-sampled-space, with an INDEPENDENT oracle, before the
mesh introduces concurrent authorities that partition for real.

THE LAW SWEPT (the Seam Composition Theorem, D16): for any valid partition `seams` of the in-scope
world, `worldregion.region_simulate(w, log, seams)` equals `worldstep.simulate(w, log)` — the
MONOLITH — bit-for-bit. The monolith is the INDEPENDENT ORACLE (the anti-Goodhart rule): it never
partitions, never admits a ghost, never consults `worldregion`, so a bug in the regional tick cannot
hide inside its own answer. A seeded integer generator mints random valid partitions (strictly-
increasing integer x-seams, 0..3 seams → 1..4 regions) and asserts every one composes to the monolith.

SCOPE (declared, honest): the sweep varies the PARTITION, not the world — `worldregion` states its
per-region contact pass is exact for the single-cross-seam-pair regime of the in-scope `seam2` scene
(multi-pair seam ordering is a declared successor). Randomising arbitrary worlds could mint scenes
outside that regime and falsely "falsify" a law that is only DECLARED there. So the quantifier swept is
the theorem's own — ∀ valid partition — over the in-scope world; that is exactly the "random partitions"
the review named.

NON-VACUITY is asserted, not hoped: the sweep must exercise at least three distinct region counts (a
generator stuck on one partition shape is a defect), and the monolith must genuinely EVOLVE (its frame
chain has more than one distinct frame — a static world would make composition trivial). RED-FIRST: the
dropped-boundary defect (`defect_drop_ghost`) diverges from the monolith, and a malformed partition is
REGION-REFUSEd before a tick runs — both proven to make the sweep raise before the golden pinned.

THE GENERATOR uses the HIGH bits of an integer LCG for its small-range draws: an LCG's LOW bits cycle
with tiny period, so `nxt() % k` for small k is degenerate (this was caught making every partition the
same shape; `nxt() >> 16 % k` fixes it) — recorded as an engineering-rigor find.

GRADE. The theorem over the fixed-seed sweep, the non-vacuity counters, and the aggregate-digest
determinism are MEASURED (exact, reproducible, a defect diverges — the gate re-derives the sweep). The
IN-GATE sweep is fixed-seed (byte-identical); the OFF-GATE `--explore` reseeds and files the first
counterexample as a pinned scene. DECLARED: SAMPLING over partitions of the in-scope world, not a proof
over all worlds — MEASURED stays "the theorem survived N seeded partitions on a named host." does_not_show:
the off-gate explorer (declared, not gate-run); world randomisation beyond the single-pair regime;
cross-placement (URDRRGP1 is Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRRGP1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import worldregion as _R                                        # the regional tick under test
import worldstep as _WS                                        # the MONOLITHIC oracle (never partitions)
import lockstep as _L                                          # the frozen witness-chain digest

SEED = 20260721
COUNT = 200


class SweepError(Exception):
    def __init__(self, message):
        super().__init__(f"REGIONPROP-FALSIFIED: {message}")
        self.code = "REGIONPROP-FALSIFIED"


class _LCG:
    """Deterministic integer LCG. Small-range draws use the HIGH bits (`nxt() >> 16`): an LCG's LOW
    bits cycle with tiny period, so `nxt() % k` for small k is degenerate — the high bits are not."""
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


def gen_seams(r):
    """A random VALID partition: 0..3 strictly-increasing integer x-seams (1..4 regions)."""
    nseam = r.rng(0, 3)
    seams, cur = [], r.rng(80, 120)
    for _ in range(nseam):
        seams.append(cur)
        cur += r.rng(5, 60)
    return seams


def sweep(seed=SEED, count=COUNT):
    """Run the Seam Composition sweep: `count` random valid partitions of the in-scope world, each
    asserted EQUAL to the monolith (the independent oracle). RAISES `SweepError` on the first partition
    that diverges OR on a non-vacuity failure; returns {scenarios, region_counts, frames, digest} on
    success. The digest is SHA-256 over the monolith witness + the ordered seams of every scenario."""
    w, log = _R.seam2_world(), _R.seam2_log()
    mono = _WS.simulate(w, log)                                 # the ORACLE, computed once
    frames = len(set(mono))
    if frames <= 1:
        raise SweepError("NON-VACUITY: the monolith did not evolve — composition would be trivial")
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|mono:{_L.trace_digest(mono)}".encode())
    region_counts = {}
    r = _LCG(seed)
    for s in range(count):
        seams = gen_seams(r)
        try:
            comp = _R.region_simulate(w, log, seams)
        except _R.RegionError as exc:
            raise SweepError(f"scenario {s}: a generated partition {seams} was refused ({exc.code}) — "
                             f"the generator must only mint VALID partitions")
        if comp != mono:
            raise SweepError(f"scenario {s} (seed {seed}): partition {seams} did NOT compose to the "
                             f"monolith — the Seam Composition Theorem is FALSIFIED")
        rc = len(seams) + 1
        region_counts[rc] = region_counts.get(rc, 0) + 1
        hh.update(f"|{s}:{','.join(map(str, seams))}".encode())
    if len(region_counts) < 3:
        raise SweepError(f"NON-VACUITY: only {len(region_counts)} distinct region counts — the "
                         f"generator is stuck on one partition shape")
    return {"scenarios": count, "region_counts": region_counts, "frames": frames,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SEED, count=COUNT):
    return sweep(seed, count)["digest"]


def golden():
    with open(_os.path.join(_HERE, "conformance_regionprop.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise SweepError("no golden named 'sweep'")


# ---- the OFF-GATE reseeded explorer (declared; NOT gate-run) -----------------------------
def explore(base_seed, n_seeds, count=COUNT):
    """Reseed the sweep across `n_seeds` seeds; return the counterexamples (each a (seed, message)).
    The theorem is expected to hold, so the list is normally empty — a found counterexample is filed
    back as a new pinned scene (the off-gate→pinned discipline)."""
    found = []
    for k in range(n_seeds):
        seed = base_seed + k * 2654435761 & 0x7FFFFFFF
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
                  f"reunify == monolith held on every partition.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg in found:
                print(f"  seed={seed}: {msg}")
        return 0
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} partitions, region counts {dict(sorted(rep['region_counts'].items()))}, "
          f"monolith frames {rep['frames']}")
    print(f"digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(_sys.argv))
