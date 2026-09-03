# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (C) 2026 Daniel J. Dillberg
"""voxbreak (URDRVXZ1) — THE BREAK-EVEN LEDGER, AND THE GATE THAT WAS PROPOSED IS THE WRONG ONE.

`voxfriction` measured the payoff surface and found a sharp phase transition at four distinct owners,
with single-owner tiles carrying the overwhelming share of all value. The obvious reading — EXPLOIT
THE SINGLE-OWNER CASE FIRST, and if it cannot break even stop the branch — was proposed before any
gated arrangement had been run. THIS RUNG BUILDS THE GATE AND KEEPS THE BOOKS, and it returns two
answers, one of which contradicts the proposal:

    THE INEQUALITY HAS NO SOLUTION ON THIS LOOP. Under EVERY declared admission rule the total spend
    exceeds the committed reference. The break-even the arc has been chasing does not exist here, and
    it does not miss by a little.

    AND THE SINGLE-OWNER GATE IS WORSE THAN NO GATE AT ALL. Admitting only single-owner tiles spends
    MORE than admitting every tile, because it declines the two- and three-owner tiles that
    `voxfriction` measured as PROFITABLE. `single_ownership_is_not_the_profitable_gate` states that
    as a law, so the refutation is re-run every gate rather than remembered.

THE SIX ACCOUNTS ARE KEPT SEPARATELY AND NEVER FUSED, because a break-even question answered with a
single number cannot say which term is responsible:

    recognise   the admission read — the tile's owner set, which the certificate's first step pays anyway
    encode      naming the owners the gate admitted, one operation each
    verify      the certificate's own sufficient condition, checked against the CURRENT camera
    execute     the raster that produced the committed frame
    fallback    raster operations DISCARDED when an admitted tile failed and had to be redone
    retired     BASELINE MINUS EXECUTED, taken from the run — the quantity no unused fast path can earn

WHAT THE LEDGER SHOWS IS THAT THE CERTIFICATE IS NOT THE PROBLEM AND NEVER WAS. Against the cold
tiled loop it lives in, the certified arrangement retires real work. Against `voxref` it loses, and
it loses by roughly three times everything the certificate retires — because the TILED SCAFFOLDING
costs the reference several times over before a single certificate is consulted.
`the_deficit_is_the_scaffolding_and_not_the_certificate` is the law that separates those two, and it
is the finding that decides where the next rung goes.

AND THE FRICTION IS A ROUNDING ERROR, WON IN A WAY A GATE IS NOT USUALLY FOR. The best gate beats no
gate — friction does pay, exactly as `voxfriction` said it would — but by under one per cent of what
the certificate itself retires and under one per cent of the scaffolding tax. More importantly, the
best gate and no gate at all EXECUTE THE IDENTICAL NUMBER OF OPERATIONS: not one certificate is lost
by gating, and the entire gain is fallback, encode and verify that no longer happen because every
tile the gate declines was going to FAIL. THE GATE DOES NOT CHOOSE WHICH CERTIFICATES TO EARN; IT
PREDICTS WHICH ATTEMPTS ARE DOOMED, and that is a strictly smaller prize than a payoff surface makes
it look — the surface counts a declined tile's forgone COST, the ledger can only collect its forgone
WASTE. `the_gates_whole_gain_is_waste_avoided` states it, and the single-owner rule crosses that line
the other way: it declines tiles that would have SUCCEEDED, which is exactly why it loses.

THE `none` RULE IS THE COLD TILED LOOP EXACTLY, not an approximation of it —
`the_none_rule_is_exactly_the_cold_tiled_loop` requires it to equal `voxmanifold`'s Z0 operation for
operation, so the baseline every retirement is measured against is the one already committed.

NO PROMOTION AND NO PREDICTION IS SCORED HERE. The hypothesis this rung tests was stated before the
measurement but was NEVER COMMITTED to the tree, so it earns no pre-registration credit and none is
claimed for it: `the_refuted_hypothesis_carries_no_preregistration_credit` says so as a law.
Pre-registration is COMMIT ORDER or it is nothing. WHAT THIS RUNG DOES SHIP, one commit early, is the
pre-registration for the next one — five predictions about THE TILE SIZE, which is the parameter the
scaffolding tax is a function of and which no rung in this arc has ever varied.

does_not_show: NOTHING ABOUT TIME, and no wall clock enters. NOTHING ABOUT MEMORY, which is where an
owner map's storage would be paid and where a tiled loop's real-world case is usually made. THAT NO
GATE CAN WIN — five are declared and measured; a sixth reading a different signal is not ruled out.
THAT THE SCAFFOLDING CANNOT BE MADE CHEAPER — this rung measures its cost at ONE tile size and the
next one varies it. And NO PROMOTION: `voxref` is untouched.

falsifier: `the_observable_never_moves_under_any_rule` compares colour and depth AS LISTS for all
five rules across all sixteen states and reddens if a gate ever moves a byte;
`single_ownership_is_not_the_profitable_gate` reddens the day the single-owner gate stops losing to
no gate at all, which is the day the proposal this rung refutes becomes right; and
`the_inequality_has_no_solution_on_this_loop` reddens the day any rule undercuts the committed
reference, which is the result the whole arc is trying to produce and would be the best possible
failure of this law.
"""
import hashlib
import os
import sys as _sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)

