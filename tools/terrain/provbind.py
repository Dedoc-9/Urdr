# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""provbind — ADMISSIBILITY AS A BOUND TYPED REFUSAL (URDRPRV1): slice S3 of the city-replica arc.
NO NEW GLYPH.

WHAT THIS IS FOR. A capture may be lawful to serve in one jurisdiction and not another; the surveyed
constraint surface is genuinely fragmented (France permits non-commercial panorama only, Italy
requires authorization for cultural goods, Greece limits the exception to occasional media, Belgium
permits full commercial use, and no statute anywhere says whether a 3D mesh is the same act as a
photograph). This rung does not resolve any of that — it is not legal advice and could not be. What
it does is make the ANSWER ENFORCEABLE: a block carries a provenance record, and the server refuses
to serve it where its provenance is inadmissible, as a typed refusal rather than as moderation policy.

TWO DEFECTS IN THE HANDED-DOWN DESIGN, both fatal, both one line to fix.

  (1) THE CERTIFICATE WAS DETACHABLE. The proposed `digest()` hashed only the metadata fields, so
      nothing tied a certificate to the geometry it certifies. An attacker lifts the permissive
      certificate off a public-domain block and staples it to a restricted capture, and every check
      downstream passes. `_digest_metadata_only` keeps that form as a plant and `lift_attack`
      MEASURES it succeeding. The law binds: `H(MAGIC | cert | lattice_digest)`, and the lattice
      digest is RECOMPUTED at serve time rather than trusted, so the binding cannot be asserted by
      whoever supplied it.

  (2) IT CONTRADICTED ITS OWN CLAIM. The stated property was "decidable at serve time from embedded
      provenance, no external lookup," and the check then called `distance_to_nearest_school(...)` —
      an external lookup, on the hot path, whose answer can differ between two serves of the same
      block. Here the buffer test is evaluated ONCE AT CAPTURE TIME and its result is a FIELD inside
      the certificate, so the claim becomes true instead of aspirational, and the buffer distance
      becomes part of what the digest commits to. `_admit_by_live_lookup` is the plant, and it is
      measured returning different verdicts for the same block on two serves.

THE EXCLUSION SET is taken from the closest shipped template found — Niantic Wayfarer's (no private
residences, K-12 schools, cemeteries, active farmland), together with its 2019 trespass settlement
terms (40 m removal from single-family residences). Those are DECLARED as a policy import, not
derived, and the point of this rung is that whatever the policy turns out to be, it is committed to
by a digest and enforced by a refusal.

THREE REFUSAL CLASSES, KEPT DISTINCT because they mean different things to a contributor and must
never share a counter: PROVBIND-UNBOUND (the certificate does not belong to this geometry — an
integrity event), PROVBIND-CONSENT (the capture itself is inadmissible anywhere), and
PROVBIND-JURISDICTION (admissible somewhere, not here — the only one that is a property of the
REQUEST rather than of the block, so the same block legitimately admits for one viewer and refuses
for another).

