# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""budget — THE DEFECT BUDGET AS A MONOTONE RESOURCE (URDRBGT1): the composition law turned from
passive knowledge into active enforcement. NO NEW GLYPH.

THE MOVE, AND IT IS THE RIGHT ONE. `jurisdiction` decided `defect(A ∪ B) ≤ defect(A) + defect(B)` in
cells and left it a theorem about composition. This rung spends it: a shard declares a total budget
in CELLS, every admitted capture is charged its measured defect, and a charge that would take the
remainder below zero REFUSES. Three thresholds become one resource, and the unit is the one S2, S6
and the jurisdictional predicate already share.

SOUNDNESS RUNS THE RIGHT WAY, AND THAT IS WHY THIS WORKS AT ALL. Charging per part and summing can
only OVER-charge, never under-charge, because subadditivity bounds the union by the sum. So a budget
that survives per-part accounting has certainly survived the true total. Decided over the pinned
family: 0 under-charges. And the conservatism is PRICED rather than hidden — on overlapping parts the
per-part sum exceeds the union defect, and the worst over-charge is reported as a number, because an
accounting scheme that silently drifts pessimistic is one that eventually refuses honest work.

ON PREFIX-DISJOINT SHARDS IT IS EXACT. Half B's structural commutation gives equality, not slack:
disjoint supports contribute disjoint forbidden cells, so `sum == union` with no covariance term.
Decided over every disjoint pair, 0 exceptions. That is what makes tiling sound — a city is not one
block with one budget, it is prefix-partitioned tiles whose budgets compose to the shard total
because the partition is forced by the word and the composition is forced by the law.

    THREE CORRECTIONS TO THE DESIGN THIS RUNG WAS WRITTEN TO, EACH MEASURED RATHER THAN ARGUED.

(1) THERE ARE NO REFUNDS, AND A REFUND IS NOT A TUNING CHOICE — IT VOIDS THE MECHANISM. The proposal
    credited budget back when a block passes, on the reasoning that good captures are cheaper to
    verify. That creates a PUMP: submit clean blocks, accumulate credit, spend it on a bad one.
    Measured here — with refunds enabled, 4 trivially-clean submissions buy one violating block that
    the honest ledger refuses, and the ratio is set by the refund rate, so a patient submitter buys
    ANY defect. The budget must be MONOTONE NON-INCREASING, which is the same well-founded descent on
    (ℕ, <) that `liveness` needed one rung earlier and for the same reason: a quantity that can go
    back up has no termination argument and therefore no bound.

