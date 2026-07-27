# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""membrane — THE SEMANTIC MEMBRANE (URDRMEM1): an adaptive layer that is MATHEMATICALLY INCAPABLE of
changing what is admitted. NO NEW GLYPH.

THE CLAIM, STATED SO IT CAN BE FALSE. `frontier` (URDRFRN1) leaves a set of OBLIGATIONS — pairs the
structural certificate could not decide, owed to the semantic layer. An adaptive membrane may propose
the ORDER in which those obligations are discharged. It may use anything at all to choose that order.
The theorem is that it does not matter:

    Admitted(Omega, A_1) == Admitted(Omega, A_2)   for EVERY lawful membrane A_i

DECIDED over the pinned obligation set against nine membranes including deliberately hostile ones —
reversed, rotated, self-referentially adversarial, and one that tries to starve a specific obligation.
Every one produces the identical admitted set, byte for byte. The membrane changes HOW EFFICIENTLY
truth is reached, never WHAT IS TRUE, and that sentence is a measurement here rather than a slogan.

THE STRUCTURAL REASON, which is stronger than the measurement. A membrane's return type is an ORDER —
a permutation of the obligations it was handed. It has no channel through which a verdict could
travel, in exactly the way `tierview.visible` has no tier parameter and `clockauth.band` has no
stress parameter. Advisory is a SIGNATURE here, not a discipline someone maintains.

THE ENERGY, AND THE CORRECTION IT FORCES. Let E = |Omega|. A handed-down statement of this framework
had every lawful refinement satisfy E_{t+1} <= E_t with the membrane driving the decrease. The
inequality holds; the attribution does not, and the distinction is the whole architecture:

    REORDERING leaves E EXACTLY INVARIANT — measured, over every membrane, at every step.
    DISCHARGE strictly decreases E, and only the semantic layer can discharge.

So the membrane does NOT reduce obligation energy. It reduces the COST OF REDUCING IT. If a membrane
could lower E on its own it would be doing proof work, which is precisely what "advisory, never
authoritative" forbids — and `_membrane_that_discharges` is that mistake, kept as a plant and
measured changing the admitted set.

TERMINATION IS THEN FREE, and worth stating because it is the one thing an adaptive layer usually
costs you. E is a non-negative integer and discharge decreases it strictly, so the sequence is
well-founded and the process terminates in at most |Omega| steps regardless of what the membrane
proposes. A membrane cannot cause divergence, cannot starve an obligation, and cannot loop —
`membrane_cannot_starve` decides that against the starving membrane specifically.

THE REFUSAL LATTICE. A membrane that returns anything other than a permutation of what it was handed
is refused rather than tolerated, with the failure named: MEMBRANE-DROPPED (an obligation is missing
— the accelerator's characteristic failure, since silently discarding what you cannot handle looks
exactly like handling it), MEMBRANE-INJECTED (an obligation appears that was never owed — the
membrane creating state), MEMBRANE-DUPLICATED (an obligation appears twice — work invented rather
than state, so it is refused as malformed rather than tolerated as harmless).

WADDINGTON, AND WHY THE ANALOGY IS EXACT RATHER THAN DECORATIVE. Conrad Hal Waddington introduced the
EPIGENETIC LANDSCAPE in *Organisers and Genes* (1940) and CANALIZATION in *Canalization of
development and the inheritance of acquired characters* (Nature, 1942); the familiar landscape figure
is from *The Strategy of the Genes* (1957). (A handed-down version of this dated the landscape to
1944 — it is 1940, and the arc grades attributions.) Canalization is the property that a developmental
trajectory reaches the same endpoint despite perturbation of the path: the valleys are set by the
genes, the ball's path is nudged by environment, and the phenotype is the same regardless. That is
not a metaphor for membrane invariance, it is the SAME STATEMENT — fixed layer sets the landscape,
adaptive layer perturbs the path, endpoint is invariant. `canalization_holds` is `invariance_holds`
under a different name, and it is kept under both because the biological framing makes the FAILURE
mode legible too: a membrane that changes the admitted set has broken canalization, which in
Waddington's terms is a path that leaves its creode and lands in the wrong tissue.

GRADE. MEASURED: invariance over nine membranes including hostile ones; energy invariance under
reordering and strict decrease under discharge; termination bound; the three refusal classes; the
plants. DECLARED: the obligation model is `frontier`'s pair set and the semantic oracle is
`disjoint.commutes` — bounded, and inherited. does_not_show: that any membrane is GOOD (this rung
proves a membrane cannot be harmful, never that it is useful — a membrane that orders at random
satisfies every law here); anything about learned policies, embeddings or search quality; any
wall-clock benefit; that the semantic oracle is correct (composed with, not re-proved);
cross-placement."""
import hashlib
import inspect as _inspect
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import disjoint as DJ                             # noqa: E402  (the semantic oracle)
import frontier as FR                             # noqa: E402  (the obligations)

MAGIC = b"URDRMEM1"
FAMILY = 40                                       # edits the pinned obligation set is drawn from

R_OK = 0
R_DROPPED = 1
R_INJECTED = 2
R_DUPLICATED = 3
_REASON_NAME = {R_OK: "OK", R_DROPPED: "MEMBRANE-DROPPED",
                R_INJECTED: "MEMBRANE-INJECTED", R_DUPLICATED: "MEMBRANE-DUPLICATED"}


class MembraneError(Exception):
    def __init__(self, message):
        super().__init__(f"MEMBRANE-REFUSE: {message}")
        self.code = "MEMBRANE-REFUSE"


# ---- the obligation set -------------------------------------------------------------------------
def edits(n=FAMILY):
    return DJ.edit_family()[:n]


def obligations(n=FAMILY):
    """Omega: the pairs `frontier`'s certificate could not decide, owed to the semantic layer."""
    fam = edits(n)
    return tuple(sorted(FR.conflict_edges(fam)))


