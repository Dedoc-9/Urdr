# The out-of-band prior (URDROOB1): a design pass

A design-first record for the rung that closes URDRPNG1's declared cold-start residual. Composition over
`pingpolicy` (over `latencyest`, `clockauth`, `lagcomp`, `hitbox`, `perception`), no new glyph.

## OODA

**Observe.** URDRPNG1's monotone-disadvantage theorem is *conditional* on a session floor founded on a window
the client did not pad. A client padding every ack from connect founds an inflated floor and keeps a
permanently wider band. URDRPNG1 also said precisely why it could not close this itself: a cold-start padder is
**indistinguishable, from timing alone**, from a client on a genuinely slow path. At connect the server holds
no prior for that client, and refusing the padded one would refuse the honest laggy one identically.

**Orient.** That framing names the fix. The missing ingredient is not *more* timing evidence — no amount of it
separates the two — but evidence of a **different kind**. Other clients on the same route have already founded
honest floors. Those floors say what the route costs, and crucially the client being judged does not control
them.

**Decide.** Cap the founding floor by the cohort: `admissible = min(claimed, cohort_reference + TOLERANCE)`,
where the reference is the **lower median of peer floors**. A padder may still claim what it likes; the claim
is simply not believed past what its peers demonstrate. Three design constraints follow, and each is a law
below: the reference must be **leave-one-out** (the judged client cannot feed its own ruler), **robust** (a
minority of padded peers must not move it), and **per-route** (so corroborated slowness is believed).

**Act.** Built red-first; four gate rows (`oobprior`), a 120-cohort sweep, 22 falsifiers. The including-self,
mean-reference, and no-cap plants were each proven to bite before any golden was pinned.

## The laws

- **The neutral ruler, enforced structurally.** `cohort_reference(observations, cohort_key, exclude_client)`
  cannot *receive* the judged client's own observation — the exclusion lives in the function, not a comment. If
  a client's own rows fed the baseline it is measured against, the ruler would be built from the very quantity
  the adversary optimises: circular, and the cap would be theatre.
- **The cap, and what it is worth.** A padded founding claim is believed only to `reference + TOLERANCE`, and
  the reach that buys is measured against URDRPNG1 with no prior at all.
- **Fairness.** A genuinely slow client whose *peers are also slow* is **not** capped — the cohort encodes what
  that route costs. This is why the reference is per-route rather than one global constant: it keeps the prior
  from becoming a tax on distant players.
- **Bootstrap.** Below `MIN_COHORT` founded peers there is **no** prior; the claim stands and the rung falls
  back to URDRPNG1 alone, rather than inventing a reference from too little evidence.
- **Robustness.** The reference is a median, so a minority of padded peers cannot move it.
- **Proof-carrying.** The founding record is bound by digest to its exact cohort; a forged higher admissible
  floor, or the record replayed against a different cohort, fails.

## Exactly what the exclusion buys — measured, and not more

This rung's first draft assumed the leave-one-out exclusion was doing more work than it is, and the assumption
was corrected before landing:

- Against a **single** inflated self-observation the exclusion is belt-and-braces. The robust median already
  absorbs it — law and plant agree. Nothing is bought.
- Against **self-sybil** — a client flooding the pool with inflated rows under its **own id** — the exclusion is
  *load-bearing*: it drops every one of them and the reference is unmoved (6), while the including-self plant is
  dragged to 16 on the reference cohort. This is where it earns its keep.
- Against **other-sybil** — many *distinct* fake identities — the exclusion does nothing, because those rows are
  not the judged client's. That is the declared residual below.

## Measured, not assumed

Two properties are *counted* rather than asserted as universals, because asserting them universally would have
been false:

- **The prior never hurts** (universal, asserted), and **strictly reduces** a padder's reach in **86 of 120**
  sweep cases. Where URDRPNG1's rate limit binds before the padder's own ceiling, both land on the same reach
  and the prior is merely redundant.
- **A mean reference is inflated** by one outlier in **110 of 120** cases — it can coincide with the median
  under integer division. That is the case for a robust statistic, stated at its true strength.

Both carry fixed witnesses in the sweep, so neither can quietly become vacuous.

## The glyph verdict: NO new glyph (kernel frozen)

The prior is a leave-one-out median over peer floors the server already holds, plus a clamp — producing the
founding floor URDRPNG1 already consumes. No new primitive. Ruled against D1 §20: the kernel stays frozen. It
lives in `tools/`, never editing the kernel.

## Honest scope & boundaries (does_not_show)

- **The prior is only as honest as the cohort.** A **majority-poisoned** cohort — other-sybil or collusion on
  one route — moves the reference, and this rung does **not** defeat that. It is pinned as the
  `majority_poison` scene, witnessed in the sweep, and the successor is identity / sybil cost: again a
  different *kind* of evidence, not a better statistic.
- **Cohort assignment is server-derived** from the connection, but a client that can change apparent route
  (VPN, relay) chooses which baseline it is judged against. Declared, not solved.
- **An honest slow client in a fast cohort is capped** and under-compensated — the same deliberate fairness
  trade the session floor makes, favouring the defender.
- The transport, the identity layer, and cross-placement (Python reference only) are out of scope.

## Where this sits

The clock subsystem's last timing-only gap is now addressed with non-timing evidence: URDRHIT1 (where) ·
URDRLAG1 (when) · URDRCLK1 (which view-tick) · URDRLES1 (the measured clock) · URDRPNG1 (the measurement) ·
URDROOB1 (a prior the measured party does not control). What remains is an identity layer that would make
cohorts sybil-resistant — the one place the chain still rests on an assumption rather than a check.
