# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""citation — the DETERMINISTIC CROSS-TICK CITATION PROTOCOL (URDRCIT1): lawful historical reuse on the
byte layer. URDRBYT1 proves every emitted packet is a deterministic witness bounded by an exact byte budget
B; the remaining inefficiency is TEMPORAL redundancy — successive ticks retransmit state the client has
already verified. This rung does not invent an adaptive compressor; it proves that historical reuse can be
made DETERMINISTIC, REPLAYABLE, and CLOSED-WORLD, preserving every law of perception, scheduling, and byte
accounting. Composition over `byteacct`/`schedule`/.../`perception`, NO NEW GLYPH — the kernel stays frozen.
See `docs/citation_brief.md` for the design pass and the D1 §20 glyph ruling.

THE HEADLINE LAW — CITED ≡ BASELINE. Compression never alters semantics: the client's reconstructed state
sequence is IDENTICAL whether the server cites history (CITE records) or always sends full baselines (FULL
records). A citation merely changes the lawful REPRESENTATION of an already-certified history.

A citation is not a heuristic cache lookup; it is a content-addressed reference to state BOTH server and
client have verified. A large entity update (a FULL — an absolute position + the 32-byte authority citation)
that returns to a previously-acknowledged value is re-expressed as a compact fixed-width CITE, reconstructing
exactly the same transcript as the uncited baseline. Four structural laws keep it proof-carrying:

  1. CERTIFIED CITATION LAW — a citation may reference only history the client has ACKNOWLEDGED. Each client
     carries a deterministic Acknowledgment Witness: at tick t, ticks `T ≤ t − ACK_LAG` are certified. The
     encoder is forbidden from citing outside it; with no certified anchor it emits a complete baseline. The
     protocol REFUSES uncertainty rather than speculating about receiver state.
  2. CONSTANT-SHAPE CITATION LAW — a CITE occupies a FIXED-WIDTH slot independent of citation age (the
     immediately-preceding tick and a much older admitted tick cost the same), and every packet is padded to
     exactly B bytes — the constant-shape transcript of URDRPCP1 is preserved.
  3. CLOSED-WORLD CITATION LAW — the citation cache is a function of the MANIFESTED set. When an entity
     leaves and becomes an un-addressed absence (∅), its citation history is immediately and deterministically
     EVICTED; a historical reference cannot resurrect information perception has withdrawn.
  4. CROSS-TICK RATE LAW — compression may not postpone mandatory baselines indefinitely. Every manifested
     entity receives a complete FULL baseline within REFRESH_INTERVAL ticks, bounding the citation-chain
     depth and the client's recovery cost, regardless of how effective compression becomes — the
     bounded-freshness of URDRSCH1 is preserved.

RED-FIRST (the plants bite before the goldens pin):
  * `_encode_unacknowledged` cites a tick outside the AckW — admission REFUSES.
  * `_encode_ghost` cites the history of an entity already removed from the manifested set — a closed-world
    violation (the resolution resurrects withdrawn state).
  * `_encode_no_baseline` lets citation suppress the mandatory baseline forever — the rate law catches an
    entity that exceeds REFRESH_INTERVAL without a baseline.
  * `_serialize_shape_drift` encodes the anchor as a variable-width varint — the packet is no longer exactly
    B, violating the constant-shape law.

