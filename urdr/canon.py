# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Canonical bytes → SHA-256 (D1 §7). One canonical form per value; identity is
content. Sorts every mapping; never touches Python iteration order. digest ≠ MAC."""
import hashlib
import struct

from . import values as V


def _varint(n: int) -> bytes:
    assert n >= 0
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _sym_bytes(name: str) -> bytes:
    raw = name.encode("utf-8")
    return _varint(len(raw)) + raw


def canon(v) -> bytes:
    if isinstance(v, V.Int):
        return b"i" + struct.pack(">q", v.n)
    if isinstance(v, V.Sym):
        return b"y" + _sym_bytes(v.name)
    if isinstance(v, V.ListV):
        return b"l" + _varint(len(v.items)) + b"".join(canon(x) for x in v.items)
    if isinstance(v, V.Store):
        parts = [b"s", _varint(len(v.fields))]
        for key in sorted(v.fields):
            parts.append(_sym_bytes(key))
            parts.append(canon(v.fields[key]))
        parts.append(digest(v.parent) if v.parent is not None else b"\x00" * 32)
        return b"".join(parts)
    if isinstance(v, V.Grounded):   # before Claim: Grounded is not a Claim subclass
        return b"g" + canon(v.value) + v.witness
    if isinstance(v, V.Claim):
        return (b"c"
                + bytes([V.MATURITIES.index(v.maturity)])
                + bytes([V.EVIDENCES.index(v.evidence)])
                + canon(v.value))
    if isinstance(v, V.Conflict):
        return b"x" + canon(v.claim) + v.verifier_digest
    if isinstance(v, V.Lambda):
        parts = [b"f", _varint(len(v.params))]
        for p in v.params:
            parts.append(_sym_bytes(p))
        parts.append(v.body.canon_bytes())
        parts.append(_varint(len(v.captured)))
        for name in sorted(v.captured):
            parts.append(_sym_bytes(name))
            parts.append(canon(v.captured[name]))
        return b"".join(parts)
    if isinstance(v, V.Composed):
        return b"o" + canon(v.f) + canon(v.g)
    if isinstance(v, V.Builtin):
        return b"b" + _sym_bytes(v.name)
    if isinstance(v, V.DigestV):
        return b"d" + v.raw
    raise TypeError(f"no canonical form for host object {type(v).__name__}")


def digest(v) -> bytes:
    return hashlib.sha256(canon(v)).digest()


def hexdigest(v) -> str:
    return hashlib.sha256(canon(v)).hexdigest()
