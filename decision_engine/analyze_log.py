import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("autoscaler_log.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

print("=== KARAR DAGILIMI ===")
print(df["action"].value_counts())
print(f"\nToplam karar dongusu: {len(df)}")
print(f"Ortalama CPU: {df['current_cpu'].mean():.2f}")
print(f"Maksimum desired_count: {df['desired_count_after'].max()}")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

ax1.plot(df["timestamp"], df["current_cpu"], label="Anlik CPU", color="steelblue", alpha=0.6)
ax1.plot(df["timestamp"], df["avg_cpu"], label="Hareketli ortalama", color="darkorange")
ax1.axhline(y=70, color="red", linestyle="--", alpha=0.5, label="Scale up esigi")
ax1.axhline(y=20, color="green", linestyle="--", alpha=0.5, label="Scale down esigi")
ax1.set_ylabel("CPU (%)")
ax1.legend()
ax1.set_title("Autoscaler Davranisi: CPU ve Esikler")

ax2.step(df["timestamp"], df["desired_count_after"], where="post", color="purple")
ax2.set_ylabel("Task sayisi")
ax2.set_xlabel("Zaman")
ax2.set_title("desired_count Degisimi")

plt.tight_layout()
plt.savefig("autoscaler_behavior.png")
plt.show()