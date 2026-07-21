# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""meshattest — THE MESH REALITY ATTESTATION (Phase M rung M2.5, URDRMAT1): authority migration
over REAL sockets and REAL processes, judged by the same laws after the fact. `migrate` (M2) proved
the handoff protocol with INFORMATIONAL isolation — the shard's inputs do not contain the world, but
everything still ran in one process. This rung crosses the one boundary M2 declared out of scope:
the migration certificate is SERIALIZED, sent over a real TCP socket to a SEPARATE OS PROCESS,
DESERIALIZED there from raw bytes, and adopted by the unmodified `migrate` law running in that far
process — and the source node's post-handoff write is refused ACROSS the process boundary. It is the
wireattest discipline (T3.51) applied to custody: sockets and wall-clock are NONDETERMINISTIC, so by
the house law they may not live inside the gate; what crosses back is a SELF-DIGESTED TRACE — reality
recorded once, re-verified forever.

THE SPLIT. The RUN (off-gate, `python meshattest.py --run` on a NAMED host): a COORDINATOR process
mints migration certificates and drives two real steward-NODE subprocesses over TCP; each node runs
the UNMODIFIED `migrate` laws on state it receives as raw bytes — a node ADOPTS a certificate it
never minted (apply_migration from the wire bytes, in the far process), a node ADMITS a write as the
region's steward, and the OLD steward node's write is REFUSED after the handoff (the double-writer
caught across a real socket). Every migration, admission, outcome, and witness is recorded; the trace
is sealed with its own SHA-256. The CHECK (in-gate, pure): the checker REPLAYS every recorded
migration through `migrate.migrate` and every recorded write through `migrate.admit` against its own
world — reality's claims (the certificate bytes, the outcomes, the witnesses, the custody head) must
MATCH what the law replays, or the attestation is UNLAWFUL. The gate certifies the laws; the
attestation certifies reality met them; the trace is where they shake hands.

THE NAMED-HOST LAW, MECHANIZED (bench_protocol's rule made structural, inherited from wireattest): a
trace with an empty or missing host line REFUSES — an unnamed MEASURED is no MEASURED at all. The
pinned trace lives at spec/attest/mesh_attest.txt; the gate re-verifies it on every run, on every
host, byte-deterministically, and names its host in the gate output.

THE LAWS THE CHECKER ENFORCES: genesis custody must be total and lawful; every recorded migration's
CERTIFICATE BYTES must equal what `migrate` mints from the current world+custody (a forged or
substituted certificate refuses — reality may not overrule the mint); every recorded write outcome
must equal the law's replayed outcome (a usurper's write recorded as ADMIT refuses — the double-
writer cannot launder itself through reality); every recorded ADMIT witness must equal the replayed
world (silent drift refuses); a refused write must leave the world untouched; outcomes are typed
ADMIT / MIGRATE-REFUSE only; and the final world witness and custody head must equal the replayed
head. THE DIFFERENTIATED CLAIM, re-attested over reality: after A→B, the source steward's fully-
lease-lawful write is REFUSED — single-writer safety survives a real process boundary.

