#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""frontfps_view — the display-only view stream (frontfps Stage 5, URDR-FPSW-VIEW-2).

The binary, delta-framed successor of D15's `to_view`: what a layer-3 renderer
consumes to draw a frame. It CARRIES the authoritative witness as a bound
reference and moves a separate VIEW encoding — presentation, never authority.

Three laws, each a gate row that can redden:

  1. recompute   — a view frame is a pure function of authority state: encode is
                   deterministic (byte-identical twice), decode∘encode reproduces
                   the display sequence, and the bound witness recomputes from the
                   authoritative snapshot.
  2. no-feedback — the authoritative witness bound in a frame is invariant under
                   presentation (the quantization / LOD shift). A defect that
                   folds a presentation value into the witness MUST make it move.
                   And the decoded display is a LOSSY projection: two distinct
                   authority states collapse to one display, so there is no
                   inverse — the firewall is structural (decode returns a display
                   frame, never a Scene), not a comment.
  3. bandwidth   — bytes per authored scene are a host-independent fact, pinned
                   like the op-count proxies (never fps).

Delta framing: a stream is one keyframe (full visible set) followed by delta
frames that encode only the actors whose quantized transform changed since a
named base sequence number. A delta that references a base never sent — or a
stream that opens on a delta — is VIEW-REFUSEd.

Scope: the authored corpus has a FIXED actor set (spawn/despawn is a later
increment). `does_not_show`: the native renderer (layer-3, not gate-able — see
the frontfps README §6), occlusion, culling, any wall-clock property.

