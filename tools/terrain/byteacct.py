# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""byteacct — PROOF-CARRYING BYTE ACCOUNTING (URDRBYT1): the wire-level refinement of the adaptive
scheduler. The scheduler proves WHICH entities are served under a bounded refresh COUNT; this rung proves
the same properties under a real BYTE budget, where updates have different serialized costs — and makes the
byte total a replayable artifact: the scheduler's decision, the serialized packet, and the measured byte
count are all deterministic consequences of the same world. Composition over `schedule`/`throttle`/
`anamorphosis`/`perception`, NO NEW GLYPH — the kernel stays frozen. See `docs/byteacct_brief.md` for the
design pass and the D1 §20 glyph ruling.

THE UNIFICATION (how this preserves the perception hardening rather than undoing it). A variable-length
packet would re-open the timing/bandwidth side-channel URDRPCP1 closed. So the BYTE BUDGET `B` IS THE
CONSTANT PACKET SIZE: every tick emits EXACTLY `B` bytes — variable-size delta records followed by anonymous
padding to `B`. The emitted transcript never exceeds `B` (it equals `B`), constant-shape is preserved (no
visible-count leak), and the accounting proves the USEFUL record bytes ≤ `B − overhead`. Byte-accounting
COMPOSES with the constant-shape hardening; the budget is the size.

