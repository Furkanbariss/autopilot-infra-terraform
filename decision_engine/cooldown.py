import time

class CooldownManager:
    """
    Bir scaling aksiyonundan sonra belirli bir sure boyunca
    yeni aksiyon alinmasini engeller.
    """
    def __init__(self, cooldown_seconds=120):
        self.cooldown_seconds = cooldown_seconds
        self.last_action_time = None

    def can_act(self):
        if self.last_action_time is None:
            return True
        elapsed = time.time() - self.last_action_time
        return elapsed >= self.cooldown_seconds

    def record_action(self):
        self.last_action_time = time.time()

    def remaining_cooldown(self):
        if self.last_action_time is None:
            return 0
        elapsed = time.time() - self.last_action_time
        remaining = self.cooldown_seconds - elapsed
        return max(0, remaining)


if __name__ == "__main__":
    cooldown = CooldownManager(cooldown_seconds=5)
    print("Ilk kontrol - aksiyon alinabilir mi:", cooldown.can_act())  # True olmali

    cooldown.record_action()
    print("Aksiyon sonrasi hemen kontrol:", cooldown.can_act())  # False olmali
    print("Kalan sure:", cooldown.remaining_cooldown())

    time.sleep(6)
    print("6 saniye sonra kontrol:", cooldown.can_act())  # True olmali