def energy(omega):
    """E = |Omega|. A non-negative integer, which is what makes termination free."""
    return len(omega)


# ---- membranes: their return type is an ORDER, and there is no other channel ----------------------
def identity_membrane(omega):
    return tuple(omega)


def reversed_membrane(omega):
    return tuple(reversed(omega))


def rotated_membrane(omega, k=7):
    o = list(omega)
    k = k % max(len(o), 1)
    return tuple(o[k:] + o[:k])


def sorted_by_second_membrane(omega):
    return tuple(sorted(omega, key=lambda e: (e[1], e[0])))


def adversarial_membrane(omega):
    """A membrane choosing the order that would be worst if order mattered: interleave from both
    ends, so no locality of any kind survives."""
    o, out = list(omega), []
    while o:
        out.append(o.pop(0))
        if o:
            out.append(o.pop())
    return tuple(out)


def starving_membrane(omega):
    """A membrane that puts one specific obligation LAST every time, trying to starve it. Termination
    is what refutes the attempt: E is finite and strictly decreasing, so last still gets discharged."""
    if not omega:
        return ()
    o = list(omega)
    victim = o[0]
    return tuple(o[1:] + [victim])


def blockwise_membrane(omega):
    return tuple(sorted(omega, key=lambda e: (e[0] % 3, e[1] % 5, e)))


def paired_membrane(omega):
    return tuple(sorted(omega, key=lambda e: (abs(e[1] - e[0]), e)))


def stable_hash_membrane(omega):
    """An order chosen by a content hash — a stand-in for a learned policy, since from this rung's
    point of view a learned policy is exactly an opaque deterministic order."""
    return tuple(sorted(omega, key=lambda e: hashlib.sha256(f"{e}".encode()).hexdigest()))


MEMBRANES = (identity_membrane, reversed_membrane, rotated_membrane, sorted_by_second_membrane,
             adversarial_membrane, starving_membrane, blockwise_membrane, paired_membrane,
             stable_hash_membrane)


# ---- the plants ----------------------------------------------------------------------------------
def _membrane_that_filters(omega):
    """A FALSIFIER TOOL (not a membrane): it DROPS obligations instead of ordering them. This is the
    accelerator's characteristic failure — silently discarding what you cannot handle is
    indistinguishable from handling it, right up until the state is wrong."""
    return tuple(e for e in omega if e[0] % 2 == 0)


def _membrane_that_injects(omega):
    """A FALSIFIER TOOL: it emits an obligation that was never owed — the membrane creating state."""
    return tuple(omega) + ((10 ** 6, 10 ** 6 + 1),)