THE BYTE BUDGET THEOREM. For any tick, the emitted packet is exactly `B` bytes and its records never exceed
the body budget `B − OVERHEAD`. The MANDATORY records — departures (REMOVE) and entrants (FULL), which
membership needs — are emitted first; if they alone cannot fit, the scheduler explicitly REFUSES (a typed
`BYTEACCT-REFUSE`, never a silent drop). The DISCRETIONARY position updates (the due-known set, in the
scheduler's priority order) are admitted as the deterministic MAXIMAL PREFIX that fits; the rest defer and
age. The remaining body is anonymous padding.

THE SERIALIZATION (deterministic, exact-integer, canonical). A record is `tag | eid | payload`:
  * REMOVE (tag 0) — a departed entity (membership drop);
  * MOVE  (tag 2) — a position delta `zigzag-varint(dx), zigzag-varint(dy)` (small move = few bytes);
  * FULL  (tag 1) — an absolute position + the 32-byte authority citation (an entrant or a cite change).
Varints are CANONICAL (minimal length); positions are exact integers (no floats). Identical worlds serialize
to identical byte streams.

THE GATE-CHECKED LAWS (red-first — the plants bite before the goldens pin):
  * BYTE BUDGET — the packet is exactly `B`, records ≤ body budget; `_pack_overrun` exceeds it.
  * MAXIMAL PREFIX / FRAGMENTATION — the admitted discretionary set is the priority PREFIX, independent of
    packing cleverness; `_pack_firstfit` (skip a non-fitting update and continue) admits a different set.
  * VARIABLE-SIZE STARVATION-FREEDOM — a large update, when it is oldest, is admitted before smaller newer
    ones (age-first prefix); `_pack_smallest_first` starves the large update.
  * SERIALIZATION STABILITY — identical worlds → identical bytes, and every record round-trips and is
    CANONICAL; `_serialize_noncanonical` (non-minimal varint) is caught.
  * ACCOUNTING FIDELITY — the reported useful-byte total equals the actual serialized record bytes;
    `_report_wrong` forges it.
  * CLOSED-WORLD (membership live) — the client reconstructs the manifested set from the WIRE alone; a
    departure is mandatory, so `_drop_departure` (budget away a REMOVE) leaves a ghost and is caught.
  * DETERMINISTIC REPLAY — a run is a pure function of (ticks, lens, byte budget); the wall-clock plant
    diverges. REDUCES TO THE SCHEDULE at a large budget (every due update fits — no byte pressure).

GRADE: MEASURED. DECLARED: inherits every scheduler/throttle/anamorphosis/perception boundary; adds a NEW
declared boundary — under byte pressure a position update may defer (staleness up to the scheduler's bound
plus the byte-deferral), the cost of the byte cap; bounded and declared (raise `B`). `does_not_show`:
compression of the citation (the 32-byte authority digest is sent whole on a FULL); multi-packet
fragmentation across ticks (one packet per tick); cross-placement (URDRBYT1 Python reference only)."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import schedule as SC                                            # the rung this composes over  # noqa: E402
import throttle as TH                                            # noqa: E402
import anamorphosis as A                                         # noqa: E402
import perception as PC                                          # noqa: E402

MAGIC = b"URDRBYT1"
DIGEST_BYTES = A.DIGEST_BYTES
COARSEST = A.COARSEST
OVERHEAD = len(MAGIC) + 4 + 4 + 4 + DIGEST_BYTES               # MAGIC | tick | budget | count | digest
_REMOVE, _FULL, _MOVE = 0, 1, 2


class ByteAcctError(Exception):
    def __init__(self, message):
        super().__init__(f"BYTEACCT-REFUSE: {message}")
        self.code = "BYTEACCT-REFUSE"


# ---- canonical zigzag varint ------------------------------------------------------------------
def _zz(n):
    return (n << 1) if n >= 0 else ((-n) << 1) - 1


def _unzz(z):
    return (z >> 1) if (z & 1) == 0 else -((z + 1) >> 1)


def _uvarint(u):
    if u < 0:
        raise ByteAcctError("varint is unsigned")
    out = bytearray()
    while True:
        b = u & 0x7F
        u >>= 7
        if u:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _read_uvarint(buf, off):
    shift = 0
    res = 0
    start = off
    while True:
        b = buf[off]; off += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    if off - start > 1 and buf[off - 1] == 0:
        raise ByteAcctError("non-canonical varint (trailing zero continuation)")   # canonicity
    return res, off


# ---- records ----------------------------------------------------------------------------------
def rec_remove(eid):
    return bytes([_REMOVE]) + eid.to_bytes(4, "big")


def rec_move(eid, dx, dy):
    return bytes([_MOVE]) + eid.to_bytes(4, "big") + _uvarint(_zz(dx)) + _uvarint(_zz(dy))


def rec_full(eid, x, y, cite_hex):
    return bytes([_FULL]) + eid.to_bytes(4, "big") + _uvarint(_zz(x)) + _uvarint(_zz(y)) \
        + PC._cite_bytes(cite_hex)


def _read_record(buf, off):
    tag = buf[off]; off += 1
    eid = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if tag == _REMOVE:
        return ("remove", eid, None), off
    if tag == _MOVE:
        zx, off = _read_uvarint(buf, off); zy, off = _read_uvarint(buf, off)
        return ("move", eid, (_unzz(zx), _unzz(zy))), off
    if tag == _FULL:
        zx, off = _read_uvarint(buf, off); zy, off = _read_uvarint(buf, off)
        cite = buf[off:off + DIGEST_BYTES].hex(); off += DIGEST_BYTES
        return ("full", eid, (_unzz(zx), _unzz(zy), cite)), off
    raise ByteAcctError(f"unknown record tag {tag}")


# ---- the packet (exactly `budget` bytes — constant-shape at B) --------------------------------
def _pack(mandatory, discretionary, body_budget):
    """Admit ALL mandatory records (or REFUSE), then the deterministic MAXIMAL PREFIX of discretionary that
    fits. Returns (admitted_records, used_bytes)."""
    used = sum(len(r) for r in mandatory)
    if used > body_budget:
        raise ByteAcctError(f"mandatory records {used}B exceed the body budget {body_budget}B — the byte "
                            f"budget cannot preserve membership this tick")
    admitted = list(mandatory)
    for r in discretionary:
        if used + len(r) <= body_budget:
            admitted.append(r); used += len(r)
        else:
            break                                              # maximal PREFIX — stop at the first non-fit
    return admitted, used


def serialize(tick, budget, records):
    """Serialize the admitted records into EXACTLY `budget` bytes: header, records, anonymous padding to the
    body budget, digest. Constant-shape at B."""
    body_budget = budget - OVERHEAD
    body = bytearray()
    for r in records:
        body += r
    if len(body) > body_budget:
        raise ByteAcctError(f"records {len(body)}B exceed the body budget {body_budget}B")
    body += b"\x00" * (body_budget - len(body))                # anonymous padding — no identity
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)
    return frame + hashlib.sha256(frame).digest()


