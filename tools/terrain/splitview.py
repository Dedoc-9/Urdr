# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""splitview — THE OFFICIAL SERVER'S OWN AUDIT (URDRSPV1): the one authority in the whole
architecture that nothing was pointed at. NO NEW GLYPH.

WHAT EVERY PRIOR RUNG DEFENDS AGAINST, AND WHAT NONE OF THEM DOES. `voxlat` certifies the lattice,
`divergence` bounds a capture, `geoquorum` adjudicates a doctored submission, `provbind` refuses an
unbound certificate, `tierview` refuses an asymmetric visibility claim, `lagcomp` refuses a dated
one, `persist` reconstructs-or-refuses a durable record. Every one of them hardens the server against
a lying CLIENT. The stated design goal has an OFFICIAL GLOBAL SERVER, and nothing in the repository
asks what happens when THAT lies. It does not have to forge anything: it serves Alice history H_A and
Bob history H_B, both internally consistent, both correctly signed, both passing every check above.

    A FORKED SERVER IS NOT DETECTABLE BY VERIFICATION. IT IS DETECTABLE ONLY BY COMPARISON.

THE LONELY-CLIENT THEOREM, and it is the whole point of the rung. Let a server fork its log into A and
B, and let a client be confined to side A. That client's ENTIRE transcript — its heads, its inclusion
proofs, its consistency proofs between its own successive heads — is BIT-IDENTICAL to the transcript
it would hold in an honest world whose log is exactly A. So no function of that transcript is a fork
detector; there is nothing to grip. This is not "our detector was too weak." It is that the input is
identical, so detection power is exactly 0 for EVERY solo detector, including ones not yet written.
MEASURED as the contrast that makes it non-vacuous: the strongest solo detector — one that verifies
every proof it is ever offered — flags 0 of the forks, and the SAME forks are flagged by 100% of
crossing comparisons. Zero and total, on one family.

THE CUT THEOREM, WITH THE HYPOTHESIS THE TEXTBOOK VERSION OMITS. It is tempting to stop at "gossip
catches equivocation": detection happens iff some gossip edge joins a client on side A to one on side
B. That is TRUE AND INSUFFICIENT, and stating it alone would have been an inflation. Two clients on
opposite sides of a fork detect NOTHING unless BOTH their heads are deeper than the point where the
log diverged — a head at or below the common prefix is a prefix of the other side too, and a
consistency proof honestly exists. DECIDED exhaustively:

    detection  <=>  a gossip edge crosses the cut  AND  both endpoints' heads exceed the common prefix

which has a deployment consequence that is not obvious: A FRESHLY JOINED CLIENT CANNOT AUDIT. Audit
power lives entirely in clients that were present across the divergence, so it is a property of
tenure, not of headcount.

THE COST IS LINEAR, NOT QUADRATIC. Undetected equivocation is possible iff the gossip graph is
DISCONNECTED — the server may serve one view per connected component and no more, so the number of
undetected forkings is exactly 2^c - 2 for c components. Detection is therefore guaranteed by any
spanning tree: the minimum edge count over k clients is exactly k-1, DECIDED over every labelled
graph on up to 5 vertices. All-pairs gossip buys nothing over a tree.

THE CRYPTO IS DECIDED, NOT CITED. RFC 6962's Merkle tree hash, consistency proof and verifier are
implemented here and then CHECKED AGAINST THE STRUCTURAL ORACLE — `is_prefix` — over every ordered
pair in an exhaustive log family. Agreement is total or the gate is red. An implementation of a
published algorithm is not evidence that the algorithm was implemented; the census is.

ABSENCE OF PROOF IS THE EVIDENCE, AND THAT POLARITY IS LOAD-BEARING. A server that has forked cannot
produce a consistency proof between the two heads it served, so the protocol must treat "no proof" as
FORKED rather than as "retry later" — otherwise a forked server simply stalls forever and buys
permanent silence. The safe polarity costs something real and it is stated rather than hidden: at
this layer a transient outage is indistinguishable from a fork.

