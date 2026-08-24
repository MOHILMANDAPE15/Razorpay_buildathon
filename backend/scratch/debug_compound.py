from app.core.llm import get_llm_client
from app.agents.generator import HypothesisGenerator
from app.data.loader import load_train_data

df = load_train_data().head(10)
gen = HypothesisGenerator()
print("Generator LLM model:", gen.llm.model_name if hasattr(gen.llm, "model_name") else gen.llm.model)
candidates = gen.generate_hypotheses(
    n_hypotheses=2,
    notepad_summary="Cold start round",
    generation_round=1,
    df_sample=df,
)
print("Candidates:", len(candidates))
for c in candidates:
    print(c.name, ":", c.code)
