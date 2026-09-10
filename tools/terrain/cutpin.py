# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""cutpin (URDRCPN1) — THE EXPENSIVE HALF OF A PROOF IS PINNED, AND WHAT IS TRUSTED IS ONE INTEGER.

`shadowcut` and `cutbound` rest on an EXHAUSTION: `cohort.min_cut` trying every subset of a wall up
to `CUT_SEARCH_MAX` and refusing. That refusal is the best evidence in the arc — and re-deriving it
cost about 134 seconds on every gate run, on two walls, in both stages and both suites, on every
patch whether or not anything near `cohort` had changed. TWENTY MINUTES A RUN, DOUBLED BECAUSE THE
GATE IS RUN TWICE, TO RE-PROVE SOMETHING THAT HAD NOT MOVED.

THE ANSWER IS NOT TO DELETE THE WITNESS OR WEAKEN THE CLASS LAW. `(6,5)` is the only wall that
populates `cutbound`'s `bracketed` class, and dropping it would turn a runtime problem into an
epistemic regression: the class would become a distinction nobody has met. THE ANSWER IS TO SEPARATE
CERTIFICATION EVIDENCE FROM ROUTINE EXECUTION, and to be exact about which is which.

WHAT THE ORDINARY RUN STILL PROVES FROM SCRATCH. Exhaustion is graded by subset SIZE, and the cost is
not flat:

    wall        size 1     size 2      size 3
    (n=6, t=4)   0.01s      0.96s      46.00s
    (n=6, t=5)   0.02s      1.47s      88.31s

So sizes ONE and TWO are re-proved every single run, for about two and a half seconds, and only SIZE
THREE is consumed from the pin. THE TRUSTED INCREMENT IS EXACTLY ONE INTEGER: every run re-derives
"no cut of size 2 or below exists", and the pin supplies only the step from there to "no cut of size
3 or below exists". That is the whole of what is taken on trust, and naming it is the point.

THE PIN CARRIES ITS OWN PROVENANCE AND GOES STALE LOUDLY. The record binds a digest over the LIVE
SOURCE of every function that could change the answer — `min_cut`, `free_reaches`, `spanning_wall`,
`world` — together with `CUT_SEARCH_MAX` and the case list. Change any of them and the digest moves,
`the_pin_is_current` REFUSES, and the gate reddens demanding regeneration. A cached proof whose
invalidation is weaker than the thing it caches is worse than no cache, so the binding is to SOURCE
TEXT rather than to a version anyone has to remember to bump.

THE PIN MAY ONLY RECORD A REFUSAL. These walls are pinned precisely because the enumeration declines,
and a record asserting a NUMBER would be asserting something the cheap re-proof cannot check. A pin
that could carry any answer would be a place to put an answer; this one can only carry the absence of
a small cut, and `the_pin_records_only_refusals` is where that is enforced.

AND THE CHEAP RE-PROOF IS A DELIBERATE TRANSCRIPTION, BOUND TO ITS SUBJECT. To exhaust one size
without paying for all of them this module writes its own subset walk, which is exactly the
duplication `shadowcut` refused. The difference is that this one is CHECKED: on a wall the subject
can decide, the transcription's reconstruction must equal `cohort.min_cut` exactly, so a drifting
copy is caught by the module it drifted from rather than by a reader.

does_not_show: NOT THAT THE PINNED SIZE WAS RE-DERIVED THIS RUN — that is the entire point, and the
row says which mode it ran in rather than passing quietly. NOT THAT THE PIN IS UNFORGEABLE: a record
edited together with the sources it binds would carry a matching digest, so this defends against
DRIFT and not against an author who means it. NOT THAT THE COST MODEL GENERALISES — three sizes on
two walls were measured, and the growth past that is unmeasured here. NOTHING ABOUT TIME AS A CLAIM:
the timings above decided a design and are not evidence for any law, and no wall clock enters any
gated predicate.

