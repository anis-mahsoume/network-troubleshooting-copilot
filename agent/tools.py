import random

def ping_host(host):
    # occasionally simulate a bad result for demo variety
    if random.random() < 0.3:
        return {
            "host": host,
            "avg_latency_ms": round(random.uniform(150, 400), 1),
            "packet_loss_pct": round(random.uniform(5, 25), 1),
            "jitter_ms": round(random.uniform(30, 90), 1)
        }
    return {
        "host": host,
        "avg_latency_ms": round(random.uniform(5, 40), 1),
        "packet_loss_pct": 0.0,
        "jitter_ms": round(random.uniform(1, 8), 1)
    }

def traceroute(host):
    hops = random.randint(6, 14)
    path = []
    for i in range(1, hops + 1):
        path.append({
            "hop": i,
            "ip": f"10.0.{i}.1",
            "latency_ms": round(random.uniform(1, 30) * i / 3, 1)
        })
    stopped_early = random.random() < 0.2
    return {
        "host": host,
        "hops": path if not stopped_early else path[:random.randint(2, hops - 2)],
        "reached_destination": not stopped_early
    }

def check_device_status(device_id):
    statuses = ["up", "up", "up", "unresponsive", "degraded"]  # weighted toward healthy
    status = random.choice(statuses)
    return {
        "device_id": device_id,
        "status": status,
        "cpu_pct": round(random.uniform(10, 95), 1),
        "memory_pct": round(random.uniform(20, 90), 1),
        "uptime_hours": round(random.uniform(1, 4000), 1)
    }

def lookup_dns(domain):
    rcodes = ["NOERROR", "NOERROR", "NOERROR", "SERVFAIL", "NXDOMAIN"]
    rcode = random.choice(rcodes)
    return {
        "domain": domain,
        "rcode": rcode,
        "resolved_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}" if rcode == "NOERROR" else None,
        "response_time_ms": round(random.uniform(2, 300), 1)
    }

def check_dhcp_lease(client_mac_or_hostname):
    statuses = ["active", "active", "no_lease", "conflict"]
    status = random.choice(statuses)
    return {
        "client": client_mac_or_hostname,
        "lease_status": status,
        "ip": f"10.0.4.{random.randint(2,254)}" if status == "active" else None,
        "pool_utilization_pct": round(random.uniform(40, 100), 1)
    }

TOOL_FUNCTIONS = {
    "ping_host": ping_host,
    "traceroute": traceroute,
    "check_device_status": check_device_status,
    "lookup_dns": lookup_dns,
    "check_dhcp_lease": check_dhcp_lease,
}