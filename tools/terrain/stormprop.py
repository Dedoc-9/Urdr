# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""stormprop — THE PROPERTY-BASED FALSIFIER STAGE for the storm's PREFIX PROPERTY (Tier-2, URDRSTP1):
equal-or-refuse under chaos, swept. `storm` (URDRSTM1) proves that a wire client under a seeded
adversarial transport (loss / duplication / reorder / delay) either converges to the authority's
witness or freezes each gapped region at the authority's PREFIX — but it checks FOUR curated seeds.
The pre-mesh hardening review's technical #1: sweep the seed space with an INDEPENDENT oracle, so the
equal-or-refuse thesis faces an adversary actively searching for the counterexample before the mesh
introduces concurrent, partitionable authorities.

THE LAWS SWEPT. A seeded generator mints random storms — `(seed, loss%, dup%, delay_max)` — and drives
ONE honest wire client (`storm.run_client`, the landed `wire.client_admit` UNMODIFIED) through each:

  * LOSS-FREE convergence — with loss=0, chaos (reorder + duplication) notwithstanding, the client's
    replica witness equals the AUTHORITY'S OWN witness and every update is admitted EXACTLY ONCE. The
    oracle is `storm.authority_log`'s `want` — the authority's direct witness, not the loom's.
  * THE PREFIX PROPERTY — with loss>0, the client's replica equals `storm.prefix_witness`: per region,
    the authority's prefix up to the first dropped in-region update — NO state the authority never had.
    `prefix_witness` is the INDEPENDENT ORACLE (the anti-Goodhart rule): it is computed WITHOUT the
    retry loom, so a bug in the loom cannot hide inside its own answer.

LOAD-BEARING (the prefix property is not decoration): in a lossy storm with a real gap the prefix is
STRICTLY BELOW the full authority log (`prefix_witness != want`), so a broken client that silently
admitted past a gap would converge to `want` and be CAUGHT by `replica == prefix_witness`. The sweep
asserts this strict-prefix case occurs (`prefix_ne_want > 0`) — else the two branches would be
indistinguishable and the test vacuous.

NON-VACUITY is asserted, not hoped: the sweep must exercise BOTH branches (lossy and loss-free), and
the storm must be REAL — nonzero total drops, reorderings, duplicates, and detected stalls (a gap with
a record queued behind it, frozen and counted). A becalmed or single-branch sweep raises.

THE GENERATOR uses the HIGH bits of an integer LCG for small-range draws (an LCG's low bits cycle with
tiny period — degenerate for small moduli). Seeds are LCG-drawn bytes, so the whole sweep is a pure,
host-deterministic integer function — byte-identical in-gate.

GRADE. Both laws over the fixed-seed sweep, the load-bearing strict-prefix check, the non-vacuity
counters, and the aggregate-digest determinism are MEASURED (exact, reproducible, a defect diverges —
the gate re-derives the sweep). The IN-GATE sweep is fixed-seed (byte-identical); the OFF-GATE
`--explore` reseeds and files the first counterexample as a pinned scene. DECLARED: SAMPLING over the
storm space, not a proof over all storms — MEASURED stays "the prefix property survived N seeded storms
on a named host." does_not_show: the off-gate explorer (declared, not gate-run); malice injection (the
`storm` maelstrom scene owns the tampered/foreign-record refusals); cross-placement (URDRSTP1 is Python
reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSTP1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _p in (_HERE, _os.path.join(_os.path.dirname(_HERE), "physics")):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import storm as _ST                                            # the loom + the independent prefix oracle

SEED = 20260721
COUNT = 200
CSIZE = 8


class SweepError(Exception):
    def __init__(self, message):
        super().__init__(f"STORMPROP-FALSIFIED: {message}")
        self.code = "STORMPROP-FALSIFIED"


class _LCG:
    """Deterministic integer LCG; small-range draws use the HIGH bits (low bits cycle with tiny
    period). `seed_bytes` mints a 4-byte storm seed from the same stream."""
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))

    def seed_bytes(self):
        return self.nxt().to_bytes(4, "big")


