# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""linear_core — the C4 STAGING APPARATUS (D13 §3). Not a glyph. Not Urðr syntax.

The Urðr kernel is sealed; D13 deferred C4 (linearity) with pre-registered triggers
that have NOT fired. This module is the review apparatus built ahead of need: a
reference MULTIPLICITY CHECKER over a deliberately minimal core term language, so
the eventual §20 review measures a floor instead of debating a sketch. If the
triggers never fire, this stays a study; if they fire, this is the reference whose
verdicts an independent placement must reproduce.

THE CORE (six ops, semicolon-separated; case- and whitespace-insensitive — the
canon law below quotients the surface):

    NEW k          bind a fresh linear resource k       (rebinding a live name refuses)
    USE k          consume k                            (second use refuses, naming BOTH sites)
    DROP k         consume k by explicit discard        (satisfies linear mode)
    DUP k j        alias k as j                         (ALWAYS refuses — no-cloning)
    IF ( a ) ( b ) two arms; their consumption effects MUST match (the split law)
    SKIP / END     no-op / terminator

THE LAWS (static — no evaluation exists in this language, only the judgment):
  * linear mode: every bound resource is consumed exactly once (USE or DROP);
    affine mode: at most once. The affine/linear fork is the decision D13 requires
    the eventual review to make; both directions are falsified here.
  * every refusal is URDR-LINEAR and NAMES its sites (1-based op indices) — a
    static refusal is only useful if it points at the program text;
  * linearity is a property of the CANON: verdicts and digests are computed on the
    canonical form (`URDRLIN1` | canon text), never the surface;
  * first refusal wins, deterministically (walk order is program order).

