# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Mostowski's collapse hypotheses, measured MODULE BY MODULE against shipped admission code.

WHY THIS IS A TEST AND NOT AN INSTRUMENT. Rung 17 stopped the epistemics arc and RELOCATED the
collapse question: not "what could a collapse-oriented engine look like" (architecture, unearned) but
"does the admission machinery that already ships satisfy the hypotheses" (measurement). A measurement
on shipped code belongs where this repository puts measurements on shipped code -- in a red-first
falsifier the gate discovers, so the answer can go RED when it stops being true. An instrument in
`exe_epistemics/` would have been ungated, which is where all seven recorded carriers lived.

THE HYPOTHESES, and the module-local check each becomes. Mostowski: a WELL-FOUNDED, EXTENSIONAL,
SET-LIKE relation collapses onto a unique transitive image by pi(x) = {pi(y) : y R x}.

    WELL-FOUNDED           admission terminates in concrete data, never in circular justification.
    EXTENSIONAL            identical operational dependencies admit identically -- and distinct
                           ones do not collide.
    EXHAUSTIVE PARTITION   every input is admitted or TYPED-refused; nothing falls through.
    UNIQUE RECONSTRUCTION  the admitted state is recoverable from its record, and no two distinct
                           states share a record.

EVIDENCE TYPE IS ITS OWN DIMENSION, adopted from review after the first version collapsed five
distinct epistemic statuses into two words. "MEASURED" was doing the work of three different things
-- a sampled sweep, an exhaustive decision over a bounded domain, and a round-trip -- and "DECLARED"
was doing the work of two, since a structural argument from content-addressing is not the same object
as a bare assumption. The five statuses, and every cell of the matrix now carries one:

    EXECUTED       run over a SAMPLE of the domain. Honest and weak: `sample != universal` (L20).
    EXHAUSTIVE     run over EVERY point of a bounded domain, so within that bound there is no
                   sample to generalise from. Strictly stronger than EXECUTED and worth the
                   separate word: `commute`'s 256-point sweep decides its bound, it does not
                   estimate it.
    STRUCTURAL     an argument from construction, unformalised and unmechanised. Stronger than an
                   assumption, weaker than a proof, and it must not borrow the word "proven": a
                   self-parenting record needs a hash fixed point, which is a reason to believe and
                   not a thing this suite ran.
    DECLARED       assumed, with the assumption named. No evidence offered here at all.
    N/A            the hypothesis is not the right question for this module's structure.

**NO REPOSITORY-WIDE VERDICT IS ASSERTED, and that is deliberate.** A reviewer's correction, adopted:
different modules may satisfy different subsets, so the result is a MATRIX with per-cell evidence,
not a yes/no. A cell that fails is informative rather than damning -- `lease` deliberately admits
under a *cheap* predicate proven equal to the global reproof, so its uniqueness question is genuinely
different from `rannull`'s. Failures are recorded as measured facts about scope, never as defects.

