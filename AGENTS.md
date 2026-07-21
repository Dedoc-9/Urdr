<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# AGENTS.md — how to work in this repository

> **Nihil ultrā probātum — nothing beyond what is proven.**
> A program that claims more than it verifies does not typecheck; a *contributor*
> that claims more than the gate proves does not get merged.

This file is the operating contract for any agent (human or AI) making changes to
Urðr. Read it before touching code. The normative documents are in
[`spec/`](spec/) — this file tells you the *discipline*; the specs tell you the
*rules*. If this file and a spec disagree, the spec wins; if a doc and the gate
disagree, the gate wins.

---

## 1. What this repository is

Urðr is two things at once:

1. **A small sealed language** (`urdr/`) — glyphic, membrane-native,
   epistemically-typed, deterministic. Identity is a content digest; a value's
   epistemic maturity can only rise through an explicit verification; nothing is
   ambient. Spec: [`spec/D1-spec.md`](spec/D1-spec.md).
2. **A deterministic, certified execution pipeline** built on that kernel — exact
   math, physics (dynamics, contacts, joints), a fixed-point renderer, and a
   reactive scalar-field layer — in which **every admitted output is either
   bit-identical across independent implementations or explicitly refused.**
   Overview: [`docs/PAPER.md`](docs/PAPER.md); contracts:
   [`spec/D11-layer-contracts.md`](spec/D11-layer-contracts.md).

The reproducibility spine is the whole point. Do not add anything that can make an
admitted result non-reproducible.

---

## 2. The stack (layers)

Each layer depends only on the layer beneath it and may assume only that layer's
*written* contract (D11). Narrow responsibilities, testable interfaces.

```
   applications            (games, sims, tools) — consumers
        │
   urdr-netcode            N1–N5 + N4.1: lockstep · rollback · authenticated inputs · authored worlds · body-body contact · authenticated rollback over worlds; D16 regional authority (partition→one witness)  [tools/netcode/]
        │
   urdr-world              multi-actor deterministic world (weave, history)
        │
   urdr-field              reactive scalar transport (advection-diffusion)   [tools/physics/field.py]
        │
   urdr-render             deterministic fixed-point rasterizer + 3D depth    [tools/render/]
        │
   urdr-physics            exact dynamics + n-contact LCP + articulated joints [tools/physics/]
                           + BOUNDED fixed-point dynamics (the real-time path)  [tools/physics/fp_dynamics.py]
        │
   urdr-rigidity           exact structural certificates (Connelly)           [tools/intla/, tools/physics/]
        │
   urdr-math               exact integer linear algebra (Bareiss, i64-refusal) [tools/intla/]
        │
   urdr-core               the sealed language: digest identity, refusals      [urdr/]
        │
   capabilities (R4)       recorded inputs / effect-plans at the līmes         [urdr/capability.py]
        │
   operating system
```

Reference implementation is **Python** (chosen for auditability, not speed).
Independent second placements are **single-file, `std`-only Rust** with hand-rolled
SHA-256 (no crates, no cargo): `tools/urdr_core_rs/`, `tools/render/urdr_render_rs/`,
`tools/physics/urdr_physics_rs/`, `tools/intla/urdr_math_rs/` (the exact-integer
linear-algebra spine + atlas certificates), `tools/physics/fp_dynamics_rs/` (the
bounded fixed-point steppers — rung 5), and the netcode placements
`tools/netcode/{lockstep,rollback,authinput,worldstep,worldpeer}_rs/` (rungs N1–N5),
`tools/netcode/worldregion_{rs,c}/` (D16 regional authority + N4.1 contact), and the two
invariant detectors `tools/intla/{toric,rigidity}_{rs,c}/` (the toric-code dimension and
the rigidity verdict) — each ADMITTED on Windows/`rustc`, MEASURED both placements, with
its port logic first validated by an independent C99 cross-check that agrees on the golden
AND the defect digests. Counting the math spine's `tools/intla/urdr_math_c/` (std-only,
`__int128`), that is **32 Rust placements and 14 C99 runtimes** — three
languages, two OSes, one digest.

---

## 3. The language (in one page)

- **Alphabet.** A small closed set of glyphs curated from historical sign systems,
  *every glyph with an ASCII digraph* so programs are 100% typeable offline
  (`spec/D1-spec.md`, `spec/D4-typeability.md`). Confusables are refused
  (`URDR-LEX-CONFUSABLE`).
- **Identity is content.** `digest = SHA-256(canon(value))` (D1 §7). Same value →
  same bytes → same digest. This is the authority everywhere.
- **Epistemic types.** `𒀭⟨maturity, evidence⟩ v` checked statically. Evidence may
  never exceed what maturity licenses (`URDR-INFLATE-STATIC`); writing `MEASURED`
  in source is refused (`URDR-EVIDENCE-UNEARNED`) — `MEASURED`/`Grounded` is
  minted **only** by the verify primitive `ᛞ` (Milner's `thm` discipline, applied
  to evidence).
- **Membrane.** An immutable content-addressed store `ᚠ`; view `☽` (pure), edit
  `☿` (new store, new digest), anamnesis `↩` (return to the exact prior state).
- **Refusals are typed stops.** 18 kernel codes (`urdr/errors.py`) plus layer
  codes `PHYS-REFUSE`, `RENDER-REFUSE`, `FIELD-REFUSE`. A refusal is total: no
  partial write, no wrapped integer, no saturated pixel, no guessed answer.

---

## 4. The Ursprung discipline (the rules you must follow)

These are non-negotiable. Every rung in this repo was built under them.

