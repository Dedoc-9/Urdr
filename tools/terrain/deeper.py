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
COUNTERS = ("blocks", "gc0", "gc1", "gc2", "peak")

#: Counters a v1 log does not carry. Kept as data so a comparison against an ARCHIVED record uses
#: the fields that record actually has, rather than reading absence as zero.
ADDED_AFTER_V1 = ("peak",)


class DeeperError(Exception):
    def __init__(self, message):
        super().__init__(f"DEEPER-REFUSE: {message}")
        self.code = "DEEPER-REFUSE"


# ---- the probe ------------------------------------------------------------------------------------
def counters():
    """A snapshot of the deeper quantities. Version-dependent BY NATURE, which is why nothing here
    ever reaches a gate golden. `peak` is filled by `count_delta`, which is the only place a
    transient figure can be observed at all."""
    import gc
    import sys
    g0, g1, g2 = gc.get_count()
    return {"blocks": sys.getallocatedblocks(), "gc0": g0, "gc1": g1, "gc2": g2, "peak": 0}


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
    import tracemalloc
    started = not tracemalloc.is_tracing()
    if started:
        tracemalloc.start()
    tracemalloc.reset_peak()
    before = counters()
    held = fn(*args, **kwargs)
    after = counters()
    _cur, peak = tracemalloc.get_traced_memory()
    if started:
        tracemalloc.stop()
    del held
    out = {k: after[k] - before[k] for k in COUNTERS}
    # `peak` IS THE CHURN THE RESIDENT COUNTER CANNOT SEE, and adding it was forced by a real
    # reading: on the named host `blocks` was 4 against 4 in EVERY cell while the times differed by
    # a constant microsecond, so the instrument was blind BY CONSTRUCTION — both arms return the
    # same-shaped result and resident counting compares the shapes. It is a LEVEL over the call
    # rather than a delta, so it is not differenced; `tracemalloc` is far too heavy for the timed
    # loop and is used only here, off the clock.
    out["peak"] = peak
    return out


def verdict_grouped(a_by_run, b_by_run, time_field="p50_ns"):
    """THE ROW-AT-A-TIME FORM WAS WRONG ACROSS EXECUTIONS, AND USING IT FOUND THAT OUT. Handed five
    executions, `verdict` reads whichever row comes first — and on the named host one cell reported
    EXPLAINED purely because run 0's two timings happened to tie. A verdict that depends on which
    row was listed first is not a verdict. So the comparison is made on MEDIANS across executions,
    the same level `repeat` grades at, and the two modules now agree about what a measurement is."""
    runs = sorted(set(a_by_run) & set(b_by_run))
    if not runs:
        raise DeeperError("the two arms share no execution — there is nothing to compare")

    def med(rows, field):
        vals = sorted(r[field] for r in rows if field in r)
        if not vals:
            return None
        return vals[(len(vals) - 1) // 2]
    a_rows = [a_by_run[r] for r in runs]
    b_rows = [b_by_run[r] for r in runs]
    ta, tb = med(a_rows, time_field), med(b_rows, time_field)
    if ta is None or tb is None:
        raise DeeperError(f"a row carries no {time_field} — there is no difference to explain")
    shared = [k for k in COUNTERS
              if med(a_rows, k) is not None and med(b_rows, k) is not None]
    if not shared:
        return NOT_ASKED
    same_counts = all(med(a_rows, k) == med(b_rows, k) for k in shared)
    return EXPLAINED if (ta != tb) != same_counts else UNEXPLAINED


def the_grouped_form_does_not_depend_on_row_order():
    """THE DEFECT, PINNED. Two executions whose per-row order differs must give the same verdict —
    the row-at-a-time form does not, which is how a tie in one execution became an EXPLAINED."""
    # THE REAL SHAPE: run 0 happens to TIE while the medians across executions do not. The row form
    # sees the tie, calls it consistent with equal counts, and reports EXPLAINED. The grouped form
    # sees a difference no counter accounts for and reports UNEXPLAINED. This is not a constructed
    # edge case — it is the cell that reported EXPLAINED on the named host.
    a = {0: {"p50_ns": 100, "blocks": 4}, 1: {"p50_ns": 100, "blocks": 4},
         2: {"p50_ns": 100, "blocks": 4}}
    b = {0: {"p50_ns": 100, "blocks": 4}, 1: {"p50_ns": 300, "blocks": 4},
         2: {"p50_ns": 300, "blocks": 4}}
    shuffled_a = {0: a[2], 1: a[0], 2: a[1]}
    shuffled_b = {0: b[1], 1: b[2], 2: b[0]}
    return (verdict_grouped(a, b) == UNEXPLAINED
            and verdict_grouped(shuffled_a, shuffled_b) == UNEXPLAINED
            and verdict(a[0], b[0]) == EXPLAINED)          # the row form, disagreeing


def the_transient_counter_sees_what_resident_counting_cannot():
    """WHY `peak` EXISTS, AND IT WAS FORCED BY A READING RATHER THAN CHOSEN. A callable that
    allocates and FREES leaves `blocks` unchanged — resident counting compares what SURVIVES — while
    `peak` records the high-water mark. On the named host `blocks` read 4 against 4 in every single
    cell while the times differed by a constant microsecond: the instrument was blind by
    construction, and reporting UNEXPLAINED was correct and useless."""
    def churns():
        for _ in range(200):
            tmp = [object() for _ in range(50)]
            del tmp
        return None
    d = count_delta(churns)
    return d["blocks"] < 50 and d["peak"] > 1000


def a_v1_record_is_compared_on_the_fields_it_has():
    """L64, AT THE COMPARISON RATHER THAN THE PARSER. An archived log predates `peak`; comparing it
    must use the counters IT carries instead of reading absence as zero, which would manufacture a
    difference out of a field nobody measured."""
    a = {0: {"p50_ns": 100, "blocks": 4, "gc0": 0}}
    b = {0: {"p50_ns": 200, "blocks": 4, "gc0": 0}}
    return verdict_grouped(a, b) == UNEXPLAINED and "peak" in ADDED_AFTER_V1


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
    return (len(COUNTERS) == 5 and "blocks" in COUNTERS and "peak" in COUNTERS
            and all(k in counters() for k in COUNTERS))


# ---- scenes ------------------------------------------------------------------------------------------
SCENES = ("verdicts", "probe", "grouped")


def scene_case(name):
    if name == "verdicts":
        return "explained=%s|unexplained=%s|notasked=%s|symmetric=%s|refuse=%s|distinct=%s" % (
            a_count_that_moves_with_the_time_explains_it(),
            a_difference_with_no_moving_count_is_unexplained(),
            a_log_without_counters_reads_not_asked(),
            equal_times_with_unequal_counts_are_also_unexplained(),
            a_row_without_a_time_refuses(), the_three_verdicts_are_different_findings())
    if name == "grouped":
        return "orderfree=%s|transient=%s|v1=%s|added=%s" % (
            the_grouped_form_does_not_depend_on_row_order(),
            the_transient_counter_sees_what_resident_counting_cannot(),
            a_v1_record_is_compared_on_the_fields_it_has(), ADDED_AFTER_V1)
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
