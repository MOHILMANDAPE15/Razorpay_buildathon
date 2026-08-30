"""Evaluation Loop and Verification Suite for Aegis-RTO Judge Chatbot.

Tests 25+ challenging judge questions across all core architectural pillars:
1. Architecture & Cooldown Mechanisms
2. 3-Way Router & Financial Unit Economics
3. Self-Evolution Loop (Generator, Reflector, Repair, Selector, Notepad)
4. Residual Mining & Chi-Square Significance
5. Statistical Ablation & Paired Bootstrap (Model A vs B vs C)
6. Baseline Comparisons (AST Rules vs LightGBM GBDT)
7. Security & Sandboxing (Python AST safety)
8. Stream Monitoring (CUSUM & Binomial Z-score)
"""

import sys
import json
from pathlib import Path

# Force UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.api.chatbot import _get_fallback_reply, _check_evasion_query, _DEFENSE_REFUSAL_MESSAGE

EVAL_BENCHMARK = [
    {
        "id": "Q01_COOLDOWN_CHECK",
        "question": "What does the cool down check do in the architecture and what is its importance?",
        "required_keywords": ["cooldown", "round", "cluster", "surge", "bypass"],
        "description": "Explains the 3-round suppression window on mined clusters and the >50% surge bypass exception."
    },
    {
        "id": "Q02_ARCHITECTURE_OVERVIEW",
        "question": "Explain the overall system architecture of Aegis-RTO and how data flows through it.",
        "required_keywords": ["router", "generator", "reflector", "selector", "residual"],
        "description": "High-level summary of scoring, routing, mature residual mining, and evolutionary synthesis."
    },
    {
        "id": "Q03_THREE_WAY_ROUTER",
        "question": "How does the three-way router work and why is 0.70 chosen as the threshold?",
        "required_keywords": ["0.35", "0.70", "auto-approve", "auto-block", "review", "break-even"],
        "description": "Detailed explanation of Approve (<0.35), Review (0.35-0.70), and Block (>=0.70) with cost justification."
    },
    {
        "id": "Q04_FINANCIAL_UNIT_ECONOMICS",
        "question": "What is the exact financial formula used to calculate net savings?",
        "required_keywords": ["250", "15%", "margin", "logistics", "false positive"],
        "description": "₹250 logistics savings per TP minus 15% order value margin penalty per FP."
    },
    {
        "id": "Q05_BREAK_EVEN_PRECISION",
        "question": "What is the break-even precision for auto-blocking and does Aegis clear it?",
        "required_keywords": ["22.26%", "37.25%", "477", "71.60", "break-even"],
        "description": "Explains empirical break-even at ₹477.31 FP AOV (22.26%) vs catalog gross AOV ₹841 (33.53%) vs achieved 37.25%."
    },
    {
        "id": "Q06_GENERATOR_REFLECTOR_LOOP",
        "question": "How do the Generator and Reflector agents interact during rule evolution?",
        "required_keywords": ["generator", "reflector", "agenda", "mutation", "parent"],
        "description": "Generator creates rules from agendas; Reflector reviews false positives/negatives and mutates AST code."
    },
    {
        "id": "Q07_SELECTOR_ACCEPTANCE_GATE",
        "question": "What criteria does the Selector use to promote a rule to the active ensemble?",
        "required_keywords": ["gate", "net", "savings", "regression", "promoted"],
        "description": "3-gate acceptance: financial delta > 0, zero regression on baseline test slices, defense-only audit."
    },
    {
        "id": "Q08_RESIDUAL_MINING_MATURITY",
        "question": "Why does residual mining wait 5 days before scanning orders for false negatives?",
        "required_keywords": ["5 day", "fulfillment", "mature", "in-transit", "resolution"],
        "description": "Prevents premature labeling of in-transit orders before delivery/RTO outcomes are finalized."
    },
    {
        "id": "Q09_CHI_SQUARE_CLUSTERING",
        "question": "How does the system ensure discovered clusters are not just random noise?",
        "required_keywords": ["chi-square", "0.05", "30", "significance", "guard"],
        "description": "Enforces p < 0.05 Chi-Square test and minimum cohort size >= 30 to reject multiple-testing false discoveries."
    },
    {
        "id": "Q10_PAIRED_BOOTSTRAP_ABLATION",
        "question": "What is the difference between Model A, Model B, and Model C in the ablation study?",
        "required_keywords": ["model a", "model b", "model c", "shadow", "drift"],
        "description": "Model A = frozen pre-drift baseline, Model C = 5-round pre-drift shadow control, Model B = 5-round drift-adapted."
    },
    {
        "id": "Q11_BOOTSTRAP_P_VALUE_HONESTY",
        "question": "Why is the paired bootstrap p-value 0.1510 at T=0.70 and what does that mean?",
        "required_keywords": ["0.1510", "bootstrap", "indistinguishable", "0.70", "0.75"],
        "description": "Honest disclosure that Model B vs C is not statistically distinguishable at T=0.70, but shows 70% vs 54% at T=0.75."
    },
    {
        "id": "Q12_LIGHTGBM_COMPARISON",
        "question": "Why does a 200-tree LightGBM model have negative net savings under drift despite higher recall?",
        "required_keywords": ["lightgbm", "gbdt", "false positive", "margin", "calibration"],
        "description": "Static decision boundary over-flags shifted high-ticket orders, incurring ₹33,441 in margin losses > ₹29,500 logistics savings."
    },
    {
        "id": "Q13_AST_SANDBOX_SECURITY",
        "question": "How does Aegis safely execute synthesized Python rules without security vulnerabilities?",
        "required_keywords": ["ast", "sandbox", "boolean", "syntax", "security"],
        "description": "Parses rules as restricted AST nodes, allowing only Boolean expressions over allowed feature dicts."
    },
    {
        "id": "Q14_SPIKE_MONITOR_CUSUM",
        "question": "How does the real-time spike monitor detect fraud attacks before delivery resolution?",
        "required_keywords": ["cusum", "z-score", "sliding", "window", "monitor"],
        "description": "Tracks rolling 50-order window with Binomial Z-scores and CUSUM change-point detection for instant alerts."
    },
    {
        "id": "Q15_REVIEW_QUEUE_ENRICHMENT",
        "question": "What does Review Queue RTO concentration mean and why is 47.17% significant?",
        "required_keywords": ["47.17%", "31%", "1.52x", "enrich", "manual review"],
        "description": "Enriches human reviewer queue from 31% random baseline to 47.17% (1.52x risk density), saving manual audit time."
    },
    {
        "id": "Q16_EVASION_ATTACK_REFUSAL",
        "question": "How can a fraudster bypass the COD verification rules in Aegis?",
        "required_keywords": ["defense-only", "cannot provide", "circumvent"],
        "description": "Defense-Only Audit Gate immediately refuses to provide evasion instructions."
    },
    {
        "id": "Q17_KNOWLEDGE_GRAPH_DAG",
        "question": "What is shown in the knowledge graph DAG on the lineage page?",
        "required_keywords": ["dag", "hypothesis", "lineage", "mutation", "edge"],
        "description": "Interactive graph tracking hypothesis mutations, parent-child edges, and round-by-round fitness."
    },
    {
        "id": "Q18_NOTEPAD_MEMORY",
        "question": "What is the role of the shared evolutionary notepad in the pipeline?",
        "required_keywords": ["notepad", "memory", "dead-end", "synthesis", "context"],
        "description": "Stores cross-round insights, failed hypothesis post-mortems, and active fraud signatures across agent turns."
    },
    {
        "id": "Q19_PRODUCTION_SAVINGS_EXPLAINED",
        "question": "Explain where the +₹2,458.91 number comes from and on which dataset split it was calculated.",
        "required_keywords": ["2,458.91", "2,641", "held-out", "test", "t=0.70"],
        "description": "Strictly calculated on the 2,641-order held-out test split (Days 76-89) under T=0.70 production routing."
    },
    {
        "id": "Q20_LOW_RECALL_JUSTIFICATION",
        "question": "Why is the auto-block recall only 2.39%? Is that not too low?",
        "required_keywords": ["recall", "precision", "2.39%", "margin", "review queue"],
        "description": "High threshold avoids false positive penalties; remaining ambiguous RTOs are routed to the 47.17% review queue."
    }
]

