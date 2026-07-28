from datetime import datetime
from cost_fetcher import get_cost_last_n_days, summarize_costs
from idle_detector import find_unattached_volumes, find_unassociated_elastic_ips, find_stopped_instances

REPORT_FILE = "cost_reporter/weekly_cost_report.md"


def generate_report():
    lines = []
    lines.append(f"# Haftalik Maliyet Raporu")
    lines.append(f"Olusturulma: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Maliyet ozeti
    lines.append("## Son 7 Gun Maliyet\n")
    response = get_cost_last_n_days(7)
    costs = summarize_costs(response)
    total = 0
    for service, amount in costs:
        #if amount > 0.001:
            lines.append(f"- {service}: ${amount:.10f}")
            total += amount
    lines.append(f"\n**Toplam: ${total:.10f}**\n")

    # Idle kaynaklar
    lines.append("## Optimizasyon Onerileri (Idle Kaynaklar)\n")

    volumes = find_unattached_volumes()
    if volumes:
        lines.append(f"### Bagli olmayan {len(volumes)} EBS volume tespit edildi:")
        for v in volumes:
            lines.append(f"- `{v['volume_id']}` ({v['size_gb']}GB) — kullanilmiyorsa silinebilir")
    else:
        lines.append("- Bagli olmayan EBS volume yok.")

    ips = find_unassociated_elastic_ips()
    if ips:
        lines.append(f"\n### Bagli olmayan {len(ips)} Elastic IP tespit edildi:")
        for ip in ips:
            lines.append(f"- `{ip['public_ip']}` — serbest birakilabilir (ucret aliniyor)")
    else:
        lines.append("\n- Bagli olmayan Elastic IP yok.")

    stopped = find_stopped_instances()
    if stopped:
        lines.append(f"\n### Durdurulmus {len(stopped)} instance tespit edildi:")
        for s in stopped:
            lines.append(f"- `{s['instance_id']}` ({s['instance_type']}) — uzun sure kullanilmayacaksa silinebilir")

    report = "\n".join(lines)

    with open(REPORT_FILE, "w") as f:
        f.write(report)

    print(report)
    print(f"\n\nRapor kaydedildi: {REPORT_FILE}")


if __name__ == "__main__":
    generate_report()