WHAT IS MEASURED HERE AND WHAT IS NOT. MEASURED: determinism, injectivity over a swept domain,
typed-refusal totality over malformed inputs, and round-trip recovery. NOT MEASURED: well-foundedness
of the LIVE parent chain -- these record formats are content-addressed, so a self-parenting record
would need a hash fixed point and cannot be constructed, but that argument is STRUCTURAL and the
chain law itself lives in `terraform`, not here. The matrix records that as DECLARED, not measured,
because a test that cannot construct the counterexample has not tested for it.
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (os.path.join(ROOT, "tools", "terrain"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import commute as CM                                                       # noqa: E402
import lease as LS                                                         # noqa: E402
import rannull as RN                                                       # noqa: E402

PARENT = "a" * 64

#: THE MATRIX, as EXECUTABLE DATA WITH PROSE EXPLAINING ITS SEMANTICS — and the distinction is the
#: honest form, adopted from review. The executable part knows STATUS STRINGS and CONSISTENCY RULES.
#: It does NOT know what `STRUCTURAL` MEANS; that meaning lives in the docstring above and is human
#: interpretation. Merging the two would overstate what the gate enforces. What is genuinely bought
#: is that a matrix living only in a comment is a claim no test can reach — which is the shape this
#: sequence has recorded seven times — and that is now fixed for the CONSISTENCY of the cells only.
#:
#: THE FALSIFIERS BELOW HOLD CONSISTENCY, NOT CORRECTNESS. They check that the vocabulary does not
#: drift and that no cell claims evidence the suite does not produce. They do NOT validate that these
#: five categories are the right ontology — that is DECLARED. Outside this repository there are
#: evidence modes these five do not fit (formal proof, model checking, statistical inference,
#: independent replication, operational telemetry), so this is a PROJECT-SPECIFIC taxonomy answering
#: a concrete maintenance question — *what kind of evidence supports this cell?* — and not an
#: epistemology. Same narrowing as L63's, and for the same reason.
MATRIX_STATUSES = ("EXECUTED", "EXHAUSTIVE", "STRUCTURAL", "DECLARED", "N/A")
MATRIX = {
    "rannull": {"wellfounded": "STRUCTURAL", "extensional": "EXECUTED",
                "partition": "EXECUTED", "reconstruction": "EXECUTED"},
    "commute": {"wellfounded": "STRUCTURAL", "extensional": "EXECUTED",
                "partition": "EXHAUSTIVE", "reconstruction": "N/A"},
    "lease": {"wellfounded": "STRUCTURAL", "extensional": "EXECUTED",
              "partition": "EXECUTED", "reconstruction": "EXECUTED"},
}


class RannullCollapse(unittest.TestCase):
    """RAN-0: the proof of ABSENCE. Its record is the unit of admission."""

    def test_extensional_identical_dependencies_give_identical_records(self):
        a = RN.regional_record(PARENT, 1, 2, 3, 4, 10, 20)
        b = RN.regional_record(PARENT, 1, 2, 3, 4, 10, 20)
        self.assertEqual(a, b, "identical dependencies must produce an identical record")

    def test_extensional_distinct_dependencies_never_collide(self):
        """INJECTIVITY over a swept domain. One pair proves nothing (L20); this sweeps every
        single-field perturbation and demands all records be pairwise distinct."""
        seen = {}
        base = (PARENT, 1, 2, 3, 4, 10, 20)
        for i in range(1, 7):
            for delta in (1, 2, 7):
                args = list(base)
                args[i] = args[i] + delta
                rec = RN.regional_record(*args)
                self.assertNotIn(rec, seen,
                                 "records collided: %s and %s" % (seen.get(rec), tuple(args)))
                seen[rec] = tuple(args)
        self.assertEqual(len(seen), 18, "the sweep must actually cover 18 distinct states")

    def test_unique_reconstruction_round_trips(self):
        for k in range(6):
            args = (PARENT, k, k + 1, k + 2, k + 3, k * 10, k * 10 + 5)
            self.assertEqual(RN.restore_regional(RN.regional_record(*args)), args)

    def test_exhaustive_partition_malformed_input_is_typed_refusal(self):
        """Nothing falls through: every malformed shape raises the module's OWN typed error, not a
        generic exception and not a plausible wrong answer.

        THE DECLARED DOMAIN INCLUDES `bytearray`, AND THE FIRST VERSION OF THIS TEST DID NOT KNOW
        THAT. It listed `bytearray(rec)` among the malformed shapes and failed. The module is right
        and the test was wrong: `restore_regional` opens with
        `type(buf) is bytes or type(buf) is bytearray`, an explicit and deliberate widening, and a
        well-formed bytearray therefore round-trips by design. Recorded rather than quietly fixed,
        because it is the first defect in this sequence caught by EXECUTION rather than by a reader
        — which is what relocating the work into a gated falsifier was supposed to buy."""
        rec = RN.regional_record(PARENT, 1, 2, 3, 4, 10, 20)
        self.assertEqual(RN.restore_regional(bytearray(rec)),
                         RN.restore_regional(rec),
                         "bytearray is inside the declared domain and must round-trip")
        for bad in (b"", b"x" * len(rec), rec[:-1], rec + b"x"):
            with self.assertRaises(RN.RanError) as ctx:
                RN.restore_regional(bad)
            self.assertEqual(ctx.exception.code, "RAN-REFUSE")
        for outside in ("a string", 17, None, memoryview(rec), list(rec)):
            with self.assertRaises(RN.RanError) as ctx:
                RN.restore_regional(outside)
            self.assertEqual(ctx.exception.code, "RAN-REFUSE",
                             "a type outside the declared domain must be a TYPED refusal")

    def test_refusal_is_total_over_out_of_domain_scalars(self):
        for bad_parent in ("", "z" * 64, PARENT[:-1]):
            with self.assertRaises(RN.RanError):
                RN.regional_record(bad_parent, 1, 2, 3, 4, 10, 20)
        with self.assertRaises(RN.RanError):
            RN.regional_record(PARENT, -1, 2, 3, 4, 10, 20)


class CommuteCollapse(unittest.TestCase):
    """The commutation certificate: a proof object that order cannot matter."""

    def test_exhaustive_partition_contested_write_is_refused_not_ranked(self):
        """The same cell twice has NO rank. A system that returned one anyway would be inventing an
        order — the exact 'plausible wrong answer' an exhaustive partition exists to forbid."""
        with self.assertRaises(CM.CommuteError) as ctx:
            CM.predict(16, 5, 5, 5, 5)
        self.assertEqual(ctx.exception.code, "COMMUTE-REFUSE")

    def test_extensional_prediction_is_a_function_of_the_cells_alone(self):
        first = CM.predict(16, 1, 2, 3, 4)
        for _ in range(5):
            self.assertEqual(CM.predict(16, 1, 2, 3, 4), first)

    def test_partition_is_exhaustive_over_the_swept_domain(self):
        """Every distinct-cell pair yields a rank; every same-cell pair refuses. No third outcome —
        which is what makes the partition exhaustive rather than merely typed (L60)."""
        ranked = refused = 0
        for xa in range(4):
            for ya in range(4):
                for xb in range(4):
                    for yb in range(4):
                        if (xa, ya) == (xb, yb):
                            with self.assertRaises(CM.CommuteError):
                                CM.predict(16, xa, ya, xb, yb)
                            refused += 1
                        else:
                            self.assertIn(CM.predict(16, xa, ya, xb, yb), (0, 1))
                            ranked += 1
        self.assertEqual(ranked + refused, 256)
        self.assertEqual(refused, 16, "exactly the diagonal must refuse")

    def test_refusal_is_typed_on_out_of_domain_scalars(self):
        for bad in ((0, 1, 2, 3, 4), (16, -1, 2, 3, 4), (16, 1, 2, 3, "x")):
            with self.assertRaises(CM.CommuteError):
                CM.predict(*bad)


class LeaseCollapse(unittest.TestCase):
    """The write capability: cheap admission proven equal to the full global reproof."""

    def test_extensional_identical_dependencies_give_identical_leases(self):
        self.assertEqual(LS.lease_record(PARENT, 7, 8), LS.lease_record(PARENT, 7, 8))

    def test_extensional_distinct_dependencies_never_collide(self):
        seen = {}
        for kx in range(6):
            for ky in range(6):
                rec = LS.lease_record(PARENT, kx, ky)
                self.assertNotIn(rec, seen, "lease collision at %s vs %s" % ((kx, ky), seen.get(rec)))
                seen[rec] = (kx, ky)
        self.assertEqual(len(seen), 36)

    def test_unique_reconstruction_and_tamper_is_refused(self):
        """The digest is what makes reconstruction unique: a single flipped bit must be REFUSED
        rather than repaired, or the record no longer determines the state."""
        rec = LS.lease_record(PARENT, 7, 8)
        self.assertEqual(LS.restore_lease(rec)[:3], (PARENT, 7, 8))
        caught = 0
        for i in (4, 20, len(rec) - 1):
            bad = bytearray(rec)
            bad[i] ^= 0xFF
            with self.assertRaises(LS.LeaseError) as ctx:
                LS.restore_lease(bytes(bad))
            self.assertEqual(ctx.exception.code, "LEASE-REFUSE")
            caught += 1
        self.assertEqual(caught, 3, "every planted bit-flip must be refused")

    def test_exhaustive_partition_malformed_lease_is_typed_refusal(self):
        rec = LS.lease_record(PARENT, 7, 8)
        for bad in (b"", b"y" * len(rec), rec[:-1], rec + b"z"):
            with self.assertRaises(LS.LeaseError) as ctx:
                LS.restore_lease(bad)
            self.assertEqual(ctx.exception.code, "LEASE-REFUSE")


class TheMatrixIsHonest(unittest.TestCase):
    """The falsifier on the REPORTING, not on the modules. The matrix in this file's docstring and
    in the ledger must not claim a cell that no test above measures."""

    def test_well_foundedness_is_declared_not_measured(self):
        """A self-parenting record would need a hash fixed point and cannot be constructed, so
        well-foundedness here is STRUCTURAL and this suite does NOT measure it. The check is that
        the claim stays honest: constructing a record whose parent is its own digest is not
        attempted, and no test above is named as if it were."""
        names = [m for cls in (RannullCollapse, CommuteCollapse, LeaseCollapse)
                 for m in dir(cls) if m.startswith("test_")]
        self.assertFalse([n for n in names if "well_founded" in n],
                         "no test may be named for a hypothesis this suite does not measure")

    def test_evidence_types_are_the_declared_five(self):
        """The taxonomy must not grow a sixth status by accident. Any cell status this suite reports
        has to be one of the five named in the module docstring — a matrix whose vocabulary drifts
        is a matrix whose earlier rows mean something different from its later ones."""
        declared = {"EXECUTED", "EXHAUSTIVE", "STRUCTURAL", "DECLARED", "N/A"}
        self.assertEqual(set(MATRIX_STATUSES), declared)
        for mod, cells in MATRIX.items():
            for hypothesis, status in cells.items():
                self.assertIn(status, declared,
                              "%s/%s reports an undeclared evidence type %r"
                              % (mod, hypothesis, status))

    def test_no_cell_claims_more_than_this_suite_runs(self):
        """The honesty falsifier, generalised from the well-foundedness case. A cell may claim
        EXECUTED or EXHAUSTIVE only if a test method exists whose name carries that hypothesis for
        that module. STRUCTURAL, DECLARED and N/A cells must have NO such method — otherwise the
        matrix is claiming evidence the suite does not produce."""
        by_module = {"rannull": RannullCollapse, "commute": CommuteCollapse, "lease": LeaseCollapse}
        for mod, cells in MATRIX.items():
            names = [m for m in dir(by_module[mod]) if m.startswith("test_")]
            for hypothesis, status in cells.items():
                key = hypothesis.split("_")[0]
                has_test = any(key in n for n in names)
                if status in ("EXECUTED", "EXHAUSTIVE"):
                    self.assertTrue(has_test,
                                    "%s/%s claims %s with no test naming it"
                                    % (mod, hypothesis, status))
                else:
                    self.assertFalse(has_test,
                                     "%s/%s is %s yet a test is named for it — the cell claims "
                                     "evidence this suite does not produce" % (mod, hypothesis, status))

    def test_every_module_under_test_has_a_typed_refusal_class(self):
        for mod, code in ((RN, "RAN-REFUSE"), (CM, "COMMUTE-REFUSE"), (LS, "LEASE-REFUSE")):
            err = [getattr(mod, n) for n in dir(mod)
                   if n.endswith("Error") and isinstance(getattr(mod, n), type)]
            self.assertTrue(err, "%s has no typed error class" % mod.__name__)
            raised = err[0]("x")
            self.assertEqual(getattr(raised, "code", None), code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