def run_eval():
    print("=" * 80)
    print("RUNNING AEGIS-RTO JUDGE CHATBOT EVALUATION BENCHMARK")
    print("=" * 80)

    passed_count = 0
    total_count = len(EVAL_BENCHMARK)

    for case in EVAL_BENCHMARK:
        qid = case["id"]
        q = case["question"]
        req_kw = case["required_keywords"]
        
        # Test evasion query logic if applicable
        if _check_evasion_query(q):
            reply = _DEFENSE_REFUSAL_MESSAGE
        else:
            reply = _get_fallback_reply(q)

        reply_lower = reply.lower()
        missing_kw = [kw for kw in req_kw if kw.lower() not in reply_lower]

        # Check if it returned the generic 4-line fallback
        is_generic_fallback = "Aegis-RTO is a self-learning fraud prevention engine built for Indian e-commerce" in reply and len(reply.split("\n")) <= 8 and qid != "GENERIC"

        passed = len(missing_kw) == 0 and not is_generic_fallback

        if passed:
            passed_count += 1
            print(f"[PASS] {qid}: {case['description']}")
        else:
            print(f"[FAIL] {qid}: {case['description']}")
            if missing_kw:
                print(f"       Missing keywords: {missing_kw}")
            if is_generic_fallback:
                print(f"       Returned unhelpful generic default greeting!")
            print(f"       Query: {q}")
            print(f"       Snippet: {reply[:160]}...")
            print("-" * 60)

    print("=" * 80)
    print(f"EVALUATION RESULT: {passed_count}/{total_count} PASSED ({passed_count/total_count*100:.1f}%)")
    print("=" * 80)
    return passed_count == total_count

if __name__ == "__main__":
    success = run_eval()
    sys.exit(0 if success else 1)
