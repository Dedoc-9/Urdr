# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""tellegen — Tellegen orthogonality of integer potential/flow pairs on a shared digraph.

A detector under D17 — the second constraint instrument of the D19 abductive-gauntlet
contract (`spec/D19-abductive-gauntlet.md` §6 lineage row, 1952), and the first
graph-theoretic detector in the library.

    𝒟_T = (Dom, Inv, W, ~, R)

  * Dom — a directed multigraph (n ≥ 1 nodes, m ≥ 1 edges as (tail, head) integer pairs;
    parallel edges and self-loops admitted) together with an integer POTENTIAL p on nodes
    and an integer FLOW i on edges that is CONSERVATIVE: at every node, inflow equals
    outflow exactly (KCL). Membership is decided in exact integer arithmetic.
  * Inv — the Tellegen pairing `S = Σₖ vₖ·iₖ ∈ ℤ` with branch voltages `vₖ = p[headₖ] −
    p[tailₖ]`. Tellegen's theorem (B. D. H. Tellegen, "A general network theorem, with
    applications", Philips Research Reports 7, 1952): on Dom, S = 0 for ANY potential and
    ANY conservative flow — independently chosen, no constitutive relation between them.
    The one-line reason: Σₖ (p[h]−p[t])·iₖ regroups to Σₙ p[n]·(inflow(n) − outflow(n)),
    and every bracket is zero exactly when KCL holds. This is what distinguishes it from
    KCL itself: KCL constrains one assignment on one network; Tellegen constrains EVERY
    admissible pair the topology can carry.
  * W — the per-edge product list `(k, vₖ·iₖ)`; anyone can recount; the sum IS the pairing.
  * ~ — declared invariance class: global potential shift `p → p + c` (gauge — voltages
    unchanged); simultaneous permutation of (edges, flow); single-edge reorientation
    `(t,h) → (h,t)` with `iₖ → −iₖ` (the product is unchanged). All exact, all tested.
  * R — `TELL-REFUSE`, total: non-integer input (bool included), an edge naming a node that
    does not exist, length mismatches (p vs nodes, i vs edges), and a non-conservative flow
    — refused NAMING the first violating node and its exact net imbalance, never summed
    over silently.

