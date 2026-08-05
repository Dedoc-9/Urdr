# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""probes — Rung 3: the FROZEN PROBE CORPUS Q, and the machinery for the predictive operator Psi.

WHY THIS EXISTS. Checkpoint 10 accepted Psi as the OBSERVATIONAL QUOTIENT of the engine
(S1 ~ S2 iff Psi(S1) = Psi(S2)) and froze every downstream quantity -- operator drift
Delta_Psi(t,k) = d(Psi_t, Psi_{t-k}), the attractor radius r_t = d(Psi_t, A), and the finite-probe
identifiability candidate W3 -- as UNBUILT pending one thing: a probe corpus. Rung 2 established why
it cannot be skipped. The engine's errors are unpredictable at both batch and joint granularity, but
the repeated-measures questions (persistent bottlenecks, calibration improving on hard joints) are
UNTESTED rather than refuted, because the READ corpus has n = 1 per joint: every joint is read once
and never re-measured. Psi over a fixed Q is precisely the instrument that supplies repeated
measurement, and nothing else in the engine does.

THIS FILE FREEZES Q AND NOTHING ELSE. `PSI` is deliberately EMPTY in the commit that introduces Q.
The corpus must be sealed before any operator is emitted against it, or the probe set becomes tunable
to the answer -- the same discipline checkpoint 9's null spec followed, and the same trap the ledger
has now avoided three times (the null's alpha, the orbit falsifier's threshold, this).

WHY THE PROBES ARE SYNTHETIC. A probe drawn from a module the engine has READ is worthless: the
engine would recite a known resolution at high confidence, and Psi would measure recall rather than
predictive disposition. A probe drawn from a module the engine is ABOUT to read is worse -- it
contaminates the READ pass it is meant to observe (L59). So every probe below is FABRICATED: a
plausible module that does not exist, is not on any roadmap, and will never be built. No answer
exists, so none can leak, and the probes stay valid as instruments for as long as that holds. They
carry a `QP` prefix so they can never collide with a real module name.

DESIGN CRITERION, from L61 turned on the corpus itself: a probe every operator answers identically
cannot detect drift. Each probe is therefore written to be GENUINELY AMBIGUOUS across two or three
classes -- deliberately sitting on a seam the engine has historically split on (police vs
representation, invariant vs equivalence, price vs order, floor vs measure). A corpus of easy probes
would read CONSISTENT forever, which is an empty answer wearing a confirmation's clothes.

THE FIXED CLASS SPACE. Unlike the READ freezes -- where each joint carried its own partition -- every
probe is scored over ONE fixed class vocabulary, so Psi_t is a vector in a common space and the L1
distance between operators is well defined. Without this, drift between checkpoints would be
comparing vectors of different shapes.

THE HONEST BOUNDARY, stated before any number exists. Psi is AUTHOR-EMITTED: the basis B-M' is a
reading heuristic, not executable code, so the credences it assigns are DECLARED, not MEASURED. What
this module MEASURES is the arithmetic over recorded vectors (distances, drift, radii); what it
cannot certify is that a re-emitted Psi reflects only the engine's disposition and not the author's
memory or mood on the day. That noise floor is real, it is not estimable from one emission, and every
drift number computed here inherits it. `declared != verified`. The mitigation is structural rather
than hopeful: the probes are fixed and public, the class space is fixed, and every emission is
committed before the next is computed -- so a drift claim can at least be audited against the record
that produced it.

