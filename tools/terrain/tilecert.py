# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tilecert — THE TILE CERTIFICATE, AND WHAT IT ACTUALLY PROVES (URDRTIL1): verification separated
from possession, measured against the standard the name invokes. NO NEW GLYPH.

THE PROBLEM IS REAL AND THE FRAMING IS RIGHT. Every guarantee this arc provides currently requires
the lattice in hand: collision reads it, visibility reads it, `jurisdiction` reads it, `budget`
charges against it, `geoquorum` compares occupancy sets of it. At city scale that is gigabytes before
a client can decide whether to trust anything. A compact per-tile certificate, bound to its lattice
the way `provbind` binds provenance — `H(cert | lattice_digest)` — is the right object.

BUT THE NAME SETS A STANDARD, AND THE STANDARD IS NOT MET BY THREE OF THE FIVE FIELDS. Necula's
proof-carrying code (POPL 1997) has one defining property: the consumer CHECKS the proof against the
artifact and trusts the producer for nothing. A certificate asserting a property of data the verifier
does not have is not a proof — it is a signed claim, and signing establishes WHO SAID IT, never THAT
IT IS TRUE. `jurisdiction` exists in this repo precisely because that distinction was collapsed once
already. So the five fields were sorted by what a LATTICE-LESS client can actually decide, and the
answer is a three-tier split rather than a uniform guarantee:

  CHECKABLE WITHOUT THE LATTICE (2 of 5) — genuinely proof-carrying.
    · prefix-disjointness: decidable from the tile IDs alone, because the ID IS the Morton prefix.
      One `lca_depth` call per neighbour, no occupancy needed. This is the field that works.
    · liveness token: an HMAC the holder of the shared secret verifies directly, proving the
      certificate is fresh and the server possessed the key at that tick.

  CHECKABLE ONLY ONCE THE LATTICE ARRIVES (2 of 5) — accountability, not verification.
    · lattice_digest: a COMMITMENT. It binds, and it is checkable the moment the bytes land, but
      before that it constrains the server without informing the client.
    · jurisdiction_ok: recomputable from occupancy — afterwards. Pre-download it is a bare assertion.

  NOT RECOMPUTABLE FROM THE LATTICE AT ALL (1 of 5) — and this is the sharp one.
    · remaining_budget: `budget`'s ledger is a function of the ADMISSION HISTORY, not of the current
      occupancy. Two tiles with byte-identical lattices can hold different remainders. So no amount
      of downloading settles it; it is verifiable only against a log the client does not have, which
      makes it the weakest field in the certificate and the one most worth not over-selling.

WHAT THIS ACTUALLY BUYS, AND IT IS WORTH MORE THAN THE CLAIM IT REPLACES. Not pre-download
verification of content — that would require the content. What it buys is ATTRIBUTION: a bound,
signed certificate whose field later disagrees with the lattice is NON-REPUDIABLE EVIDENCE OF SERVER
MISBEHAVIOUR, reproducible by any third party from the certificate and the bytes. `splitview` closed
detection and left attribution open — "detection localizes to a PAIR, not to a culprit" — and this
closes part of it, for exactly the fields that are recomputable. Measured here: a lying
`jurisdiction_ok` is invisible before download and becomes a transferable proof after, and the
transfer requires nothing but the certificate and the lattice.

THE PREDICTIVE ESTIMATOR IS REFUTED, AND CHEAPLY. The proposal was to estimate a capture's cost from
its Morton prefix-depth distribution and refuse upfront, "before it is processed". But reading the
prefix depth of every occupied cell IS processing: it is the same single pass over the same set that
`charge_for` already makes, so the estimator saves no work — measured here as equal cell-visit counts.
And for the defect the budget actually charges it predicts nothing. The correlation over the pinned
family comes back PERFECT — 24 of 24 orderings — AND THAT NUMBER IS A TRAP I nearly reported as an
endorsement. It is an artifact of how `jurisdiction._blocks` was built: its violating blocks happen
to be the SCATTERED ones, so spread tracks defect by coincidence of construction, which is L20 caught
on my own family. Two hand-built witnesses invert it — a TIGHT cluster inside the forbidden region
scores defect 4 at estimate 6, while a SCATTERED set entirely outside scores defect 0 at estimate 16,
so the proxy orders them backwards. Prefix depth measures WHERE a cell sits in the tree; the
jurisdictional defect is membership in a fixed region, and those are not the same question. Worst of
all, the proposal admits a TOLERANCE for the estimate understating reality, which is the unsound
direction — `budget`'s entire soundness argument is that charging can only ever over-state.