GRADE. The checker's laws (each with a refusing synthetic forge), trace integrity (any byte flip
refuses), the named-host rule, determinism of the check, and the verdict-bound report digest are
MEASURED. The pinned trace's verdict is MEASURED (named host) in bench_protocol's sense — the trace
IS the host log. DECLARED, honestly: the run exercises loopback TCP on one machine (real sockets,
real processes, real serialization and kernel buffering — but not cross-machine networks, NAT, or the
open internet); wall-clock latency is NOT claimed (`bench.py` §3's job); a PARTITION during handoff
(a lost certificate, a torn commit visible to a live peer) is M4's territory, not re-attested here —
this rung attests the RELIABLE handoff crossing a real boundary, the CP posture's happy path made
real. `does_not_show`: throughput/scale (never a measured number until the scale bench); cross-
placement (URDRMAT1 attests URDRMIG1, itself Python reference only)."""
import hashlib
import os as _os
import socket as _socket
import subprocess as _subprocess
import sys as _sys
import tempfile as _tempfile

MAGIC = b"URDRMAT1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import chunkload as _CK                                         # noqa: E402
import rannull as _RN                                           # noqa: E402
import lease as _LS                                             # noqa: E402
import migrate as _MG                                           # noqa: E402

_OUTCOMES = ("ADMIT", "MIGRATE-REFUSE")
_C = 8


class MeshAttestError(Exception):
    def __init__(self, message):
        super().__init__(f"MESHATTEST-REFUSE: {message}")
        self.code = "MESHATTEST-REFUSE"


# ---- the fixed world -------------------------------------------------------------------
def _blank():
    import heightfield as _HF
    return _HF.scene_digest(_HF.SCENES["blank"]())[1]


def _fresh_world():
    fld = _blank()
    man = _CK.field_manifest(fld, _C)
    store = {_CK.address(r): r for r in _CK.cut(fld, _C).values()}
    return man, store


def _lease_and_rec(man, store, kx, ky, lx, ly, dh):
    """Reconstruct the lease + regional record for one region-local cell against the CURRENT world
    — leases are byte-identical regardless of holder (M2's blindness), so custody, not the lease,
    decides admission."""
    x, y = kx * _C + lx, ky * _C + ly
    grid = _CK.parse_manifest(man)[3]
    chunk = store[grid[(kx, ky)]]
    old = _CK.restore_chunk(chunk)[2][ly][lx]
    return (_LS.lease_from_chunk(chunk),
            _RN.regional_record(_CK.address(chunk), kx, ky, x, y, old, old + dh))


# ---- the trace object (wireattest discipline) ------------------------------------------
def seal_trace(lines):
    body = "\n".join(lines)
    dig = hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest()
    return body + "\ndigest " + dig + "\n"


def parse_trace(text):
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise MeshAttestError("a trace must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest() != claimed:
        raise MeshAttestError("the trace does not hash to its own digest — tampered or truncated; "
                              "a record is re-made, never edited")
    if lines[0] != "URDRMAT1 v1":
        raise MeshAttestError("not a URDRMAT1 v1 trace")
    return lines[:-1]


# ---- the checker (pure — the migration law replayed over reality's record) -------------
def check_trace(text):
    """The attestation verdict: replay every recorded genesis / migration / write through the
    UNMODIFIED `migrate` laws; reality's claims must match. Returns the report dict; every
    violation is a typed MESHATTEST-REFUSE."""
    lines = parse_trace(text)
    if len(lines) < 2 or not lines[1].startswith("host ") or not lines[1][5:].strip():
        raise MeshAttestError("the attestation names no host — an unnamed MEASURED is no "
                              "MEASURED at all (bench_protocol's law, mechanized)")
    host = lines[1][5:].strip()
    man, store = _fresh_world()
    sman = None
    certs = {}
    scenarios = []
    nodes = {}
    stats = {"migrations": 0, "admits": 0, "refusals": 0, "usurpers_refused": 0}
    scen = None
    for ln in lines[2:]:
        parts = ln.split()
        if not parts:
            continue
        tag = parts[0]
        if tag == "scenario":
            scen = parts[1]
            scenarios.append(scen)
            man, store = _fresh_world()               # each scenario is a fresh world
            sman, certs, nodes = None, {}, {}
        elif tag == "world":
            if parts[1:] != ["blank", "8"]:
                raise MeshAttestError(f"unknown world {parts[1:]} — the corpus is blank/C=8")
        elif tag == "genesis":
            steward = _MG.steward_tag(parts[1])
            sman = _MG.steward_genesis(man, {k: steward for k in _CK.parse_manifest(man)[3]})
        elif tag == "node":
            nodes[parts[1]] = parts[2]                 # node id -> home steward (informational)
        elif tag == "migrate":
            if sman is None:
                raise MeshAttestError("a migration arrived before genesis")
            kx, ky, src, dst, cert_hex = (int(parts[1]), int(parts[2]),
                                          _MG.steward_tag(parts[3]), _MG.steward_tag(parts[4]),
                                          parts[5])
            sman2, cert = _MG.migrate(sman, certs, man, kx, ky, src, dst)
            if cert.hex() != cert_hex:
                raise MeshAttestError(f"migration of ({kx},{ky}) recorded a certificate that the "
                                      f"law does not mint — a forged or substituted certificate "
                                      f"crossed the wire; reality may not overrule the mint")
            certs[_MG.address(cert)] = cert
            sman = sman2
            stats["migrations"] += 1
        elif tag == "write":
            if sman is None:
                raise MeshAttestError("a write arrived before genesis")
            _nid, writer = parts[1], _MG.steward_tag(parts[2])
            kx, ky, lx, ly, dh = (int(parts[3]), int(parts[4]), int(parts[5]),
                                  int(parts[6]), int(parts[7]))
            outcome = parts[8]
            if outcome not in _OUTCOMES:
                raise MeshAttestError(f"outcome {outcome!r} is untyped — refusals are typed or "
                                      f"they are nothing")
            ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
            before = _CK.address(man)
            try:
                new_man, ch = _MG.admit(sman, certs, man, dict(store), writer, ls, rec)
                law = "ADMIT"
            except _MG.MigrateError:
                law = "MIGRATE-REFUSE"
            if law != outcome:
                raise MeshAttestError(f"node {_nid} recorded {outcome} for {_MG._tag_str(writer)} "
                                      f"writing ({kx},{ky}) but the law replays {law} — reality "
                                      f"may not overrule the law (a double-writer cannot launder "
                                      f"itself through a socket)")
            if law == "ADMIT":
                if len(parts) < 10:
                    raise MeshAttestError("an ADMIT write must record its resulting witness")
                store[_CK.address(ch)] = ch
                man = new_man
                if parts[9] != _CK.address(man):
                    raise MeshAttestError(f"node {_nid}'s recorded witness does not equal the "
                                          f"replayed world — silent drift, the one poison")
                stats["admits"] += 1
            else:
                if _CK.address(man) != before:
                    raise MeshAttestError("a refused write moved the world — refuse purity broken")
                stats["refusals"] += 1
                # a refusal by a steward that USED to own the region is the usurper
                cur = _MG.current_steward(sman, kx, ky)[0]
                if writer != cur:
                    stats["usurpers_refused"] += 1
        elif tag == "finalwit":
            if parts[1] != _CK.address(man):
                raise MeshAttestError("the recorded final world witness does not equal the "
                                      "replayed head")
        elif tag == "finalcustody":
            if sman is None or parts[1] != _MG.address(sman):
                raise MeshAttestError("the recorded final custody head does not equal the "
                                      "replayed steward manifest")
        else:
            raise MeshAttestError(f"unknown trace line {tag!r}")
    if not scenarios:
        raise MeshAttestError("the trace records no scenario")
    if stats["migrations"] == 0:
        raise MeshAttestError("the attestation records no migration — nothing crossed the wire")
    if stats["usurpers_refused"] == 0:
        raise MeshAttestError("no usurper was refused — the differentiated claim (single-writer "
                              "across a real boundary) is unwitnessed")
    return {"verdict": "LAWFUL", "host": host, "scenarios": tuple(scenarios),
            "nodes": len(nodes), "migrations": stats["migrations"], "admits": stats["admits"],
            "refusals": stats["refusals"], "usurpers_refused": stats["usurpers_refused"]}


def report_digest(rep):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for key in sorted(rep):
        hh.update(f"|{key}:{rep[key]}".encode())
    return hh.hexdigest()


# ---- the honest simulator (shared by synthetic fixtures AND the real run's recorder) ---
_HANDOFF = (("write", "0", "alfa", 0, 1, 5, 0, 1000),
            ("migrate", 0, 1, "alfa", "bravo"),
            ("write", "1", "bravo", 0, 1, 6, 0, 50),
            ("write", "0", "alfa", 0, 1, 4, 0, 7),          # the usurper, post-handoff
            ("write", "0", "alfa", 1, 1, 2, 2, 300))        # a disjoint region, still alfa's
_RELAY = (("write", "0", "alfa", 0, 1, 5, 0, 100),
          ("migrate", 0, 1, "alfa", "bravo"),
          ("write", "1", "bravo", 0, 1, 5, 0, 50),
          ("migrate", 0, 1, "bravo", "charl"),
          ("write", "2", "charl", 0, 1, 5, 0, 25),
          ("write", "1", "bravo", 0, 1, 4, 0, 9))           # bravo is now the usurper


def _play(script, genesis="alfa"):
    """Execute a script through the REAL laws IN PROCESS, returning the recorded trace lines (no
    host/header). Every outcome is what the law did — the same recorder the real run reuses so a
    node that merely echoes the law produces an identical record."""
    man, store = _fresh_world()
    sman = _MG.steward_genesis(man, {k: _MG.steward_tag(genesis) for k in _CK.parse_manifest(man)[3]})
    certs = {}
    lines = ["world blank 8", f"genesis {genesis}"]
    homes = {}
    for step in script:
        if step[0] == "write":
            homes.setdefault(step[1], step[2])
    for nid in sorted(homes):
        lines.append(f"node {nid} {homes[nid]}")
    for step in script:
        if step[0] == "migrate":
            _t, kx, ky, src, dst = step
            sman2, cert = _MG.migrate(sman, certs, man, kx, ky, _MG.steward_tag(src),
                                      _MG.steward_tag(dst))
            certs[_MG.address(cert)] = cert
            sman = sman2
            lines.append(f"migrate {kx} {ky} {src} {dst} {cert.hex()}")
        else:
            _t, nid, writer, kx, ky, lx, ly, dh = step
            ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
            try:
                new_man, ch = _MG.admit(sman, certs, man, dict(store), _MG.steward_tag(writer),
                                        ls, rec)
                store[_CK.address(ch)] = ch
                man = new_man
                lines.append(f"write {nid} {writer} {kx} {ky} {lx} {ly} {dh} ADMIT "
                             f"{_CK.address(man)}")
            except _MG.MigrateError:
                lines.append(f"write {nid} {writer} {kx} {ky} {lx} {ly} {dh} MIGRATE-REFUSE")
    lines.append(f"finalwit {_CK.address(man)}")
    lines.append(f"finalcustody {_MG.address(sman)}")
    return lines


def synth_trace(kind, host="synthetic-host (fixture, not a MEASURED claim)", forge=None):
    """Deterministic synthetic traces for the falsifiers and the gate's law rows. kind: 'handoff'
    (A→B with a usurper + a disjoint write) or 'relay' (A→B→C custody chain). forge: a named
    violation woven in (each must REFUSE)."""
    script = {"handoff": _HANDOFF, "relay": _RELAY}.get(kind)
    if script is None:
        raise MeshAttestError(f"unknown synthetic kind {kind!r}")
    lines = _play(script)
    if forge == "usurper_admit":
        # the post-handoff usurper's REFUSE relabelled ADMIT — the double-writer lie
        idx = next(i for i, ln in enumerate(lines)
                   if ln.startswith("write 0 alfa ") and ln.endswith("MIGRATE-REFUSE"))
        lines[idx] = lines[idx].replace("MIGRATE-REFUSE", "ADMIT") + " " + "0" * 64
    elif forge == "witness":
        idx = next(i for i, ln in enumerate(lines) if " ADMIT " in ln)
        p = lines[idx].split()
        wit = p[-1]
        p[-1] = ("0" if wit[0] != "0" else "1") + wit[1:]
        lines[idx] = " ".join(p)
    elif forge == "forged_cert":
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("migrate "))
        p = lines[idx].split()
        cert = p[5]
        p[5] = cert[:20] + ("0" if cert[20] != "0" else "1") + cert[21:]
        lines[idx] = " ".join(p)
    elif forge == "swap_dst":
        # a migration recorded to the WRONG destination steward (the cert won't re-mint)
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("migrate "))
        p = lines[idx].split()
        p[4] = "mallory"
        lines[idx] = " ".join(p)
    elif forge == "untyped":
        idx = next(i for i, ln in enumerate(lines) if " MIGRATE-REFUSE" in ln)
        lines[idx] = lines[idx].replace("MIGRATE-REFUSE", "SOFT-FAIL")
    elif forge == "drop_migration":
        # remove the migration but keep bravo's ADMIT write — bravo has no standing → law refuses
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("migrate "))
        del lines[idx]
    elif forge == "finalwit":
        idx = next(i for i, ln in enumerate(lines) if ln.startswith("finalwit "))
        wit = lines[idx].split()[1]
        lines[idx] = f"finalwit {('0' if wit[0] != '0' else '1') + wit[1:]}"
    elif forge is not None:
        raise MeshAttestError(f"unknown forge {forge!r}")
    return seal_trace(["URDRMAT1 v1", f"host {host}", f"scenario {kind}"] + lines)


# ---- the off-gate runner (real processes, real TCP, the certificate on the wire) -------
def _recvn(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise MeshAttestError("the peer closed mid-message")
        buf += chunk
    return buf


def _send_msg(sock, fields):
    body = "\n".join(f"{k} {v}" for k, v in fields.items()).encode("utf-8")
    sock.sendall(len(body).to_bytes(8, "big") + body)


def _recv_msg(sock):
    n = int.from_bytes(_recvn(sock, 8), "big")
    body = _recvn(sock, n).decode("utf-8")
    out = {}
    for ln in body.split("\n"):
        k, _, v = ln.partition(" ")
        out[k] = v
    return out


def _store_from_hex(blob):
    if not blob:
        return {}
    return {_CK.address(bytes.fromhex(h)): bytes.fromhex(h) for h in blob.split(",")}


def _certs_from_hex(blob):
    """The CERTIFICATE store — keyed by the certificate's own address (`migrate.address`), not a
    chunk address; a cert is URDRMIG1, not URDRCHK1."""
    if not blob:
        return {}
    return {_MG.address(bytes.fromhex(h)): bytes.fromhex(h) for h in blob.split(",")}


def _store_to_hex(store):
    return ",".join(rec.hex() for rec in store.values())


def _certs_to_hex(certs):
    return ",".join(c.hex() for c in certs.values())


def _node_main(argv):
    """A real steward-NODE subprocess: bind a TCP port, then answer, in the FAR PROCESS, requests
    that run the UNMODIFIED `migrate` laws on state received as raw bytes. Ops:
      adopt: deserialize a certificate from the wire, apply_migration → new steward manifest hex.
      admit: reconstruct lease+record, run migrate.admit as <writer> → outcome + witness.
    The node never trusts a byte it did not verify — restore_certificate / admit refuse corruption."""
    port = int(argv[0])
    srv = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
    srv.setsockopt(_socket.SOL_SOCKET, _socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(4)
    srv.settimeout(30.0)
    while True:
        try:
            conn, _addr = srv.accept()
        except _socket.timeout:
            break
        try:
            req = _recv_msg(conn)
            op = req.get("op", "")
            if op == "stop":
                conn.close()
                break
            man = bytes.fromhex(req["man"])
            sman = bytes.fromhex(req["sman"])
            certs = _certs_from_hex(req.get("certs", ""))
            if op == "adopt":
                cert = bytes.fromhex(req["cert"])           # raw bytes off the wire
                try:
                    new_sman = _MG.apply_migration(sman, man, cert)
                    _send_msg(conn, {"ok": "1", "sman": new_sman.hex()})
                except _MG.MigrateError as exc:
                    _send_msg(conn, {"ok": "0", "err": str(exc).replace("\n", " ")})
            elif op == "admit":
                store = _store_from_hex(req["store"])
                writer = bytes.fromhex(req["writer"])
                kx, ky, lx, ly, dh = (int(req["kx"]), int(req["ky"]), int(req["lx"]),
                                      int(req["ly"]), int(req["dh"]))
                ls, rec = _lease_and_rec(man, store, kx, ky, lx, ly, dh)
                try:
                    new_man, ch = _MG.admit(sman, certs, man, dict(store), writer, ls, rec)
                    _send_msg(conn, {"ok": "1", "outcome": "ADMIT", "man": new_man.hex(),
                                     "chunk": ch.hex(), "wit": _CK.address(new_man)})
                except _MG.MigrateError:
                    _send_msg(conn, {"ok": "1", "outcome": "MIGRATE-REFUSE"})
            else:
                _send_msg(conn, {"ok": "0", "err": f"unknown op {op!r}"})
        finally:
            conn.close()
    srv.close()


def _call_node(port, fields, tries=40):
    import time
    last = None
    for _ in range(tries):
        try:
            c = _socket.create_connection(("127.0.0.1", port), timeout=5.0)
            _send_msg(c, fields)
            rep = _recv_msg(c)
            c.close()
            return rep
        except (ConnectionRefusedError, OSError) as exc:      # node still binding
            last = exc
            time.sleep(0.1)
    raise MeshAttestError(f"node on port {port} never answered: {last}")


def _run_scenario(name, script, genesis="alfa"):
    """One REAL scenario: the migration certificate and every admission cross a real TCP socket to
    real node subprocesses; the coordinator records what reality did, in the trace format `_play`
    also emits, so the checker replays both identically."""
    import time
    homes = {}
    for step in script:
        if step[0] == "write":
            homes.setdefault(step[1], step[2])
    ports = {}
    procs = {}
    s0 = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)   # borrow free ports
    frees = []
    for _ in range(len(homes)):
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        frees.append(s)
    for nid, s in zip(sorted(homes), frees):
        ports[nid] = s.getsockname()[1]
        s.close()
    s0.close()
    for nid in sorted(homes):
        procs[nid] = _subprocess.Popen([_sys.executable, _os.path.abspath(__file__),
                                        "--role", "node", str(ports[nid])])
    time.sleep(1.0)                                            # let nodes bind
    try:
        man, store = _fresh_world()
        sman = _MG.steward_genesis(man, {k: _MG.steward_tag(genesis)
                                         for k in _CK.parse_manifest(man)[3]})
        certs = {}
        lines = [f"scenario {name}", "world blank 8", f"genesis {genesis}"]
        for nid in sorted(homes):
            lines.append(f"node {nid} {homes[nid]}")
        for step in script:
            if step[0] == "migrate":
                _t, kx, ky, src, dst = step
                # coordinator mints; the DESTINATION node adopts it from raw wire bytes
                sman2, cert = _MG.migrate(sman, certs, man, kx, ky, _MG.steward_tag(src),
                                          _MG.steward_tag(dst))
                dst_nid = next(n for n in sorted(homes) if homes[n] == dst)
                rep = _call_node(ports[dst_nid], {"op": "adopt", "man": man.hex(),
                                                  "sman": sman.hex(), "certs": _certs_to_hex(certs),
                                                  "cert": cert.hex()})
                if rep.get("ok") != "1" or bytes.fromhex(rep["sman"]) != sman2:
                    raise MeshAttestError(f"the destination node did not reproduce the adopted "
                                          f"steward manifest for ({kx},{ky}) — reality diverged "
                                          f"from the mint")
                certs[_MG.address(cert)] = cert
                sman = sman2
                lines.append(f"migrate {kx} {ky} {src} {dst} {cert.hex()}")
            else:
                _t, nid, writer, kx, ky, lx, ly, dh = step
                rep = _call_node(ports[nid], {"op": "admit", "man": man.hex(), "sman": sman.hex(),
                                              "certs": _certs_to_hex(certs),
                                              "store": _store_to_hex(store),
                                              "writer": _MG.steward_tag(writer).hex(),
                                              "kx": str(kx), "ky": str(ky), "lx": str(lx),
                                              "ly": str(ly), "dh": str(dh)})
                outcome = rep["outcome"]
                if outcome == "ADMIT":
                    ch = bytes.fromhex(rep["chunk"])
                    store[_CK.address(ch)] = ch
                    man = bytes.fromhex(rep["man"])
                    lines.append(f"write {nid} {writer} {kx} {ky} {lx} {ly} {dh} ADMIT "
                                 f"{_CK.address(man)}")
                else:
                    lines.append(f"write {nid} {writer} {kx} {ky} {lx} {ly} {dh} MIGRATE-REFUSE")
        lines.append(f"finalwit {_CK.address(man)}")
        lines.append(f"finalcustody {_MG.address(sman)}")
        return lines
    finally:
        for nid, port in ports.items():
            try:
                _call_node(port, {"op": "stop"}, tries=1)
            except Exception:
                pass
        for p in procs.values():
            try:
                p.wait(timeout=15)
            except Exception:
                p.kill()


def run_attestation(out_path, host_note=""):
    """THE OFF-GATE RUN: both scenarios over real TCP + real node subprocesses, checked, sealed,
    written. The host line is platform truth plus the operator's note — the NAMED host."""
    import platform
    host = (f"{platform.node()} | {platform.system()} {platform.release()} | "
            f"python {platform.python_version()}" + (f" | {host_note}" if host_note else ""))
    lines = ["URDRMAT1 v1", f"host {host}"]
    lines += _run_scenario("handoff", _HANDOFF)
    lines += _run_scenario("relay", _RELAY)
    text = seal_trace(lines)
    rep = check_trace(text)                                    # refuse to write an unlawful run
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return rep


def golden_trace_path():
    return _os.path.join(_HERE, "..", "..", "spec", "attest", "mesh_attest.txt")


if __name__ == "__main__":
    if len(_sys.argv) >= 3 and _sys.argv[1] == "--role" and _sys.argv[2] == "node":
        _node_main(_sys.argv[3:])
    elif len(_sys.argv) >= 2 and _sys.argv[1] == "--run":
        out = _sys.argv[2] if len(_sys.argv) > 2 else golden_trace_path()
        note = _sys.argv[3] if len(_sys.argv) > 3 else ""
        report = run_attestation(out, note)
        print("MESH ATTESTATION", report["verdict"], "->", out)
        for key in sorted(report):
            print(f"  {key}: {report[key]}")
    else:
        print("usage: meshattest.py --run [out_path] [host_note]")
