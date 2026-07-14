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

## 3. The staged ladder (each stage ends in its OODA loop)

| Stage | Deliverable | Gate exit (Observe) | Pioneering pivot to weigh (Orient) | LLM / auto affordance (Decide ahead) |
|---|---|---|---|---|
| **1. World canon** — DONE | URDR-FPSW-1 + `auto_capsule` | `frontfps` rows green ×2 | — | refusal-guided repair loop (§7) |
| **2. Rotation substrate** | Q32.32 quaternion ops + Newton–Raphson rsqrt as a **versioned D9 extension** (D12 successor, never a mutation) | op corpus + property falsifiers (unit norm bound, composition assoc. within rounding, rsqrt error bound vs exact ℚ) ×2; cross-placed before Stage 3 opens | fixed-point **dual quaternions** (one type for rotation+translation) vs quat+vec — decide on op count under the 240 Hz budget, not elegance | the op spec is machine-checkable: an LLM-written placement is admitted by digest agreement alone — ports become cheap, trust stays in the gate |
| **3. Pose & clip canon** | URDR-CLIP-1: keyframes on Q32.32 time, deterministic sampling, state machine with sorted transition priorities | clip playback digests ×2; permuted-authoring invariance; ambiguous-transition refusal; defect: unsorted priorities diverge | blend **graph** vs blend **tree**; sub-tick sampling now or at netcode M3 | `auto_blend` candidates: propose transitions, admit only those passing the same determinism rows — auto proposes, the gate disposes |
| **4. Posed hitboxes + IK seam** | per-bone `auto_capsule` over posed skeletons; **one-tick-late IK contract** (reads T−1 contacts, writes T transforms, lag IS in the witness) | containment certificates over a posed corpus + floor defect; IK lag visible in `first_field_desync` fixtures | hitbox LOD (fewer capsules far away) — only if it never touches authority | artist-facing "why is my hitbox this size": the witness vertex, surfaced |
| **5. View stream** | URDR-FPSW-VIEW-2: binary, delta-framed successor of `to_view` for the native renderer (D15 successor version) | view recompute law; structural no-feedback test (renderer inputs can't reach canon); bandwidth measured per authored scene | share the compact-witness encoding with netcode replay (one format, two consumers) | `auto_lod` proposals for view meshes — presentation-only, so admissible on visual review, not witness proof |
| **6. LLM authoring surface** | line-oriented text form of the canon + the repair loop; `auto_arena` / `auto_rig` candidates under §4's law | an LLM-emitted world admitted with **zero human edits** on a pinned scenario set; adversarial fuzz: refusals stay total under random/hostile emissions | prompt→world as a *pipeline of admissions*, never one leap; each auto keeps its witness | this stage IS the affordance; its falsifier is the fuzz corpus |
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

## 7. Proposed D5 ledger rows (pending Architecture-Office sign-off)

| Capability | Maturity | Evidence | Where falsified |
|---|---|---|---|
| URDR-FPSW-1 world canon: one identity law over meshes/rigs/hitboxes/actors/spawns/seams; provenance-excluded; order laws tested both sides; FPSW-REFUSE total; no digest for an inadmissible world | IMPLEMENTED | MEASURED | `frontfps` gate stage; `tests/test_frontfps.py` |
| `auto_capsule` — deterministic capsule derivation with witness + containment certificate; ceiling radius load-bearing | IMPLEMENTED | MEASURED | `frontfps-auto-capsule` row; floor-radius defect |
| frontfps cross-placement (any second implementation) | SPECULATIVE | N/A | none yet — the corpus is the target |
| Stages 2–7 (rotation, clips, posed hitboxes, view stream, LLM loop, native bench) | SPECULATIVE | N/A | this README §3 |

## 8. Run it

```
PYTHONHASHSEED=0 python tools/frontfps/frontfps.py     # prints the two corpus digests
PYTHONHASHSEED=0 python verify.py                      # the gate (frontfps rows inside)
```

Falsifier for this whole document: any claim above whose named gate row does not
exist or is not green. File it.
