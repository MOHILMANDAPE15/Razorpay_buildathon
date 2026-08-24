from app.agents.generator import HypothesisGenerator
from app.data.loader import load_train_data

df = load_train_data().head(10)
gen = HypothesisGenerator()
candidates = gen.generate_hypotheses(
    n_hypotheses=2,
    notepad_summary="Cold start round",
    generation_round=1,
    df_sample=df,
)
print("Candidates generated:", len(candidates))
for c in candidates:
    print("Candidate:", c.name)
    print(c.code)
