# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""observe (URDRFBR1) — THE OBJECT BESIDE THE DIGEST, AND ONLY ONE CLAIM MADE OF IT.

THE QUESTION. A replay folds an input word into a state and renders it. Two frames with the same
framebuffer digest — is that because the state repeated, or because the render map threw
something away? The chain has only ever been an IDENTITY instrument here; nobody had looked at
what it identifies.

THE INSTRUMENT. `fibre_build.py` slices the demo between the exact-integer helpers and the
entry door — every renderer, the clipper, the digest, the trace loader, unedited — and appends a
replay main that emits THE OBJECT beside the digest at EVERY frame rather than every sixtieth.
The object is read out of the code, not chosen: `step_cam`'s camera `(px, py, q, pitch_acc)`,
plus the wanderer's `av_state` and its elapsed frames since the last transition, because
`av_start = frame` is what makes concatenating two trace segments legal at all.

WHAT THIS GATE ROW CERTIFIES, AND IT IS DELIBERATELY NARROW: every checkpoint of the committed
HOST record is reproduced by the committed CONTAINER record, on a different operating system and
compiler. That is a cross-placement reproduction claim of exactly the kind this tree already
makes, and nothing more. The transcribed main is a SECOND IMPLEMENTATION of the demo's per-frame
sequence and could drift from it; the 43-checkpoint reproduction is what would catch that, which
is why the reproduction is the claim and everything else is output.

WHAT IS REPORTED RATHER THAN ASSERTED — the census, derived from the record's own bytes at claim
time (L75), stated because it is interesting and NOT promoted to an invariant:

  * 2564 frames, 2564 DISTINCT objects, 2309 distinct digests.
  * 31 digest classes contain more than one object.
  * 29 of them differ in the clip phase alone; 2 also differ in `qw`/`qz`.
  * Coarsening the object by forgetting phase produces 7 coarse states carrying MORE THAN ONE
    digest — so phase CANNOT be declared semantically irrelevant, and the tempting structural
    quotient is refuted by the corpus rather than argued away.

WHAT THE CENSUS MEANS, STATED CAREFULLY. Inspecting the two orientation classes shows a camera
standing still at one tile while the quaternion drifts by ONE ULP per frame, some of those frames
rendering identically and some not. So the equivalence here is not `forget a coordinate`. It is
the fibres of the render map: state advances in increments so small that the framebuffer changes
only when one of them pushes a projected vertex across a pixel boundary. RENDER-INDUCED
OBSERVATIONAL EQUIVALENCE is the honest name — not a kernel, because no group or linear structure
has been demonstrated, and not a projection, because it forgets no nameable field uniformly.

`does_not_show`, and each of these is a door someone will want to walk through:
  * that the digest is INJECTIVE on the object. It is a finite fingerprint of a framebuffer —
    the demo's own header calls it a divergence detector, never an attestation. Equal object
    implies equal digest; equal digest implies nothing.
  * that equal objects yield equal digests. All 2564 objects here are DISTINCT, so that converse
    is UNTESTED on this corpus rather than passed, and `full_state_equality_is_unobserved` says
    so in a falsifier instead of leaving the silence to be read as a result.
  * anything about a walk other than this one, a reach other than 60, a resolution other than
    720p, or a configuration with the castle on.
