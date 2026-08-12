# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""deeper — A TIMING DIFFERENCE WITH NO COUNTED DIFFERENCE IS UNEXPLAINED, AND UNEXPLAINED IS A
VERDICT (URDRDPR1). Ousterhout's rule, mechanized against a live instance this arc produced.

THE INSTANCE. Under a balanced schedule the named host reported `moulded` beating `flat` at exactly
one work level — ticks = 8 — in three of four workloads (-5.2%, -2.9%, -5.6%), with `flat` winning
again at 11 and 12 ticks. Three independent workloads agreeing at one point is too orderly to file
as noise and too narrow to explain by hand. And `measure` had already proved, in EXACT COUNTS, that
the three representations share a slope and differ only in the intercept — so a band that appears at
one tick count and vanishes on either side is a difference the op model says CANNOT EXIST.

That leaves exactly two honest possibilities, and the point of this module is to make the tree say
which: either something below the op model differs there, or the band is not real. What is NOT
available is a story.

    MEASURE ONE LEVEL DEEPER, OR RECORD THAT YOU DID NOT.

THE LAW:

    A TIMING DIFFERENCE BETWEEN TWO ARMS AT THE SAME CONDITION IS EXPLAINED ONLY IF SOME COUNTED
    QUANTITY ALSO DIFFERS THERE. WITH NO COUNTED DIFFERENCE, THE VERDICT IS UNEXPLAINED.

Three verdicts, and the third is the one that makes this an instrument rather than an opinion.
EXPLAINED: a counted quantity moves where the time moves. UNEXPLAINED: none does, and the
difference is real in the log and unaccounted for. NOT_ASKED: no counts were carried at all, which
is what every log in this repository has looked like until now and is a different finding from
having looked and found nothing.

WHERE THE COUNTS LIVE, AND WHY NOT HERE. Allocation and collection counts are CPython-version
dependent — this container runs 3.11 and the named host runs 3.14 — so digesting them into a gate
golden would redden the operator's gate for a reason that has nothing to do with the tree. They are
carried in the LOG, beside the timings, under exactly the rule the timings already obey: the FORMAT
and the ADMISSION LAW are on the gate, the NUMBERS are the operator's. This module grades the
reasoning and never the counts.

`does_not_show` — the bound, and it is the honest half. A COUNTED DIFFERENCE IS NOT A CAUSE. If
allocations move where the time moves, that is a correlation across two quantities in the same run,
not a demonstration that one produced the other; establishing that needs an intervention, which is
Mytkowicz's second remedy and is not built here. Nor is the counter list exhaustive: it names
allocated blocks and the three GC generation counts, so a difference living in branch prediction,
cache residency or scheduler placement reads UNEXPLAINED — correctly, because this instrument
cannot see it, and reporting UNEXPLAINED is the accurate statement of that.