GRADE. MEASURED: the lift attack succeeding against the metadata-only digest and failing against the
bound one, over the whole pinned corpus; the live-lookup plant's instability across serves; the
verdict table; determinism. DECLARED: the exclusion set and the jurisdiction table are POLICY
IMPORTS, chosen not derived — the mechanism is the contribution, the contents need a lawyer.
does_not_show: that any particular refusal set is legally sufficient (it is a constraint surface, not
advice); whether a 3D reproduction is the same act as a photograph in any jurisdiction (untested
everywhere); identity of the contributor (that is not touched here, exactly as `geoquorum` declares);
cross-placement."""
import hashlib
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRPRV1"

R_ADMIT = 0
R_UNBOUND = 1                                  # the certificate does not belong to this geometry
R_CONSENT = 2                                  # inadmissible anywhere
R_JURISDICTION = 3                             # admissible somewhere, not here
_REASON_NAME = {R_ADMIT: "ADMIT", R_UNBOUND: "PROVBIND-UNBOUND",
                R_CONSENT: "PROVBIND-CONSENT", R_JURISDICTION: "PROVBIND-JURISDICTION"}

# DECLARED policy imports — the mechanism is the contribution, the contents need a lawyer.
EXCLUDED_CONSENT = ("private_residence", "k12_school", "cemetery", "active_farmland")
RESIDENCE_BUFFER_M = 40                        # Niantic's 2019 settlement term
COMMERCIAL_OK = {"US": True, "UK": True, "DE": True, "BE": True,
                 "FR": False, "IT": False, "GR": False}
_FIELDS = ("capture_region", "consent_basis", "licence", "buffer_m", "commercial")


class ProvbindError(Exception):
    def __init__(self, message):
        super().__init__(f"PROVBIND-REFUSE: {message}")
        self.code = "PROVBIND-REFUSE"


# ---- the certificate --------------------------------------------------------------------------
def certificate(capture_region, consent_basis, licence, buffer_m, commercial):
    """A provenance record. `buffer_m` is the distance to the nearest excluded structure, EVALUATED
    AT CAPTURE TIME and carried as a field — which is what makes serve-time adjudication a decision
    rather than a lookup, and what puts the buffer inside the digest's commitment."""
    for v, n in ((capture_region, "capture_region"), (consent_basis, "consent_basis"),
                 (licence, "licence")):
        if type(v) is not str or not v:
            raise ProvbindError(f"{n} must be a non-empty string, got {v!r}")
    if type(buffer_m) is not int or buffer_m < 0:
        raise ProvbindError(f"buffer_m must be a non-negative int, got {buffer_m!r}")
    if type(commercial) is not bool:
        raise ProvbindError(f"commercial must be a bool, got {commercial!r}")
    return (capture_region, consent_basis, licence, buffer_m, commercial)


def _canon(cert):
    return "|".join(f"{k}={v}" for k, v in zip(_FIELDS, cert))


def bound_digest(cert, lattice_digest):
    """THE LAW: the commitment binds the certificate TO THE GEOMETRY. H(MAGIC | cert | lattice)."""
    if type(lattice_digest) is not str or len(lattice_digest) != 64:
        raise ProvbindError(f"lattice digest must be a 64-hex string, got {lattice_digest!r}")
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{_canon(cert)}|{lattice_digest}".encode())
    return hh.hexdigest()


def _digest_metadata_only(cert, lattice_digest=None):
    """A FALSIFIER TOOL (not the law): the handed-down form, hashing only the metadata. It commits to
    nothing about the geometry, so the certificate travels — which is the whole attack."""
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{_canon(cert)}".encode())
    return hh.hexdigest()


# ---- adjudication -----------------------------------------------------------------------------
def adjudicate(cert, lattice_digest, claimed_binding, serving_region, _digest=None, _lookup=None):
    """The serve-time verdict, in order: is the certificate BOUND to this geometry, is the capture
    admissible at all, is it admissible HERE. Everything is decided from carried fields — the only
    external input is `serving_region`, which is a property of the request."""
    dig = _digest or bound_digest
    if dig(cert, lattice_digest) != claimed_binding:
        return R_UNBOUND
    _region, consent, _lic, buffer_m, commercial = cert
    if _lookup is not None:
        buffer_m = _lookup()
    if consent in EXCLUDED_CONSENT or buffer_m < RESIDENCE_BUFFER_M:
        return R_CONSENT
    if commercial and not COMMERCIAL_OK.get(serving_region, False):
        return R_JURISDICTION
    return R_ADMIT


def _admit_by_live_lookup(_calls=[0]):
    """A FALSIFIER TOOL (not the law): the buffer distance fetched at SERVE time instead of carried.
    It returns a different answer on successive serves of the same block, so the verdict is unstable
    and the 'no external lookup, decidable at serve time' claim is false."""
    _calls[0] += 1
    return 100 if _calls[0] % 2 else 10


# ---- the pinned corpus and the attacks ---------------------------------------------------------
def corpus():
    """Pinned certificates: one permissive, one restricted, one consent-excluded."""
    return {
        "public_domain": certificate("US", "public_space", "PublicDomain", 500, True),
        "restricted": certificate("FR", "public_space", "CommercialRestricted", 500, True),
        "residence": certificate("US", "private_residence", "PublicDomain", 5, False),
    }


