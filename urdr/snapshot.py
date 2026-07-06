# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""R2c: runner-level store snapshots. Persistence is a *līmes* at the process
boundary, owned by the CLI — the language has no I/O syntax and none is added.

Rules of the boundary (fail closed, all URDR-LIMES):
- Grounded does NOT cross: a witness certifies a verification in THIS process
  under THIS evaluator. MEASURED is re-earned after load, never imported.
- Conflict, λ, ∘-compositions, and builtins do not cross (behavior is not data).
- The file carries the value's digest; the loader re-derives and compares —
  a tampered snapshot is refused, not repaired.
"""
import json

from . import canon as C
from . import values as V
from .errors import UrdrError, LIMES

_FORMAT = 1


def _enc(v):
    if isinstance(v, V.Int):
        return {"t": "i", "n": v.n}
    if isinstance(v, V.Sym):
        return {"t": "y", "s": v.name}
    if isinstance(v, V.ListV):
        return {"t": "l", "xs": [_enc(x) for x in v.items]}
    if isinstance(v, V.DigestV):
        return {"t": "d", "h": v.raw.hex()}
    if isinstance(v, V.Store):
        return {"t": "s",
                "f": {k: _enc(v.fields[k]) for k in sorted(v.fields)},
                "p": _enc(v.parent) if v.parent is not None else None}
    if isinstance(v, V.Grounded):
        raise UrdrError(LIMES, "Grounded does not cross the process boundary: "
                               "MEASURED is re-earned after load, never imported")
    if isinstance(v, (V.Capability, V.CapSet)):
        raise UrdrError(LIMES, "authority does not cross the process boundary: "
                               "a grant is minted by THIS run's runner, never "
                               "imported as data")
    if isinstance(v, V.EffectPlan):
        raise UrdrError(LIMES, "an effect-plan does not cross as data: plans "
                               "are executed at the līmes or they are nothing")
    if isinstance(v, V.Claim):
        return {"t": "c", "m": v.maturity, "e": v.evidence, "v": _enc(v.value)}
    raise UrdrError(LIMES, f"{type(v).__name__} is not persistable "
                           f"(behavior and verdicts are not data)")


def _dec(d):
    try:
        tag = d["t"]
        if tag == "i":
            return V.Int(int(d["n"]))
        if tag == "y":
            return V.Sym(str(d["s"]))
        if tag == "l":
            return V.ListV(_dec(x) for x in d["xs"])
        if tag == "d":
            return V.DigestV(bytes.fromhex(d["h"]))
        if tag == "s":
            parent = _dec(d["p"]) if d["p"] is not None else None
            fields = {str(k): _dec(x) for k, x in d["f"].items()}
            store = V.Store(fields, parent=None)
            store.parent = parent  # re-link the lineage chain
            return store
        if tag == "c":
            return V.Claim(_dec(d["v"]), str(d["m"]), str(d["e"]))
    except UrdrError:
        raise
    except Exception as exc:
        raise UrdrError(LIMES, f"malformed snapshot: {exc}")
    raise UrdrError(LIMES, f"malformed snapshot: unknown tag {d.get('t')!r}")


def encode_payload(value) -> dict:
    """The one codec, encode side. R4 shares it: effect-plan execution and
    --save-store both come HERE, so what cannot cross, cannot cross anywhere
    (Grounded, λ, Conflict, builtins, authority, plans)."""
    return {"urdr_snapshot": _FORMAT,
            "digest": C.hexdigest(value),
            "value": _enc(value)}


def write_payload(path: str, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, sort_keys=True, ensure_ascii=True, indent=1)


def save(path: str, value) -> str:
    payload = encode_payload(value)
    write_payload(path, payload)
    return payload["digest"]


def load(path: str):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except (OSError, ValueError) as exc:
        raise UrdrError(LIMES, f"cannot read snapshot: {exc}")
    if payload.get("urdr_snapshot") != _FORMAT:
        raise UrdrError(LIMES, "unknown snapshot format")
    value = _dec(payload["value"])
    derived = C.hexdigest(value)
    if derived != payload.get("digest"):
        raise UrdrError(LIMES, "snapshot digest mismatch: file is tampered or "
                               "corrupted; refused, not repaired")
    return value
