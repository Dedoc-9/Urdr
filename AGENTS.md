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
`__int128`), that is **thirteen Rust placements and four C99 runtimes** — three
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
   graded inventory is [`spec/D5-ledger.md`](spec/D5-ledger.md). Never write a
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

10. **Docs must match reality.** When counts change, comb the docs (`README.md`,
    `docs/PAPER.md`, `spec/D*`) and fix stale numbers. `spec/D5` is the graded
    ledger, `spec/D11` the layer contracts, `spec/D12` the versions/freeze. A doc
    that overstates is a bug — file it (or fix it).

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
| `tools/intla/` | `urdr-math` (exact integer linear algebra), `urdr-rigidity`, and the D17 invariant-detector library (`gf2` exact 𝔽₂ substrate, `toric` code dimension, `persim` persistence barcode) |
| `tools/physics/` | exact dynamics, LCP, joints, `field.py`; the `Q`/`Vec` exact substrate; **`fp_dynamics.py`** bounded fixed-point steppers (rung 5) |
| `tools/render/` | fixed-point rasterizer (`raster.py`) + 3D depth (`raster3d.py`) |
| `tools/*/*_rs/` | independent `std`-only Rust placements (kernel, render, physics, math, fixed-point dynamics, the N1–N5 netcode stack, D16 regional authority, and the toric/rigidity detectors) |
| `tools/netcode/` | The N1–N5 stack: **`lockstep.py`** (peers exchange inputs only, one `URDRLST1` witness chain, desyncs localized), **`rollback.py`** (canonical snapshots; late inputs rewind + replay and converge to the N1 chain; `ROLLBACK-REFUSE`/`ROLLBACK-CONFLICT`), **`authinput.py`** (Lamport-OTS envelopes gate admission; `AUTH-REFUSE`), **`worldstep.py`** (authored `URDR-WORLD-3` scenes in the loop; `WORLD-REFUSE`; **N4.1** opt-in sqrt-free body-body contact), **`worldpeer.py`** (N5 — the composed contract: authored world + authenticated transcript → one witness or one typed refusal; `URDRWPN1` world pin), and **`worldregion.py`** (**D16** regional authority: partition by integer x-seams → deterministic reunification reproduces the monolith witness, `REGION-REFUSE`); six corpora + Rust placements `{lockstep,rollback,authinput,worldstep,worldpeer}_rs` + `worldregion_{rs,c}`; all frozen at 0.1 in D12 |
| `tools/editor/` | browser authoring + deterministic-replay front-end (`urdr_designer.html`, `replay.py`, `load_world.py`) — **exploratory** consumer; the `--fp` stepping it demos is the gated rung 5 |
| `tools/frontfps/` | **`frontfps.py`** — the consolidated FPS/MMO authoring canon (**URDR-FPSW-1**, Stage 1): meshes + rigs + capsule hitboxes + actors + spawns + D16 seams under ONE world-identity law (provenance excluded, `FPSW-REFUSE` total, no digest for an inadmissible world), plus the first auto-affordance (`auto_capsule`, containment-certified, defect-checked). Staged FPS/MMO plan + OODA reports in its README |
| `tools/world_host/` | multi-actor world runtime (weave, history, regional) |
| `spec/` | **normative**: D1 language, D5 ledger, D7 execution geometry, D8 portable kernel, D9 numeric substrate, D10 observer, D11 layer contracts, D12 versions/freeze |
| `docs/` | narrative: `PAPER.md` (OSDI-style systems paper), `network_bridge.md`, roadmap, transcripts |
| `LESSONS.md` | ported laws / hard-won rules |

---

## 7. Grading vocabulary (quick reference)

- **`MEASURED`** — the gate (or a named host's cross-placement run) proves it *now*.
- **`DECLARED`** — a written target/contract; not yet demonstrated.
- **`SPECULATIVE`** — plausible, unmeasured (e.g. a Rust placement before compile).
- **`cross-placement`** — a second, independent implementation reproduces the
  digests bit-for-bit (the strongest evidence tier).
- **reproducible ≠ exact** — fixed-point layers are deterministic and
  cross-placeable but *round*; say which you mean.
- **corpus agreement ≠ universal correctness** — the gate certifies agreement on a
  *stated corpus*, not all inputs.

If you remember one thing: **claim exactly what the corpus shows, and make the gate
able to prove you wrong.**
