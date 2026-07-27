import boto3

REGION = "eu-north-1"
CLUSTER_NAME = "furkan-autopilot-cluster"
SERVİCE_NAME = "furkan-autopilot-service"
MIN_TASKS = 1
MAX_TASKS = 4

ecs = boto3.client("ecs", region_name=REGION)

def get_service_status():
    response =  ecs.describe_services(
        cluster=CLUSTER_NAME,
        services=[SERVİCE_NAME], #bir clusterın altında birden fazla servis olabileceği için böyle çağırdık.
    )

    services = response.get("services", [])
    if not services:
        raise RuntimeError(f"Service bulunamadı: {SERVİCE_NAME}") 

    service = services[0]
    return {
        "desired_count": service["desiredCount"], #Bu servisten her an kaç tane task/container çalışmasını istiyorum?
        "running_count": service["runningCount"], #saniye itibarıyla AWS üzerinde hatasız bir şekilde çalışan task sayısı
        "pending_count": service["pendingCount"], # AWS'nin başlattığı ama henüz tam olarak hazır olmayan container sayısı
        "status": service["status"]
    }

def update_desired_count(new_count):
    # scale edildiğinde 1 ila 4 arası servis ayağa kaldırabilecek şekilde tasarlıyoruz.
    safe_count = max(MIN_TASKS,min(MAX_TASKS,new_count))

    if safe_count != new_count:
        print(f"UYARI: Istenen deger {new_count}, guvenlik siniri nedeniyle {safe_count} uygulandi")

    ecs.update_service(
        cluster = CLUSTER_NAME,
        service = SERVİCE_NAME,
        desiredCount= safe_count,
    )
    return safe_count

def scale(action):
    current = get_service_status()["desired_count"]

    if action == "SCALE_UP":
        new_count = current + 1
    elif action == "SCALE_DOWN":
        new_count = current - 1
    else:
        return current

    applied=update_desired_count(new_count)
    print(f"Olceklendirme: {current} -> {applied} (aksiyon: {action})")
    return applied


if __name__ == "__main__":
    status = get_service_status()
    print("ECS Service durumu:")
    for key, value in status.items():
        print(f" {key}: {value}")