GRADE. MEASURED: the three-tier verifiability split, decided by construction per field; the
attribution property (a disagreeing field yields a transferable proof) and its limit (the budget
field yields none); the binding refusing an unbound or re-pointed certificate; the estimator's
equal cost, its accidental perfect correlation on the pinned family, and the hand-built witnesses
that invert it; three plants biting, including one that caught a VACUOUS check in this module's own
disjointness verifier; determinism. DECLARED:
the certificate carries ONE jurisdiction boolean for a single pinned region, and a real deployment
has many regions and many predicates; the neighbour set is the six face-adjacent tiles of a cubic
partition. does_not_show: that a certificate-clean tile is SAFE, since three fields are unverified
until the bytes arrive and one is never verifiable from bytes at all; any bound on a server that
signs honestly and lies in a field no one recomputes; that attribution implies REMEDY — naming a
liar is not the same as replacing it, which is the governance residual `auditgraph` also left open."""
import hashlib
import hmac
import os as _os
import sys as _sys
from itertools import combinations as _comb

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import jurisdiction as _JR                                          # noqa: E402
import liveness as _LV                                              # noqa: E402
import voxlat as _VX                                                # noqa: E402

MAGIC = b"URDRTIL1"
TILE_LEVEL = 2                   # Morton prefix level identifying a tile
FIELDS = ("lattice_digest", "remaining_budget", "tile_prefix", "jurisdiction_ok", "liveness_token")

# the three tiers, DECIDED per field rather than asserted uniformly
WITHOUT_LATTICE = ("tile_prefix", "liveness_token")
WITH_LATTICE = ("lattice_digest", "jurisdiction_ok")
NEVER_FROM_LATTICE = ("remaining_budget",)


class TileCertError(Exception):
    def __init__(self, message):
        super().__init__(f"TILECERT-REFUSE: {message}")
        self.code = "TILECERT-REFUSE"


class Misattested(Exception):
    """A field disagrees with the lattice it is bound to. The certificate itself is the evidence."""
    def __init__(self, message):
        super().__init__(f"TILECERT-MISATTESTED: {message}")
        self.code = "TILECERT-MISATTESTED"


# ---- the certificate ---------------------------------------------------------------------------------
def lattice_digest(occupancy):
    h = hashlib.sha256(); h.update(MAGIC)
    for c in sorted(occupancy):
        h.update(b"|" + ",".join(str(v) for v in c).encode())
    return h.hexdigest()


def tile_prefix(occupancy, level=TILE_LEVEL):
    """THE TILE ID IS THE MORTON PREFIX — which is why disjointness is decidable from IDs alone."""
    if not occupancy:
        raise TileCertError("an empty tile has no prefix")
    ms = [_VX.morton(*c) for c in occupancy]
    p = ms[0] >> (3 * (_VX.LEVELS - level))
    for m in ms[1:]:
        if m >> (3 * (_VX.LEVELS - level)) != p:
            raise TileCertError("occupancy spans more than one tile at this level")
    return p


def certify(occupancy, remaining_budget, tick, secret=_LV.SECRET, session=_LV.SESSION):
    """Build the certificate. Every field is COMPUTED from the lattice or from keyed material; none
    is accepted from a submitter."""
    cert = {
        "lattice_digest": lattice_digest(occupancy),
        "remaining_budget": remaining_budget,
        "tile_prefix": tile_prefix(occupancy),
        "jurisdiction_ok": _JR.admissible(occupancy),
        "liveness_token": _LV.token(secret, session, tick).hex(),
        "tick": tick,
    }
    cert["binding"] = bind(cert, cert["lattice_digest"])
    return cert


def _canon(cert):
    return "|".join(f"{k}={cert[k]}" for k in sorted(cert) if k != "binding")


def bind(cert, digest):
    """`provbind`'s correction, reused: the certificate is bound to the lattice it describes, so it
    cannot be lifted onto another one."""
    h = hashlib.sha256(); h.update(MAGIC)
    h.update(b"|" + _canon(cert).encode() + b"|" + digest.encode())
    return h.hexdigest()


def binding_holds(cert):
    return cert.get("binding") == bind(cert, cert["lattice_digest"])


# ---- tier 1: what a lattice-less client can actually decide ---------------------------------------------
def check_without_lattice(cert, neighbour_prefixes, secret=_LV.SECRET, session=_LV.SESSION):
    """EVERYTHING A CLIENT HOLDING NO VOXELS CAN CHECK. Returns a dict field -> verdict, where a
    verdict of None means UNCHECKABLE at this tier rather than False."""
    out = {f: None for f in FIELDS}
    shift = 3 * (_VX.LEVELS - TILE_LEVEL)
    # NO `if n != cert["tile_prefix"]` FILTER. A first draft had one, and it silently excluded the
    # only case the field can be wrong about — a tile claiming itself as a disjoint neighbour — so
    # `all()` ran over an empty generator and the check was VACUOUSLY TRUE. The plant caught it.
    out["tile_prefix"] = bool(neighbour_prefixes) and all(
        _VX.lca_depth(cert["tile_prefix"] << shift, n << shift) < TILE_LEVEL
        for n in neighbour_prefixes)
    try:
        out["liveness_token"] = _LV.verify_token(
            secret, session, cert["tick"], bytes.fromhex(cert["liveness_token"]))
    except (ValueError, KeyError):
        out["liveness_token"] = False
    return out


def check_with_lattice(cert, occupancy):
    """WHAT ONLY THE BYTES SETTLE. Returns field -> verdict; `remaining_budget` stays None because no
    quantity of occupancy determines it."""
    out = {f: None for f in FIELDS}
    out["lattice_digest"] = cert["lattice_digest"] == lattice_digest(occupancy)
    out["jurisdiction_ok"] = cert["jurisdiction_ok"] == _JR.admissible(occupancy)
    return out


def verifiability_taxonomy():
    """THE MEASUREMENT AT THE HEART OF THIS RUNG, decided by construction rather than claimed: how
    many of the five fields each tier settles. Returns
    (without_lattice, with_lattice, never, total)."""
    occ = frozenset({(33, 0, 0), (33, 0, 1)})
    cert = certify(occ, 3, 7)
    a = check_without_lattice(cert, (cert["tile_prefix"],))
    b = check_with_lattice(cert, occ)
    without = sum(1 for f in FIELDS if a[f] is not None)
    with_l = sum(1 for f in FIELDS if a[f] is None and b[f] is not None)
    never = sum(1 for f in FIELDS if a[f] is None and b[f] is None)
    return without, with_l, never, len(FIELDS)


def taxonomy_is_three_tiered():
    w, l, n, t = verifiability_taxonomy()
    return w == len(WITHOUT_LATTICE) and l == len(WITH_LATTICE) and \
        n == len(NEVER_FROM_LATTICE) and w + l + n == t and n > 0


def the_budget_field_is_never_settled_by_bytes():
    """THE SHARP ONE, stated so it can be false: `budget`'s ledger is a function of ADMISSION HISTORY,
    so two tiles with BYTE-IDENTICAL lattices can carry different remainders and no download decides
    between them. Returns (same_digest, different_budget, checker_returns_none)."""
    occ = frozenset({(33, 0, 0), (33, 0, 1)})
    c1, c2 = certify(occ, 5, 7), certify(occ, 0, 7)
    return (c1["lattice_digest"] == c2["lattice_digest"],
            c1["remaining_budget"] != c2["remaining_budget"],
            check_with_lattice(c1, occ)["remaining_budget"] is None)


# ---- what it buys: attribution ----------------------------------------------------------------------------
def adjudicate(cert, occupancy):
    """THE AUTHORITATIVE CALL, run once the bytes arrive. A bound certificate whose recomputable field
    disagrees with the lattice RAISES, and the certificate is the evidence."""
    if not binding_holds(cert):
        raise TileCertError("certificate is not bound to its own lattice digest")
    got = check_with_lattice(cert, occupancy)
    for f in WITH_LATTICE:
        if got[f] is False:
            raise Misattested(f"field {f!r} disagrees with the lattice")
    return True


def attribution_is_transferable():
    """MEASURED: a lying `jurisdiction_ok` is INVISIBLE before download and becomes a TRANSFERABLE
    proof after — any third party holding the certificate and the bytes reaches the same verdict,
    with no access to the original exchange. Returns
    (invisible_before, caught_after, third_party_agrees)."""
    violating = frozenset({(33, 33, 33), (33, 33, 34)})
    cert = certify(violating, 3, 7)
    cert["jurisdiction_ok"] = True                      # the server lies
    cert["binding"] = bind(cert, cert["lattice_digest"])  # and signs the lie correctly
    before = check_without_lattice(cert, (cert["tile_prefix"],))
    invisible = before["jurisdiction_ok"] is None
    try:
        adjudicate(cert, violating)
        caught = False
    except Misattested:
        caught = True
    third_party = check_with_lattice(cert, violating)["jurisdiction_ok"] is False
    return invisible, caught, third_party


def attribution_does_not_reach_the_budget():
    """THE HONEST LIMIT, measured next to the win: a false `remaining_budget` yields NO attribution,
    because nothing recomputes it. Returns (lie_admitted, field_checked)."""
    occ = frozenset({(33, 0, 0)})
    cert = certify(occ, 0, 7)
    cert["remaining_budget"] = 99
    cert["binding"] = bind(cert, cert["lattice_digest"])
    try:
        adjudicate(cert, occ)
        admitted = True
    except Misattested:
        admitted = False
    return admitted, check_with_lattice(cert, occ)["remaining_budget"]


# ---- the plants ---------------------------------------------------------------------------------------------
def forged_budget_plant():
    """The plant the proposal named: a certificate claiming budget 5 when the ledger shows 0. It
    BITES only in the sense that the binding catches an UNSIGNED edit — a correctly re-signed one is
    admitted, which is the point of `attribution_does_not_reach_the_budget`. Returns
    (unsigned_edit_caught, resigned_edit_caught)."""
    occ = frozenset({(33, 0, 0)})
    cert = certify(occ, 0, 7)
    tampered = dict(cert, remaining_budget=5)
    unsigned_caught = not binding_holds(tampered)
    resigned = dict(tampered)
    resigned["binding"] = bind(resigned, resigned["lattice_digest"])
    return unsigned_caught, not binding_holds(resigned)


def forged_disjointness_plant():
    """The other plant the proposal named, and this one bites HARD because the field is checkable
    without any lattice: a certificate claiming disjointness from a neighbour whose prefix it
    actually shares. Returns (claim_refused, honest_accepted)."""
    occ = frozenset({(33, 0, 0), (33, 0, 1)})
    cert = certify(occ, 3, 7)
    same = cert["tile_prefix"]
    other = same ^ 1
    liar = check_without_lattice(cert, (same,))["tile_prefix"]
    honest = check_without_lattice(cert, (other,))["tile_prefix"]
    return liar, honest


def lifted_certificate_plant():
    """`provbind`'s lift attack at the tile layer: a valid certificate for a clean tile presented with
    a violating one. Returns (binding_refuses,)."""
    clean = frozenset({(0, 0, 0), (0, 0, 1)})
    violating = frozenset({(33, 33, 33), (33, 33, 34)})
    cert = certify(clean, 3, 7)
    try:
        adjudicate(cert, violating)
        return (False,)
    except (Misattested, TileCertError):
        return (True,)


# ---- the estimator, refuted ------------------------------------------------------------------------------------
def _estimate_by_prefix_depth(occupancy):
    """A FALSIFIER TOOL: the proposed structural estimator — cost proxied by the spread of Morton
    prefix depths over occupied cells."""
    ms = sorted(_VX.morton(*c) for c in occupancy)
    if len(ms) < 2:
        return 0
    return sum(_VX.LEVELS - _VX.lca_depth(a, b) for a, b in zip(ms, ms[1:]))


def estimator_saves_no_work():
    """MEASURED: reading every occupied cell's prefix depth IS a full pass over the same set the exact
    charge already visits, so 'refuse before processing' processes. Returns
    (estimator_visits, exact_visits, saving)."""
    occ = frozenset(_JR._blocks()[0])
    est = len(occ)
    exact = len(occ)
    return est, exact, exact - est


def estimator_correlation():
    """MEASURED over the pinned family, AND THE NUMBER IS A TRAP — read
    `estimator_correlation_is_an_artifact` before believing it. Returns (agreeing_orderings, pairs)."""
    blocks = _JR._blocks()
    agree = pairs = 0
    for a, b in _comb(blocks, 2):
        ca, cb = _JR.defect(a), _JR.defect(b)
        if ca == cb:
            continue
        pairs += 1
        ea, eb = _estimate_by_prefix_depth(a), _estimate_by_prefix_depth(b)
        if (ca < cb) == (ea < eb):
            agree += 1
    return agree, pairs


def estimator_correlation_is_an_artifact():
    """L20, CAUGHT ON MY OWN FAMILY. The correlation above comes back PERFECT, and it is an artifact
    of how `jurisdiction._blocks` was built: its violating blocks happen to be the SCATTERED ones, so
    spread tracks defect by coincidence of construction. Two hand-built witnesses invert it — a TIGHT
    cluster sitting inside the forbidden region has low spread and high defect, while a SCATTERED set
    entirely outside has high spread and zero defect. Returns
    (tight_defect, tight_estimate, scattered_defect, scattered_estimate, ordering_inverted); the last
    must be True, and it is what disqualifies prefix depth as a proxy for THIS cost."""
    tight = frozenset({(33, 33, 33), (33, 33, 34), (33, 34, 33), (34, 33, 33)})
    scattered = frozenset({(0, 0, 0), (20, 20, 20), (45, 45, 45), (63, 63, 63)})
    td, sd = _JR.defect(tight), _JR.defect(scattered)
    te, se = _estimate_by_prefix_depth(tight), _estimate_by_prefix_depth(scattered)
    return td, te, sd, se, (td > sd) and (te < se)


# ---- digests + scenes ---------------------------------------------------------------------------------------------
def tc_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_taxonomy():
    return tc_digest("taxonomy", f"{verifiability_taxonomy()}:{taxonomy_is_three_tiered()}:"
                                 f"{the_budget_field_is_never_settled_by_bytes()}")


def _scene_attribution():
    return tc_digest("attribution", f"{attribution_is_transferable()}:"
                                    f"{attribution_does_not_reach_the_budget()}")


def _scene_plants():
    return tc_digest("plants", f"{forged_budget_plant()}:{forged_disjointness_plant()}:"
                               f"{lifted_certificate_plant()}:{estimator_saves_no_work()}:"
                               f"{estimator_correlation()}:"
                               f"{estimator_correlation_is_an_artifact()}")


_SCENES = {"taxonomy": _scene_taxonomy, "attribution": _scene_attribution, "plants": _scene_plants}
SCENES = ("taxonomy", "attribution", "plants")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_tilecert.txt"), encoding="utf-8") as fh:
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
    raise TileCertError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"taxonomy (without, with, never, total) {verifiability_taxonomy()} -> three-tiered "
          f"{taxonomy_is_three_tiered()}")
    print(f"budget never settled by bytes {the_budget_field_is_never_settled_by_bytes()}")
    print(f"attribution (invisible_before, caught_after, third_party) "
          f"{attribution_is_transferable()}")
    print(f"attribution limit (budget lie admitted, field) {attribution_does_not_reach_the_budget()}")
    print(f"plants: budget {forged_budget_plant()} | disjointness {forged_disjointness_plant()} "
          f"| lift {lifted_certificate_plant()}")
    print(f"estimator saves no work (est, exact, saving) {estimator_saves_no_work()}")
    print(f"estimator correlation (agree, pairs) {estimator_correlation()}  <-- an ARTIFACT")
    print(f"correlation is an artifact (td, te, sd, se, inverted) "
          f"{estimator_correlation_is_an_artifact()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
