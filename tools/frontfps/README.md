<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# frontfps — the FPS/MMO front end (URDR-FPSW-1, staged)

One consolidated module (`frontfps.py`) that carries the authoring surface of a
competitive shooter / MMO at the **authority layer**: meshes, skeletal rigs, capsule
hitboxes, actor instances, spawn points, and D16-compatible region seams under one
content-addressed identity law. It is the "advanced" successor of the existing
front-end line — built by scraping the load-bearing logic, not the code, of what was
already measured, then re-earning everything through its own red-first stage.

Grades in this file follow `spec/D5-ledger.md` (maturity × evidence). Everything not
explicitly `MEASURED` here is design, and says so. Performance and visual-fidelity
numbers appear ONLY in §6, graded, with their precondition stated. No stage opens
until the previous stage's OODA report closes; no OODA report closes without the
gate rows it names being green.

## 1. The consolidation map (what was scraped, from where)

| Law carried forward | Source (measured there) | Where it lives now |
|---|---|---|
| Canonical bytes → SHA-256; identity is content | `urdr/canon.py` (L1) | `canon_bytes` / `world_digest` |
| Geometry-only identity; provenance excluded | `tools/frontend/canon_ref.py` (D14) | canon never reads `provenance`; folding defect ships in-module |
| Integer snap at authoring; runtime never rounds | D14 / N4 boundary | `_need_int` — FPSW-REFUSE, never round |
| Edge normalization (min-first, sorted) | URDROBJ2 | mesh section of `_canon_parts` |
| Authored order IS content for instances | `tools/netcode/worldstep.py` (N4) | actors + spawns are sequences; tested from both sides |
| Strictly-increasing integer seams | `tools/netcode/worldregion.py` (D16) | `regions` obligation |
| Typed, total refusals; no partial admit | 18 kernel codes + layer codes | `FpswError` (`FPSW-REFUSE`); no digest for an inadmissible world |
| View is display-only, witness-bound | `spec/D15` view-export | `to_view` (`URDR-FPSW-VIEW-1`) |
| Defects ship with the feature | every gate stage | provenance-folding + floor-radius defects |

New in Stage 1 (no upstream precedent): the **rig topology law** (bone 0 is root,
parents strictly below — cycles unconstructible, not detected), the **yaw refusal
law** (out-of-range yaw refused, never normalized: one value, one identity), the
**closed name alphabet** (`[a-z0-9_]+` — confusables unconstructible at the authoring
layer), and the **auto-affordance admission law** (§4).

## 2. Stage 1 — SHIPPED. OODA-1 report

**Observe.** Gate stage `frontfps` green inside the full gate (436 unit falsifiers,
335 stage rows, `GATE PASSED` ×2 bit-identical, Linux/CPython 3.10, PYTHONHASHSEED=0).
Corpus: `crate_solo 6c4c807f…`, `arena_duel 0c9ec33a…`, each computed twice per run.
Order laws measured **from both sides**: name-keyed scramble never moves identity;
actor/spawn/bone order swaps always do. Provenance-folding defect diverges (the gate
can redden). `auto_capsule` containment certificate holds on the crafted cloud and
its floor-radius defect violates it (r=3 vs floor 2 — the ceiling is load-bearing).
Ten obligations refuse typed. 17 unit falsifiers + 6 stage rows.

**Orient.** The authority-side authoring surface now exists and is total: everything
a world needs for deterministic play EXCEPT motion (no rotation math yet — D9 has no
quaternion/rsqrt), and everything an external tool needs to target it (plain dict in,
ADMIT+digest or exact refusal out). The binding constraint for every future stage is
D9's op set; the binding risk is scope creep into presentation (refused by D15).

**Decide.** Stage 2 is the rotation substrate — nothing animation-shaped can be
honest before it. Rejected alternatives: starting with the view stream (presentation
before authority inverts the membrane) and starting with keyframes over Euler
integers (accumulates the exact ambiguity quaternions exist to kill).

