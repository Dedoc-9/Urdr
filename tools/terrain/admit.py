# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""admit (URDRADM1) — THE INSTRUMENT REPORTS; THE GATE ADJUDICATES.

A REPLAY THAT ENDED EARLY LOOKED EXACTLY LIKE A REPLAY THAT ENDED. `ab_off_a` consumed 2479 of
its trace's 2564 frames and printed a record identical in shape to a finished one — same header,
same segments, same digest section, no marker anywhere. It was caught only because three runs
were compared by hand, and the shape of that catch does not scale: the next one would be found
by whoever happened to notice, or not at all. That is L85 one level up — a condition sampled
once is an assumption that it held throughout, and a RUN ASSUMED COMPLETE is the same mistake
about the whole run.

fpsdemo v1.15 emits the conditions and their conjunction. This module is the OTHER HALF, and the
split is the point. The instrument reports `replay_status`; this reader RECOMPUTES the predicates
from the record's own fields and compares. Agreement admits or rejects. DISAGREEMENT is a third
and more serious verdict, because it means the producer's contract and the reader's have drifted
apart — the failure where both halves are individually green and the pair is lying. A reader that
merely checked the string `COMPLETE` was present would have recreated the original defect one
layer up, and this module would be the thing certifying it.

THE NEUTRAL RULER, at the trace layer. `replay_frames n/expected` is only meaningful if
`expected` is not derived from the same possibly-damaged file: a partial write shrinks a
row-count ruler to fit the workload and the run reports complete. v1.15 traces DECLARE their
length (`# frames N`) and the loader refuses a declaration that disagrees with its rows, so
`expected` comes from the declaration. `replay_declared legacy` names a trace written before the
contract, and naming it is what keeps it from passing as a measured quantity.