def parse(packet):
    if not (type(packet) is bytes or type(packet) is bytearray):
        raise ByteAcctError("a packet must be bytes")
    t = bytes(packet)
    if t[:len(MAGIC)] != MAGIC:
        raise ByteAcctError("bad magic — not a URDRBYT1 packet")
    if len(t) < OVERHEAD:
        raise ByteAcctError("packet too small")
    if hashlib.sha256(t[:-DIGEST_BYTES]).digest() != t[-DIGEST_BYTES:]:
        raise ByteAcctError("digest mismatch — tampered or truncated")
    tick = int.from_bytes(t[8:12], "big")
    budget = int.from_bytes(t[12:16], "big")
    count = int.from_bytes(t[16:20], "big")
    if len(t) != budget:
        raise ByteAcctError(f"packet length {len(t)} != declared budget {budget} (not constant-shape at B)")
    off = OVERHEAD - DIGEST_BYTES
    records = []
    for _ in range(count):
        rec, off = _read_record(t, off)
        records.append(rec)
    return tick, budget, records, off - (OVERHEAD - DIGEST_BYTES)   # (…, used_body_bytes)


# ---- the stateful step (server) and the client replay -----------------------------------------
def _importance(entities, cl, L, eid):
    return COARSEST - A.shift_of(entities, cl, L, eid)


def _due(state, entities, cl, L, tick, eid):
    prev = state.get(eid)
    if prev is None:
        return True
    return (tick - prev[3]) >= TH.rate_of(A.shift_of(entities, cl, L, eid))


def _build(state, entities, walls, cl, L, tick):
    """Return (manifest, mandatory_records, discretionary_pairs). `state` is {eid:(x,y,cite,as_of)} — the
    last SHOWN record (what the client holds). discretionary_pairs are (eid, record) in priority order."""
    man = A._manifest_under(entities, walls, cl, L)
    man_set = set(man)
    mandatory = []
    for eid in sorted(state):                                  # departures → REMOVE (mandatory)
        if eid not in man_set:
            mandatory.append(rec_remove(eid))
    for eid in man:                                            # entrants → FULL (mandatory)
        if eid not in state:
            ex, ey, cite = entities[eid]
            mandatory.append(rec_full(eid, ex, ey, cite))
    due = [e for e in man if e in state and _due(state, entities, cl, L, tick, e)]
    due.sort(key=lambda e: (tick - state[e][3], _importance(entities, cl, L, e), -e), reverse=True)
    disc = []
    for eid in due:
        ex, ey, cite = entities[eid]
        px, py, pcite, _asof = state[eid]
        if cite != pcite:
            disc.append((eid, rec_full(eid, ex, ey, cite)))    # a cite change needs a FULL
        else:
            disc.append((eid, rec_move(eid, ex - px, ey - py)))
    return man, mandatory, disc


