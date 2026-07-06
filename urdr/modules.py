# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R5: import-by-digest modules, offline (D1 §17). A module is a `.urdr` file
addressed by the SHA-256 of its CANONICAL SOURCE BYTES — byte-level content
addressing, the Unison lesson at the integrity level. `source-hash ≠
definition-hash`: this refuses tampered/renamed *bytes*, not reformatted
*definitions* (α-normalized semantic addressing is the SCOPED strengthening,
D5). Resolution is purely local: a `vendor/<digest>.urdr` store plus a
`vendor/urdr.lock` manifest. A wrong pin or tampered file is `URDR-PIN`; an
unvendored or unpinned digest is `URDR-MODULE`. Nothing here touches a
network — offline is structural (there is no import of a network library),
not hopeful (`tests/test_modules.py::test_resolver_imports_no_network`)."""
import hashlib
import os
import unicodedata

from .errors import UrdrError, PIN, MODULE

_HEX = frozenset("0123456789abcdef")
_VENDOR = "vendor"
_LOCK = "urdr.lock"


def valid_digest(s: str) -> bool:
    return isinstance(s, str) and len(s) == 64 and all(c in _HEX for c in s)


def canonical_text(raw: bytes) -> str:
    """The exact text the lexer would consume: utf-8 (BOM tolerated), universal
    newlines, NFC. Formatting/comments ARE content here — that is the honest
    limit of a source-hash (D5). A BOM and CRLF are not content and are
    normalized away so the same source addresses identically on every host."""
    text = raw.decode("utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text)


def module_digest(raw: bytes) -> str:
    return hashlib.sha256(canonical_text(raw).encode("utf-8")).hexdigest()


def load_lock(root: str) -> dict:
    """vendor/urdr.lock → {name: digest}. Missing or malformed ⇒ URDR-MODULE
    (a broken manifest is refused, not guessed)."""
    path = os.path.join(root, _VENDOR, _LOCK)
    if not os.path.isfile(path):
        raise UrdrError(MODULE, f"no lockfile at {_VENDOR}/{_LOCK}: an offline "
                                f"build needs a manifest, not a network")
    out = {}
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, ln in enumerate(fh, 1):
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            parts = ln.split()
            if len(parts) != 2 or not valid_digest(parts[1]):
                raise UrdrError(MODULE, f"malformed lock line {lineno}: want "
                                        f"'NAME <64-hex-digest>'")
            name, digest = parts
            if name in out:
                raise UrdrError(MODULE, f"duplicate lock name '{name}': one "
                                        f"name, one pin")
            out[name] = digest
    return out


def resolve_source(digest: str, root: str, line: int = 0, col: int = 0) -> str:
    """Static resolution: existence → the file hashes to its address (URDR-PIN
    else) → the address is pinned in the lockfile (URDR-MODULE else). No
    evaluation happens here, so a wrong pin is refused *statically*."""
    if not valid_digest(digest):
        raise UrdrError(MODULE, f"not a 64-hex module digest: {digest!r}",
                        line, col)
    path = os.path.join(root, _VENDOR, digest + ".urdr")
    if not os.path.isfile(path):
        raise UrdrError(MODULE, f"no vendored module @{digest[:12]}… under "
                                f"{_VENDOR}/ (offline; nothing is fetched)",
                        line, col)
    with open(path, "rb") as fh:
        raw = fh.read()
    actual = module_digest(raw)
    if actual != digest:
        raise UrdrError(PIN, f"vendored bytes hash to {actual[:12]}…, not the "
                             f"declared @{digest[:12]}… — a wrong pin is "
                             f"refused, not resolved", line, col)
    if digest not in set(load_lock(root).values()):
        raise UrdrError(MODULE, f"@{digest[:12]}… is not pinned in "
                                f"{_VENDOR}/{_LOCK} (unpinned dependency)",
                        line, col)
    return canonical_text(raw)


def verify_lock(root: str) -> list:
    """The gate's manifest check: every lock entry's file exists and hashes to
    its pin. Returns [(name, digest)] sorted; raises URDR-PIN / URDR-MODULE on
    the first breach (a lockfile that does not match its vendor/ is refused)."""
    lock = load_lock(root)
    for name in sorted(lock):
        resolve_source(lock[name], root)  # existence + hash + pinned
    return sorted(lock.items())