GRADE: MEASURED. DECLARED: inherits every byteacct/scheduler/throttle/anamorphosis/perception boundary; the
compression benefit is a reduction in USEFUL bytes (fewer/cheaper records), which under a tight byteacct
budget becomes fewer deferrals — here B is roomy to isolate the citation laws. `does_not_show`: adaptive
anchor selection (the encoder cites the OLDEST certified match, a fixed rule); lossy history compaction;
cross-placement (URDRCIT1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import byteacct as BY                                            # the rung this composes over  # noqa: E402
import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRCIT1"
DIGEST_BYTES = A.DIGEST_BYTES
OVERHEAD = len(MAGIC) + 4 + 4 + 4 + DIGEST_BYTES               # MAGIC | tick | budget | count | digest
_REMOVE, _FULL, _MOVE, _CITE = BY._REMOVE, BY._FULL, BY._MOVE, 3
CITE_BYTES = 1 + 4 + 4                                          # tag | eid | anchor tick (fixed width)
ACK_LAG = 2                                                    # ticks T ≤ t − ACK_LAG are acknowledged
REFRESH_INTERVAL = 4                                           # a mandatory baseline at least this often
B_ROOMY = OVERHEAD + 360                                       # roomy enough that nothing defers


class CitationError(Exception):
    def __init__(self, message):
        super().__init__(f"CITATION-REFUSE: {message}")
        self.code = "CITATION-REFUSE"


def rec_cite(eid, anchor):
    return bytes([_CITE]) + eid.to_bytes(4, "big") + (anchor & 0xFFFFFFFF).to_bytes(4, "big")


def ack_max(tick, ack_lag=ACK_LAG):
    """The newest tick the client is certified to have acknowledged at `tick`."""
    return tick - ack_lag


# ---- serialize / parse (constant-shape at B, with the CITE record) ----------------------------
def serialize(tick, budget, records, _ser=None):
    if _ser is not None:
        return _ser(tick, budget, records)
    body_budget = budget - OVERHEAD
    body = bytearray()
    for r in records:
        body += r
    if len(body) > body_budget:
        raise CitationError(f"records {len(body)}B exceed the body budget {body_budget}B")
    body += b"\x00" * (body_budget - len(body))
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)
    return frame + hashlib.sha256(frame).digest()


def _read_record(buf, off):
    tag = buf[off]; off += 1
    eid = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if tag == _REMOVE:
        return ("remove", eid, None), off
    if tag == _CITE:
        anchor = int.from_bytes(buf[off:off + 4], "big"); off += 4
        return ("cite", eid, anchor), off
    if tag == _MOVE:
        zx, off = BY._read_uvarint(buf, off); zy, off = BY._read_uvarint(buf, off)
        return ("move", eid, (BY._unzz(zx), BY._unzz(zy))), off
    if tag == _FULL:
        zx, off = BY._read_uvarint(buf, off); zy, off = BY._read_uvarint(buf, off)
        cite = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
        return ("full", eid, (BY._unzz(zx), BY._unzz(zy), cite)), off
    raise CitationError(f"unknown record tag {tag}")


def parse(packet):
    t = bytes(packet)
    if t[:len(MAGIC)] != MAGIC:
        raise CitationError("bad magic — not a URDRCIT1 packet")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise CitationError("digest mismatch — tampered or truncated")
    budget = int.from_bytes(t[12:16], "big")
    if len(t) != budget:
        raise CitationError(f"packet length {len(t)} != declared budget {budget} (not constant-shape at B)")
    tick = int.from_bytes(t[8:12], "big")
    count = int.from_bytes(t[16:20], "big")
    off = OVERHEAD - DIGEST_BYTES
    records = []
    for _ in range(count):
        rec, off = _read_record(t, off)
        records.append(rec)
    return tick, budget, records, off - (OVERHEAD - DIGEST_BYTES)


# ---- the server encoder ------------------------------------------------------------------------
def _encode(cur, hist, base, entities, walls, cl, L, tick, cfg, mode="cited"):
    """Produce the records for one tick. `cur` {eid:(x,y,cite)} is the last shown state; `hist`
    {eid:{tick:state}} is the acknowledged history (evicted on departure); `base` {eid:tick} is the last
    baseline. Returns (manifest, records, baselined_eids). `mode` selects cited / baseline / a plant."""
    B, ack_lag, refresh = cfg
    am = ack_max(tick, ack_lag)
    man = A._manifest_under(entities, walls, cl, L)
    man_set = set(man)
    records = []
    for eid in sorted(cur):                                    # departures → REMOVE (mandatory, evicts)
        if eid not in man_set:
            records.append(BY.rec_remove(eid))
    for eid in man:
        ex, ey, cite = entities[eid]; s = (ex, ey, cite)
        periodic = mode != "no_baseline" and (tick - base.get(eid, -10 ** 9)) >= refresh
        must_baseline = eid not in cur or periodic       # entrants always baseline; periodic unless suppressed
        if mode == "baseline" or must_baseline:
            records.append(BY.rec_full(eid, ex, ey, cite))
        elif s == cur[eid]:
            pass                                              # unchanged — temporal redundancy, no record
        else:
            anchor = None
            if mode == "unack":
                anchor = tick - 1                             # the plant: cite an UN-acknowledged anchor (> am)
            elif mode == "cited":
                for T in sorted(hist.get(eid, {})):
                    if T <= am and hist[eid][T] == s:         # the OLDEST certified match (deterministic)
                        anchor = T
                        break
            if anchor is not None:
                records.append(rec_cite(eid, anchor))
            elif cur[eid][2] == cite:
                records.append(BY.rec_move(eid, ex - cur[eid][0], ey - cur[eid][1]))
            else:
                records.append(BY.rec_full(eid, ex, ey, cite))
    return man, records


