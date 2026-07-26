# The commuting-defect framework

**Design document. Section 6 is held private.** A rewrite of the URDRQCI1 proposal that keeps
its one real find and discards the rest. The find is worth keeping: it is the first framework in this thread that is
disciplined by construction rather than decorated with physics.

---

## 1. What the proposal gets right, and it is not small

Six things, and they are the reason this is a rewrite rather than a refutation.

It refuses metaphor. "No crystal metaphors, no Miller indices. Just measure the difference and
declare it. If it's too big, change the rendering, not the math." That sentence is the whole
discipline, correctly stated, and it is a genuine advance over the Lyndon/Clifford/Monge-Ampère
material.

It builds on S1 rather than inventing a foundation. It uses `lca_depth` and not `ctz`, which means
the correction propagated. It stores measured epsilons *in the conformance file* instead of asserting
them in prose. It attaches a falsification protocol to every claim, and each protocol has a stated
failure action — "if mean flip rate is 12%, we accept that and redesign." It grades itself
SPECULATIVE and says so at the top.

And most importantly it notices that the four remaining items **share a structure**. That observation
is correct and it is the thing worth building on. Everything below is an attempt to state it
precisely enough to be false.

---

## 2. The one real find, sharpened

The proposal says the four items are all "representation transitions" and asks whether the transition
commutes with property computation. That is a commuting square, and stating it as one makes the
framework smaller rather than larger:

```
        F  ──Q──▶  I
        │          │
       P_F        P_I
        │          │
        ▼          ▼
        A  ──q──▶  B
```

The square **commutes** iff `q(P_F(f)) = P_I(Q(f))` for every f. When it does not, the difference is
the **defect**, and the defect — not a checklist of unrelated epsilons — is the measurand.

This is a real simplification. The proposal has four independent constants (ε_S, ε_V, τ_G, a schema
version) with four unrelated protocols. There is one object: a square, and its defect.

### 2.1 The correction that makes it usable: units

The proposal's epsilons are in incompatible units — flip *rate* (dimensionless fraction), luminance
*delta* (normalized 0-1), a *z-score*, and a schema version. Mixing them is why they cannot compose.

**A defect must be measured in the codomain's own units, and for this arc the codomain is always
integers over sets.** That single rule fixes three of the four components, because it tells you the
proposal measured two of them in the wrong space:

| Item | Proposal's units | Correct units | Why |
|---|---|---|---|
| S2 | flip *rate* (float fraction) | **cells** (integer count) | a rate hides which cells; the adversary picks cells, not rates |
| S6 | luminance delta (float) | **resolvable opponents** (integer set difference) | see §3.2 — luminance is not information |
| S3 | schema version | **binding** (digest equality, boolean) | see §3.3 |
| S4 | z-score (float) | **cohort disagreement** (integer) | already shipped as URDRGEO1 |

Every corrected unit is exact-integer, which means defects compose by ordinary addition and the whole
framework stays inside the arc's no-floats-in-authority rule. The proposal's version cannot: a fraud
verdict computed from a float z-score is not reproducible across platforms, which is the exact desync
class `voxlat` exists to prevent.

### 2.2 The composition, stated so it can be false

The proposal's composition lemma is

> `π_I(Q(f₁),Q(f₂)) = 0 ∧ G_P(s,P) ≤ τ_G ⟹ π_S(f₁,f₂) ≈ 0`

which reads: identical lattices plus a passing quorum implies the originals were honest. **That
affirms the consequent.** Two *doctored* captures from the same attacker also quantize identically,
and a quorum passing means the cohort agreed, never that the cohort was right — `geoquorum`'s own
`does_not_show` says exactly this, and says further that k sybil identities defeat it outright.

The defensible composition runs the other way and bounds rather than concludes:

> **The total defect of a chain of squares bounds what an adversary can extract from the chain.**
> `defect(P ∘ Q) ≤ defect(P) + defect(Q)`, in cells, exactly.

