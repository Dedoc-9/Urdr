<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: fpsrecord-crossos -->

# `fpsrecord` (URDRFPR1) — design brief

*The demo's workload records become artifacts the gate re-reads.*

## Observe

The fpsdemo input arc produced its evidence in the most fragile places a repository has:
terminal transcripts and one machine's working directory. The authoring container lost its
scratch copies to rollbacks four times while the arc ran; the operator's `fpsdemo_log.txt` is
overwritten by every run; and the strongest claim the arc produced — byte-identical rendering
across two operating systems — existed only as pasted text no gate could re-read.

The traces themselves are the arc's findings in miniature. The v0 recording carries 0 keyed
frames across 1800 because a WS_POPUP window never took keyboard focus. The v1.3 recording
carries `moused 1386` with an idle XInput pad because the handheld's vendor layer holds the
physical sticks and emits desktop vocabulary. The one-frame record exists because v1.4 put
Enter in the end-run set and Enter is the key that launches a program from a shell. And the
real walk — 1145 frames, 757 keyed, ended by an armed Esc — is the first trace in the arc
where a human moved through the world.

## Orient

Two constraints shaped the reader. The gate cannot execute the demo (wall-clock class, Win32),
so a chain must be bound to its trace by laws derivable from bytes alone: the checkpoint frames
must be exactly the loop's digest schedule for that trace's length, and every checkpoint inside
a trace's leading all-zero prefix must equal the pinned static-spawn constant — a chain that
claims a still camera must open with the still frame. The real walk makes that law non-vacuous:
236 zero frames, three checkpoints inside, all equal to the constant.

And cross-OS agreement had to become a comparison of committed artifacts. The named host's log
carries its own 20-digest chain under declared conditions; the authoring container's chain for
the same committed trace is a separate record from a separate binary on a separate OS. The gate
parses both and compares digest for digest. Neither side is trusted; both are pinned.

## Decide

Commit eight records: four traces (the workloads and the incident witness), three container
chains, one named host log. Derive every figure from the bytes at claim time — frames, keyed,
moused, zero-prefix per trace — so the activity numbers quoted in the arc's commit messages
stop being transcript claims. Refuse the one-frame record as a workload by law
(`MIN_WORKLOAD_FRAMES`), the way pixelcost preserves-and-refuses the v0.4 chains record. The
log's cost rows are PRESERVED and graded nowhere: budget verdicts belong to `pixelcost`, and
feeding a moving-workload row through `sealframe`'s door is a future rung, not a footnote here.

## Act

`fpsrecord-records` re-reads the eight pins and re-derives the activity table; `fpsrecord-crossos`
asserts the host/container agreement and the declared conditions; `fpsrecord-selftest` proves six
plants bite — flipped byte, unknown version, one-frame workload, edited digest, foreign chain,
truncated log. The falsifier that names this brief: edit one digest in either committed chain and
`fpsrecord-crossos` reddens.
