<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: versionarc-evidence -->

# `versionarc` (URDRVRA1) — design brief

*A version that stamps evidence must be documented.*

## Observe

`fpsdemo` and `present_probe` are wall-clock class and deliberately ungated: no timing they
produce may enter the gate, so neither carries a design brief, so the brief-falsifier-index
coupling that binds every gated module cannot reach them. That exemption was granted for
BEHAVIOUR — the tree refuses to certify a number it cannot reproduce, and that refusal is
correct. It became something else without anyone deciding it should. Four fpsdemo versions
shipped without a paragraph in their own module README, and every gate run in that span was
green, because there was nothing in the tree entitled to look.

The damage is not tidiness. Committed records under `spec/attest/` stamp the version that
produced them, and the gate re-reads those records on every run. Two of the missing versions,
v1.13.2 and v1.13.3, stamp six such records. A reader holding `fpsdemo-scene-s1-full.txt` could
see that `fpsdemo v1.13.2` produced the bytes the gate checks and could not learn anywhere in
this repository what v1.13.2 was. That is an evidence-provenance hole, and it is a documentation
law the gate may enforce without certifying a single nanosecond.

## Orient

Three things had to be decided rather than assumed.

The law is ONE-DIRECTIONAL, and the data decided that. The converse verdict was drafted — a
README paragraph for a version no record ever stamped — and the corpus refuted it before it was
written: the fpsdemo section documents v1.1 through v1.8 and evidence stamps almost none of
them, because a version can be superseded before anyone runs a measurement worth committing.
Documenting a version that never stamped a record is good documentation. An ORPHANED verdict
would have reddened the tree for its own thoroughness.

The obligation has TWO INDEPENDENT SOURCES. Evidence obliges (a stamp on a committed record) and
so does the source's own title line (the version a reader will meet next, which is exactly the
one nobody has written up yet). Starving one proves they are separate: with no records at all,
`fpsdemo` still owes its README the version it declares, while `present_probe` declares none and
owes nothing, so it reports VACUOUS rather than CLEAN.

TOKEN BOUNDARIES ARE THE MECHANISM, not a detail. A substring test lets `v1.14` satisfy `v1.1`
and lets `v1.13.2` satisfy `v1.13`, silently and in both directions, which would make the door
report CLEAN precisely on the versions most likely to be missing — the point increments at the
end of an arc. Both directions ship as plants.

## Decide

The register is DATA, swept mechanically, because L68's lesson is that a caller reads an API and
not a paragraph, and a documentation door written as prose would be the joke telling itself. Two
artifacts share one README, so every sweep is scoped to the `## ` section that names the
artifact's code — otherwise `present_probe`'s paragraphs would document `fpsdemo`'s versions and
the door would certify a coincidence.

`present_probe` is in the register as the CONTROL, not as a second target. It stamps v0.1, v0.3,
v0.4 and v0.5, its section names all four, and the identical sweep reports it CLEAN. A door that
refuses everything it is pointed at has measured nothing.

`does_not_show`: that the paragraph is true, current, or useful. This door establishes only that
a version is not a stranger to its own README — that a reader who meets it on a record can find
the place where the project speaks about it. `documented != accurate`, and no sweep will close
that gap.

## Act

`versionarc-evidence` holds the law over the committed corpus; `versionarc-declared` holds it
over the version the source declares and reports the control; `versionarc-selftest` proves the
plants bite. The falsifier naming this brief: stamp a record with a version the module README
does not name — which is what the tree itself did at `6d450cf`, where this door was run before
the repair and returned `fpsdemo UNDOCUMENTED (v1.13.2 v1.13.3 v1.14)` beside `present_probe
CLEAN` — and `versionarc-evidence` refuses.