That is subadditivity, it is provable in the integer setting, and it is *useful*: it says the budget
for quantization error and the budget for tier reduction come out of the same purse, so they cannot
be tuned independently. The proposal's four separate protocols implicitly assume they can.

---

## 3. The components, rebuilt

### 3.1 S2 — measure cells, not rates, and drop the Gaussian

Keep the protocol shape. Change three things.

Measure the **count** of flipped cells and their **spatial distribution**, not the mean rate. An
adversary does not attack the mean; a 2% flip rate concentrated on one wall face is a hole, and the
same rate scattered over a park is nothing. The quantity that matters is the largest *connected* run
of flipped cells, which is an integer and is what a player can walk through.

Drop `sigma=0.5` Gaussian noise. Capture error is view-dependent, correlated, and anisotropic —
worse behind the capture hemisphere, worse on specular and textureless surfaces. An iid Gaussian
model will report an optimistic epsilon and the optimism is not bounded. If a synthetic model must be
used, it should be **declared as a model**, and the honest sentence is that the resulting epsilon is
a lower bound on real divergence, not an estimate of it.

Do not use `np.percentile`. Order statistics on floats are not reproducible; `horn.tail_threshold`
already does exact integer order statistics and should be reused.

### 3.2 S6 — luminance is not information, and this is the proposal's biggest miss

The proposal measures `|luminance_high − luminance_low|` per pixel. That is the wrong quantity in
both directions, and the failure is easy to state:

- **Large luminance delta, zero asymmetry.** Two tiers with different fog colour differ on every
  pixel and neither can see anything the other cannot.
- **Tiny luminance delta, total asymmetry.** One tier renders foliage that hides a player silhouette;
  the other culls it. A handful of pixels differ. One client can shoot someone the other cannot see.

Information asymmetry is a question about **what is resolvable**, not about pixel values. The correct
defect is a set difference:

> For an opponent occupying lattice cell v, let `Vis_t ⊆ cells` be the set of cells a tier-t client
> can resolve an opponent in. The asymmetry defect is `|Vis_high △ Vis_low|` — an integer count of
> cells, decided by the same visibility predicate `perception` (URDRPCP1) already uses.

This lands S6 inside existing machinery instead of requiring a renderer in the gate, and it makes the
bound refusable: a tier pair whose defect exceeds the budget is not shipped, rather than logged as a
warning. The proposal explicitly declines to refuse here ("visual asymmetry is a warning, not a
refusal"), which given that this is a competitive shooter is the one place it should have refused.

### 3.3 S3 — the certificate must bind to the lattice, or it is decoration

Two defects in the proposed design, both fatal and both cheap to fix.

**The certificate is detachable.** `ProvenanceCertificate.digest()` hashes only the metadata fields.
Nothing binds a certificate to the geometry it certifies, so an attacker lifts the permissive
certificate off a public-domain block and staples it to a restricted capture. The fix is one line:
the commitment must be `H(cert ‖ lattice_digest)`, and the lattice digest must be recomputed at serve
time rather than trusted. That makes admissibility a **typed refusal** in the arc's sense instead of
a lookup that can be lied to.

**It contradicts its own claim.** The stated property is "decidable at serve time from embedded
provenance, no external lookup," and then `admissibility_check` calls
`distance_to_nearest_school(self.capture_location)` — an external lookup at serve time, on the hot
path, whose result can change between two serves of the same block. Either the buffer test is
evaluated **at capture time** and its result is a field inside the certificate (making it decidable
as claimed), or the claim is dropped. The first is right, and it has the additional virtue that the
buffer distance becomes part of what the digest commits to.

### 3.4 S4 — the proposed detector is blind by construction, and the shipped one is not

This is the sharpest error in the document and it is worth showing rather than describing. The
proposal detects fraud from `lca_depth` statistics between Morton **keys**. Measured:

```
honest submitter key 448  vs  liar key 449 :  lca_depth = 5
their occupancy sets      :  [0,1,2]  vs  [1,2]
shipped geoquorum verdict :  GEOQUORUM-DEVIATE
```

`lca_depth` measures **where a submitter is**, never **what they claim**. It is identical whether the
submitter lies or not, so a detector built on it cannot see a thinned wall — while it *will* flag an
honest contributor whose capture happens to sit in an unusual spatial position. It has the polarity
of the failure exactly inverted: blind to fraud, sensitive to geography.

The formula is also dimensionally broken independently of that. `expected_avg = 0.7 * 3 * max_levels`
gives 33.6 at `max_levels = 16`, while `lca_depth` returns a value in [0, 16]. The expected value
exceeds the maximum attainable value, so every honest submission scores maximally anomalous — TPR
100% and FPR 100%, a detector that flags everything.

The shipped `geoquorum` (URDRGEO1) compares **occupancy sets** by strict majority with the judged
party structurally excluded, and refuses the doctored submitter while admitting every honest member
of the same cohort. It is already gated. The proposal's Protocol 3 (calibrate τ from a ROC curve on
100 honest and 10 doctored submissions) should be discarded: a decided threshold beats a calibrated
one, and `geoquorum` decides its thresholds by enumeration — collusion at `ceil(k/2)`, false-positive
at `ceil((k−1)/2)` — rather than fitting them to a sample that an adversary can shift.