Honest scope: this core has no functions, no data flow, no borrows — it isolates
multiplicity accounting and branch splitting, the two laws every linear system in
the survey (Girard, Rust, session types, OTS keys) shares. Generalizing to Urðr's
binder structure is review work, not staging work. GRADE: staging study —
IMPLEMENTED/MEASURED on this core via `tests/test_linear_core.py` + the pinned
corpus; the GLYPH remains unadmitted and ungraded."""
import hashlib
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
MAGIC = b"URDRLIN1"
KEYWORDS = ("NEW", "USE", "DROP", "DUP", "IF", "SKIP", "END")


class Verdict:
    def __init__(self, verdict, sites=(), message=""):
        self.verdict = verdict
        self.sites = list(sites)
        self.message = message

    def __repr__(self):
        return f"Verdict({self.verdict}, sites={self.sites}, {self.message!r})"


# ---- parse + canon -------------------------------------------------------------------
def _tokens(text):
    out, word = [], ""
    for ch in text:
        if ch in ";()":
            if word:
                out.append(word)
                word = ""
            out.append(ch)
        elif ch.isspace():
            if word:
                out.append(word)
                word = ""
        else:
            word += ch
    if word:
        out.append(word)
    return out


def parse(text):
    """Parse to a nested op list. Ops get 1-based sites in source order (flat,
    including arm interiors). Malformed input raises ValueError — the staging
    corpus is well-formed by construction; parse errors are not refusals."""
    toks = _tokens(text)
    pos = {"i": 0, "site": 0}

    def peek():
        return toks[pos["i"]].upper() if pos["i"] < len(toks) else None

    def take(expect=None):
        if pos["i"] >= len(toks):
            raise ValueError("unexpected end of program")
        t = toks[pos["i"]]
        pos["i"] += 1
        if expect is not None and t.upper() != expect:
            raise ValueError(f"expected {expect!r}, got {t!r}")
        return t

    def name():
        t = take()
        if t.upper() in KEYWORDS or t in ";()":
            raise ValueError(f"expected a resource name, got {t!r}")
        return t.lower()                                   # canon: names case-folded

    def op():
        kw = take().upper()
        pos["site"] += 1
        s = pos["site"]
        if kw == "NEW":
            return ("NEW", name(), s)
        if kw == "USE":
            return ("USE", name(), s)
        if kw == "DROP":
            return ("DROP", name(), s)
        if kw == "DUP":
            return ("DUP", name(), name(), s)
        if kw == "SKIP":
            return ("SKIP", s)
        if kw == "END":
            return ("END", s)
        if kw == "IF":
            take("(")
            a = seq(stop=")")
            take(")")
            take("(")
            b = seq(stop=")")
            take(")")
            return ("IF", a, b, s)
        raise ValueError(f"unknown op {kw!r}")

    def seq(stop=None):
        ops = []
        while True:
            nxt = peek()
            if nxt is None or nxt == stop:
                return ops
            if nxt == ";":
                take()
                continue
            ops.append(op())

    prog = seq()
    if not prog or prog[-1][0] != "END":
        raise ValueError("program must end with END")
    return prog


def _canon_text(prog):
    def one(o):
        if o[0] == "IF":
            return "IF ( %s ) ( %s )" % (_canon_text(o[1]), _canon_text(o[2]))
        return " ".join(str(x) for x in o[:-1])            # site excluded from canon
    return " ; ".join(one(o) for o in prog)


def program_digest(prog):
    """Digest(program) = SHA-256(MAGIC | canonical text) — linearity judgments and
    identity both live on the canon, per the D13 §3 pre-registration."""
    return hashlib.sha256(MAGIC + _canon_text(prog).encode("utf-8")).hexdigest()


# ---- the judgment ---------------------------------------------------------------------
def _walk(prog, env, mode, defect_first_use_only):
    """env: name -> ("live", bind_site) | ("consumed", first_site). Returns a
    Verdict on refusal, else None (env mutated)."""
    for o in prog:
        kw = o[0]
        if kw == "NEW":
            _, nm, s = o
            if nm in env and env[nm][0] == "live":
                return Verdict("URDR-LINEAR", [env[nm][1], s],
                               f"rebinding live resource {nm!r}")
            env[nm] = ("live", s)
        elif kw in ("USE", "DROP"):
            _, nm, s = o
            if nm not in env:
                return Verdict("URDR-LINEAR", [s], f"{nm!r} is not bound")
            state, first = env[nm]
            if state == "consumed":
                if defect_first_use_only:
                    continue                               # THE DEFECT: miscounts
                return Verdict("URDR-LINEAR", [first, s],
                               f"{nm!r} consumed twice (sites {first} and {s})")
            env[nm] = ("consumed", s)
        elif kw == "DUP":
            _, nm, nm2, s = o
            return Verdict("URDR-LINEAR", [s],
                           f"DUP {nm!r} -> {nm2!r}: linear resources cannot alias")
        elif kw == "IF":
            _, arm_a, arm_b, s = o
            env_a = dict(env)
            va = _walk(arm_a, env_a, mode, defect_first_use_only)
            if va is not None:
                return va
            env_b = dict(env)
            vb = _walk(arm_b, env_b, mode, defect_first_use_only)
            if vb is not None:
                return vb
            # the split law compares consumption STATUS, not site provenance:
            # (USE k) and (DROP k) arms agree; sites differing across arms do not
            # constitute a mismatch. The merge keeps arm A's sites (canonical).
            if {n: st[0] for n, st in env_a.items()} != {n: st[0] for n, st in env_b.items()}:
                return Verdict("URDR-LINEAR", [s],
                               "IF arms consume different resource multisets")
            env.clear()
            env.update(env_a)
        elif kw == "END":
            _, s = o
            if mode == "linear":
                live = [(nm, st[1]) for nm, st in sorted(env.items())
                        if st[0] == "live"]
                if live:
                    return Verdict("URDR-LINEAR", [b for (_n, b) in live],
                                   "unconsumed under linear mode: "
                                   + ", ".join(n for (n, _b) in live))
        # SKIP: nothing
    return None


def check(prog, mode="linear"):
    """The static judgment. mode in {"linear", "affine"} — the fork the eventual
    §20 review must decide; both are first-class here so both stay falsified."""
    if mode not in ("linear", "affine"):
        raise ValueError(f"unknown mode {mode!r}")
    env = {}
    v = _walk(prog, env, mode, defect_first_use_only=False)
    return v if v is not None else Verdict("ACCEPT")


def check_defect_first_use_only(prog, mode="linear"):
    """THE DEFECT (non-vacuity): a checker that counts only the FIRST use of each
    resource. Must accept double-uses the real judgment refuses."""
    env = {}
    v = _walk(prog, env, mode, defect_first_use_only=True)
    return v if v is not None else Verdict("ACCEPT")


# ---- the pinned corpus ------------------------------------------------------------------
def load_corpus():
    """rows of (name, program_text, mode, expected_verdict) from corpus_linear.txt."""
    rows = []
    with open(os.path.join(_HERE, "corpus_linear.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            name, mode, expected, prog = (x.strip() for x in ln.split("|", 3))
            rows.append((name, prog, mode, expected))
    return rows


if __name__ == "__main__":
    red = 0
    for (name, prog_text, mode, expected) in load_corpus():
        v = check(parse(prog_text), mode=mode)
        ok = v.verdict == expected
        red += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {name:<24} {mode:<6} -> {v.verdict}"
              f"{' (pinned ' + expected + ')' if not ok else ''}")
    raise SystemExit(1 if red else 0)