1. **Honest grading (no inflation).** Every capability claim carries two grades:
   **maturity** (`IMPLEMENTED` / `SCOPED` / `SPECULATIVE`) and **evidence**
   (`MEASURED` / `DECLARED` / `N/A`), and evidence never exceeds maturity. The
   graded inventory is [`spec/D5-ledger.md`](spec/D5-ledger.md) (Volume I, sealed at the
   placement-batch closure) continued in [`spec/D5-ledger-2.md`](spec/D5-ledger-2.md)
   (the live volume — new entries append there; a capability's current grade is its
   latest entry across the volumes). Never write a
   grade the gate does not support. `admitted ≠ trusted` — a green gate certifies
   *these tests on this code*, never that a name means what it says.

2. **Red-first + non-vacuity.** Write the falsifier *before* the feature. Every
   gate stage must be able to go **red** — include a deliberate defect self-test
   that *must* be caught. A gate that cannot redden proves nothing (LESSONS L5).

3. **Determinism is the invariant.** No floating point, no clock, no RNG, no
   iteration-order or hash/pointer dependence in the authority path. Run the gate
   with `PYTHONHASHSEED=0`. If a computation cannot be made deterministic, it does
   not belong on the authority path.

4. **Exact where affordable; deterministic-bounded where not; refuse otherwise.**
   Prefer exact integer/rational arithmetic. Where exactness is unaffordable or
   impossible (iterated fields overflow; `sin/cos`, curvature, and continuous
   curved collision are irrational), use the **Q32.32 fixed-point** substrate —
   which is *deterministic and reproducible but rounds* — and say so. The worked
   example is **rung 5, bounded fixed-point dynamics** (`tools/physics/fp_dynamics.py`):
   where the exact ℚ rungs refuse on long sims, it time-steps a settling stack and a
   swinging pendulum for as long as you like (uniqueness-by-certificate → reproducibility-
   by-frozen-rounding). **Surface the boundary; never silently approximate.** i64
   overflow is a **refusal**, not a wrap. (Bignum only if a real consumer actually hits
   the ceiling — not speculatively.)

5. **The admission ladder.** Every capability goes:
   `prototype → reference proof → conformance corpus → independent second
   placement → admission → freeze`. Do not skip rungs. Do not claim
   cross-placement (`MEASURED`) until an independent Rust placement reproduces the
   digests **twice, bit-for-bit, with the defect caught** on a named host.

6. **The kernel is frozen.** The sealed language does not change except for
   bug-fixes. **No new glyph without a D1 §20 review** — and none has been needed.
   New capability lives in `tools/` and consumes the kernel; it never edits it.

7. **Freeze before you extend.** Once a subsystem is cross-placed, freeze it in
   [`spec/D12-versions.md`](spec/D12-versions.md): serialization grammar, arithmetic
   parameters, refusal semantics, witnesses, public API, and corpus become
   immutable except through a versioned successor. Future work *extends*, never
   *mutates* an admitted digest. Frozen so far: `urdr-core 1.0`, `urdr-physics 1.0`,
   `urdr-field 0.1`; `urdr-render 1.0`.

8. **The gate is CI.** `PYTHONHASHSEED=0 python3 verify.py` must print
   `GATE PASSED` after every change. It runs unit falsifiers, example
   determinism+goldens, the in-process oracle (`compiled ≡ reference` + a defect
   that must diverge), per-layer conformance stages (each with a non-vacuity
   self-test), the rejection fixtures (each an exact typed refusal code), and a
   final tamper self-test.

9. **Module basenames are globally unique across `tools/`.** The gate assembles
   ONE `sys.path` across every tool dir, so two files named `scenes.py` in
   different tools collide via `sys.modules`. (This actually bit us —
   `render/scenes.py` vs `physics/scenes.py`.) Name modules uniquely
   (`phys_scenes`, `nd_scenes`, `lcp_scenes`, `joint_scenes`, `scenes3d`,
   `field_scenes`, …).

10. **Docs must match reality — and the gate enforces it (`doc-currency`).** Five
    live counts are checked MECHANICALLY against the seven tracked docs —
    `README.md`, `AGENTS.md`, `docs/PAPER.md`, `docs/THEOREMS.md`, `docs/README.md`,
    `tools/README.md`, `tests/README.md` — on every run; a doc quoting a stale number
    reddens `doc-currency`. Each count has ONE source of truth, never a re-count:
    **unit falsifiers** = the gate's own `testsRun` (add a `tests/test_*.py` method and
    it rises); **gate rows** = the live row total (add a `self.record(...)` and it
    rises); **Rust / C99 placements** = the count of `*_rs` / `*_c` directories under
    `tools/` (the filesystem itself); **detectors** = the length of `verify.py`'s
    `invariant_detectors` manifest (admit a D17 detector and it rises). The idioms are
    DIGIT-form only: `<n> unit falsifiers`, `<n>-test gate`, `<n> unit falsifiers / <m>
    rows`, `<n> … Rust`, `<n> C99`, `<n> detectors` / `<n>-detector`. Markdown emphasis
    is stripped first, so a bolded count cannot hide. THE GOTCHA, learned the hard way:
    a count written in WORDS (a spelled-out detector or placement count) is INVISIBLE to
    the checker and silently rots — it has happened twice. Write every count you want
    protected in DIGITS. Workflow when you add tests, rows, placements, or a detector:
    run the gate, read the `doc-currency` refusal (it NAMES each stale doc and count),
    and fix EVERY tracked doc; the non-vacuity selftest proves the checker catches a
    planted stale count, so a green `doc-currency` means the docs are current, not that
    the check was skipped. Deliberately NOT tracked (they carry historical or
    forward-looking numbers the idiom would wrongly read as live counts): `spec/D5` (the
    graded ledger, BOTH volumes — it records `x → y` count steps) and `spec/D17` (it names a future
    catalog size). `spec/D11` is the layer contracts, `spec/D12` the versions/freeze. A
    doc that overstates is a bug — the gate now files it for you.

