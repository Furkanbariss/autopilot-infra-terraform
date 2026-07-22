import boto3 
import csv 
import time
from datetime import datetime, timezone, timedelta

# boto3 aws servisleri ile konuşmamı sağlayacak olan kütüphene API'sidir. önve venv kur aktifleştir daha sonra ise "python -m pip install boto3 pandas" diyerek projene kurmayı unutma!

# değişebilecek değerler küçük harkle yazılır, sabit değerler ise BÜYÜK harfle yazılır.
# Şimdi burada hangi AWS kaynaklarının takip edileceğini ve kaç saniyede bir metrikleri toplayacağını tanımlıyorum.
CLUSTER_NAME = "xxxxxxxx-cluster"
SERVICE_NAME = "xxxxxxxx-service"
ALB_ARN_SUFFIX = "app/xxxxxxxxxxxx-alb-tf/xxxxxxxxxxxx"
REGION = "eu-north-1"
OUTPUT_FILE = "metrics_snapshot.csv"
COLLECTION_INTERVAL_SECONDS = 30 

# boto3'e bana AWS'ten cloudwatch hizmetini getir adıda benim_izleyicim adını verdim
benim_izleyicim = boto3.client("cloudwatch", region_name=REGION) 

def get_metric_average(namespace, metric_name, dimensions, period=60):
    # namespace: hangi servis? (Örn: AWS/ECS veya AWS/ApplicationELB).
    # metric_name: ölmek istediğin şeyne (Örn: CPUUtilization veya RequestCount).
    # dimensions: Bu, hedefin tam adresidir. "Hangi Cluster? Hangi Load Balancer?" sorularının cevabı olan filtreleri içerir.
    # period=60 : 1 dakikalık ortalamayı verir.
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=2)

    response = benim_izleyicim.get_metric_statistics(
        Namespace = namespace,
        MetricName = metric_name,
        Dimensions = dimensions,
        StartTime = start_time,
        EndTime = end_time,
        Period = period,
        Statistics = ["Average"], #Bana ani fırlamaları değil, o dakikanın genel ortalamasını (Average) getir
    )

    
    datapoints = response.get("Datapoints", []) #Eğer AWS bize boş bir cevap dönerse kodun çökmesini engeller, onun yerine boş bir liste [] verir.
    if not datapoints:
        return None
    
    latest = sorted(datapoints, key=lambda x: x["Timestamp"])[-1]
    return latest["Average"]

def collect_snapshot():
    timestamp = datetime.now(timezone.utc).isoformat()

    cpu = get_metric_average(
        "AWS/ECS", "CPUUtilization",
        [{"Name": "ClusterName", "Value": CLUSTER_NAME},
         {"Name": "ServiceName", "Value": SERVICE_NAME}]
    )
    memory = get_metric_average(
        "AWS/ECS", "MemoryUtilization",
        [{"Name": "ClusterName", "Value": CLUSTER_NAME},
         {"Name": "ServiceName", "Value": SERVICE_NAME}]
    )
    request_count = get_metric_average(
        "AWS/ApplicationELB", "RequestCount",
        [{"Name": "LoadBalancer", "Value": ALB_ARN_SUFFIX}]
    )
    latency = get_metric_average(
        "AWS/ApplicationELB", "TargetResponseTime",
        [{"Name": "LoadBalancer", "Value": ALB_ARN_SUFFIX}]
    )

    row = {
        "timestamp": timestamp,
        "service": SERVICE_NAME,
        "cpu": cpu,
        "memory": memory,
        "requests": request_count,
        "latency": latency,
    }
    return row
def main():
    print(f"Metrik toplama basladi. Her {COLLECTION_INTERVAL_SECONDS} saniyede bir kayit yapilacak.")
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "service", "cpu", "memory", "requests", "latency"])
        writer.writeheader()

        while True:
            row = collect_snapshot()
            writer.writerow(row)
            f.flush()  # her yazimda diske bas, program yarida kesilirse veri kaybolmasin
            print(row)
            time.sleep(COLLECTION_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()