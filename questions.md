# Pre-Submission Audit Questions

Answer each directly and specifically (file/function names, actual numbers,
actual test output) — not "yes it's handled," show how.

---

## A. Data Leakage / No-Leakage Guarantees

1. Show the actual code path that strips `phase`, `drift_weight`, and
   `is_rto` before a hypothesis function ever touches a dataframe. Is this
   enforced in ONE central place (e.g. `schema.py`'s sanitizer) that
   everything routes through, or could a new code path accidentally bypass
   it? How would we know if it did?

2. Confirm `held_out_test.csv` has been accessed exactly once, ever, across
   the whole project. Show the lock file's timestamp and PID. Has anything
   — a test, a debug script, a UI page — read that file a second time since
   the official evaluation?

3. For the `pincode_rolling_rto_rate` and `device_order_count_24h` features:
   confirm they're still computed using only past orders (no future/same-
   order leakage) in every place they're used now, not just in the original
   dataset generation script.

4. Are the decoy columns (`device_model_name`, `app_theme_color`) still
   present and still statistically independent of `is_rto` in the CURRENT
   version of the data, or did any later regeneration/re-ingestion step
   accidentally change this?

## B. Track 2 Alignment

5. Walk through the four bar clauses one more time against the CURRENT
   codebase (not the design doc's intentions): one class of loss, held-out
   test set, honest metrics incl. false-positive cost, strictly
   defense-only. Any drift between what's built now and what's documented?

6. Show a hypothesis (rule) whose rationale text was actually caught and
   rejected by the Defense-Only Audit Gate. If none exists yet, generate
   one deliberately and confirm the gate blocks it.

7. Is there anywhere in the system — UI, API, exported code — that could be
   read as "how to evade detection" rather than "what we watch for"? Do a
   pass specifically looking for this in the frontend copy, not just the
   backend rule text.

## C. Wiring / Are Features Actually Connected, or Just UI Shells?

8. The Spike Monitor and Human Review dashboard pages currently show all
   zeros / empty state. Confirm: is this because they're wired to LIVE
   data only (and nothing has streamed yet), or is there a bug preventing
   them from displaying the real batch results we already computed
   (the 2,537/51/53 held-out test routing split, 47.17% RTO concentration)?
   If it's the former, is there a way to load/display our actual computed
   results, not just live simulated traffic?

9. When the Drift Detector fires, does it pass the SPECIFIC failing orders
   to the next Generator/Reflector round as targeted examples, or does it
   just trigger a generic new evolution round with no memory of what
   caused the trigger? Same question for the Human Review Queue — do
   analyst-confirmed labels from review ever get fed back into training?

10. Does `check_and_rollback_on_outcomes()` ever, under any code path,
    read from `held_out_test.csv`? Show the guard that prevents this.

11. Is the Knowledge Graph's default view (`/lineage`) still scoped to a
    single clean evolution run, or could it currently show a mix of
    discarded/superseded runs (seeded rule, promo-leak rule, etc.) if a
    different `run_id` is selected or omitted?

## D. Consistency Between Claims and Artifacts

12. Do the numbers shown in the Shadow Control UI page match
    `shadow_control_results.json` exactly? Pull both and diff them.

13. Do the numbers shown anywhere in the frontend match the actual
    `final_held_out_test_results.json`? Or are any UI numbers hardcoded/
    stale from an earlier run?

14. Run the full test suite right now and report the exact current count
    (last known: 53/53). Any new failures or skips since then, and why?

## E. Final Bugs / Robustness

15. If the Generator produces a rule that references a column that doesn't
    exist (typo, hallucinated column name), what happens? Confirm this is
    caught by the sandbox/repair loop and doesn't crash anything.

16. What's the current total LLM API call count so far, and does it leave
    enough headroom under rate limits for the demo video recording
    (which may trigger live calls) plus any last-minute reruns before
    Sep 5?

17. If someone clones the repo fresh right now and follows the README, does
    it actually run end to end — dataset present, DB migrations documented,
    `.env.example` complete, no missing manual steps? Has this been tested
    on a clean checkout, or only ever run in the existing dev environment?