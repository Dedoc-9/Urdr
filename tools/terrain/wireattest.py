# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""wireattest — THE REALITY ATTESTATION (T3.51, W5, URDRWAT1): the wire over real sockets,
judged by the same laws after the fact. Sockets and wall-clock are NONDETERMINISTIC, so by the
house's own law they may not live inside the gate; what crosses the boundary instead is a
SELF-DIGESTED TRACE — reality recorded once, re-verified forever.

THE SPLIT. The RUN (off-gate, `python wireattest.py --run` on a NAMED host): an authority
process streams the 12-edit log as raw 104-byte UDP datagrams through a REAL chaos relay
process (seeded duplication, reordering by delayed forwarding, corrupt-duplicate malice, and —
in the tempest — real drops) to REAL client subprocesses running the UNMODIFIED wire loom
(refused deliveries requeued to fixpoint); a loss-stalled client repairs by a VERIFIED FETCH
over a TCP side-channel (the driftgaze law over reality). Every attempt, outcome, fetch, and
witness is recorded; the trace is sealed with its own SHA-256. The CHECK (in-gate, pure): the
checker REPLAYS every recorded delivery through `wire.client_admit` and every recorded fetch
through the acquisition law against its own replica — reality's claims (outcomes, witnesses,
addresses) must MATCH what the law replays, or the attestation is UNLAWFUL. The gate certifies
the laws; the attestation certifies reality met them; the trace is where they shake hands, and
neither pretends to be the other.

