<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: view-witness:cite -->
# `view_witness` — design brief (URDRTVW1, T3.6, the citation contract)

**Read**: 2026-08-04, the centrality-ordered READ pass — P32 of batch 8
(`../exe_epistemics/PREDICTIONS.md`), the joint that **closed run 9**. Outcome: **C-R** — the author's
leading credence (45) correct, and the batch's only clean leading call. Reading grade: **CONFIRMATION**.

## What it is

**The declared view must honestly CITE the measured authority.** The WebGL2 studio view is DECLARED
presentation — raw browser float, off the exact gate, fifteen knobs — and that boundary never moves:
its pixels are not measured and are not claimed to be. But the view *embeds* two authority digests it
claims to be displaying (`hf_witness`, the URDRHF1 heightfield; `wave_witness`, the URDRWAV1 swell@0
field). Nothing stopped a careless or dishonest edit from printing a FORGED digest there and staying
green. This rung closes exactly that hole: it does not certify the render, it certifies the CITATION.

## The core law (what `view-witness:cite` certifies)

**A declared view may not MISQUOTE the authority it names.** The digests the view prints as measured
must EQUAL the live digests recomputed from the authority modules — an exact digest equality, and a
one-hex-flip forgery reddens it. Refusals are typed `VIEW-REFUSE` (no authority blob, a non-hex or
wrong-length witness, a missing required citation). `view-witness-firewall` certifies the other half
structurally: the declared knobs are a namespace DISJOINT from the authority, and the view's
presentation digest is anchored on the authority witness — so a knob moves the view, never the
witness. Versioned overlays are first-class: `VIEWS` is a list, so every future fidelity overlay
inherits the same guarantee — the look can iterate or revert, and the gate still forbids the overlay
from forging or laundering the measured core.

## The seam (P32's finding)

**The dual of the D15 firewall, and the pair is the point.** `terrain_view`'s D15 stage proves the
view cannot CONTAMINATE the authority (nothing flows inward); this proves the view cannot MISQUOTE it
(nothing false flows outward). Neither alone is sufficient and the arc needed both — an honest
one-way membrane still permits a lie about what is on the other side. Police over representation,
B-M′'s founding cell, and the leading credence landed. Structurally this is the first joint of the
read pass drawn from the arc's four TRUE CONFORMANCE GAPS (a gate stage and falsifiers, but no pinned
corpus of its own) — and the read found nothing hiding in that gap: the citation equality is exogenous
to any corpus by construction, because it recomputes the authority live rather than comparing against
a pinned digest. A corpus would have been the weaker instrument here, which is why its absence is a
design choice rather than a debt.

## does_not_show

The RENDER (pixels stay declared — this makes no claim the view is measured, and that boundary is the
rung's whole premise); the fifteen presentation knobs (declared by construction, firewalled by
namespace); WHO authored the view; anything about float behaviour in the browser. A view that cites
honestly is not an ACCURATE view — it faithfully quotes a digest it may still be drawing badly.
`integrity ≠ truth`, and here the two are deliberately kept in separate rooms.

## Falsifier

This brief cites `view-witness:cite`: the digests the view prints must equal the LIVE digests
recomputed from the authority modules, with a one-hex-flip forgery reddening. If a forged or stale
witness ever passed the citation check, or a required citation went missing without a typed
`VIEW-REFUSE`, that row reddens and this brief's central claim dies with it.
