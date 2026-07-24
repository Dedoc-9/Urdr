# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""meshsession — THE ATTESTED MESH SESSION (Phase M, rung M5, URDRMSS1): the capstone, and an EVIDENCE
theorem built ON TOP of the correctness theorems (M3 mesh == monolith, M4 the partition prefix), never
a replacement for them. M1 proved independent authorities execute concurrently; M2 proved authority
moves; M2.5 proved the handoff survives a real socket; M3 proved the mesh equals the monolith while
connected; M4 proved the partitioned mesh stays a prefix of the monolith or refuses. M5 proves the
ENTIRE multi-authority session — concurrency, migration, and a partition episode, threaded through one
timeline — can be ATTESTED and REPLAYED: the demo is not a video, it is a proof.

THE DISCIPLINE (sealsession / wireattest, applied to the whole mesh). A named SESSION is a deterministic
multi-authority playthrough that composes the landed laws: a sequence of EPISODES, each either a
connected MESH TICK (M3 — concurrent writes by the current stewards, then witness-neutral migrations)
or a PARTITION episode (M4 — the world splits into two sides from the live cut, each side writes only
what it can verify, cross-partition ops freeze, and reunification equals a prefix of the monolith),
threaded through ONE evolving state. Running the session yields a chain of WITNESS CHECKPOINTS — the
world witness and custody head after every episode. The session TRACE is that checkpoint chain plus its
own SHA-256: a content-addressed proof object. The CHECK (in-gate, pure): `check_session` RE-RUNS the
named session through the UNMODIFIED laws (`mesh.apply_tick`, `partition.partitioned_from`) and requires
every recorded checkpoint to reproduce bit-for-bit — a tampered witness, a forged custody head, a
dropped episode, or a byte flip in the trace all REFUSE. The session's claims are exactly what the
composed calculus produces, re-derivable by anyone; nothing is trusted.

WHY THIS IS THE CAPSTONE. It exercises the whole Phase-M stack in a single timeline and freezes the
architecture behind one attestation: the concurrency of M1, the migration of M2, the mesh==monolith of
M3, and the partition-prefix of M4 are replayed together to the same witnesses, or the attestation is
UNLAWFUL. Because the correctness theorems already hold, the session is deterministic and its trace is a
fixed artifact; M5 adds the EVIDENCE layer (recorded, self-digested, replayable), not new authority.

