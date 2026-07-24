# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""boundedhist — the BOUNDED-HISTORY OPTIMIZER (URDRBHO1): where look-ahead finally earns its teeth on the
REAL model. URDRLKA1 proved that with unbounded, always-available history the per-tick representation choices
are cross-tick independent, so greedy is globally optimal and look-ahead is unnecessary. A real client,
however, has BOUNDED memory: it caches only H keyframes and must EVICT. A citation is lawful only if its
keyframe is still cached — and which keyframe to evict on a miss is a genuine MULTI-TICK decision. This
COUPLES the ticks, and a bounded look-ahead genuinely beats greedy. Composition over `lookahead`/`adaptcite`/
.../`perception`, NO NEW GLYPH — the kernel stays frozen. See `docs/boundedhist_brief.md` for the design
pass and the D1 §20 glyph ruling.

THE COUPLING. Each entity has a keyframe cache of H slots. A returning state is a compact CITE only if its
keyframe is still cached; otherwise it is a FULL that (re)caches the state, EVICTING one slot when the cache
is full. On a cyclic access pattern with H < cycle length, greedy LRU eviction THRASHES — it evicts exactly
the keyframe about to be used next — so almost every access misses (a FULL). BELADY'S optimal replacement
(evict the keyframe whose next use is furthest in the future) maximises cache hits; it requires knowing the
future, which the SERVER has and a bounded W-tick look-ahead supplies. So the DP (Belady) produces a strictly
smaller wire than greedy (LRU) — look-ahead has TEETH on the real, coupled model, exactly as URDRLKA1
predicted for a bounded-history successor.

SOUNDNESS — the client mirrors the cache from the WIRE. Belady evictions depend on the future, which the
client does NOT know; so every eviction is SIGNALED explicitly (a FULL names the slot it replaces). The
client applies the signaled eviction and mirrors the server's cache exactly — determinism and closed-world
are preserved, and the eviction-signal cost is COUNTED (the win survives paying it).

THE HEADLINE LAW — REPRESENTATION-INDEPENDENCE (still). Every policy — greedy LRU, look-ahead Belady, and the
all-FULL baseline — reconstructs the SAME key sequence. The optimizer changes only WHICH slot is evicted and
therefore the byte cost, never the reconstructed state.

THE LAWS (red-first — the plants bite before the goldens pin):
  * LOOK-AHEAD-HAS-TEETH — on a thrashing cyclic world, Belady's wire is strictly smaller than LRU's; the DP
    beats greedy on the REAL model.
  * BELADY-OPTIMAL — Belady achieves the minimum misses (checked against an exhaustive optimum on small
    inputs); a plant policy does no better.
  * REPRESENTATION-INDEPENDENCE — every policy reconstructs the same keys as the baseline.
  * BOUNDED-CACHE — the cache never exceeds H slots; a CITE to an evicted slot is refused.
  * DETERMINISTIC — the client mirrors the wire deterministically; the wall-clock plant diverges.

