# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""terrain_view — T3.0: the view-export FIREWALL for a certified terrain/sea state.

The one measurable thing about the presentation layer (see `docs/presentation_doctrine.md`
§4): we do not measure the pixels and we do not measure the budget — we measure that the
budget cannot touch the truth. This is D15's view contract applied to terrain, and it mints
NO new authority class: the `view_digest` below is a PRESENTATION digest (D15's VIEW digest),
never a witness.

A view descriptor carries the authoritative witness — the `URDRHF1`/`URDRFLD1` digest of the
recorded state — as a BOUND, SUBORDINATE field, alongside a `view_digest` over the witness
and the declared presentation knobs (palette, exposure, LOD stride, wave amplitude, frame
rate, …). The firewall properties, each a gate row:

  * BIND — the view carries the authority digest VERBATIM; it never recomputes or alters it;
  * OBSERVATIONAL — changing ANY presentation knob moves the `view_digest` and leaves the
    carried witness byte-identical (presentation is observational only — the boundary);
  * DEFECT — a `view_digest` variant that folds a presentation knob INTO the carried witness
    diverges from the true witness (the fold is caught — the firewall is load-bearing);
  * REFUSAL — a non-hex witness or a malformed presentation dict is `VIEW-REFUSE`, total.

Grade: MEASURED (reference) — the firewall, not the view. Everything the HTML renderer draws
from this descriptor is presentation: declared, off-gate, browser float, NOT measured, and
unmeasurable in principle. `Semel` the authority is measured; `et iterum` the presentation is
declared; `idem` the boundary never moves."""
import hashlib

MAGIC = b"URDRTVW1"
_HEX = set("0123456789abcdef")
# the declared presentation knobs a terrain view may carry (order-independent; values free)
_KNOBS = ("palette", "exposure", "contrast", "saturation", "lod_stride",
          "wave_amp", "sea_alpha", "frame_rate", "sun_azimuth", "sun_elevation")


class ViewError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise ViewError("VIEW-REFUSE", message)


def _check(witness, presentation):
    if not (isinstance(witness, str) and len(witness) == 64 and all(c in _HEX for c in witness)):
        _refuse(f"carried witness must be a 64-hex authority digest, got {witness!r}")
    if not isinstance(presentation, dict) or not presentation:
        _refuse("presentation must be a non-empty dict of declared knobs")
    for k in presentation:
        if k not in _KNOBS:
            _refuse(f"unknown presentation knob {k!r} (declared knobs: {', '.join(_KNOBS)})")


def _canon_presentation(presentation):
    """Deterministic serialization of the declared knobs — sorted, so knob order is inert."""
    return "|".join(f"{k}={presentation[k]!r}" for k in sorted(presentation))


def view_digest(witness, presentation):
    """The PRESENTATION digest — SHA-256(MAGIC | carried witness | canon(presentation)).
    A function of the witness AND the declared knobs; moves when either moves."""
    _check(witness, presentation)
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(b"|w:")
    h.update(witness.encode())
    h.update(b"|p:")
    h.update(_canon_presentation(presentation).encode())
    return h.hexdigest()


def view_digest_defect(witness, presentation):
    """THE DEFECT (D15 non-vacuity): fold a presentation knob INTO the carried witness — the
    exact leak the firewall forbids. The returned 'witness' must diverge from the true one,
    proving presentation-cannot-move-the-witness is a checked property, not an accident."""
    tampered = hashlib.sha256((witness + "|" + _canon_presentation(presentation)).encode()).hexdigest()
    return {"carried_witness": tampered, "view_digest": view_digest(witness, presentation)}


def export_view(witness, presentation):
    """The view descriptor: the carried witness (bound, subordinate, VERBATIM) + the
    presentation digest. This is what a renderer consumes; the renderer draws pixels from it
    and may never write back into `carried_witness`."""
    _check(witness, presentation)
    return {"carried_witness": witness,                 # the authority digest, unaltered
            "view_digest": view_digest(witness, presentation),
            "presentation": dict(presentation)}


def carried_witness_matches(descriptor, authority_digest):
    """The BIND check: the view carries the authority digest verbatim (never recomputed)."""
    return descriptor.get("carried_witness") == authority_digest


# ---- the pinned T3.0 scene: a view of the certified wide sea -----------------------------
# The base presentation the HTML renderer opens with; the gate perturbs it to prove the
# firewall. The carried witness is supplied by the caller from the RECORDED state
# (`sea.golden("island_sea_wide")`), never computed here — the view carries authority.
BASE_PRESENTATION = {"palette": "cartoon_terra", "exposure": 100, "sea_alpha": 200,
                     "lod_stride": 1, "wave_amp": 0, "frame_rate": 0}
