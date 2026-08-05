# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""probes2 — the SUCCESSOR probe corpus Q', with per-axis redundancy. FROZEN; Psi deliberately empty.

WHY THIS EXISTS. Rung 5 measured a defect in Q, not in the engine: the W3 identifiability verdict was
ONE-PROBE FRAGILE. QP05 alone carried 73% of the ablation difference, and leave-one-out showed that
removing that single probe flips the verdict from INCONCLUSIVE to SUPPORTED. Q's ten probes were each
written on a DISTINCT seam -- correct under L61, since a probe everyone answers identically detects
nothing -- and that very distinctness left every axis with exactly one witness. **Discriminating
breadth and per-axis redundancy pull against each other, and Q was built for the first without
noticing the second.**

Q IS NOT EDITED. A corpus revised in response to a verdict it produced is tunable to the answer. Q
stays frozen exactly as it was, with its defect recorded; Q' is a SUCCESSOR, and both are retained so
the two can be compared rather than one quietly replacing the other.

THE L63 TENSION, STATED RATHER THAN STEPPED AROUND. At batch 11 this module was explicitly REFUSED on
L63 grounds: building more Psi apparatus while Psi is EXPERIMENTAL and has never beaten a seated
incumbent is the accumulation the law exists to stop. That objection has NOT been answered -- Psi still
holds no standing. What changed is narrower and is the only thing claimed here: the READ pass is
complete, so the competing use of effort the refusal partly rested on no longer exists. Q' is built
EXPERIMENTAL, may be computed and reported, and MAY NOT be reasoned from until Psi beats a seated
incumbent on a declared objective. Recording the tension is the point; a successor that quietly
outgrew a refusal would be worse than the refusal.

WHAT IS NEW IN Q'.
  * TWO probes per named axis, so no verdict can rest on a single row. Leave-one-out on Q' must not
    flip any verdict; if it does, the redundancy failed and Q' inherits Q's defect.
  * The pairs are DELIBERATELY NOT PARAPHRASES. Two probes that differ only in wording would give
    redundancy of form without redundancy of evidence -- they would fail together. Each pair puts its
    axis in two structurally different settings (a spatial one and a temporal one, an authority one
    and an arithmetic one), so a basis that has the axis for the wrong reason can split the pair.
  * Same SYNTHETIC discipline as Q: every probe is a fabricated module (QR prefix) that does not exist
    and will never be built, so no answer exists and none can leak.
  * Same FIXED class space as Q, so Psi vectors over Q and Q' live in comparable coordinates.

GRADE. MEASURED: the corpus integrity checks (per-axis coverage >= 2, unique ids, QR prefix, non-empty
seams) and, once PSI is populated, all distance arithmetic. DECLARED: the probe texts, the axis
assignment of each probe, and every emitted vector. does_not_show: that Q' actually resolves any axis
-- redundancy of construction is not resolving power, and the leave-one-out check on real emissions is
what would show it; nor that two probes per axis is ENOUGH, which is a design choice no measurement
here supports.

    PYTHONHASHSEED=0 python3 exe_epistemics/probes2.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from probes import CLASSES, SCALE, ProbeError                      # the SAME fixed class space as Q

#: The named axes Q' must cover with redundancy — the live substantive classes of the pass.
AXES = ("C-R", "C-EQ", "C-INV", "C-AB", "C-REP", "C-PRICE", "C-ORD", "C-FLOOR")

