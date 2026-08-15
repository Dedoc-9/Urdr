<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: latchain-bound -->

# `latchain` (URDRLTC1) — design brief

*The waiting latency record graduates through the strict door.*

## Observe

`probelog` graduated the first click-chain record loosely: present_probe v0.1's record declared
no power or scheduler, so `ledger_from_log(require_conditions=True)` refused it — and that
refusal was pinned as the next instrument's specification rather than papered over. Probe v0.4
discharged the specification: conditions declared in its header, 32 click chains across all four
resolution cells, at the 1:1 fullscreen geometry that v0.4 existed to establish. Its record then
sat committed for the whole envelope arc, preserved by `pixelcost`'s version dispatch — a
different question, refused from the cost table by law, waiting for the latency rung.

## Orient

This rung is cheap evidence debt, deliberately: no new measurement hypothesis, no change to the
demo. It adjudicates an existing artifact. The one danger worth designing against is inflation —
a partial chain quietly becoming an end-to-end claim. The chains evidence four software-timer
segments (authority_tick, view_export, frame_render, present_queue) on one clock; they say
nothing about input_transport (a switch closure is not software-visible), present_wait (the
platform must report when a present actually landed), or panel (a photon is not a QPC stamp).
Software-reachable latency is not input-to-photon latency.

## Decide

Graduate through sealframe's door, injected, with nothing restated: the strict admission is the
exact call probelog pinned red, now passing because the record carries its conditions. Bands are
floor(min)..ceil(max) over all 32 chains; every chain's total must re-add from its parts or the
row refuses; authority_tick keeps its 100-biped floor against 32 cheaper readings because a log
may only raise a floor. And the partial-chain law is asserted at the gate, not remembered: the
lower bound rises (0.0723 → 0.1761 ms of the 25 ms budget) and the budget verdict stays
UNDETERMINED with the unevidenced segments named by kind.

## Act

`latchain-admit` re-reads the pin, re-derives the bands, and passes the strict door;
`latchain-bound` asserts the bound rose and the verdict stayed honest; `latchain-selftest`
proves five plants bite. The falsifier that names this brief: grade `panel` with a software
timer, or hand the door a condition-stripped log, and `latchain-bound`'s machinery refuses —
the inflation is impossible, not discouraged.
