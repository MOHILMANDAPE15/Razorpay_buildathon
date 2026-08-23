# RTO/COD Synthetic Dataset — Data Card

## What this is
Synthetic order-level data for the Razorpay Buildathon Track 2 (Return-risk scorer).
No public RTO/COD dataset exists, so records are fabricated — but the underlying
distributions are calibrated against published industry figures: COD RTO rate
25–35%, prepaid RTO rate under 2%, RTO loss concentrated in a repeat-offender /
device-abuse segment.

## Files
- `full_dataset_with_phase_labels.csv` — everything, including `phase` (for
  narrative/debugging only — **do not use as a model feature**, it's ground
  truth about the drift schedule, not something a real detector would know)
- `train.csv` — days 0–55 (10,807 orders)
- `validation.csv` — days 56–75 (3,885 orders)
- `held_out_test.csv` — days 76–89 (2,641 orders) — **touch this exactly once,
  at the very end, after the evolved ensemble is frozen**

## Split methodology
Chronological, not random. Fraud patterns evolve over time in this data (see
drift section below); a random split would let post-drift orders leak into
training and inflate validation scores artificially. Train-on-past /
validate-and-test-on-future mirrors how the system would actually be deployed.

## Schema
| Column | Description |
|---|---|
| `order_id`, `order_date`, `order_datetime`, `day_index` | identifiers / timing |
| `customer_id`, `is_first_time_customer`, `customer_account_age_days`, `customer_prior_orders` | customer history |
| `payment_mode` | COD or Prepaid |
| `order_value`, `item_category` | order details |
| `pincode`, `pincode_rolling_rto_rate` | location + **causal** rolling RTO rate (computed from past orders for that pincode only, cold-start prior = 0.15) |
| `promo_code_used` | promo abuse signal |
| `device_id`, `device_order_count_24h` | device reuse signal, **causal** (trailing 24h count using only past orders) |
| `order_hour` | hour of day (0–23) |
| `phase`, `drift_weight` | ground-truth drift schedule — **narrative/eval only, not a feature** |
| `is_rto` | target label (1 = returned to origin / abusive loss, 0 = fine) |

## Injected drift scenario
- **Days 0–50 (`pre_drift`)**: baseline pattern — risk driven by COD + first-time
  customer + pincode history + high order value.
- **Days 51–70 (`transition`)**: a new pattern ramps in linearly — promo-code
  stacking + device reuse (small ring-device pool reused more often as drift
  progresses) + late-night ordering.
- **Days 71–89 (`post_drift`)**: new pattern fully active.

Verified in generation output: RTO rate among (promo + device-reuse) orders
rises from ~50% pre-drift to ~89% post-drift, and device-reuse prevalence
rises from 0.0% → 2.5% of orders — confirming the injected pattern is real
and learnable, not just noise.

## Calibration result
| Split | COD RTO rate |
|---|---|
| Train | 26.1% |
| Validation | 30.7% |
| Held-out Test | 33.3% |

Within the real-world 25–35% band, and rising across splits as an emergent
property of the drift schedule (not manually forced per split).

## No-leakage guarantees
- `pincode_rolling_rto_rate` and `device_order_count_24h` are computed using
  only orders that occurred *before* the current order in time — never future
  orders, and never the current order's own label.
- The held-out test set is not touched during evolution, hypothesis scoring,
  or the LightGBM baseline's training — only for the final reported metrics.
