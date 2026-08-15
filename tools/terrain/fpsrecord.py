# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""fpsrecord (URDRFPR1) — the demo's workload records become artifacts the gate re-reads.

THE CLAIM CLASS THIS RUNG MOVES: until now every fpsdemo replay result lived in terminal
transcripts and on one machine's Desktop — the session that produced them lost its scratch
copies to container rollbacks four times while this arc ran. This module commits the traces,
the authoring container's digest chains, and the named host's log as sha256-pinned records,
and derives every figure FROM THOSE BYTES at claim time (L75). What graduates:

  * REPLAY INPUT RECORDS — four traces spanning the input arc: the v0 mouse-only pan (the
    recording whose 0 keyed frames exposed the focusless window), the v1.3 stick-mouse pan
    (whose pad_connected/padded/moused triple identified the handheld), the ONE-FRAME record
    (the Enter-kill witness: v1.4's end key was the key that launches the program), and the
    first REAL WALK (v1.5: 757 keyed frames, ended by an armed Esc).
  * CROSS-OS AGREEMENT AS A COMPARISON OF COMMITTED ARTIFACTS — the named host's log carries
    its own 20-digest chain; the authoring container's chain for the same trace is a separate
    committed record produced by a separate binary on a separate OS. This module parses both
    and asserts equality digest for digest. Byte-identical rendering across operating systems
    stops being a paste in a conversation.
  * INTERNAL BINDING WITHOUT RE-EXECUTION — the gate cannot run the demo (wall-clock class,
    Win32), so a chain is bound to its trace by laws derivable from bytes alone: checkpoint
    frames are exactly the set the loop would emit for that trace's length, and every
    checkpoint inside a trace's leading all-zero prefix must equal the PINNED static-spawn
    constant — a chain claiming to belong to a still camera must open with the still frame.

does_not_show: that the cost rows in the committed log meet any budget (pixelcost owns budget
verdicts; the rows are PRESERVED here, graded nowhere yet); that the container chains were
produced by the exact committed fpsdemo.rs (the harness is its math slice — the selfcheck door
and the host agreement are the evidence, not a hash of the producer); that the walk FELT right
(a trace records what happened, not whether the operator liked it).

falsifier: flip one byte in any record and its pin refuses; edit one digest in either chain
and the cross-OS row or the binding law reddens; hand the trace parser an unknown version
header and it refuses; hand the workload set the one-frame record and it refuses — each is
demonstrated as a law in the selftest, not assumed.
"""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))
_ROOT = _os.path.dirname(_os.path.dirname(_HERE))

MAGIC = b"URDRFPR1"

#: DECLARED — the pinned static-spawn frame digest (fnv64 of the 1280x720 framebuffer at the
#: spawn pose under the v1.1+ render path). Provenance: measured IDENTICAL on the operator's
#: Windows build and the authoring container's Linux build — three replays of the all-zero
#: trace and the openings of walk_v13 and walk_real all print it.
ZERO_CONSTANT = "e224235741921d0f"

#: DECLARED — trace headers this reader admits, exactly as each recording binary wrote them.
KNOWN_TRACE_VERSIONS = (
    "# fpsdemo v0 input trace: keys dx dy (one line per frame)",
    "# fpsdemo v1.3 input trace: keys dx dy (one line per frame)",
    "# fpsdemo v1.4 input trace: keys dx dy (one line per frame)",
    "# fpsdemo v1.5 input trace: keys dx dy (one line per frame)",
)

#: DECLARED — a workload record must span at least two digest checkpoints. The one-frame
#: Enter-kill record is COMMITTED as an incident witness and refused as a workload, as a law.
MIN_WORKLOAD_FRAMES = 120

#: The committed records: verbatim bytes off the named machine's disk (device bridge,
#: 2026-08-14/15) and the authoring container's harness stdout. kind: trace | chain | log.
RECORDS = (
    ("spec/attest/fpsdemo-trace-v0.txt", "trace",
     "28df94134ceb8f97124d16667f71275948b00f75efa6de4eb14c75307b8dd69f"),
    ("spec/attest/fpsdemo-walk-v13.txt", "trace",
     "a3db4792fb9db7f677b91b122e5f6469f9cf97fa7694d246c8c2a88c72ad6874"),
    ("spec/attest/fpsdemo-walk-real.txt", "trace",
     "3b580d9e115c9e2a266729be897bc93e5088b6dd6b11977c131130e2956227d1"),
    ("spec/attest/fpsdemo-junk-1frame.txt", "trace",
     "62917eb9af01b8908d0cdbb7eef036c754b4cb3eb0cd19c41be7480d9e92c6e0"),
    ("spec/attest/fpsdemo-chain-trace-v0.txt", "chain",
     "5b55ebfdbf425be85e8cba9038ab5ef020ef532e55aa42f16c43beee026e4087"),
    ("spec/attest/fpsdemo-chain-walk-v13.txt", "chain",
     "cd35dbdf438c0fdaa5ceb516a5fc699641c3931572ddde26e90f0776049a289d"),
    ("spec/attest/fpsdemo-chain-walk-real.txt", "chain",
     "6eaeb8f4aad5ba79515670d04f8a6f0587d21179b412b4805656a1a3d44a8acc"),
    ("spec/attest/fpsdemo-log-walk-real-named.txt", "log",
     "939055e2fd5429133b3d71a60f6791a22f279254854d1eca043961b3d3f0554c"),
)

#: DECLARED — which chain narrates which trace (indexes into RECORDS), and which traces are
#: workloads. The binding is not taken on trust: bind() checks it from the bytes.
CHAIN_OF = {0: 4, 1: 5, 2: 6}
WORKLOADS = (0, 1, 2)
INCIDENT = 3
NAMED_LOG = 7
LOG_TRACE = 2                      # the named log replays the real walk


class FpsrecordError(Exception):
    def __init__(self, message):
        super().__init__(f"FPSRECORD-REFUSE: {message}")
        self.code = "FPSRECORD-REFUSE"


# ---- records ------------------------------------------------------------------------------------
def load(which, text=None):
    path, _kind, pin = RECORDS[which]
    if text is None:
        with open(_os.path.join(_ROOT, path), encoding="utf-8", newline="") as fh:
            text = fh.read()
    dig = hashlib.sha256(text.encode()).hexdigest()
    if dig != pin:
        raise FpsrecordError(f"record {which} does not hash to its pin — tampered or wrong file")
    return text


def parse_trace(text):
    """A recording binary's trace: one admitted version header, then `keys dx dy` rows."""
    lines = text.rstrip("\n").split("\n")
    if not lines or lines[0] not in KNOWN_TRACE_VERSIONS:
        head = lines[0] if lines else "<empty>"
        raise FpsrecordError(f"unknown trace version header: {head!r}")
    rows = []
    for i, ln in enumerate(lines[1:], start=2):
        if not ln.strip() or ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) != 3:
            raise FpsrecordError(f"trace line {i}: wants `keys dx dy`")
        k, dx, dy = int(p[0]), int(p[1]), int(p[2])
        if not 0 <= k <= 15:
            raise FpsrecordError(f"trace line {i}: keys {k} outside the 4-bit vocabulary")
        rows.append((k, dx, dy))
    if not rows:
        raise FpsrecordError("trace carries no frames")
    return {"version": lines[0], "rows": rows}