---

## 4. Three claims about the arc's own state that are wrong

**"Task 58B = geoquorum."** It is not. Task 58 Half B is making **commutation structural rather than
per-instance checked** — the `commute` (URDRCMU1) / `rannull` (RAN-0) / `nway` (URDRNWY1)
composition. Geoquorum is slice S4 of the city arc, and it shipped. This matters beyond bookkeeping,
because Half B is *the* item this framework should have connected to: §2's commuting square is
literally the object Half B is about, and the proposal walked past its own best result.

**"Position 33."** There is no position 33. The `33` was a git hook reporting the number of unpushed
commits on this cloud mirror, whose `origin` is a read-only proxy. The document builds an elaborate
"Layer 3 ← POSITION 33" structural theory, an unsatisfiability argument, and a dead-zone mitigation
on top of a commit counter. This is the same failure as the invented Lyndon foundation: an artifact
of the environment read as a fact about the system.

**The dead zone solves a problem this arc does not have.** There is no float player position to map.
Positions are Q32.32 fixed point, distances are squared integers, and `hitbox` adjudicates with exact
integer predicates — `_on_box` and `_on_ray` have no boundary ambiguity because there is no rounding.
Introducing a dead zone would *create* the flicker it claims to prevent, and `DEFER` during a
firefight is a gameplay failure, not a mitigation.

---

## 5. One more thing that would have failed the gate immediately

The conformance template ends with

```
last_measurement_run 2026-07-26T08:00:00Z
```

A timestamp in a conformance file makes "run twice, byte-identical" impossible by construction —
measured, two runs one second apart hash to `dc8e543a…` and `94fd480a…`. That is the single invariant
this whole apparatus rests on. Nothing in the arc's conformance files carries a clock, and the
`Date.now()`-style hazard is why. Provenance about *when* something was measured belongs in the D5
ledger, which is append-only history and explicitly exempt from the staleness checker.

The floats in the template have the same problem one layer down: `0.047`, `0.082`, `3.1` do not
round-trip identically across platforms and cannot be compared for equality in a gate. Express them
as exact rationals or as integer counts over an integer denominator, the way `horn` expresses its
relative costs as `Fraction(511, 513)`.

---

## 6. Build order — HELD PRIVATE

The ordering of remaining candidate slices is privileged and is deliberately not committed. One
conclusion from it is recorded here because it is a statement about work already named in this
repository rather than about unbuilt slices: **Task 58 Half B is the argument this framework makes
for itself.** If the commuting square of §2 can be made structural — commutation proven by
construction rather than checked per instance — then the squares it covers have defect zero *by
construction* instead of by measurement. That is strictly stronger than any number of calibrated
epsilons, and the proposal this rewrite responds to was one step from noticing it.
