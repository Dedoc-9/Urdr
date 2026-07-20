# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""sealsession — THE ATTESTED SESSION (T3.56, V5, URDRSSN1): the visible-world CAPSTONE. `wireattest`
proved the NETWORK met the laws; this proves a PLAY SESSION did. A session composes the whole
visible world Hainuwele built — the loop (V1 `panelight`), the wired world (V2 `panewire`: live
terraform edits over a streamed, region-acquired terrain), and the ghosts (V3 `ghostsnap`: other
actors as equal-or-refuse pose snapshots) — and records it as a SELF-DIGESTED TRACE: the input the
player pressed, the edits that arrived, the ghost stream, and the THREE witnesses the session
produced (avatar, world, ghosts). The demo stops being a video and becomes a PROOF.

THE SPLIT (the `wireattest` discipline, on a session). The RUN is OFF-GATE: a human plays; the
frame timing is wall-clock and nondeterministic, so it may not live in the gate. What crosses the
boundary is the trace — the INPUT (deterministic authority driver) plus the witnesses reality
produced. The CHECK is PURE: the gate REPLAYS the recorded input through the UNMODIFIED laws —
`panewire.run_wired` for the avatar + world, `ghostsnap.ghost_admit` for the ghosts — and verifies
every recorded witness MATCHES what the law replays. Reality's claims (the session's own witnesses)
must equal the law's, or the session is UNLAWFUL. The gate certifies the laws; the attested session
certifies a PLAYTHROUGH met them; neither pretends to be the other.

THE LAWS THE CHECKER ENFORCES: the recorded avatar witness must equal the replayed loop transcript
witness (a forged avatar refuses); the recorded world witness must equal the replayed wired-world
replica (a forged world refuses); the recorded ghost witness must equal the replayed ghost map (a
forged ghost refuses); a recorded edit the wire law would reject cannot appear admitted (malice
refuses); the trace names a host (the named-host law, mechanized); and any byte flip refuses on the
self-digest. Outcomes are LAWFUL or a typed SESSION-REFUSE — never a trusted claim.

GRADE. The checker's laws (each with a refusing synthetic forge — avatar / world / ghost / malice),
trace integrity, the named-host rule, and determinism of the check are MEASURED. The composed
attestation of a real playthrough is MEASURED-on-named-host in bench_protocol's sense (the trace
IS the host log). DECLARED, honestly: the RUN's wall-clock frame cadence is nondeterministic and
OFF-GATE (the `--record` runner captures the deterministic input + witnesses on the named host; the
fps/latency numbers are `sealframe`'s V4 territory, not re-claimed here); the RENDER (the pixels the
player saw) is presentation behind the D15 firewall, never in the witness; a session proves the
AUTHORITY evolution was lawful, not that the pixels were pretty. `does_not_show`: fps/latency; the
render; cross-placement (URDRSSN1 joins the frontier). THIS RUNG SEALS PHASE V — the visible world
is now seen (V1), replicated+streamed (V2), multiplayer (V3), graded honestly (V4), and ATTESTED
(V5): a playthrough whose every authority byte is admitted rather than trusted."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRSSN1"
_HERE = _os.path.dirname(_os.path.abspath(__file__))
_PHYS = _os.path.join(_os.path.dirname(_HERE), "physics")
for _p in (_HERE, _PHYS):
    if _p not in _sys.path:
        _sys.path.insert(0, _p)
import ghostsnap as _GH
import panewire as _PW
from field import ONE


class SessionError(Exception):
    def __init__(self, message):
        super().__init__(f"SESSION-REFUSE: {message}")
        self.code = "SESSION-REFUSE"


# ---- the trace object --------------------------------------------------------------------
def seal_session(lines):
    body = "\n".join(lines)
    return body + "\ndigest " + hashlib.sha256(MAGIC + body.encode()).hexdigest() + "\n"


def parse_session(text):
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 2 or not lines[-1].startswith("digest "):
        raise SessionError("a session trace must end with its own digest line")
    body, claimed = "\n".join(lines[:-1]), lines[-1].split()[1]
    if hashlib.sha256(MAGIC + body.encode()).hexdigest() != claimed:
        raise SessionError("the session does not hash to its own digest — tampered, refused")
    if lines[0] != "URDRSSN1 v1":
        raise SessionError("not a URDRSSN1 v1 session")
    return lines[:-1]