import voxref as VR                                          # noqa: E402
import voxray as VX                                          # noqa: E402
import voxwork as VO                                         # noqa: E402
import voxsilo as VS                                         # noqa: E402
import voxcond as VD                                         # noqa: E402
import voxstate as VT                                        # noqa: E402
import voxmanifold as VM                                     # noqa: E402
import voxfriction as VF                                     # noqa: E402

MAGIC = b"URDRVXZ1"
TILE = VD.TILE

#: DECLARED — the admission rules, each keyed on AT MOST this many distinct owners in the
#: predecessor's tile. `none` admits nothing and is therefore the cold tiled loop exactly; `all`
#: admits every tile and is `voxmanifold`'s Z3 unchanged. `one` is the rule this rung was built to
#: test, and it is the one that loses.
RULES = ("none", "one", "two", "three", "all")
ADMIT = {"none": 0, "one": 1, "two": 2, "three": 3, "all": None}

#: DECLARED — the five accounts, kept separately and never fused. A break-even question answered
#: with one number cannot say which term is responsible, and every term here has a different remedy.
ACCOUNTS = ("recognise", "encode", "verify", "execute", "fallback")


class VoxbreakError(Exception):
    """VOXBREAK-REFUSE — a rule, an account or a record this module will not pretend to read."""


