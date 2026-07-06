#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""A Value-of-Information decision gate — a small, buildable runtime engine.

WHAT THIS IS. A decision boundary a pipeline can evaluate continuously:
    Decision(a) = [ value_per_bit · VoI(a) − Cost(a) > ρ ]
where VoI(a) is the EXPECTED reduction in uncertainty (mutual information, in
bits) that action a produces, Cost(a) is its operational overhead, and ρ is an
irreversibility / risk margin. A fuzz run, an extra test, a formal proof, and a
human review are all the same object: each produces information, consumes
resources, and moves confidence — they differ only in the measured numbers.

WHAT THIS IS NOT. Not the Urðr language core. This is FLOAT arithmetic
(entropy uses log2), so it is a separate tool with its OWN runner
(`python tools/voi_gate/test_voi_gate.py`); it is deliberately NOT sealed by
`verify.py`, whose gate is integer-exact and deterministic by design law.
Provenance: the observable-projector lens (D1 §18) gave the invariant pattern
(signal vs overhead); this replaces the projector with measurable accounting.
`projection = theoretical lens ; VoI + cost ledger = runtime mechanism`.

TWO CORRECTIONS BAKED IN (from the design discussion):
  1. VoI is MUTUAL INFORMATION I(X;O) = H(X) − E_o[H(X|O=o)] ≥ 0 always. A single
     surprising observation can *raise* conditional entropy; only the EXPECTED
     value is guaranteed non-negative, so we compute the expectation.
  2. bits ≠ cost. `value_per_bit` is an explicit exchange rate; without it,
     `VoI − Cost` subtracts cost units from bits (a hidden units error).