def parse_chain(text):
    """The container harness's stdout: `digest frame N fnv64 H` lines, N strictly ascending."""
    out = []
    for i, ln in enumerate(text.rstrip("\n").split("\n"), start=1):
        p = ln.split()
        if len(p) != 5 or p[0] != "digest" or p[1] != "frame" or p[3] != "fnv64":
            raise FpsrecordError(f"chain line {i}: not a digest line")
        fr, dig = int(p[2]), p[4]
        if len(dig) != 16 or any(c not in "0123456789abcdef" for c in dig):
            raise FpsrecordError(f"chain line {i}: digest is not 16 lowercase hex chars")
        if out and fr <= out[-1][0]:
            raise FpsrecordError(f"chain line {i}: frames not strictly ascending")
        out.append((fr, dig))
    if not out:
        raise FpsrecordError("chain carries no checkpoints")
    return out


def parse_named_log(text):
    """The demo's own log off the named machine: header with declared conditions, a conditions
    line, a frames line, and the digest chain."""
    lines = text.rstrip("\n").split("\n")
    if len(lines) < 4:
        raise FpsrecordError(f"log too short: {len(lines)} lines")
    head = [p.strip() for p in lines[0].split("|")]
    if not head[0].startswith("fpsdemo v1.5"):
        raise FpsrecordError(f"log version not admitted: {head[0]!r}")
    fields = {}
    for part in head[1:]:
        kv = part.split(None, 1)
        if len(kv) == 2:
            fields[kv[0]] = kv[1]
    for cond in ("host", "power", "scheduler"):
        if fields.get(cond, "-") == "-":
            raise FpsrecordError(f"log declares no {cond} — an anonymous log grades nothing")
    if "frames" not in lines[2]:
        raise FpsrecordError("log line 3 is not the frames line")
    frames = int(lines[2].split("|")[0].split()[1])
    chain = parse_chain("\n".join(ln for ln in lines if ln.startswith("digest ")))
    return {"fields": fields, "frames": frames, "chain": chain}