# ---- one state, rendered under one admission rule --------------------------------------------------------
def render_state(n, prev_key, admit):
    """(colour, depth, key, {account: operations}) for one lattice state under one admission rule.

    `admit` is the largest owner count the gate will attempt, or None for no ceiling. `admit == 0`
    means the gate is statically empty, so the tile is NEVER READ — which is what makes the `none`
    rule the cold tiled loop exactly rather than the cold loop plus a pointless traversal.

    The certificate is `voxcond`'s P4 and nothing else: ownership, VERIFIED against the current
    camera, with depth RECONSTRUCTED from the owner's own plane. No probe policy can move the
    observable, because the certificate's sufficient condition is checked independently of the gate.
    """
    _c, eye, fwd = VT.state(n)
    prims = VX.primitives_with("reversed")
    m = VR.basis(fwd)
    cx, cy = VR.W // 2, VR.H // 2
    tw = (VR.W + TILE - 1) // TILE
    th = (VR.H + TILE - 1) // TILE
    colour = [VR.BACKGROUND] * (VR.W * VR.H)
    depth = [VR.FAR] * (VR.W * VR.H)
    key = [-1] * (VR.W * VR.H)
    acc = dict.fromkeys(ACCOUNTS, 0)
    tris = []
    for pk, col, quad in prims:
        acc["execute"] += VO.MUL_PER_QUAD
        s = VD._tri_setup(quad, eye, m, cx, cy)
        if s is None:
            continue
        acc["execute"] += VO.MUL_PER_SEEN + VO.DIV_PER_SEEN + 2 * VO.MUL_PER_TRIANGLE
        for t in s:
            tris.append((pk, col) + t)
    bins = [[] for _ in range(tw * th)]
    for t in tris:
        p, q, r = t[2], t[3], t[4]
        xl = max(min(p[0], q[0], r[0]), 0) // TILE
        xh = min(max(p[0], q[0], r[0]), VR.W - 1) // TILE
        yl = max(min(p[1], q[1], r[1]), 0) // TILE
        yh = min(max(p[1], q[1], r[1]), VR.H - 1) // TILE
        if xl > xh or yl > yh:
            continue
        for ty in range(yl, yh + 1):
            for tx in range(xl, xh + 1):
                bins[ty * tw + tx].append(t)
    by_key = {}
    for t in tris:
        by_key.setdefault(t[0], []).append(t)

    def raster(group, x0, x1, y0, y1):
        used = 0
        for pk, col, p, q, r, area, b0, b1, b2, _z in group:
            for y in range(y0, y1 + 1):
                row = y * VR.W
                for x in range(x0, x1 + 1):
                    used += VO.MUL_PER_WALK
                    w0 = VR._edge(p[0], p[1], q[0], q[1], x, y) + b0
                    w1 = VR._edge(q[0], q[1], r[0], r[1], x, y) + b1
                    w2 = VR._edge(r[0], r[1], p[0], p[1], x, y) + b2
                    if w0 < 0 or w1 < 0 or w2 < 0:
                        continue
                    used += VO.MUL_PER_COVER + VO.DIV_PER_COVER
                    d = (p[2] * w1 + q[2] * w2 + r[2] * w0) // area
                    i = row + x
                    if (d, pk) < (depth[i], key[i] if key[i] >= 0 else (1 << 62)):
                        depth[i], key[i], colour[i] = d, pk, col
        return used

    for ty in range(th):
        for tx in range(tw):
            b = bins[ty * tw + tx]
            x0, x1 = tx * TILE, min(tx * TILE + TILE, VR.W) - 1
            y0, y1 = ty * TILE, min(ty * TILE + TILE, VR.H) - 1
            taken = False
            if prev_key is not None and b and admit != 0:
                owners, _lrun, pops = VF.probe(prev_key, x0, x1, y0, y1)
                acc["recognise"] += pops
                oset = {prev_key[y * VR.W + x]
                        for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
                if -1 not in oset and (admit is None or owners <= admit):
                    acc["encode"] += len(oset)
                    group, far, ok = [], -1, True
                    for k in oset:
                        got = by_key.get(k)
                        if not got:
                            ok = False
                            break
                        for t in got:
                            acc["verify"] += 1
                            group.append(t)
                            z = max(t[2][2], t[3][2], t[4][2])
                            if z > far:
                                far = z
                    if ok:
                        for t in b:
                            acc["verify"] += 1
                            if t[0] not in oset and t[9] <= far:
                                ok = False
                                break
                    if ok:
                        spent = raster(group, x0, x1, y0, y1)
                        if any(key[y * VR.W + x] < 0
                               for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)):
                            # the certificate held but left the tile incomplete: everything the
                            # owner-only raster just did is DISCARDED, and it is charged as waste
                            # rather than quietly dropped
                            acc["fallback"] += spent
                            for y in range(y0, y1 + 1):
                                for x in range(x0, x1 + 1):
                                    i = y * VR.W + x
                                    depth[i], key[i], colour[i] = VR.FAR, -1, VR.BACKGROUND
                        else:
                            acc["execute"] += spent
                            taken = True
            if not taken:
                acc["execute"] += raster(b, x0, x1, y0, y1)
    return colour, depth, key, acc


# ---- the ledger over the whole lattice ---------------------------------------------------------------
_LEDGER = {}


def ledger(rule):
    """{account: operations} plus `sound`, `certified` and `attempted`, over the whole lattice.

    Every state inherits from `voxstate`'s nearest-neighbour traversal, which `voxmanifold` measured
    as the best of the four. The traversal is held FIXED across all five rules so the only thing
    varying is the gate.
    """
    if rule not in RULES:
        raise VoxbreakError("VOXBREAK-REFUSE: no admission rule named %r" % (rule,))
    k = (VR.world_digest(), rule)
    if k in _LEDGER:
        return _LEDGER[k]
    seq, pred = VT.order("Z3")
    keys = {}
    acc = dict.fromkeys(ACCOUNTS, 0)
    sound = True
    for n in seq:
        prev = None if pred[n] is None else keys[pred[n]]
        col, dep, kk, a = render_state(n, prev, ADMIT[rule])
        keys[n] = kk
        for name in ACCOUNTS:
            acc[name] += a[name]
        ref = VT.frames()[n]
        if col != ref[0] or dep != ref[1]:
            sound = False
    acc["sound"] = sound
    _LEDGER[k] = acc
    return acc