def step(state, entities, walls, cl, L, tick, budget, _pack_fn=_pack, _clock=None):
    """One tick: emit the byte-budgeted packet and advance the (shared) client/server state. Returns
    (packet, new_state, manifest, used_body_bytes, admitted_disc_eids)."""
    man, mandatory, disc = _build(state, entities, walls, cl, L, tick)
    disc_recs = [r for (_e, r) in disc]
    drift = 0 if _clock is None else _clock()
    if drift:                                                  # the wall-clock plant reorders discretionary
        disc_recs = list(reversed(disc_recs))
    admitted, used = _pack_fn(mandatory, disc_recs, budget - OVERHEAD)
    admitted_set = set(admitted)
    packet = serialize(tick, budget, admitted)
    # advance state to exactly what the client will hold after applying `admitted`
    admitted_disc = [e for (e, r) in disc if r in admitted_set]
    new_state = {}
    for eid in man:
        ex, ey, cite = entities[eid]
        if eid not in state or eid in set(admitted_disc):
            s = A.shift_of(entities, cl, L, eid)
            new_state[eid] = (ex, ey, cite, tick)              # refreshed (entrant or admitted move)
        else:
            new_state[eid] = state[eid]                        # carried (deferred or not due)
    return packet, new_state, man, used, admitted_disc


def client_apply(cstate, packet):
    """The CLIENT: reconstruct full state from the WIRE alone by applying a packet to the carried state."""
    _tick, _budget, records, _used = parse(packet)
    st = dict(cstate)
    for (kind, eid, payload) in records:
        if kind == "remove":
            st.pop(eid, None)
        elif kind == "full":
            x, y, cite = payload
            st[eid] = (x, y, cite)
        else:                                                  # move
            dx, dy = payload
            px, py, cite = st[eid]
            st[eid] = (px + dx, py + dy, cite)
    return st


def run(ticks, cl, L, budget, _pack_fn=_pack, _clock=None):
    """Thread a sequence of authority worlds through the byte accountant. Also replays the CLIENT from the
    wire and records the reconstructed states, so closed-world is checked against the packets alone."""
    state = {}
    cstate = {}
    packets = []
    recon = []
    used_total = manifest_total = deferrals = departures = max_stale = max_used = 0
    prev_man = set()
    for t, (entities, walls) in enumerate(ticks):
        man, mandatory, disc = _build(state, entities, walls, cl, L, t)
        packet, state, man2, used, admitted_disc = step(state, entities, walls, cl, L, t, budget,
                                                         _pack_fn, _clock)
        cstate = client_apply(cstate, packet)                  # the client reconstructs from the wire
        packets.append(packet)
        recon.append({e: v[:3] for e, v in state.items()})
        used_total += used; manifest_total += len(man2)
        deferrals += len(disc) - len(admitted_disc)
        departures += len(prev_man - set(man2))
        max_used = max(max_used, used)
        for _e, (_x, _y, _c, asof) in state.items():
            max_stale = max(max_stale, t - asof)
        prev_man = set(man2)
    return {"packets": packets, "recon": recon, "cstate_final": cstate, "used_total": used_total,
            "manifest_total": manifest_total, "deferrals": deferrals, "departures": departures,
            "max_stale": max_stale, "max_used": max_used, "budget": budget}


# ---- laws -------------------------------------------------------------------------------------
def byte_budget_ok(report):
    """Every packet is EXACTLY the budget, and records fit the body budget."""
    B = report["budget"]
    for p in report["packets"]:
        if len(p) != B:
            return False
        _t, _b, _recs, used = parse(p)
        if used > B - OVERHEAD:
            return False
    return report["max_used"] <= B - OVERHEAD


def is_closed_world(entities, walls, cl, L, packet, cstate_before):
    """MEMBERSHIP LIVE from the wire: applying the packet to the carried client state yields EXACTLY the
    manifested set."""
    st = client_apply(cstate_before, packet)
    return set(st) == set(A._manifest_under(entities, walls, cl, L))


def _reencode(rec):
    kind, eid, payload = rec
    if kind == "remove":
        return rec_remove(eid)
    if kind == "full":
        x, y, cite = payload
        return rec_full(eid, x, y, cite)
    dx, dy = payload
    return rec_move(eid, dx, dy)