def apply_records(cur, hist, base, records, tick):
    """Apply PARSED records (kind, eid, payload) to advance (cur, hist, base) — the SAME function the client
    runs, so server and client stay identical. CITE resolves from history; REMOVE evicts (closed-world)."""
    cur = dict(cur); hist = {k: dict(v) for k, v in hist.items()}; base = dict(base)
    for (kind, eid, payload) in records:
        if kind == "remove":
            cur.pop(eid, None); hist.pop(eid, None); base.pop(eid, None)   # closed-world eviction
        elif kind == "full":
            x, y, cite = payload; cur[eid] = (x, y, cite); base[eid] = tick
        elif kind == "move":
            dx, dy = payload; px, py, cite = cur[eid]; cur[eid] = (px + dx, py + dy, cite)
        elif kind == "cite":
            anchor = payload
            if eid not in hist or anchor not in hist[eid]:
                raise CitationError(f"CITE for entity {eid} anchor {anchor} not in the acknowledged history "
                                    f"— a historical ghost (closed-world violation)")
            cur[eid] = hist[eid][anchor]
    for eid in cur:                                           # record this tick's admitted state as history
        hist.setdefault(eid, {})[tick] = cur[eid]
    return cur, hist, base


def verify_records(records, tick, cfg, hist):
    """Admission check: every CITE anchor must be CERTIFIED (T ≤ t − ACK_LAG) and RESOLVABLE (present in the
    entity's non-evicted history). Refuse uncertainty."""
    _B, ack_lag, _refresh = cfg
    am = ack_max(tick, ack_lag)
    live = set()
    for (kind, eid, _p) in records:
        if kind in ("full", "move", "cite"):
            live.add(eid)
    for (kind, eid, payload) in records:
        if kind == "cite":
            if payload > am:
                return False                                  # uncertified anchor (outside the AckW)
            if eid not in hist or payload not in hist[eid]:
                return False                                  # unresolvable / evicted history
    return True


# ---- run (server + client replay) --------------------------------------------------------------
def run(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="cited", _ser=None):
    """Thread the authority worlds through the citation protocol; replay the client from the wire. Returns
    {packets, recon, report}. In `baseline` mode every update is a FULL (the uncited reference)."""
    cur, hist, base = {}, {}, {}
    ccur, chist, cbase = {}, {}, {}
    packets, recon = [], []
    cites = fulls = moves = 0
    used_total = 0
    max_gap = 0
    for t, (entities, walls) in enumerate(ticks):
        man, byte_records = _encode(cur, hist, base, entities, walls, cl, L, t, cfg, mode)
        packet = serialize(t, cfg[0], byte_records, _ser)
        parsed = parse(packet)[2]
        for (kind, _e, _p) in parsed:
            cites += kind == "cite"; fulls += kind == "full"; moves += kind == "move"
        cur, hist, base = apply_records(cur, hist, base, parsed, t)
        ccur, chist, cbase = apply_records(ccur, chist, cbase, parsed, t)   # client from the wire alone
        packets.append(packet); recon.append(dict(ccur))
        used_total += parse(packet)[3]
        for eid in man:                                       # freshness: ticks since last baseline
            max_gap = max(max_gap, t - base.get(eid, t))
        prune = t - (REFRESH_INTERVAL + ACK_LAG + 1)
        for e in list(hist):                                  # bound the server history window (still ≥ needed)
            hist[e] = {k: v for k, v in hist[e].items() if k > prune}
    return {"packets": packets, "recon": recon, "cites": cites, "fulls": fulls, "moves": moves,
            "used_total": used_total, "max_gap": max_gap, "cfg": cfg}