def spend(rule):
    """EVERY operation the arrangement charges — the left-hand side of the break-even inequality."""
    a = ledger(rule)
    return sum(a[name] for name in ACCOUNTS)


def retired(rule):
    """BASELINE MINUS EXECUTED, taken from the run. The baseline is the `none` rule, which is the
    cold tiled loop this arrangement is a modification of."""
    return spend("none") - spend(rule)


def net(rule):
    """The break-even margin against the COMMITTED reference. Positive is underwater."""
    return spend(rule) - VM.reference_cost()


def best():
    """The declared rule with the lowest total spend."""
    return min(RULES, key=spend)


# ---- the laws -------------------------------------------------------------------------------------------
def the_observable_never_moves_under_any_rule():
    """THE CONTRACT, AND IT IS WHY A GATE IS SAFE TO GET WRONG. The gate only chooses whether to
    ATTEMPT a certificate whose sufficient condition is checked independently, so no rule can move
    `O_t`. Compared as LISTS, colour and depth, across all five rules and all sixteen states — the
    contract that has now caught an unsound optimisation in three consecutive rungs."""
    return all(ledger(r)["sound"] for r in RULES)


def the_none_rule_is_exactly_the_cold_tiled_loop():
    """The baseline every retirement is measured against is the one ALREADY COMMITTED, operation for
    operation, not a re-derivation of it that might have drifted."""
    a = ledger("none")
    return (spend("none") == VM.run("Z0")[1]
            and a["recognise"] == 0 and a["encode"] == 0 and a["verify"] == 0
            and a["fallback"] == 0)


def the_all_rule_is_exactly_the_committed_traversal():
    """And the ungated arrangement is `voxmanifold`'s Z3 unchanged, so this rung's ledger is a
    DECOMPOSITION of a committed number rather than a second measurement of it."""
    a = ledger("all")
    return a["execute"] + a["fallback"] == VM.run("Z3")[1]


def single_ownership_is_not_the_profitable_gate():
    """THE REFUTATION, RE-RUN EVERY GATE RATHER THAN REMEMBERED.

    `voxfriction` found single-owner tiles carrying the overwhelming share of the payoff, and the
    natural reading was to gate on them and nothing else. THAT READING IS WRONG, and the reason is
    visible in `voxfriction`'s own surface: the two- and three-owner buckets are POSITIVE too. A gate
    that admits only single-owner tiles declines them, forfeits their payoff, and still pays the
    admission read on every tile it declines. It therefore spends MORE than no gate at all.

    Sharing the overwhelming majority of a benefit is not the same as being the whole of it, and this
    law is the difference between those two statements, measured."""
    return spend("one") > spend("all")


def the_gate_pays_but_only_against_the_loop_it_lives_in():
    """FRICTION DOES WORK, EXACTLY AS `voxfriction` SAID. Some declared gate beats no gate — the
    admission read is not wasted — and the certificate beats the cold tiled loop. Both are true and
    neither is enough, which is why the next law exists."""
    return spend(best()) < spend("all") and spend(best()) < spend("none")


def the_inequality_has_no_solution_on_this_loop():
    """THE HEADLINE. `C_admission + C_encode + C_verify + C_execute + C_fallback < C_reference` has
    NO SOLUTION among the declared rules. Not one is under the committed reference, and the best is
    not close. This is the law that would redden the day the arc succeeds, which is the only kind of
    failure worth building in."""
    return all(net(r) > 0 for r in RULES)


def scaffolding_tax():
    """What the tiled loop costs OVER the committed reference before a certificate is consulted."""
    return spend("none") - VM.reference_cost()