**Act.** Shipped: `frontfps.py`, `conformance_frontfps.txt` (2 vectors),
`tests/test_frontfps.py`, the `frontfps` gate stage, this report. Pivots + LLM notes
for the whole ladder are §5's rightmost columns — each stage re-reads them at open.

## 2b. Stage 2 — SHIPPED. OODA-2 report

**Observe.** `fpquat.py` on the frozen FIELDFP laws (ONE = 2^32, `_rdiv`
round-to-nearest ties-away, i64 refusal ceiling — imported, not reinvented).
Battery: 66 rows, digest `3f4aa0d1…`, ×2 per gate run; gate now 452 unit
falsifiers + 340 rows. The rsqrt law is an inequality proof per input
(r²·x ≤ 2^96 < (r+2)²·x), not a sample. Corpus bounds measured then pinned with
~2× headroom: unit-norm ≤2 ulp (pinned 4), conj roundtrip ≤8 (pinned 16),
composition ≤15 (pinned 32), rotate norm² drift ≤39 (pinned 64). **C99 placement
ADMITTED** (sandbox host, gcc 11.4, `-std=c99 -Wall -Wextra` clean): battery
digest bit-for-bit, twice, refusals total, AND the wrap64 defect digest agrees
with the reference defect (`5c965ff8…`) — golden *and* defect parity, the
rigidity-precedent bar. **Rust placement authored** (334 lines, std-only,
hand-rolled SHA-256): SPECULATIVE until a named host prints ADMITTED twice with
the defect caught.

**Orient.** Rotation now exists on the frozen substrate with two agreeing
placements; nlerp gives Stage 3 its interpolant without trigonometry. One
first-hand datum for the LLM-affordance thesis: the C placement was written
same-session *from the module docstring's op recipes* and matched the golden on
first compile — the machine-checkable-spec loop (§5) held in practice, once
(`one datum ≠ a law`). The vacuity lesson of the day: the first isqrt defect
candidate (skip final adjustment) was *provably unreachable* for this Newton stop
rule — a defect that cannot bite proves nothing, so it was replaced by the wrap64
defect this repo has actually been bitten by. Check your defects against theory
before shipping them.

**Decide.** Stage 3 (URDR-CLIP-1 pose/clip canon) opens once the Rust placement
is ADMITTED on the Windows host (the ladder's own law: cross-placed before Stage
3 opens; Python+C99 already satisfies two-placement agreement — the Rust run adds
the named-host tier). The dual-quaternion pivot stays open and is weighed at
Stage-3 open on op-count, not elegance.

**Act.** Shipped: `fpquat.py`, `conformance_fpquat.txt` (1 vector, 66 rows),
`tests/test_fpquat.py` (16 falsifiers), gate stage `frontfps_quat` (5 rows),
`fpquat_c/fpquat.c` (ADMITTED here), `fpquat_rs/fpquat.rs` (pending your rustc),
this report.

## 2c. Stage 3 — SHIPPED. OODA-3 report

**Observe.** Since OODA-2: the Rust fpquat placement printed **ADMITTED twice
with the wrap64 defect caught on the owner's Windows host** (golden `3f4aa0d1…`,
defect `5c965ff8…`) — fpquat is now **three placements, two OSes, golden+defect
parity**; its grade row below is flipped. Stage 3 itself: `fpclip.py` (URDRCLP1)
— keyframed rotation tracks sampled by binary search + one Stage-2 `qnlerp` per
bone; a state machine whose transition choice is canonical minimum-priority with
ambiguity refused at admission. Gate now 466 unit falsifiers + 346 rows, ×2
bit-identical. Corpus: `walk_pose 73b763f8…`, `arena_trace 823a7746…` (96 ticks
@ 240 Hz through go/sprint/stop, the sprint tick arming the authored-order
defect), and the pinned budget proxy: **55 frozen divisions per biped pose
sample** (`fpclip-ops`). Tick times are computed absolutely (`_rdiv(i·ONE, HZ)`)
so rounding never accumulates across a match.

