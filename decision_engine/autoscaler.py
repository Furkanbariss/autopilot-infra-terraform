import sys
import time
from decision_engine import ScalingDecisionEngine
from metrics_client import get_current_cpu
from ecs_client import get_service_status, scale
from audit_logger import log_decision

CHECK_INTERVAL_SECONDS = 30
DRY_RUN = False 

def main():
    engine = ScalingDecisionEngine(
        window_size=3,
        scale_up_threshold=70,
        scale_down_threshold=20,
        cooldown_seconds=180,
    )

    mode = "DRY RUN" if DRY_RUN else "CANLI"
    print(f"Autoscaler basladi — mod: {mode}")
    print(f"Kontrol araligi: {CHECK_INTERVAL_SECONDS} saniye\n")

    try:
        while True:
            cpu= get_current_cpu()

            if cpu is None:
                print("CloudWatch'tan veri gelmedi, bu dongu atlaniyor.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            action, reason, details = engine.evaluate(cpu)
            count_before = get_service_status()["desired_count"]

            if action != "NO_CHANGE" and not DRY_RUN:
                count_after = scale(action)
            else:
                count_after = count_before

            row = log_decision(cpu, details, action, reason, count_before, count_after)

            print(f"[{row['timestamp']}] CPU={cpu:.1f} avg={details.get('avg_cpu')} " f"trend={details.get('trend')} -> {action} ({reason})")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nAutoscaler durduruldu.")
        sys.exit(0)

if __name__ == "__main__":
    main()