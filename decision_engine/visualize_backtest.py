import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("backtest_results.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(df["timestamp"], df["cpu"], label="CPU", color="steelblue", alpha=0.7)

scale_up_points = df[df["action"] == "SCALE_UP"]
scale_down_points = df[df["action"] == "SCALE_DOWN"]

ax.scatter(scale_up_points["timestamp"], scale_up_points["cpu"], color="red", marker="^", s=80, label="SCALE UP", zorder=5)
ax.scatter(scale_down_points["timestamp"], scale_down_points["cpu"], color="green", marker="v", s=80, label="SCALE DOWN", zorder=5)

ax.set_xlabel("Zaman")
ax.set_ylabel("CPU Kullanimi (%)")
ax.set_title("Karar Motoru Backtest: CPU ve Scaling Kararlari")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("backtest_visualization.png")
plt.show()