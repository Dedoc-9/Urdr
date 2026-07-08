#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""world_host -- the smallest shared-world runtime REFERENCE (Milestone 7, Step 1).

This is an executable SPECIFICATION of the host enforcement loop, not a production
runtime. It CONSUMES the measured invariants (it does not extend them):

  * authority = the kernel's content digest  (urdr.canon.digest = canon -> SHA-256, D1 s7);
    the very digest the reference and urdr-core-rs already agree on (D8 conformance).
  * admissible observer = a COVERING (injective) chart atlas  (D10 / Milestone 6: an atlas
    determines the state iff its charts span the coordinates).
  * a frame is admitted iff it reconstructs to the authoritative state  (D10 / Milestone 6.5:
    observation is bound to the authenticated digest -- view-laundering is refused).

NO networking, NO graphics, NO optimization, NO concurrency (those are Steps 3-5). This file
answers exactly one question: can multiple observers render DIFFERENT images of one
authoritative world while every ADMITTED frame stays bound to the SAME authority digest, and
is a laundered or inadmissible frame REFUSED (not repaired)?

`the runtime consumes the theorem; it does not re-prove it`.
"""
from urdr import values as V, canon as C


def _state(vec):
    """A world state is an Urdr list value -> its digest is the kernel's content digest."""
    return V.ListV([V.Int(int(n)) for n in vec])


def digest(vec):
    """Authority = the SAME canon->SHA-256 the kernel and the Rust placement agree on."""
    return C.digest(_state(vec))


class Chart:
    """An axis-selection observer chart: it observes a subset of the state's coordinates."""
    def __init__(self, axes):
        self.axes = list(axes)

    def project(self, vec):
        return [vec[i] for i in self.axes]


class Atlas:
    """A chart family (an observer). Covering iff every axis is observed by some chart
    (the injectivity / trivial-kernel condition for axis-selection charts, D10 s2)."""
    def __init__(self, charts):
        self.charts = list(charts)

    def covers(self, n):
        seen = set()
        for ch in self.charts:
            seen.update(ch.axes)
        return all(a in seen for a in range(n))

    def image(self, vec):
        """The rendered frame = concatenation of every chart's projection."""
        out = []
        for ch in self.charts:
            out.extend(ch.project(vec))
        return out

    def recon(self, image, n):
        """Reconstruct the source state from a frame (needs a covering atlas). Returns the
        recovered vector, or None if the atlas cannot cover axis a (inadmissible)."""
        pos, axis_at = 0, {}
        for ch in self.charts:
            for a in ch.axes:
                if a not in axis_at:      # first chart to observe axis a fixes its position
                    axis_at[a] = pos
                pos += 1
        if any(a not in axis_at for a in range(n)):
            return None
        return [image[axis_at[a]] for a in range(n)]


class WorldHost:
    """Owns the authoritative world state and its digest. Admits/refuses observer frames."""
    def __init__(self, initial_vec):
        self.n = len(initial_vec)
        self.state = list(initial_vec)
        self.anchor = digest(self.state)      # the one authority every observer must agree on

    def admit(self, atlas, image):
        """A frame is ADMITTED iff (1) its atlas is admissible (covering / injective) AND
        (2) it reconstructs to the authoritative state (digest binds to the anchor).
        Otherwise REFUSED -- never repaired. Returns (verdict, reason)."""
        if not atlas.covers(self.n):
            return ("REFUSE", "inadmissible atlas: non-covering (kernel nontrivial)")
        src = atlas.recon(image, self.n)
        if src is None:
            return ("REFUSE", "inadmissible atlas: cannot reconstruct")
        if digest(src) != self.anchor:
            return ("REFUSE", "view laundering: frame source digest != authority")
        return ("ADMIT", "bound to authority")
