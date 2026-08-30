Replace the text-heavy comparison cards on /shadow-control and /mining
with bar and line charts, using the existing chart library already in the
project. Do NOT remove, hide, or omit any model, cluster, or figure --
every number currently shown in text form must still be present, just
rendered visually instead of as prose/stat lists. This includes numbers
that make Aegis look worse than an alternative (e.g. Model C's precision
or net savings exceeding Model B's) -- those stay, unchanged, same
prominence as any other bar.

PART A: /shadow-control

1. Replace the 3-way Model A/B/C text cards with a grouped bar chart:
   x-axis = Model A / Model C / Model B, grouped bars per metric
   (Precision, Recall, Net Savings -- net savings on its own bar/axis
   given different scale). Use neutral, identical bar coloring across all
   three models -- no color implying winner/loser (e.g. do not make one
   green and others grey).

2. Add a line chart showing net savings across the 3-phase trajectory:
   Genesis baseline (training) -> Drift shock (validation, pre-adaptation)
   -> Evolved/mutated (validation, post-adaptation). Use ONLY the already-
   verified figures for this (Genesis ~Rs 24,312 training savings, Drift
   collapse ~Rs 6,567 validation, Evolved ~Rs 22,734 validation) -- and
   keep the same honest framing already established on the Overview page:
   a caption or footnote noting the bootstrap test could not statistically
   confirm this recovery is specifically drift-adaptation vs. additional
   rounds, linking to the significance panel. Do not present this line
   chart as a standalone triumphant claim without that caveat visible on
   the same view.

3. Keep the paired bootstrap CI panel (point estimate, 95% CI, "not
   statistically distinguishable at T=0.70") as-is or convert to a simple
   error-bar/CI visual if it improves clarity -- do not remove or shrink
   its prominence relative to before.

4. Keep the LightGBM comparison section, converted to a bar chart
   (Aegis vs LightGBM: precision, recall, net savings side by side),
   including LightGBM's higher raw precision/recall numbers -- unchanged,
   full prominence.

PART B: /mining

5. Replace each discovered cluster's stat block (miss volume, cohort
   size, lift) with a small bar chart per cluster, or one combined bar
   chart comparing both discovered clusters side by side on the same
   three metrics.

6. Add a chart for the significance guard section: a simple bar or dot
   plot showing all 4 candidates (2 accepted, 2 rejected) with their
   p-values against the p=0.05 threshold line, so the guard's filtering
   is visually obvious rather than read from text. Keep the 2 rejected
   candidates fully visible and labeled, same as the accepted ones -- do
   not visually de-emphasize or omit them.

Report back with a screenshot of each new chart before wiring into the
live pages.