THE NAMED-HOST LAW, MECHANIZED (bench_protocol's rule made structural): a trace with an empty
or missing host line REFUSES — an unnamed MEASURED is no MEASURED at all. The pinned trace
lives at spec/attest/wire_attest.txt; the gate re-verifies it on every run, on every host,
byte-deterministically, and names its host in the gate output.

THE LAWS THE CHECKER ENFORCES: the update log itself must replay lawfully on the authority
side (authwit recomputed, compared); every recorded outcome must equal the law's replayed
outcome (a forged admission refuses — reality may not overrule the law); every recorded
client witness must equal the replayed replica (silent drift refuses); outcomes are typed
ADMIT / WIRE-REFUSE only; corrupt deliveries (recorded inline as `deliverx`) must refuse in
replay and may never claim admission; a recorded fetch must land the authority's OWN head
address for that region (repair is verified or it is nothing); and convergence: a client with
zero stalls must equal the authority's witness bit-for-bit, while a stalled client's witness
is exactly what the replayed prefix law yields (the storm's law over reality).

GRADE. The checker's laws (all of the above, each with a refusing synthetic forge), trace
integrity (any byte flip refuses), the named-host rule, determinism of the check, and the
verdict-bound report digest are MEASURED. The pinned trace's verdict is MEASURED (named host)
in bench_protocol's sense — the trace IS the host log. DECLARED, honestly: the run exercises
loopback UDP on one machine (real sockets, real processes, real kernel buffering — but not
cross-machine networks, NAT, or the open internet); wall-clock latency is NOT claimed (that is
`bench.py` §3's job); the chaos relay's misbehavior is seeded and bounded (real networks are
worse in ways no relay exhausts — the storm's declaration, inherited). `does_not_show`:
throughput/bandwidth; the depicting client; cross-placement (URDRWAT1 joins the frontier —
the phase seals with this rung, so placement batch #3 now falls due)."""
import hashlib
import os as _os
import socket as _socket
import subprocess as _subprocess
import sys as _sys
import tempfile as _tempfile

MAGIC = b"URDRWAT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # noqa: E402
import rannull as _RN                                           # noqa: E402
import wire as _W                                               # noqa: E402

_FIN = b"URDRWAT1FIN|"
_ALL4 = frozenset({(0, 0), (0, 1), (1, 0), (1, 1)})
_EDITS = ((5, 8, 1000), (2, 2, 11), (12, 4, 22), (6, 8, 50), (12, 12, 33), (3, 2, -4),
          (13, 4, 7), (5, 8, -30), (12, 12, 9), (2, 3, 5), (13, 5, -2), (6, 9, 12))
_OUTCOMES = ("ADMIT", "WIRE-REFUSE")


class AttestError(Exception):
    def __init__(self, message):
        super().__init__(f"ATTEST-REFUSE: {message}")
        self.code = "ATTEST-REFUSE"


def _draw(seed, *idx):
    """One deterministic draw from a SHA-256 digest stream (the storm's discipline)."""
    hh = hashlib.sha256(MAGIC + seed + ("/".join(str(i) for i in idx)).encode())
    return int.from_bytes(hh.digest()[:4], "big")


# ---- the fixed world and its update log --------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def authority_log():
    """The 12-edit chained log on blank/C=8 plus the final manifest, store, and witness."""
    fld = _blank()
    man = _CK.field_manifest(fld, 8)
    store = {_CK.address(r): r for r in _CK.cut(fld, 8).values()}
    updates = []
    for (x, y, dh) in _EDITS:
        _w, _h, _c, grid = _CK.parse_manifest(man)
        chunk = store[grid[(x // 8, y // 8)]]
        kx, ky, cells = _CK.restore_chunk(chunk)
        old = cells[y - ky * 8][x - kx * 8]
        rec = _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh)
        new_chunk = _RN.shard_apply(chunk, rec)
        man = _RN.reunify(man, (new_chunk,))
        store[_CK.address(new_chunk)] = new_chunk
        updates.append(rec)
    _w, _h, _c, grid = _CK.parse_manifest(man)
    mirror = {"c": 8, "chunks": {k: store[grid[k]] for k in sorted(grid)}}
    return tuple(updates), man, store, _W.replica_witness(mirror)


# ---- the trace object --------------------------------------------------------------------
def seal_trace(lines):
    """Lines -> one LF-joined text with a trailing self-digest line."""
    body = "\n".join(lines)
    dig = hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest()
    return body + "\ndigest " + dig + "\n"


def parse_trace(text):
    """Verify the self-digest and return the body lines. Any byte flip refuses."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise AttestError("a trace must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest() != claimed:
        raise AttestError("the trace does not hash to its own digest — tampered or truncated; "
                          "a record is re-made, never edited")
    if lines[0] != "URDRWAT1 v1":
        raise AttestError("not a URDRWAT1 v1 trace")
    return lines[:-1]


# ---- the checker (pure — the law replayed over reality's record) -------------------------
def check_trace(text):
    """The attestation verdict: replay every recorded delivery and fetch through the
    UNMODIFIED laws; reality's claims must match. Returns the report dict; every violation
    is a typed ATTEST-REFUSE."""
    lines = parse_trace(text)
    if len(lines) < 2 or not lines[1].startswith("host ") or not lines[1][5:].strip():
        raise AttestError("the attestation names no host — an unnamed MEASURED is no "
                          "MEASURED at all (bench_protocol's law, mechanized)")
    host = lines[1][5:].strip()
    updates, man, store, authwit = authority_log()
    upd_hex = {i: rec.hex() for i, rec in enumerate(updates)}
    _w, _h, _c, grid = _CK.parse_manifest(man)
    fld = _blank()
    scenarios = []
    clients = {}                                 # (scenario, cid) -> replica
    admitted = {}                                # (scenario, cid) -> set of update indices
    fetched = {}                                 # (scenario, cid) -> set of regions
    wits = {}                                    # (scenario, cid) -> recorded witness
    seen_authwit = {}
    stats = {"deliveries": 0, "refusals": 0, "malice_refused": 0, "fetches": 0}
    scen = None

    def _key(cid):
        if scen is None:
            raise AttestError("a record line arrived before any scenario line")
        k = (scen, cid)
        if k not in clients:
            clients[k] = _W.subscribe(fld, 8, _ALL4)
            admitted[k], fetched[k] = set(), set()
        return k

    for ln in lines[2:]:
        parts = ln.split()
        if not parts:
            continue
        tag = parts[0]
        if tag == "scenario":
            scen = parts[1]
            scenarios.append(scen)
        elif tag == "world":
            if parts[1:] != ["blank", "8"]:
                raise AttestError(f"unknown world {parts[1:]} — the corpus is blank/C=8")
        elif tag == "update":
            i, hx = int(parts[1]), parts[2]
            if upd_hex.get(i) != hx:
                raise AttestError(f"update {i} does not match the lawful authority log — "
                                  f"the recorded log must replay under the authority's laws")
        elif tag == "authwit":
            if parts[1] != authwit:
                raise AttestError("the recorded authority witness does not equal the "
                                  "replayed authority head")
            seen_authwit[scen] = True
        elif tag == "client":
            _key(int(parts[1]))
        elif tag == "deliver":
            cid, ref, outcome = int(parts[1]), parts[2], parts[3]
            if outcome not in _OUTCOMES:
                raise AttestError(f"outcome {outcome!r} is untyped — refusals are typed or "
                                  f"they are nothing")
            if not ref.startswith("u"):
                raise AttestError(f"delivery reference {ref!r} is not an update index")
            i = int(ref[1:])
            if i not in upd_hex:
                raise AttestError(f"delivery references unknown update {i}")
            k = _key(cid)
            stats["deliveries"] += 1
            try:
                new_rep = _W.client_admit(clients[k], updates[i])
                law = "ADMIT"
            except _W.WireError:
                law = "WIRE-REFUSE"
            if law != outcome:
                raise AttestError(f"client {cid} recorded {outcome} for update {i} but the "
                                  f"law replays {law} — reality may not overrule the law")
            if law == "ADMIT":
                if i in admitted[k]:
                    raise AttestError(f"update {i} admitted twice on client {cid} — "
                                      f"at-most-once is the wire's theorem")
                admitted[k].add(i)
                clients[k] = new_rep
            else:
                stats["refusals"] += 1
        elif tag == "deliverx":
            cid, hx, outcome = int(parts[1]), parts[2], parts[3]
            if outcome != "WIRE-REFUSE":
                raise AttestError("a corrupt delivery may never claim admission")
            k = _key(cid)
            stats["deliveries"] += 1
            before = _W.replica_witness(clients[k])
            try:
                _W.client_admit(clients[k], bytes.fromhex(hx))
                raise AttestError(f"corrupt delivery on client {cid} ADMITS in replay — "
                                  f"the recorded malice was not malice")
            except _W.WireError:
                pass
            if _W.replica_witness(clients[k]) != before:
                raise AttestError("a refusal moved the replica — refuse purity broken")
            stats["refusals"] += 1
            stats["malice_refused"] += 1
        elif tag == "fetch":
            cid, kx, ky, addr = int(parts[1]), int(parts[2]), int(parts[3]), parts[4]
            k = _key(cid)
            key = (kx, ky)
            if key not in grid:
                raise AttestError(f"fetch names region {key} outside the grid")
            if addr != grid[key]:
                raise AttestError(f"fetch for region {key} landed {addr[:12]}… but the "
                                  f"authority's head is {grid[key][:12]}… — repair is "
                                  f"verified or it is nothing")
            held = dict(clients[k]["chunks"])
            held[key] = store[addr]
            clients[k] = {"c": 8, "chunks": held}
            fetched[k].add(key)
            stats["fetches"] += 1
        elif tag == "clientwit":
            cid = int(parts[1])
            k = _key(cid)
            if parts[2] != _W.replica_witness(clients[k]):
                raise AttestError(f"client {cid}'s recorded witness does not equal the "
                                  f"replayed replica — silent drift, the wire's one poison")
            wits[k] = parts[2]
        else:
            raise AttestError(f"unknown trace line {tag!r}")
    if not scenarios:
        raise AttestError("the trace records no scenario")
    stalls = 0
    for k, rep in clients.items():
        if k not in wits:
            raise AttestError(f"client {k[1]} in scenario {k[0]!r} records no witness")
        missing = set(range(len(updates))) - admitted[k]
        stalls += len(missing)
        if not missing and wits[k] != authwit:
            raise AttestError(f"client {k[1]} admitted everything yet does not equal the "
                              f"authority — convergence broken")
    return {"verdict": "LAWFUL", "host": host, "scenarios": tuple(scenarios),
            "clients": len(clients), "updates": len(updates),
            "deliveries": stats["deliveries"], "refusals": stats["refusals"],
            "malice_refused": stats["malice_refused"], "stalls": stalls,
            "fetches": stats["fetches"]}


def report_digest(rep):
    """URDRWAT1 canon over the report — SHA-256(MAGIC | sorted key:value)."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for key in sorted(rep):
        hh.update(f"|{key}:{rep[key]}".encode())
    return hh.hexdigest()


# ---- the honest simulator (shared by the synthetic fixtures) -----------------------------
def _simulate(plans, host):
    """Execute per-client delivery plans through the REAL laws, recording what the law did.
    plans: {cid: [("u", i) | ("x", i, flip_off) | ("fetch", (kx, ky))]}."""
    updates, man, store, authwit = authority_log()
    _w, _h, _c, grid = _CK.parse_manifest(man)
    fld = _blank()
    lines = ["URDRWAT1 v1", f"host {host}", "scenario " + ("tempest" if any(
        step[0] == "fetch" for plan in plans.values() for step in plan) else "gale"),
        "world blank 8"]
    for i, rec in enumerate(updates):
        lines.append(f"update {i} {rec.hex()}")
    lines.append(f"authwit {authwit}")
    for cid in sorted(plans):
        lines.append(f"client {cid}")
        rep = _W.subscribe(fld, 8, _ALL4)
        for step in plans[cid]:
            if step[0] == "u":
                i = step[1]
                try:
                    rep = _W.client_admit(rep, updates[i])
                    lines.append(f"deliver {cid} u{i} ADMIT")
                except _W.WireError:
                    lines.append(f"deliver {cid} u{i} WIRE-REFUSE")
            elif step[0] == "x":
                bad = bytearray(updates[step[1]])
                bad[step[2]] ^= 0x01
                lines.append(f"deliverx {cid} {bytes(bad).hex()} WIRE-REFUSE")
            elif step[0] == "fetch":
                key = step[1]
                held = dict(rep["chunks"])
                held[key] = store[grid[key]]
                rep = {"c": 8, "chunks": held}
                lines.append(f"fetch {cid} {key[0]} {key[1]} {grid[key]}")
            elif step[0] == "badfetch":
                key, wrong = step[1], step[2]
                held = dict(rep["chunks"])
                held[key] = store[grid[wrong]]           # the WRONG region's chunk,
                rep = {"c": 8, "chunks": held}           # witness recorded CONSISTENTLY —
                lines.append(f"fetch {cid} {key[0]} {key[1]} {grid[wrong]}")
        lines.append(f"clientwit {cid} {_W.replica_witness(rep)}")
    return lines


def _gale_plan(cid):
    """A deterministic chaotic order: every update delivered, with reorder-refuse-retry,
    duplicates, and two corrupt-duplicate malice probes."""
    seed = b"gale-%d" % cid
    n = 12
    order = list(range(n))
    for i in range(n - 1, 0, -1):                # seeded shuffle
        j = _draw(seed, i) % (i + 1)
        order[i], order[j] = order[j], order[i]
    plan, queue = [], list(order)
    while queue:                                 # the loom: passes to fixpoint
        nxt = []
        for i in queue:
            plan.append(("u", i))
            nxt.append(i)                        # provisional; replay decides
        # the simulator records real outcomes; refused ones are re-tried by re-planning:
        queue = _replay_refused(plan)
        if len(queue) == len(nxt):
            break
    for i in (2, 9):                             # duplicates of already-passed updates
        plan.append(("u", i))
    plan.insert(5, ("x", 4, 60))                 # corrupt duplicates woven in
    plan.append(("x", 11, 50))
    return plan


def _replay_refused(plan):
    """Which planned u-deliveries would still be refused if the plan ran now — used to
    build a fixpoint loom plan deterministically."""
    updates, _man, _store, _authwit = authority_log()
    rep = _W.subscribe(_blank(), 8, _ALL4)
    admitted = set()
    refused_last = []
    for step in plan:
        if step[0] != "u":
            continue
        i = step[1]
        try:
            rep = _W.client_admit(rep, updates[i])
            admitted.add(i)
        except _W.WireError:
            pass
    refused_last = [i for i in range(len(updates)) if i not in admitted]
    return refused_last


def synth_trace(kind, host="synthetic-host (fixture, not a MEASURED claim)", forge=None):
    """Deterministic synthetic traces for the falsifiers and the gate's law rows. kind:
    'gale' (chaotic convergent + malice) or 'tempest' (loss, stall, verified repair).
    forge: a named violation woven in (each must REFUSE — except 'norepair', which is the
    lawful stalled variant)."""
    if kind == "gale":
        plans = {0: _gale_plan(0), 1: _gale_plan(1)}
    elif kind == "tempest":
        lost = {3}                               # region (0,1)'s second update, dropped
        seq0 = [("u", i) for i in range(12) if i not in lost]
        if forge == "fetchaddr":
            seq0.append(("badfetch", (0, 1), (1, 1)))
        elif forge not in ("norepair", "norepair_lie"):
            seq0.append(("fetch", (0, 1)))
        plans = {0: seq0, 1: [("u", i) for i in range(12)]}
    else:
        raise AttestError(f"unknown synthetic kind {kind!r}")
    lines = _simulate(plans, host)
    if forge == "admission":
        seen = set()                             # pick a REORDER-early refusal (its update
        idx = None                               # not yet admitted) — the one lie only the
        for i, ln in enumerate(lines):           # outcome law can catch, so the forge tests
            p = ln.split()                       # THAT law and not at-most-once behind it
            if p[0] == "deliver" and p[1] == "0":
                u = int(p[2][1:])
                if p[3] == "ADMIT":
                    seen.add(u)
                elif u not in seen:
                    idx = i
                    break
        lines[idx] = lines[idx].replace("WIRE-REFUSE", "ADMIT")
    elif forge == "witness":
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("clientwit 0 "))
        wit = lines[idx].split()[2]
        flipped = ("0" if wit[0] != "0" else "1") + wit[1:]
        lines[idx] = f"clientwit 0 {flipped}"
    elif forge == "double":
        src = next(ln for ln in lines if ln.startswith("deliver 0 ") and ln.endswith("ADMIT"))
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("clientwit 0 "))
        lines.insert(idx, src)
    elif forge == "untyped":
        idx = next(i for i, ln in enumerate(lines)
                   if ln.startswith("deliver ") and ln.endswith("WIRE-REFUSE"))
        lines[idx] = lines[idx].replace("WIRE-REFUSE", "SOFT-FAIL")
    elif forge == "corrupt_admit":
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("deliverx "))
        lines[idx] = lines[idx].replace("WIRE-REFUSE", "ADMIT")
    elif forge == "norepair_lie":
        aw = next(ln for ln in lines if ln.startswith("authwit ")).split()[1]
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("clientwit 0 "))
        lines[idx] = f"clientwit 0 {aw}"
    elif forge == "fetchaddr":
        pass                                     # woven at plan level (consistent witness)
    elif forge not in (None, "norepair"):
        raise AttestError(f"unknown forge {forge!r}")
    return seal_trace(lines)


# ---- the off-gate runner (real processes, real UDP, a real chaos relay) ------------------
def _client_main(argv):
    """Child process: the wire loom over a real UDP socket; a stall repairs by verified
    TCP fetch; every attempt logged."""
    port, tcp_port, log_path, do_fetch = (int(argv[0]), int(argv[1]), argv[2],
                                          argv[3] == "1")
    fld = _blank()
    rep = _W.subscribe(fld, 8, _ALL4)
    log = []
    sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))
    sock.settimeout(15.0)
    queue, fin_man = [], None

    def attempt(payload):
        nonlocal rep
        try:
            rep = _W.client_admit(rep, payload)
            log.append(("P", payload.hex(), "ADMIT"))
            return True
        except _W.WireError:
            log.append(("P", payload.hex(), "WIRE-REFUSE"))
            return False

    def loom():
        progress = True
        while progress and queue:
            progress = False
            for payload in list(queue):
                before = _W.replica_witness(rep)
                if attempt(payload):
                    queue.remove(payload)
                    progress = True
                elif _W.replica_witness(rep) != before:  # pragma: no cover - law guard
                    raise AttestError("refusal moved the replica")

    try:
        while fin_man is None:
            data, _addr = sock.recvfrom(65535)
            if data.startswith(_FIN):
                fin_man = data[len(_FIN):]
            else:
                if not attempt(data):
                    queue.append(data)
                loom()
    except _socket.timeout:
        pass
    loom()
    if fin_man is not None and do_fetch:
        try:
            _w, _h, _c, grid = _CK.parse_manifest(fin_man)
            for key in sorted(grid):
                if _CK.address(rep["chunks"][key]) != grid[key]:
                    tc = _socket.create_connection(("127.0.0.1", tcp_port), timeout=10)
                    tc.sendall(b"FETCH %d %d\n" % key)
                    blob = b""
                    while len(blob) < 8:
                        blob += tc.recv(65535)
                    total = int.from_bytes(blob[:8], "big")
                    while len(blob) < 8 + total:
                        blob += tc.recv(65535)
                    tc.close()
                    man_len = int.from_bytes(blob[8:16], "big")
                    man = blob[16:16 + man_len]
                    chunk = blob[16 + man_len:8 + total]
                    _w2, _h2, _c2, g2 = _CK.parse_manifest(man)
                    if _CK.address(chunk) != g2[key]:            # verified or nothing
                        continue
                    kx, ky, _cells = _CK.restore_chunk(chunk)
                    if (kx, ky) != key:
                        continue
                    held = dict(rep["chunks"])
                    held[key] = chunk
                    rep = {"c": 8, "chunks": held}
                    log.append(("F", f"{key[0]} {key[1]} {g2[key]}", "OK"))
                    loom()
        except Exception:
            pass
    log.append(("W", _W.replica_witness(rep), ""))
    with open(log_path, "w", encoding="utf-8", newline="\n") as fh:
        for (tag, a, b) in log:
            fh.write(f"{tag} {a} {b}".rstrip() + "\n")


def _relay_main(argv):
    """Child process: the real chaos relay — forwards each datagram to every client port
    with seeded duplication and delayed (reordering) forwarding; configured indices are
    DROPPED for client 0 (the tempest); FIN forwards untouched, thrice."""
    in_port, seed = int(argv[0]), argv[1].encode()
    client_ports = [int(p) for p in argv[2].split(",")]
    drops0 = {int(x) for x in argv[3].split(",")} if argv[3] else set()
    sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", in_port))
    sock.settimeout(15.0)
    out = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    held = {p: [] for p in client_ports}         # delayed datagrams per client
    n = 0
    try:
        while True:
            data, _addr = sock.recvfrom(65535)
            if data.startswith(_FIN):
                for p in client_ports:           # flush delays, then FIN x3, clean
                    for d in held[p]:
                        out.sendto(d, ("127.0.0.1", p))
                    held[p] = []
                    for _ in range(3):
                        out.sendto(data, ("127.0.0.1", p))
                break
            for ci, p in enumerate(client_ports):
                if ci == 0 and n in drops0:
                    continue                     # REAL loss for client 0
                r = _draw(seed, n, ci)
                if r % 100 < 35:                 # delay: hold for a later flush
                    held[p].append(data)
                else:
                    out.sendto(data, ("127.0.0.1", p))
                if r % 100 >= 70:                # duplicate
                    out.sendto(data, ("127.0.0.1", p))
                if r % 100 >= 96:                # corrupt duplicate (malice)
                    bad = bytearray(data)
                    bad[60] ^= 0x01
                    out.sendto(bytes(bad), ("127.0.0.1", p))
                if held[p] and r % 3 == 0:       # flush the delay buffer (reordered)
                    for d in held[p]:
                        out.sendto(d, ("127.0.0.1", p))
                    held[p] = []
            n += 1
    except _socket.timeout:
        pass


def _serve_fetch(tcp_sock, man, store):
    """The authority's fetch side-channel: one FETCH request answered with the head."""
    tcp_sock.settimeout(20.0)
    try:
        conn, _addr = tcp_sock.accept()
        req = b""
        while not req.endswith(b"\n"):
            req += conn.recv(1024)
        _tag, kx, ky = req.split()
        _w, _h, _c, grid = _CK.parse_manifest(man)
        chunk = store[grid[(int(kx), int(ky))]]
        payload = len(man).to_bytes(8, "big") + man + chunk
        conn.sendall(len(payload).to_bytes(8, "big") + payload)
        conn.close()
    except _socket.timeout:
        pass


def _free_ports(k):
    socks, ports = [], []
    for _ in range(k):
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        s.bind(("127.0.0.1", 0))
        socks.append(s)
        ports.append(s.getsockname()[1])
    for s in socks:
        s.close()
    return ports


def _run_scenario(name, seed, drops0, do_fetch, host_note):
    """One real scenario: relay + two client subprocesses, the authority in-process."""
    import time
    updates, man, store, authwit = authority_log()
    relay_port, c0, c1 = _free_ports(3)
    tdir = _tempfile.mkdtemp(prefix="urdrwat_")
    logs = [_os.path.join(tdir, f"client{ci}.log") for ci in (0, 1)]
    tcp = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    tcp.bind(("127.0.0.1", 0))
    tcp.listen(2)
    tcp_port = tcp.getsockname()[1]
    procs = [_subprocess.Popen([_sys.executable, _os.path.abspath(__file__), "--role",
                                "relay", str(relay_port), seed, f"{c0},{c1}",
                                ",".join(str(d) for d in sorted(drops0))])]
    for ci, (port, log) in enumerate(zip((c0, c1), logs)):
        procs.append(_subprocess.Popen([_sys.executable, _os.path.abspath(__file__),
                                        "--role", "client", str(port), str(tcp_port), log,
                                        "1" if (do_fetch and ci == 0) else "0"]))
    time.sleep(1.0)                              # children bind before the stream starts
    out = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
    for rec in updates:
        out.sendto(rec, ("127.0.0.1", relay_port))
        time.sleep(0.02)
    time.sleep(0.5)
    out.sendto(_FIN + man, ("127.0.0.1", relay_port))
    if do_fetch:
        _serve_fetch(tcp, man, store)
    for p in procs:
        p.wait(timeout=60)
    tcp.close()
    upd_by_hex = {rec.hex(): i for i, rec in enumerate(updates)}
    lines = [f"scenario {name}", "world blank 8"]
    for i, rec in enumerate(updates):
        lines.append(f"update {i} {rec.hex()}")
    lines.append(f"authwit {authwit}")
    for ci, log in enumerate(logs):
        lines.append(f"client {ci}")
        with open(log, encoding="utf-8") as fh:
            for ln in fh:
                parts = ln.split()
                if parts[0] == "P":
                    hx, outcome = parts[1], parts[2]
                    if hx in upd_by_hex:
                        lines.append(f"deliver {ci} u{upd_by_hex[hx]} {outcome}")
                    else:
                        lines.append(f"deliverx {ci} {hx} {outcome}")
                elif parts[0] == "F":
                    lines.append(f"fetch {ci} {parts[1]} {parts[2]} {parts[3]}")
                elif parts[0] == "W":
                    lines.append(f"clientwit {ci} {parts[1]}")
    return lines


def run_attestation(out_path, host_note=""):
    """THE OFF-GATE RUN: both scenarios over real sockets, checked, sealed, written. The
    host line is platform truth plus the operator's note — the NAMED host."""
    import platform
    host = (f"{platform.node()} | {platform.system()} {platform.release()} | "
            f"python {platform.python_version()}"
            + (f" | {host_note}" if host_note else ""))
    lines = ["URDRWAT1 v1", f"host {host}"]
    lines += _run_scenario("gale", "gale-seed-1", set(), False, host)
    lines += _run_scenario("tempest", "tempest-seed-1", {3}, True, host)
    text = seal_trace(lines)
    rep = check_trace(text)                      # the runner refuses to write an unlawful run
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return rep


def golden_trace_path():
    return _os.path.join(_HERE, "..", "..", "spec", "attest", "wire_attest.txt")


if __name__ == "__main__":
    if len(_sys.argv) >= 2 and _sys.argv[1] == "--role":
        if _sys.argv[2] == "client":
            _client_main(_sys.argv[3:])
        elif _sys.argv[2] == "relay":
            _relay_main(_sys.argv[3:])
    elif len(_sys.argv) >= 2 and _sys.argv[1] == "--run":
        out = _sys.argv[2] if len(_sys.argv) > 2 else golden_trace_path()
        note = _sys.argv[3] if len(_sys.argv) > 3 else ""
        report = run_attestation(out, note)
        print("ATTESTATION", report["verdict"], "->", out)
        for key in sorted(report):
            print(f"  {key}: {report[key]}")
    else:
        print("usage: wireattest.py --run [out_path] [host_note]")