# ---- the recorded session's authority (deterministic given the input) --------------------
def _play(input_log, edits, ghost_stream, observer, radius):
    """Run one session through the UNMODIFIED composed laws: the avatar+world via
    `panewire.run_wired`, the ghosts via `ghostsnap`. Returns (loop_wit, world_wit, ghost_wit,
    ticks, n_edits, n_ghosts). This IS the authority — a pure function of the recorded input."""
    import panelight as _PL
    fld = _PW._blank()
    edit_map = {i: spec for (i, spec) in edits}
    out = _PW.run_wired(fld, (2, 8), input_log, edit_map, 4, 4000)
    loop_wit = _PL.loop_witness(out["transcript"])
    world_wit = _PW.composed_witness(out["transcript"], out["client"])
    gclient = _GH.subscribe_ghosts(observer, radius)
    for snap in ghost_stream:
        gclient = _GH.ghost_admit(gclient, snap)
    ghost_wit = _GH.ghost_witness(gclient)
    return (loop_wit, world_wit, ghost_wit, len(out["transcript"]) - 1,
            len(edits), len(ghost_stream))


def record_session(input_log, edits, ghost_stream, observer, radius, host):
    """Produce a sealed session trace: the input the player pressed, the edits, the ghost stream,
    and the three witnesses the composed laws produced. The RUN is the operator's; this records its
    authority deterministically (the frame timing is off-gate and not recorded here)."""
    loop_wit, world_wit, ghost_wit, ticks, ne, ng = _play(
        input_log, edits, ghost_stream, observer, radius)
    lines = ["URDRSSN1 v1", f"host {host}", "world blank 8", f"input {input_log}",
             f"observer {observer[0]},{observer[1]} radius {radius}"]
    for (i, spec) in edits:
        lines.append("edit %d %s" % (i, " ".join(str(x) for x in spec)))
    for snap in ghost_stream:
        lines.append("ghost " + snap.hex())
    lines.append(f"avatar_wit {loop_wit}")
    lines.append(f"world_wit {world_wit}")
    lines.append(f"ghost_wit {ghost_wit}")
    return seal_session(lines)


# ---- the checker (pure — the composed law replayed over the recorded session) ------------
def check_session(text):
    """THE ATTESTATION VERDICT: replay the recorded input through the UNMODIFIED loop/wire/ghost
    laws and verify every recorded witness matches. Reality's claims must equal the law's, or the
    session is UNLAWFUL. Returns the report; every violation is a typed SESSION-REFUSE."""
    lines = parse_session(text)
    if len(lines) < 2 or not lines[1].startswith("host ") or not lines[1][5:].strip():
        raise SessionError("the session names no host — an unnamed attestation is none "
                           "(bench_protocol's law, mechanized)")
    host = lines[1][5:].strip()
    input_log = None
    observer, radius = (2, 8), 16
    edits, ghosts = [], []
    rec = {}
    for ln in lines[2:]:
        parts = ln.split()
        tag = parts[0]
        if tag == "world":
            if parts[1:] != ["blank", "8"]:
                raise SessionError(f"unknown world {parts[1:]}")
        elif tag == "input":
            input_log = parts[1] if len(parts) > 1 else ""
        elif tag == "observer":
            ox, oy = parts[1].split(",")
            observer = (int(ox), int(oy))
            radius = int(parts[3])
        elif tag == "edit":
            i = int(parts[1])
            spec = tuple(parts[2:]) if parts[2] == "malice" else (parts[2], int(parts[3]),
                                                                  int(parts[4]), int(parts[5]))
            edits.append((i, spec))
        elif tag == "ghost":
            ghosts.append(bytes.fromhex(parts[1]))
        elif tag in ("avatar_wit", "world_wit", "ghost_wit"):
            rec[tag] = parts[1]
        else:
            raise SessionError(f"unknown session line {tag!r}")
    if input_log is None:
        raise SessionError("the session records no input")
    # replay through the unmodified composed laws
    try:
        loop_wit, world_wit, ghost_wit, ticks, ne, ng = _play(
            input_log, edits, ghosts, observer, radius)
    except (_PW.PaneWireError, _GH.GhostError) as exc:
        raise SessionError(f"the recorded session does not replay lawfully: {exc}")
    if rec.get("avatar_wit") != loop_wit:
        raise SessionError("the recorded avatar witness does not equal the replayed loop — "
                           "a forged playthrough, refused")
    if rec.get("world_wit") != world_wit:
        raise SessionError("the recorded world witness does not equal the replayed wired world")
    if rec.get("ghost_wit") != ghost_wit:
        raise SessionError("the recorded ghost witness does not equal the replayed ghost map")
    return {"verdict": "LAWFUL", "host": host, "ticks": ticks, "edits": ne, "ghosts": ng,
            "avatar_wit": loop_wit, "world_wit": world_wit, "ghost_wit": ghost_wit}


