#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""name -> digest REGISTRY + fetch-and-pin -- the package/asset UX for R4.

R5 already gives CODE this shape: `use @<sha256>`, vendored offline, pinned in
`vendor/urdr.lock`; a wrong pin is refused statically (URDR-PIN/URDR-MODULE).
This is the SAME shape for DATA -- an API response, an online asset, a live
update -- captured at the *līmes* as a RECORDED INPUT (R4). The internet is
non-deterministic; the kernel is not. The bridge is a pin:

  1. fetch ONCE at the boundary (host-side; the evaluator never touches a socket),
  2. RECORD the response as a content-addressed snapshot via the one codec
     (the filename IS its SHA-256 digest -- the authority),
  3. PIN a human name to that digest in `urdr.registry`,
  4. thereafter RESOLVE by name, OFFLINE: no network, load digest-verified.

The digest is the only authority. A name is UX; a URL is provenance/audit --
neither can smuggle a value in. A tampered snapshot is URDR-LIMES (the codec).
A name whose pin does not match its snapshot is refused, not resolved. A
re-fetch that returns different bytes is a NEW digest = a NEW pin = a NEW run;
you cannot silently move a name to new content. That is how a live, changing
internet composes with a kernel that must replay bit-identically.

This file is a runner-side / boundary tool (like verify.py's grant plumbing),
NOT part of the sealed evaluator. Its record/pin/resolve/verify path is pure and
deterministic (tested). Its fetch path is a host capability: inject a `fetcher`
(so the deterministic core is testable without a network) or run it where the
network lives."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from urdr import snapshot                       # noqa: E402
from urdr import canon as C                     # noqa: E402
from urdr.errors import UrdrError, CAP, LIMES   # noqa: E402

_HEX = "0123456789abcdef"
_REGISTRY = "urdr.registry"
_SNAP = ".urdrsnap"


def valid_digest(s: str) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in _HEX for c in s)


def _snap_path(registry_dir: str, digest: str) -> str:
    return os.path.join(registry_dir, digest + _SNAP)


def record(value, registry_dir: str) -> str:
    """Record an Urðr value as a CONTENT-ADDRESSED snapshot. The returned digest
    IS the filename IS the authority (mirrors R5's vendor/<digest>.urdr). Idempotent:
    the same value records to the same path with the same bytes."""
    digest = C.hexdigest(value)
    os.makedirs(registry_dir, exist_ok=True)
    snapshot.save(_snap_path(registry_dir, digest), value)   # digest-verified codec
    return digest


def load_registry(registry_dir: str) -> dict:
    """urdr.registry -> {name: (digest, url)}. Each line: NAME DIGEST URL. A
    missing index is empty (nothing pinned yet); a malformed or duplicate line is
    URDR-CAP -- a broken index is refused, not guessed (mirrors R5 load_lock)."""
    path = os.path.join(registry_dir, _REGISTRY)
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, ln in enumerate(fh, 1):
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split(None, 2)
            if len(parts) < 2 or not valid_digest(parts[1]):
                raise UrdrError(CAP, f"malformed registry line {lineno}: want "
                                     f"'NAME <64-hex-digest> [URL]'")
            name, digest = parts[0], parts[1]
            url = parts[2] if len(parts) == 3 else "-"
            if name in out:
                raise UrdrError(CAP, f"duplicate registry name '{name}': one "
                                     f"name, one pin")
            out[name] = (digest, url)
    return out


