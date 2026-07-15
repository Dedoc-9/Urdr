<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/rejected/vendor/` — a must-fail vendor import

## Index

- `ffff…ffff.urdr` — a vendor module whose content does not match its claimed digest.
- `urdr.lock` — the lockfile pinning the (wrong) expectation.

## Whitepaper

The import-by-digest counterpart to `examples/rejected/`: it proves the vendor path
*refuses* a module whose bytes do not hash to the pinned digest. Content-addressing is
only a security property if the mismatch case is enforced, so this fixture makes that
enforcement a gate-checked fact.

## Dev notes

- The digest mismatch is the whole point; do not reconcile the filename with the contents.
