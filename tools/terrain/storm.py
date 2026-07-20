# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""storm — the deterministic adversarial-transport loom (T3.48, W2, URDRSTM1): the DST discipline
(the FoundationDB-simulation / turmoil lineage the wire-phase brief researched) landed as a gate
stage. The wire's laws were stated where a transport must meet them; the storm is that transport,
misbehaving REPRODUCIBLY: frozen, seeded schedules of loss, duplication, reordering, and burst
delivery — every draw a SHA-256 digest-stream decision (no clock, no RNG, no platform hash), so
the same seed mints the same storm on every host and the gate stays byte-deterministic while the
network inside it does not.

THE MODEL. The authority emits a lawful serial history of updates (each the 104-byte URDRRAN0
record — the wire's own objects, unchanged). A SCHEDULE transforms the emission order into a
delivery order per client: each update may be dropped (loss), copied (duplication), or delayed
past its successors (reordering/burst). THE LOOM delivers; the client is `wire.client_admit`,
unmodified — the storm tests the landed law, it does not get a friendlier one. Refused deliveries
are REQUEUED and re-attempted to fixpoint (a pass admitting nothing ends the storm): the retry is
the transport's redelivery, the only repair mechanism in scope.

THE LAWS. CONVERGENCE-UNDER-CHAOS: every loss-free schedule lands every client on the authority's
witness bit-for-bit, each update admitted EXACTLY once (at-most-once holds under duplication
because a duplicate's parent has already moved). TYPED CHAOS, the invariant with two teeth: a
schedule with MEASURED reorderings must produce refusals — zero refusals convicts either the storm
(vacuous: it never stormed) or the client (the 'helpful' defect: buffering out-of-order updates
and applying them silently — production's reflex, the house's poison); one assertion reddens both.
THE PREFIX PROPERTY under loss: every region equals some authority prefix at every moment — no
state ever exists that the authority never had; the first gap freezes the region and the post-gap
deliveries stall as counted, typed refusals (DETECTED, never silent; REPAIR is W4's verified-fetch
law, declared out of this rung). MALICE UNDER CHAOS: tampered copies and foreign records injected
into the storm refuse without perturbing convergence. THE CONTROL: the identity schedule converges
with zero refusals — refusals are caused by chaos, never by the loom.

GRADE. Convergence-under-chaos with exactly-once, the typed-chaos invariant (with the measured-
reorder floor that keeps it non-vacuous), cross-seed agreement, the prefix property and detected
stalls under measured loss, malice-under-chaos, the becalmed control, schedule and outcome
determinism, and the lawfulness of the emission log are MEASURED (exact, reproducible, a defect
diverges). DECLARED: the schedule FAMILY is a pinned corpus (drops/dups/delays drawn from digest
streams — real networks are worse in ways no corpus exhausts; the corpus is falsifiable coverage,
not a proof of all weathers); GAP REPAIR (W4's fetch); sender authenticity (W3); REAL sockets
(W5's off-gate attestation — this rung is the reason that attestation can be judged: the laws it
must exhibit are pinned here first). `does_not_show`: wall-clock, bandwidth, congestion
(`bench.py` territory); partitions between MULTIPLE authorities (single-authority storms only —
the mesh phase's problem); cross-placement (URDRSTM1 joins the frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSTM1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK
import rannull as _RN
import wire as _WR


class StormError(Exception):
    def __init__(self, message):
        super().__init__(f"STORM-REFUSE: {message}")
        self.code = "STORM-REFUSE"


def _draw(seed, *idx):
    """One deterministic byte-stream draw: SHA-256(seed | indices) -> int. The storm's only
    randomness — portable, seeded, host-independent."""
    hh = hashlib.sha256()
    hh.update(seed)
    hh.update(("|" + "/".join(str(i) for i in idx)).encode())
    return int.from_bytes(hh.digest()[:4], "big")


# ---- the authority's emission log --------------------------------------------------------
_EDITS = ((5, 8, 1000), (2, 2, 11), (12, 4, 22), (6, 8, 50), (12, 12, 33), (3, 2, -4),
          (13, 4, 7), (5, 8, -30), (12, 12, 9), (2, 3, 5), (13, 5, -2), (6, 9, 12))


def authority_log(field, csize):
    """A lawful serial history: twelve edits across all four regions of the blank world, three per
    region, each authored against the then-current chunk state (the parent chain per region).
    Returns (updates, final replica witness over the full region set)."""
    man = _CK.field_manifest(field, csize)
    store = {_CK.address(r): r for r in _CK.cut(field, csize).values()}
    updates = []
    for (x, y, dh) in _EDITS:
        _w, _h, _c, grid = _CK.parse_manifest(man)
        key = (x // csize, y // csize)
        chunk = store[grid[key]]
        kx, ky, cells = _CK.restore_chunk(chunk)
        old = cells[y - ky * csize][x - kx * csize]
        rec = _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)
        new_chunk = _RN.shard_apply(chunk, rec)
        man = _RN.reunify(man, (new_chunk,))
        store[_CK.address(new_chunk)] = new_chunk
        updates.append(rec)
    _w, _h, _c, grid = _CK.parse_manifest(man)
    final = {"c": csize, "chunks": {k: store[d] for k, d in grid.items()}}
    return tuple(updates), _WR.replica_witness(final)


# ---- the schedule ------------------------------------------------------------------------
def schedule(seed, n, loss_pct, dup_pct, delay_max):
    """The frozen storm: for each emission index draw drop / duplicate / delay decisions from the
    digest stream; deliveries sort by (arrival slot, emission index, copy). Returns a tuple of
    (emission_index, copy_number) in DELIVERY order — the loom's script, pinned by the seed."""
    if not (type(seed) is bytes and seed):
        raise StormError("a storm needs a byte seed")
    deliveries = []
    for i in range(n):
        if loss_pct and _draw(seed, "loss", i) % 100 < loss_pct:
            continue                                            # dropped — never delivered
        delay = _draw(seed, "delay", i) % (delay_max + 1) if delay_max else 0
        deliveries.append((i + delay, i, 0))
        if dup_pct and _draw(seed, "dup", i) % 100 < dup_pct:
            delay2 = _draw(seed, "dup-delay", i) % (delay_max + 1) if delay_max else 0
            deliveries.append((i + delay2, i, 1))
    deliveries.sort()
    return tuple((i, copy) for (_slot, i, copy) in deliveries)


def measure(sched):
    """The storm measured from its own script — never assumed: reorderings (a delivery whose
    emission index precedes an earlier delivery's), duplicates, and drops (indices never
    delivered). The non-vacuity floor the falsifiers stand on."""
    seen_max = -1
    seen_max_first = -1
    reorderings = 0
    primary_reorderings = 0
    first_seen = set()
    duplicates = 0
    for (i, copy) in sched:
        if i < seen_max:
            reorderings += 1
        seen_max = max(seen_max, i)
        if i in first_seen:
            duplicates += 1
        else:
            if i < seen_max_first:
                primary_reorderings += 1        # a FIRST delivery arriving out of order — the
            seen_max_first = max(seen_max_first, i)  # storm's primary stream actually stormed
        first_seen.add(i)
    n = (max(first_seen) + 1) if first_seen else 0
    drops = sum(1 for i in range(n) if i not in first_seen)
    return {"reorderings": reorderings, "primary_reorderings": primary_reorderings,
            "duplicates": duplicates, "drops": drops}


# ---- the loom ----------------------------------------------------------------------------
def _tamper(rec, seed, i):
    bad = bytearray(rec)
    bad[_draw(seed, "flip", i) % len(bad)] ^= 0x01
    return bytes(bad)


def run_client(field, csize, updates, sched, inject=False):
    """Deliver the storm to ONE honest wire client (all four regions resident) with the retry
    loom: refused deliveries requeue; passes repeat to fixpoint (a pass admitting nothing ends the
    storm). Returns the outcome: the final client, admitted / refusals / stalled counts, and —
    with inject=True — tampered copies and foreign records woven in, their refusals counted
    separately. The client is `wire.client_admit`, UNMODIFIED: the storm tests the landed law."""
    w, h = len(field[0]), len(field)
    regions = frozenset((kx, ky) for ky in range(h // csize) for kx in range(w // csize))
    client = _WR.subscribe(field, csize, regions)
    queue = [updates[i] for (i, _copy) in sched]
    if inject:
        woven = []
        for j, rec in enumerate(queue):
            woven.append(rec)
            if _draw(b"malice", j) % 3 == 0:
                woven.append(_tamper(rec, b"malice", j))
            if _draw(b"malice-foreign", j) % 4 == 0:
                woven.append(_RN.regional_record("f" * 64, 0, 0, 1, 1, 0, 1))
        queue = woven
    admitted = 0
    refusals = 0
    malice_refused = 0
    lawful = set(bytes(u) for u in updates)
    while True:
        retry = []
        progressed = False
        for rec in queue:
            try:
                client = _WR.client_admit(client, rec)
                admitted += 1
                progressed = True
            except _WR.WireError:
                if bytes(rec) in lawful:
                    refusals += 1
                    retry.append(rec)
                else:
                    malice_refused += 1                         # malice never retries
        if not progressed or not retry:
            break
        queue = retry
    return {"client": client, "admitted": admitted, "refusals": refusals,
            "stalled": len(retry) if retry else 0, "malice_refused": malice_refused}


def prefix_witness(field, csize, updates, sched):
    """The HONEST expectation under loss: per region, the authority's prefix up to the first
    dropped in-region update — computed independently of the loom (the falsifier's oracle)."""
    delivered = set(i for (i, _c) in sched)
    w, h = len(field[0]), len(field)
    regions = frozenset((kx, ky) for ky in range(h // csize) for kx in range(w // csize))
    client = _WR.subscribe(field, csize, regions)
    gapped = set()
    for i, rec in enumerate(updates):
        _p, kx, ky, _x, _y, _oh, _nh = _RN.restore_regional(rec)
        if (kx, ky) in gapped:
            continue
        if i not in delivered:
            gapped.add((kx, ky))
            continue
        client = _WR.client_admit(client, rec)
    return _WR.replica_witness(client)


def storm_digest(name, witness_hex, updates, seeds, verdict):
    """URDRSTM1 canon — SHA-256(MAGIC | name | witness | updates | seeds | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|w:{witness_hex}|u:{updates}|s:{seeds}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _scene_tempest():
    """Three clients, three storms, one truth: loss-free reorder+dup chaos under three seeds — all
    converge to the authority's witness with exactly-once admission and typed (nonzero) refusals
    over measurably nonzero reorderings."""
    fld = _blank()
    updates, want = authority_log(fld, 8)
    ok = True
    for seed in (b"gale-1", b"gale-2", b"gale-3"):
        sched = schedule(seed, len(updates), loss_pct=0, dup_pct=40, delay_max=6)
        m = measure(sched)
        out = run_client(fld, 8, updates, sched)
        ok = ok and (m["primary_reorderings"] > 0 and _WR.replica_witness(out["client"]) == want
                     and out["admitted"] == len(updates) and out["refusals"] > 0)
    return want, len(updates), 3, ("ADMIT" if ok else "STORM-REFUSE")


def _scene_becalmed():
    """The control: the identity schedule — zero chaos, zero refusals, full convergence. Refusals
    are caused by the storm, never by the loom."""
    fld = _blank()
    updates, want = authority_log(fld, 8)
    sched = schedule(b"calm", len(updates), loss_pct=0, dup_pct=0, delay_max=0)
    m = measure(sched)
    out = run_client(fld, 8, updates, sched)
    ok = (m["reorderings"] == 0 and m["duplicates"] == 0 and m["drops"] == 0
          and _WR.replica_witness(out["client"]) == want and out["refusals"] == 0)
    return want, len(updates), 1, ("ADMIT" if ok else "STORM-REFUSE")


def _scene_gale_loss():
    """The lossy gale: measured drops; the client freezes each gapped region at the authority's
    prefix (the prefix property — no state the authority never had) and the stall is DETECTED as
    counted refusals, never silent drift."""
    fld = _blank()
    updates, _want = authority_log(fld, 8)
    sched = schedule(b"tempest-loss", len(updates), loss_pct=25, dup_pct=20, delay_max=6)
    m = measure(sched)
    out = run_client(fld, 8, updates, sched)
    expected = prefix_witness(fld, 8, updates, sched)
    ok = (m["drops"] > 0 and _WR.replica_witness(out["client"]) == expected
          and out["stalled"] > 0)
    return expected, len(updates), 1, ("ADMIT" if ok else "STORM-REFUSE")


def _scene_maelstrom():
    """Chaos plus malice: tampered copies and foreign records woven into the storm — every
    injected object a counted refusal, convergence unharmed."""
    fld = _blank()
    updates, want = authority_log(fld, 8)
    sched = schedule(b"maelstrom", len(updates), loss_pct=0, dup_pct=30, delay_max=5)
    out = run_client(fld, 8, updates, sched, inject=True)
    ok = (_WR.replica_witness(out["client"]) == want and out["malice_refused"] > 0
          and out["admitted"] == len(updates))
    return want, len(updates), 1, ("ADMIT" if ok else "STORM-REFUSE")


_SCENES = {"tempest": _scene_tempest, "becalmed": _scene_becalmed,
           "gale_loss": _scene_gale_loss, "maelstrom": _scene_maelstrom}
SCENES = ("tempest", "becalmed", "gale_loss", "maelstrom")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    wit, updates, seeds, verdict = scene_case(name)
    return storm_digest(name, wit, updates, seeds, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_storm.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise StormError(f"no golden named {name!r}")
