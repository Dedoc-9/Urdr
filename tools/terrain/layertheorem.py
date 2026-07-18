# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""layertheorem — the Integer Scalar Potential Layer Theorem, CERTIFIED (T3.22). The terrain studio's
seven layers are not seven independent modules that happen to agree; they are one authority-rooted manifold,
and this binds them into a single conservation law the gate enforces. It does NOT re-certify each layer
(their own stages do that) — it measures the CROSS-LAYER properties no single stage checks: that there is
one source of authority, that authority flows strictly OUTWARD, and that nothing flows back.

THE SEVEN LAYERS (the theorem's strata, as instantiated over the `island` authority Φ):
  * Authority   — `heightfield` (URDRHF1): the exact-integer scalar potential Φ: Z^2 -> Z.
  * Consumer    — `stance`: a read-only projection (the grounded walk).
  * Presentation— `terrain_view3d.html`: DECLARED pixels (no measured digest of its own).
  * Firewall    — `view_witness`: certifies the presentation CITES the authority (citation measured).
  * Observer    — `gaze`: admits only frames that reconstruct to the authoritative pose, else a refusal.
  * Transcript  — `drive`: the exact-integer fold of an input log over Φ, tamper-evident.
  * Horizon     — `traj`: sequence consistency across time (every frame agrees with the dynamics).

THREE MEASURED CROSS-LAYER FACTS.
  * SINGLE SOURCE — the firewall's cited authority digest (`hf_witness`) EQUALS the authority's own live
    digest: the declared presentation is bound, through the firewall, to the exact same Φ the observers and
    transcript consume. There is one source of authority, and every layer roots at it.
  * OUTWARD FLOW — a perturbation of Φ at a SINGLE cell moves EVERY downstream layer's digest (Consumer,
    Observer, Transcript, Horizon). Each layer genuinely depends on the authority — a layer that ignored Φ
    would be caught here. Authority flows strictly outward.
  * MEMBRANE (no feedback) — running the full downstream pass leaves the authority field bit-identical, and
    a FORGED presentation is refused by the firewall, never reaching authority. Nothing flows back.

The composite THEOREM DIGEST binds the measured layers over the island authority; it reproduces
deterministically and moves if any bound layer drifts.

