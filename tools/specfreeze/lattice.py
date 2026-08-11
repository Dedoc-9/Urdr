# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""lattice — the scoped, coverage-qualified proof-lattice pin (READ-2 step 2).

The proof lattice is `REQUIRES(A, B)` = "severing B reddens A" — logical necessity established by
severance, not imports or calls. Freezing it honestly means keeping THREE claims apart, because they
have different lifetimes and different strengths:

  1. LIVE structural theorem (the strong, cheap one). Proved for ALL 92 relevant law modules despite
     only 79 having enumerated out-edges:  depth(REQUIRES) <= CEILING.  Re-derived every run from the
     import graph and the sealed coverage partition, because `REQUIRES ⊆ transitive-imports` bounds
     the longest dependency chain by the longest import chain. It does NOT re-run the 439s sweep.

  2. SEALED historical snapshot (durable, not live). `lattice_snapshot.json`: at a named commit under
     a named protocol, the 79-law sweep produced these 221 edges (bound by a digest), with its
     eligible/excluded/dynamic partition, longest chain, degree distribution and articulation set.
     Its claim is historical — "this measurement happened" — NOT "this is the current graph." A
     sampled re-check could never prove no unsampled edge changed, so this is not re-derived and not
     asserted as live truth; it is evidence with a commit stamp.

  3. LIVE mechanism conformance (the instrument still bites). A tiny deterministic corpus of positive
     and negative severance cases re-derived each run, plus plants, proving the severance mechanism
     still detects a real edge and rejects a non-edge — WITHOUT pretending to reproduce the whole
     measurement.