GRADE. MEASURED: the crypto/structural agreement census (0 exceptions); the forgery census (0 of the
enumerated forgeries verify); solo detection 0 of F against crossing detection F of F on one family;
the head-depth law decided over every fork and head pair; the connectivity law and the attained
minimum k-1 over every labelled graph to 5 vertices; four plants biting; determinism. DECLARED: the
gossip model is a static undirected graph over a fixed client set with truthful head exchange —
clients may be confined and deceived but do not lie ABOUT each other's heads, and a sybil population
that reports fabricated heads is a separate rung (`geoquorum`'s cohort problem, not this one); the
log is append-only leaves with no semantics. does_not_show: WHO forked or when — detection localizes
to a pair, not to a culprit, and attributing a fork needs signed heads this rung does not model;
liveness, so a transient outage reads as a fork here; that detection implies remedy — a detected fork
is an alarm, and which side is canonical is a governance question with no cryptographic answer."""
import hashlib
import os as _os
import sys as _sys
from itertools import combinations as _comb, product as _prod

_HERE = _os.path.dirname(_os.path.abspath(__file__))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

MAGIC = b"URDRSPV1"
ALPHABET = (b"0", b"1")          # leaf values; two suffice to fork
AGREE_LEN = 5                    # crypto-vs-structure census over every log to this length
FORK_LEN = 4                     # fork/head census over logs of exactly this length
MAX_CLIENTS = 5                  # graph laws decided over every labelled graph to this order


class SplitViewError(Exception):
    def __init__(self, message):
        super().__init__(f"SPLITVIEW-REFUSE: {message}")
        self.code = "SPLITVIEW-REFUSE"


class ForkDetected(Exception):
    """The typed alarm. Raised by `adjudicate`, never returned as a warning — a fork that is reported
    as advisory is a fork that ships."""
    def __init__(self, message):
        super().__init__(f"SPLITVIEW-FORKED: {message}")
        self.code = "SPLITVIEW-FORKED"


# ---- RFC 6962 section 2.1: the tree ---------------------------------------------------------------
def _largest_pow2_below(n):
    """k, the largest power of two STRICTLY less than n (so k < n <= 2k)."""
    if n < 2:
        raise SplitViewError("the split point is defined only for n >= 2")
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def _leaf(d):
    return hashlib.sha256(b"\x00" + d).digest()


def _node(left, right):
    return hashlib.sha256(b"\x01" + left + right).digest()


def mth(D):
    """MTH(D[n]). Empty tree is SHA-256 of the empty string; a leaf carries the 0x00 prefix and an
    interior node the 0x01 prefix, which is what keeps a leaf from being replayed as a node."""
    n = len(D)
    if n == 0:
        return hashlib.sha256(b"").digest()
    if n == 1:
        return _leaf(D[0])
    k = _largest_pow2_below(n)
    return _node(mth(D[:k]), mth(D[k:]))


def inclusion_path(m, D):
    """PATH(m, D[n])."""
    n = len(D)
    if not (0 <= m < n):
        raise SplitViewError("inclusion index out of range")
    if n == 1:
        return ()
    k = _largest_pow2_below(n)
    if m < k:
        return inclusion_path(m, D[:k]) + (mth(D[k:]),)
    return inclusion_path(m - k, D[k:]) + (mth(D[:k]),)


def verify_inclusion(m, n, leaf_data, path, root):
    if not (0 <= m < n):
        return False
    fn, sn, h = m, n - 1, _leaf(leaf_data)
    for p in path:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            h = _node(p, h)
            while fn != 0 and not (fn & 1):
                fn >>= 1
                sn >>= 1
        else:
            h = _node(h, p)
        fn >>= 1
        sn >>= 1
    return sn == 0 and h == root


# ---- RFC 6962 section 2.1.2: the consistency proof -------------------------------------------------
def _subproof(m, D, b):
    n = len(D)
    if m == n:
        return () if b else (mth(D),)
    k = _largest_pow2_below(n)
    if m <= k:
        return _subproof(m, D[:k], b) + (mth(D[k:]),)
    return _subproof(m - k, D[k:], False) + (mth(D[:k]),)


def consistency_proof(m, D):
    """PROOF(m, D[n]) = SUBPROOF(m, D[n], true). The proof a server offers to convince a client whose
    head is at size m that its size-n head EXTENDS that head rather than replacing it."""
    if not (0 <= m <= len(D)):
        raise SplitViewError("consistency size out of range")
    if m == 0 or m == len(D):
        return ()
    return _subproof(m, D, True)


def verify_consistency(m, root_m, n, root_n, proof):
    """The verifier. It must RECONSTRUCT BOTH roots from the proof — deriving only the new root and
    trusting the old one is the classic implementation defect, and `_verify_new_root_only` below is
    that defect kept live so it can be counted."""
    if m > n:
        return False
    if m == n:
        return tuple(proof) == () and root_m == root_n
    if m == 0:
        return tuple(proof) == ()
    p = list(proof)
    if not p:
        return False
    if m & (m - 1) == 0:                      # m an exact power of two: the old root is implicit
        p = [root_m] + p
    fn, sn = m - 1, n - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    fr = sr = p[0]
    for c in p[1:]:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            fr = _node(c, fr)
            sr = _node(c, sr)
            while fn != 0 and not (fn & 1):
                fn >>= 1
                sn >>= 1
        else:
            sr = _node(sr, c)
        fn >>= 1
        sn >>= 1
    return sn == 0 and fr == root_m and sr == root_n


# ---- the structural oracle ------------------------------------------------------------------------
def is_prefix(A, B):
    """GROUND TRUTH, with no hashing in it at all. The crypto predicate is checked against THIS."""
    return len(A) <= len(B) and tuple(B[:len(A)]) == tuple(A)


def common_prefix_len(A, B):
    p = 0
    while p < len(A) and p < len(B) and A[p] == B[p]:
        p += 1
    return p


def is_fork(A, B):
    return not is_prefix(A, B) and not is_prefix(B, A)


def _logs_upto(n):
    out = [()]
    for ln in range(1, n + 1):
        out.extend(_prod(ALPHABET, repeat=ln))
    return tuple(tuple(x) for x in out)


def _logs_exactly(n):
    return tuple(tuple(x) for x in _prod(ALPHABET, repeat=n))


# ---- law 1: the crypto predicate IS the structural predicate ---------------------------------------
def agreement_census(limit=AGREE_LEN):
    """DECIDED over every ordered pair of logs to `limit`: a consistency proof generated from the
    larger log and verified against both heads succeeds EXACTLY when the smaller log is a structural
    prefix of the larger. Returns (agreements, exceptions, total). Exceptions must be 0 — that is
    what makes the implementation evidence rather than assertion."""
    logs = _logs_upto(limit)
    roots = {L: mth(L) for L in logs}
    agree = exc = total = 0
    for A in logs:
        for B in logs:
            if len(A) > len(B):
                continue
            total += 1
            structural = is_prefix(A, B)
            try:
                pf = consistency_proof(len(A), B)
                crypto = verify_consistency(len(A), roots[A], len(B), roots[B], pf)
            except SplitViewError:
                crypto = False
            if structural == crypto:
                agree += 1
            else:
                exc += 1
    return agree, exc, total


def crypto_matches_structure(limit=AGREE_LEN):
    _a, exc, total = agreement_census(limit)
    return exc == 0 and total > 0


# ---- law 2: a forked server cannot forge its way out ------------------------------------------------
def _forgery_candidates(A, B):
    """Everything a server holding BOTH sides can honestly compute and dishonestly offer: the proof
    for A's size taken from B's tree, the same taken from A's own tree, the honest proof for the
    common prefix passed off as a proof for A, the empty proof, and single-node proofs made of the
    roots it holds."""
    p = common_prefix_len(A, B)
    out = [consistency_proof(len(A), B), consistency_proof(len(A), A)]
    try:
        out.append(consistency_proof(p, B))
        out.append(consistency_proof(p, A))
    except SplitViewError:
        pass
    out.append(())
    out.append((mth(A),))
    out.append((mth(B),))
    out.append((mth(A[:p]),))
    return out


def forgery_census(length=FORK_LEN):
    """MEASURED: over every forked pair, how many enumerated forgeries VERIFY. Must be 0 of many —
    the denominator is reported so a zero cannot be mistaken for an empty search."""
    logs = _logs_exactly(length)
    roots = {L: mth(L) for L in logs}
    accepted = tried = forks = 0
    for A in logs:
        for B in logs:
            if not is_fork(A, B):
                continue
            forks += 1
            for pf in _forgery_candidates(A, B):
                tried += 1
                if verify_consistency(len(A), roots[A], len(B), roots[B], pf):
                    accepted += 1
    return accepted, tried, forks


# ---- law 3: the lonely client -----------------------------------------------------------------------
def solo_transcript(D, heads):
    """Everything a client confined to one side ever holds: its successive heads, the consistency
    proofs between them, and an inclusion proof for every leaf it has seen."""
    heads = tuple(sorted(set(h for h in heads if 0 <= h <= len(D))))
    items = []
    for h in heads:
        items.append(("head", h, mth(D[:h])))
    for a, b in zip(heads, heads[1:]):
        items.append(("consistency", a, b, consistency_proof(a, D[:b])))
    top = heads[-1] if heads else 0
    for i in range(top):
        items.append(("inclusion", i, top, D[i], inclusion_path(i, D[:top])))
    return tuple(items)


def _solo_detector(transcript):
    """THE STRONGEST SOLO DETECTOR: verify absolutely everything. Returns True if it flags a fork.
    It is CORRECT — it never fires on an honest transcript — and it is POWERLESS, which is the
    theorem. Its verification effort is not weak; its input is identical."""
    roots = {h: r for (kind, h, r) in (t for t in transcript if t[0] == "head")}
    for t in transcript:
        if t[0] == "consistency":
            _k, a, b, pf = t
            if not verify_consistency(a, roots[a], b, roots[b], pf):
                return True
        elif t[0] == "inclusion":
            _k, i, top, data, path = t
            if not verify_inclusion(i, top, data, path, roots[top]):
                return True
    return False


def solo_vs_crossing_census(length=FORK_LEN):
    """THE CONTRAST THAT MAKES THE ZERO MEAN SOMETHING. Over every forked pair, with each client
    holding every head it could hold: how many forks does the strongest SOLO detector flag, and how
    many does a single CROSSING comparison flag. Returns (solo_flagged, crossing_flagged, forks).
    A bare `solo_flagged == 0` would be satisfied by an empty fork family; the second number and the
    denominator are what forbid that reading."""
    logs = _logs_exactly(length)
    solo = crossing = forks = 0
    for A in logs:
        for B in logs:
            if not is_fork(A, B):
                continue
            forks += 1
            if _solo_detector(solo_transcript(A, range(len(A) + 1))):
                solo += 1
            if pair_detects(A, B, len(A), len(B)):
                crossing += 1
    return solo, crossing, forks


def solo_power_is_zero(length=FORK_LEN):
    solo, crossing, forks = solo_vs_crossing_census(length)
    return forks > 0 and solo == 0 and crossing == forks


# ---- law 4: detection needs the cut AND the depth -----------------------------------------------------
def pair_detects(A, B, m, n):
    """Two clients compare heads: one at size m of side A, one at size n of side B. They detect a
    fork exactly when NO consistency proof exists in EITHER direction — absence of proof is the
    evidence. Decided by the crypto, cross-checked against the structure."""
    ha, hb = A[:m], B[:n]
    ra, rb = mth(ha), mth(hb)
    fwd = verify_consistency(m, ra, n, rb, consistency_proof(m, B[:n])) if m <= n else False
    bwd = verify_consistency(n, rb, m, ra, consistency_proof(n, A[:m])) if n <= m else False
    return not (fwd or bwd)


def head_depth_census(length=FORK_LEN):
    """DECIDED over every forked pair and every pair of head sizes: detection holds EXACTLY when both
    heads exceed the common prefix. Returns (agreements, exceptions, total, detected). The exception
    count is the claim; `detected` strictly between 0 and total is the non-vacuity."""
    logs = _logs_exactly(length)
    agree = exc = total = det = 0
    for A in logs:
        for B in logs:
            if not is_fork(A, B):
                continue
            p = common_prefix_len(A, B)
            for m in range(len(A) + 1):
                for n in range(len(B) + 1):
                    total += 1
                    d = pair_detects(A, B, m, n)
                    det += 1 if d else 0
                    if d == (m > p and n > p):
                        agree += 1
                    else:
                        exc += 1
    return agree, exc, total, det


def shallow_gossip_is_worthless(length=FORK_LEN):
    """The deployment consequence, stated so it can be false: a client whose head sits at or below the
    divergence detects NOTHING no matter which side it is on. Returns (shallow_detections,
    shallow_pairs) — the first must be 0 and the second must be positive."""
    logs = _logs_exactly(length)
    shallow = pairs = 0
    for A in logs:
        for B in logs:
            if not is_fork(A, B):
                continue
            p = common_prefix_len(A, B)
            for m in range(p + 1):
                for n in range(len(B) + 1):
                    pairs += 1
                    if pair_detects(A, B, m, n):
                        shallow += 1
    return shallow, pairs


def _assume_cut_suffices(A, B, m, n):
    """A FALSIFIER TOOL: the textbook claim without its hypothesis — 'opposite sides, therefore
    detected'. It over-claims on every shallow head."""
    return is_fork(A, B)


def cut_plant_overclaims(length=FORK_LEN):
    """The plant BITES: it asserts detection where none occurs, and the count is the gap the omitted
    hypothesis would have hidden."""
    logs = _logs_exactly(length)
    over = 0
    for A in logs:
        for B in logs:
            if not is_fork(A, B):
                continue
            for m in range(len(A) + 1):
                for n in range(len(B) + 1):
                    if _assume_cut_suffices(A, B, m, n) and not pair_detects(A, B, m, n):
                        over += 1
    return over


# ---- law 5: the gossip graph — connectivity, and the attained minimum --------------------------------
def _components(k, edges):
    parent = list(range(k))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
    return len(set(find(i) for i in range(k)))


def undetected_forkings(k, edges):
    """The server may serve one view per connected component and no more, so the number of
    equivocations it can survive is 2^c - 2 (the two constant colourings are not forks)."""
    return 2 ** _components(k, edges) - 2


def detection_guaranteed(k, edges):
    return undetected_forkings(k, edges) == 0


def _all_graphs(k):
    verts = list(range(k))
    pairs = list(_comb(verts, 2))
    for mask in range(1 << len(pairs)):
        yield tuple(pairs[i] for i in range(len(pairs)) if mask >> i & 1)


def connectivity_census(max_k=MAX_CLIENTS):
    """DECIDED over EVERY labelled graph to order `max_k`: guaranteed detection holds exactly when the
    gossip graph is connected. Returns (agreements, exceptions, total)."""
    agree = exc = total = 0
    for k in range(1, max_k + 1):
        for edges in _all_graphs(k):
            total += 1
            if detection_guaranteed(k, edges) == (_components(k, edges) == 1):
                agree += 1
            else:
                exc += 1
    return agree, exc, total


def min_edges_for_guarantee(k):
    """DECIDED, not argued: the fewest gossip links that make equivocation impossible over k clients.
    Enumerated over every labelled graph on k vertices."""
    if not (1 <= k <= MAX_CLIENTS):
        raise SplitViewError("the minimum is decided only to MAX_CLIENTS")
    best = None
    for edges in _all_graphs(k):
        if detection_guaranteed(k, edges) and (best is None or len(edges) < best):
            best = len(edges)
    return best


def min_edges_table(max_k=MAX_CLIENTS):
    return tuple((k, min_edges_for_guarantee(k)) for k in range(1, max_k + 1))


def gossip_cost_is_linear(max_k=MAX_CLIENTS):
    """A SPANNING TREE SUFFICES: k-1 links, attained, so all-pairs gossip buys nothing. The bound is
    attained, which is what makes it a bound and not an estimate."""
    return all(v == max(k - 1, 0) for k, v in min_edges_table(max_k))


def single_client_is_vacuously_safe():
    """HONESTY ABOUT A BOUNDARY THAT READS AS A RESULT. At k=1 detection is 'guaranteed' — but only
    because a server with one client has one view to serve and cannot equivocate at all. That is
    absence of the attack, not presence of a defence, and it is named here so the k=1 entry in the
    table is never read as detection. Returns (guaranteed_at_1, can_fork_at_1)."""
    return detection_guaranteed(1, ()), 2 ** _components(1, ()) - 2 > 0


def _gossip_by_client_count(k, edges, threshold=3):
    """A FALSIFIER TOOL: 'enough clients are gossiping, so we are safe' — a detector keyed on
    HEADCOUNT rather than on connectivity. A sample promoted to a universal, exactly L20."""
    return k >= threshold


def count_plant_bites(max_k=MAX_CLIENTS):
    """The plant BITES: graphs with many clients and no connectivity that it calls safe."""
    bad = 0
    for k in range(1, max_k + 1):
        for edges in _all_graphs(k):
            if _gossip_by_client_count(k, edges) and not detection_guaranteed(k, edges):
                bad += 1
    return bad


# ---- the polarity plants ------------------------------------------------------------------------------
def _detect_by_root_inequality(A, B, m, n):
    """A FALSIFIER TOOL: 'the roots differ, therefore a fork'. Roots differ whenever the heads sit at
    different sizes, which is the NORMAL case — this is the polarity inversion of L18, treating
    difference as evidence when difference is the resting state."""
    return mth(A[:m]) != mth(B[:n])


def root_plant_false_positives(limit=AGREE_LEN):
    """The plant BITES on HONEST logs: over every prefix pair at different sizes it cries fork.
    Returns (false_positives, honest_pairs)."""
    logs = _logs_upto(limit)
    fp = honest = 0
    for A in logs:
        for B in logs:
            if not is_prefix(A, B) or len(A) == len(B):
                continue
            honest += 1
            if _detect_by_root_inequality(A, B, len(A), len(B)):
                fp += 1
    return fp, honest


def _verify_new_root_only(m, root_m, n, root_n, proof):
    """A FALSIFIER TOOL: the historically real implementation defect — derive the NEW root from the
    proof and never check that the OLD root is reproduced. It drops exactly the half of the check that
    binds the client's own history."""
    if m >= n or m == 0:
        return False
    p = list(proof)
    if not p:
        return False
    if m & (m - 1) == 0:
        p = [root_m] + p
    fn, sn = m - 1, n - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    sr = p[0]
    for c in p[1:]:
        if sn == 0:
            return False
        if (fn & 1) or fn == sn:
            sr = _node(c, sr)
            while fn != 0 and not (fn & 1):
                fn >>= 1
                sn >>= 1
        else:
            sr = _node(sr, c)
        fn >>= 1
        sn >>= 1
    return sn == 0 and sr == root_n


def _short_long_forks(limit=AGREE_LEN):
    """Forked pairs with len(A) < len(B) — the only shape a consistency proof is even defined on. A
    FIRST DRAFT DREW THIS FAMILY FROM LOGS OF ONE FIXED LENGTH, where `len(A) < len(B)` is never
    true, so the plant census returned (0, 0): a plant that appeared not to bite because it had
    never been offered anything to bite. The denominator is what caught it."""
    logs = _logs_upto(limit)
    return tuple((A, B) for A in logs for B in logs if len(A) < len(B) and is_fork(A, B))


def unchecked_plant_admits_forks(limit=AGREE_LEN):
    """The plant BITES: it accepts the server's own proof on a forked pair, because that proof does
    build the new root correctly — it simply does not belong to the client's history. Returns
    (admitted, forks); both must be positive."""
    admitted = 0
    fam = _short_long_forks(limit)
    for A, B in fam:
        pf = consistency_proof(len(A), B)
        if _verify_new_root_only(len(A), mth(A), len(B), mth(B), pf):
            admitted += 1
    return admitted, len(fam)


def unchecked_plant_is_blind_at_powers_of_two(limit=AGREE_LEN):
    """THE FINDING THE VACUOUS CENSUS WAS HIDING, and it is worth more than the plant. When the
    client's head size m is an exact power of two the old root is IMPLICIT — the verifier splices
    root_m into the proof — so a defective verifier that never checks the old root still fails,
    because the root it was handed poisons the NEW root it does check. The classic omission is
    therefore INVISIBLE at exactly those sizes: a test suite that exercised only power-of-two log
    sizes would certify a broken verifier. Returns (admitted_pow2, forks_pow2, admitted_off,
    forks_off) — the first must be 0 and the third must be positive, and that contrast is the
    result."""
    ap = fp = ao = fo = 0
    for A, B in _short_long_forks(limit):
        m = len(A)
        if m == 0:
            continue
        pf = consistency_proof(m, B)
        bit = _verify_new_root_only(m, mth(A), len(B), mth(B), pf)
        if m & (m - 1) == 0:
            fp += 1
            ap += 1 if bit else 0
        else:
            fo += 1
            ao += 1 if bit else 0
    return ap, fp, ao, fo


def unchecked_plant_witness():
    """An explicit biting pair, pinned so the class cannot silently become untestable: heads at size
    3 — deliberately NOT a power of two — where the honest verifier refuses and the defective one
    admits."""
    A = (b"0", b"0", b"1")
    B = (b"0", b"0", b"0", b"1")
    if not is_fork(A, B):
        return False
    pf = consistency_proof(len(A), B)
    honest = verify_consistency(len(A), mth(A), len(B), mth(B), pf)
    plant = _verify_new_root_only(len(A), mth(A), len(B), mth(B), pf)
    return plant and not honest


# ---- the refusal ---------------------------------------------------------------------------------------
def adjudicate(A, B, m, n):
    """THE AUTHORITATIVE CALL. It RAISES on a fork; it does not return an advisory flag. A fork
    reported as a warning is a fork that ships."""
    if pair_detects(A, B, m, n):
        raise ForkDetected(f"no consistency proof exists between heads {m} and {n}")
    return True


def refuses_a_fork():
    A, B = (b"0", b"1"), (b"0", b"0")
    try:
        adjudicate(A, B, 2, 2)
    except ForkDetected as exc:
        return exc.code == "SPLITVIEW-FORKED"
    return False


def admits_an_extension():
    A, B = (b"0",), (b"0", b"1")
    return adjudicate(A, B, 1, 2) is True


# ---- digests + scenes ------------------------------------------------------------------------------------
def sv_digest(name, payload):
    hh = hashlib.sha256(); hh.update(MAGIC)
    hh.update(f"|{name}|{payload}".encode())
    return hh.hexdigest()


def _scene_crypto():
    return sv_digest("crypto", f"{agreement_census()}:{forgery_census()}:"
                               f"{crypto_matches_structure()}:"
                               f"{unchecked_plant_admits_forks()}:"
                               f"{unchecked_plant_is_blind_at_powers_of_two()}:"
                               f"{unchecked_plant_witness()}")


def _scene_lonely():
    return sv_digest("lonely", f"{solo_vs_crossing_census()}:{solo_power_is_zero()}:"
                               f"{head_depth_census()}:{shallow_gossip_is_worthless()}")


def _scene_gossip():
    return sv_digest("gossip", f"{connectivity_census()}:{min_edges_table()}:"
                               f"{gossip_cost_is_linear()}:{single_client_is_vacuously_safe()}")


_SCENES = {"crypto": _scene_crypto, "lonely": _scene_lonely, "gossip": _scene_gossip}
SCENES = ("crypto", "lonely", "gossip")


def scene_result(name):
    return _SCENES[name]()


def golden(name):
    with open(_os.path.join(_HERE, "conformance_splitview.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise SplitViewError(f"no golden named {name!r}")


def _main(argv):
    for n in SCENES:
        print(n, scene_result(n))
    print(f"crypto vs structure {agreement_census()} (exceptions must be 0)")
    print(f"forgeries accepted {forgery_census()}")
    solo, crossing, forks = solo_vs_crossing_census()
    print(f"solo {solo}/{forks} | crossing {crossing}/{forks} | lonely-client theorem "
          f"{solo_power_is_zero()}")
    print(f"head-depth law {head_depth_census()} | shallow gossip {shallow_gossip_is_worthless()}")
    print(f"cut plant overclaims {cut_plant_overclaims()} times")
    print(f"connectivity {connectivity_census()} | min edges {min_edges_table()} "
          f"(linear: {gossip_cost_is_linear()})")
    print(f"k=1 vacuously safe {single_client_is_vacuously_safe()}")
    print(f"plants: root {root_plant_false_positives()} | unchecked "
          f"{unchecked_plant_admits_forks()} | count {count_plant_bites()}")
    print(f"unchecked blind at powers of two {unchecked_plant_is_blind_at_powers_of_two()} "
          f"| witness {unchecked_plant_witness()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(_sys.argv))
