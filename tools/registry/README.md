# tools/registry — name→digest registry + fetch-and-pin (R4)

The package/asset UX for a **deterministic** kernel that must live next to a
**non-deterministic** internet. R5 already gives this shape to *code*
(`use @<sha256>`, vendored offline, pinned in `vendor/urdr.lock`; a wrong pin is
refused statically). This gives the same shape to *data* — an API response, an
online asset, a live update — captured at the *līmes* as a **recorded input**.

## The one rule

**The digest is the only authority.** A name is UX; a URL is provenance. Neither
can carry a value across the boundary — only a content-addressed, digest-verified
snapshot can. `Nihil ultrā probātum`.

## Workflow

    fetch ONCE (boundary, host-side)  →  RECORD (content-addressed snapshot)
                                      →  PIN a name to the digest (urdr.registry)
                                      →  RESOLVE by name forever after, OFFLINE

1. **fetch** — a host-side capability at the boundary. The evaluator never opens
   a socket; the runner does, once. In `fetch_and_pin(name, url, dir, fetcher)`
   the `fetcher(url) -> Value` is injected, so the deterministic record+pin core
   is exercised without a network. The default fetcher refuses (`URDR-CAP`):
   there is no ambient network.
2. **record** — `record(value, dir)` writes `dir/<digest>.urdrsnap` through the
   one snapshot codec. The filename **is** the SHA-256 digest (like R5's
   `vendor/<digest>.urdr`). Idempotent: same value → same bytes.
3. **pin** — `pin(name, digest, url, dir)` binds a human name to a digest in
   `urdr.registry`. The digest must already be recorded; a pin cannot name absent
   content. Re-pinning a name to a **new** digest is explicit and overwrites — a
   name never moves to new content silently.
4. **resolve** — `resolve(name, dir) -> (value, digest)`, offline and
   digest-verified. Unpinned name → `URDR-CAP`. Tampered snapshot → `URDR-LIMES`
   (the codec). Loaded value that does not hash to the pin → `URDR-CAP`.

## `urdr.registry` format

    # comments and blank lines ignored
    NAME  DIGEST(64-hex)  URL

`DIGEST` is authority; `NAME` is UX; `URL` is provenance/audit only. Managed by
the tool — edit through `pin.py`, not by hand. A malformed or duplicate line is
`URDR-CAP` (a broken index is refused, not guessed) — mirroring `load_lock`.

## Why this bridges the internet to the kernel

A live endpoint is non-deterministic: fetch it twice, get two answers. A kernel
that must replay bit-identically cannot depend on that. The pin resolves the
tension by **freezing one observation**: the fetch happens once, at the boundary,
and its result becomes a recorded input with a stable digest. Re-fetching later
that returns different bytes yields a **different digest = a different pin = a
different run** — the change is visible and explicit, never silent. You cannot
have *live* and *deterministic* for one execution; you *can* have a live world
turned into a sequence of pinned, replayable, auditable snapshots. That is the
competitive-engine story: online assets and updates enter through pins, and every
build stays offline-reproducible and bit-identical.

## Grading (honest)

- **record / pin / resolve / verify_registry** — MEASURED. Pure, deterministic,
  gate-checked (`tests/test_registry.py`, and the gate's `registry` stage:
  `registry-pins` + `registry-mispin-selftest` non-vacuity).
- **fetch_and_pin's deterministic core** — MEASURED (injected fetcher).
- **the real network fetch** — SPECULATIVE. No sanctioned socket runs in the
  build/sandbox; the fetch is a host capability at the boundary, graded only
  where it is actually exercised.

## Files

- `pin.py` — the tool (record, pin, resolve, verify_registry, fetch_and_pin).
- `../../examples/registry/urdr.registry` — a demonstration registry (one pin).
- `../../examples/registry/<digest>.urdrsnap` — the content-addressed snapshot.
- `../../tests/test_registry.py` — the falsifiers.
- `../../docs/network_bridge.md` — the design note this tool implements.