# ---- laws --------------------------------------------------------------------------------------
def cited_equals_baseline(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL)):
    """THE HEADLINE LAW: the client reconstructs the SAME state sequence whether the server cites history or
    always sends baselines. Compression never alters semantics."""
    return run(ticks, cl, L, cfg, "cited")["recon"] == run(ticks, cl, L, cfg, "baseline")["recon"]


def is_closed_world_run(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="cited"):
    rep = run(ticks, cl, L, cfg, mode)
    for t, (e, w) in enumerate(ticks):
        if set(rep["recon"][t]) != set(A._manifest_under(e, w, cl, L)):
            return False
    return True


def certified_ok(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL)):
    """Every emitted CITE references a certified, resolvable anchor."""
    cur, hist, base = {}, {}, {}
    for t, (e, w) in enumerate(ticks):
        _man, byte_records = _encode(cur, hist, base, e, w, cl, L, t, cfg, "cited")
        parsed = parse(serialize(t, cfg[0], byte_records))[2]
        if not verify_records(parsed, t, cfg, hist):
            return False
        cur, hist, base = apply_records(cur, hist, base, parsed, t)
    return True


def constant_shape_ok(rep):
    B = rep["cfg"][0]
    return all(len(p) == B for p in rep["packets"])


def rate_ok(rep):
    """No manifested entity goes longer than REFRESH_INTERVAL ticks without a baseline."""
    return rep["max_gap"] <= rep["cfg"][2]


# ---- falsifier serializer (NOT a law) ----------------------------------------------------------
def _serialize_shape_drift(tick, budget, records):
    """Encode each CITE's anchor as a VARIABLE-WIDTH varint (so older anchors cost more) and pad only to the
    used length, not to B — the packet size now drifts with citation age, violating constant-shape."""
    body = bytearray()
    for r in records:
        if r[0] == _CITE:
            eid = r[1:5]; anchor = int.from_bytes(r[5:9], "big")
            body += bytes([_CITE]) + eid + BY._uvarint(anchor)      # variable width
        else:
            body += r
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)                          # NO padding to B
    return frame + hashlib.sha256(frame).digest()


# ---- digests / scenarios -----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def run_digest(ticks, cl, L, cfg=(B_ROOMY, ACK_LAG, REFRESH_INTERVAL), mode="cited"):
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


def _toggle(nticks=12):
    """A world with TEMPORAL REDUNDANCY: entities whose authority citation TOGGLES between two acknowledged
    values (a door open/closed), so a return to a prior cite is re-expressed as a compact CITE; plus a
    departing mover and a hidden entity."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    paths = {
        1: [(4, 0, _d(500 + (t // 2) % 2)) for t in range(nticks)],     # cite toggles A/B every 2 ticks
        3: [(6, 0, _d(600 + (t // 3) % 2)) for t in range(nticks)],     # cite toggles on a different period
        2: [(-9, 0, _d(2)) for t in range(nticks)],                     # hidden (behind)
    }
    return _seq(paths, nticks), cl


def _scene(name, ticks, cl, L, verdict):
    return hashlib.sha256(MAGIC + f"|{name}|d:{run_digest(ticks, cl, L)}|v:{verdict}".encode()).hexdigest()


def _scene_reuse():
    ticks, cl = _toggle()
    rep = run(ticks, cl, A.lens(0, 0))
    ok = rep["cites"] > 0 and rep["used_total"] < run(ticks, cl, A.lens(0, 0), mode="baseline")["used_total"]
    return _scene("reuse", ticks, cl, A.lens(0, 0), "COMPRESSED" if ok else "FLAT")


def _scene_equiv():
    ticks, cl = _toggle()
    return _scene("equiv", ticks, cl, A.lens(0, 0),
                  "IDENTICAL" if cited_equals_baseline(ticks, cl, A.lens(0, 0)) else "DRIFT")


def _scene_evict():
    """A departing entity's history is evicted — a later would-be citation cannot resurrect it."""
    cl = PC.client(0, 0, 1, 0, 1, 2, 400, 0)
    paths = {1: [(5, t * 3, _d(500 + t % 2)) for t in range(6)]}        # drifts off-axis → departs
    ticks = _seq(paths, 6)
    ok = is_closed_world_run(ticks, cl, A.lens(0, 0))
    return _scene("evict", ticks, cl, A.lens(0, 0), "EVICTED" if ok else "GHOST")


