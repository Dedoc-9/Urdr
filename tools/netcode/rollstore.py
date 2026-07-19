# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""rollstore — the durable rollback window (N2.5 / T3.45, URDRRBS1): the N2-window/durable-window
UNIFICATION, and the settling of a recorded debt. Every terrain storage rung since `persist` carried
the same deferral — resurrect's does_not_show: "the netcode-layer analog (N2 rollback's in-memory
snapshots — unifying its window with this durable one is a future rung, stated not begun)." This is
that rung, begun and finished: the terrain arc's window law (one digest = integrity check + content
address + filename; restore-or-refuse; the priced window; the REAL death boundary) lands on N2's
rollback window, so the repo's two window disciplines become ONE law.

THE RECORDS. snapshot_record = MAGIC | tick | n | (pos.x pos.y vel.x vel.y as signed int64)* |
SHA-256 — 52 + 32·n, the Q32.32 state under the persist encoding discipline. log_record = the event
transcript (47 + 48·m). window_manifest = head | K | H | the (tick, digest) list IN ORDER + the
log's address (95 + 40·s) — a disordered manifest REFUSES, never re-sorts.

THE SOURCE LAW (resurrect's, verbatim). The event log is the REWINDABLE SOURCE: `restore_peer`
rebuilds the peer by replaying the log from the world's start — and the saved window is CHECKED
EVIDENCE, never trusted state: every restored snapshot must EQUAL the replay's regenerated window
bit-for-bit (tick, positions, velocities, count, head), or the restore REFUSES. Integrity is not
truth (L11): a crafted-but-digested snapshot whose physics disagrees with the replay is caught by
the cross-check, not welcomed by the digest.

THE THEOREMS. (1) restored == never-died, in EVERY observable — state, head, chain, known set,
window — and forever after (both peers finish the run identically, equal to the canonical N1
timeline). (2) ROLLBACK CROSSES DEATH: a real successor process (this file as __main__: argv =
store dir, manifest address, one late event; disk the only channel) restores, REWINDS on the
post-death input, and converges to `lockstep.simulate` bit-for-bit, twice. (3) THE LAW SURVIVES:
horizon refuse, identity conflict, duplicate absorption, and K-invariance hold identically on the
restored peer; the apply-at-head DEFECT still diverges (non-vacuity survives death). (4) THE PRICE:
window_cost = Σ snapshots + log + manifest, closed forms EQUAL to real bytes, gated by
`storecost.within_storage_budget` — the N2 window priced exactly as the terrain window was.

GRADE. The three record laws (closed forms, round-trips, exhaustive corruption refuses), the
restored == never-died equality, the through-death rollback convergence, the checked-evidence
refuse (integral-but-inconsistent window), the disorder and substitution refuses, horizon/conflict/
duplicate/K-invariance preservation, the surviving defect anchor, the priced window, and
determinism are MEASURED (exact, reproducible, a defect diverges). DECLARED: the restore path is
O(history) — replay from the world start with the window as evidence; an O(window) suffix-restore
that reproduces the FULL witness chain needs a durable frame chain (a future rung, stated not
begun); WHO may save/restore is `authinput` territory; eviction/cadence policy is operational (K
and H are parameters, proven non-semantic). `does_not_show`: cross-peer window exchange (each peer
saves its OWN window; a shared store is transport territory); wall-clock (`bench.py`);
cross-placement (Python reference only — URDRRBS1 joins the placement frontier)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRRBS1"
LOG_MAGIC = b"URDRRBS1LOG"
WIN_MAGIC = b"URDRRBS1WIN"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
for _d in (_HERE, _os.path.join(_HERE, "..", "physics"), _os.path.join(_HERE, "..", "terrain")):
    if _d not in _sys.path:
        _sys.path.insert(0, _d)
import lockstep as _L                                           # the N1 oracle (frozen)
import rollback as _R                                           # N2, consumed never edited

DIGEST_BYTES = 32


class RollstoreError(Exception):
    def __init__(self, message):
        super().__init__(f"ROLLSTORE-REFUSE: {message}")
        self.code = "ROLLSTORE-REFUSE"


def _i64(v, nm):
    if not (type(v) is int and -(1 << 63) <= v < (1 << 63)):
        raise RollstoreError(f"{nm} {v!r} does not fit signed int64 — refuse, never truncate")
    return (v & ((1 << 64) - 1)).to_bytes(8, "big")


def _u32(v, nm):
    if not (type(v) is int and 0 <= v < (1 << 32)):
        raise RollstoreError(f"{nm} must be uint32, got {v!r}")
    return v.to_bytes(4, "big")


def _verified(buf, magic, name):
    if not (type(buf) is bytes or type(buf) is bytearray):
        raise RollstoreError(f"a {name} must be bytes")
    buf = bytes(buf)
    if len(buf) < len(magic) + DIGEST_BYTES:
        raise RollstoreError(f"a {name} of {len(buf)} bytes is shorter than its envelope")
    if buf[:len(magic)] != magic:
        raise RollstoreError(f"bad magic — not a {name}")
    if hashlib.sha256(buf[:-DIGEST_BYTES]).digest() != buf[-DIGEST_BYTES:]:
        raise RollstoreError(f"{name} digest mismatch — tampered, truncated, or corrupted; "
                             f"refused, not repaired")
    return buf


def address_of(buf):
    """One digest, three roles: the trailing digest hex is integrity check, content address, and
    on-disk filename."""
    return bytes(buf)[-DIGEST_BYTES:].hex()


# ---- the snapshot record -----------------------------------------------------------------
def snapshot_bytes(n):
    """52 + 32·n — the closed form the gate checks EQUAL to real records."""
    return len(MAGIC) + 8 + 4 + 32 * n + DIGEST_BYTES


def snapshot_record(tick, pos, vel):
    """MAGIC | tick | n | (pos.x pos.y vel.x vel.y, signed int64 Q32.32)* | SHA-256."""
    n = len(pos)
    if len(vel) != n:
        raise RollstoreError(f"pos has {n} bodies but vel has {len(vel)}")
    pre = bytearray(MAGIC) + _i64(tick, "tick") + _u32(n, "n")
    for i in range(n):
        pre += _i64(pos[i][0], "pos.x") + _i64(pos[i][1], "pos.y")
        pre += _i64(vel[i][0], "vel.x") + _i64(vel[i][1], "vel.y")
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def restore_snapshot(buf):
    """(tick, pos, vel) BIT-FOR-BIT or a typed refuse — signed decoding, exact structural length."""
    buf = _verified(buf, MAGIC, "URDRRBS1 snapshot record")
    off = len(MAGIC)
    tick = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
    n = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if len(buf) != snapshot_bytes(n):
        raise RollstoreError(f"snapshot length {len(buf)} does not match its n={n}")
    pos, vel = [], []
    for _i in range(n):
        px = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        py = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        vx = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        vy = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        pos.append([px, py])
        vel.append([vx, vy])
    return tick, pos, vel


# ---- the event-log record ----------------------------------------------------------------
def log_bytes(m):
    """47 + 48·m."""
    return len(LOG_MAGIC) + 4 + 48 * m + DIGEST_BYTES


def log_record(events):
    """LOG_MAGIC | count | (tick peer seq body dvx dvy, each signed int64)* | SHA-256 — the
    transcript, canonically ordered by the caller (the record preserves what it is given)."""
    events = tuple(tuple(int(x) for x in e) for e in events)
    for e in events:
        if len(e) != 6:
            raise RollstoreError(f"an event must have 6 fields, got {e!r}")
    pre = bytearray(LOG_MAGIC) + _u32(len(events), "count")
    for e in events:
        for k, v in enumerate(e):
            pre += _i64(v, f"event[{k}]")
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def restore_log(buf):
    """The events BIT-FOR-BIT or a typed refuse."""
    buf = _verified(buf, LOG_MAGIC, "URDRRBS1 log record")
    off = len(LOG_MAGIC)
    m = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if len(buf) != log_bytes(m):
        raise RollstoreError(f"log length {len(buf)} does not match its count {m}")
    out = []
    for _i in range(m):
        e = []
        for _k in range(6):
            e.append(int.from_bytes(buf[off:off + 8], "big", signed=True)); off += 8
        out.append(tuple(e))
    return tuple(out)


# ---- the window manifest -----------------------------------------------------------------
def window_bytes(s):
    """95 + 40·s."""
    return len(WIN_MAGIC) + 8 + 4 + 4 + 4 + 40 * s + DIGEST_BYTES + DIGEST_BYTES


def window_manifest(head, K, H, entries, log_addr):
    """WIN_MAGIC | head | K | H | count | (tick | snapshot digest)* | log digest | SHA-256. The
    entries bind the retained window IN ORDER — ascending ticks; a disordered list refuses at
    restore, never re-sorts."""
    pre = bytearray(WIN_MAGIC) + _i64(head, "head") + _u32(K, "K") + _u32(H, "H")
    pre += _u32(len(entries), "count")
    for (tick, dig) in entries:
        pre += _i64(tick, "tick") + bytes.fromhex(dig)
    pre += bytes.fromhex(log_addr)
    return bytes(pre) + hashlib.sha256(bytes(pre)).digest()


def parse_window(buf):
    """(head, K, H, ((tick, digest-hex), ...), log-address-hex) or a typed refuse."""
    buf = _verified(buf, WIN_MAGIC, "URDRRBS1 window manifest")
    off = len(WIN_MAGIC)
    head = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
    K = int.from_bytes(buf[off:off + 4], "big"); off += 4
    H = int.from_bytes(buf[off:off + 4], "big"); off += 4
    s = int.from_bytes(buf[off:off + 4], "big"); off += 4
    if len(buf) != window_bytes(s):
        raise RollstoreError(f"manifest length {len(buf)} does not match its count {s}")
    entries = []
    for _i in range(s):
        tick = int.from_bytes(buf[off:off + 8], "big", signed=True); off += 8
        entries.append((tick, buf[off:off + DIGEST_BYTES].hex())); off += DIGEST_BYTES
    log_addr = buf[off:off + DIGEST_BYTES].hex()
    return head, K, H, tuple(entries), log_addr


# ---- save / restore ----------------------------------------------------------------------
def save_peer(dirpath, peer):
    """The peer's window made durable: every snapshot, the event log, and the binding manifest,
    each under its content address. Returns the manifest address. Deterministic — the same peer
    mints the same addresses."""
    entries = []
    for (tick, pos, vel) in peer.snapshots:
        rec = snapshot_record(tick, pos, vel)
        with open(_os.path.join(dirpath, address_of(rec)), "wb") as fh:
            fh.write(rec)
        entries.append((tick, address_of(rec)))
    lg = log_record(sorted(peer.known.values()))
    with open(_os.path.join(dirpath, address_of(lg)), "wb") as fh:
        fh.write(lg)
    man = window_manifest(peer.head, peer.K, peer.H, entries, address_of(lg))
    with open(_os.path.join(dirpath, address_of(man)), "wb") as fh:
        fh.write(man)
    return address_of(man)


def _load(dirpath, addr):
    try:
        with open(_os.path.join(dirpath, addr), "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise RollstoreError(f"object {addr[:12]}… missing from the store: {exc}")


def restore_peer(dirpath, man_addr, w):
    """THE SOURCE LAW: replay the event log from the world's start, then require the SAVED window
    to equal the replay's regenerated one bit-for-bit — tick order, states, count, head. The log
    is the rewindable source; the window is checked evidence. Every object must hash to its
    filename (substitution refuses). Returns a peer equal to the never-died one in every
    observable."""
    man = _load(dirpath, man_addr)
    if address_of(man) != man_addr:
        raise RollstoreError(f"substitution — the manifest at {man_addr[:12]}… addresses "
                             f"{address_of(man)[:12]}…; the address IS the identity")
    head, K, H, entries, log_addr = parse_window(man)
    ticks = [t for (t, _d) in entries]
    if ticks != sorted(ticks) or len(set(ticks)) != len(ticks):
        raise RollstoreError(f"the manifest's snapshot ticks {ticks} are not strictly ascending — "
                             f"a disordered window is refused, never re-sorted")
    lg = _load(dirpath, log_addr)
    if address_of(lg) != log_addr:
        raise RollstoreError(f"substitution — the log at {log_addr[:12]}… addresses "
                             f"{address_of(lg)[:12]}…")
    events = restore_log(lg)
    saved = []
    for (tick, dig) in entries:
        rec = _load(dirpath, dig)
        if address_of(rec) != dig:
            raise RollstoreError(f"substitution — the snapshot at {dig[:12]}… addresses "
                                 f"{address_of(rec)[:12]}…")
        s_tick, pos, vel = restore_snapshot(rec)
        if s_tick != tick:
            raise RollstoreError(f"the manifest claims tick {tick} but the record says {s_tick}")
        saved.append((tick, pos, vel))
    peer = _R.Peer(w, K=K, H=H)
    for e in events:
        peer.known[(e[1], e[2])] = e
    peer.advance(head)
    if peer.head != head:
        raise RollstoreError(f"the replay reached tick {peer.head}, the manifest claims {head} — "
                             f"an inconsistent head is refused")
    if len(peer.snapshots) != len(saved):
        raise RollstoreError(f"the replay retains {len(peer.snapshots)} snapshots, the saved "
                             f"window holds {len(saved)} — an inconsistent window is refused")
    for (got, want) in zip(peer.snapshots, saved):
        if (got[0], got[1], got[2]) != (want[0], want[1], want[2]):
            raise RollstoreError(f"the saved snapshot at tick {want[0]} disagrees with the replay "
                                 f"— a crafted-but-digested window is refused, not trusted "
                                 f"(integrity is not truth)")
    return peer


def window_cost_bytes(n, s, m):
    """The window's EXACT durable cost: s snapshot records + the log + the manifest — the N2
    window priced under the same closed-form discipline as the terrain window."""
    return s * snapshot_bytes(n) + log_bytes(m) + window_bytes(s)


def rollstore_digest(name, trace_hex, man_hex, K, nbytes, verdict):
    """URDRRBS1 canon — SHA-256(MAGIC | name | trace | manifest | K | bytes | verdict)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}|t:{trace_hex}|w:{man_hex}|k:{K}|n:{nbytes}|v:{verdict}".encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
def _late_sched(w, log, delay=3):
    return sorted(((min(e[0] + delay, w["T"] - 1), i, e) for i, e in enumerate(log)),
                  key=lambda x: (x[0], x[1]))


def _drive(peer, sched, upto, idx=0):
    for t in range(peer.head, upto):
        while idx < len(sched) and sched[idx][0] <= t:
            peer.deliver(sched[idx][2])
            idx += 1
        peer.advance(t + 1)
    return idx


def _scene_mirror_window():
    """Save mid-run, restore, finish on both peers: identical traces, equal to the canonical N1
    timeline — restored == never-died in every observable."""
    import tempfile
    w = _L.world()
    log = _L.sample_log()
    sched = _late_sched(w, log)
    peer = _R.Peer(w, K=4, H=8)
    idx = _drive(peer, sched, 60)
    with tempfile.TemporaryDirectory(prefix="urdr_rbs_scene_") as td:
        man_addr = save_peer(td, peer)
        revived = restore_peer(td, man_addr, w)
    _drive(peer, sched, w["T"], idx)
    _drive(revived, sched, w["T"], idx)
    canon = _L.trace_digest(_L.simulate(w, log)[0])
    ok = revived.trace() == peer.trace() == canon
    nbytes = window_cost_bytes(w["n"], 8, len(peer.known))
    return canon, man_addr, 4, nbytes, ("ADMIT" if ok else "ROLLSTORE-REFUSE")


def _scene_phoenix_peer():
    """The rollback that crosses death: one late event held back past the save; the restored peer
    receives it, rewinds from a restored-and-verified snapshot, and converges to canonical."""
    import tempfile
    w = _L.world()
    log = _L.sample_log()
    sched = _late_sched(w, log)
    held = sched[-1]
    peer = _R.Peer(w, K=4, H=64)
    for (_at, _i, e) in sched[:-1]:
        peer.deliver(e)
    peer.advance(w["T"])
    with tempfile.TemporaryDirectory(prefix="urdr_rbs_scene_") as td:
        man_addr = save_peer(td, peer)
        revived = restore_peer(td, man_addr, w)
    revived.deliver(held[2])
    revived.advance(w["T"])
    canon = _L.trace_digest(_L.simulate(w, log)[0])
    ok = revived.trace() == canon
    return canon, man_addr, 4, window_cost_bytes(w["n"], len(peer.snapshots), len(peer.known)), \
        ("ADMIT" if ok else "ROLLSTORE-REFUSE")


def _scene_crooked_window():
    """The checked-evidence law: a crafted-but-digested snapshot (integral bytes, wrong physics)
    refuses at restore — the window is evidence, never trusted state."""
    import tempfile
    w = _L.world()
    sched = _late_sched(w, _L.sample_log())
    peer = _R.Peer(w, K=4, H=8)
    _drive(peer, sched, 60)
    refused = False
    with tempfile.TemporaryDirectory(prefix="urdr_rbs_scene_") as td:
        man_addr = save_peer(td, peer)
        head, K, H, entries, la = parse_window(_load(td, man_addr))
        tick, pos, vel = peer.snapshots[-1]
        forged = snapshot_record(tick, pos, [[v[0], v[1] + 1] for v in vel])
        open(_os.path.join(td, address_of(forged)), "wb").write(forged)
        victim = entries[-1][1]
        man2 = window_manifest(head, K, H,
                               [(t, (address_of(forged) if d == victim else d))
                                for (t, d) in entries], la)
        open(_os.path.join(td, address_of(man2)), "wb").write(man2)
        try:
            restore_peer(td, address_of(man2), w)
        except RollstoreError:
            refused = True
    ok = refused
    return "0" * 64, "0" * 64, 4, 0, ("ROLLSTORE-REFUSE" if ok else "ADMIT")


def _scene_priced_window():
    """K-invariance through the restore + the priced window: K=4 and K=8 both restore and finish
    to ONE trace; the cost closed form equals real bytes under the budget law."""
    import tempfile
    import storecost as _SC
    w = _L.world()
    log = _L.sample_log()
    sched = _late_sched(w, log)
    traces = set()
    nbytes = 0
    for K in (4, 8):
        peer = _R.Peer(w, K=K, H=64)
        idx = _drive(peer, sched, 60)
        with tempfile.TemporaryDirectory(prefix="urdr_rbs_scene_") as td:
            man_addr = save_peer(td, peer)
            real = sum(_os.path.getsize(_os.path.join(td, f)) for f in _os.listdir(td))
            revived = restore_peer(td, man_addr, w)
        want = window_cost_bytes(w["n"], len(peer.snapshots), len(peer.known))
        if real != want or not _SC.within_storage_budget(want, 10 ** 6):
            traces.add("COST-DRIFT")
        nbytes = max(nbytes, want)
        _drive(revived, sched, w["T"], idx)
        traces.add(revived.trace())
    canon = _L.trace_digest(_L.simulate(w, log)[0])
    ok = traces == {canon}
    return canon, "0" * 64, 48, nbytes, ("ADMIT" if ok else "ROLLSTORE-REFUSE")


_SCENES = {"mirror_window": _scene_mirror_window, "phoenix_peer": _scene_phoenix_peer,
           "crooked_window": _scene_crooked_window, "priced_window": _scene_priced_window}
SCENES = ("mirror_window", "phoenix_peer", "crooked_window", "priced_window")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    canon, man, K, nbytes, verdict = scene_case(name)
    return rollstore_digest(name, canon, man, K, nbytes, verdict)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_rollstore.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise RollstoreError(f"no golden named {name!r}")


if __name__ == "__main__":
    # THE SUCCESSOR: python rollstore.py <store_dir> <manifest_addr> <tick> <peer> <seq> <body>
    # <dvx> <dvy> — restore from the directory alone (the arena world is the static authority, by
    # construction), deliver the ONE post-death late event, run to the end, print the trace digest.
    if len(_sys.argv) != 9:
        print("usage: rollstore.py <store_dir> <manifest_addr> <tick> <peer> <seq> <body> <dvx> <dvy>")
        raise SystemExit(2)
    _w = _L.world()
    try:
        _peer = restore_peer(_sys.argv[1], _sys.argv[2], _w)
        _peer.deliver(tuple(int(x) for x in _sys.argv[3:9]))
        _peer.advance(_w["T"])
        print(_peer.trace())
    except (RollstoreError, _R.RollbackError) as exc:
        print(str(exc))