What is deliberately NOT gated: the edge count (221), the articulation set, `deg-(heightfield)=28`.
Those are snapshot results that will legitimately drift as coverage and code change; walling them
would freeze the architecture rather than verify it. The stable theorem is narrower and is what this
module gates live: the lattice is severance-derived not declared, its measurement is reproducible
under a sealed protocol, the full REQUIRES depth cannot exceed the ceiling, and the live checker
demonstrably catches a false edge and broken support.
"""
import hashlib
import io
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
for _d in ("terrain", "physics", "netcode"):
    _p = os.path.join(ROOT, "tools", _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)


def load(root=ROOT):
    with io.open(os.path.join(root, "tools", "specfreeze", "lattice_snapshot.json"),
                 encoding="utf-8") as fh:
        return json.load(fh)


# ---- the import graph (static, cheap, the bound REQUIRES lives inside) ---------------------
def _universe(root):
    mods = {}
    for sub in ("terrain", "netcode", "physics"):
        d = os.path.join(root, "tools", sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".py") and not f.startswith("_"):
                mods[f[:-3]] = os.path.join(d, f)
    return mods


def import_graph(root=ROOT):
    files = _universe(root)
    uni = set(files)
    imp = {n: set() for n in files}
    for n, path in files.items():
        try:
            src = io.open(path, encoding="utf-8").read()
        except OSError:
            continue
        for m in re.findall(r"^\s*import\s+(\w+)", src, re.M):
            if m in uni and m != n:
                imp[n].add(m)
        for m in re.findall(r"^\s*from\s+(\w+)\s+import", src, re.M):
            if m in uni and m != n:
                imp[n].add(m)
    return imp


def _transitive(n, imp):
    seen, st = set(), [n]
    while st:
        x = st.pop()
        for y in imp.get(x, ()):
            if y not in seen:
                seen.add(y)
                st.append(y)
    return seen


def _longest_down(imp):
    """longest import chain STARTING at each node (node count), cycle-guarded, memoised on acyclic use."""
    sys.setrecursionlimit(10000)
    memo = {}

    def d(n, seen):
        best = 0
        for m in imp.get(n, ()):
            if m in seen:
                continue
            best = max(best, d(m, seen | {n}))
        return 1 + best
    return {n: d(n, frozenset()) for n in imp}


def _longest_up(imp):
    """longest import chain ENDING at each node (node count) — via the reverse graph."""
    rev = {n: set() for n in imp}
    for n in imp:
        for m in imp[n]:
            rev.setdefault(m, set()).add(n)
        rev.setdefault(n, rev.get(n, set()))

    def u(n, seen):
        best = 0
        for m in rev.get(n, ()):
            if m in seen:
                continue
            best = max(best, u(m, seen | {n}))
        return 1 + best
    return {n: u(n, frozenset()) for n in imp}


def _chain_len(edges):
    """longest path (node count) in the enumerated REQUIRES DAG."""
    adj = {}
    nodes = set()
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        nodes.add(a)
        nodes.add(b)

    def d(n, seen):
        best = 0
        for m in adj.get(n, ()):
            if m in seen:
                continue
            best = max(best, d(m, seen | {n}))
        return 1 + best
    return max((d(n, frozenset()) for n in nodes), default=0)


# ---- CLAIM 1: the live depth-ceiling theorem ----------------------------------------------
def depth_proof(root=ROOT, snap=None):
    """LIVE proof that depth(REQUIRES) <= CEILING for ALL law modules, re-derived from the import
    graph and the sealed coverage partition. Returns (ok, [problems]). Each obligation is mechanical:

      (a) every enumerated REQUIRES edge lies inside transitive imports (severance can't reach
          outside imports, so an edge that does means the snapshot or the graph is inconsistent);
      (b) the enumerated lattice's own longest chain equals the recorded CEILING;
      (c) no excluded or dynamically-wired module lies on any import chain longer than CEILING
          (so a module we did NOT sweep cannot host a deeper REQUIRES chain than we proved);
      (d) every excluded module's import-depth is below CEILING (it cannot START a longer chain);
      (e) the recorded coverage partition still covers every current scene_result law module
          (a new module outside eligible ∪ excluded ∪ post-seal means the coverage is stale);
      (g) every POST-SEAL law carries a reason, names a module that exists, and is not also in
          the sealed partition — the `#[expect]` shape, so a module minted after the seal is
          DECLARED rather than silently uncovered;
      (f) the dynamic modules are withheld from the enumerated (closure-pruned) set.

    THE POST-SEAL REGISTER, and why it is outside the digest. The seal's claim is HISTORICAL — at
    commit 2f13fa2 this sweep produced these edges under this partition — so a module that did not
    exist then cannot honestly be added to it; doing so would rewrite a record to fit the present,
    which is the L64 class. But (e) is right to demand totality over the LIVE tree. So the sealed
    partition stays frozen and post-seal laws are registered live, under exactly the obligations
    that make `excluded` safe: the depth bounds in (c)/(d) apply to them UNCHANGED, so an unswept
    post-seal module still cannot host a REQUIRES chain deeper than the ceiling. What the register
    does NOT claim is that its modules were swept — they were not, and the coverage string says so."""
    snap = load(root) if snap is None else snap
    D = snap["depth_ceiling"]
    elig = set(snap["eligible_laws"])
    excl = set(snap["excluded_laws"])
    dyn = set(snap["dynamic_withheld"])
    post = dict(snap.get("post_seal_laws", {}))
    edges = [tuple(e.split("|")) for e in snap["edges"]]
    imp = import_graph(root)
    out = []
    # (a)
    for a, b in edges:
        if b not in _transitive(a, imp):
            out.append(("edge-outside-imports", f"{a}->{b}"))
            break
    # (b)
    got = _chain_len(edges)
    if got != D:
        out.append(("chain-len", f"enumerated depth {got} != ceiling {D}"))
    # (c) + (d) — the UNSWEPT set, which is `excluded` and `post-seal` alike: neither was measured,
    # so both carry the same obligation not to host a chain the sweep never bounded.
    down = _longest_down(imp)
    up = _longest_up(imp)
    unswept = excl | set(post)
    for X in (unswept | dyn):
        if X in imp and X in unswept and down.get(X, 0) >= D:
            out.append(("unswept-import-depth", f"{X} import-depth {down[X]} >= ceiling {D}"))
        if X in imp and (up.get(X, 0) + down.get(X, 0) - 1) > D:
            out.append(("unswept-on-deep-chain", f"{X} sits on an import chain > {D}"))
    # (e) coverage partition still total over current scene_result laws
    known = elig | excl | set(post)
    for n in sorted(imp):
        try:
            m = __import__(n)
        except Exception:
            continue
        if hasattr(m, "scene_result") and hasattr(m, "SCENES") and n not in known:
            out.append(("coverage-stale", f"{n} has scene_result but is in neither eligible nor "
                                          f"excluded nor post-seal"))
    # (g) the post-seal register is DECLARED, not a parking lot
    for n, why in sorted(post.items()):
        if n in elig or n in excl:
            out.append(("post-seal-double-counted", f"{n} is already in the sealed partition"))
        if n not in imp:
            out.append(("post-seal-unknown", f"{n} names no module in the tree"))
        if not isinstance(why, str) or len(why.strip()) < 20:
            out.append(("post-seal-unreasoned", f"{n} carries no reason"))
    # (f)
    for X in dyn:
        if X in elig:
            out.append(("dynamic-not-withheld", X))
    return (not out), out


# ---- CLAIM 2: the sealed historical snapshot ---------------------------------------------
def _combined_digest(snap):
    """The seal binds the edges AND the coverage partition, so a changed eligible/excluded/dynamic
    set presented under the old digest is caught, not just a changed edge."""
    payload = "\x00".join(["\n".join(sorted(snap["edges"])),
                           "\n".join(sorted(snap["eligible_laws"])),
                           "\n".join(sorted(snap["excluded_laws"].keys())),
                           "\n".join(sorted(snap["dynamic_withheld"].keys()))])
    return hashlib.sha256(payload.encode()).hexdigest()


def snapshot_integrity(root=ROOT, snap=None):
    """Recompute the edge digest and confirm the sealed metadata is complete. This proves the
    HISTORICAL record is intact; it makes no claim that the 221 edges are still the live graph."""
    snap = load(root) if snap is None else snap
    out = []
    dig = _combined_digest(snap)
    if dig != snap["edge_digest"]:
        out.append(("digest", f"recomputed {dig[:12]} != sealed {snap['edge_digest'][:12]}"))
    if len(snap["edges"]) != snap["n_edges"]:
        out.append(("count", f"{len(snap['edges'])} != {snap['n_edges']}"))
    for k in ("source_commit", "algorithm", "eligible_laws", "excluded_laws",
              "longest_chain", "articulation_nodes", "monotonicity", "coverage"):
        if not snap.get(k):
            out.append(("missing-field", k))
    return (not out), out


# ---- CLAIM 3: live mechanism conformance -------------------------------------------------
#: (target_module, atom, law_module, expected_REQUIRES). Positive = severing the atom must move the
#: law; negative = it must not. Pinned; re-derived by real severance every run.
CONFORMANCE = (
    ("storecost", "serialize", "persist", True),      # direct requirement
    ("glide", "glide_cells", "resurrect", True),       # deep transitive requirement
    ("persist", "checkpoint", "drive", False),         # cross-family non-edge
    ("rannull", "regional_record", "glide", False),    # a foundational law requires nothing upward
)


class _Sev:
    def __call__(self, *a, **k):
        raise RuntimeError("LATTICE-SEVER")


def _law(mod):
    ks = mod.SCENES
    ks = ks if isinstance(ks, (tuple, list)) else list(ks)
    return tuple(mod.scene_result(k) for k in ks)


def _moves(target, atom, lawmod, identity_wide=False):
    """Sever target.atom (optionally every repo-module alias of it) and report whether lawmod's
    scene_result moves. Restores in finally."""
    tm = __import__(target)
    lm = __import__(lawmod)
    base = _law(lm)
    real = getattr(tm, atom)
    binds = [(tm, atom)]
    if identity_wide:
        for n in list(sys.modules.values()):
            f = getattr(n, "__file__", None)
            if f and os.path.abspath(f).startswith(os.path.join(ROOT, "tools")):
                for b in list(vars(n).keys()):
                    if not b.startswith("__"):
                        try:
                            if getattr(n, b) is real:
                                binds.append((n, b))
                        except Exception:
                            pass
    sent = _Sev()
    for (mm, bb) in binds:
        setattr(mm, bb, sent)
    try:
        try:
            return _law(lm) != base
        except Exception:
            return True
    finally:
        for (mm, bb) in binds:
            setattr(mm, bb, real)


def conformance(root=ROOT):
    """Every pinned case's severance reproduces its expected REQUIRES verdict, and the corpus is
    non-vacuous (contains both a positive and a negative case)."""
    out = []
    pos = neg = 0
    for target, atom, lawmod, expect in CONFORMANCE:
        got = _moves(target, atom, lawmod)
        if got != expect:
            out.append(("wrong-verdict", f"{target}.{atom}->{lawmod} got {got} want {expect}"))
        pos += expect
        neg += (not expect)
    if pos == 0 or neg == 0:
        out.append(("vacuous-corpus", f"pos={pos} neg={neg}"))
    return (not out), out


def plants_bite(root=ROOT):
    """RED-FIRST: the instrument must catch each failure the pin exists to exclude.
      (1) an INVENTED edge   — a non-edge severance falsely read as a requirement;
      (2) a REMOVED edge     — a real requirement severance falsely read as independent;
      (3) a DYNAMIC module falsely declared closure-safe — proof (f) reddens;
      (4) a CHANGED coverage set under the sealed digest — integrity reddens;
      (5) a WRONG depth ceiling — enumerated depth != ceiling, proof (b) reddens;
      (6) a DEEP module wrongly excluded (unswept) — it can host a chain > ceiling, proof (c/d)
          reddens;
      (7) the identity-wide alias control AGREES with setattr-only on a real edge (S8)."""
    snap = load(root)
    out = []
    # (1) invented edge: the pinned NEG case must read False
    t, a, lm, _ = CONFORMANCE[2]
    if _moves(t, a, lm) is not False:
        out.append(("neg-not-negative", f"{t}.{a}->{lm}"))
    # (2) removed edge: the pinned POS case must read True (severance is doing the work)
    t, a, lm, _ = CONFORMANCE[0]
    if _moves(t, a, lm) is not True:
        out.append(("pos-not-positive", f"{t}.{a}->{lm}"))
    # (3) dynamic falsely closure-safe -> proof (f): a module still declared dynamic yet admitted to
    #     the closure-pruned eligible set is the contradiction the check exists to catch.
    bad = dict(snap)
    bad["eligible_laws"] = sorted(set(snap["eligible_laws"]) | set(snap["dynamic_withheld"]))
    if depth_proof(root, bad)[0]:
        out.append(("dynamic-plant-survived",))
    # (4) changed coverage under the sealed digest -> integrity (add a law to eligible, keep digest)
    bad2 = dict(snap)
    bad2["eligible_laws"] = sorted(set(snap["eligible_laws"]) | {"heightfield"})
    if snapshot_integrity(root, bad2)[0]:
        out.append(("coverage-digest-plant-survived",))
    # (5) wrong depth ceiling -> proof (b)
    bad3 = dict(snap)
    bad3["depth_ceiling"] = snap["depth_ceiling"] - 1
    if depth_proof(root, bad3)[0]:
        out.append(("ceiling-plant-survived",))
    # (6) a deep module wrongly moved to excluded (unswept) -> proof (c/d)
    bad4 = dict(snap)
    bad4["excluded_laws"] = dict(snap["excluded_laws"]); bad4["excluded_laws"]["meshsession"] = 0.0
    bad4["eligible_laws"] = [n for n in snap["eligible_laws"] if n != "meshsession"]
    if depth_proof(root, bad4)[0]:
        out.append(("deep-excluded-plant-survived",))
    # (7) alias control agrees on a real edge (S8)
    t, a, lm, _ = CONFORMANCE[0]
    if _moves(t, a, lm, identity_wide=False) != _moves(t, a, lm, identity_wide=True):
        out.append(("alias-control-disagrees", f"{t}.{a}->{lm}"))
    # (8) the POST-SEAL register is not a parking lot: a DEEP module moved there is still caught by
    #     (c)/(d), so registering something instead of sweeping it buys nothing.
    bad5 = dict(snap)
    bad5["eligible_laws"] = [n for n in snap["eligible_laws"] if n != "meshsession"]
    bad5["post_seal_laws"] = dict(snap.get("post_seal_laws", {}),
                                  meshsession="a deep module parked rather than swept")
    if depth_proof(root, bad5)[0]:
        out.append(("post-seal-depth-plant-survived",))
    # (9) an UNREASONED post-seal entry reddens — `#[expect]`, not `#[allow]`
    bad6 = dict(snap)
    bad6["post_seal_laws"] = dict(snap.get("post_seal_laws", {}), contact="")
    if depth_proof(root, bad6)[0]:
        out.append(("post-seal-unreasoned-plant-survived",))
    # (10) an entry naming a module that does not exist is STALE, not coverage
    bad7 = dict(snap)
    bad7["post_seal_laws"] = dict(snap.get("post_seal_laws", {}),
                                  ghostmodule="a module that was deleted after being registered")
    if depth_proof(root, bad7)[0]:
        out.append(("post-seal-unknown-plant-survived",))
    # (11) NON-VACUITY of the register itself: dropping it entirely must redden (e), or the whole
    #      mechanism is decoration and the coverage check was already total without it.
    bad8 = dict(snap)
    bad8["post_seal_laws"] = {}
    if depth_proof(root, bad8)[0]:
        out.append(("post-seal-register-not-load-bearing",))
    return (not out), out
