# The Network Bridge — living on the līmes

> *Nihil ultrā probātum.* A program that claims more than it verifies does not
> typecheck. A kernel that reads more than it can replay does not stay
> deterministic.

This note explains how Urðr — a deterministic, epistemically-typed kernel —
composes with the one thing that is irreducibly non-deterministic: the live
internet. It is the design behind the R4 network-read fixture
(`examples/network_read.urdr`) and the name→digest registry
(`tools/registry/`). Nothing here changes the sealed language. No new glyph is
minted. The kernel stays frozen; the network lives *outside* it, at the boundary.

## 1. The tension, stated honestly

A game/simulation engine that wants to be competitive needs the outside world:
package registries, HTTP APIs, live config, downloadable assets, patch feeds. All
of these are non-deterministic. Fetch the same URL twice and you may get two
different bytes — a new revision, a load-balanced mirror, a clock-stamped
payload, an outage. 

Urðr's whole value is the opposite property: **the same program on the same
inputs produces the same digest, bit-for-bit, on every host and placement**
(D8 portable-kernel conformance). The evaluator has no clock, no RNG, no float,
no ambient I/O, no iteration-order dependence. Determinism is not a feature to be
traded away for convenience; it is the thing being sold.

So the two cannot be naively mixed. You **cannot have a single execution that is
both live and deterministic.** If the kernel reached out and touched a socket
mid-evaluation, the digest would depend on whatever the network happened to
return, and reproducibility — the entire premise — would be gone.

## 2. The resolution: the līmes

Urðr already has the shape of the answer, from R4 (D1 §16): **I/O is a capability,
nothing is ambient, and the boundary where the program meets the world is the
*līmes*.**

- **Reads are RECORDED INPUTS.** A read capability is not a live handle. It is a
  value that was *loaded once, at the boundary, through the one snapshot codec,
  digest-verified*, and thereafter *replayed bit-identically*. The evaluator does
  no I/O — it consumes a recording. (See `urdr/capability.py`: `build_capset`
  loads the snapshot at mint time; evaluation only replays it.)
- **Writes are EFFECT-PLANS.** The evaluator never writes; it *returns* a pure
  plan, and the runner executes it at the līmes, after success,
  validate-everything-then-write-everything, fail-closed.

The bridge is one sentence:

> **A network response is just a recorded input whose provenance is a URL.**

An API call, an online asset, a live update — each is fetched **once**, at the
boundary, by the runner (never the evaluator), and **recorded** as a
content-addressed, digest-verified snapshot. From that moment it is an ordinary
R4 recorded input: replayed bit-identically, folded into the program's own
identity, auditable, and refused (`URDR-LIMES`) if tampered. The kernel never
knew there was a network at all.

```
        NON-DETERMINISTIC                 |            DETERMINISTIC
        (the internet)                    |            (the kernel)
                                          |
   GET https://api.example/asset  --->  [ līmes ]  ---> recorded input
        (runner, host-side, ONCE)          fetch-once      (digest-pinned,
                                           record          replayed exactly)
                                           pin-by-digest
                                          |
                                          the evaluator never opens a socket
```

## 3. The authority is the digest, never the name or the URL