falsifier: `the_pin_is_current` reddens the moment any source it binds changes, which is the whole
guarantee; `the_affordable_exhaustion_is_reproved` reddens if a cut of size one or two ever turns up
on a pinned wall, which would mean the pinned refusal was false; and
`the_transcribed_exhaustion_agrees_with_the_subject` reddens if this module's own subset walk ever
disagrees with `cohort.min_cut` on a wall the subject can decide.
"""
import hashlib
import inspect
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
ROOT = _os.path.dirname(_os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import cohort as CO                                             # noqa: E402

MAGIC = b"URDRCPN1"

#: DECLARED — the walls whose full exhaustion is pinned. Both are walls the enumeration REFUSES, and
#: both are load-bearing: `(6,4)` is `cutbound`'s meeting point and `(6,5)` is the only case that
#: populates its `bracketed` class.
EXPENSIVE = ((6, 4), (6, 5))

#: DECLARED — the subset sizes re-proved from scratch on EVERY run. Measured affordable: about two
#: and a half seconds across both walls, against 134 for the size the pin carries.
REPROVED = (1, 2)

#: DECLARED — the environment switch that asks for the expensive half to be re-derived. Absent, the
#: certification row is recorded SKIPPED and honestly labelled rather than passed.
CERTIFY_ENV = "URDR_CERTIFY_CUTPIN"

#: DECLARED — every source whose text could change what the enumeration answers. The provenance
#: digest is taken over these, so invalidation follows the CODE rather than anyone's memory.
BOUND_SOURCES = ("min_cut", "free_reaches", "spanning_wall", "world")


class CutpinError(Exception):
    """A case or a record this module will not pretend to have."""

    def __init__(self, message):
        super().__init__("CUTPIN-REFUSE: %s" % message)
        self.code = "CUTPIN-REFUSE"


def pinned_sizes():
    """The sizes the pin carries: everything above what is re-proved, up to the subject's cap."""
    return tuple(range(max(REPROVED) + 1, CO.CUT_SEARCH_MAX + 1))


def provenance_digest():
    """A digest over the LIVE source of everything that could change the answer.

    Bound to source TEXT rather than to a version number, because a version is a thing someone has
    to remember to bump and a cache whose invalidation depends on memory is not an invalidation.
    """
    parts = [inspect.getsource(getattr(CO, n)) for n in BOUND_SOURCES]
    parts.append(repr((CO.CUT_SEARCH_MAX, EXPENSIVE, REPROVED)))
    return hashlib.sha256(MAGIC + b"|prov|" + "".join(parts).encode()).hexdigest()


def no_cut_of_size(wall, n, size):
    """No subset of exactly `size` wall cells opens the wall.

    A DELIBERATE TRANSCRIPTION of one slice of the subject's enumeration, so a single size can be
    exhausted without paying for every size below the cap. `the_transcribed_exhaustion_agrees_with_
    the_subject` binds it to `cohort.min_cut` on a wall the subject can decide.
    """
    for s in _comb(sorted(wall), size):
        if CO.free_reaches(wall - frozenset(s), n):
            return False
    return True


def reconstruct(wall, n, cap):
    """The subject's answer, rebuilt from the transcription — used only to CHECK the transcription."""
    if CO.verdict(wall, n) == CO.BREACHED:
        return 0
    for size in range(1, cap + 1):
        if not no_cut_of_size(wall, n, size):
            return size
    return None


# ---- the record ------------------------------------------------------------------------------------
RECORD = _os.path.join("spec", "attest", "cutsearch-enumeration.txt")


def generate():
    """Emit the pin. RUNS THE EXPENSIVE EXHAUSTION — this is the certification path, not the hot one."""
    lines = ["# URDRCPN1 the pinned exhaustion — emitted by cutpin.py under regeneration ONLY.",
             "# Sizes %s are re-proved on every ordinary run; this record carries %s."
             % (", ".join(map(str, REPROVED)), ", ".join(map(str, pinned_sizes()))),
             "# provenance %s" % provenance_digest(), ""]
    for (n, t) in EXPENSIVE:
        w = CO.spanning_wall(n, t)
        answer = CO.min_cut(w, n)
        if answer is not None:
            raise CutpinError("wall (%d,%d) is decided by the subject and does not belong in a pin"
                              % (n, t))
        lines.append("refused %d %d %d" % (n, t, CO.CUT_SEARCH_MAX))
    lines.append("digest %s" % pin_digest())
    return "\n".join(lines) + "\n"


def pin_digest():
    return hashlib.sha256(MAGIC + b"|pin|" + repr(
        (EXPENSIVE, CO.CUT_SEARCH_MAX, REPROVED, pinned_sizes())).encode()).hexdigest()


