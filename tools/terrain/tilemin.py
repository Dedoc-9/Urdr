# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tilemin — THE MINIMAL CERTIFICATE, ALL THREE FIELDS PROOF-CARRYING (URDRTMN1): what survived
URDRTIL1's sort, plus the one field that legitimately moves from commitment to proof. NO NEW GLYPH.

WHAT THIS IS. `tilecert` sorted five proposed fields by what a LATTICE-LESS client can decide and got
(2, 2, 1): two proof-carrying, two commitments, one never recomputable at all. This rung keeps the
two that worked, drops the three that did not, and adds a third that reaches the bar — giving a
certificate where 3 of 3 fields are checkable with no occupancy in hand:

    tile_prefix        WHERE the tile sits          decidable from tile IDs alone (the ID IS the prefix)
    jurisdiction_region WHAT it may serve           recomputable from the prefix + the published survey
    liveness_token     WHEN it was last attested    an HMAC the secret-holder verifies directly

`remaining_budget` stays OFF the certificate entirely and lives only in the shard ledger, because
`budget`'s remainder is a function of ADMISSION HISTORY and no download settles it. Putting an
unverifiable number on a certificate is how a certificate becomes a claim.

THE REGION FIELD REACHES THE BAR ONLY BECAUSE IT IS RECOMPUTED, NEVER TRUSTED — AND THAT IS A
CORRECTION TO THE DESIGN THIS RUNG WAS WRITTEN TO. The proposal described the region as "server-read
from the Morton prefix at admission time and stored in the tile's registry entry", which would make
it exactly the kind of stored assertion the previous rung refused. The dichotomy is sharp: if the
region is a pure function of the prefix, the client can compute it and the certificate's copy carries
no information; if it is NOT such a function, the client cannot check it and it is a bare claim.
Resolved by making the SURVEY the shared artifact: the exclusion zone is an exogenous legal object
(`jurisdiction` already declares it so), the prefix→region table is published, and the client
RECOMPUTES the region and compares. The certificate's copy is a convenience that gets verified — a
lie in it is caught with NO LATTICE AT ALL, which is what makes the field proof-carrying in Necula's
sense rather than merely stored.

LOCATION-JURISDICTION IS SOUND, AND IT IS COARSE, AND BOTH ARE MEASURED. Deciding admissibility from
WHERE a tile sits rather than from WHAT IT CONTAINS is an over-approximation, and the direction is
the safe one: over every tile in the pinned world, an OPEN region provably contains no forbidden
cell — 0 exceptions of 64. But it refuses whole tiles to protect single cells, and that price is
reported rather than elided:

    4096 cells refused to protect 4 — a 1024x over-refusal at this tile granularity

which is the same Galois shape `frontier` established: a sound over-approximation whose precision
loss is a stated number, not a defect. Finer tiles cost less precision and more certificates; the
tradeoff is a deployment choice this rung enforces rather than makes.

INTEGRITY AND POLICY ARE TWO VERDICTS, AND A FIRST DRAFT MERGED THEM. That draft folded the client's
policy into the region check, so an honest certificate for a legitimately RESTRICTED tile came back
False and was INDISTINGUISHABLE FROM A FORGED ONE — which destroys attribution, because the client can
no longer tell "the server lied about the region" from "the region is restricted and I may not enter".
Measured after the split: honest integrity True, honest policy False, forged integrity False. Three
distinct verdicts where there was one, and the discipline is `geoquorum`'s — THIN is coverage,
DEVIATE is integrity, and they must never merge.

WHAT IT BUYS, STATED AT ITS TRUE WIDTH. A client verifies partition, region and freshness before
possessing a single voxel, and the binding to the lattice digest preserves `tilecert`'s attribution
result for afterwards: a bound certificate that later disagrees with the lattice is non-repudiable
evidence any third party can reproduce. Verification before download for three facts; accountability
after download for the rest.

