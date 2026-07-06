# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Runtime values. The epistemic ladder lives here, and the dynamic latch with it:
even if the static checker were unsound, the Claim constructor refuses inflation
(URDR-INFLATE-DYN) and Grounded cannot exist without a 32-byte witness."""
from .errors import UrdrError, INFLATE_DYN, TYPE_RUN

MATURITIES = ("SPECULATIVE", "SCOPED", "IMPLEMENTED")
EVIDENCES = ("NA", "DECLARED", "MEASURED")
# maturity → highest licensed evidence (D1 §5, the ladder)
CEILING = {"SPECULATIVE": "NA", "SCOPED": "DECLARED", "IMPLEMENTED": "MEASURED"}

_I64_MOD = 1 << 64
_I64_HALF = 1 << 63


def wrap_i64(n: int) -> int:
    """Defined two's-complement wrap: the core's only arithmetic convention."""
    return ((n + _I64_HALF) % _I64_MOD) - _I64_HALF


def ladder_allows(maturity: str, evidence: str) -> bool:
    return EVIDENCES.index(evidence) <= EVIDENCES.index(CEILING[maturity])


class Value:
    __slots__ = ()


class Int(Value):
    __slots__ = ("n",)

    def __init__(self, n: int):
        self.n = wrap_i64(int(n))


class Sym(Value):
    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name


class ListV(Value):
    __slots__ = ("items",)

    def __init__(self, items):
        self.items = tuple(items)


class Store(Value):
    """Immutable, parent-linked, content-addressed record. Views cannot mutate it
    because nothing can: there is no mutation API at all (LESSONS L12)."""
    __slots__ = ("fields", "parent")

    def __init__(self, fields: dict, parent):
        self.fields = dict(fields)   # private copy; never exposed for writing
        self.parent = parent          # Store | None

    def view(self, key: str):
        if key not in self.fields:
            raise UrdrError(TYPE_RUN, f"store has no field '{key}")
        return self.fields[key]

    def edit(self, key: str, value) -> "Store":
        fields = dict(self.fields)
        fields[key] = value
        return Store(fields, parent=self)


class Claim(Value):
    """⟨value, maturity, evidence⟩. The constructor is the latch."""
    __slots__ = ("value", "maturity", "evidence")

    def __init__(self, value, maturity: str, evidence: str):
        if maturity not in MATURITIES or evidence not in EVIDENCES:
            raise UrdrError(TYPE_RUN, f"bad epistemic tag ⟨{maturity}, {evidence}⟩")
        if not ladder_allows(maturity, evidence):
            raise UrdrError(
                INFLATE_DYN,
                f"latch: evidence {evidence} exceeds what {maturity} licenses "
                f"(ceiling {CEILING[maturity]})",
            )
        self.value = value
        self.maturity = maturity
        self.evidence = evidence


class Grounded(Value):
    """The only inhabitant of 'MEASURED'. Mintable solely by ᛞ (see evaluate.py);
    structurally it cannot exist without a 32-byte witness digest."""
    __slots__ = ("value", "witness")

    maturity = "IMPLEMENTED"
    evidence = "MEASURED"

    def __init__(self, value, witness: bytes):
        if not isinstance(witness, bytes) or len(witness) != 32:
            raise TypeError("Grounded requires a 32-byte witness digest")
        self.value = value
        self.witness = witness


class Conflict(Value):
    """↯ — a failed verification. Carries the claim and the verifier's digest.
    No operation merges, averages, or coerces a Conflict."""
    __slots__ = ("claim", "verifier_digest")

    def __init__(self, claim: Claim, verifier_digest: bytes):
        if not isinstance(verifier_digest, bytes) or len(verifier_digest) != 32:
            raise TypeError("Conflict requires a 32-byte verifier digest")
        self.claim = claim
        self.verifier_digest = verifier_digest


class Lambda(Value):
    """A closure. Captured free variables are part of its canonical form —
    content identity includes what the function closes over."""
    __slots__ = ("params", "body", "captured")

    def __init__(self, params, body, captured: dict):
        self.params = tuple(params)
        self.body = body
        self.captured = dict(captured)  # name → Value, resolved strictly at creation


class Composed(Value):
    """f ∘ g as a first-class value."""
    __slots__ = ("f", "g")

    def __init__(self, f, g):
        self.f = f
        self.g = g


class Builtin(Value):
    __slots__ = ("name", "arity", "fn")

    def __init__(self, name: str, arity: int, fn):
        self.name = name
        self.arity = arity
        self.fn = fn


class DigestV(Value):
    __slots__ = ("raw",)

    def __init__(self, raw: bytes):
        if not isinstance(raw, bytes) or len(raw) != 32:
            raise TypeError("Digest value requires 32 raw bytes")
        self.raw = raw