GRADE. MEASURED: the corpus integrity checks, and (once PSI is populated) all distance/drift
arithmetic -- integer, exhaustive, rerun byte-identical. DECLARED: the probe texts, the class space,
and every emitted Psi vector. does_not_show: that Psi is a faithful image of the engine (it is the
image over THIS Q, which is W3's whole point); that drift measures anything beyond the recorded
vectors; any predictive claim whatsoever -- Psi is EXPERIMENTAL under L63 and may be computed and
reported but NOT reasoned from until it beats a seated incumbent on a declared objective.

    PYTHONHASHSEED=0 python3 exe_epistemics/probes.py
"""

#: THE FIXED CLASS SPACE. One vocabulary for every probe, so Psi_t lives in a common vector space.
#: Drawn from the classes the READ pass actually resolved, plus the mandatory catch-all (L60).
CLASSES = ("C-R", "C-EQ", "C-INV", "C-AB", "C-REP", "C-PRICE", "C-ORD", "C-FLOOR", "R-M", "R-O")

#: Integer ten-thousandths, as everywhere else in this ledger -- no float enters a verdict.
SCALE = 10000

#: THE FROZEN CORPUS. Ten fabricated modules, each sitting on a seam the engine has historically
#: split on. `seam` records the intended ambiguity so a later reader can check the corpus was built
#: to discriminate rather than to be answered easily -- it is documentation of intent, never an
#: answer key (no answers exist).
Q = (
    ("QP01", "QPRALLOC1", "Deterministic replica budget allocator: how many replicas a region may "
     "hold, refused above the ceiling", "the opcost/govern cost family; wire's replication",
     "price vs admission -- a ceiling that refuses looks like both"),
    ("QP02", "QPMIRROR1", "Mirror witness: a shadow region recomputed independently and compared to "
     "the primary each tick", "terraform's chain law; mesh's monolith oracle",
     "equivalence vs police -- an oracle comparison that refuses on mismatch"),
    ("QP03", "QPTENURE1", "Tenure ledger: an authority's right to a region decays unless renewed, "
     "and lapse is proved rather than assumed", "lease's standing lease; rannull's nullity",
     "structural invariant vs admission -- continuity proved by refusal"),
    ("QP04", "QPSIEVE1", "Candidate sieve: a cheap over-approximating filter ahead of the exact "
     "predicate, never missing a member", "frontier, ashdepth, interest -- the approximation axis",
     "equivalence vs floor -- soundness of an over-approximation, and its non-vacuity"),
    ("QP05", "QPCADENCE1", "Cadence governor: work admitted in a certified deadline order with a "
     "proven bound on the wait", "priogov's certified order; schedule's aging",
     "order vs price -- the scheduling axis's own ambiguity"),
    ("QP06", "QPECHO1", "Echo transcript: the observable record of what a client was shown, "
     "replayable and citable", "drive's transcript; view_witness's citation contract",
     "representation vs police -- a transcript that must also refuse forgery"),
    ("QP07", "QPQUELL1", "Quell: a proof that a proposed elaboration of the admission path changes "
     "no verdict and may be omitted", "recirc's 'there is no loop'; ashdepth's vacuity floor",
     "floor vs equivalence -- a soundness-of-absence result stated as an identity"),
    ("QP08", "QPBRAID1", "Braid: two independently certified streams interleaved, with the merged "
     "witness equal to either applied alone in order", "commute's diamond; nway's independence round",
     "equivalence vs composition -- a two-law join or a single identity"),
    ("QP09", "QPTITHE1", "Tithe: every admitted operation pays a fixed structural cost into a pool "
     "that bounds total outstanding work", "budget's pure subtraction; byteacct's accounting",
     "price vs invariant -- a conserved quantity or a charged one"),
    ("QP10", "QPVEIL1", "Veil: a region whose contents are provably unreadable by a peer while "
     "remaining verifiable by it", "tierview's zero-by-construction; perception's witnessed absence",
     "police vs representation vs floor -- absence that must still be certified"),
)

def _v(**kw):
    """A Psi entry: named classes carry mass, every unnamed class is explicitly zero. Written this
    way so an omitted class is a ZERO on the record rather than a hole in the vector."""
    vec = dict((c, 0) for c in CLASSES)
    for k, val in kw.items():
        cls = k.replace("_", "-")
        if cls not in vec:
            raise ProbeError("unknown class %s" % cls)
        vec[cls] = val
    return vec


#: RUNG 4 -- THE REPEATABILITY CONTROL, and its reading rule FROZEN BEFORE the control was emitted.
#:
#: WHY: standard measurement practice requires a repeatability coefficient before any observed change
#: can be called real -- CR = 2.77 x SEM, and a difference below CR is indistinguishable from the
#: instrument's own error. Psi is AUTHOR-EMITTED, so it has measurement error, and until that floor is
#: measured every drift number is uninterpretable no matter how many batches accumulate.
#:
#: THE CONFOUND, stated before the number: this control was emitted in the SAME session that produced
#: Psi_0, so the original vectors were visible in context. Anchoring is therefore unavoidable and
#: pushes the measured difference DOWN. The result is a LOWER BOUND on author-emission noise, and a
#: weak one.
#:
#: FROZEN READING RULE (asymmetric, because the confound is one-directional):
#:   * eps_author > 0  -- INFORMATIVE. Disagreement that survives anchoring is real emission noise, so
#:                        it is a genuine lower bound on the floor. Any future ||Psi_k - Psi_j||_1 at
#:                        or below it is uninterpretable and treated as system noise (L63).
#:   * eps_author == 0 -- UNINFORMATIVE, and must NOT be read as "the instrument is stable". A zero is
#:                        exactly what perfect anchoring produces. It would establish nothing.
#: A VALID (unanchored) control requires a FRESH SESSION with no access to Psi_0 -- emitted before the
#: ledger is read -- or emission by a different agent. That experiment is named here and NOT claimed.
#:
#: KILL CONDITION (frozen): if eps_author is large relative to the dispositional shifts Psi would need
#: to detect, Psi is RETIRED under L63 as an uncalibrated instrument, before anything is built on it.

#: RECORDED OPERATORS. `PSI[t]` maps probe id -> {class: integer ten-thousandths}. EMPTY at the
#: commit that freezes Q; each checkpoint appends exactly one emission, committed before the next is
#: computed. A vector must cover CLASSES exactly and sum to SCALE.
#:
#: Psi_0 -- emitted 2026-08-04 by the SEATED basis B-M' ("input x semantics" + the approximation and
#: scheduling axes), against the corpus frozen in the preceding commit. DECLARED, not measured.
PSI = {
    "0": {
        "QP01": _v(C_PRICE=3800, C_R=3000, C_AB=1200, C_INV=800, C_EQ=400, C_ORD=300,
                   C_REP=200, C_FLOOR=100, R_M=100, R_O=100),
        "QP02": _v(C_EQ=3800, C_R=2500, C_AB=1800, C_INV=800, C_REP=400, C_PRICE=200,
                   C_FLOOR=200, C_ORD=100, R_M=100, R_O=100),
        "QP03": _v(C_INV=3800, C_R=2800, C_EQ=1200, C_AB=1000, C_PRICE=400, C_REP=300,
                   C_FLOOR=200, C_ORD=100, R_M=100, R_O=100),
        "QP04": _v(C_EQ=3600, C_FLOOR=2000, C_R=1600, C_AB=1200, C_INV=700, C_REP=300,
                   C_PRICE=200, C_ORD=100, R_M=150, R_O=150),
        "QP05": _v(C_ORD=4200, C_PRICE=2200, C_INV=1200, C_R=1000, C_AB=700, C_EQ=300,
                   C_REP=200, C_FLOOR=100, R_M=50, R_O=50),
        "QP06": _v(C_REP=3200, C_R=3000, C_AB=1500, C_EQ=1000, C_INV=700, C_PRICE=200,
                   C_FLOOR=200, C_ORD=100, R_M=50, R_O=50),
        "QP07": _v(C_FLOOR=3600, C_EQ=2800, C_INV=1200, C_R=900, C_AB=800, C_REP=200,
                   C_PRICE=200, C_ORD=100, R_M=100, R_O=100),
        "QP08": _v(C_EQ=3800, C_AB=2600, C_INV=1400, C_R=900, C_REP=400, C_PRICE=300,
                   C_ORD=200, C_FLOOR=200, R_M=100, R_O=100),
        "QP09": _v(C_PRICE=3400, C_INV=2400, C_AB=1600, C_R=1000, C_EQ=700, C_REP=300,
                   C_ORD=300, C_FLOOR=100, R_M=100, R_O=100),
        "QP10": _v(C_R=2800, C_INV=2400, C_FLOOR=1800, C_REP=1200, C_EQ=800, C_AB=500,
                   C_PRICE=200, C_ORD=100, R_M=100, R_O=100),
    },
    # Psi_0' -- THE REPEATABILITY CONTROL (Rung 4). Same engine state as Psi_0 (post-batch-9, no
    # intervening work), re-derived from the probe TEXT with the corpus traversed in a scrambled order
    # (QP07, QP02, QP10, QP05, QP01, QP09, QP03, QP08, QP04, QP06) rather than in index order. The
    # anchoring confound above applies in full.
    "0'": {
        "QP01": _v(C_PRICE=3700, C_R=3100, C_AB=1200, C_INV=800, C_EQ=400, C_ORD=300,
                   C_REP=200, C_FLOOR=100, R_M=100, R_O=100),
        "QP02": _v(C_EQ=3700, C_R=2600, C_AB=1700, C_INV=900, C_REP=400, C_PRICE=200,
                   C_FLOOR=200, C_ORD=100, R_M=100, R_O=100),
        "QP03": _v(C_INV=3700, C_R=2900, C_EQ=1200, C_AB=1000, C_PRICE=400, C_REP=300,
                   C_FLOOR=200, C_ORD=100, R_M=100, R_O=100),
        "QP04": _v(C_EQ=3500, C_FLOOR=2100, C_R=1600, C_AB=1200, C_INV=700, C_REP=300,
                   C_PRICE=200, C_ORD=100, R_M=150, R_O=150),
        "QP05": _v(C_ORD=4300, C_PRICE=2100, C_INV=1200, C_R=1000, C_AB=700, C_EQ=300,
                   C_REP=200, C_FLOOR=100, R_M=50, R_O=50),
        "QP06": _v(C_R=3100, C_REP=3100, C_AB=1500, C_EQ=1000, C_INV=700, C_PRICE=200,
                   C_FLOOR=200, C_ORD=100, R_M=50, R_O=50),
        "QP07": _v(C_FLOOR=3400, C_EQ=3000, C_INV=1200, C_R=900, C_AB=700, C_REP=200,
                   C_PRICE=200, C_ORD=100, R_M=150, R_O=150),
        "QP08": _v(C_EQ=3900, C_AB=2500, C_INV=1400, C_R=900, C_REP=400, C_PRICE=300,
                   C_ORD=200, C_FLOOR=200, R_M=100, R_O=100),
        "QP09": _v(C_PRICE=3300, C_INV=2500, C_AB=1600, C_R=1000, C_EQ=700, C_REP=300,
                   C_ORD=300, C_FLOOR=100, R_M=100, R_O=100),
        "QP10": _v(C_R=2700, C_INV=2300, C_FLOOR=1900, C_REP=1300, C_EQ=800, C_AB=500,
                   C_PRICE=200, C_ORD=100, R_M=100, R_O=100),
    },
}

#: The control pair. Named so the repeatability computation cannot silently drift onto other keys.
CONTROL_PAIR = ("0", "0'")


class ProbeError(Exception):
    pass


def corpus_is_sealed():
    """The corpus is well-formed: unique ids, a QP prefix (so no probe can name a real module),
    a stated seam for each, and a non-trivial size."""
    ids = [p[0] for p in Q]
    if len(set(ids)) != len(ids):
        return False
    if not all(p[0].startswith("QP") and p[1].startswith("QP") for p in Q):
        return False
    if not all(p[4].strip() for p in Q):
        return False
    return len(Q) >= 8


def validate(vec):
    """A Psi entry must cover the fixed class space exactly and sum to SCALE -- so distances are
    between points of the same simplex and cannot silently compare different shapes."""
    if set(vec) != set(CLASSES):
        raise ProbeError("vector must cover exactly CLASSES")
    if sum(vec.values()) != SCALE:
        raise ProbeError("vector must sum to %d, got %d" % (SCALE, sum(vec.values())))
    return True


def l1(a, b):
    """Integer L1 distance between two operators over the whole corpus."""
    return sum(abs(a[p][c] - b[p][c]) for p in sorted(a) for c in CLASSES)


def emissions():
    return sorted(PSI)


def local_drift(t):
    """d(Psi_t, Psi_{t-1}) -- how far the operator moved this checkpoint."""
    ks = emissions()
    i = ks.index(t)
    return None if i == 0 else l1(PSI[ks[i]], PSI[ks[i - 1]])


def cumulative_drift(t):
    """d(Psi_t, Psi_0) -- how far the operator has moved in total."""
    ks = emissions()
    return None if not ks else l1(PSI[t], PSI[ks[0]])


def attractor(keys=None):
    """A = mean(Psi_i) over the given emissions -- the centroid of a predictive regime. Integer
    mean with a deterministic remainder, so the attractor is reproducible."""
    ks = list(keys if keys is not None else emissions())
    if not ks:
        return None
    out = {}
    for pid, *_ in Q:
        vec = {}
        for c in CLASSES:
            vec[c] = sum(PSI[k][pid][c] for k in ks) // len(ks)
        drift = SCALE - sum(vec.values())
        if drift:
            vec[sorted(vec)[0]] += drift
        out[pid] = vec
    return out


def attractor_radius(t, keys=None):
    """r_t = d(Psi_t, A) -- repeated approach to the same PREDICTIVE REGIME. Lives entirely in
    behaviour space, so it evades W2/RST by construction rather than by patching."""
    a = attractor(keys)
    return None if a is None else l1(PSI[t], a)


def spread():
    """L61 on the corpus itself: a probe every operator answers identically cannot detect drift.
    Returns per-probe max-minus-min mass on the modal class across emissions; all-zero means the
    corpus is STARVED as an instrument, not that the engine is stable."""
    ks = emissions()
    if len(ks) < 2:
        return None
    out = {}
    for pid, *_ in Q:
        vals = [max(PSI[k][pid].values()) for k in ks]
        out[pid] = max(vals) - min(vals)
    return out


def leading(vec):
    """The argmax, tie-broken lexically so a tie is resolved deterministically rather than by dict
    order. A leading class that FLIPS between the control pair is inside the noise floor."""
    return max(sorted(vec), key=lambda c: vec[c])


def repeatability():
    """RUNG 4. eps_author = ||Psi_0' - Psi_0||_1 over the whole corpus, plus the per-probe breakdown
    and any leading-class FLIPS. Returns (eps, per_probe, flips). Read under the FROZEN asymmetric
    rule above: a positive value is a genuine lower bound; a zero establishes nothing."""
    a, b = CONTROL_PAIR
    if a not in PSI or b not in PSI:
        return None
    per, flips = {}, []
    for pid, *_ in Q:
        d = sum(abs(PSI[b][pid][c] - PSI[a][pid][c]) for c in CLASSES)
        per[pid] = d
        la, lb = leading(PSI[a][pid]), leading(PSI[b][pid])
        if la != lb:
            flips.append((pid, la, lb))
    return sum(per.values()), per, flips


def smallest_detectable_drift():
    """The floor a future drift must EXCEED to be interpretable. Deliberately the raw eps rather than
    a 2.77x repeatability coefficient: the standard CR multiplier assumes an SEM estimated from many
    independent pairs, and one anchored pair supports no such estimate. Inflating a single anchored
    difference into a CR would manufacture precision this control cannot supply."""
    r = repeatability()
    return None if r is None else r[0]


def drift_is_interpretable(t, k):
    """DECIDED: is ||Psi_t - Psi_k||_1 above the measured floor? False means the observed movement is
    indistinguishable from author-emission noise and may NOT be reasoned from (L63)."""
    floor = smallest_detectable_drift()
    if floor is None or t not in PSI or k not in PSI:
        return None
    return l1(PSI[t], PSI[k]) > floor


def main():
    print("FROZEN PROBE CORPUS Q -- %d synthetic probes, fixed class space of %d"
          % (len(Q), len(CLASSES)))
    print("classes: %s" % ", ".join(CLASSES))
    print()
    for pid, magic, role, ambient, seam in Q:
        print("%-5s %-11s %s" % (pid, magic, role))
        print("      ambient: %s" % ambient)
        print("      seam:    %s" % seam)
    print()
    print("corpus sealed and well-formed: %s" % corpus_is_sealed())
    bad = []
    for t in emissions():
        for pid in sorted(PSI[t]):
            try:
                validate(PSI[t][pid])
            except ProbeError as exc:
                bad.append("%s/%s: %s" % (t, pid, exc))
    print("every recorded vector valid (covers CLASSES, sums to %d): %s"
          % (SCALE, not bad if not bad else bad))
    if emissions():
        t0 = emissions()[0]
        print()
        print("Psi_%s leading class per probe:" % t0)
        for pid, *_ in Q:
            v = PSI[t0][pid]
            top = max(sorted(v), key=lambda c: v[c])
            ranked = sorted(v, key=lambda c: (-v[c], c))
            print("   %-5s %-8s %5d   (2nd %-8s %5d, margin %d)"
                  % (pid, top, v[top], ranked[1], v[ranked[1]], v[top] - v[ranked[1]]))
    print("recorded emissions: %s" % (emissions() or "NONE -- Q is frozen; Psi_0 is emitted in the"
                                      " NEXT commit, never in the one that seals the corpus"))
    if len(emissions()) >= 2:
        print()
        for t in emissions():
            print("  Psi_%s  local drift %s  cumulative %s  radius %s"
                  % (t, local_drift(t), cumulative_drift(t), attractor_radius(t)))
        print("  corpus spread (L61): %s" % spread())
    r = repeatability()
    if r is not None:
        eps, per, flips = r
        print()
        print("RUNG 4 -- THE REPEATABILITY CONTROL (Psi_0' vs Psi_0, same engine state)")
        print("  per-probe L1: %s" % ", ".join("%s=%d" % (k, per[k]) for k in sorted(per)))
        print("  eps_author = %d   (total mass across corpus = %d, so %.1f%%)"
              % (eps, len(Q) * SCALE, 100.0 * eps / (len(Q) * SCALE)))
        print("  leading-class FLIPS: %s"
              % (", ".join("%s %s->%s" % f for f in flips) if flips else "none"))
        print("  reading (frozen rule): %s"
              % ("INFORMATIVE -- disagreement survived anchoring, so this is a genuine LOWER BOUND"
                 if eps > 0 else
                 "UNINFORMATIVE -- a zero is what perfect anchoring produces; establishes nothing"))
        print("  smallest detectable drift = %s (raw eps; NOT inflated to a 2.77x CR, which would"
              % smallest_detectable_drift())
        print("     manufacture precision one anchored pair cannot supply)")
    print()
    print("STATUS: EXPERIMENTAL under L63 -- may be computed and reported, may NOT be reasoned from")
    print("until it beats a seated incumbent on a declared objective.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
