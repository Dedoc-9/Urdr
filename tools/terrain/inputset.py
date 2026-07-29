# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""inputset — WHICH INPUTS DETERMINE A QUANTITY (URDRINP1): the arc-wide state-versus-path
classifier, decided by underdetermination witness rather than tabulated. NO NEW GLYPH.

WHAT THIS IS AND WHY IT IS NOT A TABLE. `tilecert` established for ONE field that occupancy does not
determine the ledger remainder, and `tilemin` used that to keep it off the certificate. The general
question — for every quantity the arc computes, what is the SMALLEST input set that determines it —
is what decides where a quantity may live: inline on a certificate, in the payload, or only in a
published log. A hand-written taxonomy would be an opinion. This decides it:

    a quantity belongs to the COARSEST level whose projection determines it, and the tier is proved
    by exhibiting a WITNESS PAIR that the next-coarser level does NOT determine it

So every classification carries its own falsifier. Claim a quantity is certificate-local and the
classifier looks for two situations with identical certificates and different values; if one exists
the claim dies. Nothing is asserted that a witness search could not have refuted.

THE LEVELS ARE NESTED, which is what makes "coarsest" well defined: CERT ⊂ LATTICE ⊂ HISTORY ⊂
COHORT. Each adds strictly more information, so determination is monotone and the first level that
determines is unique.

THE PROPOSED THREE-TIER TAXONOMY MISFILES ONE QUANTITY, AND THE CLASSIFIER FOUND IT. The handed-down
design placed `quorum_agreement` in the post-download tier, alongside `jurisdiction_ok` and the
occupancy defect — verifiable "once the spatial bytes arrive". It is not. Downloading YOUR tile
settles nothing about whether a cohort of independent observers agrees with you, because agreement is
a function of OTHER PARTIES' submissions. Measured: two situations with identical certificate,
identical occupancy AND identical history differ in quorum agreement, so neither the payload nor the
log determines it.

    THERE ARE FOUR TIERS, NOT THREE, AND THE FOURTH IS PEER-DEPENDENT RATHER THAN PATH-DEPENDENT.

That distinction is the same shape as last turn's correction between a gauge obstruction and ordinary
accumulation: two quantities can be equally unverifiable from your own bytes and still need
completely different remedies. A path-dependent quantity is fixed by publishing the LOG. A
peer-dependent one is fixed by publishing the COHORT. Filing them together would tell a deployment
to build the wrong thing.

WHAT EACH TIER MEANS OPERATIONALLY. CERT: verifiable inline, before a byte of payload moves — this is
the only tier that may appear on `tilemin`'s minimal certificate. LATTICE: unverifiable up front,
recomputable once the payload lands, so it buys `tilecert`'s attribution rather than verification.
HISTORY: no download settles it; it needs an append-only log, and publishing that log genuinely fixes
it because the obstruction is accumulation and not symmetry. COHORT: no log of YOUR events settles
it either; it needs the peers' submissions, which is `geoquorum`'s object rather than this tile's.

GRADE. MEASURED: the tier of each of six arc quantities, decided by witness search over an enumerated
family; a refuting witness pinned for every quantity at the level below its tier, so no classification
is asserted where a search could have refuted it; the monotonicity of determination across the nested
levels; the misfiled quorum quantity and the witness that moves it; determinism. DECLARED: the family
is a small enumerated set of situations built to separate the levels — it can prove a quantity is NOT
determined at a level (one witness suffices) but "determined" is over THIS family rather than over all
possible situations, which is the honest asymmetry of a witness search and is the reason each
positive classification also ships its refuting witness one level down. does_not_show: that a
CERT-tier quantity is TRUE — determination is about which inputs fix a value, never about whether the
value is honest, and `tilemin` needed a separate recomputation check for exactly that reason; what a
quantity MEANS; any quantity outside the pinned six."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import budget as _BG                                                # noqa: E402
import jurisdiction as _JR                                          # noqa: E402
import liveness as _LV                                              # noqa: E402
import tilemin as _TM                                               # noqa: E402

MAGIC = b"URDRINP1"
LEVELS = ("CERT", "LATTICE", "HISTORY", "COHORT")
NOW = 6


class InputSetError(Exception):
    def __init__(self, message):
        super().__init__(f"INPUTSET-REFUSE: {message}")
        self.code = "INPUTSET-REFUSE"


# ---- a situation, and the nested projections ---------------------------------------------------------
def situation(occupancy, tick, history, cohort):
    """Everything that could possibly bear on a quantity, in one object."""
    return {"occupancy": frozenset(occupancy), "tick": tick,
            "history": tuple(history), "cohort": tuple(frozenset(c) for c in cohort)}


def proj(level, s):
    """THE NESTED PROJECTIONS. CERT ⊂ LATTICE ⊂ HISTORY ⊂ COHORT, so determination is monotone and
    'the coarsest level that determines' is unique."""
    if level not in LEVELS:
        raise InputSetError(f"unknown level {level!r}")
    cert = _TM.certify(s["occupancy"], s["tick"])
    base = (cert["tile_prefix"], cert["jurisdiction_region"], cert["liveness_token"], cert["tick"])
    if level == "CERT":
        return base
    if level == "LATTICE":
        return base + (tuple(sorted(s["occupancy"])),)
    if level == "HISTORY":
        return base + (tuple(sorted(s["occupancy"])), s["history"])
    return base + (tuple(sorted(s["occupancy"])), s["history"],
                   tuple(sorted(tuple(sorted(c)) for c in s["cohort"])))


