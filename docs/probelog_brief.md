<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: probelog-record -->

# `probelog` (URDRPBL1) — design brief

*The first §3 log becomes evidence, through the door that already existed.*

## Observe

`sealframe`'s SEGMENTS partition tiled `input_actuation → photon` across seven instants and
carried `frame_render`, `present_queue` and `input_to_photon` as NOT_MEASURED with the note "the
layer-3 renderer does not exist." Its admission machinery — `ledger_from_log`, with the named-host
law, the instrument-class refusal and the monotone floor — had nothing real to admit since the day
it was written.

`present_probe` v0.1 (`hainuwele/parallel/`, deliberately ungated, wall-clock class) ran on the
named machine on 2026-08-13. The run produced twenty click chains: dispatch wait, tick, view
export, raster, and blit, each in integer nanoseconds, plus a full-frame white flash for the
phone-camera segment software cannot reach. The log's 966 bytes were staged off the device over
the bridge and committed verbatim.

## Orient

The interesting design fact is that **nothing new needed to be designed**. The door exists; the
discipline questions were all about what may pass through it, and each had an answer already
carved somewhere in the tree:

The figures must be **derived, not typed** (L75, the `attest` shape) — so the module parses the
committed bytes at claim time and computes floor(min)..ceil(max) bands in exact integer hundreds
of nanoseconds. The record is pinned by sha256; a flipped byte refuses.

The probe's trivial tick reads *under* the 100-biped floor from bench_protocol §4b — which is not
a problem but a **live demonstration of the floor law**: `ledger_from_log` keeps the old floor and
cites both sources, exactly the FRAME_BUDGET one-component-two-workloads error it was built to
prevent, now shown biting on real data rather than a fixture.

The probe recorded the machine but **not the power or scheduler state**, so the strict door
(`require_conditions=True`) refuses the record, naming exactly `power` and `scheduler`. That
refusal is pinned as a law rather than worked around: it is probe v0.2's specification, in the
shape `rollbench` already established (`--power`/`--scheduler` as operator declarations in the
documented argv).

And the module had to be a **leaf**. `confound`, `pedigree` and `rehearse` each tried to import
what they graded and the depth ceiling refused all three. `probelog` imports nothing from the
tree; `make_segment_log`, `ledger_from_log`, `budget_verdict` and the static table arrive as
arguments from the tests and the gate stage, which import both sides.

## Decide

What graduates: `frame_render` and `present_queue` NOT_MEASURED → MEASURED, `view_export`
DECLARED → MEASURED, all with derived bands and workload-naming citations. What deliberately does
not: `input_to_photon` stays UNDETERMINED, and the verdict names whose task each missing segment
is — `pending` is **empty** (nothing left is software's alone), `present_wait` waits on the
platform's presentation feedback, `input_transport` and `panel` wait on a camera. The lower bound
rises from the tick floor alone to the sum of every graduated floor, computed from the ledger both
ways rather than typed.

A v0 log refuses by version discipline: v0's pacing was defective (its own catch) and its one
chain-bearing run was anonymous. An empty click table refuses: a chainless run measured only the
frame loop, and the protocol's completeness line is now enforced rather than advised.

## Act

Built red-first; rows `probelog-record` and `probelog-ledger`; the committed record at
`spec/attest/present_probe-allyx-v01.txt`; falsifiers covering the flipped byte, the v0 log, the
empty table, the malformed row, the floor demonstration, the strict-door refusal, the anonymous
host, the wrong instrument, and the both-ways bound.

D1 §20 ruling: **no new glyph.** The kernel is untouched; this is a parser and an injection
harness around a door that already existed.

## `does_not_show`

The bands bound the probe workload on the GDI path at 1280x729 — a gradient scene and a
`StretchDIBits` blit. The layer-3 renderer remains unmeasured, and the ceilings here say nothing
about it. Conditions are undeclared, so two runs under different power states are not comparable
yet — the strict-door refusal is that fact made checkable. Nothing bounds input latency from
actuation: the hardware-to-dispatch wait is invisible to the probe by construction, and the
chain's `input_wait` column is reported but never graded. One run is one execution-level sample
(URDRRPT1); the day's own record shows frame p50 moving between runs.

## Grade

**MEASURED.** Every figure is derived at claim time from a committed record pinned by digest; the
graduation passes through `sealframe.ledger_from_log` unmodified; every refusal is asserted
against the injected door rather than restated. **DECLARED:** which record is the evidence, and
that its conditions are insufficient for the strict door.