11. **The completion rule.** No capability is COMPLETE until its transcript is
    frozen, its refusals are specified, its corpus exists, and an independent
    implementation reproduces it. Passing tests is a milestone, not completion;
    every subsystem eventually earns the same status as the kernel — not just
    "works", but "can be independently reproduced and mechanically checked."
    Until then its grade says exactly where it stands on the ladder, and no doc
    calls it done.

---

## 5. How to add a rung (concrete workflow)

1. **Prototype** the exact/deterministic math in a scratch script; confirm the
   core properties and any invariants (conservation, complementarity, boundedness,
   determinism) *and* a non-vacuity control (a defect that breaks them).
2. **Write the reference module** in the appropriate `tools/<layer>/`. No float,
   no ambient I/O; overflow refuses.
3. **Pin a conformance corpus** (`conformance*.txt`) — canonical scenes → digests.
4. **Write red-first falsifiers** in `tests/test_*.py` (unique basename) — assert
   the invariants and that the wrong outcome would have passed.
5. **Add a gate stage** in `verify.py` (determinism ×2 + golden match + a
   `*-selftest` non-vacuity control) and wire it into `main()`.
6. **Grade honestly** in `spec/D5-ledger.md`; update `spec/D11` (contract) and
   `spec/D12` (version) as needed.
7. **Cross-place**: extend/author a `std`-only Rust file to reproduce the digests;
   cross-check the port logic (mirror it) before compiling. It is `SPECULATIVE`
   until a host recompiles and prints `ADMITTED` twice + defect caught; then flip
   to `MEASURED` on that named host.
8. **Gate green → commit → push.** Keep commits scoped; the commit message states
   what is MEASURED vs DECLARED and the scope caveat.

---

## 6. Repository map

