# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""Exact rational vector -- dimension-agnostic (the same code is 2D and 3D).

A Vec is a tuple of `rational.Q` components. Add / sub / scale / dot are exact
over Z; i64 overflow refuses through the underlying Q. This is the substrate for
n-dimensional dynamics: one implementation, any dimension. No float, ever."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rational import Q, Z                              # noqa: E402


class Vec:
    __slots__ = ("c",)

    def __init__(self, comps):
        self.c = tuple(comps)

    def dim(self):
        return len(self.c)

    def __add__(self, o):
        return Vec(a + b for a, b in zip(self.c, o.c))

    def __sub__(self, o):
        return Vec(a - b for a, b in zip(self.c, o.c))

    def scale(self, k):
        return Vec(a * k for a in self.c)

    def dot(self, o):
        acc = Z(0)
        for a, b in zip(self.c, o.c):
            acc = acc + a * b
        return acc

    def __eq__(self, o):
        return self.c == o.c

    def __hash__(self):
        return hash(self.c)

    def __repr__(self):
        return "Vec[" + ", ".join(f"{a.n}/{a.d}" for a in self.c) + "]"


def vec(*ints):
    """A Vec from plain integers (each becomes an exact rational)."""
    return Vec([Z(i) for i in ints])


def zero(dim):
    return Vec([Z(0)] * dim)