HONEST GRADE. The engine is testable and tested (this file's falsifiers). The
CLAIM that it "improves software outcomes" is NOT established here — that needs
longitudinal deployment data, which is exactly what `Pipeline.calibration()`
is built to collect. Until those numbers exist, outcome-improvement is
SPECULATIVE (see tools/voi_gate/README.md and D5)."""
import json
import math
import sys


def entropy(dist) -> float:
    """Shannon entropy in bits of a probability distribution (iterable of p)."""
    return -sum(p * math.log2(p) for p in dist if p > 0.0)


def expected_voi_bits(prior, likelihood) -> float:
    """Mutual information I(X;O) in bits = H(X) − Σ_o P(o)·H(X|O=o) ≥ 0.

    prior:      P(X=x)         — list over states x, sums to 1.
    likelihood: P(O=o | X=x)   — rows[x][o].
    Returns the EXPECTED information gain (never a single-observation drop, which
    could be negative). Tiny negative float noise is clamped to 0; MI ≥ 0 exactly.
    """
    n_x = len(prior)
    n_o = len(likelihood[0])
    joint = [[prior[x] * likelihood[x][o] for o in range(n_o)]
             for x in range(n_x)]
    p_o = [sum(joint[x][o] for x in range(n_x)) for o in range(n_o)]
    h_x = entropy(prior)
    h_x_given_o = 0.0
    for o in range(n_o):
        if p_o[o] <= 0.0:
            continue
        post = [joint[x][o] / p_o[o] for x in range(n_x)]
        h_x_given_o += p_o[o] * entropy(post)
    return max(0.0, h_x - h_x_given_o)


def binary_diagnostic_voi(prior_bug: float, sensitivity: float,
                          specificity: float) -> float:
    """Expected info (bits) of a binary test for X ∈ {ok, bug}.
    sensitivity = P(pos | bug), specificity = P(neg | ok)."""
    prior = [1.0 - prior_bug, prior_bug]           # [ok, bug]
    likelihood = [
        [specificity, 1.0 - specificity],          # X=ok:  [P(neg), P(pos)]
        [1.0 - sensitivity, sensitivity],          # X=bug: [P(neg), P(pos)]
    ]
    return expected_voi_bits(prior, likelihood)


def worth_running(delta_h_bits: float, cost: float, margin: float = 0.0,
                  value_per_bit: float = 1.0) -> bool:
    """A check is worth running only if its information exceeds cost + margin;
    otherwise it is ceremony (ΔH > C + ρ)."""
    return value_per_bit * delta_h_bits - cost > margin


def attempted_claim(candidate, observed_delta_bits, requested_grade="MEASURED"):
    """Emit an ATTEMPTED claim — never a grade. This tool measures ΔH (float,
    provenance); it does NOT mint evidence. In the Urðr model ᛞ is the sole
    constructor of Grounded: the pipeline PROPOSES, the mint ADJUDICATES. The
    returned dict carries `requested_grade`, never a granted one."""
    return {
        "candidate": candidate,
        "observed_delta_bits": round(float(observed_delta_bits), 6),
        "requested_grade": requested_grade,
        "note": "attempted claim only; the mint (ᛞ) alone constructs Grounded",
    }


class Action:
    """A pipeline action: it produces information (voi_bits), consumes resources
    (cost), and carries a margin ρ (irreversibility premium). The decision is
    dimensionally honest: value_per_bit converts bits into cost units."""

    def __init__(self, name, voi_bits, cost, margin=0.0, value_per_bit=1.0):
        self.name = name
        self.voi_bits = float(voi_bits)
        self.cost = float(cost)
        self.margin = float(margin)
        self.value_per_bit = float(value_per_bit)

    def value(self) -> float:
        return self.value_per_bit * self.voi_bits

    def net(self) -> float:
        return self.value() - self.cost

    def gate(self) -> bool:
        return self.net() > self.margin

    def efficiency(self) -> float:
        """η = V / (V + Co) ∈ [0, 1]: the flow-efficiency share of this action
        (value produced over value + overhead). Dimensionless."""
        v = self.value()
        denom = v + self.cost
        return v / denom if denom > 0.0 else 0.0

    def report(self) -> dict:
        return {
            "action": self.name,
            "uncertainty_removed_bits": round(self.voi_bits, 6),
            "cost_units": round(self.cost, 6),
            "margin": round(self.margin, 6),
            "efficiency": round(self.efficiency(), 6),
            "decision": "GREEN" if self.gate() else "RED",
        }


class Pipeline:
    """Evaluates actions and keeps a decision ledger. The engine does NOT assert
    that high-VoI actions prevent failures — it LOGS the decisions and the
    realized outcomes so that claim is falsifiable once data exists.
    `calibration()` is that falsifier surface: it returns tallies, not a verdict."""

    def __init__(self):
        self.ledger = []

    def evaluate(self, action: "Action") -> dict:
        row = action.report()
        self.ledger.append(row)
        return row

    def record_outcome(self, action_name: str, prevented_failure: bool) -> bool:
        for row in reversed(self.ledger):
            if row["action"] == action_name and "outcome" not in row:
                row["outcome"] = bool(prevented_failure)
                return True
        return False

    def calibration(self) -> dict:
        greens = [r for r in self.ledger
                  if r["decision"] == "GREEN" and "outcome" in r]
        reds = [r for r in self.ledger
                if r["decision"] == "RED" and "outcome" in r]
        return {
            "green_n": len(greens),
            "green_prevented": sum(1 for r in greens if r["outcome"]),
            "red_n": len(reds),
            "red_prevented": sum(1 for r in reds if r["outcome"]),
        }


def _cli(argv) -> int:
    """Three-output decision from the command line:
      voi_gate.py --bits B --cost C [--margin R] [--value-per-bit V]
      voi_gate.py --diagnostic PRIOR_BUG SENS SPEC --cost C [...]"""
    def opt(flag, default=None, cast=float):
        return cast(argv[argv.index(flag) + 1]) if flag in argv else default

    cost = opt("--cost", 0.0)
    margin = opt("--margin", 0.0)
    vpb = opt("--value-per-bit", 1.0)
    if "--diagnostic" in argv:
        i = argv.index("--diagnostic")
        p, sens, spec = (float(argv[i + 1]), float(argv[i + 2]),
                         float(argv[i + 3]))
        bits = binary_diagnostic_voi(p, sens, spec)
    else:
        bits = opt("--bits", 0.0)
    action = Action("cli", bits, cost, margin, vpb)
    r = action.report()
    sys.stdout.write(json.dumps({
        "uncertainty_removed_bits": r["uncertainty_removed_bits"],
        "cost_units": r["cost_units"],
        "decision": r["decision"],
    }, indent=2) + "\n")
    return 0 if action.gate() else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv))
