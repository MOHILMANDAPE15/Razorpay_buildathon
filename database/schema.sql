-- Aegis-RTO PostgreSQL Database Schema
-- Defines physically isolated order tables (train, validation, held_out_test),
-- evolution run tracking, rule memory, lineage graphs, evaluation reports, and live scoring logs.

-- 1. ORDERS TRAIN TABLE (Days 0-55: Baseline Pattern)
CREATE TABLE IF NOT EXISTS orders_train (
    order_id VARCHAR(64) PRIMARY KEY,
    order_date DATE NOT NULL,
    order_datetime TIMESTAMP NOT NULL,
    day_index INTEGER NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    is_first_time_customer BOOLEAN NOT NULL,
    customer_account_age_days INTEGER NOT NULL,
    customer_prior_orders INTEGER NOT NULL,
    payment_mode VARCHAR(16) NOT NULL,
    order_value NUMERIC(10, 2) NOT NULL,
    item_category VARCHAR(64) NOT NULL,
    pincode VARCHAR(16) NOT NULL,
    pincode_rolling_rto_rate NUMERIC(6, 4) NOT NULL,
    promo_code_used BOOLEAN NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    device_order_count_24h INTEGER NOT NULL,
    order_hour INTEGER NOT NULL,
    phase VARCHAR(32) DEFAULT 'pre_drift',
    drift_weight NUMERIC(6, 4) DEFAULT 0.0,
    is_rto INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Circularity guard decoy columns (Section 5.4): random, NO causal link to is_rto
    device_model_name VARCHAR(64),
    app_theme_color VARCHAR(16)
);

CREATE INDEX IF NOT EXISTS idx_train_customer ON orders_train(customer_id);
CREATE INDEX IF NOT EXISTS idx_train_pincode ON orders_train(pincode);
CREATE INDEX IF NOT EXISTS idx_train_device ON orders_train(device_id);


-- 2. ORDERS VALIDATION TABLE (Days 56-75: Injected Drift Ramp-In)
CREATE TABLE IF NOT EXISTS orders_validation (
    order_id VARCHAR(64) PRIMARY KEY,
    order_date DATE NOT NULL,
    order_datetime TIMESTAMP NOT NULL,
    day_index INTEGER NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    is_first_time_customer BOOLEAN NOT NULL,
    customer_account_age_days INTEGER NOT NULL,
    customer_prior_orders INTEGER NOT NULL,
    payment_mode VARCHAR(16) NOT NULL,
    order_value NUMERIC(10, 2) NOT NULL,
    item_category VARCHAR(64) NOT NULL,
    pincode VARCHAR(16) NOT NULL,
    pincode_rolling_rto_rate NUMERIC(6, 4) NOT NULL,
    promo_code_used BOOLEAN NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    device_order_count_24h INTEGER NOT NULL,
    order_hour INTEGER NOT NULL,
    phase VARCHAR(32) DEFAULT 'transition',
    drift_weight NUMERIC(6, 4) DEFAULT 0.5,
    is_rto INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Circularity guard decoy columns (Section 5.4): random, NO causal link to is_rto
    device_model_name VARCHAR(64),
    app_theme_color VARCHAR(16)
);

CREATE INDEX IF NOT EXISTS idx_val_customer ON orders_validation(customer_id);
CREATE INDEX IF NOT EXISTS idx_val_pincode ON orders_validation(pincode);
CREATE INDEX IF NOT EXISTS idx_val_device ON orders_validation(device_id);


-- 3. ORDERS HELD-OUT TEST TABLE (Days 76-89: Post-Drift - Single-Touch Locked)
CREATE TABLE IF NOT EXISTS orders_held_out_test (
    order_id VARCHAR(64) PRIMARY KEY,
    order_date DATE NOT NULL,
    order_datetime TIMESTAMP NOT NULL,
    day_index INTEGER NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    is_first_time_customer BOOLEAN NOT NULL,
    customer_account_age_days INTEGER NOT NULL,
    customer_prior_orders INTEGER NOT NULL,
    payment_mode VARCHAR(16) NOT NULL,
    order_value NUMERIC(10, 2) NOT NULL,
    item_category VARCHAR(64) NOT NULL,
    pincode VARCHAR(16) NOT NULL,
    pincode_rolling_rto_rate NUMERIC(6, 4) NOT NULL,
    promo_code_used BOOLEAN NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    device_order_count_24h INTEGER NOT NULL,
    order_hour INTEGER NOT NULL,
    phase VARCHAR(32) DEFAULT 'post_drift',
    drift_weight NUMERIC(6, 4) DEFAULT 1.0,
    is_rto INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Circularity guard decoy columns (Section 5.4): random, NO causal link to is_rto
    device_model_name VARCHAR(64),
    app_theme_color VARCHAR(16)
);

