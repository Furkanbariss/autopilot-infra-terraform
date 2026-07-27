from collections import deque

class MovingAverageTracker:
    """
    Son N olcumun ortalamasini tutan basit bir yapi.
    Ani sicramalari yumusatmak icin kullanilir.
    """
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    def add(self, value):
        self.history.append(value)

    def get_average(self):
        if len(self.history) == 0:
            return None
        return sum(self.history) / len(self.history)

    def is_ready(self):
        # Guvenilir bir ortalama icin en az window_size kadar veri istiyoruz
        return len(self.history) == self.window_size


# Hizli test
if __name__ == "__main__":
    tracker = MovingAverageTracker(window_size=5)
    test_values = [20, 22, 21, 75, 23]  # 75, tek seferlik bir sicrama (spike)

    for v in test_values:
        tracker.add(v)
        print(f"Eklenen: {v}, Ortalama: {tracker.get_average():.2f}, Hazir mi: {tracker.is_ready()}")