#: THE SUCCESSOR CORPUS. (id, magic, role, ambient, axis, setting) — TWO per axis, each pair placed in
#: structurally different settings so a basis holding the axis for the wrong reason can split them.
Q2 = (
    ("QR01", "QRLEDGER1", "Ledger admission: an entry is accepted only if its predecessor digest "
     "resolves in the store, else refused", "terraform's chain law; sealwrit's registry",
     "C-R", "authority"),
    ("QR02", "QRGATEKEEP1", "Arrival gate: a claimed sensor reading is admitted only when it falls "
     "inside the declared instrument envelope", "warden's kinematic gate; stance's domain refusal",
     "C-R", "measurement"),
    ("QR03", "QRTWINRUN1", "Twin run: the same world stepped on two independent schedulers yields "
     "byte-identical witnesses", "mesh == monolith; commuteprop's diamond",
     "C-EQ", "concurrency"),
    ("QR04", "QRFOLDBACK1", "Foldback: a compressed transcript expanded and re-compressed returns "
     "the identical bytes", "quintessence's injectivity; predict's rollback equivalence",
     "C-EQ", "serialization"),
    ("QR05", "QRTETHER1", "Tether: an actor's authority region may move only through a chain of "
     "overlapping holds, never by jump", "hand's handoff continuity; lease's standing",
     "C-INV", "authority"),
    ("QR06", "QRBALLAST1", "Ballast: total charge across a partitioned world is unchanged by any "
     "redistribution among partitions", "sea's mass conservation; govern's admitted+deferred",
     "C-INV", "physical"),
    ("QR07", "QRSHUTTER1", "Shutter: a frame is admitted only when BOTH its exposure is lawful and "
     "its content replays equal to the authority", "panewire's equal-or-refuse under play",
     "C-AB", "composition"),
    ("QR08", "QRPORTCULLIS1", "Portcullis: a migration commits only if the custody chain verifies "
     "AND the destination's independence round is schedulable", "mesh's reject-whole; migrate",
     "C-AB", "authority"),
    ("QR09", "QRIMPRINT1", "Imprint: the certified record of what an observer was shown, replayable "
     "and addressable", "drive's transcript; ghostsnap's pose records",
     "C-REP", "observation"),
    ("QR10", "QRDISTILL1", "Distil: every record of four families reduces to one tuple, no two "
     "records colliding", "quintessence's five-family extractor",
     "C-REP", "identity"),
    ("QR11", "QRMETER1", "Meter: each admitted operation draws from a fixed allowance and the "
     "allowance is never exceeded", "opcost's envelope; budget's subtraction",
     "C-PRICE", "resource"),
    ("QR12", "QRTOLLGATE1", "Tollgate: the worst-case wait for any class of request is bounded and "
     "the bound is refused if it cannot be met", "slo/clslo's composite and per-class bounds",
     "C-PRICE", "latency"),
    ("QR13", "QRTIDEBOOK1", "Tidebook: work is drained in a certified deadline order and no item "
     "waits beyond a proven bound", "priogov's certified order and aging",
     "C-ORD", "scheduling"),
    ("QR14", "QRPROCESSION1", "Procession: eligibility is checked strictly before admission, and a "
     "failed eligibility check consumes nothing", "sealwrit's ordering theorem",
     "C-ORD", "authority"),
    ("QR15", "QRHOLLOW1", "Hollow: a proposed refinement of the admission path is shown to change no "
     "verdict on any input, and is therefore omitted", "recirc's one-step closure; ashdepth's floor",
     "C-FLOOR", "elaboration"),
    ("QR16", "QRLEVELPEG1", "Levelpeg: the advantage a higher-capability client can obtain over a "
     "lower one is zero because the predicate cannot receive capability",
     "tierview's zero-by-construction", "C-FLOOR", "fairness"),
)

#: RECORDED OPERATORS over Q'. EMPTY at the commit that seals the corpus — the same discipline Q
#: followed: a probe set chosen after seeing an operator is tunable to the answer.
PSI2 = {}


def axis_coverage():
    """Probes per named axis. The redundancy requirement Rung 5's defect created."""
    out = {}
    for probe in Q2:
        out[probe[4]] = out.get(probe[4], 0) + 1
    return out


def corpus_is_sealed():
    """Well-formedness: unique ids, QR prefix (so no probe can name a real module or a Q probe), a
    stated axis and setting for each, EVERY named axis covered at least TWICE, and the pair for each
    axis placed in DIFFERENT settings (redundancy of evidence, not of wording)."""
    ids = [p[0] for p in Q2]
    if len(set(ids)) != len(ids):
        return False
    if not all(p[0].startswith("QR") and p[1].startswith("QR") for p in Q2):
        return False
    if not all(p[4] in CLASSES and p[5].strip() for p in Q2):
        return False
    cov = axis_coverage()
    if any(cov.get(a, 0) < 2 for a in AXES):
        return False
    for a in AXES:
        settings = [p[5] for p in Q2 if p[4] == a]
        if len(set(settings)) != len(settings):
            return False                       # a paraphrase pair: same setting twice
    return True


def redundancy_report():
    """Per axis: how many probes, and in which settings — the check Q could not have passed."""
    return dict((a, [p[5] for p in Q2 if p[4] == a]) for a in AXES)


def main():
    print("SUCCESSOR PROBE CORPUS Q' — %d synthetic probes over %d named axes" % (len(Q2), len(AXES)))
    print("class space: shared with Q (%d classes), so Psi vectors are comparable" % len(CLASSES))
    print()
    for pid, magic, role, ambient, axis, setting in Q2:
        print("%-5s %-15s [%-8s %-13s] %s" % (pid, magic, axis, setting, role[:62]))
    print()
    print("axis coverage: %s" % redundancy_report())
    print("corpus sealed and well-formed (>=2 per axis, no paraphrase pairs): %s" % corpus_is_sealed())
    print("recorded emissions: %s" % (sorted(PSI2) or "NONE — Q' is frozen; any Psi is emitted in a "
                                      "LATER commit, never in the one that seals the corpus"))
    print()
    print("STATUS: EXPERIMENTAL under L63. The batch-11 refusal of this module is NOT answered —")
    print("Psi still holds no standing; only the competing use of effort has gone. May be computed")
    print("and reported, may NOT be reasoned from.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
