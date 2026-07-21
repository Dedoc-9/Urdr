# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""partition — THE PARTITIONED MESH (Phase M, rung M4, URDRPRT1): the CP posture made executable, and
the theorem that has been implicit since `storm`, `wire`, `chunkstate`, and `reunify == monolith` —
UNDER PARTITION, THE SYSTEM REFUSES TO INVENT HISTORY. M3 proved MESH == MONOLITH while connected; M4
asks what happens when the connection disappears, and the answer is already latent in the laws: M1's
disjointness, M2's custody CAS, and the storm prefix property compose into it. This is a stronger,
more distinctive statement than "the cluster remains available."

THE PARTITION PREFIX THEOREM. Every lawful partitioned execution equals a PREFIX of the corresponding
connected execution; any attempt to extend beyond that certified prefix either preserves equality or
refuses. In one line:  `partitioned mesh == monolith prefix`  OR  `PARTITION-REFUSE`. It is the
mesh-scale version of the storm prefix property (a stalled client freezes at the authority's prefix,
never a state the authority never had).

THE MODEL. A partition splits the stewards (and thus the regions they own) into two SIDES, L and R,
from a shared CUT (the world + custody both sides agree on at partition time). Each side runs its own
schedule of ticks from the frozen cut, but — and this is the whole rung — a side may only admit an
operation it can VERIFY from its frozen knowledge:
  * THE FREEZE RULE (refuse rather than guess): a write to a region whose steward is on the UNREACHABLE
    side FREEZES — the side cannot prove it holds the sole authority, so it does not speculate. This is
    the storm freeze at custody scale.
  * CUSTODY STILL BITES (M2, inherited): every admitted write is steward-checked against the FROZEN cut
    custody — so even a duplicated lease (the split-brain attack) cannot write on the side that is not
    the region's steward; the lease is blind, custody is not.
  * A CROSS-PARTITION MIGRATION FREEZES: authority cannot be handed to an unreachable node — a transfer
    whose destination is on the other side is not admitted (mid-transfer regions stay with their
    pre-transfer steward until reunification resolves them deterministically from the content chain).
  * THE MIGRATION CAS refuses PARTITION-TRANSPORT FORGERY: a certificate minted on the unreachable side
    chains from a custody head this side's frozen custody does not contain, so its parent CAS fails —
    refused, never rebased.

REUNIFICATION, two layers individually redundant and jointly load-bearing: because the freeze rule
keeps each side writing only regions it solely owns, the two sides change DISJOINT chunk slots (M1's
n-way nullity, now across the partition boundary), so reunification is well-defined and equals the
monolith of the admitted writes. The SECOND layer is the overlap check: if the freeze rule is gutted
and both sides change the same region (silent divergence / split-brain), reunification DETECTS the
shared slot and REFUSES — divergence is caught even if the first layer is defeated.

WHAT M4 PROVES (each red-first, the five attacks the honest implementation must survive): (1) SILENT
DIVERGENCE — refused before it occurs (the freeze rule; the reunify overlap as backstop); (2)
AVAILABILITY FORGERY — a gutted freeze rule's speculation fails at reunification; (3) PREFIX VIOLATION
— a mid-transfer region admits nothing beyond the shared prefix; (4) SPLIT-BRAIN AUTHORITY — a
duplicated lease admits on only the owning side, and forcing both refuses at reunify; (5)
PARTITION-TRANSPORT FORGERY — a certificate from the unreachable side refuses on the migration CAS.

