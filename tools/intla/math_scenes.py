#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Conformance scenes for the urdr-math cross-placement (D8 for the exact-integer
linear-algebra spine).

Each named scene runs a frozen urdr-math primitive (or an atlas certificate built
on it) over a fixed integer fixture and serializes the RESULT to a canonical byte
string, hashed to a SHA-256 digest. An independent placement (`urdr_math_rs/`) is
ADMITTED iff it reproduces every digest bit-for-bit and refuses the same cases; a
mismatch is `URDR-MATH-DIVERGENCE`. Reproducing these digests is exactly what
lifts the general-n injectivity certificate and the exact reconstruction solver
from reference-proven to cross-placement MEASURED.

Serialization is deliberately dead-simple and portable (big-endian, name-bound so
a digest can never be cross-wired to another scene):

    payload = MAGIC(8) ‖ u16(len name) ‖ name ‖ op(1) ‖ result-encoding
    digest  = SHA-256(payload)

Integers are two's-complement i64 big-endian; vectors are u16 count then i64 each.
This module is the Python reference; the goldens live in `conformance_math.txt`."""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import urdr_math as UM                                  # noqa: E402  frozen v0.1
import atlas_injective as AI                            # noqa: E402
import atlas_reconstruct as AR                          # noqa: E402

MAGIC = b"URDRMTH1"

# op tags
OP_RANK, OP_DET, OP_FDIV, OP_INJ, OP_RECON = 1, 2, 3, 4, 5
# generic result status
ST_OK, ST_REFUSE = 0, 1
# reconstruction status  (mirrors atlas_reconstruct.OK/NOT_INJECTIVE/INCONSISTENT/REFUSE)
RC = {AR.OK: 0, AR.NOT_INJECTIVE: 1, AR.INCONSISTENT: 2, AR.REFUSE: 3}


def _u16(buf, v):
    buf += int(v).to_bytes(2, "big")


def _i64(buf, v):
    buf += (int(v) & ((1 << 64) - 1)).to_bytes(8, "big")   # two's-complement BE


def _name(buf, s):
    b = s.encode("ascii")
    _u16(buf, len(b))
    buf += b


def _ivec(buf, xs):
    _u16(buf, len(xs))
    for x in xs:
        _i64(buf, x)


def _digest(name, op, encode):
    buf = bytearray(MAGIC)
    _name(buf, name)
    buf.append(op)
    encode(buf)
    return hashlib.sha256(bytes(buf)).hexdigest()


# --------------------------------------------------------------- result encoders
def _rank_digest(name, matrix):
    r = UM.rank(matrix)

    def enc(buf):
        if r == "REFUSE":
            buf.append(ST_REFUSE); _i64(buf, 0)
        else:
            buf.append(ST_OK); _i64(buf, r)
    return _digest(name, OP_RANK, enc)


def _det_digest(name, matrix):
    d = UM.determinant(matrix)

    def enc(buf):
        if d == "REFUSE":
            buf.append(ST_REFUSE); _i64(buf, 0)
        else:
            buf.append(ST_OK); _i64(buf, d)
    return _digest(name, OP_DET, enc)


def _fdiv_digest(name, a, b):
    res = UM.floor_divmod(a, b)

    def enc(buf):
        if res == "REFUSE":
            buf.append(ST_REFUSE); _i64(buf, 0); _i64(buf, 0)
        else:
            q, r = res
            buf.append(ST_OK); _i64(buf, q); _i64(buf, r)
    return _digest(name, OP_FDIV, enc)


def _inj_digest(name, charts, n):
    verdict = AI.injective(charts, n)
    witness = AI.collision_witness(charts, n)           # nonzero v with Mv=0, or None

    def enc(buf):
        buf.append(1 if verdict else 0)
        if witness is None:
            buf.append(0); _ivec(buf, [])
        else:
            buf.append(1); _ivec(buf, witness)
    return _digest(name, OP_INJ, enc)


def _recon_digest(name, charts, y, n):
    status, state = AR.solve(charts, y, n)

    def enc(buf):
        buf.append(RC[status])
        if state is None:
            _i64(buf, 0); _ivec(buf, [])
        else:
            num, den = state
            _i64(buf, den); _ivec(buf, num)
    return _digest(name, OP_RECON, enc)


# ------------------------------------------------------------------- the fixtures
_I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
_SING3 = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]              # rank 2, kernel spans one vector
_DEP = [[1, 2, 0], [2, 4, 0], [0, 0, 1]]               # rank 2 (row1 = 2*row0)
_ZERO = [[0, 0], [0, 0]]                                # rank 0
_RECT = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [0, 1, 1]]   # 5x3 full column rank
_DET2 = [[2, 5], [1, 3]]                                # det 1
_DET3 = [[1, 1, 0], [0, 1, 1], [1, 0, 1]]              # det 2
_OVR = [[10 ** 10, 3, 1], [7, 10 ** 10, 2], [1, 4, 10 ** 10]]     # forces i64 overflow -> REFUSE

_N = 3
_FULL = [[[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [1, 1, 0]], [[0, 1, 1]]]   # injective atlas
_DEFICIENT = [[[1, 0, 0], [0, 1, 0]], [[1, 1, 0]]]      # z unobserved (deficient)
_HALF = [[[2, 0], [0, 2]], [[1, 1]]]                    # det-2 subsystem -> half-integer state


def scene_digests():
    """name -> hex SHA-256 digest for every conformance scene (deterministic order)."""
    mFULL = AR.stack(_FULL)
    d = {}
    # -- primitives: rank
    d["rank_identity3"] = _rank_digest("rank_identity3", _I3)
    d["rank_singular3"] = _rank_digest("rank_singular3", _SING3)
    d["rank_dependent"] = _rank_digest("rank_dependent", _DEP)
    d["rank_zero"] = _rank_digest("rank_zero", _ZERO)
    d["rank_rect5x3"] = _rank_digest("rank_rect5x3", _RECT)
    d["rank_overflow"] = _rank_digest("rank_overflow", _OVR)      # REFUSE
    # -- primitives: determinant
    d["det_2x2"] = _det_digest("det_2x2", _DET2)
    d["det_3x3"] = _det_digest("det_3x3", _DET3)
    d["det_singular"] = _det_digest("det_singular", _SING3)       # 0
    d["det_overflow"] = _det_digest("det_overflow", _OVR)         # REFUSE
    # -- primitives: floor_divmod
    d["fdiv_pos"] = _fdiv_digest("fdiv_pos", 7, 2)               # (3, 1)
    d["fdiv_neg"] = _fdiv_digest("fdiv_neg", -7, 2)              # (-4, 1)
    d["fdiv_zero"] = _fdiv_digest("fdiv_zero", 5, 0)            # REFUSE
    # -- injectivity certificate (verdict + exact nullspace collision witness)
    d["inj_full"] = _inj_digest("inj_full", _FULL, _N)          # injective, no witness
    d["inj_deficient"] = _inj_digest("inj_deficient", _DEFICIENT, _N)   # witness v=[0,0,1]
    d["inj_singular3"] = _inj_digest(
        "inj_singular3", [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9]]], _N)     # nontrivial witness
    # -- reconstruction certificate (exact recovered state / typed refusal)
    d["recon_integer"] = _recon_digest("recon_integer", _FULL, AR.matvec(mFULL, [2, -3, 5]), _N)
    yhalf = [v // 2 for v in AR.matvec(AR.stack(_HALF), [1, 1])]
    d["recon_half"] = _recon_digest("recon_half", _HALF, yhalf, 2)      # [1,1]/2
    forged = list(AR.matvec(mFULL, [2, -3, 5])); forged[4] += 1
    d["recon_forged"] = _recon_digest("recon_forged", _FULL, forged, _N)       # INCONSISTENT
    d["recon_deficient"] = _recon_digest(
        "recon_deficient", _DEFICIENT, AR.matvec(AR.stack(_DEFICIENT), [2, -3, 0]), _N)  # NOT_INJECTIVE
    return d


ORDER = [
    "rank_identity3", "rank_singular3", "rank_dependent", "rank_zero", "rank_rect5x3",
    "rank_overflow", "det_2x2", "det_3x3", "det_singular", "det_overflow",
    "fdiv_pos", "fdiv_neg", "fdiv_zero", "inj_full", "inj_deficient", "inj_singular3",
    "recon_integer", "recon_half", "recon_forged", "recon_deficient",
]


if __name__ == "__main__":
    dg = scene_digests()
    for name in ORDER:
        print(f"{name:18s} {dg[name]}")