def lattices():
    """Two pinned lattice digests — stand-ins for URDRVOX1 outputs, fixed, never generated fresh."""
    return {n: hashlib.sha256(f"URDRVOX1|{n}".encode()).hexdigest()
            for n in ("block_a", "block_b")}


def lift_attack(_digest=None):
    """THE ATTACK, MEASURED: take the permissive certificate's binding from block_a and present it
    with block_b's geometry. Under the metadata-only digest the binding still matches and the lie is
    admitted; under the bound digest it does not. Returns (binding_matches, verdict)."""
    dig = _digest or bound_digest
    cert = corpus()["public_domain"]
    lat = lattices()
    stolen = dig(cert, lat["block_a"])
    verdict = adjudicate(cert, lat["block_b"], stolen, "US", _digest=dig)
    return dig(cert, lat["block_b"]) == stolen, verdict


def binding_defeats_the_lift():
    """THE LAW, stated so it can be false: the lift must SUCCEED against the metadata-only plant and
    FAIL against the bound digest. Requiring both is what keeps the law from passing vacuously."""
    plant_matches, plant_verdict = lift_attack(_digest=_digest_metadata_only)
    law_matches, law_verdict = lift_attack()
    return (plant_matches and plant_verdict == R_ADMIT
            and not law_matches and law_verdict == R_UNBOUND)


def live_lookup_is_unstable(trials=4):
    """The second plant, MEASURED: the same block adjudicated repeatedly must give one answer. With
    a serve-time lookup it does not."""
    cert, lat = corpus()["public_domain"], lattices()["block_a"]
    b = bound_digest(cert, lat)
    carried = {adjudicate(cert, lat, b, "US") for _ in range(trials)}
    live = {adjudicate(cert, lat, b, "US", _lookup=_admit_by_live_lookup) for _ in range(trials)}
    return len(carried) == 1 and len(live) > 1


def verdict_table():
    """The full pinned verdict set — every certificate against every serving region."""
    lat = lattices()["block_a"]
    rows = []
    for name, cert in sorted(corpus().items()):
        b = bound_digest(cert, lat)
        for region in ("US", "FR", "XX"):
            rows.append((name, region, _REASON_NAME[adjudicate(cert, lat, b, region)]))
    return rows


def classes_are_distinct():
    """The three refusal classes must be distinct and all reachable — a class no input can produce is
    decoration, and a shared counter would conflate an integrity event with a lawful geography."""
    seen = {v for _n, _r, v in verdict_table()}
    return (len({R_ADMIT, R_UNBOUND, R_CONSENT, R_JURISDICTION}) == 4
            and {"ADMIT", "PROVBIND-CONSENT", "PROVBIND-JURISDICTION"} <= seen
            and lift_attack()[1] == R_UNBOUND)


# ---- digests + scenes -------------------------------------------------------------------------
def pv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_binding():
    return pv_digest("binding", f"{lift_attack(_digest=_digest_metadata_only)}:{lift_attack()}:"
                                f"{binding_defeats_the_lift()}")


def _scene_verdicts():
    return pv_digest("verdicts", f"{verdict_table()}:{classes_are_distinct()}")


def _scene_lookup():
    return pv_digest("lookup", f"{live_lookup_is_unstable()}")


_SCENES = {"binding": _scene_binding, "verdicts": _scene_verdicts, "lookup": _scene_lookup}
SCENES = ("binding", "verdicts", "lookup")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_provbind.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ProvbindError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"lift vs metadata-only plant: {lift_attack(_digest=_digest_metadata_only)}")
    print(f"lift vs bound digest       : {lift_attack()}")
    print(f"binding defeats the lift {binding_defeats_the_lift()} | "
          f"live lookup unstable {live_lookup_is_unstable()} | classes distinct {classes_are_distinct()}")
    for r in verdict_table():
        print(f"   {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
