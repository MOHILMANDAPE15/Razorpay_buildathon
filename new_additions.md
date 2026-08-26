tell you model this to add in the doc 
Update the RTO/COD fraud engine design doc with a residual-driven evolution trigger.
Keep everything else in the doc as-is. Additions only — do not remove the Drift
Detector; this runs alongside it.

WHAT TO ADD

New component: Residual Miner (offline, runs on a schedule).
- Reads the Live Logging stream and collects orders the frozen ensemble got wrong,
  primarily false negatives (RTO/abuse that shipped and was not flagged).
- Clusters those misses and hands them to the Generator as the round's explicit
  agenda: "propose hypotheses targeting this specific miss cluster," rather than
  the current open-ended "propose something better."
- Rationale to state in the doc: the Drift Detector is an aggregate trigger — a new
  abuse pattern that is low in volume will not move PSI or rolling precision enough
  to fire it, but it will appear as a coherent false-negative cluster. Residual
  mining catches what drift detection structurally cannot. The two triggers are
  complementary, not alternatives.

Label maturity gate (new subsection under the Residual Miner).
- An order's true RTO/delivered status is only known after fulfillment resolves
  (days). The Residual Miner must only consider orders whose delivery window has
  closed. Cadence is tied to outcome maturity, not a fixed nightly timer.
- Without this, the miss pool is partially labeled and the false-negative count
  reads artificially low.

Acceptance gate — make this explicit and non-negotiable in the text.
- A hypothesis generated from a miss cluster is accepted ONLY on net cost-weighted
  fitness computed over the FULL validation set — never on accuracy or recall
  measured on the miss cluster itself.
- State the failure mode plainly: every rule written to catch misses also fires on
  some legitimate orders. A rule recovering 30 misses while adding 400 false
  positives must be rejected by the arithmetic automatically. Gating on
  "did we catch the previously-missed frauds" is a precision-destroying loop.
- Reuse the existing Section 4.2 cost terms (TP value Rs 150-300 avoided;
  FP cost = order_value x assumed margin). Promotion criterion is net rupee delta
  versus the incumbent ensemble on validation.
- Note that raw accuracy is unusable here: COD RTO base rate is ~26% and the two
  error costs are asymmetric, so accuracy stays flat while the economics go
  underwater.

Held-out test set — reinforce, do not weaken.
- The Residual Miner loop touches train (Generator/Reflector context) and
  validation (fitness) only. The held-out test set stays sealed until the final
  single scoring run. Add an explicit warning line that iterating this loop until
  the test number looks acceptable is test-set leakage and violates the track bar.

New guardrail: shipped-holdout against outcome censoring.
- The false-negative pool is only observable for orders that were actually shipped.
  Blocked or rejected orders never produce an outcome, so the system never learns
  whether they would have been RTO. Over successive rounds it trains on an
  increasingly self-selected slice of traffic and its own false positives become
  invisible to it.
- Mitigation to document: a small random exemption from blocking — a holdout of
  deliberately-shipped high-risk orders — to keep the observed outcome
  distribution unbiased.
- Even if this is only described rather than built, name it in the README. It is
  the first question a panelist with real fraud experience will ask.

Ensemble growth control.
- Note that appending a rule per miss cluster grows the ensemble and creates
  overlap indefinitely. Point at the existing mechanisms: Selector top-k pruning
  bounds the active population, and the Regression Suite requires that any new
  rule not break cases the previous ensemble already caught.

Also add to Section 10 (Anticipated Panel Questions):
- Q: How do you learn about frauds you blocked? A: shipped-holdout, per the
  censoring guardrail above.
- Q: Won't mining false negatives wreck your precision? A: acceptance is net
  cost-weighted fitness on full validation, not recall on the miss cluster.