**Orient.** The owner's hardware guide became the pinned bench protocol
(`docs/bench_protocol.md`): named host, display segregation as law (built-in
120 Hz = performance surface; LG 75 Hz = workstation, latency-invalid), budgets
DECLARED until the protocol runs, plus two scope corrections (witness chains
prove state integrity, not input legitimacy; hit registration is exact at tick
quantization, sub-tick is netcode M3, unbuilt). The op-count row is the honest
bridge between this repo and the 3 ms tick budget: counts are host-independent
facts; milliseconds wait for the named-host run. Vacuity lesson recurred: the
first w-only defect arming failed because normalization moves w — re-armed with
an equal-norm axis rotation. Two defects in two stages died on theory before
shipping; the check-your-defect step is now standing practice.

**Decide.** Stage 4 (posed hitboxes + one-tick-late IK contract) opens after
fpclip cross-placement (C99 first, sandbox-verifiable; Rust on the owner's
host) — same law as Stage 2→3. The blend-graph-vs-tree pivot stays open; nlerp
composition data from Stage 4's posed corpus will decide it.

**Act.** Shipped: `fpclip.py`, `conformance_fpclip.txt` (2 digests + 1 count),
`tests/test_fpclip.py` (14 falsifiers), gate stage `frontfps_clip` (6 rows),
`docs/bench_protocol.md`, this report.

**Act, addendum (cross-placement).** `fpclip_c/fpclip.c` ADMITTED on the sandbox
gcc-11.4 host: pose + 96-tick trace bit-for-bit ×2, 55 ops, refusals total, and
the authored-order defect trace agrees with the reference defect digest
(`1e6b480c…`) — golden AND defect parity, second rung in a row. `fpclip_rs/`
authored (319 lines, std-only), SPECULATIVE until the owner's host prints
ADMITTED twice with `--defect` caught — that run opens Stage 4.

## 2d. Stage 4 (authority core) — SHIPPED. OODA-4 report

**Observe.** Since OODA-3: fpclip Rust ADMITTED ×2 + defect caught on the owner's
host (pose/trace/defect digests bit-for-bit) — **fpclip: three placements, two
OSes, golden+defect parity**, Stage 4 opened lawfully. Stage 4's authority core:
`fppose.py` (URDRPSE1) — pose × rig → world transforms by hierarchy composition
with normalize-per-compose (drift cannot accumulate down a chain), and posed
segment capsules with an EXACT integer point-in-capsule certificate (boundary
tested to one ulp). Gate 474 unit falsifiers + 351 rows, ×2. Corpus:
`posed_biped fee3c118…`, 77 ops per world-transform pass pinned. Two defects,
both armed the hard way: swapped compose order (quaternions do not commute) and
local-offset capsules — which are BYTE-IDENTICAL to the truth at the rest pose
(a test documents this) and fail coverage only on the reach pose built to move.

**Orient.** Two of my own scale bugs died at the gate before shipping: rig
offsets used as raw Q32.32 (microscopic skeleton, giant capsules — a vacuously
true certificate) and walk-pose rotations too subtle to arm the defect. The
authoring-grid→Q32.32 boundary is now ONE conversion in ONE stated place
(`_off3`). Third session lesson of the same shape: certificates and defects must
be armed against theory, not against the first fixture that comes to mind.

**Decide.** The one-tick-late IK contract stays DECLARED (pinned in the fppose
docstring: reads T−1 resolved contacts, writes T transforms, lag in the witness)
— red-first implementation waits for the physics wiring, where its falsifier
(same-tick vs lagged divergence, visible to `first_field_desync`) can exist.
Stage 5 (view stream) gates on fppose cross-placement, same law as before.

**Act.** Shipped: `fppose.py`, `conformance_fppose.txt` (1 digest + 1 count),
`tests/test_fppose.py` (8 falsifiers), gate stage `frontfps_pose` (5 rows),
this report.

