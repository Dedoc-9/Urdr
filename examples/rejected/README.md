<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# `examples/rejected/` — the must-die corpus (every program here MUST be refused)

## Index

- `MANIFEST.txt` — maps each rejected program to its **expected refusal reason**.
- `*.urdr` — ~46 programs that must each be refused (capability overclaims, deficient
  atlases, wrong centering, actor overclaims, malformed structure, …).
- [`vendor/`](vendor/) — a rejected vendor module (bad digest) + its lock.

## Whitepaper

A type system is only as strong as what it *refuses*. This corpus is the negative space of
the language: each program is designed to die, and the `rejections` gate stage asserts not
merely that it fails but that it fails **for the declared reason** in `MANIFEST.txt`. A
program that starts passing — or fails for the wrong reason — reddens the gate. This is how
"the checker rejects X" becomes a measured claim instead of a hope.

## Dev notes

- Add a rejection as a `.urdr` file **plus** a `MANIFEST.txt` line naming its refusal code;
  a rejected program with no expected reason is not a test, it is noise.
- Never make one of these pass to "clean up" the corpus — a green must-die is a regression.
