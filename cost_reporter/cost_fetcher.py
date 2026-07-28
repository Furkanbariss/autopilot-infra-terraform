import boto3
from datetime import datetime, timedelta

REGION = "us-east-1"  # Cost Explorer API SADECE us-east-1'de calisir, dikkat!

ce = boto3.client("ce", region_name=REGION)


def get_cost_last_n_days(days=7):
    """Son N gunun gunluk maliyetini servis bazinda ceker."""
    end = datetime.now().date()
    start = end - timedelta(days=days)

    response = ce.get_cost_and_usage(
        TimePeriod={
            "Start": start.isoformat(),
            "End": end.isoformat(),
        },
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[
            {"Type": "DIMENSION", "Key": "SERVICE"},
        ],
    )
    return response


def summarize_costs(response):
    """API cevabini servis bazli toplam maliyete cevirir."""
    service_totals = {}

    for day in response["ResultsByTime"]:
        for group in day["Groups"]:
            service_name = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            service_totals[service_name] = service_totals.get(service_name, 0) + amount

    # Buyukten kucuge sirala
    sorted_services = sorted(service_totals.items(), key=lambda x: x[1], reverse=True)
    return sorted_services


if __name__ == "__main__":
    response = get_cost_last_n_days(7)
    costs = summarize_costs(response)
    print(response["ResultsByTime"])
    print("=== SON 7 GUN MALIYET RAPORU (servis bazli) ===\n")
    total = 0
    for service, amount in costs:
        # if amount > 0.001:  # cok kucuk degerleri gosterme
        print(f"  {service:40s} ${amount:.10f}")
        total += amount
    print(f"\n  {'TOPLAM':40s} ${total:.10f}")