# ---- the six arc quantities ---------------------------------------------------------------------------
def q_exclusion_membership(s):
    """tilemin's region — a pure function of the tile prefix and the published survey."""
    return _TM.region_of(_TM.tile_prefix(s["occupancy"]))


def q_prefix_disjointness(s, reference=0):
    """Half B's predicate against a fixed reference tile — decidable from IDs alone."""
    shift = 3 * (_TM._VX.LEVELS - _TM.TILE_LEVEL)
    import voxlat as _VX
    return _VX.lca_depth(_TM.tile_prefix(s["occupancy"]) << shift, reference << shift) \
        < _TM.TILE_LEVEL


def q_liveness_horizon(s, now=NOW):
    """liveness freshness at a fixed `now` — the certificate carries the tick and the token."""
    return 0 <= now - s["tick"] <= _TM.HORIZON


def q_occupancy_defect(s):
    """jurisdiction's defect in cells — needs the actual occupied cells, not just the tile."""
    return _JR.defect(s["occupancy"])


def q_ledger_remainder(s):
    """budget's monotone ledger, replayed from the history."""
    remaining = _BG.SHARD_BUDGET
    for cost in s["history"]:
        try:
            remaining = _BG.charge(remaining, cost)
        except _BG.Overdrawn:
            return -1
    return remaining


def q_quorum_agreement(s):
    """geoquorum's shape: how many cohort members' occupancy matches this submitter's. A function of
    OTHER PARTIES' state, which is what the handed-down taxonomy missed."""
    return sum(1 for c in s["cohort"] if c == s["occupancy"])


QUANTITIES = (
    ("exclusion_membership", q_exclusion_membership),
    ("prefix_disjointness", q_prefix_disjointness),
    ("liveness_horizon", q_liveness_horizon),
    ("occupancy_defect", q_occupancy_defect),
    ("ledger_remainder", q_ledger_remainder),
    ("quorum_agreement", q_quorum_agreement),
)


# ---- the family, built to SEPARATE the levels -----------------------------------------------------------
_IN_TILE_FORBIDDEN = frozenset({(33, 33, 33)})          # tile (2,2,2), defect 1
_IN_TILE_CLEAN = frozenset({(40, 40, 40)})              # SAME tile, defect 0
_OTHER_TILE = frozenset({(0, 0, 0)})                    # a different tile entirely


def family():
    """A small enumerated set of situations built so that each adjacent pair of levels is separated
    by at least one pair. If it were not, every quantity would classify as CERT-local for free — the
    same vacuity that has bitten this repo repeatedly."""
    out = []
    for occ in (_IN_TILE_FORBIDDEN, _IN_TILE_CLEAN, _OTHER_TILE):
        for tick in (5, 6):
            for hist in ((), (1,), (1, 2)):
                for coh in ((), (occ,), (_OTHER_TILE, _OTHER_TILE)):
                    out.append(situation(occ, tick, hist, coh))
    return tuple(out)


def family_separates_every_level():
    """L19 — the family must contain, for each adjacent level pair, at least one pair of situations
    agreeing at the coarser level and differing at the finer. Returns a tuple of counts, all > 0."""
    fam, counts = family(), []
    for coarse, fine in zip(LEVELS, LEVELS[1:]):
        n = sum(1 for a, b in _comb(fam, 2)
                if proj(coarse, a) == proj(coarse, b) and proj(fine, a) != proj(fine, b))
        counts.append(n)
    return tuple(counts)


# ---- the decision procedure ------------------------------------------------------------------------------
def determines(level, qfn, fam=None):
    """DOES `level` DETERMINE THE QUANTITY? Equal projections must give equal values. Returns
    (determined, witness) where the witness is the refuting pair when it does not."""
    fam = fam or family()
    for a, b in _comb(fam, 2):
        if proj(level, a) == proj(level, b) and qfn(a) != qfn(b):
            return False, (qfn(a), qfn(b))
    return True, None


def tier_of(name):
    """THE COARSEST LEVEL THAT DETERMINES, with the refuting witness from the level below. Returns
    (tier, witness_below) — `witness_below` is None only for CERT-tier quantities, which have no
    coarser level to be refuted at."""
    qfn = dict(QUANTITIES)[name]
    prev = None
    for level in LEVELS:
        ok, witness = determines(level, qfn)
        if ok:
            return level, prev
        prev = witness
    raise InputSetError(f"{name!r} is not determined even at the finest level")


def classification():
    """THE ARC-WIDE TABLE, DECIDED. Returns ((name, tier, refuting_witness_below), ...)."""
    return tuple((name, ) + tier_of(name) for name, _fn in QUANTITIES)