Once a response is recorded, its **SHA-256 digest is its only authority**. This
is the same content-addressing the kernel already uses everywhere (the membrane
store `ᚠ`, the module system R5's `use @<sha256>`, D8 accept-digests).

- A **name** (`asset:hero_manifest`) is *UX* — a human handle.
- A **URL** (`https://…`) is *provenance* — an audit trail of where the bytes
  came from.
- Neither can carry a value across the boundary. Only the digest-verified
  snapshot can. A name that resolves to content that does not hash to its pin is
  **refused, not resolved** (`URDR-CAP`). A snapshot whose bytes do not match
  their recorded digest is **refused, not repaired** (`URDR-LIMES`).

This is what makes "live" safe: the live world is turned into a *sequence of
pinned observations*, each one frozen and named. A re-fetch that returns
different bytes produces a **different digest → a different pin → a different
run.** The change is always explicit and visible; a name never silently slides
onto new content.

## 4. Packages / registries: the R5 shape, extended to data

R5 already gives **code** this exact discipline: `use @<sha256> as lib`, vendored
offline in `examples/vendor/`, pinned in `vendor/urdr.lock`; a wrong pin is
refused *statically* (`URDR-PIN` / `URDR-MODULE`); an offline build needs a
manifest, not a network.

`tools/registry/` gives **data** the same shape (a `pip`/`npm`/`cargo`-like UX
without surrendering determinism):

| concern            | R5 (code)                     | registry (data)                     |
|--------------------|-------------------------------|-------------------------------------|
| address            | `@<sha256>`                   | `<digest>.urdrsnap` (content-addr)  |
| human handle       | `use … as lib`                | `NAME` in `urdr.registry`           |
| manifest           | `vendor/urdr.lock` (NAME→dig) | `urdr.registry` (NAME→dig, +URL)    |
| offline build      | vendored, no fetch            | recorded snapshot, no fetch         |
| wrong pin          | `URDR-PIN` (static)           | refused on resolve (`URDR-CAP`)     |
| tamper             | hash mismatch refused         | `URDR-LIMES` (the one codec)        |

**fetch-and-pin** is the workflow that populates it: fetch once at the boundary,
record content-addressed, pin a name to the digest. After that the build is
**offline-reproducible** — `resolve(name)` needs no network, ever. See
`tools/registry/README.md` for the API and the honest grading.

## 5. What is proven, and what is not (grading)

Following the no-inflation discipline — *library-proven* vs *URDR-gate MEASURED*
vs *both-placements* — this is graded exactly as far as it is exercised:

- **MEASURED (URDR gate, reference placement).** The recorded-input replay
  (`examples/network_read.urdr`) is deterministic, golden-pinned, and the
  compiled placement agrees with the reference (`oracle:network_read`). The
  ungranted network read is refused `URDR-CAP` (`network_read_ungranted`). A
  tampered recording is refused `URDR-LIMES`. The registry's
  record/pin/resolve/verify path is gate-checked (`registry-pins` +
  `registry-mispin-selftest` non-vacuity; `tests/test_registry.py`).
- **Reference-runner only (not cross-placed).** The *capability layer* — grants,
  snapshot loading, effect-plan execution — is the reference runner's job, by
  design (`urdr-core-rs` exits loudly on `--grant`: capabilities and snapshots
  are not the portable kernel's concern). The **pure computation** over a
  recorded value is cross-placeable; the **plumbing that recorded it** is not.
- **SPECULATIVE.** The *real network fetch itself* is a host capability. No
  sanctioned socket runs in the gate/sandbox, so `fetch_and_pin`'s network step
  is graded only where it is actually exercised; its deterministic core
  (record + pin) is tested with an injected fetcher. A live socket is future
  work at the *runner* tier, and it will never move into the evaluator.

## 6. Why this is the competitive-engine enabler

A deterministic engine that *cannot* touch the internet is a toy. A live engine
that *cannot* reproduce a frame is not trustworthy — no replay, no rollback
netcode, no deterministic lockstep multiplayer, no auditable asset pipeline, no
reproducible build.

The līmes gives both at once, at different tiers:

- the **runner** talks to the live, changing world and turns each observation
  into a pinned, replayable snapshot;
- the **kernel** consumes only pinned snapshots and stays bit-identical, so every
  frame, every transition, every world-tick is reproducible and cross-checkable.

Online assets and live updates enter through **pins**; every execution stays
**offline-reproducible** and **bit-identical**. That is how a program that
"claims more than it verifies does not typecheck" can nonetheless ship with the
whole internet behind it — the internet just has to leave its authority at the
door, as a digest.

## See also

- `urdr/capability.py` — the R4 runner side of the līmes (the mint).
- `examples/network_read.urdr` / `.grants` — the recorded-input fixture.
- `examples/rejected/network_read_ungranted.urdr` — the ambient-read falsifier.
- `tools/registry/` — name→digest registry + fetch-and-pin.
- `spec/D1-spec.md` §16 (R4 capabilities), §17 (R5 modules).
- `spec/D8-portable-kernel.md` — why the kernel stays placement-portable.
- `spec/D5-ledger.md` — the graded claim ledger (network-bridge rows).