GRADE (Phase M rung M5). The named sessions' checkpoint chains and their digests; the sealed trace's
round-trip; the checker's laws (each with a refusing forge — a tampered tick witness, a tampered
partition witness, a forged custody head, a dropped episode); trace integrity (any byte flip refuses on
the self-digest); and determinism are MEASURED (exact, reproducible, a defect diverges). DECLARED: this
is a DETERMINISTIC in-process attestation (the composed correctness laws are deterministic, so the
session needs no named host — the REAL cross-process boundary is attested separately by `meshattest`,
M2.5); scale (the session is a fixed multi-authority playthrough, not a scale claim — "thousands of
authorities" stays MEASURED-on-a-named-host or unclaimed). `does_not_show`: wall-clock (`bench.py`);
cross-placement (URDRMSS1 Python reference only — it attests the Python reference mesh)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRMSS1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import mesh as _MS                                             # M3: concurrent ticks (stateful hooks)
import partition as _PT                                       # M4: the partition episode (stateful hook)


class MeshSessionError(Exception):
    def __init__(self, message):
        super().__init__(f"MESHSESSION-REFUSE: {message}")
        self.code = "MESHSESSION-REFUSE"


# ---- the named session scripts (deterministic multi-authority playthroughs) --------------
def _quadrants():
    """16 regions → four stewards by quadrant; two per side (alfa/bravo = L, charl/delta = R). The
    migration target 'echo' is L."""
    assign = {}
    for ky in range(4):
        for kx in range(4):
            if kx < 2 and ky < 2:
                assign[(kx, ky)] = "alfa"
            elif kx < 2:
                assign[(kx, ky)] = "bravo"
            elif ky < 2:
                assign[(kx, ky)] = "charl"
            else:
                assign[(kx, ky)] = "delta"
    side_of = {"alfa": "L", "bravo": "L", "echo": "L", "charl": "R", "delta": "R"}
    return assign, side_of


def _campaign():
    """The rich capstone session: four stewards write concurrently (M1/M3), authority migrates
    mid-session (M2), a PARTITION episode splits the world and reunifies to a prefix (M4), then the
    reunified world takes more concurrent writes — the whole Phase-M stack in one timeline."""
    fld = _MS.flat_world(32)
    assign, side_of = _quadrants()
    episodes = [
        # 1 — four concurrent stewards, one independence round (M1/M3)
        ("tick", [("alfa", 0, 0, 1, 1, 11), ("bravo", 0, 2, 1, 1, 22),
                  ("charl", 2, 0, 1, 1, 33), ("delta", 2, 2, 1, 1, 44)], []),
        # 2 — concurrent writes + a live migration alfa→echo of region (0,0) (M2)
        ("tick", [("bravo", 0, 3, 2, 2, 5), ("charl", 3, 0, 2, 2, 6)], [(0, 0, "alfa", "echo")]),
        # 3 — the new steward echo writes its region; delta writes concurrently
        ("tick", [("echo", 0, 0, 3, 3, 7), ("delta", 3, 3, 2, 2, 8)], []),
        # 4 — a PARTITION: each side writes its own regions; a cross-write freezes (M4)
        ("partition",
         [("write", "echo", 0, 0, 4, 4, 9), ("write", "bravo", 1, 2, 1, 1, 10),
          ("write", "charl", 2, 0, 4, 4, 99)],                            # 3rd is cross → frozen
         [("write", "charl", 2, 1, 1, 1, 12), ("write", "delta", 3, 2, 1, 1, 13)]),
        # 5 — after reunification, more concurrent writes
        ("tick", [("alfa", 1, 0, 5, 5, 14), ("delta", 2, 2, 6, 6, 15)], []),
    ]
    return fld, assign, side_of, episodes


def _skirmish():
    """A smaller session: two stewards, a migration, a partition, a final tick — the minimal composed
    timeline (used as a second pinned session and a determinism cross-check)."""
    fld = _MS.flat_world(32)
    assign = {}
    for ky in range(4):
        for kx in range(4):
            assign[(kx, ky)] = "lear" if kx < 2 else "raun"
    side_of = {"lear": "L", "raun": "R", "mira": "R"}
    episodes = [
        ("tick", [("lear", 0, 0, 1, 1, 20), ("raun", 3, 3, 1, 1, 21)], []),
        ("tick", [("lear", 1, 1, 2, 2, 22)], [(3, 3, "raun", "mira")]),
        ("partition",
         [("write", "lear", 0, 0, 3, 3, 23), ("write", "lear", 1, 0, 1, 1, 24)],
         [("write", "mira", 3, 3, 3, 3, 25), ("write", "lear", 0, 1, 2, 2, 99)]),  # 2nd R-op cross → frozen
        ("tick", [("raun", 2, 2, 4, 4, 26)], []),
    ]
    return fld, assign, side_of, episodes


_SESSIONS = {"campaign": _campaign, "skirmish": _skirmish}
SESSIONS = ("campaign", "skirmish")


# ---- the executor (threads the session through the unmodified laws) -----------------------
def run_session(name):
    """Run a named session, returning its CHECKPOINT CHAIN: one record per episode (the world witness
    and custody head after it) plus a final checkpoint. Composes `mesh.apply_tick` (M3) and
    `partition.partitioned_from` (M4) through one threaded state."""
    if name not in _SESSIONS:
        raise MeshSessionError(f"unknown session {name!r}")
    field, genesis, side_of, episodes = _SESSIONS[name]()
    state = _MS.initial_state(field, genesis)
    checks = []
    for ep in episodes:
        if ep[0] == "tick":
            _t, writes, migrations = ep
            state = _MS.apply_tick(state, writes, migrations)
            checks.append(("tick", _MS.state_witness(state), _MS.state_custody(state), -1, -1))
        elif ep[0] == "partition":
            _t, left, right = ep
            rep = _PT.partitioned_from(state["field"], state["sman"], side_of, left, right)
            state = _MS.state_from_field(rep["field"], state["sman"], state["certs"])
            checks.append(("partition", rep["witness"], _MS.state_custody(state),
                           rep["admitted_count"], rep["frozen"]))
        else:
            raise MeshSessionError(f"unknown episode {ep[0]!r} in session {name!r}")
    checks.append(("final", _MS.state_witness(state), _MS.state_custody(state), -1, -1))
    return checks


def session_digest(name):
    """URDRMSS1 canon over a session's checkpoint chain — a content address for the whole playthrough."""
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(f"|{name}".encode())
    for (kind, wit, cust, adm, fro) in run_session(name):
        hh.update(f"|{kind}:{wit}:{cust}:{adm}:{fro}".encode())
    return hh.hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_meshsession.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MeshSessionError(f"no golden named {name!r}")


# ---- the self-digested session trace (the proof object) ----------------------------------
def seal_session(name):
    """Serialize a session's checkpoint chain to a self-digested trace — the content-addressed proof
    object anyone can replay."""
    lines = ["URDRMSS1 v1", f"session {name}"]
    for (kind, wit, cust, adm, fro) in run_session(name):
        if kind == "partition":
            lines.append(f"episode partition {wit} {cust} {adm} {fro}")
        else:
            lines.append(f"episode {kind} {wit} {cust}")
    body = "\n".join(lines)
    dig = hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest()
    return body + "\ndigest " + dig + "\n"


def _parse(text):
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise MeshSessionError("a session trace must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest() != claimed:
        raise MeshSessionError("the trace does not hash to its own digest — tampered or truncated; "
                               "a record is re-made, never edited")
    if lines[0] != "URDRMSS1 v1":
        raise MeshSessionError("not a URDRMSS1 v1 session trace")
    if not lines[1].startswith("session "):
        raise MeshSessionError("the trace names no session")
    return lines[1][len("session "):].strip(), lines[2:-1]


def check_session(text):
    """THE ATTESTATION: re-run the named session through the UNMODIFIED laws and require every recorded
    checkpoint to reproduce bit-for-bit — a tampered witness, a forged custody head, a dropped or added
    episode all REFUSE. Returns the report dict; every violation is a typed MESHSESSION-REFUSE."""
    name, recorded = _parse(text)
    truth = run_session(name)                                  # the law re-derives the whole chain
    recs = []
    for ln in recorded:
        p = ln.split()
        if not p or p[0] != "episode":
            raise MeshSessionError(f"unexpected trace line {ln!r}")
        kind = p[1]
        if kind == "partition":
            recs.append(("partition", p[2], p[3], int(p[4]), int(p[5])))
        elif kind in ("tick", "final"):
            recs.append((kind, p[2], p[3], -1, -1))
        else:
            raise MeshSessionError(f"unknown episode kind {kind!r}")
    if len(recs) != len(truth):
        raise MeshSessionError(f"the trace records {len(recs)} episodes but the session has "
                               f"{len(truth)} — a dropped or added episode is refused")
    ticks = parts = 0
    for i, (rec, tru) in enumerate(zip(recs, truth)):
        if rec != tru:
            raise MeshSessionError(f"episode {i} ({tru[0]}) recorded {rec[1][:12]}…/{rec[2][:12]}… but "
                                   f"the law replays {tru[1][:12]}…/{tru[2][:12]}… — reality may not "
                                   f"overrule the composed mesh law")
        ticks += rec[0] == "tick"
        parts += rec[0] == "partition"
    if parts == 0:
        raise MeshSessionError("the session records no partition episode — the capstone must exercise "
                               "the M4 prefix under partition")
    return {"verdict": "LAWFUL", "session": name, "episodes": len(recs), "ticks": ticks,
            "partitions": parts, "final": truth[-1][1]}


def report_digest(rep):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for key in sorted(rep):
        hh.update(f"|{key}:{rep[key]}".encode())
    return hh.hexdigest()


# ---- forges (each must REFUSE — the checker's laws made falsifiable) ----------------------
def forge(name, kind):
    """A tampered session trace (each must refuse under `check_session`): 'tick_witness' flips a tick's
    recorded witness; 'partition_witness' flips the partition episode's witness; 'custody' flips a
    custody head; 'drop_episode' removes an episode; 'admitted' flips the partition admitted count."""
    text = seal_session(name)
    lines = text.rstrip("\n").split("\n")[:-1]                 # drop the digest; we re-seal
    if kind == "tick_witness":
        i = next(k for k, ln in enumerate(lines) if ln.startswith("episode tick "))
        p = lines[i].split()
        p[2] = ("0" if p[2][0] != "0" else "1") + p[2][1:]
        lines[i] = " ".join(p)
    elif kind == "partition_witness":
        i = next(k for k, ln in enumerate(lines) if ln.startswith("episode partition "))
        p = lines[i].split()
        p[2] = ("0" if p[2][0] != "0" else "1") + p[2][1:]
        lines[i] = " ".join(p)
    elif kind == "custody":
        i = next(k for k, ln in enumerate(lines) if ln.startswith("episode tick "))
        p = lines[i].split()
        p[3] = ("0" if p[3][0] != "0" else "1") + p[3][1:]
        lines[i] = " ".join(p)
    elif kind == "drop_episode":
        i = next(k for k, ln in enumerate(lines) if ln.startswith("episode "))
        del lines[i]
    elif kind == "admitted":
        i = next(k for k, ln in enumerate(lines) if ln.startswith("episode partition "))
        p = lines[i].split()
        p[4] = str(int(p[4]) + 1)
        lines[i] = " ".join(p)
    else:
        raise MeshSessionError(f"unknown forge {kind!r}")
    body = "\n".join(lines)
    return body + "\ndigest " + hashlib.sha256(MAGIC + body.encode("utf-8")).hexdigest() + "\n"


def sealed_path():
    return _os.path.join(_HERE, "..", "..", "spec", "attest", "mesh_session.txt")


def _main(argv):
    if len(argv) >= 2 and argv[1] == "--seal":
        for name in SESSIONS:
            with open(sealed_path().replace("mesh_session", f"mesh_session_{name}")
                      if name != "campaign" else sealed_path(), "w", encoding="utf-8",
                      newline="\n") as fh:
                fh.write(seal_session(name))
        print("sealed", ", ".join(SESSIONS))
        return 0
    for name in SESSIONS:
        rep = check_session(seal_session(name))
        print(f"{name}: {rep['verdict']} — {rep['episodes']} episodes "
              f"({rep['ticks']} ticks, {rep['partitions']} partition), digest {session_digest(name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
