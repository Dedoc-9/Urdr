<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `hainuwele/parallel/` — parallel substrates

Structures explored **alongside** the Euclidean arc, never disturbing it. The arc's geometry
modules (`heightfield`, `perception`'s supercover, `hitbox`'s AABB and integer aim-ray,
`chunkload`'s demand sets) all assume Euclidean ℤ². Anything that changes that assumption is built
here as a *parallel* substrate with its own gate stage, so the existing pinned goldens never move.

## `URDRPRS1` — the present probe (`present_probe.rs`, wall-clock class, deliberately ungated)

The first §3 instrument for the visible loop: a real Win32 window, a real present path, QPC stamps
at every `sealframe` instant software can reach, and a click-triggered white flash so a phone
camera can measure the one segment software cannot. Raw FFI, std-only, integer nanoseconds
throughout; the entry door refuses unknown flags; `--defect` plants a 50 ms stall the instrument
must catch in its own numbers or exit red. Like `bench.py` it reads a wall clock and therefore
never enters the gate — its LOG is what the repo will grade, under the `sealframe-honesty`
admission pattern, and a log without `--host` cannot graduate anything.

First named-host reading (Ally X, 2026-08-13, v0): frame work p50 0.50 ms / p99 2.03 ms at
1280x729 against an 8.33 ms slot — and the instrument's first catch was ITSELF: 176 of 723
deadlines missed with 0.5 ms of work, the classic Sleep(1)-under-15.6ms-timer-resolution pacing
defect. v0.1 requests 1 ms resolution, logs whether it was granted, and records lateness as a
magnitude rather than a count. The red-first plant was caught on the same host before any real
run was trusted.

v0.2 carries the P2 contract — *measure the renderer until resolution is an evidence-derived
decision* — and is the instrument the analysis rung will read. The workload became real: an
integer 3D terrain (heightfield mesh, yaw-orbit camera, z-buffered edge-function fill, no float
anywhere), swept across resolution CELLS that run as interleaved segments with the order rotated
between passes, so the treatment axis is not a proxy for elapsed time and between-pass spread is
the variance ruler. The a-priori prediction is affine cost in pixel count; the log records
per-(cell,pass) bands and the analysis decides whether the data agrees — the form is a prediction,
never an assumption. A named-host run now REFUSES without `--power` and `--scheduler` (probelog
pinned the strict door's refusal as this instrument's specification, and v0.2 discharges it), and
`--defect` stalls exactly one cell so the per-cell aggregation must LOCALIZE the plant rather than
merely notice it.

v0.3 is what v0.2's own red-first run forced, before any real data was trusted. The cross-cell
defect check MISSED a plant that was plainly present, because a larger cell honestly costs more
than a stalled smaller one — comparing across cells conflates the treatment with the plant. The
stall now runs on the middle cell's ODD passes only, so stalled-vs-clean passes of the SAME cell
are the comparison and the treatment cancels. The same run exposed flash frames polluting the
raster distribution (a white fill is nearly free, so lo columns read as if a 720p frame cost tens
of microseconds) — flash frames are excluded from workload rows and counted separately, while
staying in the click chains where they belong. And lateness became a per-segment epoch: one
absolute schedule let a stalled segment's lag be "caught up" inside the next cell's segment, which
then wore the blame.

v0.4 kills the downscale artifact `pixelcost` v1.1 named as this instrument's specification. v0.3
presented every cell into a fixed small window, so a 1920x1080 cell paid a StretchDIBits DOWNSCALE
the real demo would never pay natively — leaving 1080p's present band structurally dishonest and
its 60 Hz budget verdict UNDETERMINED. v0.4 presents 1:1 in a borderless popup covering the whole
screen: each cell blitted at its own size, centered, source and destination dimensions equal, the
border blacked at segment changes so a smaller cell never wears a larger cell's leftovers, and a
cell larger than the screen REFUSES (a clipped blit measures a different operation — the same
artifact class in a new coat). Present chains at every cell now mean what they say.

v0.5 removes the last human ritual from the cost question. Three named runs in a row arrived with
empty click tables, and the miss was the instrument's: the present cost is measured every frame,
but earlier versions only reported it on click frames, because the cost band was welded onto the
latency chain. Those are different questions — the chain needs a real click, the cost band needs
nothing but the loop — so every cell row now carries a present_ns band beside raster_ns, and
clicks are optional, wanted only for the input-latency chain itself. The same version repairs the
defect check's localization threshold, which fired a false DELOCALIZED on real data: 1080p's
thermal walk produced a spurious odd-even gap against a fixed constant that its own between-pass
range would have absorbed — a cross-cell constant applied to cells with different natural
variance, the v0.2 checker's lesson one level up. A non-planted cell is now judged anomalous only
against its own spread.

## `URDRFPD1` — the demo skeleton (`fpsdemo.rs`, wall-clock class, deliberately ungated)

P3.1: the playable skeleton, carrying the tree's replay DNA. A workload that depends on player
input is not reproducible unless the inputs are records, so `--play` (WASD + mouse-look over an
unbounded integer heightfield, 1:1 fullscreen at the measured 720p operating point by default)
RECORDS every frame's input to a trace, and `--replay` drives the same loop from the trace with
the framebuffer digested every sixty frames — integer-only math end to end, so two replays of one
trace must print identical digest chains, on one machine and across hosts. The digest is fnv64
and says so: a divergence detector, never an attestation — committed records keep sha256 on the
repo side. `--defect` is the red-first check in one run: a copy of every post-plant framebuffer
carries one flipped byte, and the clean and planted chains must match before the plant and
diverge at it. Cost rows (raster_ns / present_ns per segment) ride along unchanged from the
probe, so the budget the envelope established is checked against the real moving workload.

Said plainly, v0 was not the fp-chain: yaw plus a horizon-shift pitch approximation and a hash
heightfield; it claimed only the replay properties and the budget measurement — both verified on
the named host (thirty digest checkpoints identical across three replays; the planted byte caught;
the moving workload inside the envelope).

v1 (P3.2a) makes the pixels certified. The Q32.32 quaternion substrate is lifted VERBATIM from
`fpquat_rs` and the demo runs that placement's battery at every launch against the same golden the
gate pins; mouse-look is real rotation (yaw world-frame, pitch local-frame, renormalized
increments). The terrain is the URDRHF1 canon machinery lifted verbatim from `heightfield_rs`,
reproducing all three pinned canon scenes at launch, with the world sampled from the canon
"mountains" parameters over unbounded coordinates — the one edit is floored divmod in `noise16`,
identical on the canon domain, and the selfcheck reproducing the canon digests through the edited
function is the proof. A launch that fails its selfcheck refuses to run: conformance is the door,
not a comment. The selfcheck core was compiled and RUN on the authoring container before delivery
(battery and all three canon pins matching on Linux), so the kernels are cross-OS-reproduced
before the named host ever builds them. `fppose`/`fpclip` integration remains queued; the committed workload-record rung shipped as `fpsrecord` (URDRFPR1, gated) — the arc's traces, chains and named log are sha256-pinned records the gate re-reads.

v1.1 is what first host contact taught. The operator's v1 run was green on every claim v1 could
check and wrong on the one it couldn't — the picture: a green-and-magenta ribbon floating in sky.
The repair path is the finding: the v1 trace bytes replayed HEADLESSLY on the authoring container
reproduced the operator's 30-digest chain bit for bit, so the operator's frames could be examined
off-host, and every defect below was measured in them before being fixed. The floor was
backface-culled (`area > 0` kept one winding; ground below eye level winds the other way in
screen space — terrain the camera walks on is two-sided now). The magenta was a byte carry
(`wrapping_add` on a packed color with a saturated channel; colors are per-channel now, full
relief range, depth-fogged). The keyboard never arrived (the trace: 0 keyed frames of 1800, no
Esc — a WS_POPUP window from a console process doesn't take focus; v1.1 takes it explicitly and
prints keyed/moused counts in every --play summary). A synthetic walk found two traversal defects
no recorded run had reached — the render path truncated the camera to integer world units and the
eye stepped discretely at tile edges; deltas are Q8 end to end, the eye stands on bilinear
ground. The rasterizer's per-pixel multiplies and division became incremental adds, each adopted
only after a bit-identical chain against its closed form. And `--play` now REFUSES an existing
trace path — v1's default output was the exact filename of the operator's only recorded workload,
one bare invocation from replacing it (a record is not a scratch path). The headless replay
harness that made all of this measurable is the arc's new instrument: the math slice compiles
anywhere, so an operator's trace plus their digest chain equals their session, reproducible on
any machine that can run a compiler.

v1.2 is the second keyboard death and the end of trusting focus. v1.1's SetForegroundWindow
repair was reasoned from documentation and the host refuted it: the next recording came back
`keyed 0 | moused 0` — caught by the activity line v1.1 added, on its first outing. The durable
diagnosis was the asymmetry between the input channels: the mouse survived v1 because it is
POLLED (GetCursorPos reads global state, focus-free); the keyboard died because it was QUEUED
(WM_KEYDOWN reaches only a focused window, and Windows may refuse a console-spawned process the
foreground). v1.2 makes the channels symmetric — WASD and Esc are polled via GetAsyncKeyState —
the window is topmost so the operator sees what they steer, and focus is demoted from a
dependency to a reported condition (`focus_foreground` beside `timer_1ms_granted`). The render
path is untouched, so the pinned chains stand; and the same session measured what they now
prove: the operator's Windows build and the container's Linux build printed identical digest
chains on two different traces — 60 checkpoints, two OSes, zero divergence. Cost on the named
host at the v1.1 rung: raster med ~2.0–2.4 ms, worst 3.1 ms, present med ~0.28 ms at 720p,
inside the 8.33 ms slot, with the first-frame cold start (~15 ms) a named start condition.

v1.3 is the third death identifying the machine. v1.2's polling came back `keyed 0 | moused 0`
with `focus_foreground true` — the repair worked and the recording still starved, which closed
every software suspect and left the device. The matrix across three recordings says it plainly:
v0 (console foreground) moused 800; v1.1/v1.2 (demo foreground) moused 0 — and the named host is
a ROG Ally X, a handheld whose sticks emulate a mouse only while the desktop is foreground; the
vendor layer swaps them to gamepad mode the moment a fullscreen app takes focus. Taking the
foreground — v1.2's one verified success — is what unplugged the operator's only pointing
device; the keyboard was never dead, it was never there. v1.3 polls the native channel: XInput,
loaded at runtime so absence is a reported condition (`xinput_loaded | pad_connected`) rather
than a link failure — left stick walks, right stick looks, B or Start ends the run — and every
channel merges into the same trace vocabulary, so replay neither knows nor cares which device
recorded. The input arc's lesson, stated once: an instrument must speak the machine's native
input, and every assumption it retires must become a reported condition, not a memory.

v1.4 aliases the desktop vocabulary. v1.3's run was the arc's first partial success and its most
precise measurement: `pad_connected true | padded 0 | moused 1386` — the vendor layer holds the
physical sticks and emits desktop input (the right stick became the mouse; the operator's pan
replayed cross-OS thirty for thirty as the record's third trace), while the exposed XInput
device reads idle. In that same scheme the left stick emits arrow keys — the one vocabulary the
demo did not poll. Arrows now alias WASD and Enter joins the end-run set, so the walk arrives on
whatever the machine speaks; the trace bits, and therefore replay, are unchanged.

v1.5 is the one-frame walk. Enter joined the end-run set in v1.4, and Enter is the key that
launches the program from a shell — still physically down at frame 0's poll, so the first
attempted real walk ended at birth, caught by the instrument's own activity line (`frames 1 |
keyed 0`). Launch-time input state must not leak into the run: end keys and end buttons now arm
on an observed release, so ending requires a press that began after launch. The overwrite door
did its quieter job the same minute — the second attempt refused to replace the one-frame
record wearing the walk's name.

v1.6 opens the fidelity spend, chosen by pictures and priced before purchase. Candidate 1 —
height bands plus an integer lambert sun — was rendered against the committed real-walk workload
in the headless harness before the demo changed: the altitude anchors come from a measured
height histogram over the canon terrain rather than taste, the lighting is a per-triangle
integer normal against a fixed sun, and all of it is VIEW-layer (the canon heights and the
certified camera untouched, the selfcheck door unchanged). Its price on the identical committed
workload measured statistically zero on the authoring container; the honest number is the host
A/B the protocol runs — the committed v1.5 named log is the before, the same trace replayed
under v1.6 with conditions declared is the after. The shipped render was proved bit-identical to
the approved candidate frames before delivery, and the v1.6 expected chain for the committed
walk was produced cross-OS first.

v1.7 is the reach sweep, strictly as an experiment. R2b's harness pictures answered the
architectural question — reach, not local terrain resolution, is the dominant knob — and showed
the full ladder is photo-mode territory. `--reach <tiles>` (default 20, the v1.6 window) derives
the ring ladder at launch by the v2 R2a machinery with the pixel budget fixed, so reach is the
one variable; the derived ladder prints in the log ring for ring, checkable against the model.
Three contracts ride separately: runtime (the derivation is deterministic and printed),
performance (each reach classifies independently against the measured budget from its own named
rows on the committed walk — candidate points are candidates, the host decides), and identity
(reach at or under the v1.6 window never enters the ring path, so the pinned chains stand as
the regression contract; and the vista may not leak sky at a ring seam, checked against a
monolith render in the authoring harness before delivery). Prefill runs before the frame timer
as a printed start condition — a cache cold-fill inside frame 0 would contaminate the
measurement rather than describe it — and the cache's unbounded growth is a named defect owned
by v2's R4, not hidden. The intended shape is two modes with measured borders: a competitive
default whose reach FITS the budget, and a photo/vista mode explicitly permitted to exceed it.

v1.8 repairs the sweep's two catches. The first was the author's: v1.7's log transparency
lines never shipped — the version line still read v1.6, with no reach field, ring lines or
prefill count — because an edit was applied without asserting it matched; every edit in the
repair asserted, and the lesson is the repo's own, landed at home. The second was the
measurement's: the host sweep put the envelope on record (the v1.6 window FITS 120 Hz; five
hundred tiles already costs a 60 Hz-class median; full reach runs near forty milliseconds) and
thereby identified the per-vertex quaternion sandwich as the ring path's dominant cost. The
rotation is identical for every vertex, so v1.8 derives the rotation matrix from the certified
vrotate three times per frame — the basis images, in Q16 — and applies it per vertex in plain
integer arithmetic; the certified kernel still owns the rotation, the matrix is its per-frame
shadow, and the near path still runs vrotate per vertex untouched, holding the pinned chains.
Silhouette and seam laws re-verified unchanged under the new arithmetic. The next measured
lever is already named: the per-vertex height lookup through a hashed cache, which a
per-ring resident grid would turn into direct indexing — that is a candidate rung, to be
adopted the way this one was, by before/after on the committed walk.

v1.9 adopts that candidate. Each ring holds its heights in a flat resident grid indexed by
lattice position, refilled from the backing cache only when the camera crosses that ring's
stride boundary — ring k rebases every 2^k tiles, the refill amortizes, and rebase frames stay
visible honestly in the worst column. The values are identical (a lookup restructure, not an
arithmetic change), so every v1.8 chain stands at every reach — verified on the authoring
container against the operator's own sweep digests before delivery, first and last checkpoint
for the five-hundred and two-thousand tile points. Container indication: roughly a third off
mid-reach frame cost on top of v1.8's matrix; the host re-sweep says what it truly buys, and
whether the competitive 120 Hz boundary moves past sixty tiles. Grid memory is bounded by the
ladder; the backing cache remains unbounded — R4's debt, still named, still owed.

The camera-feel verdict arrived after the v1.9 sweep: the operator walked the world across
several versions and reported it felt good. The view and input constants are now FROZEN as
operator-confirmed rather than author-guessed — mouse sensitivity, the pitch clamp, eye height
and walk speed hold, and any future change to them is a deliberate act with a before/after,
not a tuning drift. The v1.9 envelope on the named host, chains proven identical to v1.8's:
reach 60 and 120 run the committed walk with zero late frames (the 120-tile point is six times
the original draw distance inside the 120 Hz budget), 250 and 500 are marginal at 120 Hz and
solid at 60 — the competitive default awaits the operator's freeze between 60 and 120.

v1.10 pays R4's debt: the backing cache is bounded. `--cache-cap N` caps the height map at N
entries with insertion-order eviction — the victim is the oldest arrival, tracked in an
explicit ring, exactly v2/cache.py's law (a cache over a pure function is a view, and eviction
is a view event), and zero means unbounded v1.9 behavior. THE IDENTITY CONTRACT WAS VERIFIED
BEFORE DELIVERY against the gate's own committed oracles: the committed walk replayed at reach
500 under caps 4096, 8192, 32768, 65536 and unbounded, and at reach 60 under caps 4096, 16384
and unbounded, produced digest chains byte-identical to `spec/attest/fpsdemo-envchain-r500.txt`
and `-r60.txt` in all eight sweeps — starvation to infinity, the values never moved. What the
cap COSTS is deterministic and already measured: the walk's working set is 76,606 entries at
reach 500 and 22,424 at reach 60, an uncapped run recomputes exactly once per entry, and every
cap below the working set thrashes the drift pattern hard — 65,536 recomputes 4.5× the
unbounded count, 32,768 recomputes 8.3×, 8,192 and 4,096 saturate near 17.6× (recompute counts
are trace-determined, identical on any machine; only their wall-clock price is the host's).
The numbers therefore say what the cap is FOR: a hard memory ceiling set ABOVE the expected
working set — a safety rail against unbounded growth on long sessions, not a knob for
shrinking below the walk's footprint. The host cap sweep prices the thrash in milliseconds,
and the cap freeze follows the reach pattern: swept first, then chosen from numbers.

v1.11 is THE COMPETITIVE FREEZE — the operator's decision, made from the measured surface and
shipped as the defaults. REACH 60 IS THE COMPETITIVE DEFAULT because it is the measured
ceiling-clean operating point: the committed envelope grades it FITS at 120 Hz BY CEILING
with zero late frames on the committed walk, the only swept reach with that property — not
because it "feels competitive". The mode contract: COMPETITIVE (default; reach 60, 120 Hz
budget FITS, cache rail derived, deterministic budget-safe working point) — HIGH-REACH /
VISTA (`--reach 120`; six times the original draw distance, measured viable at 120 Hz with
sub-millisecond overruns, chosen for sightline ambition, not guaranteed for competition) —
PLANETARY (a derivation, not a tuning knob: v2 R2c's horizon door, awaiting its own
adoption). THE CACHE RAIL DERIVES: absent `--cache-cap`, the cap is twice the ladder's own
live footprint (the arithmetic capcost pins), a declared margin POLICY on the committed
evidence, never a proven optimum; `--cache-cap 0` stays unbounded, an explicit N is honored,
and the log declares which policy ran (`cache_policy`). Verified before delivery on the
authoring container: the derived rail resolves to 35,828 at reach 60 and 139,322 at reach
500, both replays of the committed walk count-identical to unbounded (zero evictions,
recomputes equal to the working set) with digest chains byte-identical to the committed
oracles. Compatibility, stated: pre-v1.7 traces replay against their committed chains with
`--reach 20`, because the default moved to the frozen point. Unmeasured intervals stay
unmeasured: reaches 20..60 and past 500, and the 1080p resolution cell — the probe's
three-cell sweep (640x360, 1280x720, 1920x1080, 1:1 since v0.4) is the one resolution
question P2 left open, and 1080p certification waits on that measurement, not on this
freeze.

## Queued: `URDRCHB1` — the discrete Chebyshev net (designed, not built)

**Motivation.** The arc establishes order-independence *by checking*: `commute` builds both orders
and compares them; `rannull` proves parallel equals every serial; `nway` does it for N! orders.
Discrete integrable systems obtain the same property **by construction** — multidimensional
consistency ("consistency around the cube") makes the diamond commute because of what the equation
*is*, not because a prover confirmed this instance. Bianchi permutability is its algebraic form,
and it is exactly the arc's "zero rebases."

**The structure.** A discrete Chebyshev net is `r: ℤ² → ℝ³` with `(Δ₁r)² = f(n₁)`,
`(Δ₂r)² = g(n₂)` — opposite edges of each quad equal in squared length, each depending on one
lattice index only; equivalently `Δ₁₂r ∥ N̂`. Two facts make this a fit for this repository:

1. The condition is stated on **squared** edge lengths, which this arc already computes in exact
   integers everywhere. The *discretisation* is what makes it exact — this is not a numerical
   approximation of a smooth surface.
2. `f` and `g` are **arbitrary functions of one lattice index each** — the discrete residue of the
   reparametrisation freedom `u → U(u)`, `v → V(v)` on asymptotic lines. That is the
   arbitrary-function (gauge) symmetry Noether's *second* theorem requires, and which a uniform
   grid does not have.

**Why Dini.** Dini's surface has constant Gaussian curvature `K = −1`, and the Dini family arises
from the 1-soliton (kink) solution of sine-Gordon — pseudospherical surfaces correspond to
sine-Gordon solutions, and Bäcklund transformations generate new ones from old.

**Open before building — stated honestly.** Noether's second theorem is an *iff*: no
arbitrary-function symmetry, no identity. The Chebyshev freedom is *geometric*; whether it descends
to a **variational** symmetry of a discrete Lagrangian on this net is unestablished, and the whole
programme rests on it. A negative answer is a valid result and would close the line cleanly.

**References.** Schief, *Discrete Chebyshev nets and a universal permutability theorem*;
Bobenko & Suris, *Discrete differential geometry: consistency as integrability*; Hydon & Mansfield,
*Extensions of Noether's Second Theorem: from continuous to discrete systems* (Thm 5.1:
`D̃ᵅᵣ Ẽᵅ(L) ≡ 0`, identically, off-shell).

## Built, and DELIBERATELY UNGATED: `URDRRPI1` — `rpimm.py`, the degree-dimension problem for RP^n

**Status.** Built with its own falsifiers and its own runner; **no stage in `verify.py`**, by design.
Run it with `python3 hainuwele/parallel/rpimm.py`. It stays ungated until there is either a
constructive family that survives the corrected tangent-space test or an obstruction genuinely beyond
the blockwise case. Ungated means it **can rot**, and that is stated rather than hidden — the same
treatment `bench.py` gets for wall-clock. Selfcheck: 16/16.

**What it is.** The question is whether a bounded-degree *even* polynomial map can immerse `RP^n` in a
target dimension approaching the topological one, and the module holds the corrected machinery for
asking. Exact rational arithmetic throughout; no float ever decides a rank.

**Three errors pinned as witnesses, because each was made in the design that preceded it.**

1. **A parity category error, not a missing proof.** The original construction was antipodally ODD and
   was asked to induce a map on `RP^n`. It cannot: descending to `S^n/{±1}` needs `Φ(-x) = Φ(x)`, and
   an odd map satisfying that is identically zero. Only EVEN maps descend, so the linear block `x` is
   inadmissible from the start rather than "lost to the quotient". Measured `(True, False, True)`.
2. **The identity block made the original obstruction vacuous.** The argument was "one block's
   differential dies, therefore the rank drops." Measured, at exactly the points where `DQ_k = 0` the
   map with an identity block still has FULL rank `n` — `n = 2,3,4,5` all give `n`, not `n-1`. A
   vanishing sub-block is not a rank deficit until you count what survives.
3. **"Positive-dimensional" failed at a boundary case.** The vanishing locus is exactly
   `S^(n-|B_k|)`, so a *proper* block missing one coordinate gives `S^0` — two points. The exact
   dimension formula replaces the adjective; `(n,|B|) = (5,4) → S^1` but `(5,5) → S^0`.

**The lemma that survives, in its general form.** For an even variable-separable map with blocks
partitioning the coordinates and every monomial of degree ≥ 2, let `Z` be the union of blocks
vanishing *entirely* at `x`. Every direction supported in `Z` is tangent and in the kernel, so

    rank DΦ|T_xS^n  ≤  n − |Z|

Measured on 6 cases, holds on 6, **attained** on 6, and below `n` on 6 — so it is a bound that bites
rather than a slack inequality. It recovers both special cases: block-supported points give
`rank ≤ |B_1| − 1` (measured `(2,1)→0`, `(3,2)→1`, `(4,2)→1`, `(5,3)→2`), and `{x_Bj = 0}` gives
`rank ≤ n − |B_j|`. **The obstruction is factorization through independent coordinate projections —
locality — not the degree:** raising the degree from 2 to 4 to 6 leaves the rank at 2 against a needed
4. That is what later constructions must avoid.

**The rank test was the most dangerous error available.** The immersion condition is the rank of the
differential *restricted* to `T_xS^n`. Two sound routes are implemented and cross-checked — project
onto a tangent basis, or stack the normal row `xᵀ` and subtract one, since
`ker([A; xᵀ]) = ker(A) ∩ T_x` gives `rank(A|T_x) = rank([A; xᵀ]) − 1` identically. They agree on 12
of 12 cases, and a **mutation probe** proves the agreement can fail: a variant using the ambient basis
disagrees on 12 of 12, so the cross-check is measuring something (L23).

**And the naive ambient test is off by exactly one, for a reason.** Euler's relation `A x = d·Φ(x)`
puts one unit of rank in the radial direction, verified on every case. Measured, there are points
where the ambient rank reaches `n` while the true tangent rank is `n−1`: `(n, ambient, tangent)` =
`(3,3,2)`, `(4,4,3)`, `(5,5,4)`. **The naive test certifies an immersion that is not one.** Kept live.

**The algebraic certification has a real-versus-complex trap.** Sound direction only:
`I_minors + I_sphere = (1)` ⟹ immersion. The converse fails, because the Nullstellensatz is about
algebraically closed fields while immersion is a real question. Witness in exact Gaussian integers:
`f = x₀² + x₁² + 2x₂² + 2x₃²` is positive definite so `V_R(f)` misses the sphere entirely, yet
`z = (1,1,0,i)` gives `Σz_i² = 1` and `f(z) = 0`. A pipeline reading "ideal ≠ (1) ⟹ not an immersion"
returns a false negative here.

**Positive control, and the gap that shows where the difficulty is.** The Veronese returns rank exactly
`n` at every point tested for `n = 2…5`, so the rank routine is measuring separability and not a bug.
Its target dimension is `(n+1)(n+2)/2` = 6, 10, 15, 21 — **quadratic**, against topological targets
linear in `n`. The open question is whether any bounded-degree family closes a quadratic-to-linear gap.

**Refutations only, never a certified positive.** A refutation is exact from ONE witness: if the
tangent rank drops below `n` anywhere, the map is not an immersion. A positive is not available by
search, so the subset census reports `RPIMM_REFUTED` or `RPIMM_CANDIDATE` and **never "immersion"** —
enforced in the return vocabulary, not in a comment. This is the same asymmetry `autoroute` inherited
from view determinacy (L27), arriving from a different direction. Measured over monomial subsets of the
degree-2 Veronese at `n = 2`: size 3 → **20 refuted, 0 candidates** (a real negative), size 4 → 13
refuted, **2 candidates**, size 5 → 3 refuted, 3 candidates.

**Two invariants, kept separate.** `m_d^imm(n)` and `m_d^emb(n)`. Conflating them would let the
Veronese's *embedding* bound masquerade as an immersion bound.

**Open, stated honestly.** The asymptotics of `m_d` are untouched — this module only makes the question
askable. The subset search ranges over MONOMIAL subsets rather than general linear projections, so its
CANDIDATE verdicts are weaker than they look. The point sets used for refutation are pinned and finite.
Whether this optimization problem is already known under another formulation has **not** been
established by a literature review, so it is a natural question here and not a claimed open problem.