def report_digest(rep):
    hh = hashlib.sha256()
    hh.update(MAGIC)
    for key in sorted(rep):
        hh.update(f"|{key}:{rep[key]}".encode())
    return hh.hexdigest()


# ---- synthetic sessions (gate fixtures; the real trace is off-gate --record) -------------
def _ghost_chain(actor_id, xs, ys):
    snaps, parent = [], _GH.GENESIS
    for i, (x, y) in enumerate(zip(xs, ys)):
        s = _GH.ghost_record(actor_id, i, parent, x * ONE, y * ONE, 1)
        snaps.append(s)
        parent = _GH.address(s)
    return snaps


def synth_session(kind, host="synthetic-host (fixture, not a MEASURED claim)", forge=None):
    """Deterministic synthetic sessions for the falsifiers and the gate. kind: 'stroll' (movement
    only), 'wired' (movement + live edits + streaming), 'multiplayer' (+ a ghost stream). forge: a
    woven violation (avatar / world / ghost / malice) that must REFUSE."""
    if kind == "stroll":
        input_log, edits, ghosts, obs, rad = "EEEEEE", [], [], (4, 8), 16
    elif kind == "wired":
        edits = [(1, ("edit", 12, 12, 30)), (3, ("edit", 13, 9, 20))]
        input_log, ghosts, obs, rad = "EEEEEE", [], (4, 8), 16
    elif kind == "multiplayer":
        input_log, edits = "EEEEEE", [(1, ("edit", 12, 12, 30))]
        ghosts = _ghost_chain(2, [5, 6, 7], [9, 9, 9]) + _ghost_chain(3, [3, 3], [7, 6])
        obs, rad = (4, 8), 16
    else:
        raise SessionError(f"unknown session kind {kind!r}")
    text = record_session(input_log, edits, ghosts, obs, rad, host)
    if forge is None:
        return text
    lines = text.rstrip("\n").split("\n")[:-1]
    if forge == "malice":
        # the cheater's claim: swap a lawful edit for a malice marker while KEEPING the world
        # witness the lawful edit produced — a session claiming an illegal edit took effect.
        for i, ln in enumerate(lines):
            if ln.startswith("edit 1 "):
                lines[i] = "edit 1 malice"
                break
        return seal_session(lines)
    tag = {"avatar": "avatar_wit", "world": "world_wit", "ghost": "ghost_wit"}[forge]
    for i, ln in enumerate(lines):
        if ln.startswith(tag + " "):
            w = ln.split()[1]
            lines[i] = f"{tag} {'0' if w[0] != '0' else '1'}{w[1:]}"    # flip one hex nibble
            break
    return seal_session(lines)


def _scene(name, kind):
    rep = check_session(synth_session(kind))
    return report_digest(rep)


def _scene_stroll():
    return _scene("stroll", "stroll")


def _scene_wired():
    return _scene("wired", "wired")


def _scene_multiplayer():
    return _scene("multiplayer", "multiplayer")


def _scene_witnessed():
    """The capstone scene: a multiplayer session's full report digest, pinned — the whole visible
    world (avatar + live world + ghosts) attested in one number."""
    rep = check_session(synth_session("multiplayer"))
    return report_digest({k: rep[k] for k in rep if k != "host"})     # host-independent core


_SCENES = {"stroll": _scene_stroll, "wired": _scene_wired,
           "multiplayer": _scene_multiplayer, "witnessed": _scene_witnessed}
SCENES = ("stroll", "wired", "multiplayer", "witnessed")


def scene_case(name):
    return _SCENES[name]()


def scene_result(name):
    return scene_case(name)


def golden(name):
    with open(_os.path.join(_HERE, "conformance_sealsession.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SessionError(f"no golden named {name!r}")


if __name__ == "__main__":
    if len(_sys.argv) >= 2 and _sys.argv[1] == "--record":
        # OFF-GATE: record a scripted session on the named host (a real playthrough's input log
        # would be captured here; the synthetic script stands in for the demo).
        out = _sys.argv[2] if len(_sys.argv) > 2 else "session_attest.txt"
        note = _sys.argv[3] if len(_sys.argv) > 3 else ""
        import platform
        host = f"{platform.node()} | {platform.system()} {platform.release()}" + (f" | {note}" if note else "")
        ghosts = _ghost_chain(2, [5, 6, 7], [9, 9, 9]) + _ghost_chain(3, [3, 3], [7, 6])
        text = record_session("EEEEEE", [(1, ("edit", 12, 12, 30))], ghosts, (4, 8), 16, host)
        rep = check_session(text)
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("SESSION", rep["verdict"], "->", out)
        for key in sorted(rep):
            print(f"  {key}: {rep[key]}")
    else:
        print("usage: sealsession.py --record [out_path] [host_note]")
