import pandas as pd
import sys
sys.path.append(".")
from decision_engine import ScalingDecisionEngine

df = pd.read_csv("../forecasting/metrics_snapshot.csv")
df = df.dropna(subset=["cpu"]).reset_index(drop=True)

engine = ScalingDecisionEngine(
    window_size=5,
    scale_up_threshold=70,
    scale_down_threshold=20,
    cooldown_seconds=120,
)

results = []
for idx, row in df.iterrows():
    action, reason, details = engine.evaluate(row["cpu"])
    results.append({
        "timestamp": row["timestamp"],
        "cpu": row["cpu"],
        "action": action,
        "reason": reason,
        **details,
    })

results_df = pd.DataFrame(results)
results_df.to_csv("backtest_results.csv", index=False)

print("\n=== KARAR DAGILIMI ===")
print(results_df["action"].value_counts())
print(f"\nToplam degerlendirme: {len(results_df)}")