GRADE (Phase M rung M4). The Partition Prefix Theorem over the pinned corpus and a seeded sweep
(randomized side splits, local and cross-partition ops, migration schedules); partitioned == monolith
of the admitted writes; the prefix property (every partitioned region chunk is the connected chunk or
the cut chunk — never a third, invented state); the freeze rule and the reunify-overlap backstop; and
the five attacks are MEASURED (exact, reproducible, a defect diverges — a gutted freeze rule makes the
sweep raise). DECLARED: the CP AVAILABILITY COST is real and STATED, not hidden — a mid-transfer region
FREEZES (no liveness guarantee under partition); a consensus/quorum PROGRESS overlay that would buy
liveness by introducing a trusted majority is a NAMED, OPTIONAL, FUTURE extension, never folded into
this theorem (it is a different trust model — "every byte re-derived or refused" — and would be graded
separately). `does_not_show`: real cross-machine partitions / netsplit timing (this models the partition
as a frozen-knowledge split, not wall-clock; `meshattest`/`bench.py` own the reality boundary); the
attested mesh session (M5); cross-placement (URDRPRT1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRPRT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # chunks, manifests, addresses
import rannull as _RN                                           # regional records
import terraform as _TF                                         # the monolith oracle
import nway as _NW                                              # flat world
import migrate as _MG                                           # steward custody, admit, migration

_C = 8


class PartitionError(Exception):
    def __init__(self, message):
        super().__init__(f"PARTITION-REFUSE: {message}")
        self.code = "PARTITION-REFUSE"


def flat_world(side=32):
    return _NW.flat_world(side)


def _fresh(field):
    man = _CK.field_manifest(field, _C)
    store = {_CK.address(r): r for r in _CK.cut(field, _C).values()}
    return man, store


def region_sides(assignment, side_of_steward):
    """{(kx,ky): 'L'|'R'} — a region belongs to the side its steward is on."""
    return {reg: side_of_steward[st] for reg, st in assignment.items()}


def cut_witness(field):
    """The witness of the shared cut (the world both sides agree on at partition time)."""
    return _CK.address(_CK.field_manifest(field, _C))


def _lease_and_rec(man, store, kx, ky, lx, ly, dh):
    x, y = kx * _C + lx, ky * _C + ly
    grid = _CK.parse_manifest(man)[3]
    chunk = store[grid[(kx, ky)]]
    old = _CK.restore_chunk(chunk)[2][ly][lx]
    return (_MG._LS.lease_from_chunk(chunk),
            _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh))


def _freeze_ok(side, region_side, kx, ky):
    """THE FREEZE RULE (exposed for the falsifiers' plant): a side may act on a region only if that
    region's authority is on THIS side. A region whose steward is on the unreachable side freezes —
    the side cannot prove sole authority, so it does not speculate (refuse rather than guess)."""
    return region_side.get((kx, ky)) == side