def the_deficit_is_the_scaffolding_and_not_the_certificate():
    """THE FINDING THAT DECIDES WHERE THE NEXT RUNG GOES, AND IT SEPARATES TWO THINGS THAT HAVE BEEN
    MEASURED TOGETHER FOR FOUR RUNGS.

    The certificate retires real work against the loop it lives in. The loop costs the reference
    several times over before any certificate is consulted. The tax is LARGER than everything the
    certificate retires, so no improvement to the certificate can close the gap and the whole
    remaining question is about the scaffolding — which is a parameter, not a mechanism, and the next
    rung varies it."""
    return scaffolding_tax() > retired(best())


def friction_is_smaller_than_the_certificate_it_gates():
    """AND THE ORDERING OF MAGNITUDES IS ITSELF A RESULT. The gate's whole gain over no gate is under
    a HUNDREDTH of what the certificate retires and under a hundredth of the scaffolding tax.
    Reporting a gain of that size next to a deficit of millions without saying which is which is how
    a programme talks itself into another year of the same loop.

    THE FIRST DRAFT OF THIS LAW CLAIMED FOUR ORDERS AND REDDENED AT THREE HUNDRED AND SIXTY. The
    correction is kept visible rather than tidied away: the ordering is real and the exponent I
    reached for was not."""
    gain = spend("all") - spend(best())
    return 0 < gain * 100 < retired(best()) and gain * 100 < scaffolding_tax()


def the_gates_whole_gain_is_waste_avoided():
    """AND THE MECHANISM OF THE GAIN IS NOT WHAT A GATE IS USUALLY FOR, WHICH IS THE SHARPEST THING
    IN THIS LEDGER.

    The best gate and no gate at all EXECUTE THE IDENTICAL NUMBER OF OPERATIONS — the same tiles are
    certified either way, and not one certificate is lost by gating. The entire gain is FALLBACK,
    ENCODE and VERIFY that no longer happen: every tile the gate declines is a tile whose certificate
    was going to FAIL and be thrown away.

    So the gate does not choose which certificates to earn. It predicts which ATTEMPTS are doomed,
    and that is a strictly smaller prize than the payoff surface makes it look — the surface counts a
    declined tile's forgone cost, while the ledger can only ever collect its forgone WASTE. The
    single-owner gate crosses this line in the other direction: it declines tiles that would have
    SUCCEEDED, which is why its `execute` rises and it loses to no gate at all."""
    return (ledger(best())["execute"] == ledger("all")["execute"]
            and ledger("one")["execute"] > ledger("all")["execute"])


def the_refuted_hypothesis_carries_no_preregistration_credit():
    """PRE-REGISTRATION IS COMMIT ORDER OR IT IS NOTHING.

    The hypothesis this rung refutes — exploit the single-owner case first — was stated before any
    gated arrangement was run, and that is a real fact about the order of events. It was never
    COMMITTED to this tree, so it cannot be verified as prior by anything except my word, and this
    arc does not score claims on my word. It is therefore scored as NOTHING: the refutation stands on
    the measurement alone, and this rung declares no verdict set of its own.

    `voxfriction` deliberately made no prediction; there is consequently no committed prediction for
    this rung to score, and inventing one after the fact would be exactly the failure the mechanism
    exists to prevent."""
    return (not hasattr(_sys.modules[__name__], "PREDICTIONS")
            and VF.the_rung_makes_no_prediction_claim())


def nothing_is_promoted():
    return VD.nothing_is_promoted() and VM.nothing_is_promoted()


def no_wall_clock_enters_this_rung():
    import ast
    with open(os.path.join(_HERE, "voxbreak.py"), encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            if any(a.name.split(".")[0] in VO.FORBIDDEN_IMPORTS for a in node.names):
                return False
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".")[0] in VO.FORBIDDEN_IMPORTS:
                return False
    return True


# ---- the prediction for the NEXT rung, shipped one commit early -------------------------------------------
PREDICTION_RECORD = os.path.join("spec", "attest", "voxtile-prediction.txt")


def prediction_text():
    with open(os.path.join(ROOT, PREDICTION_RECORD), encoding="utf-8") as fh:
        return fh.read()


def prediction_digest():
    return hashlib.sha256(MAGIC + b"|pred|" + prediction_text().encode()).hexdigest()