**Act, addendum (cross-placement).** `fppose_c/fppose.c` ADMITTED on the sandbox
gcc-11.4 host (`-Wall -Wextra` clean, first compile): posed golden `fee3c118…`
bit-for-bit ×2, coverage certificate on walk AND reach, the swapped-compose defect
(`04f23abe…`) and the local-offset coverage defect both bite, 77 ops, refusals
total — golden AND defect parity, the third rung in a row. `fppose_rs/` (std-only,
own SHA-256, i128, plus a u256 for the interior point-in-capsule test) **ADMITTED
×2 with `--defect` caught on the owner's Windows host** (rustc -O, 2026-07-13;
golden `fee3c118…`, defect `04f23abe…`) — fppose is now **three placements, two
OSes, golden+defect parity**. Stage 4 is closed on its own exit law; Stage 5 opens.

## 2e. Stage 5 (view stream) — SHIPPED. OODA-5 report

**Observe.** fppose is cross-placed — C99 self-verified in-session, Rust ADMITTED
×2 + defect caught on the owner's Windows host (three placements, two OSes,
golden+defect parity); Stage 4 closed lawfully. At Stage-5 entry the gate stood
at **474 unit falsifiers / 351 rows**. Everything a shooter needs to run
deterministically at the authority layer now exists and is measured: canon,
rotation, clips, posed hitboxes.

**Orient.** Stage 5 is URDR-FPSW-VIEW-2: a binary, delta-framed, display-only
successor of `to_view` (the D15 view law, versioned up). It CARRIES the
authoritative witness as a bound reference and moves a separate VIEW digest —
presentation, never authority. Three laws make it honest: (1) *recompute* — a view
frame is a pure function of authority state, recomputed identically twice;
(2) *structural no-feedback* — the renderer's inputs cannot reach canon, enforced
by signature not by comment (a frame that tries to carry a value back into
authority is unconstructible, not merely rejected); (3) *bandwidth as a
host-independent fact* — bytes per authored scene, pinned like the op-count
proxies, never fps. The binding risk is the membrane inversion D15 already
refuses: presentation leaking into authority.

**Decide.** First increment: the view-frame canon + the recompute law + the
structural no-feedback falsifier + a delta-framing defect (a delta frame that
references a base it never sent MUST be refused, `VIEW-REFUSE`), gated as
`frontfps_view` with a pinned per-scene byte count. Deferred by their own law: the
native layer-3 renderer (not gate-able — §6), and sharing the compact-witness
encoding with netcode replay (one format, two consumers) until both consumers
exist. Rejected: starting with the renderer (presentation before the stream
inverts the membrane).

**Act.** Shipped: `frontfps_view.py` (URDR-FPSW-VIEW-2), `conformance_view2.txt`
(1 digest + 1 byte count), `tests/test_frontfps_view.py` (11 falsifiers), the
`frontfps_view` gate stage (5 rows), this report. Gate **485 unit falsifiers /
356 rows**, ×2 bit-identical. Corpus: `view_stream bc60023…` over a 3-actor,
4-tick authored trajectory (one keyframe + three delta frames), **332 bytes**
pinned as the bandwidth proxy. The no-feedback law is non-vacuous: the fold
defect makes the bound authority witness presentation-dependent (the gate
reddens), and the decoded display is a proven lossy projection — two distinct
authority states collapse to one display, so there is no inverse back to
authority. The native layer-3 renderer stays outside the gate by its own law (§6).

**Act, addendum (cross-placement).** `fpview_c/frontfps_view.c` ADMITTED on the
sandbox gcc-11.4 host (`-Wall -Wextra` clean, first compile): stream golden
`bc60023…` bit-for-bit ×2, 332 bytes, decode 4 frames, 3 VIEW-REFUSE, and the
fold-defect digest `d5ea65e…` matches the reference AND diverges from the golden —
golden AND defect parity. `fpview_rs/` authored (std-only, own SHA-256),
SPECULATIVE until the owner's host prints ADMITTED ×2 with `--defect`.

