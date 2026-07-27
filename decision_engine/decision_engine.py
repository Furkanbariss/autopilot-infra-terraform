from smoothing import MovingAverageTracker
from trend import detect_trend
from cooldown import CooldownManager


class ScalingDecisionEngine:
    def __init__(
        self,
        window_size=5,
        scale_up_threshold=70,
        scale_down_threshold=20,
        cooldown_seconds=120,
    ):
        self.tracker = MovingAverageTracker(window_size=window_size)
        self.cooldown = CooldownManager(cooldown_seconds=cooldown_seconds)
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.history_for_trend = []

    def evaluate(self, current_cpu):
        """
        Yeni bir CPU olcumu alir, karar dondurur.
        Donen deger: (action, reason, details)
        """
        self.tracker.add(current_cpu)
        self.history_for_trend.append(current_cpu)
        if len(self.history_for_trend) > 10:
            self.history_for_trend.pop(0)

        if not self.tracker.is_ready():
            return "NO_CHANGE", "Yeterli veri birikmedi (isinma periyodu)", {}

        avg_cpu = self.tracker.get_average()
        trend = detect_trend(self.history_for_trend)

        details = {
            "current_cpu": current_cpu,
            "avg_cpu": round(avg_cpu, 2),
            "trend": trend,
        }

        if not self.cooldown.can_act():
            return "NO_CHANGE", f"Cooldown aktif, kalan sure: {self.cooldown.remaining_cooldown():.0f}sn", details

        if avg_cpu > self.scale_up_threshold:
            self.cooldown.record_action()
            return "SCALE_UP", f"Ortalama CPU ({avg_cpu:.1f}) esik degerini ({self.scale_up_threshold}) asti", details

        if avg_cpu < self.scale_down_threshold and trend != "RISING":
            self.cooldown.record_action()
            return "SCALE_DOWN", f"Ortalama CPU ({avg_cpu:.1f}) esik degerinin ({self.scale_down_threshold}) altinda ve yukselme trendi yok", details

        return "NO_CHANGE", f"Ortalama CPU ({avg_cpu:.1f}) normal aralikta", details