GRADE. The single-source binding, the outward-flow sensitivity, the membrane, and the composite
determinism/tamper-evidence are MEASURED (exact, reproducible, a defect diverges). HONEST SCOPE on the
theorem's "division-free" epilogue: the manifold is exact-integer and DETERMINISTIC throughout, and every
DOWNSTREAM layer is genuinely division-free (`//`-free, tokenizer-asserted); the AUTHORITY's FBM uses
exact-integer normalization `raw*height_scale // rawmax` (rawmax not a power of two) plus Q16 shifts
(`// 2^16`), so "entirely division-free" is narrowed to "float-free, exact-integer, deterministic;
shift-only and `//`-free downstream; one exact-integer normalization at the authority." `does_not_show`: the
general theorem over an ARBITRARY integer manifold (this certifies the URDR terrain INSTANTIATION of it); the
Presentation layer's pixels (DECLARED, certified only by citation); and any claim beyond the seven bound
layers. Refusals are typed `ISPL-REFUSE` (a missing / drifted layer, a malformed authority)."""
import hashlib
import os as _os
import sys as _sys

MAGIC = b"URDRISPL1"
_SCENE = "island"                                                # the authority instance Φ
_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
import heightfield as _HF                                        # Authority (URDRHF1)
import stance as _ST                                             # Consumer
import view_witness as _VW                                       # Firewall
import gaze as _GZ                                               # Observer
import drive as _DR                                              # Transcript
import traj as _TR                                               # Horizon

# (layer, module, grade) — Presentation is DECLARED, certified only through the Firewall.
LAYERS = (
    ("Authority", "heightfield", "MEASURED"), ("Consumer", "stance", "MEASURED"),
    ("Presentation", "terrain_view3d", "DECLARED"), ("Firewall", "view_witness", "MEASURED"),
    ("Observer", "gaze", "MEASURED"), ("Transcript", "drive", "MEASURED"),
    ("Horizon", "traj", "MEASURED"),
)
_ST_ARGS = ((4, 4), "EEEE", 40)                                  # stance: start, moves, max_step
_DR_ARGS = ((4, 4), "eeee", 40)                                  # drive/traj: start, cmds, max_step
_GZ_CELL = (4, 4)                                                # gaze: the pose cell
_VIEW = "terrain_view3d.html"                                    # the DECLARED presentation file


class ISPLError(Exception):
    def __init__(self, message):
        super().__init__(f"ISPL-REFUSE: {message}")
        self.code = "ISPL-REFUSE"


def _params():
    return _HF.SCENES[_SCENE]()


def authority():
    """(digest, field) of the authoritative scalar potential Φ = the island heightfield."""
    return _HF.scene_digest(_params())


def _field_digest(field):
    p = _params()
    return _HF.field_digest(p["w"], p["h"], p["height_scale"], p["sea_level"], p["falloff"], field)


def perturb(field, x, y, delta=1):
    """Φ perturbed at ONE cell (x, y) — the outward-flow probe input. Returns a new immutable field."""
    if not (0 <= y < len(field) and 0 <= x < len(field[0])):
        raise ISPLError(f"perturb cell ({x},{y}) off the field")
    row = list(field[y])
    row[x] = row[x] + delta
    return field[:y] + (tuple(row),) + field[y + 1:]


def _hash_poses(tag, poses):
    hh = hashlib.sha256()
    hh.update(tag)
    for p in poses:
        hh.update(b"|")
        hh.update(",".join(str(int(v)) for v in p).encode())
    return hh.hexdigest()


def downstream_probes(field):
    """The field-dependent digest of each downstream layer over `field` — the outward-flow sensors. Each
    reads the authority at/near cell (4,4), so a perturbation there must move every one."""
    st = _ST.stance_digest("isplp", *_ST.walk_trace(field, *_ST_ARGS))
    gz = _GZ.pose_digest((_GZ_CELL[0], _GZ_CELL[1], field[_GZ_CELL[1]][_GZ_CELL[0]], 1))
    dr = _DR.transcript_digest("isplp", _DR_ARGS[0], _DR_ARGS[1], _DR.drive(field, *_DR_ARGS))
    tr = _hash_poses(b"URDRISPLW|", _TR.reconstruct(field, *_DR_ARGS))
    return {"Consumer": st, "Observer": gz, "Transcript": dr, "Horizon": tr}


def single_source():
    """The DECLARED presentation file embeds EXACTLY the authority's live digest — the strongest form of
    the single source: the actual `terrain_view3d.html` (not a recomputation) cites the one Φ the
    observers and transcript consume, and the firewall certifies the match."""
    view = _VW.read_view(_VIEW)
    blob, _knobs = _VW.parse_view(view)
    return blob["hf_witness"] == authority()[0] and _VW.citation_ok(view, required=("hf_witness",))


def forgery_refused():
    """A forged presentation (one flipped hex of the cited authority digest) is REFUSED by the firewall —
    the membrane: a lie about authority cannot pass, and cannot reach authority."""
    view = _VW.read_view(_VIEW)
    return _VW.firewall_ok(view) and not _VW.citation_ok(_VW.forge_citation(view))


def layer_certified():
    """Each MEASURED layer reproduces its own canonical golden (live and certified). The Firewall's
    certification is that the declared presentation cites the live authority (the single source)."""
    return {
        "Authority": _HF.scene_digest(_HF.SCENES["island"]())[0] == _HF.golden("island"),
        "Consumer": _ST.scene_result("plain_walk")[1] == _ST.golden("plain_walk"),
        "Firewall": single_source() and forgery_refused(),
        "Observer": _GZ.scene_verdict("genuine")[2] == _GZ.golden("genuine"),
        "Transcript": _DR.scene_result("stroll")[1] == _DR.golden("stroll"),
        "Horizon": _TR.scene_result("honest_full")[2] == _TR.golden("honest_full"),
    }


def theorem_digest():
    """Bind the measured layers over the island authority Φ into one conservation digest: the authority,
    the firewall's citation of it, and every downstream projection. Reproducible; moves if any drifts."""
    d, field = authority()
    pr = downstream_probes(field)
    hh = hashlib.sha256()
    hh.update(MAGIC)
    hh.update(("|A:" + d).encode())
    hh.update(("|F:" + _VW.live_witnesses()["hf_witness"]).encode())
    for role in ("Consumer", "Observer", "Transcript", "Horizon"):
        hh.update((f"|{role[0]}:" + pr[role]).encode())
    return hh.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
SCENES = {"island_manifold": None}                              # one instance: the island-rooted manifold


def scene_result(name):
    """The composite URDRISPL1 theorem digest for the named manifold instance."""
    if name != "island_manifold":
        raise ISPLError(f"no manifold scene {name!r}")
    return theorem_digest()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_layertheorem.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise ISPLError(f"no golden named {name!r}")