def every_classification_carries_a_refutation():
    """The discipline in one predicate: a quantity classified above CERT must ship the witness proving
    it is not classifiable lower. Returns (with_witness, cert_tier, total)."""
    rows = classification()
    with_w = sum(1 for _n, t, w in rows if t != "CERT" and w is not None)
    cert = sum(1 for _n, t, _w in rows if t == "CERT")
    return with_w, cert, len(rows)


def determination_is_monotone():
    """Once a level determines a quantity, every finer level does too — which is what makes the
    'coarsest' in `tier_of` meaningful rather than an artifact of iteration order."""
    for name, qfn in QUANTITIES:
        seen = [determines(lv, qfn)[0] for lv in LEVELS]
        if any(seen[i] and not seen[i + 1] for i in range(len(seen) - 1)):
            return False
    return True


# ---- the finding: the proposed taxonomy misfiles the quorum ------------------------------------------------
def quorum_is_peer_not_path():
    """THE CORRECTION, DECIDED. The handed-down taxonomy filed `quorum_agreement` in the
    post-download tier, verifiable "once the spatial bytes arrive". It is not: two situations with
    identical certificate, identical occupancy AND identical history differ in agreement, because
    agreement is a function of OTHER PARTIES' submissions. Returns
    (tier, lattice_determines, history_determines)."""
    qfn = dict(QUANTITIES)["quorum_agreement"]
    tier, _w = tier_of("quorum_agreement")
    return tier, determines("LATTICE", qfn)[0], determines("HISTORY", qfn)[0]


def path_and_peer_need_different_remedies():
    """WHY THE FOURTH TIER EARNS ITS PLACE rather than collapsing into the third: both are
    unverifiable from your own bytes, and the fixes are not interchangeable. Publishing the LOG
    determines the ledger and leaves the quorum undetermined. Returns
    (log_fixes_ledger, log_fixes_quorum)."""
    ledger = dict(QUANTITIES)["ledger_remainder"]
    quorum = dict(QUANTITIES)["quorum_agreement"]
    return determines("HISTORY", ledger)[0], determines("HISTORY", quorum)[0]


# ---- the plants -----------------------------------------------------------------------------------------
def _classify_by_assertion(name):
    """A FALSIFIER TOOL: the handed-down three-tier table, typed out rather than decided. It is right
    about five of six and wrong about the one that matters."""
    return {"exclusion_membership": "CERT", "prefix_disjointness": "CERT",
            "liveness_horizon": "CERT", "occupancy_defect": "LATTICE",
            "ledger_remainder": "HISTORY", "quorum_agreement": "LATTICE"}[name]


def asserted_table_disagrees(names=None):
    """The plant BITES on exactly one row, and it is the row a deployment would have built wrong.
    Returns (disagreements, total, the_disagreeing_row)."""
    names = names or [n for n, _f in QUANTITIES]
    bad = [(n, _classify_by_assertion(n), tier_of(n)[0])
           for n in names if _classify_by_assertion(n) != tier_of(n)[0]]
    return len(bad), len(names), tuple(bad)


def _determines_without_witness(level, qfn):
    """A FALSIFIER TOOL: 'it looks determined' — check a single situation against itself instead of
    searching for a refuting pair. It returns True for EVERY quantity at EVERY level, which is the
    vacuity a witness search exists to prevent."""
    s = family()[0]
    return proj(level, s) == proj(level, s) and qfn(s) == qfn(s)


def witnessless_check_is_vacuous():
    """The plant BITES everywhere at once: the lazy check classifies all six quantities as CERT-local.
    Returns (vacuously_true, total)."""
    n = sum(1 for _name, qfn in QUANTITIES if _determines_without_witness("CERT", qfn))
    return n, len(QUANTITIES)


# ---- digests + scenes -------------------------------------------------------------------------------------
def ip_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_classification():
    return ip_digest("classification", f"{classification()}:"
                                       f"{every_classification_carries_a_refutation()}:"
                                       f"{determination_is_monotone()}")


def _scene_correction():
    return ip_digest("correction", f"{quorum_is_peer_not_path()}:"
                                   f"{path_and_peer_need_different_remedies()}:"
                                   f"{asserted_table_disagrees()}")


def _scene_family():
    return ip_digest("family", f"{len(family())}:{family_separates_every_level()}:"
                               f"{witnessless_check_is_vacuous()}")


_SCENES = {"classification": _scene_classification, "correction": _scene_correction,
           "family": _scene_family}
SCENES = ("classification", "correction", "family")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_inputset.txt"), encoding="utf-8") as fh:
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
    raise InputSetError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"family {len(family())} situations, separations {family_separates_every_level()}")
    for name, tier, witness in classification():
        print(f"  {name:24} {tier:8} refuted-below {witness}")
    print(f"every classification carries a refutation {every_classification_carries_a_refutation()}")
    print(f"monotone {determination_is_monotone()}")
    print(f"QUORUM is peer not path {quorum_is_peer_not_path()}")
    print(f"log fixes (ledger, quorum) {path_and_peer_need_different_remedies()}")
    print(f"asserted table disagrees {asserted_table_disagrees()}")
    print(f"witnessless check vacuous {witnessless_check_is_vacuous()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