def accounting_fidelity(report):
    """PROOF-CARRYING ACCOUNTING: each packet must equal the CANONICAL re-serialization of its own declared
    records — the reported byte usage is exactly the transmitted content, with nothing hidden in the
    padding and no under-count. Also confirms the reported total equals the measured record bytes."""
    total = 0
    for p in report["packets"]:
        tick, budget, records, used = parse(p)
        if serialize(tick, budget, [_reencode(r) for r in records]) != p:
            return False                                       # a mismatch = hidden bytes or a mis-count
        total += used
    return total == report["used_total"]


def client_matches_server(report):
    """The wire is SUFFICIENT: the client's from-scratch reconstruction equals the server's state each
    tick — an attested replay of exactly what crossed the wire."""
    cstate = {}
    for t, p in enumerate(report["packets"]):
        cstate = client_apply(cstate, p)
        if {e: v for e, v in cstate.items()} != report["recon"][t]:
            return False
    return True


def prefix_correct(ticks, cl, L, budget):
    """The admitted discretionary set at each tick is exactly the priority PREFIX that fits."""
    state = {}
    for t, (entities, walls) in enumerate(ticks):
        man, mandatory, disc = _build(state, entities, walls, cl, L, t)
        used = sum(len(r) for r in mandatory)
        prefix = []
        for (eid, r) in disc:
            if used + len(r) <= budget - OVERHEAD:
                prefix.append(eid); used += len(r)
            else:
                break
        _p, state, _m, _u, admitted = step(state, entities, walls, cl, L, t, budget)
        if admitted != prefix:
            return False
    return True


# ---- falsifier packers / serializers (NOT laws) -----------------------------------------------
def _pack_overrun(mandatory, discretionary, body_budget):
    """BUDGET VIOLATION: admit EVERY record, ignoring the body budget. Paired with `_serialize_nopad` it
    emits a packet longer than B — the byte-budget law (len == B) catches it."""
    all_recs = list(mandatory) + list(discretionary)
    return all_recs, sum(len(r) for r in all_recs)


def _serialize_nopad(tick, budget, records):
    """A serializer that neither enforces the body budget nor pads to B — the packet length equals its
    content, so an over-budget record set produces `len(packet) != budget`, caught by byte_budget_ok."""
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + b"".join(records)
    return frame + hashlib.sha256(frame).digest()


def _serialize_hidden(tick, budget, records):
    """ACCOUNTING FORGERY: emit the records honestly but stuff NON-ZERO bytes into the anonymous padding
    (smuggling data while the header under-reports). The canonical re-serialization check catches it."""
    body_budget = budget - OVERHEAD
    body = bytearray()
    for r in records:
        body += r
    body += b"\x7f" * (body_budget - len(body))                # BUG: non-zero padding hides bytes
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)
    return frame + hashlib.sha256(frame).digest()


def _run_drop_departure(ticks, cl, L, budget):
    """THE GHOST: never emit REMOVE records, so a departed entity's last record lingers in the client's
    reconstruction. Breaks closed-world. Returns (packets, cstates)."""
    state = {}
    cstate = {}
    packets = []
    cstates = []
    for t, (entities, walls) in enumerate(ticks):
        man, mandatory, disc = _build(state, entities, walls, cl, L, t)
        mandatory = [r for r in mandatory if r[0] != _REMOVE]  # BUG: drop the departure markers
        disc_recs = [r for (_e, r) in disc]
        admitted, _used = _pack(mandatory, disc_recs, budget - OVERHEAD)
        packet = serialize(t, budget, admitted)
        adm = set(admitted)
        new_state = {}
        for eid in man:
            ex, ey, cite = entities[eid]
            if eid not in state or any(r for (e, r) in disc if e == eid and r in adm):
                new_state[eid] = (ex, ey, cite, t)
            else:
                new_state[eid] = state[eid]
        state = new_state
        cstate = client_apply(cstate, packet)
        packets.append(packet); cstates.append(cstate)
    return packets, cstates


