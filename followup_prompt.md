Update the dynamic residual mining implementation (backend/app/engine/residual_miner.py,
backend/app/db/models.py, backend/tests/test_residual_miner.py). Additions and targeted
fixes only — do not remove the existing dynamic subgroup discovery, the
MissClusterCooldown table, or the surge-bypass logic. This adds a statistical
significance guard, a fallback path, and clarifies agenda generation.

WHAT TO ADD

1. Significance guard on subgroup discovery (in cluster discovery, before a
   subgroup is allowed to become a cluster_id):
   - Cap conjunction depth: a discovered subgroup may combine at most 3 features.
     Reject any candidate combining more, even if it clears the lift threshold —
     deeper conjunctions overfit to small samples by construction.
   - Require a minimum cohort size (total orders matching the subgroup
     signature, not just miss count) before lift is even computed — e.g.
     cohort_size >= 30 — so a "1.35x lift" isn't being computed on 5 misses
     out of 6 total orders.
   - Add a significance check: a chi-square test (or permutation test) of the
     subgroup's RTO rate against the mature-cohort baseline rate. Only clusters
     with p < 0.05 (or your chosen threshold) are eligible to be surfaced as a
     Generator agenda item. Log rejected high-lift-but-not-significant
     candidates separately (for debugging/demo transparency) rather than
     silently dropping them.
   - State the rationale inline as a code comment: with 8 features and
     quantile thresholds searched combinatorially, some conjunctions will
     clear a raw lift bar by chance alone (multiple-testing problem) — this
     guard is the same discipline the design doc already applies to decoy
     features, applied to the miner's own search process.

2. Fallback path — keep the original 3 hardcoded clusters as a documented,
   switchable fallback rather than deleting them:
   - Move the original hardcoded cluster_promo_cod_burst /
     cluster_late_night_impulse / cluster_low_value_impulse_cod logic into a
     separate function (e.g. static_fallback_clusters()), not deleted.
   - Add a config flag (e.g. RESIDUAL_MINER_MODE = "dynamic" | "static") that
     switches which path runs. Default to "dynamic" but document in a code
     comment and in the README that "static" is the safe, pre-validated
     fallback if the dynamic miner produces unstable or low-quality clusters
     close to submission.
   - Add one test (test_static_fallback_mode_runs_end_to_end) confirming the
     static path still executes cleanly through the full miner -> cooldown ->
     Generator pipeline unchanged.

3. Clarify agenda-text generation (currently unspecified in the plan):
   - State explicitly, in code and in a doc comment, whether the descriptive
     agenda string handed to the Generator for a dynamically-discovered
     cluster is (a) templated deterministically from the feature signature
     (no LLM call), or (b) produced by an LLM call. Pick (a) — deterministic
     templating from the signature dict — unless there's a specific reason to
     spend an LLM call on it; this keeps the miner's own discovery step free
     of LLM cost, reserving calls for the actual Generator/Reflector loop per
     Section 9.2's budget cap.
   - Add a test confirming the templated agenda string contains every
     feature/value pair from the cluster's signature (no silent truncation).

4. Cooldown row creation fix:
   - In apply_cooldown / cluster creation, confirm cooldown_until_round is
     always set explicitly to current_round + N at insert time, never left to
     the column default — add a test
     (test_new_cluster_not_born_on_cooldown) asserting a freshly-discovered
     cluster's cooldown_until_round <= current_round (i.e. immediately
     eligible), not pre-cooled by the schema default.

5. Regression confirmation:
   - After these changes, re-run the full existing test suite and confirm the
     "58 tests passing" count is still accurate post-change; if the count
     changed, update the number wherever it's cited (docs, comments, README).