Replace the seeded rule in v1_frozen_rules_snapshot.json — it can't be part of the
official submission artifact.

Rule 1 (hyp_v1_pincode_cod_baseline) was hand-seeded, not LLM-generated. The
unseeded verification run you just did (payment_mode == COD & is_first_time_customer
& pincode_rolling_rto_rate > 0.35) produced a cleaner result anyway — 7.00% recall
pre-drift collapsing to 0.00% post-drift. Use that path instead.

DO THIS:

1. Confirm the unseeded run actually exercised the full pipeline — multiple
   candidate hypotheses generated, Reflector attempting mutations, Selector
   choosing/pruning among them — not just one lucky Round 1 proposal with
   nothing to compare against. Re-run with more candidates per round if the
   original 2-round run didn't really exercise Generator+Reflector+Selector
   together.

2. Regenerate v1_frozen_rules_snapshot.json using ONLY this unseeded,
   multi-candidate run's output. Remove the seeded rule entirely — no
   human-authored rule should be in the official snapshot, even alongside
   an LLM one.

3. Report full cost-weighted numbers for the new snapshot on both splits
   (net ₹ savings, precision, recall, F1 — not just precision/recall like
   the last verification run showed). Don't assume train net savings is
   positive without checking — a previous round's net-₹ sign didn't move
   the same direction as precision/recall, so confirm this one directly.

4. Update the report/README to state plainly: this snapshot is 100%
   autonomously generated, zero seeded/hardcoded rules, so it's accurate
   if asked directly in the panel.

Output the final train-vs-validation table (precision, recall, F1, net ₹
savings) for the regenerated snapshot when done.