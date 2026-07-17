# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""view_witness — the declared view must honestly CITE the measured authority (T3.6).

The WebGL2 studio view (`terrain_view3d.html`) is DECLARED presentation: raw browser float, off
the exact gate, 15 knobs. We do NOT measure its pixels — that boundary never moves. But the view
*embeds* two authority digests it claims to be displaying:

    hf_witness   — the URDRHF1 island heightfield digest
    wave_witness — the URDRWAV1 swell@0 wave-field digest

Nothing stopped a careless (or dishonest) edit from printing a FORGED digest there and staying
green. This stage closes that: it does not certify the render, it certifies the *citation* — the
digests the view prints as measured must equal the LIVE digests recomputed from the authority
modules. And it certifies the FIREWALL: the declared knobs are a namespace disjoint from the
authority, and the view's presentation digest is anchored on the authority witness (so a knob moves
the view, never the witness). This is the dual of D15/`terrain-view-observational`: we already prove
the view can't contaminate the authority; here we prove the view can't MISQUOTE it.

Versioned overlays. `VIEWS` is a list, so every future fidelity overlay (v5, v6, …) that ships as a
new view file is added here and inherits the same guarantee — you can iterate the look or revert an
effect, and the gate still forbids the overlay from forging or laundering the measured core.

GRADE. The citation check is MEASURED (an exact digest equality, reproducible, and a one-hex-flip
forgery reddens it). It makes no claim that the render is measured — the render stays declared.
Refusals are typed `VIEW-REFUSE` (no authority blob / non-hex or wrong-length witness / missing a
required citation)."""
import json
import re
import os as _os
import sys as _sys

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import heightfield as _HF                                        # URDRHF1 authority
import wavefield as _WF                                          # URDRWAV1 authority

_HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")
_BLOB = re.compile(r"const D = (\{.*?\});")                      # single-line JSON blob (no re.S)
_INPUT_ID = re.compile(r'<input[^>]*\bid="([A-Za-z0-9_]+)"')
_AUTHORITY_FIELDS = frozenset({"hf_witness", "wave_witness", "heights", "waves", "depth"})

# The views under the citation contract. Each names the witnesses it must cite honestly. Add a new
# overlay file here to bring it under the same provenance guarantee (versioned overlays).
VIEWS = [("terrain_view3d.html", ("hf_witness", "wave_witness"))]


class ViewError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise ViewError("VIEW-REFUSE", message)


def parse_view(html_text):
    """Extract the embedded authority blob + declared knob ids from a view's HTML. Every malformed
    citation is a typed `VIEW-REFUSE` (no blob / bad JSON / non-hex or wrong-length witness)."""
    m = _BLOB.search(html_text)
    if not m:
        _refuse("no embedded authority blob `const D = {...}` found")
    try:
        blob = json.loads(m.group(1))
    except Exception as exc:
        _refuse(f"authority blob is not valid JSON: {exc}")
    for key in ("hf_witness", "wave_witness"):
        if key not in blob:
            _refuse(f"the view does not cite {key}")
        v = blob[key]
        if not (isinstance(v, str) and _HEX64.match(v)):
            _refuse(f"{key} is not a 64-hex digest: {v!r}")
    knob_ids = frozenset(_INPUT_ID.findall(html_text))
    return blob, knob_ids


def live_witnesses():
    """Recompute the authority digests a view MUST cite, from the MODULES (not the pinned corpus):
    the URDRHF1 island heightfield and the URDRWAV1 swell@0 field. The terrain/ wavefield stages
    separately prove these equal their goldens, so a match here is a match to live authority."""
    hf = _HF.scene_digest(_HF.SCENES["island"]())[0]
    W = 24
    wf = _WF.wave_digest(W, W, 0, _WF.field(W, W, 0, _WF.swell()))
    return {"hf_witness": hf, "wave_witness": wf}


def citation_ok(html_text, required=("hf_witness", "wave_witness")):
    """True iff every required witness the view embeds equals the live authority digest."""
    blob, _knobs = parse_view(html_text)
    live = live_witnesses()
    return all(blob[k] == live[k] for k in required)


def firewall_ok(html_text):
    """The declared/measured boundary, structurally: (1) the knob namespace is DISJOINT from the
    authority fields (no knob can alias a witness), and (2) the presentation view-digest is ANCHORED
    on the authority witness (URDRTVW1 | wave_witness | knobs) — so a knob moves the view digest, the
    witness never moves. Observational-only, by construction."""
    _blob, knob_ids = parse_view(html_text)
    disjoint = knob_ids.isdisjoint(_AUTHORITY_FIELDS)
    anchored = ("URDRTVW1" in html_text) and ("D.wave_witness" in html_text)
    return disjoint and anchored


def forge_citation(html_text):
    """A DEFECT view (non-vacuity): flip one hex char of the embedded hf_witness. `citation_ok` MUST
    return False on the result — otherwise the citation check is vacuous."""
    blob, _knobs = parse_view(html_text)
    hf = blob["hf_witness"]
    flipped = ("1" if hf[0] != "1" else "2") + hf[1:]
    return html_text.replace(f'"hf_witness":"{hf}"', f'"hf_witness":"{flipped}"', 1)


def read_view(name):
    with open(_os.path.join(_HERE, name), encoding="utf-8") as fh:
        return fh.read()