| Path | What it is |
|---|---|
| `urdr/` | the sealed language: lexer, evaluator, canon/digest, capabilities, errors |
| `verify.py` | **the gate** (CI) — run `PYTHONHASHSEED=0 python3 verify.py` |
| `examples/` | `.urdr` programs (42) with `.digest` goldens; `examples/rejected/` (45 typed-refusal fixtures) |
| `tests/` | Python falsifiers discovered by the gate's unit stage |
| `tools/intla/` | `urdr-math` (exact integer linear algebra), `urdr-rigidity`, and the D17 invariant-detector library (`gf2` exact 𝔽₂ substrate, `toric` code dimension, `persim` persistence barcode, `winding` winding number — the W1 rung of D19, `tellegen` Tellegen orthogonality, `atlas_reconstruct` exact observer-atlas reconstruction — the information-security detector) |
| `tools/physics/` | exact dynamics, LCP, joints, `field.py`; the `Q`/`Vec` exact substrate; **`fp_dynamics.py`** bounded fixed-point steppers (rung 5) |
| `tools/render/` | fixed-point rasterizer (`raster.py`) + 3D depth (`raster3d.py`) |
| `tools/terrain/` | `urdr-terrain` T1: the `URDRHF1` deterministic heightfield canon (SHA-seeded lattice noise, Q16 quintic FBM, sqrt-free island falloff; same seed → same bytes on any host) — the D14 procedural modality — plus **T2**: `terrain_bridge.py`, the heightfield → `URDROBJ2` wireframe bridge (own canon ≡ `canon_ref`, provenance-inert); ladder + the idle law in `docs/terrain_studio_brief.md`; **S1**: `sea.py` — the island's sea as certified field state (bathymetry adapter + masked flux-form transport on the frozen urdr-field substrate; the coastline is boundary); **S2**: the masked Marangoni step — surface tension on the wide-sea scene (scene level 130 by rule, κ audited monotone tick-by-tick); **T3.0**: `terrain_view.py` — the view-export FIREWALL (D15 applied to terrain: the view carries the witness, presentation moves the view digest never the witness; the measurable half of the presentation layer) + `terrain_view.html`, the on-demand renderer (idle law: zero frames while idle). Doctrine: `docs/presentation_doctrine.md`; **T3.3 authority**: `wavefield.py` — the EXACT integer traveling-wave field (periodic parabolic profile, P²|8A, floor-mod phase, superposition; same components+tick → same bytes, no rounding) the GPU's declared Gerstner sinusoid draws from — DIVISION-FREE (no `/`/`//`/`%` operator, tokenizer-asserted: structural cross-placement parity); **T3.2/T3.3 view** `terrain_view3d.html` — a dependency-free WebGL2 3D render of the certified island + a float Gerstner water surface (analytic normals) from the SAME wave params (DECLARED presentation, off-gate, idle law); **T3.5 consumer**: `buoyancy.py` — MEASURED wave-field buoyancy (a raft's exact integer waterline `z*` on the field by division-free bisection satisfying the Archimedes bracket; the flotation law is a declared model, `z*` is measured); **T3.6**: `view_witness.py` — the citation contract (the declared view's embedded `hf_witness`/`wave_witness` must equal the live authority recomputed from the modules; knobs walled from the witness; a one-hex forgery reddens — the render stays declared, only the citation is measured); **T3.7 consumer**: `crossing.py` — MEASURED wave-crossing timing (a moving agent's exact first-overtopping tick through the traveling field; both agent and wave move, so travel is load-bearing). The arc then CONTINUES through the MMO stages: movement + observers (`stance`/`gaze`/`drive`/`traj`, `fpface`/`fpcap`), the continuous fold and its reconciles (`glide`/`splice`/`predict`/`cpredict`, Stages A–B), scale/handoff/anti-cheat (`interest`/`layertheorem`/`hand`/`warden`/`crosswarden`/`dirward`/`wardhom`, Stages C–E), the Stage-H latency guarantee on both axes (`opcost`/`govern`/`priogov`/`horizon`/`slo`/`clslo` for time, `storecost` for space), durability + recovery (`persist`/`resurrect`), and the Stage-I streaming openers (`chunkload`/`chunkstate`) — the module-by-module index is [`tools/terrain/README.md`](tools/terrain/README.md) |
| `tools/*/*_rs/` | independent `std`-only Rust placements (kernel, render, physics, math, fixed-point dynamics, the N1–N5 netcode stack, D16 regional authority, the seven-stage frontfps ladder, the URDRPD1 persistent-homology / OOB witness, the toric/rigidity detectors, and the five terrain-arc placements — `heightfield_rs`, `latstore_rs`, `glide_rs`, `streamstate_rs`, `latarith_rs` — each re-verified LIVE by the gate's placement stages wherever `rustc` exists, SKIPPED honestly where it does not) |
| `tools/netcode/` | The N1–N5 stack: **`lockstep.py`** (peers exchange inputs only, one `URDRLST1` witness chain, desyncs localized), **`rollback.py`** (canonical snapshots; late inputs rewind + replay and converge to the N1 chain; `ROLLBACK-REFUSE`/`ROLLBACK-CONFLICT`), **`authinput.py`** (Lamport-OTS envelopes gate admission; `AUTH-REFUSE`), **`worldstep.py`** (authored `URDR-WORLD-3` scenes in the loop; `WORLD-REFUSE`; **N4.1** opt-in sqrt-free body-body contact), **`worldpeer.py`** (N5 — the composed contract: authored world + authenticated transcript → one witness or one typed refusal; `URDRWPN1` world pin), and **`worldregion.py`** (**D16** regional authority: partition by integer x-seams → deterministic reunification reproduces the monolith witness, `REGION-REFUSE`); six corpora + Rust placements `{lockstep,rollback,authinput,worldstep,worldpeer}_rs` + `worldregion_{rs,c}`; all frozen at 0.1 in D12 |
| `tools/editor/` | browser authoring + deterministic-replay front-end (`urdr_designer.html`, `replay.py`, `load_world.py`) — **exploratory** consumer; the `--fp` stepping it demos is the gated rung 5 |
| `tools/frontfps/` | **`frontfps.py`** — the consolidated FPS/MMO authoring canon (**URDR-FPSW-1**, Stage 1): meshes + rigs + capsule hitboxes + actors + spawns + D16 seams under ONE world-identity law (provenance excluded, `FPSW-REFUSE` total, no digest for an inadmissible world), plus the first auto-affordance (`auto_capsule`, containment-certified, defect-checked) and **`fpquat.py`** — the Stage-2 Q32.32 rotation substrate (URDRFPQ1: qmul/norm2/rsqrt/normalize/rotate/nlerp on the frozen FIELDFP laws; C99 placement `fpquat_c/` golden+defect parity; Rust `fpquat_rs/` ADMITTED on the owner's Windows host — three placements, two OSes) and **`fpclip.py`** — the Stage-3 pose & clip canon (URDRCLP1: keyframed Q32.32 rotation tracks, canonical minimum-priority state machine, `auto_loopable` seam certificate, pinned 55-op pose budget proxy; bench protocol in `docs/bench_protocol.md`) and **`fppose.py`** — Stage-4 posed world transforms + hitbox capsules (URDRPSE1: normalize-per-compose hierarchy, exact point-in-capsule coverage certificate, one-tick-late IK contract DECLARED). Staged FPS/MMO plan + OODA reports in its README |
| `tools/world_host/` | multi-actor deterministic world (weave, history) — the layer beneath the netcode stack |
| `tools/specfreeze/` | the D12 freeze manifest checker + `doc_currency.py` (the stale-count detector the gate runs on every pass) |
| `spec/` | the normative documents: D1 (language), D5 volumes (the graded ledger), D11 (layer contracts), D12 (versions/freeze), D16/D17/D19 (regional authority, detectors, winding) — plus `spec/attest/` (the pinned reality-attestation traces, each a named-host log re-verified by the gate forever) |
| `docs/` | the papers and briefs: `PAPER.md` (systems overview), `THEOREMS.md` (what is proved), `wire_phase_brief.md` (the sealed wire phase's map), `terrain_studio_brief.md` (the arc's realized ladder), `bench_protocol.md` (the named-host performance law), `presentation_doctrine.md` (the D15 firewall) |

---

## 7. Hainuwele — the manifold MMO project (the catch-up)

The long arc that grew on top of the frozen kernel — terrain, movement, observers,
anti-cheat, latency, durability, streaming, the mutable world, the write calculus, and the
wire — carries the name **Hainuwele**, after the Wemale dema-deity of Seram (Maluku): the
coconut-girl who gave uncannily (each gift more precious than custom allowed), was killed
for it and buried, and from whose interred, divided body grew the tuber crops that fed the
people ever after (A. E. Jensen's *dema* reading: the death that generates sustenance and
order). The fit is exact and intentional: in this repository EVERY living capability grows
from something buried — a content-addressed record interred under its own digest, immutable,
divided by region, from which the world is re-derived rather than trusted. The membrane's
`ᚠ` store is the burial ground; the manifests are the graves' registry; `anamnesis` is the
exhumation that returns the exact prior body; and what grows from the pieces is *exactly
determined* — same seed, same crop, on any host, or a typed refusal. Nothing living is ever
edited; the world is fed by its dead.

**Where the arc stands (catch-up in one paragraph).** T1–T3.8 grew the certified island —
heightfield canon, sea, waves, buoyancy, the D15 view firewall. Stages A–E grew movement and
its police — the fold (`glide`), observers, interest, handoff, wardens (topology-grade
anti-cheat). Stage H bounded time and space — op-cost envelopes, governors, per-class SLOs,
priced snapshots. Stage H/I made it durable and streaming — `persist`/`resurrect`
(through-death recovery), `chunkload`/`chunkstate` (equal-or-refuse streaming, the regional
cut). Then the WRITE CALCULUS (sealed in the D5 ledger): `terraform` (the CAS edit record),
`commute` (the commutation certificate), `rannull` (RAN-0 authority nullity — proof of
absence), `lease` (proof as an interval), `testament` (the write that survives its writer),
`rollstore` (the durable rollback window), `quintessence` (the ID-0 representation theorem —
five axes of evidence characterize every lawful authority). And on top of the sealed
calculus, THE WIRE PHASE, all five rungs landed and the phase SEALED: `wire` (the update IS
the record; the client is a verifier), `storm` (the deterministic adversarial-transport
loom), `sealwrit` (the Lamport-signed writ; eligibility precedes admission), `driftgaze`
(the moving client; the gap repair), `wireattest` (real UDP processes on the named host,
recorded once, re-verified forever). Read the ledger entries newest-last in
`spec/D5-ledger-2.md` — they are the authoritative narrative; the per-module index is
`tools/terrain/README.md`.

---

## 8. The shell, exactly (how to run everything)

The gate is the only ritual. Both hosts matter: the named Windows host (Ally X) and any
Linux/cloud host. All commands run from the REPO ROOT — half of historical "Ran 1 test"
confusions were a drifted working directory.

```bash
# THE GATE (CI). Expect "GATE PASSED", 1116 unit falsifiers / 640 rows, and run it
# TWICE — the two outputs must be BYTE-IDENTICAL (determinism is a row, not a hope):
PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py > gate1.txt 2>&1
PYTHONHASHSEED=0 PYTHONUTF8=1 python verify.py > gate2.txt 2>&1
cmp gate1.txt gate2.txt && echo "GATE x2 BYTE-IDENTICAL"

# One unit suite, exactly as the gate discovers it (repo root, same env):
PYTHONHASHSEED=0 PYTHONUTF8=1 python -m unittest tests.test_storm -v

# The reality attestation (OFF-GATE by law — real UDP subprocesses on loopback;
# run it on the NAMED host; it rewrites spec/attest/wire_attest.txt, which the
# gate then re-verifies deterministically forever):
PYTHONHASHSEED=0 PYTHONUTF8=1 python tools/terrain/wireattest.py --run spec/attest/wire_attest.txt "Ally X"

# A placement by hand (the gate does this LIVE per run wherever rustc exists;
# missing rustc records SKIPPED rows honestly — row counts stay host-stable):
rustc -O tools/terrain/heightfield_rs/heightfield.rs -o /tmp/hf && /tmp/hf
```

PowerShell equivalents (the named host): `$env:PYTHONHASHSEED="0"; $env:PYTHONUTF8="1"`
then the same `python verify.py`; compare with
`(Get-FileHash gate1.txt).Hash -eq (Get-FileHash gate2.txt).Hash`.

Environment laws, non-negotiable: `PYTHONHASHSEED=0` (hash-order determinism) and
`PYTHONUTF8=1` (Windows console re-encoding must not corrupt the glyphs). Write every
tracked text file with LF endings (`newline="\n"`) — a CRLF rewrite moves byte counts and
digests. Never trust a stale `__pycache__` when bisecting oddities: delete it and re-run.
When counts move (tests, rows, placements, detectors), run the gate and let the
`doc-currency` refusal NAME each stale doc, then fix all seven tracked docs in the same
commit (see rule 10 above).

---

## 9. Lessons so far (the ones that drew blood)

The full law list is `LESSONS.md`; these are the ones this arc re-learned by being bitten,
written here so the next contributor starts where we ended rather than where we began.

1. **L5 — validity, not outcome.** A test that cannot fail proves nothing. Write the
   falsifier FIRST, watch it fail, then build. Every suite in `tests/` was born red.
2. **L15 — a plant must BITE, and masking is the default, not the exception.** Before any
   golden is pinned, inject each planted defect and PROVE the falsifier reddens. The arc's
   recurring find: defense-in-depth MASKS plants — the storm's vacuous-schedule plant passed
   on secondary chaos until the `primary_reorderings` floor was invented; the wireattest
   forged-admission fixture was absorbed by the at-most-once layer until retargeted at a
   reorder-early refusal; its wrong-address-fetch forge was absorbed by the witness backstop
   until rebuilt with a CONSISTENT witness. When a plant fails to bite, the fixture is wrong
   or the layer is redundant — find out WHICH: prove layers individually redundant and
   jointly load-bearing (the `rannull` two-layer discipline), and aim each forge at the one
   lie only its target law can catch.
3. **Goldens pin AFTER the bites.** A golden pinned before its falsifiers were proven to
   bite is void — re-derive it. No exceptions, including doc-only convenience.
4. **The gate must redden per-row.** A stage whose rows cannot each be independently
   reddened is decorative: `driftgaze`'s repair row silently excused the lazy-refresh defect
   until the row exercised BOTH repair paths. Prove each row's tooth the way you prove a
   plant's.
5. **Measure, don't remember.** A "the row reddened" observation from a stale run is worth
   nothing — one of this arc's non-vacuity claims turned out to be a pycache artifact.
   Re-run in a clean process before recording any red/green claim anywhere.
6. **Ordering claims need ordering proofs.** "Eligibility precedes admission" is narrative
   until the BOTH-BAD probe exists: an input failing two laws at once must refuse with the
   FIRST law's type, and the swapped-order plant must flip it (the `sealwrit` proof).
7. **Refusals are typed or they are nothing.** Every refusal path gets a code
   (`*-REFUSE`), a message that teaches, and a purity guarantee (the replica/ledger/store
   byte-identical after). The attestation checker refuses UNTYPED outcomes on sight.
8. **Determinism leaks in through the seams**: dict/hash order (PYTHONHASHSEED), console
   encodings, CRLF rewrites, wall-clock, `platform` strings inside gated bytes. Anything
   nondeterministic lives OFF-GATE and crosses back as a pinned, self-digested record
   (the `wireattest` split — the pattern for every future reality boundary).
9. **The covenant on debts.** Recorded ambitions become scheduled rungs or are honestly
   re-declared; a phase's placement batch falls due when the phase seals, NO LATER.
   Placement batch #3 (the wire phase's five families) LANDED as `wirephase_rs` — debt paid; V1 is open.
10. **Docs move in the same commit as the counts** — the `doc-currency` stage makes stale
    docs a RED GATE, and counts written in words instead of digits silently rot (it
    happened twice; see rule 10).

---

## 10. The road ahead (researched, declared — not begun)

Two candidate layers were scouted against the 2026 state of the art (web-researched at
writing time; conclusions recorded, laws to be falsified locally when the rungs open).
Neither opens before placement batch #3 closes — the covenant's boundary holds.

**`ghostsnap` — the actor wire (equal-or-refuse ghosts).** The industry's pattern (Unity's
Netcode-for-Entities "ghost snapshots") replicates server-authoritative entities to clients
as per-tick snapshots with interpolation and prediction timelines, importance-ranked partial
snapshots under MTU, delta compression — and the client TRUSTS every byte. Hainuwele's
counterpart extends the sealed write calculus from terrain to DYNAMIC state: a ghost is a
replica ACTOR admitted from content-addressed per-tick records (the `latstore` 25-byte pose
law + `chunkstate`'s regional cut) chained by parent digest — `wire`'s admission law on the
movement plane, `warden` regions as the interest filter, the storm re-run over actor
updates. Prediction already exists certified (`predict`/`cpredict`/`splice` — the reconcile
laws); interpolation is PRESENTATION and stays behind the D15 firewall (ghosts smooth the
VIEW, never the witness). The differentiated claim, unchanged: not a cheaper ghost — a ghost
that cannot lie.

**`intautology` — the integer-tautology layer (from corpus to theorem).** Presburger
arithmetic — integers with addition and order, no multiplication — is consistent, complete,
and DECIDABLE (Presburger 1929; quantifier elimination with a triple-exponential upper
bound and a genuine double-exponential lower bound; the quantifier-free linear fragment is
what SMT solvers decide daily for verification). Today every closed-form envelope in this
repo (`storecost`, `opcost`, `slo`, lease interval arithmetic) is MEASURED on a corpus —
falsifiable coverage, not universality. The layer: a hand-rolled, std-only decision
procedure for quantifier-free linear integer arithmetic (Cooper's algorithm or the Omega
test, budget-bounded with a typed refusal on blowup — the OPCOST discipline applied to
proof search), letting selected laws be stated as FORMULAS and graduate from
measured-on-the-corpus to DECIDED-for-all-integers. Honest scope declared up front: only
the linear fragment graduates (affine envelopes like `snapshot_bytes(n) = 4 + 25·n`
qualify directly; nonlinear forms like `window_storage(H, n)` = `(H+1)·snapshot_bytes(n)`
decide per-bounded-parameter or stay corpus-measured); the decision procedure itself is
pure integer code — a natural future cross-placement.

Behind both, unchanged from the sealed brief: Phase V (the three.js/WebGPU firewall client
rendering ONLY the admitted replica; `bench_protocol.md` §3 input→photon on the named
host) and Phase M (the mesh — certified authority migration as lease transfer, n-way
nullity as the write scheduler; the answer to server meshing that cannot lie).

**Pre-mesh hardening (this rung) — the schedule before Phase M opens.** A web-researched
adversarial debate (`docs/hardening_brief.md`) ranked the hardening that should precede the mesh.
LANDED here: Tier 1 (the headline aligned to the ledger — §11 and the README threat model) and
Tier 2b (the ghost kinematic law — a WARDED `ghost_admit` now refuses a remote ghost that
teleports, speed-hacks, or wall-clips, reusing `warden`'s gait bound + walkable-component β₀; the
one genuine correctness gap the debate found, closed). SCHEDULED, pinned by `hardening_brief.md`:
Tier 2 (property-based / metamorphic falsifiers over the flagship ∀-laws) = COMPLETE — all three
flagship universals now face a seeded adversary with independent oracles: `commuteprop` (URDRCPS1,
the commute diamond), `regionprop` (URDRRGP1, reunify == monolith), `stormprop` (URDRSTP1, the storm
prefix property); each red-first, gate-pinned, with an off-gate reseeded explorer; the AIMBOT / ANTI-CHEAT posture = a THREE-BAND phased roadmap — Band A server-driven AoI
delivery WITH Phase M (the real ESP/wallhack mitigation), Band B behavioural detection post-mesh
(DECLARED off-gate, because a statistical detector may not be graded MEASURED), Band C input-rate /
humanness bounds (partial) — because aimbot/botting via LAWFUL inputs is unaddressable at the
authority layer and is NEVER claimed as structurally prevented; Tier 3 (mutation-score + coverage)
= off-gate DECLARED metrics, no rung dependency. The "when" for each is pinned in the brief's
schedule.

**Phase M — the certified mesh (DESIGN PASS landed: `docs/mesh_phase_brief.md`).** With the pre-mesh
hardening arc complete (Tier 1, Tier 2b, Tier 2 all landed), Phase M is opened design-first. It is a
COMPOSITION, not a new mechanism: `lease` → authority migration as lease transfer (single-writer per
region, structural via the CAS); `rannull`/RAN-0 → the write scheduler (n-way nullity); `worldregion`
Seam Composition → `MESH == MONOLITH`; `commute` → same-region concurrency; `wire`+`storm` →
replication with partition→prefix; `sealwrit` → authority identity. CAP posture STATED: CP
(consistency + partition-tolerance, availability sacrificed — refuse rather than guess), the
availability cost declared, a consensus progress layer left as a named optional overlay. Six
falsifiable guarantees and a five-rung roadmap (M1 lease lattice / n-way scheduler → M2 migration →
M3 meshed simulation → M4 partitioned mesh → M5 attested mesh session) are in the brief; each lands
red-first when built. Nothing is built yet — grades are DECLARED / SPECULATIVE→SCOPED.

---

## 11. The comparative position (web-reviewed) — what Hainuwele is, next to what exists

Read the evidence stack and the genre identifies itself: this is an FPS MMO — but not in the
conventional sense. It is a persistent world where simulation depth meets twitch
responsiveness, architected for both the frame-precise demands of first-person combat and
continent-scale concurrency — with the one property nothing shipping has: the whole path is
certified. The telltale signs, each pointing at its landed rung:

- **Twitch DNA.** Rollback netcode with tick-precise desync LOCALIZATION (disagreements pinned
  to tick 4, 6, or 11 — `lockstep`/`rollback`/`field_desync`) is fighting-game/FPS lineage,
  not MMO-tab-target lineage. Certified prediction with reconciles (`predict`/`cpredict`/
  `splice`) and presentation-side interpolation behind a firewall are exactly the
  ghost-snapshot patterns Unity's Netcode-for-Entities builds for fast-paced multiplayer —
  here with ADMISSION where the industry has trust.
- **Avatar locomotion, not click-to-move.** Sprint gating by terrain, stride gaits, stance
  checks, walk-through-wall detection (`stance`/`drive`/`glide`, the warden family) — this is
  first-person movement with collision, wearing an anti-cheat that is topology-grade
  (`wardhom`: the anti-cheat's component count is a three-placed homology invariant).
- **A world larger than any client.** `driftgaze`'s lawful motion — regions acquired by
  verified fetch and released as the player moves, equal-or-refuse preserved across the
  changing resident set — is the streaming architecture of a continent-sized world, proven at
  corpus scale. (Honesty: the MECHANISMS are MEASURED; "thousands concurrent" is the
  architectural direction — `interest`/`warden`/D16 regional authority are built for it — not
  yet a measured scale claim. The scale bench is future work and will be MEASURED-on-named-host
  or it will not be claimed.)
- **Persistence, not sessions.** Content-addressed authority, immutable interred records,
  `persist`/`resurrect`/`testament` — a world with a durable past (through-death recovery,
  writes that survive their writer), not match-based state that evaporates.
- **The nearest shipping relatives** are PlanetSide 2 — the persistent MMOFPS whose
  continent battles hold the Guinness record (1,158 players in one FPS engagement) — for
  scale-plus-twitch, and Space Engineers for physics-as-the-gameplay-medium (volumetric,
  simulation-first sandbox). Hainuwele reads as PlanetSide-2-scale ambitions crossed with
  Space-Engineers-grade simulation depth — WITH a property neither has: STATE-cheats are
  structurally DETECTED, not merely policed (the honest scope — see the threat model in the
  README's Honest boundaries and `docs/hardening_brief.md`: information/input/collusion cheats
  are NOT prevented, as for any server-authoritative design). Every update carries a Lamport
  signature MECHANISM (`sealwrit`; keys and distribution out of scope), every physics step holds
  an energy witness, every contact carries an LCP certificate, every replica converges under
  adversarial chaos that is deterministically reproducible and provably non-vacuous (`storm`),
  and reality itself is attested
  (`wireattest`).
- **The deepest differentiator is the methodology.** Defense-in-depth masking of planted
  defects is encoded INTO the development process (section 9, L15); every rung's plants must
  bite before its goldens pin; individually-redundant layers are proven jointly load-bearing.
  Most engines get their falsification regime retroactively, from desync bugs shipped to
  production; here it is the constitution.

Sources reviewed at writing time: Unity Netcode-for-Entities ghost/snapshot docs; Valve's
Source multiplayer networking (fixed server tick, client interpolation ~100 ms behind between
snapshots); snapshot-interpolation netcode surveys; the PlanetSide 2 Guinness record;
Overwatch's ~63Hz tick with client-side interpolation. Conclusions recorded here; every law
implied is falsified locally, not by citation.

---

## 12. The window ladder — OODA to a windowed execution

**Observe.** The wire phase is SEALED; batch #3 is due; the certified island exists with a
declared WebGL2 view (`terrain_view3d.html` — currently a file you open, not a loop you
play); the named host's MEASURED native sim tick is ~0.073 ms (bench §4b). **Orient.** The
distance to "a game running in a window" is not simulation power — it is one missing
VERTICAL SLICE: input → certified tick → witness → declared view → pixels, closed in a loop,
in one window. **Decide.** The ladder below, strictly ordered; the covenant's boundary first.
**Act.** Each rung lands by the section-5 workflow — red-first, plants bite, goldens pin,
gate ×2.

- **V0 — placement batch #3. LANDED** (`wirephase_rs`). Single-file std-only Rust for all five
  wire-phase families (URDRWIR1/URDRSTM1/URDRSWT1/URDRDGZ1 + URDRWAT1's checker re-derived over a
  synthetic trace), live re-verified per gate run; the minted_height defect diverges fifteen of
  sixteen scenes and crashes the attest checker. The covenant's debt is PAID — V1 is now open.
- **V1 — `panelight`, the windowed loop (THE identified vertical slice — self-contained,
  end-to-end, nothing redundant with any landed rung).** One window (the existing WebGL2
  path first; three.js/WebGPU is the target, not the gate), one avatar, the real game loop:
  a fixed-timestep integer authority tick (the `drive`→`glide` fold + `worldstep`) driven by
  an accumulator, rendering at display rate, keyboard→`drive` commands in, witness-cited
  frames out. The gate covers everything except the pixels: the LOOP's tick sequence is a
  transcript with a pinned digest (deterministic given an input log); the window is its
  declared depiction under the `view_witness` citation contract.
- **V2 — the wired window.** V1's client becomes a wire client: subscribe, admit live
  terraform edits mid-play, `driftgaze` acquisition as the avatar crosses regions. The
  brief's demonstration lands: two windows, one authority, an edit made in one view
  appearing in the other, every byte admitted rather than trusted.
- **V3 — `ghostsnap` (section 10).** Other actors appear: the actor wire, certified ghosts,
  interpolation overlay declared. The window becomes multiplayer.
- **V4 — the sealed frame.** bench_protocol §3 input→photon on the named host: the fps and
  latency numbers become MEASURED (named host) or stay unclaimed. The frame budget joins the
  gate the way `frontbench-budget` already polices MEASURED-without-a-log.
- **V5 — the attested session.** The `wireattest` trace discipline extended to a real windowed
  session: a play session recorded as a self-digested input+outcome trace, replayed by the
  gate to the same witnesses. The demo is then not a video — it is a proof.

### How the frame rate is reached, specifically

The industry's standard decoupling (Source engine: fixed server tick, clients render at
display rate and interpolate between the last snapshots; Overwatch: ~63Hz tick under
higher-fps rendering) — adopted, with certified endpoints:

1. **The authority tick is integer and TINY.** The measured native sim tick on the named
   host is ~0.073 ms (bench §4b, the host log the gate enforces) — under a 60Hz frame
   budget of 16.67 ms that is <0.5% of the frame; even a 128Hz authority tick would use
   <1%. Headroom is structural: no floats, no GC-pressure allocation patterns on the hot
   path, Q32.32 fixed-point where exactness is unaffordable.
2. **Render rate is DECOUPLED from tick rate.** The window's loop runs at display rate
   (60/120/144); the authority advances on a fixed-timestep accumulator. Frames between
   tick boundaries show DECLARED interpolation of certified poses (`fpclip`/`fppose` tracks;
   `nlerp` on the frozen Q32.32 quaternion law) — the ghost-snapshot pattern with both
   endpoints admitted records. The local avatar uses certified prediction (`predict`/
   `cpredict`) with `splice` reconciles, so input feels immediate while the authority stays
   authoritative.
3. **Per-tick work is BOUNDED, so frame time cannot spike.** `opcost` pins each core
   operation's exact integer op-count; `govern`/`priogov` admit a budget-bounded prefix per
   tick and defer the rest (never overrun — a typed refusal instead of a dropped frame);
   `interest`/`driftgaze` bound resident state so tick cost scales with the demand set, not
   the world. Worst-case latency is a certified number (`slo`/`clslo`), not a hope.
4. **No fps number is claimed until §3 runs.** The pipeline above makes high fps
   ARCHITECTURALLY cheap; the claim itself stays NOT_MEASURED until input→photon is logged
   on the named host (V4). That is bench_protocol's law and it applies to us first.

### How graphics is overlaid, specifically

The D15 firewall (`presentation_doctrine.md`), applied end-to-end — the graphics layer is an
OVERLAY on the witness, never a participant in it:

1. **One-way glass.** The renderer's ONLY input is the admitted replica (heightfield bytes,
   wave params, admitted poses). Nothing renders that was not admitted; nothing admitted is
   altered by rendering. There is no readback path — the GPU cannot desync anyone.
2. **Float is legal OUT THERE.** Inside the membrane, floats are refused; the overlay may
   use GPU floats freely (Gerstner water, analytic normals, lighting) precisely BECAUSE it
   is outside the authority — divergent rasterization across GPUs changes pixels, never
   state. `terrain_view3d.html` already demonstrates this: a float Gerstner surface drawn
   from the SAME integer wave params the exact `wavefield` authority certifies.
3. **The citation is measured even though the pixels are declared.** Every exported view
   embeds `hf_witness`/`wave_witness` and the `view_witness` contract checks the citation
   against the LIVE authority — a one-hex forgery reddens the gate. The picture may be
   pretty; its CLAIM to depict the authority is mechanically checked.
4. **Knobs move the view digest, never the witness.** Camera, materials, interpolation
   smoothing, upscaling — all presentation knobs are walled: they move the view's identity,
   and the witness digest cannot move (the fold-into-witness defect diverges — a gate row).
5. **The idle law.** Zero frames while idle; the renderer draws on demand. A window that
   shows a still world costs nothing — presentation is an overlay, and an overlay you are
   not looking at does not run.

The OODA loop closes here: position reviewed, the one missing vertical slice named (V1),
the ladder ordered, the covenant's boundary respected. The next OODA review belongs at the
V2/V3 seam, when the windowed loop meets the wire.