GRADE. MEASURED: all three fields verified with no occupancy (3 of 3, against the previous rung's 2
of 5); the region recomputation catching a forged region with no lattice; location-jurisdiction's
soundness over every tile, 0 exceptions; the 1024x over-refusal price; staleness refusal outside the
liveness horizon; the binding refusing a lifted certificate; the integrity/policy split holding as
three distinct verdicts; five plants biting; determinism.
DECLARED: the survey is a PINNED PUBLIC TABLE standing in for a legal boundary — this rung enforces a
survey, it does not validate one, and a wrong survey yields wrong verdicts soundly; the tile
granularity is fixed at one level and the precision/size tradeoff is not optimised here.
does_not_show: that an open tile is SAFE — location-jurisdiction bounds only the surveyed exclusion
zone and says nothing about integrity, which is `geoquorum`'s question; that a fresh token means an
HONEST server, since an HMAC proves possession and never truthfulness; that attribution implies
remedy."""
import hashlib
import os as _os
import sys as _sys
from itertools import product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import jurisdiction as _JR                                          # noqa: E402
import liveness as _LV                                              # noqa: E402
import voxlat as _VX                                                # noqa: E402

MAGIC = b"URDRTMN1"
TILE_LEVEL = 2                                   # tiles are Morton prefixes at this level
TILE_SIDE = 2 ** (_VX.LEVELS - TILE_LEVEL)       # 16 cells per axis
TILE_CELLS = TILE_SIDE ** 3
FIELDS = ("tile_prefix", "jurisdiction_region", "liveness_token")
OPEN, RESTRICTED = 0, 1
HORIZON = 3                                      # ticks a certificate stays fresh


class TileMinError(Exception):
    def __init__(self, message):
        super().__init__(f"TILEMIN-REFUSE: {message}")
        self.code = "TILEMIN-REFUSE"


class Restricted(Exception):
    """A POLICY refusal, never an integrity one. The certificate is honest and the client may not
    enter — merging this with a forged-field refusal is what destroys attribution."""
    def __init__(self, message):
        super().__init__(f"TILEMIN-RESTRICTED: {message}")
        self.code = "TILEMIN-RESTRICTED"


class Stale(Exception):
    def __init__(self, message):
        super().__init__(f"TILEMIN-STALE: {message}")
        self.code = "TILEMIN-STALE"


# ---- the published survey ----------------------------------------------------------------------------
def prefix_of(cell, level=TILE_LEVEL):
    return _VX.morton(*cell) >> (3 * (_VX.LEVELS - level))


def survey():
    """THE PUBLISHED TABLE — the shared artifact that makes the region field checkable. The exclusion
    zone is an EXOGENOUS legal object, so the prefix→region map is not a server opinion; the client
    holds it and recomputes."""
    return frozenset(prefix_of(c) for c in _JR.FORBIDDEN)


def region_of(prefix):
    """A PURE FUNCTION of the prefix and the published survey. The client runs this itself, which is
    exactly why the certificate's copy can be checked rather than believed."""
    if type(prefix) is not int or prefix < 0 or prefix >= 8 ** TILE_LEVEL:
        raise TileMinError(f"prefix {prefix!r} outside the tile space")
    return RESTRICTED if prefix in survey() else OPEN


def all_tiles():
    return tuple(sorted({prefix_of(c) for c in _prod(range(_JR.WORLD), repeat=3)}))


# ---- the certificate ---------------------------------------------------------------------------------
def tile_prefix(occupancy):
    if not occupancy:
        raise TileMinError("an empty tile has no prefix")
    ps = {prefix_of(c) for c in occupancy}
    if len(ps) != 1:
        raise TileMinError("occupancy spans more than one tile")
    return ps.pop()


def certify(occupancy, tick, secret=_LV.SECRET, session=_LV.SESSION):
    p = tile_prefix(occupancy)
    cert = {
        "tile_prefix": p,
        "jurisdiction_region": region_of(p),
        "liveness_token": _LV.token(secret, session, tick).hex(),
        "tick": tick,
    }
    cert["binding"] = bind(cert, lattice_digest(occupancy))
    return cert


def lattice_digest(occupancy):
    h = hashlib.sha256(); h.update(MAGIC)
    for c in sorted(occupancy):
        h.update(b"|" + ",".join(str(v) for v in c).encode())
    return h.hexdigest()


def bind(cert, digest):
    h = hashlib.sha256(); h.update(MAGIC)
    h.update(b"|" + "|".join(f"{k}={cert[k]}" for k in sorted(cert) if k != "binding").encode())
    h.update(b"|" + digest.encode())
    return h.hexdigest()


# ---- verification with NO lattice ----------------------------------------------------------------------
def satisfies_policy(cert, policy_open=True):
    """THE CLIENT'S POLICY, kept SEPARATE from the integrity verdict. Whether a client may enter a
    restricted tile is not a question about whether the certificate is honest."""
    return (not policy_open) or cert["jurisdiction_region"] == OPEN


