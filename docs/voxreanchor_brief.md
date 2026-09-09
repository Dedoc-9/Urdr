<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!-- brief-falsifier: voxreanchor-finding -->

# `voxreanchor` (URDRRAN1) — design brief

*Can one cheap predecessor-derived anchor retire multiple current-frame discoveries before
fragmentation forces a re-anchor?*

## Observe

`voxrun` measured what becomes of a predecessor's ownership runs and found the failure mode is
**fragmentation**, not disappearance: 95.4 per cent of predecessor run-length does not vanish, and
the owner is still somewhere in the span. It read that as an opening. A stream demanding whole-run
survival collects only what survives whole; one that could **re-anchor** has far more in front of it.

The census priced nothing, and pre-registered five predictions one commit early. This rung builds the
arms, prices them in separate accounts, and scores that record.

## Orient

Three arms and — decisively — **one control**.

| arm | discover | construct | transition | verify | reanchor | retired | unit total |
|---|---|---|---|---|---|---|---|
| baseline | 103,680 | 0 | 0 | 0 | 0 | 0 | 103,680 |
| whole_run | 60,502 | 8,839 | 8,839 | 66,516 | 0 | 43,178 | 144,696 |
| reanchor | 7,038 | 8,839 | 8,839 | 103,680 | 7,038 | **96,642** | 135,434 |
| **coherent** | 8,674 | 1,080 | 1,080 | 102,600 | 7,594 | **95,006** | 121,028 |

**The control takes no predecessor at all.** It anchors on the first pixel of each *current* scanline,
verifies forward, and re-anchors wherever verification breaks. It has never seen another frame.

It retires 95,006 of the 96,642 the predecessor-seeded arm retires — **98.3 per cent of the result** —
and buys that with 1,080 constructions against 8,839.

**The break-even verification cost says it without a cost model at all.** Let one verification cost
`v` discoveries; an arm beats the baseline exactly when `v` is under its bar:

| arm | break-even |
|---|---|
| whole_run | 2125/5543 = 0.383 |
| reanchor | 35963/51840 = 0.693 |
| **coherent** | **21313/25650 = 0.830** |

**The loosest bar belongs to the arm with no predecessor.** The previous frame makes the inequality
*harder* to clear, not easier.

## Decide

**Amortization works and the predecessor is not what pays.** A sequential consumer can retire 93.2
per cent of observations with the predecessor and 91.6 per cent without it. What the predecessor buys
is 1,636 observations — 1.5 per cent of the frame — and what it costs is 7,759 additional
constructions and 1,080 additional verifications. Under any cost model in which building an anchor is
not free, that is a net loss.

Ownership is compressible, and **the compressibility is spatial rather than temporal.** `voxrun`
measured run structure and read it as an opportunity across *time*; essentially all of the available
amortization is scanline coherence *within* the current frame, which needs no previous frame to
exploit. The arc's amortization hypothesis survives. Its temporal premise does not.

**The control is the whole rung.** Without it, 96,642 against 43,178 reads as a triumph for the stream
hypothesis, and the arc would have gone on to build a certificate stream on a premise the data does
not support. `the_control_takes_no_predecessor` is proved on the module's own AST — the control's
function cannot receive a predecessor map — so the comparison is structural rather than a courtesy.

## The disposition of the pre-registration

Two of the five were not valid objects, and **neither was found by inspecting the record**. Both were
found by trying to score it.

| id | disposition | mechanism | why |
|---|---|---|---|
| R1 | **miss** | as stated | whole-run retires *exactly* the surviving share, not strictly less |
| R2 | **hit** | **not as stated** | only 63.8 per cent retired under the named mechanism; a control with no predecessor obtains 98.3 per cent of the result |
| R3 | **void** | not scored | names a predecessor-seeded stream on a corpus with no adjacency |
| R4 | **hit** | **not as stated** | the inequality fails on the stream's *own* accounts, before the tile loop it blamed |
| R5 | **withdrawn** | not scored | the record's own header declares the safety contract not a prediction and not scored — and R5 registers it as one |

**R1 is the instructive miss.** Its stated mechanism — verification is not free, and a run that turns
out to have fragmented is paid for and discarded — is *true*, and both halves are visible in the
accounts (66,516 verifications, 60,502 discoveries). It acts on **cost**. The claim was about
**retirement**, and retirement under an all-or-nothing policy is exactly the surviving run-length the
census measured. The prediction fused two accounts the census had deliberately recorded apart, in the
record the census itself shipped.

**R5 is a self-contradiction in a committed record.** Its header states plainly that the observable
contract is a precondition rather than a result and is not scored; R5 then registers exactly that as a
prediction. Scoring it would have been a free win on something guaranteed to hold.

**The original record is not edited.** `spec/attest/voxstream-prediction.txt` stands byte-for-byte as
committed and is quoted here by the digest `voxrun` pinned; the dispositions live in a *separate*
record. A pre-registration whose unit of analysis is refuted is evidence **about** the refutation, and
rewriting it to match what was learned would delete the only thing commit order buys.

No registered prediction may be left silent: the disposition set must **equal** the registered set,
the identifiers are read out of the committed record rather than retyped, every entry carries a
reason, and mechanism is scored apart from outcome because the record's own header demands that a hit
from the wrong reason be visible as one.

## The anchor yield, which the census could not ask

| predecessor runs retiring ≥ | count of 8,839 |
|---|---|
| 1 observation | 7,444 |
| 2 | 5,519 |
| 4 | 4,657 |
| 8 | 4,317 |
| 16 | 3,526 |

## Act

`tools/terrain/voxreanchor.py`, gate stage `voxreanchor` (four rows: arms / finding / disposition /
selftest), red-first `tests/test_voxreanchor.py` (59 falsifiers), and the committed record
`spec/attest/voxstream-disposition.txt`. No successor is pre-registered, because this rung closes the
stream question rather than opening one — and manufacturing a prediction to satisfy a habit would be
its own inflation.

`does_not_show`: **nothing about time**, and no wall clock enters. **Not what a verification actually
costs** — the unit-cost totals are a convention carried from `voxrun`'s recorded variables, and the
break-even ratios are reported precisely so a reader can price a verification differently and reach
their own verdict; measuring that ratio inside a real rasteriser is a different rung. **Not that no
stream can pay**: three arms were built and none clears its own bar at unit cost, which is a fact
about these three. **Not that the predecessor is useless for anything** — it is useless for *this*,
and 1,636 observations is a real if small quantity. **Not that the lattice is representative**: it
measurably is not, so the control is also measured on the adversarial corpus, where it retires 86.5
per cent against the lattice's 91.6. And **no promotion**: `voxref` is read only for its two
dimensions and its world digest, an enumerated allowlist checked on the AST, and no arm is proposed
for the renderer.

`falsifier`: `the_arms_reproduce_the_observable_exactly` reddens the day any arm reconstructs an owner
map differing from the reference as a list, which is the precondition of every number above;
`the_control_takes_no_predecessor` reddens if the control ever gains access to a previous frame, which
would make the comparison it exists to provide worthless; and `the_predecessor_does_not_pay` reddens
the day the predecessor-seeded arm's break-even bar rises above the control's, which would invert this
rung's finding and reopen the temporal premise.