GRADE: IMPLEMENTED / MEASURED via the `frontfps_view` gate stage + tests.
Cross-placement SPECULATIVE (queued). Falsifier: any independent implementation
of this docstring disagreeing with the pinned stream digest / byte count.
"""
import hashlib

MAGIC = b"URDRVIW2"
VERSION = 2


class ViewError(Exception):
    def __init__(self, message):
        super().__init__(f"VIEW-REFUSE: {message}")
        self.code = "VIEW-REFUSE"


# ---- the authoritative scene (pinned corpus): a short authored trajectory ----------
# actor = (id, x, y, z, yaw), authoring-grid integers. This is authority content —
# the renderer consumes a projection of it and never writes it back. Three actors
# over four ticks: actor 1 walks +x and turns, actor 2 turns then holds, actor 3
# rises once. A fixed actor set (spawn/despawn is a later increment).
def demo_trajectory():
    return (
        ((1, 0, 0, 0, 0), (2, 100, 0, 0, 512), (3, -40, 0, 20, 256)),
        ((1, 8, 0, 0, 0), (2, 100, 0, 0, 640), (3, -40, 0, 20, 256)),
        ((1, 16, 0, 0, 0), (2, 100, 0, 0, 640), (3, -40, 0, 28, 256)),
        ((1, 24, 0, 0, 96), (2, 100, 0, 0, 640), (3, -40, 0, 28, 256)),
    )


def _i32(v):
    """Signed 32-bit, big-endian — the one integer wire type."""
    return int(v).to_bytes(4, "big", signed=True)


def authority_witness(snapshot):
    """SHA-256 over the AUTHORITATIVE actor state (raw, unquantized), in the
    authored order. A pure function of authority — presentation never enters."""
    h = hashlib.sha256()
    h.update(b"URDRVIW2-AUTH")
    for actor in snapshot:
        for c in actor:
            h.update(_i32(c))
    return h.digest()


def _quantize(actor, shift):
    """Presentation projection (display-only LOD): floor-shift the position, keep
    id and yaw. Lossy by construction — this is what makes the view one-way."""
    i, x, y, z, yaw = actor
    return (i, x >> shift, y >> shift, z >> shift, yaw)


def _frame_bytes(ftype, seq, base, wit, rows):
    out = bytearray()
    out += _i32(ftype)
    out += _i32(seq)
    out += _i32(base)
    out += wit                       # 32-byte bound authority witness
    out += _i32(len(rows))
    for r in rows:
        for c in r:
            out += _i32(c)
    return bytes(out)


def _header(nframes, shift):
    return MAGIC + _i32(VERSION) + _i32(nframes) + _i32(shift)


def encode_stream(trajectory, shift, _wit_of=None):
    """Encode an authored trajectory into a URDR-FPSW-VIEW-2 byte stream: one
    keyframe then delta frames (changed display rows only). The witness bound in
    each frame is the AUTHORITY witness by default; `_wit_of` is an injection
    point used only by the fold defect below."""
    wit_of = _wit_of or (lambda snap, disp: authority_witness(snap))
    out = bytearray(_header(len(trajectory), shift))
    prev = None
    for seq, snap in enumerate(trajectory):
        disp = tuple(_quantize(a, shift) for a in snap)
        wit = wit_of(snap, disp)
        if seq == 0:
            out += _frame_bytes(0, seq, -1, wit, list(disp))
        else:
            changed = [d for d, p in zip(disp, prev) if d != p]
            out += _frame_bytes(1, seq, seq - 1, wit, changed)
        prev = disp
    return bytes(out)


def decode_stream(data):
    """Decode to a list of DISPLAY frames: [(seq, witness_bytes, display_rows)].
    display_rows is quantized and id-sorted — deliberately LOSSY, with no inverse
    to authority. VIEW-REFUSE on a bad magic/version, a delta whose base was never
    decoded, a delta whose base is not strictly earlier, or a stream opening on a
    delta (its base -1 is never present)."""
    if data[:8] != MAGIC:
        raise ViewError("bad magic")
    pos = [8]

    def rd():
        v = int.from_bytes(data[pos[0]:pos[0] + 4], "big", signed=True)
        pos[0] += 4
        return v

    version = rd()
    nframes = rd()
    _shift = rd()
    if version != VERSION:
        raise ViewError(f"unsupported version {version}")
    decoded = {}
    order = []
    for _ in range(nframes):
        ftype = rd()
        seq = rd()
        base = rd()
        wit = bytes(data[pos[0]:pos[0] + 32])
        pos[0] += 32
        n = rd()
        rows = [tuple(rd() for _ in range(5)) for _ in range(n)]
        if ftype == 0:
            frame = {r[0]: r for r in rows}
        elif ftype == 1:
            if base not in decoded:
                raise ViewError(f"delta frame {seq} references base {base} never sent")
            if base >= seq:
                raise ViewError(f"delta frame {seq} references non-earlier base {base}")
            frame = dict(decoded[base])
            for r in rows:
                frame[r[0]] = r
        else:
            raise ViewError(f"unknown frame type {ftype}")
        decoded[seq] = frame
        order.append((seq, wit, tuple(frame[k] for k in sorted(frame))))
    return order


# ---- pinned artifacts -------------------------------------------------------------------
CANON_SHIFT = 4


def stream_digest(trajectory=None, shift=CANON_SHIFT):
    if trajectory is None:
        trajectory = demo_trajectory()
    return hashlib.sha256(encode_stream(trajectory, shift)).hexdigest()


def stream_bytes(trajectory=None, shift=CANON_SHIFT):
    if trajectory is None:
        trajectory = demo_trajectory()
    return len(encode_stream(trajectory, shift))


# ---- law 1: recompute -------------------------------------------------------------------
def recompute_matches(trajectory=None, shift=CANON_SHIFT):
    if trajectory is None:
        trajectory = demo_trajectory()
    a = encode_stream(trajectory, shift)
    if a != encode_stream(trajectory, shift):
        return False
    dec = decode_stream(a)
    if len(dec) != len(trajectory):
        return False
    for (seq, wit, disp), snap in zip(dec, trajectory):
        if wit != authority_witness(snap):
            return False
        want = tuple(sorted((_quantize(x, shift) for x in snap), key=lambda r: r[0]))
        if disp != want:
            return False
    return True


# ---- law 2: no-feedback (witness ⟂ presentation; display is lossy) ----------------------
def witness_invariant_under_presentation(trajectory=None):
    """The bound authority witness is identical across two presentations."""
    if trajectory is None:
        trajectory = demo_trajectory()
    a = [w for _, w, _ in decode_stream(encode_stream(trajectory, 2))]
    b = [w for _, w, _ in decode_stream(encode_stream(trajectory, 6))]
    return a == b


def _wit_fold_presentation(snap, disp):
    """THE DEFECT: bind the witness to the QUANTIZED display, not raw authority."""
    h = hashlib.sha256()
    h.update(b"URDRVIW2-AUTH")
    for actor in disp:
        for c in actor:
            h.update(_i32(c))
    return h.digest()


def defect_folds_presentation_into_witness(trajectory=None):
    """True iff the fold defect makes the witness presentation-dependent — i.e.,
    the defect is real and the no-feedback law can redden."""
    if trajectory is None:
        trajectory = demo_trajectory()
    a = [w for _, w, _ in decode_stream(encode_stream(trajectory, 2, _wit_fold_presentation))]
    b = [w for _, w, _ in decode_stream(encode_stream(trajectory, 6, _wit_fold_presentation))]
    return a != b


def display_is_lossy(shift=CANON_SHIFT):
    """Two DISTINCT authority states inside one quantization bucket collapse to
    the SAME display — so display → authority is not a function (no inverse)."""
    snap_a = ((1, 0, 0, 0, 0),)
    snap_b = ((1, (1 << shift) - 1, 0, 0, 0),)   # same bucket: (2^shift - 1) >> shift == 0
    disp_a = decode_stream(encode_stream((snap_a,), shift))[0][2]
    disp_b = decode_stream(encode_stream((snap_b,), shift))[0][2]
    same_display = disp_a == disp_b
    diff_authority = authority_witness(snap_a) != authority_witness(snap_b)
    return same_display and diff_authority


# ---- malformed streams (the refusal surface) -------------------------------------------
def demo_stream_missing_base():
    """Keyframe(0) + delta(1) referencing base 99 (never sent) — VIEW-REFUSE."""
    traj = demo_trajectory()
    s0, s1 = traj[0], traj[1]
    d0 = tuple(_quantize(a, CANON_SHIFT) for a in s0)
    d1 = tuple(_quantize(a, CANON_SHIFT) for a in s1)
    changed = [d for d, p in zip(d1, d0) if d != p]
    out = bytearray(_header(2, CANON_SHIFT))
    out += _frame_bytes(0, 0, -1, authority_witness(s0), list(d0))
    out += _frame_bytes(1, 1, 99, authority_witness(s1), changed)
    return bytes(out)


def demo_stream_delta_first():
    """A stream that opens on a delta (base -1 never present) — VIEW-REFUSE."""
    traj = demo_trajectory()
    s0 = traj[0]
    d0 = tuple(_quantize(a, CANON_SHIFT) for a in s0)
    out = bytearray(_header(1, CANON_SHIFT))
    out += _frame_bytes(1, 0, -1, authority_witness(s0), list(d0))
    return bytes(out)


def demo_stream_bad_magic():
    return b"URDRXXXX" + encode_stream(demo_trajectory(), CANON_SHIFT)[8:]


if __name__ == "__main__":
    print("stream digest:", stream_digest())
    print("stream bytes :", stream_bytes())
    print("recompute    :", recompute_matches())
    print("witness inv. under presentation:", witness_invariant_under_presentation())
    print("fold defect bites              :", defect_folds_presentation_into_witness())
    print("display is lossy               :", display_is_lossy())
    for name, fn in (("missing-base", demo_stream_missing_base),
                     ("delta-first", demo_stream_delta_first),
                     ("bad-magic", demo_stream_bad_magic)):
        try:
            decode_stream(fn())
            print(f"REFUSAL {name}: NOT refused (BUG)")
        except ViewError as e:
            print(f"REFUSAL {name}: {e.code}")
    print("valid decodes frames:", len(decode_stream(encode_stream(demo_trajectory(), CANON_SHIFT))))
