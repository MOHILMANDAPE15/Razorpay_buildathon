Concern 1 — the recall numbers look like a bug, not a signal

4.6% recall on the training set itself is the red flag. A model gets to see this data during training — getting only 4.6% recall on data it was fit to, when the RTO base rate is ~26%, isn't "the model struggling," it's almost always a threshold problem. Working backward from your precision/recall: your model is only flagging ~144 orders out of 10,807 total (~1.3%) as risky, when ~26% of orders are actually RTOs. That's not a conservative model, that's a broken one — most likely a default predict_proba > 0.5 cutoff on a class-imbalanced problem, without sweeping for the threshold that actually maximizes net Rs impact, or without scale_pos_weight/class_weight set during training.

Why this matters beyond just "the number is low": your entire drift-recovery story rests on the frozen-v1-vs-evolved comparison being a clean signal of drift, not of a pre-existing calibration bug. If v1 is already broken before drift even enters the picture, a sharp panelist could reasonably say "your baseline was crippled from the start — this isn't proof your system adapts to drift, it's proof a badly-thresholded model does worse than literally anything." That undercuts the exact thesis-proof section we built into the design doc.

Fix: sweep thresholds on validation data and pick the one that maximizes net financial impact (or F1, at minimum), rather than using the default 0.5 cutoff. Report that threshold explicitly as a stated methodology choice. Re-run the whole comparison after this fix — I'd expect train recall to jump substantially, and the honest drift-degradation story becomes much cleaner.

Concern 2 — possible identity conflation between two different comparisons

Going back to the design doc, there were supposed to be two distinct comparisons, not one:

Section 4.7 — Frozen Static Baseline: the evolved rule ensemble itself, frozen after training on pre-drift data only, then run against post-drift data. This is the literal thesis proof ("static rules miss evolving patterns").
Section 4.8 — LightGBM Baseline: a separate, standalone trained model, used only as an honest secondary benchmark ("why not just train a classifier").

What you've built calls the LightGBM model "v1 Static Baseline" and compares it against the self-evolved rule ensemble as "v2." That's actually the Section 4.8 comparison (rules vs. trained model), not the Section 4.7 comparison (frozen rules vs. re-evolved rules). Those prove two different things — one shows "our approach beats a standard ML baseline," the other shows "static logic decays, ours self-corrects." Right now it sounds like only the first one got built.

Question before you go further: is there still a separate frozen snapshot of the Generator/Reflector/Selector's own rule ensemble (trained pre-drift, never re-evolved) planned, to compare against the re-evolved version after the Drift Detector triggers? If that's still coming later in the pipeline, great, no issue — just flag it explicitly in your notes so it doesn't get lost, since it's the more important of the two comparisons for your actual pitch. If it got merged into this LightGBM work by mistake, worth splitting them apart now before the Reflector gets built on top of whichever one is intended to be "v1."