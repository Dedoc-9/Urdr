# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""mesh — THE MESHED SIMULATION (Phase M, rung M3, URDRMSH1): the capstone ∀-law MESH == MONOLITH. N
authorities own regions of one world and MIGRATE authority between each other over time; a meshed
simulation of concurrent per-tick writes composes to the SAME world witness a single monolithic
authority would compute — bit-for-bit — or refuses. This is the answer to server meshing that cannot
lie: not a best-effort convergence, but a THEOREM, re-derived in bytes.

M3 IS A COMPOSITION, not a new mechanism (the mesh brief's thesis, executed):
  * `nway` (M1) schedules the CONCURRENT writes of a tick — the independence lattice is the
    concurrency certificate: a tick's writes admit in parallel iff they form ONE independence round
    (pairwise-disjoint regions); an overlapping batch is not schedulable and the tick refuses WHOLE.
  * `migrate` (M2) moves authority between ticks — witness-neutral (a migration returns no world) —
    and gates EVERY write through the steward-checked conjunctive admission (lease AND custody chain);
    a non-steward's write refuses the WHOLE tick.
  * `terraform` is the MONOLITH ORACLE (the anti-Goodhart neutral ruler): it applies the same writes
    globally, IGNORING custody entirely — it never consults a steward, a lease, or a certificate, so a
    bug in the meshed tick cannot hide inside its own answer.

THE CAPSTONE THEOREM (guarantee #3). For any schedule of ticks — each a set of concurrent writes by the
current stewards on pairwise-disjoint regions, followed by a set of authority migrations — the meshed
world witness equals the monolith of the same writes, bit-for-bit. This GENERALIZES `regionprop`'s
reunify == monolith from a STATIC partition (fixed seams) to a MIGRATING one (the steward of a region
changes over time): authority mobility does not perturb the witness, because migration is witness-
neutral and concurrent disjoint writes are n-way null. The partition of WORK is fixed (the chunk grid);
the partition of AUTHORITY migrates; the witness is invariant to both.

THE TICK, in two phases: (1) WRITES — the current stewards write their own regions concurrently; the
records are certified ONE independence round (M1), each admitted steward-checked (M2), and — disjoint —
their order is immaterial (the shard path equals the monolith, M1's cross-check); (2) MIGRATIONS —
authority moves for the next tick, witness-neutral (the world manifest is untouched, asserted in bytes).

REFUSAL SEMANTICS, reject-whole (the regionprop atomicity discipline): a non-steward write, an
overlapping concurrent batch (two writes on one region in one tick), and a theft migration (a source
that is not the region's steward) each refuse the WHOLE tick typed `MESH-REFUSE` — a mesh tick admits
entirely or not at all, never a partial world.

GRADE (Phase M rung M3). MESH == MONOLITH over the pinned corpus and a seeded property sweep
(randomized steward layouts, tick schedules, concurrent write batches, and migration schedules, each
asserted against the independent monolith); witness-neutrality of migration at scale (the same writes
under any migration schedule land the same world); the one-independence-round concurrency certificate;
and the reject-whole refusals are MEASURED (exact, reproducible, a defect diverges — a custody-blind
monolith and a dropped write each make the sweep raise). DECLARED: the partitioned mesh + the CAP
liveness cost under a real partition (M4 — this rung is the CP posture's consistent, un-partitioned
composition); the attested mesh session (M5); scale (the mesh's CORRECTNESS is the claim; "thousands of
authorities" is MEASURED-on-a-named-host or it is not claimed). `does_not_show`: WHO may be a steward
(`sealwrit`/genesis fiat); cross-process transport (attested separately by `meshattest`, M2.5);
wall-clock (`bench.py`); cross-placement (URDRMSH1 is Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRMSH1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, manifests, addresses
import rannull as _RN                                           # regional records, authority
import terraform as _TF                                         # the MONOLITH oracle (neutral ruler)
import nway as _NW                                              # M1: the independence lattice
import migrate as _MG                                           # M2: steward-checked admit + migration

_C = 8


class MeshError(Exception):
    def __init__(self, message):
        super().__init__(f"MESH-REFUSE: {message}")
        self.code = "MESH-REFUSE"


def flat_world(side=32):
    return _NW.flat_world(side)


def _fresh(field):
    man = _CK.field_manifest(field, _C)
    store = {_CK.address(r): r for r in _CK.cut(field, _C).values()}
    return man, store


def _lease_and_rec(man, store, kx, ky, lx, ly, dh):
    x, y = kx * _C + lx, ky * _C + ly
    grid = _CK.parse_manifest(man)[3]
    chunk = store[grid[(kx, ky)]]
    old = _CK.restore_chunk(chunk)[2][ly][lx]
    return (_MG._LS.lease_from_chunk(chunk),
            _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh))


# ---- the mesh tick -----------------------------------------------------------------------
def _apply_one_write(sman, certs, man, store, writer, kx, ky, lx, ly, dh):
    """Steward-checked admission of ONE write (M2's conjunctive predicate). Returns
    (new_man, new_store, new_chunk). A non-steward raises `migrate.MigrateError` — caught by the tick
    and re-raised as a WHOLE-tick MESH-REFUSE."""
    ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
    new_man, ch = _MG.admit(sman, certs, man, dict(store), writer, ls, rec)
    new_store = dict(store)
    new_store[_CK.address(ch)] = ch
    return new_man, new_store, ch


def _tick_writes(sman, certs, man, store, writes):
    """The WRITES phase: certify the batch is ONE independence round (M1 — genuinely concurrent), then
    admit each steward-checked (M2). Disjoint → order-immaterial. Reject-whole on overlap or a
    non-steward. Returns (new_man, new_store, width)."""
    if not writes:
        return man, store, 0
    field_now = _CK.reassemble(man, store)
    recs = []
    for (_name, kx, ky, lx, ly, dh) in writes:
        recs.append(_lease_and_rec(man, store, kx, ky, lx, ly, dh)[1])
    try:
        auths = _NW.authorities(field_now, _C, recs)
    except _NW.NwayError as exc:
        raise MeshError(f"a tick write could not be certified: {exc}")
    if _NW.first_overlap(auths) is not None:
        i, j, inter = _NW.first_overlap(auths)
        raise MeshError(f"writes {i} and {j} share region {sorted(inter)} in ONE tick — an "
                        f"overlapping batch is not concurrent-schedulable; the tick refuses whole "
                        f"(successive ticks serialize a region)")
    if _NW.independence_rounds(field_now, _C, recs) != [tuple(range(len(recs)))]:
        raise MeshError("the tick's writes do not form ONE independence round — not genuinely "
                        "concurrent; the tick refuses whole")
    for (name, kx, ky, lx, ly, dh) in writes:
        try:
            man, store, _ch = _apply_one_write(sman, certs, man, store, _MG.steward_tag(name),
                                               kx, ky, lx, ly, dh)
        except _MG.MigrateError as exc:
            raise MeshError(f"{name} may not write region ({kx},{ky}): {exc} — the tick refuses whole")
    return man, store, len(writes)


def _tick_migrations(sman, certs, man, migrations):
    """The MIGRATIONS phase: authority moves for the next tick, witness-neutral. Theft (a source that
    is not the region's steward) refuses the whole tick. The world manifest MUST be untouched — asserted
    in bytes. Returns the new steward manifest."""
    before = _CK.address(man)
    for (kx, ky, src, dst) in migrations:
        try:
            sman2, cert = _MG.migrate(sman, certs, man, kx, ky, _MG.steward_tag(src),
                                      _MG.steward_tag(dst))
        except _MG.MigrateError as exc:
            raise MeshError(f"migration ({kx},{ky}) {src}->{dst} refused: {exc} — the tick refuses whole")
        certs[_MG.address(cert)] = cert
        sman = sman2
    if _CK.address(man) != before:
        raise MeshError("a migration moved the world witness — witness neutrality broken")
    return sman


def mesh_run(field, assignment, schedule):
    """THE MESHED SIMULATION. `assignment`: {(kx,ky): steward_name} genesis custody (total). `schedule`:
    a list of ticks, each {"writes": [(steward, kx, ky, lx, ly, dh), ...], "migrations": [(kx, ky, src,
    dst), ...]}. Returns {witness, custody, ticks, migrations, concurrent_writes, max_tick_width}, or
    raises MeshError (reject-whole)."""
    man, store = _fresh(field)
    try:
        sman = _MG.steward_genesis(man, {k: _MG.steward_tag(v) for k, v in assignment.items()})
    except _MG.MigrateError as exc:
        raise MeshError(f"genesis custody refused: {exc}")
    certs = {}
    migs = cwrites = maxw = 0
    for tick in schedule:
        man, store, width = _tick_writes(sman, certs, man, store, tick.get("writes", ()))
        sman = _tick_migrations(sman, certs, man, tick.get("migrations", ()))
        cwrites += width
        maxw = max(maxw, width)
        migs += len(tick.get("migrations", ()))
    return {"witness": _CK.address(man), "custody": _MG.address(sman), "ticks": len(schedule),
            "migrations": migs, "concurrent_writes": cwrites, "max_tick_width": maxw}


# ---- the monolith oracle (the neutral ruler — never consults custody) --------------------
def _monolith_apply(field, writes):
    """Apply a tick's writes GLOBALLY via terraform (the neutral ruler), ignoring custody entirely.
    `writes`: [(kx, ky, lx, ly, dh), ...] in canonical (region-sorted) order — disjoint, so order is
    immaterial. Exposed for the L15 plant (a dropped write must diverge)."""
    cur = field
    for (kx, ky, lx, ly, dh) in writes:
        x, y = kx * _C + lx, ky * _C + ly
        lifted = _TF.edit_record(_TF.parent_address(cur, _C), x, y, cur[y][x], cur[y][x] + dh)
        cur = _TF.apply_edit(cur, _C, lifted)
    return cur


def monolith(field, schedule):
    """THE INDEPENDENT ORACLE: the world a single monolithic authority computes from the same writes,
    custody ignored. Returns the final manifest address."""
    cur = field
    for tick in schedule:
        ws = sorted((kx, ky, lx, ly, dh) for (_n, kx, ky, lx, ly, dh) in tick.get("writes", ()))
        cur = _monolith_apply(cur, ws)
    return _TF.parent_address(cur, _C)


def mesh_digest(name, parent_hex, witness_hex, custody_hex, ticks, verdict):
    """URDRMSH1 canon — SHA-256(MAGIC | name | parent | witness | custody | ticks | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|w:{witness_hex}|c:{custody_hex}|t:{ticks}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) ------------------------------------------------------
def _grid16(name):
    return {(kx, ky): name for ky in range(4) for kx in range(4)}


def _quadrants():
    a = {}
    for ky in range(4):
        for kx in range(4):
            a[(kx, ky)] = ("alfa", "bravo", "charl", "delta")[(kx // 2) + 2 * (ky // 2)]
    return a


def _scene_parallel_tick():
    """Four stewards each write their own quadrant region in ONE concurrent tick — mesh == monolith,
    one independence round (genuinely parallel), no migration."""
    fld = flat_world(32)
    parent = _CK.address(_CK.field_manifest(fld, _C))
    assign = _quadrants()
    sched = [{"writes": [("alfa", 0, 0, 1, 1, 11), ("bravo", 2, 0, 1, 1, 22),
                         ("charl", 0, 2, 1, 1, 33), ("delta", 2, 2, 1, 1, 44)], "migrations": []}]
    rep = mesh_run(fld, assign, sched)
    ok = rep["witness"] == monolith(fld, sched) and rep["max_tick_width"] == 4
    return parent, rep["witness"], rep["custody"], rep["ticks"], ("ADMIT" if ok else "MESH-REFUSE")


def _scene_migrating():
    """One genesis steward; several ticks of writes interleaved with migrations to two more stewards —
    mesh == monolith (authority mobility does not perturb the witness)."""
    fld = flat_world(32)
    parent = _CK.address(_CK.field_manifest(fld, _C))
    assign = _grid16("alfa")
    sched = [{"writes": [("alfa", 0, 0, 1, 1, 100), ("alfa", 1, 1, 2, 2, 50)],
              "migrations": [(0, 0, "alfa", "bravo")]},
             {"writes": [("bravo", 0, 0, 3, 3, 25), ("alfa", 2, 2, 1, 1, 70)],
              "migrations": [(2, 2, "alfa", "charl")]},
             {"writes": [("charl", 2, 2, 4, 4, 9), ("bravo", 0, 0, 5, 5, 12)], "migrations": []}]
    rep = mesh_run(fld, assign, sched)
    ok = rep["witness"] == monolith(fld, sched) and rep["migrations"] == 2
    return parent, rep["witness"], rep["custody"], rep["ticks"], ("ADMIT" if ok else "MESH-REFUSE")


def _scene_handoff_write():
    """A single region migrates A->B->C over ticks, each current steward writing it in turn — every
    write lands under the live steward, mesh == monolith."""
    fld = flat_world(32)
    parent = _CK.address(_CK.field_manifest(fld, _C))
    assign = _grid16("alfa")
    sched = [{"writes": [("alfa", 1, 1, 0, 0, 7)], "migrations": [(1, 1, "alfa", "bravo")]},
             {"writes": [("bravo", 1, 1, 1, 1, 8)], "migrations": [(1, 1, "bravo", "charl")]},
             {"writes": [("charl", 1, 1, 2, 2, 9)], "migrations": []}]
    rep = mesh_run(fld, assign, sched)
    ok = rep["witness"] == monolith(fld, sched) and rep["migrations"] == 2
    return parent, rep["witness"], rep["custody"], rep["ticks"], ("ADMIT" if ok else "MESH-REFUSE")


def _scene_refusal():
    """The certified conflict: a tick with a non-steward write refuses the WHOLE tick. The verdict IS
    the refusal."""
    fld = flat_world(32)
    parent = _CK.address(_CK.field_manifest(fld, _C))
    assign = _quadrants()
    sched = [{"writes": [("alfa", 0, 0, 1, 1, 5), ("bravo", 0, 0, 2, 2, 6)], "migrations": []}]
    refused = False
    try:
        mesh_run(fld, assign, sched)
    except MeshError:
        refused = True
    return parent, parent, parent, 1, ("MESH-REFUSE" if refused else "ADMIT")


_SCENES = {"parallel_tick": _scene_parallel_tick, "migrating": _scene_migrating,
           "handoff_write": _scene_handoff_write, "refusal": _scene_refusal}
SCENES = ("parallel_tick", "migrating", "handoff_write", "refusal")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, w, c, t, v = scene_case(name)
    return mesh_digest(name, p, w, c, t, v)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_mesh.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MeshError(f"no golden named {name!r}")


# ---- the seeded property sweep (regionprop generalized to migrating authorities) ---------
class _LCG:
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


SWEEP_SEED = 20260721
SWEEP_COUNT = 100
_REGIONS = tuple((kx, ky) for ky in range(4) for kx in range(4))


def gen_scenario(r, k):
    """A random VALID mesh: k stewards over the 16-region grid, and a schedule of ticks whose writes
    are always by the CURRENT steward on DISTINCT regions (the generator tracks custody so it mints
    only lawful schedules — the sweep tests the THEOREM, not the generator). Returns (field, assign,
    schedule)."""
    field = flat_world(32)
    stewards = tuple(f"st{i}" for i in range(k))
    assign = {reg: stewards[r.rng(0, k - 1)] for reg in _REGIONS}
    cust = dict(assign)
    schedule = []
    for _t in range(r.rng(2, 4)):
        nw = r.rng(1, 4)
        picks, used = [], set()
        while len(picks) < nw:
            reg = _REGIONS[r.rng(0, len(_REGIONS) - 1)]
            if reg in used:
                continue
            used.add(reg)
            picks.append((cust[reg], reg[0], reg[1], r.rng(0, _C - 1), r.rng(0, _C - 1),
                          r.rng(1, 40)))
        migrations = []
        if r.rng(0, 9) < 5:
            reg = _REGIONS[r.rng(0, len(_REGIONS) - 1)]
            others = [s for s in stewards if s != cust[reg]]
            if others:
                dst = others[r.rng(0, len(others) - 1)]
                migrations.append((reg[0], reg[1], cust[reg], dst))
                cust[reg] = dst
        schedule.append({"writes": picks, "migrations": migrations})
    return field, assign, schedule


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random valid meshes, each asserted MESH == MONOLITH
    (the independent oracle). RAISES `MeshError` on the first divergence OR on NON-VACUITY (some
    migration must occur, some tick must be genuinely concurrent, layouts must vary, the world must
    change); returns the aggregate dict + digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    steward_counts = {}
    migrations_total = concurrent_ticks = changed = 0
    r = _LCG(seed)
    for s in range(count):
        k = r.rng(2, 4)
        field, assign, schedule = gen_scenario(r, k)
        rep = mesh_run(field, assign, schedule)
        mono = monolith(field, schedule)
        if rep["witness"] != mono:
            raise MeshError(f"scenario {s} (seed {seed}): the meshed world {rep['witness'][:12]}… "
                            f"diverged from the monolith {mono[:12]}… — MESH == MONOLITH FALSIFIED")
        steward_counts[k] = steward_counts.get(k, 0) + 1
        migrations_total += rep["migrations"]
        concurrent_ticks += sum(1 for t in schedule if len(t["writes"]) > 1)
        if rep["witness"] != _CK.address(_CK.field_manifest(field, _C)):
            changed += 1
        hh.update(f"|{s}:{k}:{rep['witness']}:{rep['custody']}".encode())
    if migrations_total == 0:
        raise MeshError("NON-VACUITY: no scenario migrated authority")
    if concurrent_ticks == 0:
        raise MeshError("NON-VACUITY: no tick had more than one concurrent write")
    if len(steward_counts) < 2:
        raise MeshError(f"NON-VACUITY: only {len(steward_counts)} distinct steward counts")
    if changed == 0:
        raise MeshError("NON-VACUITY: no scenario changed the world")
    return {"scenarios": count, "steward_counts": steward_counts,
            "migrations_total": migrations_total, "concurrent_ticks": concurrent_ticks,
            "changed": changed, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_mesh.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise MeshError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    """Reseed the sweep across `n_seeds` seeds; return the counterexamples (each a (seed, message)).
    The theorem is expected to hold, so the list is normally empty — a found counterexample is filed
    as a new pinned scene (the off-gate→pinned discipline). OFF-GATE: reseeded, not gate-run."""
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except MeshError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        if not found:
            print(f"EXPLORE: no counterexample across {n} reseeded sweeps from base {base} — "
                  f"MESH == MONOLITH held on every one.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg in found:
                print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} meshes, steward counts "
          f"{dict(sorted(rep['steward_counts'].items()))}, migrations {rep['migrations_total']}, "
          f"concurrent ticks {rep['concurrent_ticks']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
