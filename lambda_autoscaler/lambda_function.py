import boto3
from datetime import datetime, timedelta, timezone

REGION = "eu-north-1"
CLUSTER_NAME = "furkan-autopilot-cluster"
SERVICE_NAME = "furkan-autopilot-service"
SCALE_UP_THRESHOLD = 70
SCALE_DOWN_THRESHOLD = 20
MIN_TASKS = 1
MAX_TASKS = 4

cloudwatch = boto3.client("cloudwatch", region_name=REGION )
ecs =boto3.client("ecs", region_name=REGION )

def get_recent_cpu_values(minutes=5):

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes = minutes)

    response = cloudwatch.get_metric_statistics(
        Namespace= "AWS/ECS",
        MetricName= "CPUUtilization",
        Dimensions=[
        { "Name": "ClusterName", "Value": CLUSTER_NAME },
        { "Name": "ServiceName", "Value": SERVICE_NAME },
         ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=["Average"],
    )

    datapoints = sorted(response.get("Datapoints", []), key=lambda x: x["Timestamp"])
    return [dp["Average"] for dp in datapoints]

def get_current_desired_count():
    response = ecs.describe_services(cluster=CLUSTER_NAME, services=[SERVICE_NAME])
    return response["services"][0]["desiredCount"]

def update_desired_count(new_count):
    safe_count = max(MIN_TASKS,min(MAX_TASKS,new_count))
    ecs.update_service(
        cluster=CLUSTER_NAME,
        service=SERVICE_NAME,
        desiredCount = safe_count,
    )
    return safe_count

def decide_action(cpu_values):
    if len(cpu_values) < 3:
        return "NO_CHANGE" , "Yeterli veri yok. CPU değerlerinin sayısı 3'ten az."

    avg_cpu = sum(cpu_values)/len(cpu_values)

    if avg_cpu > SCALE_UP_THRESHOLD:
        return "SCALE_UP" , f"Ortalama CPU {avg_cpu:.1f} > {SCALE_UP_THRESHOLD}"
    elif avg_cpu < SCALE_DOWN_THRESHOLD:
        return "SCALE_DOWN" , f"Ortalama CPU {avg_cpu:.1f} < {SCALE_DOWN_THRESHOLD}"
    else:
        return "NO_CHANGE" , f"Ortalama CPU {avg_cpu:.1f} normal aralikta"

def lambda_handler(event, context):
    cpu_values = get_recent_cpu_values(minutes=5)

    if not cpu_values:
        print("CloudWatch'tan gelen veri yok, bu döngü atlanıyor.")
        return {"action":"NO_CHANGE", "reason":"yeterli veri yok minimum 3 olmasını bekleyin."}

    action, reason = decide_action(cpu_values)
    current_count = get_current_desired_count()

    new_count =  current_count
    if action == "SCALE_UP":
        new_count = update_desired_count(current_count + 1) 
    elif action == "SCALE_DOWN":
        new_count = update_desired_count(current_count - 1)

    log_message = {
        "timestamp"     : datetime.now(timezone.utc).isoformat(),
        "avg_cpu"       : round(sum(cpu_values)/len(cpu_values),2),
        "action"        : action,
        "reason"        : reason,
        "count_before"  : current_count,
        "count_after"   : new_count,
    }
    print(log_message)

    return log_message