CREATE INDEX IF NOT EXISTS idx_test_customer ON orders_held_out_test(customer_id);
CREATE INDEX IF NOT EXISTS idx_test_pincode ON orders_held_out_test(pincode);
CREATE INDEX IF NOT EXISTS idx_test_device ON orders_held_out_test(device_id);


-- 4. EVOLUTION RUNS TABLE
CREATE TABLE IF NOT EXISTS evolution_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    total_rounds INTEGER NOT NULL,
    hypotheses_tested INTEGER NOT NULL DEFAULT 0,
    initial_best_net_savings_inr NUMERIC(12, 2) DEFAULT 0.0,
    final_best_net_savings_inr NUMERIC(12, 2) DEFAULT 0.0,
    net_savings_delta_inr NUMERIC(12, 2) DEFAULT 0.0,
    champion_hypothesis_id VARCHAR(64),
    status VARCHAR(32) DEFAULT 'RUNNING'
);


-- 5. HYPOTHESES (RULE MEMORY) TABLE
CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id VARCHAR(64) PRIMARY KEY,
    run_id VARCHAR(64) REFERENCES evolution_runs(run_id) ON DELETE SET NULL,
    generation_round INTEGER NOT NULL DEFAULT 1,
    name VARCHAR(255) NOT NULL,
    target_signal VARCHAR(64),
    description TEXT,
    rationale TEXT,
    rule_code TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'candidate',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hyp_status ON hypotheses(status);
CREATE INDEX IF NOT EXISTS idx_hyp_round ON hypotheses(generation_round);


-- 6. HYPOTHESIS LINEAGES (KNOWLEDGE GRAPH EDGES)
CREATE TABLE IF NOT EXISTS hypothesis_lineages (
    id BIGSERIAL PRIMARY KEY,
    parent_hypothesis_id VARCHAR(64) REFERENCES hypotheses(hypothesis_id) ON DELETE CASCADE,
    child_hypothesis_id VARCHAR(64) REFERENCES hypotheses(hypothesis_id) ON DELETE CASCADE,
    relationship_type VARCHAR(32) NOT NULL DEFAULT 'mutated_from',
    mutation_strategy TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lineage_parent ON hypothesis_lineages(parent_hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_lineage_child ON hypothesis_lineages(child_hypothesis_id);


-- 7. EVALUATION REPORTS (FINANCIAL & STATISTICAL PERFORMANCE)
CREATE TABLE IF NOT EXISTS evaluation_reports (
    report_id BIGSERIAL PRIMARY KEY,
    hypothesis_id VARCHAR(64) REFERENCES hypotheses(hypothesis_id) ON DELETE CASCADE,
    dataset_split VARCHAR(32) NOT NULL,
    precision NUMERIC(6, 4) NOT NULL,
    recall NUMERIC(6, 4) NOT NULL,
    f1_score NUMERIC(6, 4) NOT NULL,
    accuracy NUMERIC(6, 4) NOT NULL,
    flag_rate NUMERIC(6, 4) NOT NULL,
    total_orders INTEGER NOT NULL,
    true_positives INTEGER NOT NULL,
    false_positives INTEGER NOT NULL,
    true_negatives INTEGER NOT NULL,
    false_negatives INTEGER NOT NULL,
    avoided_rto_loss_inr NUMERIC(12, 2) NOT NULL,
    false_positive_insult_cost_inr NUMERIC(12, 2) NOT NULL,
    net_financial_savings_inr NUMERIC(12, 2) NOT NULL,
    cost_efficiency_ratio NUMERIC(8, 2) NOT NULL,
    gate_1_status VARCHAR(16) DEFAULT 'PASSED',
    gate_1_reasons JSONB DEFAULT '[]'::jsonb,
    evaluated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_eval_hyp ON evaluation_reports(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_eval_split ON evaluation_reports(dataset_split);


-- 8. SCORING LOGS (ONLINE LIVE STREAM & DRIFT ANALYTICS)
CREATE TABLE IF NOT EXISTS scoring_logs (
    log_id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL,
    active_hypothesis_id VARCHAR(64) REFERENCES hypotheses(hypothesis_id) ON DELETE SET NULL,
    risk_score NUMERIC(6, 4),
    decision VARCHAR(32) NOT NULL,
    decision_latency_ms NUMERIC(8, 2),
    is_flagged BOOLEAN NOT NULL,
    ground_truth_outcome VARCHAR(32) DEFAULT 'PENDING',
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON scoring_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_decision ON scoring_logs(decision);


-- 9. HUMAN REVIEW QUEUE (LOW-CONFIDENCE ROUTING)
CREATE TABLE IF NOT EXISTS human_review_queue (
    review_id BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL,
    risk_score NUMERIC(6, 4) NOT NULL,
    triggered_signals JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(32) DEFAULT 'PENDING',
    analyst_notes TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_status ON human_review_queue(status);