# ---- derivations (L75: every figure from the committed bytes, at claim time) --------------------
def activity(trace):
    rows = trace["rows"]
    keyed = sum(1 for k, _dx, _dy in rows if k != 0)
    moused = sum(1 for _k, dx, dy in rows if dx != 0 or dy != 0)
    zero_prefix = 0
    for k, dx, dy in rows:
        if k == 0 and dx == 0 and dy == 0:
            zero_prefix += 1
        else:
            break
    return {"frames": len(rows), "keyed": keyed, "moused": moused, "zero_prefix": zero_prefix}


def expected_checkpoints(frames):
    """The loop's digest schedule for a trace of this length: every frame ≡ 59 (mod 60), plus
    the final frame if it is not already a checkpoint."""
    out = [f for f in range(frames) if f % 60 == 59]
    if frames >= 1 and (frames - 1) % 60 != 59:
        out.append(frames - 1)
    return out


def bind(trace, chain):
    """A chain belongs to a trace only if its checkpoint frames are exactly the schedule for
    that trace's length, and every checkpoint inside the trace's leading all-zero prefix
    carries the pinned static-spawn constant."""
    act = activity(trace)
    if [f for f, _d in chain] != expected_checkpoints(act["frames"]):
        raise FpsrecordError("chain checkpoints are not the schedule for this trace's length")
    for f, d in chain:
        if f < act["zero_prefix"] and d != ZERO_CONSTANT:
            raise FpsrecordError(
                f"checkpoint {f} sits inside the all-zero prefix and is not the pinned "
                f"static-spawn constant — this chain does not narrate this trace")
    return True


def crossos(log, container_chain):
    """The named host's chain against the authoring container's, digest for digest."""
    if len(log["chain"]) != len(container_chain):
        return False
    return all(a == b for a, b in zip(log["chain"], container_chain))


# ---- the laws, as refusals the selftest demonstrates -------------------------------------------
def a_flipped_byte_refuses():
    text = load(0)
    bad = text[:100] + ("0" if text[100] != "0" else "1") + text[101:]
    try:
        load(0, text=bad)
    except FpsrecordError:
        return True
    return False


def an_unknown_trace_version_refuses():
    try:
        parse_trace("# fpsdemo v9.9 input trace: keys dx dy (one line per frame)\n0 0 0\n")
    except FpsrecordError:
        return True
    return False


def a_one_frame_trace_is_not_a_workload():
    act = activity(parse_trace(load(INCIDENT)))
    return act["frames"] < MIN_WORKLOAD_FRAMES


def a_mismatched_chain_reddens():
    log = parse_named_log(load(NAMED_LOG))
    chain = list(parse_chain(load(CHAIN_OF[LOG_TRACE])))
    f, d = chain[-1]
    chain[-1] = (f, ("0" * 16) if d != "0" * 16 else "1" * 16)
    return not crossos(log, chain)


def a_foreign_chain_refuses_binding():
    """walk_v13's chain (1800-frame schedule) may not narrate the real walk (1145 frames)."""
    trace = parse_trace(load(2))
    chain = parse_chain(load(5))
    try:
        bind(trace, chain)
    except FpsrecordError:
        return True
    return False


def a_truncated_log_refuses():
    text = load(NAMED_LOG)
    try:
        parse_named_log("\n".join(text.split("\n")[:2]))
    except FpsrecordError:
        return True
    return False


# ---- scenes -------------------------------------------------------------------------------------
def _admit_all():
    traces = {i: parse_trace(load(i)) for i, (_p, k, _s) in enumerate(RECORDS) if k == "trace"}
    chains = {i: parse_chain(load(i)) for i, (_p, k, _s) in enumerate(RECORDS) if k == "chain"}
    log = parse_named_log(load(NAMED_LOG))
    return traces, chains, log


def scene_case(name):
    traces, chains, log = _admit_all()
    if name == "records":
        acts = {RECORDS[i][0].rsplit("/", 1)[1]: activity(t) for i, t in sorted(traces.items())}
        return repr(sorted(acts.items()))
    if name == "laws":
        bound = [bind(traces[t], chains[c]) for t, c in sorted(CHAIN_OF.items())]
        return repr((bound, crossos(log, chains[CHAIN_OF[LOG_TRACE]]),
                     sorted(log["fields"].items()), log["frames"],
                     a_one_frame_trace_is_not_a_workload()))
    raise FpsrecordError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_fpsrecord.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FpsrecordError(f"no golden named {name!r}")
