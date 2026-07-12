# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""freeze_check — the D12 freeze manifest, checked mechanically (docs must match reality).

spec/D12-versions.md declares the frozen surfaces in one machine-readable
```freeze-manifest``` block. This module re-derives each frozen digest law from the
DECLARED grammar with its own independent serializers (own i64 big-endian, own SHA-256
calls, no reuse of the checked module's helpers) and compares byte-for-byte against the
live code, so drift in EITHER the doc OR the code reddens the gate:

  magic  <NAME> <module> <kind>     the digest law: kind in {state, trace, loop, field}
  corpus <relpath> <count>          a pinned conformance corpus and its vector count
  format <TAG> <relpath>            a frozen file-format tag and its canonical instance

Checks are behavioral, not string-compares: a canonical fixture is digested through the
live module (with its own defaults — nothing injected) and through this file's
independent build of the declared byte grammar. Non-vacuity: `selftest` corrupts one
declared magic and requires the checker to catch it. `a frozen interface nobody checks
is prose; this makes it a gate`."""
import hashlib
import json
import os
import sys

BLOCK_OPEN = "```freeze-manifest"
BLOCK_CLOSE = "```"
KINDS = ("state", "trace", "loop", "field")


def read_manifest_block(root):
    """The single freeze-manifest block from spec/D12-versions.md. Zero blocks -> "";
    more than one is ambiguous and raises (two manifests could disagree silently)."""
    path = os.path.join(root, "spec", "D12-versions.md")
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if text.count(BLOCK_OPEN) > 1:
        raise ValueError("multiple freeze-manifest blocks in D12 (ambiguous)")
    if BLOCK_OPEN not in text:
        return ""
    body = text.split(BLOCK_OPEN, 1)[1]
    return body.split(BLOCK_CLOSE, 1)[0]


def parse_manifest(block):
    """Parse the line grammar. Unknown directives are an ERROR (fail-closed), not ignored."""
    m = {"magics": [], "corpora": [], "formats": []}
    for raw in block.splitlines():
        ln = raw.strip()
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split()
        if parts[0] == "magic" and len(parts) == 4 and parts[3] in KINDS:
            m["magics"].append((parts[1], parts[2], parts[3]))
        elif parts[0] == "corpus" and len(parts) == 3:
            m["corpora"].append((parts[1], int(parts[2])))
        elif parts[0] == "format" and len(parts) == 3:
            m["formats"].append((parts[1], parts[2]))
        else:
            raise ValueError(f"unparseable freeze-manifest line: {raw!r}")
    return m


# ---- independent serializers (the declared grammars, rebuilt here) ----------------
def _i64(v, endian="big"):
    return int(v).to_bytes(8, endian, signed=True)


def independent_state_digest(magic, words, endian="big"):
    """state law: SHA-256(magic | each word as signed i64, big-endian)."""
    out = bytearray(magic)
    for w in words:
        out += _i64(w, endian)
    return hashlib.sha256(bytes(out)).hexdigest()


def independent_trace_digest(magic, frames):
    """trace law: SHA-256(magic | the ORDERED per-tick hex digests as UTF-8 text)."""
    h = hashlib.sha256()
    h.update(magic)
    for d in frames:
        h.update(d.encode())
    return h.hexdigest()


def independent_loop_digest(magic, vels, lam, reservoir):
    """loop law: SHA-256(magic | u8 nbodies | per-body (vx,vy) Q pairs | u8 ncontacts |
    per-contact lambda Q pair | reservoir (vx,vy) Q pairs); Q = (n, d) each signed i64 BE,
    canonically reduced, d > 0."""
    out = bytearray(magic)
    out.append(len(vels))
    for v in vels:
        for c in v:
            out += _i64(c.n) + _i64(c.d)
    out.append(len(lam))
    for l in lam:
        out += _i64(l.n) + _i64(l.d)
    for c in reservoir:
        out += _i64(c.n) + _i64(c.d)
    return hashlib.sha256(bytes(out)).hexdigest()


def independent_field_digest(magic, w, h, cells):
    """field law (FixedPoint backend): SHA-256(magic | "FIELDFP " | W u32 BE | H u32 BE |
    per-cell signed i64 BE)."""
    out = bytearray(magic) + b"FIELDFP " + w.to_bytes(4, "big") + h.to_bytes(4, "big")
    for v in cells:
        out += _i64(v)
    return hashlib.sha256(bytes(out)).hexdigest()


# ---- the checks --------------------------------------------------------------------
def _check_one_magic(name, mod, kind):
    magic = name.encode("ascii")
    if len(magic) != 8:
        return (False, f"magic must be 8 bytes, got {len(magic)}")
    if kind == "state" and mod == "fp_dynamics":
        import fp_dynamics
        got = fp_dynamics.state_digest(([1, 2], [-3]))
        want = independent_state_digest(magic, [1, 2, -3])
    elif kind == "trace" and mod == "fp_dynamics":
        import fp_dynamics
        got = fp_dynamics.trace_digest(["aa" * 32, "bb" * 32])
        want = independent_trace_digest(magic, ["aa" * 32, "bb" * 32])
    elif kind == "state" and mod == "lockstep":
        import lockstep
        got = lockstep._digest([[1 << 32, 2]], [[-3, 4]], 1)
        want = independent_state_digest(magic, [1 << 32, 2, -3, 4])
    elif kind == "trace" and mod == "lockstep":
        import lockstep
        got = lockstep.trace_digest(["aa" * 32, "bb" * 32])
        want = independent_trace_digest(magic, ["aa" * 32, "bb" * 32])
    elif kind == "loop" and mod == "loop_scenes":
        import loop_scenes
        from rational import Q
        from vecq import Vec
        comps = [[Q(1, 2), Q(-1, 3)]]
        lam = [Q(2, 1)]
        res_c = [Q(0, 1), Q(5, 7)]
        got = loop_scenes.digest_state([Vec(list(c)) for c in comps], lam, Vec(list(res_c)))
        want = independent_loop_digest(magic, comps, lam, res_c)
    elif kind == "field" and mod == "field":
        import field
        got = field.digest(field.FixedPoint, [42], 1, 1)
        want = independent_field_digest(magic, 1, 1, [42])
    else:
        return (False, f"no fixture for ({mod}, {kind}) — fail closed")
    if got != want:
        return (False, f"digest law drift: code {got[:12]}… ≠ declared grammar {want[:12]}…")
    return (True, f"code ≡ declared grammar ({got[:12]}…)")


def check_magics(root, manifest):
    rows = []
    names = [n for (n, _m, _k) in manifest["magics"]]
    rows.append(("freeze:magics-distinct", len(names) == len(set(names)),
                 "all declared magics pairwise distinct" if len(names) == len(set(names))
                 else "duplicate magic declarations"))
    for (name, mod, kind) in manifest["magics"]:
        try:
            ok, detail = _check_one_magic(name, mod, kind)
        except Exception as exc:  # fail closed: an import/shape error is a red, not a skip
            ok, detail = False, f"check errored: {exc}"
        rows.append((f"freeze:{name}", ok, detail))
    return rows


def check_corpora(root, manifest):
    rows = []
    for (rel, count) in manifest["corpora"]:
        path = os.path.join(root, *rel.split("/"))
        if not os.path.exists(path):
            rows.append((f"freeze:{rel}", False, "declared corpus missing"))
            continue
        with open(path, encoding="utf-8") as fh:
            n = sum(1 for ln in fh if ln.strip() and not ln.strip().startswith("#"))
        ok = n == count
        rows.append((f"freeze:{rel}", ok,
                     f"{n} vectors (declared {count})" if ok
                     else f"vector drift: {n} found, {count} declared"))
    return rows


def check_formats(root, manifest):
    rows = []
    for (tag, rel) in manifest["formats"]:
        path = os.path.join(root, *rel.split("/"))
        try:
            with open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
            ok = doc.get("format") == tag
            detail = (f"{rel} carries {tag}" if ok
                      else f"format drift: {rel} carries {doc.get('format')!r}, declared {tag!r}")
        except Exception as exc:
            ok, detail = False, f"unreadable: {exc}"
        rows.append((f"freeze:{tag}", ok, detail))
    return rows


def check_all(root, manifest):
    return (check_magics(root, manifest) + check_corpora(root, manifest)
            + check_formats(root, manifest))


def selftest(root, manifest):
    """Non-vacuity: the checker must be ABLE to redden. Corrupt one declared magic and
    require a failure; the uncorrupted baseline must be green."""
    base = [ok for (_n, ok, _d) in check_all(root, manifest)]
    if not all(base):
        return (False, "baseline already red — selftest cannot discriminate")
    bad = {"magics": list(manifest["magics"]), "corpora": list(manifest["corpora"]),
           "formats": list(manifest["formats"])}
    name, mod, kind = bad["magics"][-1]
    bad["magics"][-1] = ("XXXXXXX1", mod, kind)
    caught = any(not ok for (_n, ok, _d) in check_magics(root, bad))
    return (caught, "a corrupted declared magic is caught (gate can redden)" if caught
            else "corrupted magic NOT caught — the checker is vacuous")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for d in ("physics", "netcode"):
        p = os.path.join(root, "tools", d)
        if p not in sys.path:
            sys.path.insert(0, p)
    manifest = parse_manifest(read_manifest_block(root))
    rows = check_all(root, manifest)
    rows.append(("freeze:selftest",) + selftest(root, manifest))
    red = 0
    for (nm, ok, detail) in rows:
        print(f"[{'PASS' if ok else 'FAIL'}] {nm:<40} {detail}")
        red += 0 if ok else 1
    sys.exit(1 if red else 0)
