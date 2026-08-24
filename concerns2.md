# Fix Plan: Circularity Guard, Confidence Intervals, Regression Tolerance, Defense Audit

Four issues found in the current implementation audit, ranked by severity. Fix in this order — the first one is the most damaging if left as-is.

---

## Issue 1 (Critical) — Generator prompt leaks the drift-pattern answer

### Root Cause
`generator.py`'s user prompt hard-codes rule targeting hints:
- Rule 1: "COD high-value risk or pincode history combinations"
- Rule 2: "Device reuse abuse (`device_order_count_24h`) or promo code stacking abuse"

These are **exactly** the signals injected into the synthetic drift pattern in the data generator (`promo_code_used`, `device_order_count_24h`, late-night ordering — see the logit formula with `drift_weight`). Telling the Generator to look for these before evolution even starts defeats the "discovery, not reverse-engineering" claim the design doc is built around (Section 5.4). If asked "how do we know the Generator found this, not that you told it to," the honest current answer is "we told it to" — which is the opposite of the intended answer.

### Fix
- Remove all rule-targeting hints from the Generator's user prompt in `prompts.py` / `generator.py`.
- Round 1 should receive only: the column schema, plain-language column descriptions, and general domain framing ("this is COD/RTO e-commerce order data, some orders are fraudulent or high-return-risk"). No mention of which columns or combinations matter.
- Later rounds may reference the Notepad's own history (what it already tried and learned) — that's fine, since that's the system's own discovered knowledge, not human-injected hints.

---

## Issue 2 (High) — Circularity guard from Section 5.4 was never built

### Root Cause
The design doc's Section 5.4 specifies two concrete guards against the Generator "reverse-engineering" the synthetic data generation logic:
1. **Decoy features** — columns with no true causal link to RTO risk (e.g. a cosmetic "device model name" field), used to check whether the evolved system ever assigns real fitness weight to something meaningless.
2. **Blinded column naming** — a second run where causal columns are renamed generically (`col_14` instead of `pincode_rto_rate`) to test whether the Generator finds real signal without the naming hint.

Neither exists yet in `schema.py`'s 17 permissible columns or anywhere else in the codebase.

### Fix
- Add 2-3 decoy columns to the dataset (e.g. `device_model_name`, `app_theme_selected`) with no causal relationship to `is_rto` in the generation logic. Add them to `PERMISSIBLE_FEATURE_COLUMNS` so the Generator can see and potentially use them.
- Build a second, blinded-naming variant of the dataset (or a config flag that renames causal columns to `col_14`, `col_22`, etc. before handing the schema to the Generator) for at least one comparison run.
- Report honestly in results/notes whether the Generator ever assigned fitness weight to a decoy, and whether it still found the real signal-bearing columns without semantic naming hints. This is meant to be evidence you can point to, not just a described intention.

---

## Issue 3 (Medium) — No confidence intervals on evaluation metrics

### Root Cause
The design doc's prepared answer to "isn't precision/recall unstable with a small fraud class?" is k-fold or bootstrapped validation with confidence intervals reported on final metrics. `evaluator.py` currently only returns single-point precision/recall/F1/net-₹ — no CI logic anywhere.

### Fix
- Add a `evaluate_hypothesis_bootstrap(hypothesis, df, n_bootstrap=200)` method (or k-fold equivalent) that resamples the validation set and returns mean ± std (or a percentile-based CI) for precision, recall, F1, and net financial impact.
- At minimum, run this once on the final chosen ensemble before reporting held-out test numbers, so the reported metrics have an honest uncertainty range attached rather than being single-point estimates.

---

## Issue 4 (Medium) — Regression gate has zero tolerance with no noise buffer

### Root Cause
`RegressionHarness`'s `max_cost_drop_tolerance_inr = 0.0` means a candidate that scores even ₹1 below the previous best on net savings fails Gate 1 outright. Without the confidence intervals from Issue 3, there's no way to tell whether a small drop is real regression or just sampling noise between rounds — a fine candidate could get rejected for the wrong reason.

### Fix
- Once Issue 3's bootstrap/CI method exists, set the regression tolerance relative to the baseline's own confidence interval (e.g. fail only if the candidate's net savings falls outside the baseline's CI lower bound) rather than a hard ₹0 cutoff.
- Until CIs are wired in, at minimum add a small stated tolerance band (e.g. ±₹500, or ±2% of baseline net savings) instead of literal zero, and document that this is a placeholder pending the CI-based version.

---

## Issue 5 (Low, naming/consistency only) — Defense-Only Audit Gate is mislabeled

### Root Cause
The pending-items list describes a "Defense-Only Audit Gate" that "blocks high-FP rules regardless of recall" — that's a fitness/quality check, not the audit Section 6 of the design doc specifies (a keyword/pattern pass plus a second LLM-judge call checking each hypothesis's plain-English rationale for evasion-instructional content, e.g. "how to structure an order to avoid detection"). This gate maps directly to the track's literal disqualification clause ("strictly defense-only"), so it needs to be the actual described mechanism, not a differently-scoped check with the same name.

Also: gate numbering has drifted. Design doc: Gate 1 = Regression Suite, Gate 2 = Held-out test report, Gate 3 = Defense-only Audit. Current pending list calls the audit "Gate 2." Reconcile before this shows up inconsistently in the README or video.

### Fix
- Rename the existing high-FP-blocking check to something like `QualityFilter` or fold it into `RulePruner` (it already resembles the precision-floor pruning `RulePruner` does) — don't call it the Defense-Only Audit.
- Build the actual Defense-Only Audit as its own component: (1) a keyword/pattern first-pass over rule code and rationale text, (2) a second, separate LLM call prompted specifically to flag evasion-instructional content in the rationale, before any version is promoted.
- Standardize gate numbering to match the design doc (Gate 1 = Regression, Gate 2 = Held-out test, Gate 3 = Defense-only Audit) across code, comments, and any docs/README.

---

## Verification Plan

After all five fixes:
1. Re-run a fresh Generator round with the stripped prompt and confirm (by reading the raw LLM output) that no rule-targeting hints appear in what it was given — only schema + domain framing.
2. Run one evolution pass on the decoy + blinded-naming dataset variant; confirm in the Notepad output whether any decoy ever scored positive fitness, and whether real signal columns were still found without semantic names.
3. Confirm `evaluate_hypothesis_bootstrap` (or k-fold equivalent) returns a mean ± CI, and that the final reported held-out metrics include this range, not just point estimates.
4. Confirm Gate 1 now uses a tolerance band (CI-based or stated placeholder) instead of a hard ₹0 cutoff, and that a candidate within noise range of the baseline no longer fails purely on rounding.
5. Confirm the Defense-Only Audit gate exists as its own component with the keyword-pass + LLM-judge mechanism, separate from the high-FP quality filter, and that gate numbering is consistent everywhere (code, comments, README).