def the_prediction_ships_before_the_sweep():
    """`voxcond`'s and `voxstate`'s precedent. THE SCAFFOLDING TAX IS A FUNCTION OF THE TILE SIZE and
    no rung in this arc has ever varied it — every figure from `voxcond` onward was taken at one
    tile. The five predictions about that sweep are committed HERE with their digest pinned as this
    rung's golden; the sweep lands in a LATER commit."""
    t = prediction_text()
    ids = [p for p in ("T1", "T2", "T3", "T4", "T5") if ("predict %s " % p) in t]
    return len(ids) == 5 and prediction_digest() == golden("prediction")


def the_prediction_names_no_result():
    return all(not ln.startswith("verdict ") for ln in prediction_text().split("\n"))


# ---- the record ---------------------------------------------------------------------------------------
RECORD = os.path.join("spec", "attest", "voxref-breakeven.txt")


def break_digest():
    body = "\n".join("%s %s %d %d %d"
                     % (r, " ".join(str(ledger(r)[a]) for a in ACCOUNTS),
                        spend(r), retired(r), net(r))
                     for r in RULES)
    body += "\ntax %d best %s" % (scaffolding_tax(), best())
    return hashlib.sha256(MAGIC + b"|brk|" + body.encode()).hexdigest()


def generate():
    rows = ["# URDRVXZ1 the break-even ledger — emitted by voxbreak.generate(), committed as an",
            "# artifact, re-derived by the gate.",
            "# world %s" % VR.world_digest(),
            "# THE INEQUALITY HAS NO SOLUTION: every rule spends more than the committed reference.",
            "# AND THE SINGLE-OWNER GATE LOSES TO NO GATE AT ALL, which refutes the proposal this",
            "# rung was built to test. THE SIX ACCOUNTS ARE NEVER FUSED.",
            "#   rule  <rule> <recognise> <encode> <verify> <execute> <fallback>",
            "#   total <rule> <spend> <retired vs the cold tiled loop> <net vs the reference>",
            "#   tax   <scaffolding cost over the committed reference> <the reference>",
            "#   best  <the rule with the lowest spend>",
            "#   digest <break digest>"]
    for r in RULES:
        rows.append("rule %s %s" % (r, " ".join(str(ledger(r)[a]) for a in ACCOUNTS)))
    for r in RULES:
        rows.append("total %s %d %d %d" % (r, spend(r), retired(r), net(r)))
    rows.append("tax %d %d" % (scaffolding_tax(), VM.reference_cost()))
    rows.append("best %s" % best())
    rows.append("digest %s" % break_digest())
    return "\n".join(rows) + "\n"


def _read():
    with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
        return fh.read()


def parse(text=None):
    if text is None:
        text = _read()
    rows, world = [], None
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            if ln.startswith("# world "):
                world = ln.split()[2]
            continue
        f = ln.split()
        if f[0] == "rule" and (len(f) != 2 + len(ACCOUNTS) or f[1] not in RULES):
            raise VoxbreakError("VOXBREAK-REFUSE: a rule row naming no declared rule")
        if f[0] == "total" and (len(f) != 5 or f[1] not in RULES):
            raise VoxbreakError("VOXBREAK-REFUSE: a total row naming no declared rule")
        if f[0] == "tax" and len(f) != 3:
            raise VoxbreakError("VOXBREAK-REFUSE: a tax row of the wrong arity")
        if f[0] == "best" and (len(f) != 2 or f[1] not in RULES):
            raise VoxbreakError("VOXBREAK-REFUSE: a best row naming no declared rule")
        if f[0] not in ("rule", "total", "tax", "best", "digest"):
            raise VoxbreakError("VOXBREAK-REFUSE: a row of unknown kind %r" % (f[0],))
        rows.append(tuple(f))
    if world is None:
        raise VoxbreakError("VOXBREAK-REFUSE: the record names no world digest")
    if not rows:
        raise VoxbreakError("VOXBREAK-REFUSE: the record has no rows")
    return world, rows


def the_record_names_this_world():
    return parse()[0] == VR.world_digest()


def the_record_is_bound_to_the_live_code():
    _w, rows = parse()
    for r in rows:
        if r[0] == "rule":
            if tuple(int(x) for x in r[2:]) != tuple(ledger(r[1])[a] for a in ACCOUNTS):
                return False
        if r[0] == "total":
            if (int(r[2]), int(r[3]), int(r[4])) != (spend(r[1]), retired(r[1]), net(r[1])):
                return False
        if r[0] == "tax" and (int(r[1]), int(r[2])) != (scaffolding_tax(), VM.reference_cost()):
            return False
        if r[0] == "best" and r[1] != best():
            return False
    return next(r[1] for r in rows if r[0] == "digest") == break_digest()