def sweep(seed=SEED, count=COUNT, oracle=None):
    """Run the storm prefix-property sweep: `count` random storms driven through one honest wire
    client. RAISES `SweepError` on the first law violation OR non-vacuity failure; returns the
    aggregate dict on success. `oracle` overrides `storm.prefix_witness` for the selftest (a wrong
    oracle must make the sweep raise). The digest is SHA-256 over the ordered (loss,dup,delay | replica
    witness) of every scenario."""
    prefix_oracle = oracle if oracle is not None else _ST.prefix_witness
    fld = _ST._blank()
    updates, want = _ST.authority_log(fld, CSIZE)
    r = _LCG(seed)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|want:{want}".encode())
    lossy = lossfree = drops = reorder = dup = stalled = prefix_ne_want = 0
    for s in range(count):
        sd = r.seed_bytes()
        loss = r.rng(10, 35) if r.rng(0, 1) else 0
        dpct = r.rng(0, 40)
        delay = r.rng(0, 6)
        sched = _ST.schedule(sd, len(updates), loss_pct=loss, dup_pct=dpct, delay_max=delay)
        m = _ST.measure(sched)
        out = _ST.run_client(fld, CSIZE, updates, sched)
        rep = _ST._WR.replica_witness(out["client"])
        drops += m["drops"]; reorder += m["reorderings"]; dup += m["duplicates"]; stalled += out["stalled"]
        if loss == 0:
            if rep != want:
                raise SweepError(f"scenario {s} (loss-free): the replica did not converge to the "
                                 f"authority witness under reorder/dup chaos")
            if out["admitted"] != len(updates):
                raise SweepError(f"scenario {s} (loss-free): {out['admitted']} admitted, expected "
                                 f"exactly-once {len(updates)}")
            lossfree += 1
        else:
            exp = prefix_oracle(fld, CSIZE, updates, sched)
            if rep != exp:
                raise SweepError(f"scenario {s} (lossy {loss}%): the replica is NOT the authority "
                                 f"prefix — a state the authority never had, or a frozen gap released")
            if exp != want:
                prefix_ne_want += 1
            lossy += 1
        hh.update(f"|{s}:{loss},{dpct},{delay}:{rep}".encode())
    if lossy == 0 or lossfree == 0:
        raise SweepError(f"NON-VACUITY: lossy={lossy}, lossfree={lossfree} — both branches must occur")
    if not (drops > 0 and reorder > 0 and dup > 0 and stalled > 0):
        raise SweepError(f"NON-VACUITY: chaos too weak (drops={drops}, reorder={reorder}, "
                         f"dup={dup}, stalled={stalled}) — the storm did not storm")
    if prefix_ne_want == 0:
        raise SweepError("NON-VACUITY: no lossy prefix was strictly below the full log — the prefix "
                         "property would be indistinguishable from loss-free convergence")
    return {"scenarios": count, "lossy": lossy, "lossfree": lossfree, "drops": drops,
            "reorder": reorder, "dup": dup, "stalled": stalled, "prefix_ne_want": prefix_ne_want,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SEED, count=COUNT):
    return sweep(seed, count)["digest"]


def golden():
    with open(_os.path.join(_HERE, "conformance_stormprop.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise SweepError("no golden named 'sweep'")


# ---- the OFF-GATE reseeded explorer (declared; NOT gate-run) -----------------------------
def explore(base_seed, n_seeds, count=COUNT):
    """Reseed across `n_seeds` seeds; return counterexamples (each a (seed, message)). The laws are
    expected to hold, so the list is normally empty — a found counterexample is filed as a pinned scene."""
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
                  f"the prefix property held on every storm.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg in found:
                print(f"  seed={seed}: {msg}")
        return 0
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} storms (lossy={rep['lossy']} lossfree={rep['lossfree']}), "
          f"drops={rep['drops']} reorder={rep['reorder']} dup={rep['dup']} stalled={rep['stalled']} "
          f"strict-prefix={rep['prefix_ne_want']}")
    print(f"digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(_sys.argv))
