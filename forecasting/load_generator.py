import requests
import time
import threading
from datetime import datetime

ALB_URL = "http://furkan-autopilot-alb-tf-xxxxxxxxxx.eu-north-1.elb.amazonaws.com"  # Terraform output'undan aldigin ALB DNS adresi

success_count = 0
fail_count = 0

PHASES = [
    {"name": "dusuk_yuk", "duration_sec": 180, "iterations": 10000, "interval_sec": 2, "parallel": 1},
    {"name": "orta_yuk", "duration_sec": 180, "iterations": 100000, "interval_sec": 1, "parallel": 5},
    {"name": "yuksek_yuk_burst", "duration_sec": 300, "iterations": 500000, "interval_sec": 0.2, "parallel": 10},
    {"name": "cooldown", "duration_sec": 300, "iterations": 10000, "interval_sec": 3, "parallel": 1},
]

NUM_CYCLES = 1  # tum fazlari kac kere tekrarlayacagimiz


def send_compute_request(iterations):
    global success_count, fail_count
    try:
        response = requests.get(f"{ALB_URL}/compute", params={"iterations": iterations}, timeout=10)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if response.status_code == 200:
            success_count += 1
        else:
            fail_count += 1
        print(f"[{timestamp}] status={response.status_code} | basarili={success_count} hatali={fail_count}")
    except requests.exceptions.RequestException as e:
        fail_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] HATA: {e} | basarili={success_count} hatali={fail_count}")

def run_phase(phase):
    print(f"\n=== FAZ BASLADI: {phase['name']} (suresi: {phase['duration_sec']}sn) ===")
    end_time = time.time() + phase["duration_sec"]

    while time.time() < end_time:
        threads = []
        for _ in range(phase["parallel"]):
            t = threading.Thread(target=send_compute_request, args=(phase["iterations"],))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        time.sleep(phase["interval_sec"])

    print(f"=== FAZ BITTI: {phase['name']} ===")


def main():
    print(f"Load generator basliyor. {NUM_CYCLES} dongu x {len(PHASES)} faz calisacak.")
    for cycle in range(1, NUM_CYCLES + 1):
        print(f"\n########## DONGU {cycle}/{NUM_CYCLES} ##########")
        for phase in PHASES:
            run_phase(phase)

    print("\nLoad generator tamamlandi.")


if __name__ == "__main__":
    main()
    print(f"\n=== SONUC ===")
    print(f"Toplam basarili istek: {success_count}")
    print(f"Toplam hatali istek: {fail_count}")
    total = success_count + fail_count
    if total > 0:
        print(f"Basari orani: {(success_count/total)*100:.2f}%")