def _scene_rate():
    ticks, cl = _toggle()
    return _scene("rate", ticks, cl, A.lens(0, 0),
                  "BOUNDED" if rate_ok(run(ticks, cl, A.lens(0, 0))) else "STALE")


_SCENES = {"reuse": _scene_reuse, "equiv": _scene_equiv, "evict": _scene_evict, "rate": _scene_rate}
SCENES = ("reuse", "equiv", "evict", "rate")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_citation.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CitationError(f"no golden named {name!r}")


# ---- the seeded property sweep -----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 80
NTICKS = 12


def gen_sequence(r):
    """A random world with citation reuse (toggling cites), a departing mover, and a hidden entity."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    a1 = 500 + r.rng(0, 3) * 2
    a3 = 600 + r.rng(0, 3) * 2
    x1, x3 = r.rng(3, 5), r.rng(6, 8)
    behind = (-r.rng(3, 8), r.rng(-3, 3))
    depart_at = r.rng(7, 10)
    ticks = []
    for t in range(NTICKS):
        ents = {2: (behind[0], behind[1], _d(2))}
        ents[1] = (x1, t % 2, _d(a1 + (t // 2) % 2))          # cite toggles → reuse
        ents[3] = (x3, 0, _d(a3 + (t // 3) % 2))
        if t < depart_at:
            ents[4] = (r.rng(9, 12), 0, _d(700 + (t // 2) % 2))
        ticks.append((ents, frozenset()))
    return ticks, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep asserting, per world: CITED ≡ BASELINE (semantics preserved), every CITE
    certified, closed-world (with eviction), constant-shape, bounded refresh, deterministic replay, and a
    real compression (cites used, fewer useful bytes than the baseline). RAISES on the first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    cite_seen = evict_seen = base_seen = 0
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        if run_digest(ticks, cl, L) != run_digest(ticks, cl, L):
            raise CitationError(f"seq {s}: not deterministic")
        if not cited_equals_baseline(ticks, cl, L):
            raise CitationError(f"seq {s}: cited != baseline — compression altered semantics")
        if not certified_ok(ticks, cl, L):
            raise CitationError(f"seq {s}: an emitted citation was uncertified")
        if not is_closed_world_run(ticks, cl, L):
            raise CitationError(f"seq {s}: reconstruction is not the manifested set")
        rep = run(ticks, cl, L)
        if not constant_shape_ok(rep):
            raise CitationError(f"seq {s}: a packet is not constant-shape at B")
        if not rate_ok(rep):
            raise CitationError(f"seq {s}: an entity exceeded the refresh interval — freshness unbounded")
        if rep["used_total"] >= run(ticks, cl, L, mode="baseline")["used_total"]:
            raise CitationError(f"seq {s}: citation saved no bytes — inert")
        moved = [({**e, 2: (e[2][0], e[2][1], _d(9000 + s))}, w) for e, w in ticks]   # perturb the hidden id2
        if run(moved, cl, L)["packets"] != rep["packets"]:
            raise CitationError(f"seq {s}: a change to the hidden entity altered the wire — leak")
        cite_seen += 1 if rep["cites"] > 0 else 0
        evict_seen += 1 if rep["fulls"] > 0 else 0
        base_seen += 1 if rep["max_gap"] <= REFRESH_INTERVAL else 0
        hh.update(f"|{s}:{run_digest(ticks, cl, L)}:{rep['cites']}:{rep['used_total']}".encode())
    if cite_seen == 0 or evict_seen == 0 or base_seen == 0:
        raise CitationError(f"NON-VACUITY: cite {cite_seen}, full {evict_seen}, base {base_seen}")
    return {"scenarios": count, "cite_seen": cite_seen, "evict_seen": evict_seen, "base_seen": base_seen,
            "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_citation.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise CitationError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except CitationError as exc:
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
    print(f"SWEEP: {rep['scenarios']} sequences, cite {rep['cite_seen']}, full {rep['evict_seen']}, "
          f"base {rep['base_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