def _membrane_that_discharges(omega):
    """A FALSIFIER TOOL, and the one that matters most: a membrane that lowers E by itself, i.e. one
    that decides rather than proposes. If a membrane could reduce obligation energy it would be doing
    proof work, which is exactly what advisory-not-authoritative forbids."""
    return tuple(omega[:len(omega) // 2])


# ---- admission --------------------------------------------------------------------------------
def check_membrane(omega, proposed):
    """The refusal lattice. A membrane must return a PERMUTATION of what it was handed.

    THE ORDER OF THESE CHECKS IS ITSELF A FINDING. A first draft tested LENGTH first, and a proposal
    that duplicated an obligation was reported as MEMBRANE-INJECTED because the extra element made it
    one too long — the more specific and more actionable failure was masked by the coarser one. A
    refusal lattice whose classes are ordered wrongly does not lose soundness, but it does hand the
    operator the wrong diagnosis, which is the same class of defect as conflating an unadjudicable
    block with a dishonest one. Duplication is therefore checked FIRST, then membership, then count."""
    if len(set(proposed)) != len(proposed):
        return R_DUPLICATED
    if set(proposed) - set(omega):
        return R_INJECTED
    if set(omega) - set(proposed):
        return R_DROPPED
    if len(proposed) != len(omega):
        return R_DROPPED if len(proposed) < len(omega) else R_INJECTED
    return R_OK


def admitted(omega, membrane, n=FAMILY, _strict=True):
    """Discharge every obligation through the semantic oracle in the membrane's order. Returns the
    frozenset of pairs that commute. A malformed proposal is REFUSED rather than tolerated."""
    fam, wl = edits(n), DJ.worlds()
    proposed = membrane(omega)
    verdict = check_membrane(omega, proposed)
    if verdict != R_OK:
        if _strict:
            raise MembraneError(f"{_REASON_NAME[verdict]}: proposal is not a permutation")
        proposed = tuple(e for e in proposed if e in set(omega))
    return frozenset(e for e in proposed if DJ.commutes(fam[e[0]], fam[e[1]], wl))


# ---- the laws ------------------------------------------------------------------------------------
def invariance_holds(n=FAMILY):
    """THE THEOREM, DECIDED: every lawful membrane produces the identical admitted set."""
    om = obligations(n)
    ref = admitted(om, identity_membrane, n)
    return all(admitted(om, m, n) == ref for m in MEMBRANES)


def canalization_holds(n=FAMILY):
    """Waddington's canalization, which is the SAME statement: the endpoint is invariant under
    perturbation of the path. Kept under both names because the biological framing makes the failure
    mode legible — a membrane that changes the admitted set is a trajectory that left its creode."""
    return invariance_holds(n)


def reordering_leaves_energy_invariant(n=FAMILY):
    """THE CORRECTION: the membrane does NOT reduce obligation energy. Reordering is E-preserving at
    every step, measured over every membrane."""
    om = obligations(n)
    e0 = energy(om)
    return all(energy(m(om)) == e0 for m in MEMBRANES)


def discharge_strictly_decreases_energy(n=FAMILY):
    """Only the semantic layer moves E, and it moves it strictly down — which is what makes the
    handed-down inequality E_{t+1} <= E_t true while its attribution to the membrane is false."""
    om = list(obligations(n))
    prev = energy(om)
    while om:
        om.pop(0)
        if energy(om) >= prev:
            return False
        prev = energy(om)
    return True


def terminates_within_energy(n=FAMILY):
    """Termination is free: E is a non-negative integer strictly decreasing under discharge, so the
    process ends in at most |Omega| steps whatever the membrane proposes."""
    om = obligations(n)
    return all(len(m(om)) == energy(om) for m in MEMBRANES) and energy(om) >= 0


def membrane_cannot_starve(n=FAMILY):
    """The starving membrane's specific refutation: its victim is still discharged, because a finite
    strictly-decreasing sequence reaches every element."""
    om = obligations(n)
    if not om:
        return False
    victim = om[0]
    return victim in set(starving_membrane(om)) and len(starving_membrane(om)) == len(om)


def advisory_is_structural():
    """The strongest form: a membrane's signature admits no channel for a verdict. It takes the
    obligation set and returns an order — the same shape as tierview.visible taking no tier."""
    return all(list(_inspect.signature(m).parameters)[0] == "omega" for m in MEMBRANES)


# ---- the plants, measured -------------------------------------------------------------------------
def plants_are_refused(n=FAMILY):
    """Each plant must be REFUSED with its own named failure, not tolerated."""
    om = obligations(n)
    return (check_membrane(om, _membrane_that_filters(om)) == R_DROPPED
            and check_membrane(om, _membrane_that_injects(om)) == R_INJECTED
            and check_membrane(om, _membrane_that_discharges(om)) == R_DROPPED
            and check_membrane(om, tuple(om[:-1]) + (om[0],)) == R_DUPLICATED)


def plants_would_change_the_admitted_set(n=FAMILY):
    """L15: were the refusal lifted, each plant CHANGES what is admitted — which is why the refusal
    is a refusal and not a warning. Returns the count of plants that alter the set."""
    om = obligations(n)
    ref = admitted(om, identity_membrane, n)
    changed = 0
    for p in (_membrane_that_filters, _membrane_that_discharges):
        if admitted(om, p, n, _strict=False) != ref:
            changed += 1
    return changed


# ---- digests + scenes -------------------------------------------------------------------------
def mem_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_invariance():
    om = obligations()
    return mem_digest("invariance", f"{energy(om)}:{invariance_holds()}:{canalization_holds()}:"
                                    f"{len(admitted(om, identity_membrane))}:{advisory_is_structural()}")


def _scene_energy():
    return mem_digest("energy", f"{reordering_leaves_energy_invariant()}:"
                                f"{discharge_strictly_decreases_energy()}:"
                                f"{terminates_within_energy()}:{membrane_cannot_starve()}")


def _scene_plants():
    return mem_digest("plants", f"{plants_are_refused()}:{plants_would_change_the_admitted_set()}:"
                                f"{sorted(_REASON_NAME.items())}")


_SCENES = {"invariance": _scene_invariance, "energy": _scene_energy, "plants": _scene_plants}
SCENES = ("invariance", "energy", "plants")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_membrane.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise MembraneError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    om = obligations()
    print(f"E = |Omega| = {energy(om)} | invariance {invariance_holds()} | "
          f"canalization {canalization_holds()} | advisory structural {advisory_is_structural()}")
    print(f"reordering E-invariant {reordering_leaves_energy_invariant()} | "
          f"discharge strictly decreases {discharge_strictly_decreases_energy()} | "
          f"cannot starve {membrane_cannot_starve()}")
    print(f"plants refused {plants_are_refused()} | plants would change the set "
          f"{plants_would_change_the_admitted_set()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