def _pack_firstfit(mandatory, discretionary, body_budget):
    used = sum(len(r) for r in mandatory)
    admitted = list(mandatory)
    for r in discretionary:                                    # BUG: skip a non-fitting record and continue
        if used + len(r) <= body_budget:
            admitted.append(r); used += len(r)
    return admitted, used


def _pack_smallest_first(mandatory, discretionary, body_budget):
    used = sum(len(r) for r in mandatory)
    admitted = list(mandatory)
    for r in sorted(discretionary, key=len):                   # BUG: smallest-first — starves large updates
        if used + len(r) <= body_budget:
            admitted.append(r); used += len(r)
    return admitted, used


def _serialize_noncanonical(tick, budget, records):
    """A serializer whose varints are NON-MINIMAL (a padded continuation) — decodes to the same values but
    is not canonical; the parser's canonicity check rejects it."""
    body_budget = budget - OVERHEAD
    body = bytearray()
    for r in records:
        if r[0] == _MOVE:                                      # re-encode the deltas non-minimally
            eid = r[1:5]
            zx, o = _read_uvarint(r, 5); zy, _o2 = _read_uvarint(r, o)
            body += bytes([_MOVE]) + eid + bytes([(zx & 0x7F) | 0x80, 0x00]) \
                + bytes([(zy & 0x7F) | 0x80, 0x00])            # 2-byte padded varint (non-minimal)
        else:
            body += r
    body = body[:body_budget] + b"\x00" * max(0, body_budget - len(body))
    head = bytearray(MAGIC) + (tick & 0xFFFFFFFF).to_bytes(4, "big") + budget.to_bytes(4, "big") \
        + len(records).to_bytes(4, "big")
    frame = bytes(head) + bytes(body)
    return frame + hashlib.sha256(frame).digest()


# ---- digests / scenarios ----------------------------------------------------------------------
def _d(i):
    return PC._d(i)


def run_digest(ticks, cl, L, budget):
    hh = hashlib.sha256(); hh.update(MAGIC)
    for p in run(ticks, cl, L, budget)["packets"]:
        hh.update(hashlib.sha256(p).digest())
    return hh.hexdigest()


def _seq(paths, nticks):
    ticks = []
    for t in range(nticks):
        ents = {eid: (xs[t][0], xs[t][1], xs[t][2] if len(xs[t]) > 2 else _d(eid)) for eid, xs in paths.items()}
        ticks.append((ents, frozenset()))
    return ticks


_BH = (-9, 0)                                                  # a "behind the viewpoint" holding spot (hidden)


def _contended(nticks=12):
    """Mixed update sizes under a tight byte budget: entities enter ONE PER TICK (so the initial keyframe is
    a single FULL, never a refuse), a near jitterer sends small MOVEs, and two entities change their
    citation every tick (large discretionary FULLs) so the byte budget genuinely binds."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    paths = {
        1: [(5, t % 2, _d(1)) for t in range(nticks)],                                  # present t0, MOVE
        4: [(_BH[0], _BH[1], _d(4)) if t < 1 else (3, t % 2, _d(400 + t)) for t in range(nticks)],  # t1, FULL/tick
        5: [(_BH[0], _BH[1], _d(5)) if t < 2 else (4, t % 2, _d(900 + t)) for t in range(nticks)],  # t2, FULL/tick
    }
    return _seq(paths, nticks), cl


def _starve(nticks=20):
    """A starvation stress: two near jitterers (small MOVEs, rate 1 — due every tick) plus ONE close entity
    that changes its cite every tick (a large FULL, rate 1). Under a budget that fits the two MOVEs and only
    then a little more, a smallest-first packer takes both MOVEs and NEVER the FULL — starving it forever;
    age-first admits the FULL when it becomes oldest, so its staleness stays bounded."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    paths = {
        1: [(2, t % 2, _d(1)) for t in range(nticks)],                                   # present t0, rate 1
        3: [(_BH[0], _BH[1], _d(3)) if t < 1 else (3, t % 2, _d(3)) for t in range(nticks)],   # enters t1
        9: [(_BH[0], _BH[1], _d(9)) if t < 2 else (4, t % 2, _d(700 + t)) for t in range(nticks)],  # t2, FULL/tick
    }
    return _seq(paths, nticks), cl