## 2f. Stage 6 (LLM authoring surface) — SHIPPED. OODA-6 report

**Observe.** Stages 1–5 give a world identity, motion, poses, hitboxes, and a
display stream. What was missing is a surface a *model* can author against
directly. At Stage-6 entry the gate stood at 485 unit falsifiers / 356 rows.

**Orient.** The authority canon is already the right shape (plain dicts, a closed
name alphabet, total typed refusals). Stage 6 gives it a line-oriented ASCII form
(URDR-FPSW-TEXT-1) so a model emits/edits plain text, and makes the authoring
LOOP a gate property: emit → `admit_text` → on refusal feed the exact reason back
→ re-emit. It is a SURFACE, not a new identity — a parsed world's digest is
exactly the frontfps `world_digest`, provenance still excluded. The binding risk
is a parser that half-admits or crashes on hostile input; the answer is totality.

**Decide.** Four laws became the rows: round-trip (canonical, idempotent,
digest-preserving), identity (parsed == frontfps digest; a `prov` model tag never
moves it), **totality** (a seeded adversarial fuzz corpus — every input either
typed-admits or typed-refuses, never a bare Python exception, never a silent
half-admit), and repair (a refusal names its line; dropping it re-admits — the
loop provably closes). `auto_arena` joins the §4 auto family (mirror symmetry
certified; an asymmetric defect violates it). Deferred: `auto_rig`, and any claim
that a *particular* model emits valid worlds (a model property, not a gate one).

**Act.** Shipped: `frontfps_text.py` (URDR-FPSW-TEXT-1), `conformance_text.txt`
(2 digests), `tests/test_frontfps_text.py` (12 falsifiers), the `frontfps_text`
gate stage (7 rows), this report. Gate **497 unit falsifiers / 363 rows**, ×2
bit-identical. Fuzz: **74 admit / 183 refuse over 257 adversarial inputs**, all
typed — outcome digest pinned (`e57dfaea…`). Cross-placement SPECULATIVE, queued.
The model itself is not in the loop under test — the gate proves the surface it
would author against is total, typed, round-tripping, and repair-signalling.

## 3. The staged ladder (each stage ends in its OODA loop)

