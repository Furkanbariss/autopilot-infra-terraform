def detect_trend(recent_values, threshold_pct=5):
    """
    Son degerlerin ilk yarisi ile ikinci yarisini karsilastirarak
    basit bir trend yonu belirler.
    """
    if len(recent_values) < 4:
        return "INSUFFICIENT_DATA"

    mid = len(recent_values) // 2
    first_half_avg = sum(recent_values[:mid]) / mid
    second_half_avg = sum(recent_values[mid:]) / (len(recent_values) - mid)

    if first_half_avg == 0:
        return "STABLE"

    change_pct = ((second_half_avg - first_half_avg) / first_half_avg) * 100

    if change_pct > threshold_pct:
        return "RISING"
    elif change_pct < -threshold_pct:
        return "FALLING"
    else:
        return "STABLE"


if __name__ == "__main__":
    rising_example = [20, 22, 35, 45, 55, 65]
    falling_example = [65, 55, 45, 35, 22, 20]
    stable_example = [40, 41, 39, 40, 42, 39]

    print("Yukselen ornek:", detect_trend(rising_example))
    print("Dusen ornek:", detect_trend(falling_example))
    print("Sabit ornek:", detect_trend(stable_example))