Honest scope: the detector certifies objects handed to it — a (graph, potential, flow)
triple — exactly. Any story about "mapping a codebase's pipelines to circuits" is a
consumer aspiration (DECLARED), not this module. S ≡ 0 on all of Dom by theorem, so as a
separator the invariant is maximally PARTIAL — its discriminating power is the boundary:
conservative pairs pair to zero with a recountable witness; leaky flows are refused with
the leak named. Grade: MEASURED (reference) once gated; cross-placement not claimed."""
import hashlib
import os as _os

MAGIC = b"URDRTL01"
_HERE = _os.path.dirname(_os.path.abspath(__file__))


class TellegenError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def _refuse(message):
    raise TellegenError("TELL-REFUSE", message)


def _is_int(v):
    return type(v) is int                       # bool is a subclass of int — excluded on purpose


def check_domain(n, edges, p, i):
    """Membership in Dom — every violation is a typed `TELL-REFUSE`, never a wrong answer.
    A KCL violation is refused NAMING the first bad node and its exact net imbalance."""
    if not (_is_int(n) and n >= 1):
        _refuse(f"node count must be a positive int, got {n!r}")
    if not isinstance(edges, (list, tuple)) or len(edges) < 1:
        _refuse("a network needs at least one edge")
    for k, e in enumerate(edges):
        if not (isinstance(e, tuple) and len(e) == 2 and _is_int(e[0]) and _is_int(e[1])):
            _refuse(f"edge {k} is not an integer (tail, head) pair: {e!r}")
        if not (0 <= e[0] < n and 0 <= e[1] < n):
            _refuse(f"edge {k} names a node outside 0..{n-1}: {e!r}")
    if not (isinstance(p, (list, tuple)) and len(p) == n and all(_is_int(x) for x in p)):
        _refuse(f"potential must be {n} integers")
    if not (isinstance(i, (list, tuple)) and len(i) == len(edges) and all(_is_int(x) for x in i)):
        _refuse(f"flow must be {len(edges)} integers")
    net = [0] * n
    for k, (t, h) in enumerate(edges):
        net[t] -= i[k]
        net[h] += i[k]
    for node, d in enumerate(net):
        if d != 0:
            _refuse(f"flow is not conservative: KCL violated at node {node} (net {d:+d})")


def voltages(edges, p):
    """Branch voltages from the potential: `vₖ = p[head] − p[tail]` (KVL by construction)."""
    return [p[h] - p[t] for (t, h) in edges]


def products(n, edges, p, i, oriented=True):
    """The witness W: the per-edge product list `(k, vₖ·iₖ)`. `oriented=False` is THE
    DEFECT — it takes voltages min-first (`p[max(t,h)] − p[min(t,h)]`), losing edge
    orientation, so any scene with a backward edge pairs to a nonzero sum."""
    check_domain(n, edges, p, i)
    out = []
    for k, (t, h) in enumerate(edges):
        v = (p[h] - p[t]) if oriented else (p[max(t, h)] - p[min(t, h)])
        out.append((k, v * i[k]))
    return out


def pairing(n, edges, p, i):
    """The invariant: the Tellegen pairing `S ∈ ℤ` — 0 on all of Dom, by the 1952 theorem."""
    return sum(x for (_k, x) in products(n, edges, p, i))


def pairing_defect(n, edges, p, i):
    """THE DEFECT (D17 non-invariance): the orientation-blind pairing — must be nonzero on
    every pinned scene that has a backward edge (the gate proves it can redden)."""
    return sum(x for (_k, x) in products(n, edges, p, i, oriented=False))


def check_witness(n, edges, p, i, prods):
    """Independent recount: the witness verifies iff recomputation reproduces it exactly."""
    try:
        return list(prods) == products(n, edges, p, i)
    except TellegenError:
        return False


def witness_digest(n, edges, p, i, prods=None):
    """SHA-256 over MAGIC | n | m | edges | potential | flow | S | products —
    independently recomputable from the object."""
    if prods is None:
        prods = products(n, edges, p, i)
    h = hashlib.sha256()
    h.update(MAGIC)
    h.update(f"{n}|{len(edges)}".encode())
    for (t, hd) in edges:
        h.update(f"|{t},{hd}".encode())
    h.update(b"|p:")
    h.update(",".join(str(x) for x in p).encode())
    h.update(b"|i:")
    h.update(",".join(str(x) for x in i).encode())
    h.update(f"|S:{sum(x for (_k, x) in prods)}".encode())
    for (k, x) in prods:
        h.update(f"|{k}:{x}".encode())
    return h.hexdigest()


# ---- scenarios (pinned by the gate) -----------------------------------------------------
_BRIDGE_EDGES = ((0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0))   # note (3,0): a backward edge


def bridge6():
    """The Wheatstone-bridge digraph (4 nodes, 6 branches, return edge 3→0): superposed
    loop flows i = (3,2,1,2,3,5) — conservative at every node — against an arbitrary
    potential p = (7, 3, −2, 11). S = 0 by the theorem; the witness recounts it."""
    return 4, _BRIDGE_EDGES, (7, 3, -2, 11), (3, 2, 1, 2, 3, 5)


def bridge6_alt():
    """The SAME topology with an independently chosen pair — p = (0, 5, −4, 2) against the
    circulation i = (5, 0, 1, 4, 1, 5). Tellegen's content is exactly this independence:
    any admissible pair on the shared topology pairs to zero."""
    return 4, _BRIDGE_EDGES, (0, 5, -4, 2), (5, 0, 1, 4, 1, 5)


def cycle5():
    """A directed 5-cycle with uniform circulation i = 7: S telescopes to zero for any
    potential (here p = (13, −4, 0, 8, −11))."""
    edges = tuple((k, (k + 1) % 5) for k in range(5))
    return 5, edges, (13, -4, 0, 8, -11), (7, 7, 7, 7, 7)


def parallel_loop():
    """A 2-node multigraph with parallel edges both ways AND a self-loop (documented as
    admitted: a self-loop has v = 0 and nets zero at its node): p = (6, −3),
    i = (2, 3, 4, 1, 9). Exercises the multigraph corner of Dom."""
    edges = ((0, 1), (0, 1), (1, 0), (1, 0), (1, 1))
    return 2, edges, (6, -3), (2, 3, 4, 1, 9)


def universality_grid():
    """The theorem-backed property grid: THREE independent potentials × THREE independent
    conservative flows on the bridge topology — all NINE cross-pairings must be zero.
    This is the universal-constraint content that separates Tellegen from KCL."""
    potentials = [(7, 3, -2, 11), (0, 5, -4, 2), (1, 0, 0, 0)]
    flows = [(3, 2, 1, 2, 3, 5), (5, 0, 1, 4, 1, 5), (0, 1, 0, 0, 1, 1)]
    return 4, _BRIDGE_EDGES, potentials, flows


SCENES = {
    "bridge6": bridge6,
    "bridge6_alt": bridge6_alt,
    "cycle5": cycle5,
    "parallel_loop": parallel_loop,
}


def golden(name):
    """The pinned `(S, digest)` for a named scene from `conformance_tellegen.txt`."""
    with open(_os.path.join(_HERE, "conformance_tellegen.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, s, dig = ln.split()
                if nm == name:
                    return int(s), dig
    raise TellegenError("TELL-REFUSE", f"no golden named {name!r}")