def _write_registry(registry_dir: str, reg: dict) -> None:
    os.makedirs(registry_dir, exist_ok=True)
    path = os.path.join(registry_dir, _REGISTRY)
    lines = ["# name -> digest registry (R4). NAME  DIGEST  URL.",
             "# The DIGEST is authority; NAME is UX; URL is provenance only.",
             "# Managed by tools/registry/pin.py -- edit via the tool, not by hand.\n"]
    for name in sorted(reg):
        digest, url = reg[name]
        lines.append(f"{name} {digest} {url}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def pin(name: str, digest: str, url: str, registry_dir: str) -> None:
    """Bind a human name to a digest. The digest must already be recorded
    (its content-addressed snapshot must exist and hash to it) -- a pin cannot
    name content that is not present. Re-pinning a name to a NEW digest is
    explicit and overwrites; you cannot move a name silently."""
    if not valid_digest(digest):
        raise UrdrError(CAP, f"not a 64-hex digest: {digest!r}")
    snap = _snap_path(registry_dir, digest)
    if not os.path.isfile(snap):
        raise UrdrError(CAP, f"cannot pin '{name}' -> @{digest[:12]}…: no "
                             f"recorded snapshot (record() it first; nothing "
                             f"is fetched here)")
    got = C.hexdigest(snapshot.load(snap))       # URDR-LIMES if tampered
    if got != digest:
        raise UrdrError(CAP, f"snapshot for '{name}' hashes to {got[:12]}…, "
                             f"not @{digest[:12]}… — a wrong pin is refused")
    reg = load_registry(registry_dir)
    reg[name] = (digest, url or "-")
    _write_registry(registry_dir, reg)


def resolve(name: str, registry_dir: str):
    """name -> (value, digest), OFFLINE and digest-verified. URDR-CAP if the
    name is unpinned (nothing ambient). URDR-LIMES if the snapshot is tampered
    (the codec). URDR-CAP if the loaded value does not hash to the pinned digest
    (the pin is the authority, not the file's own claim)."""
    reg = load_registry(registry_dir)
    if name not in reg:
        raise UrdrError(CAP, f"'{name}' is not pinned in {_REGISTRY}: the "
                             f"internet is reachable only through an explicit "
                             f"pin, never ambiently")
    digest, _url = reg[name]
    value = snapshot.load(_snap_path(registry_dir, digest))   # URDR-LIMES if tampered
    got = C.hexdigest(value)
    if got != digest:
        raise UrdrError(CAP, f"registry pin mismatch for '{name}': content "
                             f"hashes to {got[:12]}…, pinned @{digest[:12]}… — "
                             f"refused, not resolved")
    return value, digest


def verify_registry(registry_dir: str) -> list:
    """The gate's manifest check: every pinned name's content-addressed snapshot
    exists and hashes to its pin. Returns [(name, digest)] sorted; raises on the
    first breach (mirrors R5 verify_lock)."""
    reg = load_registry(registry_dir)
    out = []
    for name in sorted(reg):
        _value, digest = resolve(name, registry_dir)
        out.append((name, digest))
    return out


def fetch_and_pin(name, url, registry_dir, fetcher=None) -> str:
    """BOUNDARY (host-side, SPECULATIVE where a real socket is involved): fetch
    ONCE, RECORD (content-addressed), PIN. After this the build is OFFLINE-
    reproducible -- resolve(name) needs no network. `fetcher(url) -> Urðr Value`
    is injected so the deterministic record+pin core is exercised WITHOUT a
    network; the default refuses, because the sealed side does no I/O and this
    sandbox has no sanctioned socket."""
    fetch = fetcher or _no_network
    value = fetch(url)                            # the ONLY non-deterministic step
    digest = record(value, registry_dir)          # from here: pure + reproducible
    pin(name, digest, url, registry_dir)
    return digest


def _no_network(url):
    raise UrdrError(CAP, "no ambient network: inject a fetcher(url)->Value at "
                         "the boundary, or run where the socket lives. The "
                         "evaluator never fetches; the runner pins.")


if __name__ == "__main__":
    # `pin.py verify <dir>` — gate-style manifest check over a registry dir.
    if len(sys.argv) == 3 and sys.argv[1] == "verify":
        rows = verify_registry(sys.argv[2])
        for name, digest in rows:
            print(f"pinned {name} @{digest[:16]}…")
        print(f"registry OK: {len(rows)} pin(s) verified")
    else:
        print("usage: pin.py verify <registry_dir>", file=sys.stderr)
        sys.exit(2)
