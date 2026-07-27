# adı üstünde sistem bir değşiklik yapacağı zaman her şeyin logunu tutuyoruzki daha sonra bu değişimi neden yapma kararı almış denetleyebilelim.
import csv
import os
from datetime import datetime, timezone

LOG_FILE = "autoscaler_log.csv"

FIELDNAMES = [
    "timestamp", # Olayın yaşandığı an
    "current_cpu",
    "avg_cpu",
    "trend",
    "action",
    "reason",
    "desired_count_before", #makine sayısının kaçtan kaça değiştiği
    "desired_count_after",
]

def _ensure_header():
    # Dosya yoksa basligi yazar.
    if not os.path.exists(LOG_FILE):
        with open (LOG_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

def log_decision(current_cpu,details, action, reason, count_before, count_after):
    # Her karar dongusunu denetlenebilir sekilde kaydeder. 
    _ensure_header()

    row = {
        "timestamp" : datetime.now(timezone.utc).isoformat(),
        "current_cpu" : round(current_cpu,2) if current_cpu is not None else None, # gelen rakamı 2 birim yuvarlar ve daha sonra 
        "avg_cpu" : details.get("avg_cpu"),
        "trend" : details.get("trend"),
        "action" : action,
        "reason" : reason,
        "desired_count_before" :count_before,
        "desired_count_after" : count_after,
    }

    with open(LOG_FILE, "a", newline="") as f:
        writer =csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)

    return row