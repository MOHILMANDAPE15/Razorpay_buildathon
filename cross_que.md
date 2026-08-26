Update the RTO/COD fraud engine design doc with a cooldown mechanism for the
Residual Miner. Keep everything else in the doc as-is. Additions only — do not
remove or restructure the Residual Miner or Selector sections; this is a new
subsection under the Residual Miner.

WHAT TO ADD

New subsection: Miss-Cluster Cooldown (under Residual Miner).
- Problem to state explicitly: a hypothesis proposed against a mined miss
  cluster can be accepted one round and then pruned in a later round by the
  Selector's top-k/N-rounds-unused rule — for reasons unrelated to that
  cluster (a stronger competing hypothesis, ensemble reshuffling). Without a
  cooldown, the same cluster gets re-mined and re-proposed to the Generator
  indefinitely every scheduled Residual Miner run, wasting LLM budget and
  cluttering the Notepad with near-duplicate lineage.
- Mechanism: when a hypothesis whose lineage traces to a specific miss cluster
  is pruned, tag that cluster_id with a cooldown of N rounds (reuse the same N
  as Selector's unused-pruning window, Section 4.4, for consistency) before
  the Residual Miner is allowed to re-surface it as an agenda item.
- Exception: cooldown is bypassed if the cluster's miss volume grows by a
  stated threshold (e.g. >50% more realized false negatives than when it was
  last mined) — a cooling-down cluster that is visibly getting worse should
  not be silently ignored until the timer expires.
- State the failure mode being prevented plainly, one sentence: without this,
  a rejected or pruned cluster consumes a full Generator/Reflector round on
  every subsequent Residual Miner scan with no new information, which is
  wasted LLM budget under the cap set in Section 9.2.

Also add to Section 10 (Anticipated Panel Questions):
- Q: What stops the same miss cluster from being re-proposed every round after
  it's rejected or pruned? A: cooldown window on cluster_id, same N as
  Selector's unused-pruning window, bypassed only if miss volume worsens
  significantly since last mined.