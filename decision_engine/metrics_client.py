import boto3
from datetime import datetime, timezone, timedelta

REGION = "eu-north-1"
CLUSTER_NAME = "furkan-autopilot-cluster".strip()
SERVICE_NAME = "furkan-autopilot-service".strip()

cloudwatch = boto3.client('cloudwatch', region_name = REGION)


def get_current_cpu():
    end_time= datetime.now(timezone.utc) 
    start_time = end_time - timedelta(hours=1)

    print("Sorgulanan Zaman (UTC):", start_time, "ile", end_time, "arasi")
    print("Sorgulanan Bolge:", REGION)

    response = cloudwatch.get_metric_statistics(
        
        Namespace='AWS/ECS',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'ClusterName',
                'Value': CLUSTER_NAME
            },
            {
               'Name': 'ServiceName',
                'Value': SERVICE_NAME
            },               
        ],
        StartTime= start_time,
        EndTime= end_time,
        Period=300,
        Statistics=['Average'],
    )

    datapoints= response.get("Datapoints",[])
    #print("AWS'den Gelen Ham Cevap:", response)
    if not datapoints:
        return None

    latest = sorted(datapoints, key=lambda x: x["Timestamp"])[-1]
    return latest["Average"]

if __name__ == "__main__":
    cpu = get_current_cpu()
    print(f"şu anki cpu :{cpu}")
    