def a_tampered_row_refuses():
    text = _read()
    for ln in text.split("\n"):
        if ln.startswith("rule one "):
            text = text.replace(ln, "rule seven " + " ".join(ln.split()[2:]), 1)
            break
    try:
        parse(text)
    except VoxbreakError:
        return True
    return False


def told():
    ref = VM.reference_cost()
    b = best()
    gain = spend("all") - spend(b)
    return ("THE INEQUALITY HAS NO SOLUTION ON THIS LOOP, AND THE GATE THAT WAS PROPOSED IS THE "
            "WRONG ONE. Five admission rules, six accounts kept separately and never fused: the "
            "cold tiled loop spends %d, the ungated certificate %d, and the best rule `%s` %d — "
            "against a COMMITTED REFERENCE of %d over the same sixteen states. EVERY RULE IS "
            "UNDERWATER and the best is %d over. AND THE SINGLE-OWNER GATE LOSES TO NO GATE AT "
            "ALL: it spends %d against the ungated %d, because it declines the two- and "
            "three-owner tiles `voxfriction` measured as PROFITABLE and still pays the admission "
            "read on every tile it turns away. Sharing the overwhelming majority of a benefit is "
            "not being the whole of it. WHAT THE LEDGER SEPARATES IS THE CERTIFICATE FROM ITS "
            "SCAFFOLDING: the certificate retires %d against the loop it lives in and that is real "
            "work, while the TILED LOOP ITSELF costs %d over the reference before a single "
            "certificate is consulted — a tax %d times everything the certificate retires. NO "
            "IMPROVEMENT TO THE CERTIFICATE CAN CLOSE THAT. And the friction is a rounding error "
            "won in a way a gate is not usually for: the gate's whole gain over no gate is %d, "
            "under one per cent of both the certificate's retirement and the tax — and the best "
            "gate and NO gate EXECUTE THE IDENTICAL %d operations, so not one certificate is lost "
            "by gating and the entire gain is fallback, encode and verify that no longer happen. "
            "THE GATE DOES NOT CHOOSE WHICH CERTIFICATES TO EARN, IT PREDICTS WHICH ATTEMPTS ARE "
            "DOOMED, and the single-owner rule crosses that line the other way by declining tiles "
            "that would have SUCCEEDED. THE HYPOTHESIS THIS RUNG REFUTES EARNS NO "
            "PRE-REGISTRATION CREDIT, because it was never committed and pre-registration is "
            "COMMIT ORDER or it is nothing — the refutation stands on the measurement alone. THE "
            "PREDICTION THAT DOES SHIP EARLY IS ABOUT THE TILE SIZE, the parameter the tax is a "
            "function of and the one thing this arc has never varied"
            % (spend("none"), spend("all"), b, spend(b), ref, net(b),
               spend("one"), spend("all"), retired(b), scaffolding_tax(),
               scaffolding_tax() // max(retired(b), 1), gain, ledger(b)["execute"]))


def scene_case(name):
    if name == "ledger":
        return repr(tuple((r,) + tuple(ledger(r)[a] for a in ACCOUNTS) for r in RULES))
    if name == "breakeven":
        return repr(tuple((r, spend(r), retired(r), net(r)) for r in RULES)
                    + (scaffolding_tax(), VM.reference_cost(), best()))
    if name == "prediction":
        return prediction_text()
    raise VoxbreakError("VOXBREAK-REFUSE: no scene named %r" % name)


def scene_result(name):
    if name == "prediction":
        return prediction_digest()
    return hashlib.sha256(MAGIC + b"|" + name.encode() + b"|"
                          + scene_case(name).encode()).hexdigest()


SCENES = ("ledger", "breakeven", "prediction")


def golden(name):
    with open(os.path.join(_HERE, "conformance_voxbreak.txt"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                nm, dig = ln.split()
                if nm == name:
                    return dig
    raise VoxbreakError("VOXBREAK-REFUSE: no golden named %r" % name)