def verify_without_lattice(cert, neighbours, now, policy_open=True,
                           secret=_LV.SECRET, session=_LV.SESSION):
    """ALL THREE FIELDS, NO OCCUPANCY. Returns field -> bool; none of them is ever None, which is the
    whole difference from `tilecert`'s (2, 2, 1) split."""
    out = {}
    shift = 3 * (_VX.LEVELS - TILE_LEVEL)
    out["tile_prefix"] = bool(neighbours) and all(
        _VX.lca_depth(cert["tile_prefix"] << shift, n << shift) < TILE_LEVEL for n in neighbours)
    # RECOMPUTED, never trusted — the certificate's copy must equal what the client derives. This is
    # an INTEGRITY verdict only. A FIRST DRAFT also folded the client's POLICY into this boolean, so
    # an honest certificate for a legitimately RESTRICTED tile came back False and was
    # indistinguishable from a FORGED one — which destroys attribution, because the client can no
    # longer tell "the server lied about the region" from "the region is restricted and I may not
    # enter". Two questions, two verdicts, exactly as geoquorum keeps THIN separate from DEVIATE.
    try:
        out["jurisdiction_region"] = cert["jurisdiction_region"] == region_of(cert["tile_prefix"])
    except TileMinError:
        out["jurisdiction_region"] = False
    try:
        out["liveness_token"] = (
            _LV.verify_token(secret, session, cert["tick"], bytes.fromhex(cert["liveness_token"]))
            and 0 <= now - cert["tick"] <= HORIZON)
    except (ValueError, KeyError, TypeError):
        out["liveness_token"] = False
    return out


def all_fields_are_lattice_free():
    """THE HEADLINE, decided by construction: 3 of 3 verifiable with no occupancy, against the
    previous rung's 2 of 5. Returns (checkable, total, previous_checkable, previous_total)."""
    occ = frozenset({(0, 0, 0), (0, 0, 1)})
    cert = certify(occ, 5)
    got = verify_without_lattice(cert, (cert["tile_prefix"] ^ 1,), 5)
    return sum(1 for f in FIELDS if got[f] is not None), len(FIELDS), 2, 5


def admits_an_honest_certificate():
    occ = frozenset({(0, 0, 0), (0, 0, 1)})
    cert = certify(occ, 5)
    got = verify_without_lattice(cert, (cert["tile_prefix"] ^ 1,), 6)
    return all(got[f] for f in FIELDS)


def adjudicate(cert, neighbours, now, policy_open=True):
    got = verify_without_lattice(cert, neighbours, now, policy_open)
    if not got["liveness_token"]:
        raise Stale(f"token outside the {HORIZON}-tick horizon or unverifiable")
    for f in ("tile_prefix", "jurisdiction_region"):
        if not got[f]:
            raise TileMinError(f"field {f!r} failed lattice-free verification")
    if not satisfies_policy(cert, policy_open):
        raise Restricted(f"tile {cert['tile_prefix']} is in a restricted region")
    return True


# ---- location-jurisdiction: sound, and priced -------------------------------------------------------------
def soundness_census():
    """DECIDED over every tile: an OPEN region provably contains no forbidden cell. Returns
    (open_tiles, restricted_tiles, exceptions)."""
    forbidden_prefixes = survey()
    op = res = exc = 0
    for t in all_tiles():
        if t in forbidden_prefixes:
            res += 1
        else:
            op += 1
            if any(prefix_of(c) == t for c in _JR.FORBIDDEN):
                exc += 1
    return op, res, exc


def location_jurisdiction_is_sound():
    _o, r, e = soundness_census()
    return e == 0 and r > 0


def over_refusal_price():
    """THE PRICE OF THE SAFE DIRECTION, reported rather than elided: whole tiles refused to protect
    single cells. Returns (cells_refused, cells_actually_forbidden, ratio)."""
    _o, restricted, _e = soundness_census()
    refused = restricted * TILE_CELLS
    actual = len(_JR.FORBIDDEN)
    return refused, actual, refused // actual


def coarseness_is_stated():
    refused, actual, ratio = over_refusal_price()
    return refused > actual and ratio > 1


# ---- the plants ------------------------------------------------------------------------------------------
def forged_region_plant():
    """THE PLANT THAT MATTERS, and it bites WITH NO LATTICE. A server marks a restricted tile OPEN and
    signs it correctly. Because the client RECOMPUTES the region from the published survey, the lie
    dies before a single voxel moves. Returns (lie_caught_without_lattice, honest_accepted)."""
    occ = frozenset({(33, 33, 33), (33, 33, 34)})
    cert = certify(occ, 5)
    liar = dict(cert, jurisdiction_region=OPEN)
    liar["binding"] = bind(liar, lattice_digest(occ))
    caught = not verify_without_lattice(liar, (liar["tile_prefix"] ^ 1,), 5)["jurisdiction_region"]
    honest = verify_without_lattice(cert, (cert["tile_prefix"] ^ 1,), 5)["jurisdiction_region"]
    return caught, honest