GRADE (honest, D5): MEASURED — a fixture where a count moves with the time reads EXPLAINED, one
where no count moves reads UNEXPLAINED, and one carrying no counts at all reads NOT_ASKED, each
planted separately and proved to give different verdicts; the counters are collected through a
differencing probe that is proved to bite on a deliberately allocating callable; the whole
comparison is integer. DECLARED: the counter list, and the rule that a count differs when it
differs at all — no tolerance, because these are exact integers and a tolerance on an exact
quantity is a threshold nobody is watching."""
import hashlib
import os as _os

_HERE = _os.path.dirname(_os.path.abspath(__file__))

MAGIC = b"URDRDPR1"

EXPLAINED = "EXPLAINED"
UNEXPLAINED = "UNEXPLAINED"
NOT_ASKED = "NOT_ASKED"
OUTCOMES = (EXPLAINED, UNEXPLAINED, NOT_ASKED)

#: DECLARED. The quantities carried beside a timing. Exact integers, so equality is equality and no
#: tolerance is applied — a tolerance on an exact count is a threshold nobody is watching.
COUNTERS = ("blocks", "gc0", "gc1", "gc2")


class DeeperError(Exception):
    def __init__(self, message):
        super().__init__(f"DEEPER-REFUSE: {message}")
        self.code = "DEEPER-REFUSE"


# ---- the probe ------------------------------------------------------------------------------------
def counters():
    """A snapshot of the deeper quantities. Version-dependent BY NATURE, which is why nothing here
    ever reaches a gate golden."""
    import gc
    import sys
    g0, g1, g2 = gc.get_count()
    return {"blocks": sys.getallocatedblocks(), "gc0": g0, "gc1": g1, "gc2": g2}


def count_delta(fn, *args, **kwargs):
    """What `fn` cost in counted quantities, by differencing — AND THE RESULT IS HELD ALIVE ACROSS
    THE SECOND SNAPSHOT, which the first draft of this function did not do and which made it read
    zero for a callable allocating five hundred objects.

    `sys.getallocatedblocks()` is a LEVEL, not a counter: it reports what is allocated NOW. Discard
    the return value before snapshotting and every transient allocation has already been freed, so
    the probe measures nothing and reports it confidently. Holding the result fixes that and fixes
    the meaning at the same time — `blocks` is the RESIDENT cost of the call, and CHURN that is
    allocated and freed inside it is invisible to that counter. `gc0` is the churn proxy, since the
    generation-0 count rises with every container allocation, and the two are reported separately
    because they answer different questions.

    The residue of the measurement itself is a CONSTANT present in every arm, exactly as `contact`'s
    read counter is, so it cancels in a comparison and is not subtracted out by hand."""
    before = counters()
    held = fn(*args, **kwargs)
    after = counters()
    del held
    return {k: after[k] - before[k] for k in COUNTERS}


def the_probe_bites():
    """NON-VACUITY, AND WITHOUT IT THIS MODULE WOULD CERTIFY SILENCE. A callable that allocates must
    show a larger `blocks` delta than one that does not — otherwise every comparison would read
    UNEXPLAINED because the instrument was dead, and a dead instrument reports 'no difference'
    exactly as convincingly as a working one reports the truth. This is the falsifier that caught
    the discard bug above, which is the whole argument for writing it."""
    def allocates():
        return [object() for _ in range(500)]

    def does_not():
        return None
    return count_delta(allocates)["blocks"] > count_delta(does_not)["blocks"] + 100


# ---- the verdict ---------------------------------------------------------------------------------
def _counts_of(row):
    if not isinstance(row, dict):
        raise DeeperError(f"{row!r} is not a row")
    have = {k: row[k] for k in COUNTERS if k in row}
    return have


def verdict(row_a, row_b, time_field="p50_ns"):
    """EXPLAINED / UNEXPLAINED / NOT_ASKED for two rows measured at the SAME condition.

    NOT_ASKED   — neither row carries counters. Nothing was looked at, which is not the same as
                  having looked and found nothing, and collapsing them would let a log that never
                  measured anything read as a log that found no cause.
    UNEXPLAINED — the times differ and no counted quantity does.
    """
    for r in (row_a, row_b):
        if time_field not in r:
            raise DeeperError(f"a row carries no {time_field} — there is no difference to explain")
    ca, cb = _counts_of(row_a), _counts_of(row_b)
    if not ca or not cb:
        return NOT_ASKED
    shared = sorted(set(ca) & set(cb))
    if not shared:
        return NOT_ASKED
    if row_a[time_field] == row_b[time_field]:
        return EXPLAINED if all(ca[k] == cb[k] for k in shared) else UNEXPLAINED
    return EXPLAINED if any(ca[k] != cb[k] for k in shared) else UNEXPLAINED


def moved(row_a, row_b):
    """Which counters differ — returned WITH the verdict everywhere it is reported, so the word is
    never handed over without the evidence that produced it."""
    ca, cb = _counts_of(row_a), _counts_of(row_b)
    return tuple(k for k in sorted(set(ca) & set(cb)) if ca[k] != cb[k])


# ---- fixtures --------------------------------------------------------------------------------------
def _row(t, **counts):
    r = {"p50_ns": t}
    r.update(counts)
    return r


# ---- the laws ---------------------------------------------------------------------------------------
def a_count_that_moves_with_the_time_explains_it():
    a = _row(1000, blocks=10, gc0=1, gc1=0, gc2=0)
    b = _row(1200, blocks=14, gc0=1, gc1=0, gc2=0)
    return verdict(a, b) == EXPLAINED and moved(a, b) == ("blocks",)


def a_difference_with_no_moving_count_is_unexplained():
    """THE BAND, AS A SHAPE. Same counts, different times — which is precisely what `measure`'s
    shared-slope result predicts CANNOT happen, so a log reading this way is telling you the model
    is incomplete rather than telling you which arm is faster."""
    a = _row(1000, blocks=10, gc0=1, gc1=0, gc2=0)
    b = _row(1200, blocks=10, gc0=1, gc1=0, gc2=0)
    return verdict(a, b) == UNEXPLAINED and moved(a, b) == ()


def a_log_without_counters_reads_not_asked():
    """AND THIS IS WHAT EVERY LOG IN THIS REPOSITORY HAS LOOKED LIKE. Not 'no cause found' —
    nothing was looked at, and a detector that fused the two would let an instrument that never
    measured anything pass as one that measured and found nothing."""
    return (verdict(_row(1000), _row(1200)) == NOT_ASKED
            and verdict(_row(1000, blocks=1), _row(1200)) == NOT_ASKED)


def the_three_verdicts_are_different_findings():
    """Planted together so the distinctions cannot quietly collapse into a boolean."""
    return len({a_count_that_moves_with_the_time_explains_it(),
                a_difference_with_no_moving_count_is_unexplained(),
                a_log_without_counters_reads_not_asked()}) == 1 and \
        len({EXPLAINED, UNEXPLAINED, NOT_ASKED}) == 3


def equal_times_with_unequal_counts_are_also_unexplained():
    """THE SYMMETRIC CASE, and leaving it out would make this a one-directional instrument. If the
    counts differ and the time does not, the model is equally wrong — it predicted a difference
    that did not appear — and a detector only looking for unexplained SLOWNESS would miss it."""
    a = _row(1000, blocks=10, gc0=1, gc1=0, gc2=0)
    b = _row(1000, blocks=99, gc0=1, gc1=0, gc2=0)
    return verdict(a, b) == UNEXPLAINED


def a_row_without_a_time_refuses():
    caught = 0
    for bad in ({}, {"blocks": 1}):
        try:
            verdict(_row(100, blocks=1), bad)
        except DeeperError:
            caught += 1
    return caught == 2


def the_counter_list_is_declared_not_discovered():
    """`does_not_show`, made checkable. FOUR counters are named; the machine has many more, so a
    difference living in branch prediction, cache residency or scheduler placement reads
    UNEXPLAINED — correctly, because this instrument cannot see it."""
    return (len(COUNTERS) == 4 and "blocks" in COUNTERS
            and all(k in counters() for k in COUNTERS))


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("verdicts", "probe")


def scene_case(name):
    if name == "verdicts":
        return "explained=%s|unexplained=%s|notasked=%s|symmetric=%s|refuse=%s|distinct=%s" % (
            a_count_that_moves_with_the_time_explains_it(),
            a_difference_with_no_moving_count_is_unexplained(),
            a_log_without_counters_reads_not_asked(),
            equal_times_with_unequal_counts_are_also_unexplained(),
            a_row_without_a_time_refuses(), the_three_verdicts_are_different_findings())
    if name == "probe":
        # THE COUNTS THEMSELVES ARE NEVER DIGESTED — they are CPython-version dependent, and this
        # container is not the named host. Only the PROBE'S PROPERTIES are pinned.
        return "bites=%s|counters=%s|declared=%s" % (
            the_probe_bites(), COUNTERS, the_counter_list_is_declared_not_discovered())
    raise DeeperError(f"no scene named {name!r}")


def scene_result(name):
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


def deeper_digest():
    return hashlib.sha256(MAGIC + b"|" + "|".join(scene_result(n)
                                                  for n in SCENES).encode()).hexdigest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_deeper.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise DeeperError(f"no golden named {name!r}")


if __name__ == "__main__":
    print("count moves -> EXPLAINED    :", a_count_that_moves_with_the_time_explains_it())
    print("no count moves -> UNEXPLAIN :", a_difference_with_no_moving_count_is_unexplained())
    print("no counters -> NOT_ASKED    :", a_log_without_counters_reads_not_asked())
    print("symmetric case              :", equal_times_with_unequal_counts_are_also_unexplained())
    print("a row without a time refuses:", a_row_without_a_time_refuses())
    print("the probe bites             :", the_probe_bites())
    print("counter list declared       :", the_counter_list_is_declared_not_discovered())
    print("live counters (NOT digested):", counters())
    for n in SCENES:
        print(n, scene_result(n))
    print("deeper", deeper_digest())
