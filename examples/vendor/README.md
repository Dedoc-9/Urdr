<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/vendor/` — import-by-digest vendor modules

## Index

- `<64-hex>.urdr` — content-addressed vendor modules (the filename is the digest).
- `urdr.lock` — the lockfile pinning each import to its exact hash.

## Whitepaper

The happy path for third-party code: modules are vendored by **content hash**, so an
import resolves to exactly the reviewed bytes or it refuses. There is no "latest", no
mutable name — the lockfile + digest filenames make every import reproducible and
tamper-evident. Pairs with `examples/rejected/vendor/` (the refusal case).

## Dev notes

- Filenames are digests; regenerating a module changes its name and its lock entry.
- Exercised alongside the `registry`/module import path.
