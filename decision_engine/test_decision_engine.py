# decision_engine/test_decision_engine.py
from decision_engine import ScalingDecisionEngine

def test_scale_up_triggered_when_cpu_high():
    engine = ScalingDecisionEngine(window_size=3, scale_up_threshold=70, cooldown_seconds=0)
    engine.evaluate(80)
    engine.evaluate(85)
    action, reason, details = engine.evaluate(90)
    assert action == "SCALE_UP"

def test_no_change_during_warmup():
    engine = ScalingDecisionEngine(window_size=5)
    action, reason, details = engine.evaluate(90)
    assert action == "NO_CHANGE"
    assert "isinma" in reason.lower()

def test_cooldown_blocks_repeated_action():
    engine = ScalingDecisionEngine(window_size=2, scale_up_threshold=70, cooldown_seconds=100)
    engine.evaluate(80)
    action1, _, _ = engine.evaluate(85)
    action2, _, _ = engine.evaluate(90)
    assert action1 == "SCALE_UP"
    assert action2 == "NO_CHANGE"  # cooldown yuzunden

if __name__ == "__main__":
    test_scale_up_triggered_when_cpu_high()
    test_no_change_during_warmup()
    test_cooldown_blocks_repeated_action()
    print("Tum testler basarili!")