def _scene(name, ticks, cl, L, budget, verdict):
    return hashlib.sha256(MAGIC + f"|{name}|L:{L[0]}:{L[1]}|B:{budget}|d:{run_digest(ticks, cl, L, budget)}"
                          f"|v:{verdict}".encode()).hexdigest()


_SB = OVERHEAD + 46                                            # a tight byte budget → contention


def _scene_budget():
    ticks, cl = _contended()
    rep = run(ticks, cl, A.lens(0, 0), _SB)
    ok = byte_budget_ok(rep) and rep["deferrals"] > 0
    return _scene("budget", ticks, cl, A.lens(0, 0), _SB, "BUDGETED" if ok else "OVER")


def _scene_prefix():
    ticks, cl = _contended()
    ok = prefix_correct(ticks, cl, A.lens(0, 0), _SB)
    return _scene("prefix", ticks, cl, A.lens(0, 0), _SB, "PREFIX" if ok else "FRAGMENTED")


def _scene_account():
    ticks, cl = _contended()
    rep = run(ticks, cl, A.lens(0, 0), _SB)
    ok = accounting_fidelity(rep) and client_matches_server(rep)
    return _scene("account", ticks, cl, A.lens(0, 0), _SB, "ATTESTED" if ok else "FORGED")


def _scene_reduce():
    ticks, cl = _contended()
    rep = run(ticks, cl, A.lens(0, 0), OVERHEAD + 400)         # roomy budget → no byte pressure
    ok = rep["deferrals"] == 0
    return _scene("reduce", ticks, cl, A.lens(0, 0), OVERHEAD + 400, "SCHEDULE" if ok else "DEFER")


_SCENES = {"budget": _scene_budget, "prefix": _scene_prefix,
           "account": _scene_account, "reduce": _scene_reduce}
SCENES = ("budget", "prefix", "account", "reduce")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_byteacct.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ByteAcctError(f"no golden named {name!r}")


# ---- the seeded property sweep ----------------------------------------------------------------
SWEEP_SEED = 20260724
SWEEP_COUNT = 70
NTICKS = 12
_BUDGETS = (OVERHEAD + 46, OVERHEAD + 70, OVERHEAD + 120)       # each fits at least one FULL keyframe record


def gen_sequence(r):
    """A contended world with STAGGERED single entries (so the tightest budget never refuses the keyframe),
    a hidden behind-entity (ground truth), a citation-changer (discretionary FULLs), and a departing
    mover (a REMOVE), with randomized positions and enter ticks."""
    cl = PC.client(0, 0, 1, 0, 4, 2, 400, 0)
    x1, x3, x4, x5 = r.rng(3, 5), r.rng(6, 8), r.rng(9, 11), r.rng(3, 5)
    behind = (-r.rng(3, 8), r.rng(-3, 3))
    depart_at = r.rng(7, 9)
    ticks = []
    for t in range(NTICKS):
        ents = {2: (behind[0], behind[1], _d(2))}              # hidden (behind)
        ents[1] = (x1, t % 2, _d(1))                           # present t0, small MOVEs
        if t >= 1:
            ents[3] = (x3, t % 2, _d(3))                       # enters t1
        if t >= 2:
            ents[5] = (x5, t % 2, _d(900 + t))                 # enters t2, cite changes → FULL/tick
        if t >= 3:
            ents[4] = (_BH[0], _BH[1], _d(4)) if t >= depart_at else (x4, t % 2, _d(4))   # enters t3, departs
        ticks.append((ents, frozenset()))
    return ticks, cl