(2) MODALITY CREDITS ARE REFUSED, BY THE PROPOSAL'S OWN SAFEGUARD. Giving LiDAR bonus tolerance over
    RGB-only photogrammetry requires knowing the modality, and the modality is not readable from the
    lattice — it is a field the submitter fills in. The design states the correct rule ("charged
    against actual lattice operations, not submitted claims") and then proposes a feature that
    breaks it. Measured: a modality-credited ledger admits a capture the lattice-only ledger refuses,
    purely because the submitter typed the favourable word. Jurisdictional variation is kept, because
    "this region has a tighter budget" is a SERVER-SIDE policy keyed on a location the server reads
    off the lattice; modality is a claim about the sensor, and `jurisdiction` exists precisely
    because claims about how a capture was produced are not evidence.

(3) THE PRIVILEGE LANE IS A STRUCTURAL FIREWALL, NOT A FLAG. The proposal's second-class lane is
    right that not all geometry serves the same function — but a tier that the authority path can
    READ is a tier the authority path can be talked into honouring. `authoritative_admit` therefore
    takes no privilege argument and structurally cannot take one, exactly as `tierview`'s visibility
    predicate cannot take a tier; the cosmetic lane is a separate function whose verdict is
    unreachable from the authority path. Decided: the authoritative verdict is invariant across every
    privilege value, a single value over the whole family.

THE COST IS COMPUTED, NEVER PASSED. `charge_for` takes a lattice and returns a cost; there is no
parameter through which a submitted number could enter the accounting. That is the same structural
move as (3) and it is what keeps this from becoming another provenance claim.

GRADE. MEASURED: soundness (0 under-charges over the pinned family); exactness on prefix-disjoint
pairs, 0 exceptions; the over-charge drift on overlapping parts, reported as a worst case rather than
elided; the well-founded descent (exactly B unit charges succeed, the next refuses, no clamp); the
refund pump ratio; the modality-credit admission; the authoritative verdict's invariance under
privilege; determinism. DECLARED: the budget is a POLICY NUMBER — this rung enforces an allocation, it
does not derive one, and what B should be for a real shard is not a question the arc can answer from
inside; the defect sources are `jurisdiction`'s exclusion-zone predicate and a cell-count quantization
model, both inheriting their own declared boundaries. does_not_show: that a within-budget capture is
CORRECT — the budget bounds admitted defect, never truth, and a capture can be entirely wrong at zero
cost; what a cell is WORTH, since cells are commensurable by construction here and a real deployment
may find a jurisdictional cell and a quantization cell are not equally bad; any bound on an adversary
who can influence the DECLARED budget, which is a governance surface this rung does not model."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import jurisdiction as _JR                                          # noqa: E402

MAGIC = b"URDRBGT1"
SHARD_BUDGET = 6                 # cells of tolerated defect per shard — a POLICY number, declared
REFUND_RATE = 1                  # the plant's credit per clean block
STRICT_REGION_BUDGET = 2         # server-side jurisdictional variation, keyed on location


class BudgetError(Exception):
    def __init__(self, message):
        super().__init__(f"BUDGET-REFUSE: {message}")
        self.code = "BUDGET-REFUSE"


class Overdrawn(Exception):
    """The ledger refuses. A charge that would take the remainder below zero is not clamped, not
    warned about, and not deferred."""
    def __init__(self, message):
        super().__init__(f"BUDGET-OVERDRAWN: {message}")
        self.code = "BUDGET-OVERDRAWN"


# ---- the cost is computed, never passed --------------------------------------------------------------
def charge_for(occupancy):
    """THE COST OF A CAPTURE, READ OFF THE LATTICE. There is no parameter here through which a
    submitted number could enter the accounting — that absence is the whole defence against the
    budget becoming another provenance claim."""
    return _JR.defect(occupancy)


def charge(remaining, cost):
    """PURE INTEGER SUBTRACTION, no clamp. A charge that would take the remainder below zero raises,
    so the ledger is monotone non-increasing on (ℕ, <) and its termination is structural — the same
    well-founded descent `liveness` needed, for the same reason."""
    if type(remaining) is not int or type(cost) is not int:
        raise BudgetError(f"ledger values must be int, got {remaining!r}, {cost!r}")
    if cost < 0:
        raise BudgetError("a negative charge is a refund, and refunds void the bound")
    nxt = remaining - cost
    if nxt < 0:
        raise Overdrawn(f"charge {cost} exceeds remaining {remaining}")
    return nxt


def spend(budget, blocks):
    """Admit captures in order until the budget refuses. Returns (admitted, remaining)."""
    remaining, admitted = budget, 0
    for b in blocks:
        try:
            remaining = charge(remaining, charge_for(b))
        except Overdrawn:
            return admitted, remaining
        admitted += 1
    return admitted, remaining


# ---- soundness: per-part accounting never under-charges ------------------------------------------------
def soundness_census():
    """DECIDED over every pair in `jurisdiction`'s pinned family: the per-part sum is never BELOW the
    union defect, so a budget that survives per-part accounting has survived the true total. Returns
    (pairs, undercharges, overcharges, worst_overcharge)."""
    blocks = _JR._blocks()
    pairs = under = over = worst = 0
    for a, b in _comb(blocks, 2):
        pairs += 1
        per_part = charge_for(a) + charge_for(b)
        union = charge_for(a | b)
        if per_part < union:
            under += 1
        elif per_part > union:
            over += 1
            worst = max(worst, per_part - union)
    return pairs, under, over, worst


def accounting_is_sound():
    p, u, _o, _w = soundness_census()
    return p > 0 and u == 0


def exactness_on_disjoint_census():
    """DECIDED: on PREFIX-DISJOINT parts the sum equals the union exactly — no slack, no covariance
    term — which is what makes prefix-partitioned tiling sound. Returns
    (disjoint_pairs, exceptions, total)."""
    blocks = _JR._blocks()
    dis = exc = total = 0
    for a, b in _comb(blocks, 2):
        total += 1
        if not _JR.prefix_disjoint_cells(a, b):
            continue
        dis += 1
        if charge_for(a) + charge_for(b) != charge_for(a | b):
            exc += 1
    return dis, exc, total


def disjoint_charging_is_exact():
    d, e, t = exactness_on_disjoint_census()
    return d > 0 and e == 0 and d < t


def conservatism_is_priced():
    """THE PRICE OF THE SAFE DIRECTION, stated rather than elided: on OVERLAPPING parts the per-part
    sum exceeds the union, so the ledger drifts pessimistic and eventually refuses honest work.
    Returns (overcharging_pairs, worst_overcharge, pairs)."""
    pairs, _u, over, worst = soundness_census()
    return over, worst, pairs


# ---- the well-founded descent ---------------------------------------------------------------------------
def unit_descent(budget=SHARD_BUDGET):
    """DECIDED: with unit charges exactly `budget` succeed and the next refuses. No clamp, and the
    remainder is never negative. Returns (succeeded, refused, budget)."""
    remaining, n = budget, 0
    while True:
        try:
            remaining = charge(remaining, 1)
        except Overdrawn:
            return n, True, budget
        n += 1
        if n > budget + 5:
            return n, False, budget


def descent_is_well_founded(budget=SHARD_BUDGET):
    n, refused, b = unit_descent(budget)
    return refused and n == b


def remainder_never_goes_negative(budget=SHARD_BUDGET):
    seen, remaining = [], budget
    for _ in range(budget + 4):
        try:
            remaining = charge(remaining, 1)
        except Overdrawn:
            break
        seen.append(remaining)
    return (min(seen) if seen else -1), all(v >= 0 for v in seen)


def jurisdictional_variation(strict=STRICT_REGION_BUDGET, loose=SHARD_BUDGET):
    """SERVER-SIDE POLICY, KEYED ON LOCATION — kept, because the server reads the region off the
    lattice. A stricter region admits strictly fewer of the same captures. Returns
    (strict_admitted, loose_admitted)."""
    blocks = [b for b in _JR._blocks() if charge_for(b) > 0] * 3
    return spend(strict, blocks)[0], spend(loose, blocks)[0]


# ---- the plants -------------------------------------------------------------------------------------------
def _charge_with_refund(remaining, cost, refund=REFUND_RATE):
    """A FALSIFIER TOOL: the proposal's refund. Credit budget back when a block passes clean, on the
    reasoning that good captures are cheaper to verify. It reads as generous and it removes the
    bound."""
    if cost == 0:
        return remaining + refund
    nxt = remaining - cost
    if nxt < 0:
        raise Overdrawn("refunding ledger overdrawn")
    return nxt


def refund_pump(target_cost=4, budget=SHARD_BUDGET):
    """The plant BITES, and it does not merely leak — it VOIDS the bound. Count the clean submissions
    needed to buy a block the honest ledger refuses. Returns
    (clean_needed, bought, honest_refuses)."""
    clean = frozenset({(0, 0, 0)})
    remaining, n = 0, 0
    while remaining < target_cost and n < 10_000:
        remaining = _charge_with_refund(remaining, charge_for(clean))
        n += 1
    bought = remaining >= target_cost
    try:
        charge(0, target_cost)
        honest_refuses = False
    except Overdrawn:
        honest_refuses = True
    return n, bought, honest_refuses


def refunds_void_the_bound():
    """Stated so it can be false: with refunds the reachable budget is UNBOUNDED in the number of
    clean submissions, so no allocation constrains anything. Returns (at_100, at_1000, honest_cap)."""
    clean = frozenset({(0, 0, 0)})
    out = []
    for rounds in (100, 1000):
        remaining = 0
        for _ in range(rounds):
            remaining = _charge_with_refund(remaining, charge_for(clean))
        out.append(remaining)
    return out[0], out[1], SHARD_BUDGET


def _charge_with_modality_credit(remaining, cost, declared_modality):
    """A FALSIFIER TOOL: bonus tolerance for a favoured sensor. The modality is NOT readable from the
    lattice — it is a field the submitter fills in — so this is a client-supplied number entering the
    accounting, which the design's own safeguard forbids."""
    credit = 3 if declared_modality == "lidar" else 0
    nxt = remaining + credit - cost
    if nxt < 0:
        raise Overdrawn("modality-credited ledger overdrawn")
    return nxt


def modality_credit_admits_what_the_lattice_refuses():
    """The plant BITES: the SAME capture, admitted or refused purely by the word the submitter typed.
    Returns (admitted_as_lidar, refused_as_rgb, refused_by_lattice_only)."""
    violating = frozenset({(33, 33, 33), (33, 33, 34), (33, 34, 33)})
    cost, start = charge_for(violating), 1

    def _try(fn, *a):
        try:
            fn(*a)
            return True
        except Overdrawn:
            return False

    return (_try(_charge_with_modality_credit, start, cost, "lidar"),
            not _try(_charge_with_modality_credit, start, cost, "rgb"),
            not _try(charge, start, cost))


# ---- the privilege firewall ----------------------------------------------------------------------------------
def authoritative_admit(occupancy, remaining):
    """THE AUTHORITY PATH. It takes no privilege argument and structurally cannot take one — the same
    move as `tierview`'s visibility predicate, which cannot accept a tier. Integrity-critical paths
    are exact-or-refuse."""
    charge(remaining, charge_for(occupancy))
    return True


def cosmetic_admit(occupancy, remaining, privilege):
    """THE SECOND-CLASS LANE, for rendering and exploration where the geometry is informational rather
    than authoritative. It exists, it is separate, and nothing it returns is reachable from
    `authoritative_admit`."""
    if privilege not in ("full", "partial", "none"):
        raise BudgetError(f"unknown privilege {privilege!r}")
    if privilege == "none":
        return False
    if privilege == "full":
        return authoritative_admit(occupancy, remaining)
    return charge_for(occupancy) <= remaining + 2


def authority_is_invariant_under_privilege():
    """DECIDED: the authoritative verdict does not move with privilege, because it cannot see it.
    Returns the set of verdicts observed across every privilege value — it must be a single value."""
    occ = frozenset({(33, 33, 33)})
    seen = set()
    for _p in ("full", "partial", "none"):
        try:
            seen.add(authoritative_admit(occ, 0))
        except Overdrawn:
            seen.add(False)
    return tuple(sorted(seen))


def the_lanes_are_separable():
    """The cosmetic lane can admit what the authority path refuses — that is its POINT — and the
    separation is structural rather than a flag. Returns (authority_refuses, cosmetic_admits)."""
    occ = frozenset({(33, 33, 33)})
    try:
        authoritative_admit(occ, 0)
        auth = False
    except Overdrawn:
        auth = True
    return auth, cosmetic_admit(occ, 0, "partial")


# ---- digests + scenes ------------------------------------------------------------------------------------------
def bg_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_accounting():
    return bg_digest("accounting", f"{soundness_census()}:{accounting_is_sound()}:"
                                   f"{exactness_on_disjoint_census()}:{disjoint_charging_is_exact()}:"
                                   f"{conservatism_is_priced()}")


def _scene_descent():
    return bg_digest("descent", f"{unit_descent()}:{descent_is_well_founded()}:"
                                f"{remainder_never_goes_negative()}:{jurisdictional_variation()}")


def _scene_plants():
    return bg_digest("plants", f"{refund_pump()}:{refunds_void_the_bound()}:"
                               f"{modality_credit_admits_what_the_lattice_refuses()}:"
                               f"{authority_is_invariant_under_privilege()}:"
                               f"{the_lanes_are_separable()}")


_SCENES = {"accounting": _scene_accounting, "descent": _scene_descent, "plants": _scene_plants}
SCENES = ("accounting", "descent", "plants")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_budget.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out.append(ln)
    return tuple(out)


def emitted_matches_pinned():
    return conformance_lines() == pinned_lines()


def golden(name):
    for ln in pinned_lines():
        nm, dig = ln.split()
        if nm == name:
            return dig
    raise BudgetError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"soundness (pairs, under, over, worst_over) {soundness_census()} -> {accounting_is_sound()}")
    print(f"exact on disjoint (disjoint, exc, total) {exactness_on_disjoint_census()} -> "
          f"{disjoint_charging_is_exact()}")
    print(f"conservatism priced (over_pairs, worst, pairs) {conservatism_is_priced()}")
    print(f"unit descent (succeeded, refused, budget) {unit_descent()} -> well-founded "
          f"{descent_is_well_founded()}")
    print(f"remainder in N (min, all_nonneg) {remainder_never_goes_negative()}")
    print(f"jurisdictional variation (strict, loose) {jurisdictional_variation()}")
    print(f"REFUND PUMP (clean_needed, bought, honest_refuses) {refund_pump()}")
    print(f"refunds void the bound (at_100, at_1000, honest_cap) {refunds_void_the_bound()}")
    print(f"modality credit (lidar_admits, rgb_refuses, lattice_refuses) "
          f"{modality_credit_admits_what_the_lattice_refuses()}")
    print(f"authority invariant under privilege {authority_is_invariant_under_privilege()} | "
          f"lanes separable {the_lanes_are_separable()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