def _mint_manifest(w, h, c, grid):
    """A chunk manifest from a {(kx,ky): address-hex} grid (the reunification substitute)."""
    pre = bytearray(_CK.MAP_MAGIC)
    for v in (w, h, c):
        pre += v.to_bytes(4, "big")
    for ky in range(h // c):
        for kx in range(w // c):
            pre += bytes.fromhex(grid[(kx, ky)])
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


# ---- one side's isolated execution from the frozen cut -----------------------------------
def _side_run(field, cut_sman, side, region_side, side_of_steward, ops):
    """Run ONE side's ops from the shared cut, admitting only what it can verify from frozen knowledge.
    Returns {man, store, admitted (list of (kx,ky,lx,ly,dh)), changed (set of regions), frozen}."""
    man, store = _fresh(field)
    sman = cut_sman                                            # FROZEN custody — the side cannot see
    certs = {}                                                 # the other side's post-cut migrations
    admitted, changed = [], set()
    frozen = 0
    for op in ops:
        if op[0] == "write":
            _t, steward, kx, ky, lx, ly, dh = op
            if not _freeze_ok(side, region_side, kx, ky):
                frozen += 1                                    # FREEZE: authority on the unreachable side
                continue
            try:
                ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
                new_man, ch = _MG.admit(sman, certs, man, dict(store), _MG.steward_tag(steward),
                                        ls, rec)
                store[_CK.address(ch)] = ch
                man = new_man
                admitted.append((kx, ky, lx, ly, dh))
                changed.add((kx, ky))
            except _MG.MigrateError:
                frozen += 1                                    # unlawful for this side — not admitted
        elif op[0] == "migrate":
            _t, kx, ky, src, dst = op
            if region_side.get((kx, ky)) != side or side_of_steward.get(dst) != side:
                frozen += 1                                    # cross-partition migration FREEZES
                continue
            try:
                sman2, cert = _MG.migrate(sman, certs, man, kx, ky, _MG.steward_tag(src),
                                          _MG.steward_tag(dst))
                certs[_MG.address(cert)] = cert
                sman = sman2
            except _MG.MigrateError:
                frozen += 1
        else:
            raise PartitionError(f"unknown op {op[0]!r}")
    return {"man": man, "store": store, "admitted": admitted, "changed": changed, "frozen": frozen}


def _reunify(field, left, right):
    """Combine the two sides' worlds. THE SECOND LAYER: a region changed on BOTH sides is split-brain —
    reunification cannot equal the monolith, so it REFUSES (never picks a winner). Otherwise the cut
    manifest with each side's changed slots substituted — disjoint, so well-defined."""
    overlap = left["changed"] & right["changed"]
    if overlap:
        raise PartitionError(f"split-brain: region(s) {sorted(overlap)} were written on BOTH sides of "
                             f"the partition — reunification cannot equal the monolith; refused rather "
                             f"than an invented merge")
    w, h, c, cut_grid = _CK.parse_manifest(_CK.field_manifest(field, _C))
    grid = dict(cut_grid)
    for reg, res in (("L", left), ("R", right)):
        _w, _h, _c, g = _CK.parse_manifest(res["man"])
        for r in res["changed"]:
            grid[r] = g[r]
    return _CK.address(_mint_manifest(w, h, c, grid))


def partitioned_run(field, assignment, side_of_steward, left_ops, right_ops):
    """THE PARTITIONED MESH. From the shared cut, each side runs its ops restricted to what it can
    verify (the freeze rule + custody CAS against frozen custody); reunification combines the disjoint
    results or REFUSES on split-brain. Returns {witness, admitted (writes), admitted_count, frozen,
    left_regions, right_regions}."""
    try:
        cut_sman = _MG.steward_genesis(_CK.field_manifest(field, _C),
                                       {k: _MG.steward_tag(v) for k, v in assignment.items()})
    except _MG.MigrateError as exc:
        raise PartitionError(f"the cut custody is unlawful: {exc}")
    rs = region_sides(assignment, side_of_steward)
    left = _side_run(field, cut_sman, "L", rs, side_of_steward, left_ops)
    right = _side_run(field, cut_sman, "R", rs, side_of_steward, right_ops)
    witness = _reunify(field, left, right)
    admitted = left["admitted"] + right["admitted"]
    return {"witness": witness, "admitted": admitted, "admitted_count": len(admitted),
            "frozen": left["frozen"] + right["frozen"],
            "left_regions": len(left["changed"]), "right_regions": len(right["changed"])}


# ---- the oracles -------------------------------------------------------------------------
def monolith_of(field, writes):
    """THE NEUTRAL ORACLE: apply the given writes GLOBALLY via terraform (custody ignored), region-
    sorted (disjoint → order-immaterial). `writes`: [(kx,ky,lx,ly,dh)]. Returns the witness."""
    cur = field
    for (kx, ky, lx, ly, dh) in sorted(writes):
        x, y = kx * _C + lx, ky * _C + ly
        lifted = _TF.edit_record(_TF.parent_address(cur, _C), x, y, cur[y][x], cur[y][x] + dh)
        cur = _TF.apply_edit(cur, _C, lifted)
    return _TF.parent_address(cur, _C)


def _connected_history(field, assignment, side_of_steward, left_ops, right_ops):
    """THE CONNECTED REFERENCE, as a per-region PATH. The same schedule run with NO partition:
    each side's LEGITIMATE own-region writes are admitted (a cross-write — the wrong side speculating
    on a region it does not own — is not part of any legitimate schedule and is skipped, exactly as
    the partitioned side freezes it), and cross-partition MIGRATIONS are ALLOWED (connected can hand
    authority across). Returns {region: set of every chunk address that region passes through,
    including the cut} — the states the connected execution genuinely produced."""
    rs = region_sides(assignment, side_of_steward)
    man, store = _fresh(field)
    sman = _MG.steward_genesis(man, {k: _MG.steward_tag(v) for k, v in assignment.items()})
    certs = {}
    _w, _h, _c, cut_grid = _CK.parse_manifest(man)
    history = {reg: {addr} for reg, addr in cut_grid.items()}
    for side, ops in (("L", left_ops), ("R", right_ops)):
        for op in ops:
            if op[0] == "write":
                _t, steward, kx, ky, lx, ly, dh = op
                if rs.get((kx, ky)) != side:
                    continue                                   # a cross-write is an attack, not legit
                try:
                    ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
                    new_man, ch = _MG.admit(sman, certs, man, dict(store), _MG.steward_tag(steward),
                                            ls, rec)
                    store[_CK.address(ch)] = ch
                    man = new_man
                    history[(kx, ky)].add(_CK.address(ch))
                except _MG.MigrateError:
                    pass
            else:
                _t, kx, ky, src, dst = op
                try:                                           # connected: cross-migration ALLOWED
                    sman2, cert = _MG.migrate(sman, certs, man, kx, ky, _MG.steward_tag(src),
                                              _MG.steward_tag(dst))
                    certs[_MG.address(cert)] = cert
                    sman = sman2
                except _MG.MigrateError:
                    pass
    return history


def _partitioned_region_addrs(field, assignment, side_of_steward, left_ops, right_ops):
    """The partitioned world's per-region chunk address (from the two side-runs; a region unchanged by
    either side keeps its cut address). Raises on split-brain."""
    cut_sman = _MG.steward_genesis(_CK.field_manifest(field, _C),
                                   {k: _MG.steward_tag(v) for k, v in assignment.items()})
    rs = region_sides(assignment, side_of_steward)
    left = _side_run(field, cut_sman, "L", rs, side_of_steward, left_ops)
    right = _side_run(field, cut_sman, "R", rs, side_of_steward, right_ops)
    if left["changed"] & right["changed"]:
        raise PartitionError("split-brain (prefix check)")
    _w, _h, _c, cut_grid = _CK.parse_manifest(_CK.field_manifest(field, _C))
    addrs = dict(cut_grid)
    for res in (left, right):
        _w2, _h2, _c2, g = _CK.parse_manifest(res["man"])
        for r in res["changed"]:
            addrs[r] = g[r]
    return addrs


def is_prefix_of_connected(field, assignment, side_of_steward, left_ops, right_ops):
    """THE PREFIX PROPERTY (no invented history): every region's chunk in the partitioned world is a
    state the connected execution GENUINELY PASSED THROUGH for that region (its cut state or one of its
    intermediate/final states) — never a third, invented state. Returns True iff so AND partitioned ==
    monolith of the admitted writes."""
    rep = partitioned_run(field, assignment, side_of_steward, left_ops, right_ops)
    if rep["witness"] != monolith_of(field, rep["admitted"]):
        return False
    part_addrs = _partitioned_region_addrs(field, assignment, side_of_steward, left_ops, right_ops)
    history = _connected_history(field, assignment, side_of_steward, left_ops, right_ops)
    for reg, addr in part_addrs.items():
        if addr not in history.get(reg, set()):
            return False                                       # an invented state — prefix violated
    return True


def adopt_foreign_certificate(field, assignment, side_of_steward):
    """ATTACK #5 (partition-transport forgery), as a self-contained refusal: the unreachable side
    evolves a region's custody TWO hops post-cut (raun→raun2→raun3), producing a certificate whose
    PARENT is a post-cut custody head. Presented to a FROZEN side (whose custody head for that region
    is still the genesis cut), the migration CAS finds parent != head and REFUSES — never rebased."""
    man = _CK.field_manifest(field, _C)
    cut_sman = _MG.steward_genesis(man, {k: _MG.steward_tag(v) for k, v in assignment.items()})
    # find a region owned by a steward we can chain from
    reg = next((r for r, st in assignment.items() if side_of_steward.get(st) == "R"), None)
    if reg is None:
        raise PartitionError("no R-side region to forge from")
    kx, ky = reg
    st0 = _MG.steward_tag(assignment[reg])
    certs = {}
    s1, c1 = _MG.migrate(cut_sman, certs, man, kx, ky, st0, _MG.steward_tag("raun2"))
    certs[_MG.address(c1)] = c1
    _s2, c2 = _MG.migrate(s1, certs, man, kx, ky, _MG.steward_tag("raun2"), _MG.steward_tag("raun3"))
    try:
        _MG.apply_migration(cut_sman, man, c2)                 # c2's parent is c1 (post-cut) != cut head
    except _MG.MigrateError as exc:
        raise PartitionError(f"partition-transport forgery refused: a certificate from the unreachable "
                             f"side chains from a custody head this side never had ({exc})")
    raise PartitionError("the forged certificate was NOT refused — the migration CAS is defeated")


def partition_digest(name, parent_hex, witness_hex, admitted, frozen, verdict):
    """URDRPRT1 canon — SHA-256(MAGIC | name | parent | witness | admitted | frozen | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|p:{parent_hex}|w:{witness_hex}|a:{admitted}|f:{frozen}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) ------------------------------------------------------
def _halves():
    """The standard cut: 16 regions, LEFT (kx<2) → 'lear', RIGHT (kx>=2) → 'raun'."""
    assign = {}
    for ky in range(4):
        for kx in range(4):
            assign[(kx, ky)] = "lear" if kx < 2 else "raun"
    return assign, {"lear": "L", "raun": "R"}


def _scene_disjoint():
    """Each side writes only its own regions — reunify == monolith of the admitted, nothing frozen."""
    fld = flat_world(32)
    parent = cut_witness(fld)
    assign, side_of = _halves()
    left = [("write", "lear", 0, 0, 1, 1, 100), ("write", "lear", 1, 3, 2, 2, 40)]
    right = [("write", "raun", 3, 3, 3, 3, 55), ("write", "raun", 2, 1, 0, 0, 25)]
    rep = partitioned_run(fld, assign, side_of, left, right)
    ok = (rep["witness"] == monolith_of(fld, rep["admitted"]) and rep["frozen"] == 0
          and is_prefix_of_connected(fld, assign, side_of, left, right))
    return parent, rep["witness"], rep["admitted_count"], rep["frozen"], ("ADMIT" if ok else "PARTITION-REFUSE")


def _scene_freeze():
    """The freeze rule: a side's cross-partition write is FROZEN; the admitted world equals the
    monolith of the local writes only (refuse to invent history), a prefix of the connected."""
    fld = flat_world(32)
    parent = cut_witness(fld)
    assign, side_of = _halves()
    left = [("write", "lear", 0, 0, 1, 1, 5), ("write", "raun", 3, 3, 2, 2, 6)]   # 2nd is cross → frozen
    right = [("write", "raun", 3, 3, 1, 1, 9)]
    rep = partitioned_run(fld, assign, side_of, left, right)
    ok = (rep["frozen"] == 1 and rep["witness"] == monolith_of(fld, rep["admitted"])
          and is_prefix_of_connected(fld, assign, side_of, left, right))
    return parent, rep["witness"], rep["admitted_count"], rep["frozen"], ("ADMIT" if ok else "PARTITION-REFUSE")


def _scene_mid_transfer():
    """Prefix violation prevented: a cross-partition migration and a beyond-prefix write both FREEZE;
    the world stays at the shared prefix (nothing invented)."""
    fld = flat_world(32)
    parent = cut_witness(fld)
    assign, side_of = _halves()
    left = [("migrate", 0, 0, "lear", "raun")]                 # cross-partition migration → frozen
    right = [("write", "raun", 0, 0, 1, 1, 50)]                # authority never received → frozen
    rep = partitioned_run(fld, assign, side_of, left, right)
    ok = (rep["admitted_count"] == 0 and rep["frozen"] >= 2 and rep["witness"] == cut_witness(fld))
    return parent, rep["witness"], rep["admitted_count"], rep["frozen"], ("MESH-FROZEN" if ok else "PARTITION-REFUSE")


def _scene_split_brain():
    """Split-brain REFUSED: with the freeze rule gutted, both sides write region (1,1) and
    reunification detects the shared slot and refuses. The verdict IS the refusal."""
    fld = flat_world(32)
    parent = cut_witness(fld)
    assign, side_of = _halves()
    left = [("write", "lear", 1, 1, 1, 1, 30)]
    right = [("write", "lear", 1, 1, 2, 2, 40)]                # duplicated authority
    orig = _freeze_ok
    globals()["_freeze_ok"] = lambda side, region_side, kx, ky: True
    refused = False
    try:
        partitioned_run(fld, assign, side_of, left, right)
    except PartitionError:
        refused = True
    finally:
        globals()["_freeze_ok"] = orig
    return parent, parent, 0, 0, ("PARTITION-REFUSE" if refused else "ADMIT")


_SCENES = {"disjoint": _scene_disjoint, "freeze": _scene_freeze,
           "mid_transfer": _scene_mid_transfer, "split_brain": _scene_split_brain}
SCENES = ("disjoint", "freeze", "mid_transfer", "split_brain")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    p, w, a, f, v = scene_case(name)
    return partition_digest(name, p, w, a, f, v)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_partition.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise PartitionError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------
class _LCG:
    def __init__(self, seed):
        self.x = seed & 0x7FFFFFFF

    def nxt(self):
        self.x = (1103515245 * self.x + 12345) & 0x7FFFFFFF
        return self.x

    def rng(self, lo, hi):
        return lo + ((self.nxt() >> 16) % (hi - lo + 1))


SWEEP_SEED = 20260721
SWEEP_COUNT = 80
_REGIONS = tuple((kx, ky) for ky in range(4) for kx in range(4))


def gen_scenario(r):
    """A random VALID partition: each region assigned to steward 'lear'(L) or 'raun'(R); each side gets
    local writes to its own regions AND cross-partition writes to the other side's regions (which must
    FREEZE) plus an occasional cross-partition migration (which must FREEZE). The generator tracks
    ownership so it mints only well-formed ops — the sweep tests the THEOREM, not the generator."""
    assign = {reg: ("lear" if r.rng(0, 1) == 0 else "raun") for reg in _REGIONS}
    side_of = {"lear": "L", "raun": "R"}
    lregs = [reg for reg in _REGIONS if assign[reg] == "lear"]
    rregs = [reg for reg in _REGIONS if assign[reg] == "raun"]
    left, right = [], []
    for (mine, theirs, steward, tsteward, bag) in (("L", "R", "lear", "raun", left),
                                                   ("R", "L", "raun", "lear", right)):
        myregs = lregs if mine == "L" else rregs
        thregs = rregs if mine == "L" else lregs
        for _i in range(r.rng(1, 3)):
            if myregs:
                reg = myregs[r.rng(0, len(myregs) - 1)]
                bag.append(("write", steward, reg[0], reg[1], r.rng(0, _C - 1), r.rng(0, _C - 1),
                            r.rng(1, 40)))
        if thregs and r.rng(0, 9) < 6:                         # a cross-partition write (must freeze)
            reg = thregs[r.rng(0, len(thregs) - 1)]
            bag.append(("write", tsteward, reg[0], reg[1], r.rng(0, _C - 1), r.rng(0, _C - 1),
                        r.rng(1, 40)))
        if myregs and thregs and r.rng(0, 9) < 4:              # a cross-partition migration (must freeze)
            reg = myregs[r.rng(0, len(myregs) - 1)]
            bag.append(("migrate", reg[0], reg[1], steward, tsteward))
    return flat_world(32), assign, side_of, left, right


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep: `count` random partitions, each asserted (A) partitioned ==
    monolith of the admitted writes, and (B) the prefix property (no invented history). RAISES on the
    first violation OR on NON-VACUITY (some op must freeze, some must admit, both sides must be active,
    the world must change). Returns the aggregate dict + digest."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    frozen_total = admitted_total = both_sides_active = changed = 0
    r = _LCG(seed)
    for s in range(count):
        field, assign, side_of, left, right = gen_scenario(r)
        rep = partitioned_run(field, assign, side_of, left, right)
        if rep["witness"] != monolith_of(field, rep["admitted"]):
            raise PartitionError(f"scenario {s} (seed {seed}): partitioned world "
                                 f"{rep['witness'][:12]}… != monolith of the admitted writes — the "
                                 f"Partition Prefix Theorem is FALSIFIED")
        if not is_prefix_of_connected(field, assign, side_of, left, right):
            raise PartitionError(f"scenario {s} (seed {seed}): the partitioned world is NOT a prefix "
                                 f"of the connected execution — invented history")
        frozen_total += rep["frozen"]
        admitted_total += rep["admitted_count"]
        both_sides_active += 1 if (rep["left_regions"] > 0 and rep["right_regions"] > 0) else 0
        if rep["witness"] != cut_witness(field):
            changed += 1
        hh.update(f"|{s}:{rep['witness']}:{rep['admitted_count']}:{rep['frozen']}".encode())
    if frozen_total == 0:
        raise PartitionError("NON-VACUITY: no op ever froze — the freeze rule was never exercised")
    if admitted_total == 0:
        raise PartitionError("NON-VACUITY: no op was ever admitted")
    if both_sides_active == 0:
        raise PartitionError("NON-VACUITY: no scenario exercised both sides")
    if changed == 0:
        raise PartitionError("NON-VACUITY: no scenario changed the world")
    return {"scenarios": count, "frozen_total": frozen_total, "admitted_total": admitted_total,
            "both_sides_active": both_sides_active, "changed": changed, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_partition.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise PartitionError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    """Reseed the sweep across `n_seeds` seeds; return the counterexamples. Normally empty — a found
    counterexample is filed as a pinned scene (the off-gate→pinned discipline). OFF-GATE."""
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except PartitionError as exc:
            found.append((seed, str(exc)))
    return found


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--explore":
        base = int(argv[2]) if len(argv) > 2 else SWEEP_SEED
        n = int(argv[3]) if len(argv) > 3 else 300
        found = explore(base, n)
        if not found:
            print(f"EXPLORE: no counterexample across {n} reseeded sweeps from base {base} — the "
                  f"Partition Prefix Theorem held on every one.")
        else:
            print(f"EXPLORE: {len(found)} counterexample(s) — FILE these as pinned scenes:")
            for seed, msg in found:
                print(f"  seed={seed}: {msg}")
        return 0
    for name in SCENES:
        print(name, scene_result(name))
    rep = sweep()
    print(f"SWEEP: {rep['scenarios']} partitions, frozen {rep['frozen_total']}, admitted "
          f"{rep['admitted_total']}, both-sides {rep['both_sides_active']}, changed {rep['changed']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