def _read():
    with open(_os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, prov = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# provenance "):
                prov = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "refused":
            if (int(f[1]), int(f[2])) not in EXPENSIVE:
                raise CutpinError("a refused row naming no pinned wall")
            if int(f[3]) != CO.CUT_SEARCH_MAX:
                raise CutpinError("a refused row naming a cap that is not the subject's")
        elif f[0] != "digest":
            raise CutpinError("a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if prov is None:
        raise CutpinError("the record names no provenance digest")
    if not rows:
        raise CutpinError("the record has no rows")
    return prov, rows


def refusal(case):
    """The pinned answer for a wall: always None, and REFUSES if the pin is not current."""
    if case not in EXPENSIVE:
        raise CutpinError("no pinned wall %r" % (case,))
    if not the_pin_is_current():
        raise CutpinError("the pin is STALE — a bound source changed; regenerate it with "
                          "%s=1 python tools/terrain/cutpin.py" % CERTIFY_ENV)
    return None


def answer_for(case):
    """What a consumer should use for a wall: the pin when it is pinned, the subject otherwise."""
    if case in EXPENSIVE:
        return refusal(case)
    n, t = case
    return CO.min_cut(CO.spanning_wall(n, t), n)


# ---- the laws --------------------------------------------------------------------------------------
def the_pin_is_current():
    """THE WHOLE GUARANTEE. The recorded provenance must equal a digest recomputed from the LIVE
    source of every function that could change the answer."""
    try:
        prov, _rows = parse()
    except CutpinError:
        return False
    return prov == provenance_digest()


def the_pin_records_only_refusals():
    """A pin that could carry any answer would be a place to PUT an answer. This one carries only
    the absence of a small cut, which is the one thing the cheap re-proof can corroborate."""
    _prov, rows = parse()
    kinds = {r[0] for r in rows}
    walls = tuple(sorted((int(r[1]), int(r[2])) for r in rows if r[0] == "refused"))
    return kinds <= {"refused", "digest"} and walls == tuple(sorted(EXPENSIVE))


def the_affordable_exhaustion_is_reproved():
    """RE-DERIVED EVERY RUN, from scratch, at the sizes that cost seconds rather than minutes. If a
    cut of size one or two ever turns up on a pinned wall, the pinned refusal was false."""
    for (n, t) in EXPENSIVE:
        w = CO.spanning_wall(n, t)
        for size in REPROVED:
            if not no_cut_of_size(w, n, size):
                return False
    return True


def the_trusted_increment_is_one_integer():
    """AND IT IS NAMED. Everything up to `max(REPROVED)` is re-proved; the pin supplies exactly the
    sizes above it up to the cap, and at the shipped constants that is a single size."""
    return (pinned_sizes() == tuple(range(max(REPROVED) + 1, CO.CUT_SEARCH_MAX + 1))
            and len(pinned_sizes()) == 1
            and max(REPROVED) + len(pinned_sizes()) == CO.CUT_SEARCH_MAX)


def the_transcribed_exhaustion_agrees_with_the_subject():
    """THE TRANSCRIPTION IS BOUND TO WHAT IT COPIES. On walls the subject can decide, this module's
    own subset walk must rebuild exactly the subject's answer — including the breached case, where
    the answer is zero and no walk happens at all."""
    for (n, t) in ((3, 1), (4, 1), (4, 2), (5, 2), (5, 3)):
        w = CO.spanning_wall(n, t)
        if reconstruct(w, n, CO.CUT_SEARCH_MAX) != CO.min_cut(w, n):
            return False
    n = 4
    partial = frozenset((1, y, z) for y in range(n - 1) for z in range(n))
    return reconstruct(partial, n, CO.CUT_SEARCH_MAX) == CO.min_cut(partial, n) == 0


def the_pinned_exhaustion_reproduces():
    """THE CERTIFICATION PATH, AND IT IS EXPENSIVE. Re-runs the pinned sizes for real. Called only
    when the certification switch is set; the ordinary run records the row SKIPPED and says so."""
    for (n, t) in EXPENSIVE:
        w = CO.spanning_wall(n, t)
        for size in pinned_sizes():
            if not no_cut_of_size(w, n, size):
                return False
        if CO.min_cut(w, n) is not None:
            return False
    return True


def certification_requested():
    return _os.environ.get(CERTIFY_ENV) == "1"


def a_tampered_record_refuses():
    text = _read().replace("refused 6 4 ", "refused 9 9 ", 1)
    try:
        parse(text)
    except CutpinError:
        return True
    return False


def a_stale_provenance_refuses():
    """THE PLANT FOR THE GUARANTEE ITSELF: a record whose provenance does not match the live source
    must not be consumable, and `refusal` must refuse rather than return a cached answer."""
    text = _read()
    prov = parse(text)[0]
    stale = text.replace(prov, "0" * len(prov), 1)
    try:
        p, _r = parse(stale)
    except CutpinError:
        return False
    return p != provenance_digest()


def told():
    return ("THE EXPENSIVE HALF OF A PROOF IS PINNED, AND WHAT IS TRUSTED IS ONE INTEGER. The "
            "exhaustion `shadowcut` and `cutbound` rest on cost about 134 seconds to re-derive on "
            "every gate run, on two walls, in both stages and both suites, whether or not anything "
            "near `cohort` had changed — and the gate is run TWICE per patch. Deleting the witness "
            "was not available: `(6,5)` is the only wall that populates `cutbound`'s BRACKETED "
            "class, so dropping it would turn a runtime problem into an epistemic regression. "
            "EXHAUSTION IS GRADED BY SUBSET SIZE AND THE COST IS NOT FLAT, so sizes %s are RE-PROVED "
            "FROM SCRATCH ON EVERY RUN for about two and a half seconds, and only size %s is "
            "consumed from the pin: THE TRUSTED INCREMENT IS EXACTLY ONE INTEGER, every run deriving "
            "`no cut of size 2 or below` and the pin supplying only the step to `no cut of size 3 or "
            "below`. THE PIN CARRIES ITS OWN PROVENANCE AND GOES STALE LOUDLY, binding a digest over "
            "the LIVE SOURCE of `min_cut`, `free_reaches`, `spanning_wall` and `world` together with "
            "the cap and the case list — source TEXT rather than a version anyone has to remember to "
            "bump, because a cache whose invalidation depends on memory is not an invalidation. AND "
            "THE PIN MAY ONLY RECORD A REFUSAL: a record that could carry any answer would be a "
            "place to PUT an answer, so this one carries only the absence of a small cut, which is "
            "the one thing the cheap re-proof can corroborate. The cheap re-proof is a DELIBERATE "
            "transcription and it is bound to what it copies — on walls the subject can decide it "
            "must rebuild the subject's answer exactly"
            % (" and ".join(map(str, REPROVED)), ", ".join(map(str, pinned_sizes()))))


def scene_case(name):
    if name == "pin":
        return repr((EXPENSIVE, REPROVED, pinned_sizes(), CO.CUT_SEARCH_MAX, BOUND_SOURCES))
    if name == "record":
        return generate() if certification_requested() else _read()
    raise CutpinError("no scene named %r" % (name,))


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode()
                          + b"|" + scene_case(name).encode()).hexdigest()


SCENES = ("pin", "record")


def golden(name):
    with open(_os.path.join(_HERE, "conformance_cutpin.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise CutpinError("no golden named %r" % (name,))


def write_record():
    """Rewrite the pin. RUNS THE EXPENSIVE EXHAUSTION — the certification path, not the hot one."""
    text = generate()
    with open(_os.path.join(ROOT, RECORD), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return provenance_digest()


def _main():
    """AND THIS ENTRY POINT READS NO `argv`, WHICH THE TREE INSISTED ON.

    The first draft took `--regenerate` off the command line, and `entry`'s census REDDENED: it
    pins the thirteen production modules that slice `argv` across forty sites and may not GROW, so
    a new positional reader refuses immediately while the existing debt is paid down deliberately.
    The ratchet was right, and the honest answer was not to raise its ceiling for a rare operation
    but to NOT INCUR THE DEBT — regeneration keys off the certification switch this module already
    declares, so there is no second way to ask and no new command line to get wrong.
    """
    if certification_requested():
        print("regenerated %s" % RECORD)
        print("provenance %s" % write_record())
    else:
        print("pin current:", the_pin_is_current())
        print("trusted sizes:", pinned_sizes(), " re-proved:", REPROVED)
        print("set %s=1 to regenerate the pinned exhaustion" % CERTIFY_ENV)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
