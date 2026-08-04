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

#: RECORDED OPERATORS. `PSI[t]` maps probe id -> {class: integer ten-thousandths}. EMPTY at the
#: commit that freezes Q; each checkpoint appends exactly one emission, committed before the next is
#: computed. A vector must cover CLASSES exactly and sum to SCALE.
PSI = {}


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
    print("recorded emissions: %s" % (emissions() or "NONE -- Q is frozen; Psi_0 is emitted in the"
                                      " NEXT commit, never in the one that seals the corpus"))
    if len(emissions()) >= 2:
        print()
        for t in emissions():
            print("  Psi_%s  local drift %s  cumulative %s  radius %s"
                  % (t, local_drift(t), cumulative_drift(t), attractor_radius(t)))
        print("  corpus spread (L61): %s" % spread())
    print()
    print("STATUS: EXPERIMENTAL under L63 -- may be computed and reported, may NOT be reasoned from")
    print("until it beats a seated incumbent on a declared objective.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