"""
import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import versionarc as VA                                          # noqa: E402

ROOT = VA.ROOT
MAGIC = b"URDRFBR1"
OBSERVED = os.path.join("spec", "attest", "fpsdemo-fibre-r60-off.txt")
HOST = os.path.join("spec", "attest", "fpsdemo-castle-r60-off-b.txt")
FIELDS = ("px", "py", "qw", "qx", "qy", "qz", "pitch", "av", "phase")


class FibreError(Exception):
    """FIBRE-REFUSE — a record that cannot carry the claim made of it."""


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def rows(text=None):
    """(frame, digest, object) per frame, in file order. The object is a tuple of strings —
    compared, never arithmetic'd, so no parsing decision can quietly normalise two states
    into one."""
    out = []
    for ln in (text if text is not None else _read(OBSERVED)).splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        p = s.split()
        if len(p) != 2 + len(FIELDS):
            raise FibreError("FIBRE-REFUSE: row wants frame, digest and %d state fields: %r"
                               % (len(FIELDS), s))
        out.append((int(p[0]), p[1], tuple(p[2:])))
    if not out:
        raise FibreError("FIBRE-REFUSE: the observation record is empty")
    return out


def host_checkpoints(text=None):
    t = text if text is not None else _read(HOST)
    return {int(a): b for a, b in
            re.findall(r"(?m)^digest frame (\d+) fnv64 ([0-9a-f]{16})$", t)}


# ---- the one claim -------------------------------------------------------------------------
def every_host_checkpoint_is_reproduced(obs_text=None, host_text=None):
    """THE GATE'S CLAIM. Cross-placement: Windows/rustc produced the host record, Linux/rustc
    produced the observation record, same trace and same configuration, and every checkpoint the
    host sealed appears in the container's dense output with the same digest."""
    seen = {f: d for f, d, _o in rows(obs_text)}
    marks = host_checkpoints(host_text)
    if not marks:
        raise FibreError("FIBRE-REFUSE: the host record carries no checkpoints")
    return all(seen.get(f) == d for f, d in marks.items())


def reproduction_count(obs_text=None, host_text=None):
    seen = {f: d for f, d, _o in rows(obs_text)}
    marks = host_checkpoints(host_text)
    return sum(1 for f, d in marks.items() if seen.get(f) == d), len(marks)


# ---- the census, REPORTED --------------------------------------------------------------------
def census(text=None):
    r = rows(text)
    by_digest, by_coarse = {}, {}
    for _f, d, o in r:
        by_digest.setdefault(d, set()).add(o)
        by_coarse.setdefault(o[:-1], set()).add(d)
    classes = {d: v for d, v in by_digest.items() if len(v) > 1}
    phase_only, with_orientation = 0, 0
    for objs in classes.values():
        differing = {FIELDS[i] for i in range(len(FIELDS))
                     if len({o[i] for o in objs}) > 1}
        if differing == {"phase"}:
            phase_only += 1
        else:
            with_orientation += 1
    return {"frames": len(r),
            "objects": len({o for _f, _d, o in r}),
            "digests": len(by_digest),
            "multi_object_digest_classes": len(classes),
            "phase_only": phase_only,
            "beyond_phase": with_orientation,
            "coarse_states_with_many_digests": sum(1 for v in by_coarse.values() if len(v) > 1)}


def told(text=None):
    c = census(text)
    return ("%d frames, %d distinct objects, %d distinct digests; %d digest classes hold more "
            "than one object (%d phase-only, %d beyond phase); forgetting phase leaves %d coarse "
            "states carrying more than one digest"
            % (c["frames"], c["objects"], c["digests"], c["multi_object_digest_classes"],
               c["phase_only"], c["beyond_phase"], c["coarse_states_with_many_digests"]))


def skip_ceiling(text=None):
    """THE ORACLE CEILING FOR TEMPORAL FRAME SKIPPING, reported because it decides whether an
    optimisation is worth designing rather than because anything here depends on it.

    A perfect, free predictor could skip exactly those frames whose framebuffer equals the
    previous frame's. That is an upper bound no conservative bound can beat, and measuring it
    BEFORE building the optimisation is cheaper than building the optimisation. On this corpus
    it is 8.4% — against a near-plane clip that cost 4-7% and was accepted without argument.

    AND IT IS A PROPERTY OF THIS WORKLOAD, not of the renderer. `walk_castle.txt` is a WALKING
    trace: position changes in 83.6% of its frames. A standing or spectating camera would skip
    far more, and quoting 8.4% without the workload attached would be the inflation this ladder
    exists to refuse."""
    r = rows(text)
    same = sum(1 for i in range(1, len(r)) if r[i][1] == r[i - 1][1])
    still = sum(1 for i in range(1, len(r)) if r[i][2][:7] == r[i - 1][2][:7])
    moved = sum(1 for i in range(1, len(r)) if r[i][2][:2] != r[i - 1][2][:2])
    redrew = sum(1 for i in range(1, len(r))
                 if r[i][2][:7] == r[i - 1][2][:7] and r[i][1] != r[i - 1][1])
    run = best = 1
    for i in range(1, len(r)):
        run = run + 1 if r[i][1] == r[i - 1][1] else 1
        best = max(best, run)
    return {"pairs": len(r) - 1, "identical": same, "longest_run": best,
            "pose_unchanged": still, "position_changed": moved,
            "pose_unchanged_but_redrew": redrew}