TWO IDENTITIES, NOT ONE (worldbind's split, S19). `replay_trace ... bytes <sha>` is PROVENANCE —
which artifact was this. `replay_workload sha256 <sha>` is IDENTITY — which motion is this, taken
over the canonical rows so line endings and whitespace cannot move it. A before/after pair is
comparable when its WORKLOAD digests agree; comparing bytes would refuse a legitimate pair the
first time a trace crossed a filesystem, and this repository's own `.gitattributes` says
`* text=auto eol=lf`.

THE EXEMPTION IS FINITE AND NAMED. Every record committed before v1.15 predates the contract, so
a reader refusing anything not marked COMPLETE would refuse the whole corpus on its first run.
Records stamped BELOW `COMPLETENESS_INTRO` are LEGACY-ADMITTED and COUNTED; records at or above
must carry the contract whole. The count is reported rather than assumed away, so the exemption
can be retired when it reaches zero instead of quietly becoming permanent (L68).

`does_not_show`: that an ADMITTED record's NUMBERS are right, that its host declaration is true,
or that two admitted records measured the same thing — only that this record states its own
completeness and that its statement survives recomputation. `admitted != correct`.
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import versionarc as VA                                          # noqa: E402  (the version extractor, IMPORTED)

ROOT = VA.ROOT
ATTEST = VA.ATTEST

#: The version that introduced the contract. A record stamped below it is exempt BY VERSION,
#: which is `probelog`'s precedent (a v0 log refuses by version discipline) rather than a note.
COMPLETENESS_INTRO = "v1.15"

#: The measurement classes and the conditions each declares. DATA, not an `if` ladder: a future
#: class is a row, and a future condition is a named predicate in an existing row.
CLASS_CONDITIONS = {
    "replay": ("frames", "focus"),
    "play": (),
}


class AdmitError(Exception):
    """ADMIT-REFUSE — a record whose contract fields are present but unreadable."""


def _cmp_version(a, b):
    ka, kb = VA._key(a), VA._key(b)
    return (ka > kb) - (ka < kb)


def parse_record(text):
    """The contract fields, read from a record's own bytes. Absent fields stay absent."""
    rec = {}
    m = re.search(r"\bfpsdemo (" + VA.VERSION + r")\b", text)
    if m:
        rec["version"] = m.group(1)
    m = re.search(r"(?m)^measurement_class (\w+)$", text)
    if m:
        rec["class"] = m.group(1)
    m = re.search(r"(?m)^replay_frames (\d+)/(\d+)$", text)
    if m:
        rec["frames"] = (int(m.group(1)), int(m.group(2)))
    m = re.search(r"(?m)^replay_focus (\d+)/(\d+)$", text)
    if m:
        rec["focus"] = (int(m.group(1)), int(m.group(2)))
    m = re.search(r"(?m)^replay_status (COMPLETE|INCOMPLETE)", text)
    if m:
        rec["status"] = m.group(1)
    m = re.search(r"(?m)^replay_workload sha256 ([0-9a-f]{64})$", text)
    if m:
        rec["workload"] = m.group(1)
    m = re.search(r"(?m)^replay_trace (\S+) bytes ([0-9a-f]{64})$", text)
    if m:
        rec["trace"] = (m.group(1), m.group(2))
    m = re.search(r"(?m)^replay_declared (\d+|legacy)$", text)
    if m:
        rec["declared"] = m.group(1)
    return rec


def recompute(rec):
    """THE READER'S OWN PREDICATES. Derived from the record's fields, never from its verdict."""
    if "frames" not in rec or "focus" not in rec:
        raise AdmitError("ADMIT-REFUSE: cannot recompute without frames and focus")
    consumed, expected = rec["frames"]
    focused, of = rec["focus"]
    # focus is counted against CONSUMED, not against expected: a run that stopped early was
    # watched for as long as it ran, and conflating the two would hide one failure behind the other.
    return consumed == expected, focused == of and of == consumed


def adjudicate(rec):
    """ADMITTED / REJECTED / DISAGREEMENT / LEGACY-ADMITTED / CONTRACT-MISSING / NOT-A-MEASUREMENT."""
    ver = rec.get("version")
    if ver is None:
        return "NOT-A-MEASUREMENT"                 # no fpsdemo banner: not this door's business
    if _cmp_version(ver, COMPLETENESS_INTRO) < 0:
        return "LEGACY-ADMITTED"
    cls = rec.get("class")
    if cls is None:
        return "CONTRACT-MISSING"
    if not CLASS_CONDITIONS.get(cls):
        return "NOT-A-MEASUREMENT"                 # `play` declares no completeness conditions
    for field in ("frames", "focus", "status", "workload", "trace", "declared"):
        if field not in rec:
            return "CONTRACT-MISSING"
    frames_ok, focus_ok = recompute(rec)
    derived = "COMPLETE" if (frames_ok and focus_ok) else "INCOMPLETE"
    if derived != rec["status"]:
        return "DISAGREEMENT"
    return "ADMITTED" if derived == "COMPLETE" else "REJECTED"


def corpus(attest=None):
    """(filename, verdict, version) for every committed record, in a fixed order."""
    d = os.path.join(ROOT, attest or ATTEST)
    out = []
    for fname in VA.corpus_files(attest):
        try:
            with open(os.path.join(d, fname), encoding="utf-8") as fh:
                text = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        rec = parse_record(text)
        out.append((fname, adjudicate(rec), rec.get("version")))
    return out


def census(attest=None):
    c = {}
    for _f, verdict, _v in corpus(attest):
        c[verdict] = c.get(verdict, 0) + 1
    return c


def told(attest=None):
    c = census(attest)
    return ", ".join("%s %d" % (k, c[k]) for k in sorted(c))


# ---- the pinned scene ----------------------------------------------------------------------
MAGIC = b"URDRADM1"


def scene_case(name):
    """THE SCENE HASHES THE VERDICT SET, NOT THE COUNTS.

    Counts move every time any record is committed, which would make the pin a tax on unrelated
    rungs and then noise. The SET of verdicts present moves only when the corpus acquires a kind
    of record it did not have — the first record under the contract, or the first refusal — and
    those are exactly the moments a human should be made to look.
    """
    if name == "verdicts":
        seen = sorted({v for _f, v, _ver in corpus()})
        return repr((COMPLETENESS_INTRO, sorted(CLASS_CONDITIONS.items()), seen))
    raise AdmitError("ADMIT-REFUSE: no scene named %r" % name)


def scene_result(name):
    import hashlib
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def golden(name):
    with open(os.path.join(_HERE, "conformance_admit.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise AdmitError("ADMIT-REFUSE: no golden named %r" % name)


# ---- the laws ------------------------------------------------------------------------------
def no_committed_record_is_refused():
    """Every record either passes the contract or is exempt by version. Nothing is REJECTED,
    DISAGREEING or missing its contract."""
    bad = [(f, v) for f, v, _ in corpus() if v in ("REJECTED", "DISAGREEMENT", "CONTRACT-MISSING")]
    return not bad


def the_exemption_is_finite_and_counted():
    """L68: an exemption that nobody counts becomes permanent. This reports the remaining legacy
    records so the boundary can be RETIRED when it reaches zero, rather than outliving its
    reason. It does NOT claim the count is small."""
    return census().get("LEGACY-ADMITTED", 0) > 0


def the_class_table_is_not_vacuous():
    return bool(CLASS_CONDITIONS) and any(CLASS_CONDITIONS.values()) \
        and any(not v for v in CLASS_CONDITIONS.values())


def the_version_extractor_is_imported():
    """ONE IMPLEMENTATION. `versionarc` owns version extraction; a private second copy here is
    how the two drift, and the drift would be invisible because both would still parse."""
    return VA.VERSION is not None and hasattr(VA, "_key")


# ---- the plants ----------------------------------------------------------------------------
_HDR = "fpsdemo v1.15 | host H | power P | scheduler S\n"


def _rec(frames, focus, status, extras=True, cls="replay", hdr=_HDR):
    t = hdr + "measurement_class %s\n" % cls
    if extras:
        t += "replay_trace w.txt bytes %s\n" % ("a" * 64)
        t += "replay_workload sha256 %s\n" % ("b" * 64)
        t += "replay_declared %d\n" % frames[1]
    t += "replay_frames %d/%d\nreplay_focus %d/%d\nreplay_status %s\n" % (
        frames[0], frames[1], focus[0], focus[1], status)
    return parse_record(t)


def a_truncated_replay_is_rejected():
    """`ab_off_a`'s exact shape: 2479 of 2564, honestly reported."""
    return adjudicate(_rec((2479, 2564), (2478, 2479), "INCOMPLETE (frames)")) == "REJECTED"


def a_lying_verdict_is_caught():
    """THE ONE THAT MATTERS. Truncated frames with COMPLETE printed beside them — a reader that
    checked only for the word would have admitted this and recreated the defect one layer up."""
    return adjudicate(_rec((2479, 2564), (2479, 2479), "COMPLETE")) == "DISAGREEMENT"


def a_lost_focus_frame_is_rejected():
    """The second condition, alone: every frame consumed, one drawn to a background window."""
    return adjudicate(_rec((2564, 2564), (2563, 2564), "INCOMPLETE (focus)")) == "REJECTED"


def a_complete_run_is_admitted():
    """NON-VACUITY: the strictness must not refuse everything."""
    return adjudicate(_rec((2564, 2564), (2564, 2564), "COMPLETE")) == "ADMITTED"


def a_current_record_without_the_contract_refuses():
    """A v1.15 record that simply omits the fields is CONTRACT-MISSING, never admitted."""
    return adjudicate(parse_record(_HDR)) == "CONTRACT-MISSING"


def a_legacy_record_is_exempt_by_version():
    """And a v1.14 record with no contract at all is admitted BY VERSION, with a reason."""
    old = "fpsdemo v1.14 | host H | power P | scheduler S\n"
    return adjudicate(parse_record(old)) == "LEGACY-ADMITTED"


def a_play_record_carries_no_completeness_verdict():
    return adjudicate(_rec((1, 1), (1, 1), "COMPLETE", cls="play")) == "NOT-A-MEASUREMENT"


def the_boundary_is_load_bearing():
    """Move the intro version above a current record and it stops being current — the exemption
    is doing work, not decorating. (L61: an exemption nobody can see bite is not measured.)"""
    global COMPLETENESS_INTRO
    keep = COMPLETENESS_INTRO
    try:
        COMPLETENESS_INTRO = "v99.0"
        return adjudicate(parse_record(_HDR)) == "LEGACY-ADMITTED"
    finally:
        COMPLETENESS_INTRO = keep


if __name__ == "__main__":                                       # pragma: no cover
    print(told())
    for f, v, ver in corpus():
        if v != "NOT-A-MEASUREMENT":
            print("%-44s %-16s %s" % (f, v, ver))