| Stage | Deliverable | Gate exit (Observe) | Pioneering pivot to weigh (Orient) | LLM / auto affordance (Decide ahead) |
|---|---|---|---|---|
| **1. World canon** — DONE | URDR-FPSW-1 + `auto_capsule` | `frontfps` rows green ×2 | — | refusal-guided repair loop (§7) |
| **2. Rotation substrate** — DONE (3 placements, 2 OSes) | Q32.32 quaternion ops + integer-Newton rsqrt on the frozen FIELDFP laws (`fpquat.py` + C99 + Rust placements) | `frontfps_quat` rows green ×2; C99 golden+defect parity; Rust ADMITTED on a named host | fixed-point **dual quaternions** (one type for rotation+translation) vs quat+vec — decide on op count under the 240 Hz budget, not elegance | held once in practice: the C placement was written from the docstring spec and matched on first compile — ports are cheap, trust stays in the gate |
| **3. Pose & clip canon** — DONE (reference) | URDRCLP1: keyframed rotation tracks on Q32.32 time, binary-search + `qnlerp` sampling, canonical minimum-priority state machine (`fpclip.py`) | `frontfps_clip` rows green ×2: goldens, rule-order invariance + authored-order defect, ambiguity/typo refusals, `auto_loopable` + w-only defect, pinned 55-op budget proxy | blend **graph** vs blend **tree** — decided by Stage-4 posed-corpus data; sub-tick sampling deferred to netcode M3 | `auto_loopable` shipped under the §4 law (witness + certificate + defect); `auto_blend` proposals queued for Stage 4 |
| **4. Posed hitboxes + IK seam** — posed core DONE (3 placements, 2 OSes); IK DECLARED | per-bone `auto_capsule` over posed skeletons; **one-tick-late IK contract** (reads T−1 contacts, writes T transforms, lag IS in the witness) | containment certificates over a posed corpus + floor defect; IK lag visible in `first_field_desync` fixtures | hitbox LOD (fewer capsules far away) — only if it never touches authority | artist-facing "why is my hitbox this size": the witness vertex, surfaced |
| **5. View stream** — DONE (reference, §2e) | URDR-FPSW-VIEW-2: binary, delta-framed successor of `to_view` for the native renderer (D15 successor version) | view recompute law; structural no-feedback test (renderer inputs can't reach canon); bandwidth measured per authored scene | share the compact-witness encoding with netcode replay (one format, two consumers) | `auto_lod` proposals for view meshes — presentation-only, so admissible on visual review, not witness proof |
| **6. LLM authoring surface** — DONE (reference, §2f) | line-oriented text form of the canon + the repair loop; `auto_arena` / `auto_rig` candidates under §4's law | an LLM-emitted world admitted with **zero human edits** on a pinned scenario set; adversarial fuzz: refusals stay total under random/hostile emissions | prompt→world as a *pipeline of admissions*, never one leap; each auto keeps its witness | this stage IS the affordance; its falsifier is the fuzz corpus |
| **7. Native scale-out** | SOA layout + bench protocol on a named host; streaming-editor integration | the §6 budgets become MEASURED-or-refuted on real silicon | volunteer-region hosting (directive §10) — only after D16 dynamic seams | auto-tuning loops audited like any self-improving system (Ursprung `m_novel` lesson) |

Stages 2–7 are `SPECULATIVE / N/A` until their rows exist. The ladder is re-ordered
only by an OODA report, never by enthusiasm.

## 4. The auto-affordance admission law (the "auto this, auto that" rule)

`auto_capsule` establishes the template every future `auto_*` must satisfy, and it
is deliberately the same shape as D17's detector law:

1. **deterministic derivation** — exact math, no RNG, no float, same input → same output;
2. **a witness** — the artifact names WHY (the extremal vertex), so the artist,
   developer, or LLM is shown the reason, not handed an assertion;
3. **a certificate** — a checkable law the output satisfies (`capsule_contains_all`);
4. **a shipped defect** — a near-miss variant that MUST violate the certificate, or
   the certificate is decoration.

An auto that cannot ship all four stays a proposal. This is what makes "streamlining
for developers and graphic artists" compatible with a witness chain: automation
*proposes*, the gate *disposes*, and nothing enters authority ungated — whether a
human clicked it, a script generated it, or a model dreamed it.

## 5. LLM compatibility posture

The surface is already the right shape: plain dicts, a line-oriented ASCII canon,
a closed name alphabet, and **total typed refusals whose reason strings are the
repair prompt**. An LLM authoring loop is: emit → `check_world` → on FPSW-REFUSE,
feed the exact reason back → re-emit. No heuristic linting layer, no "mostly valid";
the same admission a human authoring tool gets. Provenance carries the model tag
without ever entering identity, so an LLM-authored world is *distinguishable in
metadata and indistinguishable in authority* — exactly the D14 law extended to
machine authors. Stage 6 makes this a measured loop; until then it is a posture,
graded DECLARED.

## 6. Performance & visual targets (graded — read the grade column first)

Roadmap §4 is law here: real-time performance and GPU rendering are **not gate-able
in this repo**. The renderer that chases BF6-class fidelity is a **layer-3 native
consumer** of URDR-FPSW-VIEW-* downstream of D15 — it can never feed back into
authority, so visual ambition is *architecturally free* to compete: no shader,
material, or upscaler can desync the witness. That is the actual competitive story:
fidelity bounded by GPU engineering, integrity bounded by nothing the renderer does.

| Target | Value | Grade | Precondition |
|---|---|---|---|
| Authoring admission latency | interactive (<50 ms/world at editor scale) | NOT_MEASURED | Stage-7 bench protocol |
| Sim tick (authority, native placement) | ≤3 ms @ 240 Hz, 100→500 bodies | NOT_MEASURED | native placement + protocol |
| Render frame (native, 1080p) | 60 / 120–144 fps | NOT_MEASURED | layer-3 renderer exists |
| Render frame (native, 1440p) | 60 / 120 fps | NOT_MEASURED | layer-3 renderer exists |
| End-to-end input→photon | competitive-FPS class (<~25 ms @ 144 Hz) | NOT_MEASURED | all of the above |
| "BF6-competitive visuals" | subjective panel review | NOT_MEASURED (and never gate-provable) | sealed review protocol — a **neutral ruler**, per the Ursprung M3→M6b lesson: self-scored fidelity metrics get falsified later |

No number in this table may be quoted as a capability. The bench protocol (named
host, equal budget, sealed metric) must exist BEFORE optimization starts, or the
numbers will be born circular.

## 7. D5 ledger rows (recorded in `spec/D5-ledger.md`)

| Capability | Maturity | Evidence | Where falsified |
|---|---|---|---|
| URDR-FPSW-1 world canon: one identity law over meshes/rigs/hitboxes/actors/spawns/seams; provenance-excluded; order laws tested both sides; FPSW-REFUSE total; no digest for an inadmissible world | IMPLEMENTED | MEASURED | `frontfps` gate stage; `tests/test_frontfps.py` |
| `auto_capsule` — deterministic capsule derivation with witness + containment certificate; ceiling radius load-bearing | IMPLEMENTED | MEASURED | `frontfps-auto-capsule` row; floor-radius defect |
| frontfps (world canon) cross-placement | SPECULATIVE | N/A | none yet — the corpus is the target |
| `fpquat` Q32.32 rotation substrate: qmul/norm2/rsqrt/normalize/rotate/nlerp on frozen FIELDFP laws; rsqrt inequality law; FPQ-REFUSE total | IMPLEMENTED | MEASURED | `frontfps_quat` gate stage; `tests/test_fpquat.py` |
| `fpquat` C99 placement (own SHA-256, own i128 Bareiss-note-compliant arithmetic) — battery digest AND wrap64 defect digest agree with reference, twice | IMPLEMENTED | MEASURED (sandbox host, gcc 11.4) | `fpquat_c/fpquat.c` self-verify + `--defect` |
| `fpquat` Rust placement — ADMITTED ×2 + defect caught, golden `3f4aa0d1…` and defect `5c965ff8…` bit-for-bit | IMPLEMENTED | MEASURED (owner's Windows host, rustc -O, 2026-07-13) | `fpquat_rs/fpquat.rs` self-verify + `--defect` |
| `fpclip` pose & clip canon: URDRCLP1 sampling laws, canonical transitions, ambiguity/typo refusals, absolute tick time, 55-op pinned budget proxy | IMPLEMENTED | MEASURED | `frontfps_clip` gate stage; `tests/test_fpclip.py` |
| `auto_loopable` seam certificate (witness + w-only defect) | IMPLEMENTED | MEASURED | `fpclip-auto-loop` row |
| `fpclip` C99 placement — pose, trace, op count AND authored-order defect digest (`1e6b480c…`) agree with reference, twice | IMPLEMENTED | MEASURED (sandbox host, gcc 11.4) | `fpclip_c/fpclip.c` self-verify + `--defect` |
| `fpclip` Rust placement — ADMITTED ×2 + defect caught (pose/trace/defect digests bit-for-bit) | IMPLEMENTED | MEASURED (owner's Windows host, rustc -O, 2026-07-13) | `fpclip_rs/fpclip.rs` self-verify + `--defect` |
| `fppose` posed transforms + capsules: hierarchy composition (normalize-per-compose), exact point-in-capsule certificate, 77-op pinned proxy | IMPLEMENTED | MEASURED | `frontfps_pose` gate stage; `tests/test_fppose.py` |
| One-tick-late IK contract (reads T−1 contacts, writes T transforms, lag in witness) | SCOPED | DECLARED | fppose docstring; red-first fixture waits on physics wiring |
| `fppose` C99 placement — posed golden `fee3c118…` ×2, coverage walk+reach, swapped-compose defect `04f23abe…` + local-offset defect both bite, 77 ops, refusals total | IMPLEMENTED | MEASURED (sandbox host, gcc 11.4) | `fppose_c/fppose.c` self-verify + `--defect` |
| `fppose` Rust placement — ADMITTED ×2 + defect caught, golden `fee3c118…` and defect `04f23abe…` bit-for-bit | IMPLEMENTED | MEASURED (owner's Windows host, rustc -O, 2026-07-13) | `fppose_rs/fppose.rs` self-verify + `--defect` |
| `frontfps_view` view stream: URDR-FPSW-VIEW-2 delta framing; recompute law; no-feedback (witness ⟂ presentation, fold defect, lossy display); VIEW-REFUSE canaries; pinned per-scene byte count | IMPLEMENTED | MEASURED | `frontfps_view` gate stage; `tests/test_frontfps_view.py` |
| `frontfps_view` C99 placement — stream golden `bc60023…` ×2, 332 bytes, decode 4 frames, 3 VIEW-REFUSE, fold-defect `d5ea65e…` parity | IMPLEMENTED | MEASURED (sandbox host, gcc 11.4) | `fpview_c/frontfps_view.c` self-verify + `--defect` |
| `frontfps_view` Rust placement — ADMITTED ×2 + fold-defect caught | IMPLEMENTED | SPECULATIVE (owner's Windows host, pending run) | `fpview_rs/frontfps_view.rs` self-verify + `--defect` |
| `frontfps_text` LLM authoring surface: URDR-FPSW-TEXT-1 line canon; round-trip + identity; adversarial fuzz totality; repair-signal loop; `auto_arena` (§4 law) | IMPLEMENTED | MEASURED | `frontfps_text` gate stage; `tests/test_frontfps_text.py` |
| `frontfps_text` cross-placement (C99/Rust) | SPECULATIVE | N/A | queued |
| Stage 7 (native bench) | SPECULATIVE | N/A | this README §3 |

## 8. Run it

```
PYTHONHASHSEED=0 python tools/frontfps/frontfps.py     # prints the two corpus digests
PYTHONHASHSEED=0 python tools/frontfps/fpquat.py       # battery digest + defect checks
PYTHONHASHSEED=0 python tools/frontfps/fpclip.py       # pose/trace digests + op count
PYTHONHASHSEED=0 python tools/frontfps/fppose.py       # posed digest + coverage + defects
PYTHONHASHSEED=0 python verify.py                      # the gate (frontfps + fpquat rows)

# C99 placements (any gcc host):
cc -O2 -std=c99 tools/frontfps/fpquat_c/fpquat.c -o fpquat && ./fpquat && ./fpquat --defect
cc -O2 -std=c99 tools/frontfps/fpclip_c/fpclip.c -o fpclip && ./fpclip && ./fpclip --defect

# Rust placements (Windows/rustc, the named-host runs that flip their grades):
rustc -O tools\frontfps\fpquat_rs\fpquat.rs -o fpquat_rs.exe   # ADMITTED 2026-07-13
rustc -O tools\frontfps\fpclip_rs\fpclip.rs -o fpclip_rs.exe
.\fpclip_rs.exe            # expect: URDR-FPCLIP-RS: ADMITTED (…)  — run TWICE
.\fpclip_rs.exe --defect   # expect: DEFECT CAUGHT
```

Falsifier for this whole document: any claim above whose named gate row does not
exist or is not green. File it.