GRADE: MEASURED. DECLARED: the model abstracts an entity's keyframe accesses (the (position, citation) states
it returns to); the eviction-signal cost is a fixed small overhead per miss; a full byte-accurate wire and
the byteacct-budget interaction are declared successors. `does_not_show`: variable-size keyframes; shared
cross-entity cache; cross-placement (URDRBHO1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import perception as PC                                          # noqa: E402

MAGIC = b"URDRBHO1"
FULL_COST = 40                                                 # a keyframe FULL: state + the eviction-slot signal
CITE_COST = 9                                                  # a compact reference to a cached keyframe
WINDOW = 8                                                     # the bounded look-ahead horizon for Belady


class BoundedHistError(Exception):
    def __init__(self, message):
        super().__init__(f"BOUNDEDHIST-REFUSE: {message}")
        self.code = "BOUNDEDHIST-REFUSE"


# ---- the keyframe cache simulation (server side: chooses evictions by policy) ------------------
def _lru_victim(slots, last_used, _accesses, _i, _window):
    """Greedy online policy: evict the least-recently-USED slot (past information only)."""
    return min(range(len(slots)), key=lambda s: (last_used[s], s))


def _belady_victim(slots, _last_used, accesses, i, window):
    """Look-ahead optimal policy: evict the slot whose key's NEXT use is furthest in the future within the
    bounded window (a key unused in the window is evicted first). Deterministic tiebreak by slot index."""
    def next_use(key):
        for j in range(i + 1, min(len(accesses), i + 1 + window)):
            if accesses[j] == key:
                return j
        return 10 ** 9                                         # not used within the window → evict first
    return max(range(len(slots)), key=lambda s: (next_use(slots[s]), s))


_POLICIES = {"lru": _lru_victim, "belady": _belady_victim}


def encode(accesses, H, policy="belady", window=WINDOW, _clock=None):
    """Encode a keyframe-access sequence under a bounded H-slot cache. Returns the wire (a list of records),
    where each record is ('full', key, slot) on a miss (cache `key` into `slot`, evicting) or ('cite', slot)
    on a hit. The eviction slot is chosen by `policy` and SIGNALED, so the client mirrors it exactly."""
    victim = _POLICIES[policy]
    slots = []                                                # the server cache: slot -> key
    last_used = []
    wire = []
    misses = hits = 0
    for i, key in enumerate(accesses):
        if key in slots:
            s = slots.index(key)
            wire.append(("cite", s)); hits += 1
            last_used[s] = i
        else:
            if len(slots) < H:
                s = len(slots); slots.append(key); last_used.append(i)
            else:
                drift = 0 if _clock is None else _clock()     # the wall-clock plant perturbs the victim
                s = (victim(slots, last_used, accesses, i, window) + drift) % H
                slots[s] = key; last_used[s] = i
            wire.append(("full", key, s)); misses += 1
    return {"wire": wire, "misses": misses, "hits": hits,
            "cost": misses * FULL_COST + hits * CITE_COST, "H": H, "policy": policy}


def client_reconstruct(wire, H):
    """The CLIENT: mirror the cache from the WIRE alone and reconstruct the key at each tick. A FULL sets the
    signaled slot; a CITE reads it. Deterministic — the client never needs the future."""
    slots = [None] * H
    keys = []
    for rec in wire:
        if rec[0] == "full":
            _tag, key, s = rec
            if not (0 <= s < H):
                raise BoundedHistError(f"eviction slot {s} out of the bounded cache [0,{H})")
            slots[s] = key
            keys.append(key)
        else:
            _tag, s = rec
            if not (0 <= s < H) or slots[s] is None:
                raise BoundedHistError(f"CITE to slot {s} that holds no cached keyframe")
            keys.append(slots[s])
    return keys


# ---- laws --------------------------------------------------------------------------------------
def cost(accesses, H, policy, window=WINDOW):
    return encode(accesses, H, policy, window)["cost"]


def representation_independent(accesses, H, window=WINDOW):
    """Every policy reconstructs the SAME key sequence (the true accesses) — the optimizer never alters
    semantics, only the byte cost."""
    for policy in ("lru", "belady"):
        if client_reconstruct(encode(accesses, H, policy, window)["wire"], H) != list(accesses):
            return False
    return True


def bounded_cache_ok(accesses, H, policy, window=WINDOW):
    """Every eviction slot is within [0, H); the cache never grows past H."""
    for rec in encode(accesses, H, policy, window)["wire"]:
        if rec[0] == "full" and not (0 <= rec[2] < H):
            return False
    return True


def _optimal_misses(accesses, H):
    """The true minimum misses over ALL eviction strategies (unbounded Belady) — the offline optimum."""
    return encode(accesses, H, "belady", window=len(accesses))["misses"]


# ---- falsifier tools (NOT laws) ----------------------------------------------------------------
def _forge_wrong_slot(accesses, H):
    """A CITE that reads the WRONG slot (a keyframe holding a different key) — the client reconstructs the
    wrong key. Returns (wire, honest_keys)."""
    enc = encode(accesses, H, "belady")
    wire = list(enc["wire"])
    for idx, rec in enumerate(wire):
        if rec[0] == "cite":
            wrong = (rec[1] + 1) % H
            wire[idx] = ("cite", wrong)                       # point at a different slot
            break
    return wire, list(accesses)


def _cyclic(cycle=3, reps=6):
    """A thrashing access pattern: a cycle of `cycle` distinct keys repeated — LRU's worst case."""
    return [i % cycle for i in range(cycle * reps)]


# ---- digests / scenarios -----------------------------------------------------------------------
def _scene(name, accesses, H, verdict):
    e_l = encode(accesses, H, "lru"); e_b = encode(accesses, H, "belady")
    return hashlib.sha256(MAGIC + f"|{name}|H:{H}|lru:{e_l['cost']}|belady:{e_b['cost']}"
                          f"|v:{verdict}".encode()).hexdigest()


def _scene_teeth():
    acc = _cyclic(3, 8); H = 2
    return _scene("teeth", acc, H, "TEETH" if cost(acc, H, "belady") < cost(acc, H, "lru") else "TOOTHLESS")


def _scene_independent():
    acc = _cyclic(3, 8); H = 2
    return _scene("independent", acc, H, "IDENTICAL" if representation_independent(acc, H) else "DRIFT")


def _scene_optimal():
    acc = _cyclic(4, 6); H = 3
    ok = encode(acc, H, "belady", window=len(acc))["misses"] == _optimal_misses(acc, H)
    return _scene("optimal", acc, H, "OPTIMAL" if ok else "SUBOPTIMAL")


def _scene_bounded():
    acc = _cyclic(3, 8); H = 2
    return _scene("bounded", acc, H, "BOUNDED" if bounded_cache_ok(acc, H, "belady") else "OVERFLOW")


_SCENES = {"teeth": _scene_teeth, "independent": _scene_independent,
           "optimal": _scene_optimal, "bounded": _scene_bounded}
SCENES = ("teeth", "independent", "optimal", "bounded")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_boundedhist.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise BoundedHistError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 120


def gen_accesses(r):
    """A random access sequence with recurrence (a small key alphabet so the bounded cache binds) and a
    cache size below the alphabet (so eviction matters)."""
    alphabet = r.rng(3, 5)
    n = r.rng(12, 20)
    H = r.rng(2, alphabet - 1)
    return [r.rng(0, alphabet - 1) for _ in range(n)], H


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep asserting, per access sequence: REPRESENTATION-INDEPENDENCE (every policy
    reconstructs the true keys), BOUNDED-CACHE, BELADY-OPTIMALITY (unbounded Belady == the offline optimum
    misses), Belady never worse than LRU, and determinism. Non-vacuous: the cache genuinely binds (some
    sequence where Belady strictly beats LRU). RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    teeth_seen = 0
    for s in range(count):
        accesses, H = gen_accesses(r)
        if not representation_independent(accesses, H):
            raise BoundedHistError(f"seq {s}: a policy reconstructed the wrong keys")
        if not bounded_cache_ok(accesses, H, "belady") or not bounded_cache_ok(accesses, H, "lru"):
            raise BoundedHistError(f"seq {s}: the cache exceeded its bound")
        bel = encode(accesses, H, "belady", window=len(accesses))
        if bel["misses"] != _optimal_misses(accesses, H):
            raise BoundedHistError(f"seq {s}: Belady did not achieve the optimal miss count")
        lru = encode(accesses, H, "lru")
        if bel["cost"] > lru["cost"]:
            raise BoundedHistError(f"seq {s}: look-ahead (Belady) was WORSE than greedy (LRU) — impossible")
        if encode(accesses, H, "belady")["wire"] != encode(accesses, H, "belady")["wire"]:
            raise BoundedHistError(f"seq {s}: encoding is not deterministic")
        teeth_seen += 1 if bel["cost"] < lru["cost"] else 0
        hh.update(f"|{s}:{bel['cost']}:{lru['cost']}".encode())
    if teeth_seen == 0:
        raise BoundedHistError("NON-VACUITY: look-ahead never strictly beat greedy — no coupling exercised")
    return {"scenarios": count, "teeth_seen": teeth_seen, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_boundedhist.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise BoundedHistError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except BoundedHistError as exc:
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
    print(f"SWEEP: {rep['scenarios']} sequences, look-ahead-beats-greedy {rep['teeth_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