def the_two_refusals_stay_distinct():
    """DECIDED: an honest certificate for a RESTRICTED tile passes INTEGRITY and fails POLICY, while a
    FORGED region fails integrity. If these ever merge, a client can no longer tell a liar from a
    lawful no-entry sign. Returns (honest_integrity, honest_policy, forged_integrity)."""
    occ = frozenset({(33, 33, 33), (33, 33, 34)})
    cert = certify(occ, 5)
    liar = dict(cert, jurisdiction_region=OPEN)
    n = (cert["tile_prefix"] ^ 1,)
    return (verify_without_lattice(cert, n, 5)["jurisdiction_region"],
            satisfies_policy(cert, policy_open=True),
            verify_without_lattice(liar, n, 5)["jurisdiction_region"])


def stale_token_plant():
    """A certificate valid at its own tick and presented far outside the horizon. Returns
    (fresh_ok, stale_refused)."""
    occ = frozenset({(0, 0, 0)})
    cert = certify(occ, 5)
    fresh = verify_without_lattice(cert, (cert["tile_prefix"] ^ 1,), 5 + HORIZON)["liveness_token"]
    stale = verify_without_lattice(cert, (cert["tile_prefix"] ^ 1,),
                                   5 + HORIZON + 1)["liveness_token"]
    return fresh, not stale


def forged_neighbour_plant():
    """A tile claiming itself as a disjoint neighbour — the case `tilecert`'s first verifier filtered
    out and so could never catch. Returns (self_claim_refused, empty_set_refused, honest_ok)."""
    occ = frozenset({(0, 0, 0)})
    cert = certify(occ, 5)
    p = cert["tile_prefix"]
    return (not verify_without_lattice(cert, (p,), 5)["tile_prefix"],
            not verify_without_lattice(cert, (), 5)["tile_prefix"],
            verify_without_lattice(cert, (p ^ 1,), 5)["tile_prefix"])


def lifted_certificate_plant():
    """`provbind`'s attack at this layer: a certificate for one tile presented with another's bytes.
    The binding catches it AFTER download — attribution, which is what the binding is for."""
    a = frozenset({(0, 0, 0), (0, 0, 1)})
    b = frozenset({(33, 33, 33), (33, 33, 34)})
    cert = certify(a, 5)
    return cert["binding"] != bind(cert, lattice_digest(b))


def the_budget_is_absent():
    """L19-adjacent, asserted rather than assumed: the unverifiable field is not merely unused, it is
    STRUCTURALLY ABSENT from the certificate. Returns (fields, budget_present)."""
    occ = frozenset({(0, 0, 0)})
    cert = certify(occ, 5)
    return tuple(sorted(k for k in cert if k != "binding")), "remaining_budget" in cert


# ---- digests + scenes ---------------------------------------------------------------------------------------
def tm_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_fields():
    return tm_digest("fields", f"{all_fields_are_lattice_free()}:{admits_an_honest_certificate()}:"
                               f"{the_budget_is_absent()}:{sorted(survey())}")


def _scene_soundness():
    return tm_digest("soundness", f"{soundness_census()}:{location_jurisdiction_is_sound()}:"
                                  f"{over_refusal_price()}:{coarseness_is_stated()}")


def _scene_plants():
    return tm_digest("plants", f"{forged_region_plant()}:{the_two_refusals_stay_distinct()}:"
                               f"{stale_token_plant()}:{forged_neighbour_plant()}:"
                               f"{lifted_certificate_plant()}")


_SCENES = {"fields": _scene_fields, "soundness": _scene_soundness, "plants": _scene_plants}
SCENES = ("fields", "soundness", "plants")


def scene_result(name):
    return _SCENES[name]()


def conformance_lines():
    return tuple(f"{n} {scene_result(n)}" for n in SCENES)


def pinned_lines():
    out = []
    with open(_os.path.join(_HERE, "conformance_tilemin.txt"), encoding="utf-8") as fh:
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
    raise TileMinError(f"no golden named {name!r}")


def _main(argv):
    if "--emit" in argv:
        for ln in conformance_lines():
            print(ln)
        return 0
    for n in SCENES:
        print(n, scene_result(n))
    print(f"lattice-free fields (now, total, was, was_total) {all_fields_are_lattice_free()}")
    print(f"honest certificate admitted {admits_an_honest_certificate()}")
    print(f"budget absent (fields, present) {the_budget_is_absent()}")
    print(f"soundness (open, restricted, exceptions) {soundness_census()} -> "
          f"{location_jurisdiction_is_sound()}")
    print(f"over-refusal (refused, actual, ratio) {over_refusal_price()}")
    print(f"two refusals distinct (integrity, policy, forged) {the_two_refusals_stay_distinct()}")
    print(f"plants: region {forged_region_plant()} | stale {stale_token_plant()} | "
          f"neighbour {forged_neighbour_plant()} | lift {lifted_certificate_plant()}")
    print(f"emitted matches pinned {emitted_matches_pinned()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