def the_skip_ceiling_is_below_a_fifth(text=None):
    """A GUARD ON THE REPORT, not a law about renderers. If this corpus ever showed a large
    oracle skip rate the ledger's `designed, ceiling measured, not built` entry would be stale
    and someone should look again. It is here so the entry cannot rot silently."""
    c = skip_ceiling(text)
    return c["identical"] * 5 < c["pairs"]


# ---- the declared boundaries, each as a predicate rather than as a sentence -------------------
def full_state_equality_is_unobserved(text=None):
    """THE CONVERSE IS UNTESTED, NOT PASSED. Every object in this corpus is distinct, so
    `equal object implies equal digest` never gets a chance to fire. Silence is not evidence, and
    this falsifier is what stops the silence being read as one."""
    c = census(text)
    return c["objects"] == c["frames"]


def the_structural_quotient_is_refuted(text=None):
    """Forgetting phase does not yield a well-defined map to digests: some coarse state renders
    two different ways. The tidy quotient `S / irrelevant coordinates` is not available here, and
    the corpus is what says so."""
    return census(text)["coarse_states_with_many_digests"] > 0


def the_equivalence_is_not_vacuous(text=None):
    """If no digest class held two objects, the render map would look injective on this corpus
    and there would be nothing to report (L61)."""
    return census(text)["multi_object_digest_classes"] > 0


def the_digest_is_not_claimed_injective(text=None):
    """Stated as code because a boundary in prose does not travel (L68): there are strictly more
    objects than digests, so the map cannot be injective and no caller may assume it is."""
    c = census(text)
    return c["objects"] > c["digests"]


# ---- the plants ------------------------------------------------------------------------------
def a_flipped_digest_breaks_the_reproduction():
    """The claim must depend on the bytes. Move one checkpoint digest and it must fail."""
    t = _read(OBSERVED)
    marks = host_checkpoints()
    f = sorted(marks)[len(marks) // 2]
    bad = re.sub(r"(?m)^%d %s " % (f, marks[f]), "%d %s " % (f, "0" * 16), t, count=1)
    if bad == t:
        return False
    return not every_host_checkpoint_is_reproduced(obs_text=bad)


def a_missing_frame_breaks_the_reproduction():
    t = _read(OBSERVED)
    marks = host_checkpoints()
    f = sorted(marks)[1]
    bad = re.sub(r"(?m)^%d .*\n" % f, "", t, count=1)
    if bad == t:
        return False
    return not every_host_checkpoint_is_reproduced(obs_text=bad)


def a_hostless_record_refuses():
    try:
        every_host_checkpoint_is_reproduced(host_text="no checkpoints here\n")
    except FibreError:
        return True
    return False


def a_malformed_row_refuses():
    try:
        rows("0 abc 1 2 3\n")
    except FibreError:
        return True
    return False


def an_empty_record_refuses():
    try:
        rows("# only a comment\n")
    except FibreError:
        return True
    return False


# ---- the pinned scene ------------------------------------------------------------------------
def scene_case(name):
    if name == "fibre":
        got, want = reproduction_count()
        return repr((got, want, sorted(census().items()), sorted(skip_ceiling().items())))
    raise FibreError("FIBRE-REFUSE: no scene named %r" % name)


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_fibre.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise FibreError("FIBRE-REFUSE: no golden named %r" % name)


if __name__ == "__main__":                                       # pragma: no cover
    print("%d/%d host checkpoints reproduced" % reproduction_count())
    print(told())
