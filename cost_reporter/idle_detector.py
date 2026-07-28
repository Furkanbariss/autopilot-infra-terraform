import boto3

REGION = "eu-central-1"

ec2 = boto3.client("ec2", region_name=REGION)


def find_unattached_volumes():
    """Hicbir instance'a bagli olmayan (bosta duran ama ucret alinan) EBS volume'leri bulur."""
    response = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]  # 'available' = hicbir yere bagli degil
    )

    idle_volumes = []
    for vol in response["Volumes"]:
        idle_volumes.append({
            "volume_id": vol["VolumeId"],
            "size_gb": vol["Size"],
            "created": vol["CreateTime"].isoformat(),
        })
    return idle_volumes


def find_unassociated_elastic_ips():
    """Hicbir kaynaga bagli olmayan Elastic IP'leri bulur (bagli degilse ucret alinir)."""
    response = ec2.describe_addresses()

    idle_ips = []
    for addr in response["Addresses"]:
        if "AssociationId" not in addr:  # hicbir seye bagli degil
            idle_ips.append({
                "public_ip": addr.get("PublicIp"),
                "allocation_id": addr.get("AllocationId"),
            })
    return idle_ips


def find_stopped_instances():
    """Durdurulmus ama silinmemis (EBS storage ucreti almaya devam eden) instance'lari bulur."""
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )

    stopped = []
    for reservation in response["Reservations"]:
        for inst in reservation["Instances"]:
            stopped.append({
                "instance_id": inst["InstanceId"],
                "instance_type": inst["InstanceType"],
            })
    return stopped


if __name__ == "__main__":
    print("=== IDLE KAYNAK TESPITI ===\n")

    volumes = find_unattached_volumes()
    print(f"Bagli olmayan EBS volume'ler ({len(volumes)} adet):")
    for v in volumes:
        print(f"  - {v['volume_id']} ({v['size_gb']}GB) - oneri: kullanilmiyorsa sil")

    ips = find_unassociated_elastic_ips()
    print(f"\nBagli olmayan Elastic IP'ler ({len(ips)} adet):")
    for ip in ips:
        print(f"  - {ip['public_ip']} - oneri: bagli degilse serbest birak (ucret aliniyor)")

    stopped = find_stopped_instances()
    print(f"\nDurdurulmus instance'lar ({len(stopped)} adet):")
    for s in stopped:
        print(f"  - {s['instance_id']} ({s['instance_type']}) - oneri: uzun sure kullanilmayacaksa sil")