def sweep(seed=SWEEP_SEED, count=SWEEP_COUNT):
    """The in-gate fixed-seed sweep over mixed-size moving worlds × byte budgets, asserting per run: byte
    budget (each packet exactly B, records within body budget), closed-world from the wire every tick,
    accounting fidelity, client==server replay, priority-prefix packing, hidden-set invariance, and
    deterministic replay. Non-vacuous: deferrals, departures, and cite-change FULLs exercised. RAISES on the
    first violation."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    r = PC._LCG(seed)
    deferrals = departures = stale_seen = prefix_checked = 0
    for s in range(count):
        ticks, cl = gen_sequence(r)
        L = A.lens(0, 0)
        for budget in _BUDGETS:
            rep = run(ticks, cl, L, budget)
            if run_digest(ticks, cl, L, budget) != run_digest(ticks, cl, L, budget):
                raise ByteAcctError(f"seq {s} B{budget}: not deterministic")
            if not byte_budget_ok(rep):
                raise ByteAcctError(f"seq {s} B{budget}: a packet broke the byte budget")
            if not accounting_fidelity(rep):
                raise ByteAcctError(f"seq {s} B{budget}: reported bytes != actual serialized bytes")
            if not client_matches_server(rep):
                raise ByteAcctError(f"seq {s} B{budget}: the client replay diverged from the server")
            if not prefix_correct(ticks, cl, L, budget):
                raise ByteAcctError(f"seq {s} B{budget}: the admitted set is not the priority prefix")
            prefix_checked += 1
            cstate = {}
            for t, (entities, walls) in enumerate(ticks):
                if not is_closed_world(entities, walls, cl, L, rep["packets"][t], cstate):
                    raise ByteAcctError(f"seq {s} B{budget} tick {t}: reconstruction is not the manifested set")
                cstate = client_apply(cstate, rep["packets"][t])
                moved = dict(entities); moved[2] = (entities[2][0], entities[2][1], _d(8000 + s))
                st = {}
                for u in range(t + 1):
                    e_u = moved if u == t else ticks[u][0]
                    p_u, st, _m, _us, _ad = step(st, e_u, walls, cl, L, u, budget)
                if p_u != rep["packets"][t]:
                    raise ByteAcctError(f"seq {s} B{budget} tick {t}: a hidden change altered the packet")
            deferrals += rep["deferrals"]; departures += rep["departures"]
            stale_seen += 1 if rep["max_stale"] > 0 else 0
            hh.update(f"|{s}:{budget}:{run_digest(ticks, cl, L, budget)}:{rep['used_total']}".encode())
    if deferrals == 0 or departures == 0 or stale_seen == 0 or prefix_checked == 0:
        raise ByteAcctError(f"NON-VACUITY: deferrals {deferrals}, departures {departures}, stale "
                            f"{stale_seen}, prefix {prefix_checked}")
    return {"scenarios": count, "deferrals": deferrals, "departures": departures, "stale_seen": stale_seen,
            "prefix_checked": prefix_checked, "digest": hh.hexdigest()}


def sweep_digest(seed=SWEEP_SEED, count=SWEEP_COUNT):
    return sweep(seed, count)["digest"]


def sweep_golden():
    with open(_os.path.join(_HERE, "conformance_byteacct.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == "sweep":
                    return dig
    raise ByteAcctError("no golden named 'sweep'")


def explore(base_seed, n_seeds, count=SWEEP_COUNT):
    found = []
    for kk in range(n_seeds):
        seed = (base_seed + kk * 2654435761) & 0x7FFFFFFF
        try:
            sweep(seed, count)
        except ByteAcctError as exc:
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
    print(f"SWEEP: {rep['scenarios']} sequences × {len(_BUDGETS)} budgets, deferrals {rep['deferrals']}, "
          f"departures {rep['departures']}, stale {rep['stale_seen']}")
    print(f"sweep digest={rep['digest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
