TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "ping_host",
            "description": "Check latency, packet loss, and jitter to a host or IP address.",
            "parameters": {
                "type": "object",
                "properties": {"host": {"type": "string", "description": "Hostname or IP address to ping"}},
                "required": ["host"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "traceroute",
            "description": "Trace the network path to a host, showing each hop and its latency.",
            "parameters": {
                "type": "object",
                "properties": {"host": {"type": "string", "description": "Hostname or IP address to trace"}},
                "required": ["host"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_device_status",
            "description": "Check the health status (up/down/degraded), CPU, memory, and uptime of a network device such as a firewall or VPN gateway.",
            "parameters": {
                "type": "object",
                "properties": {"device_id": {"type": "string", "description": "Device identifier, e.g. 'firewall-01' or 'vpn-gateway-02'"}},
                "required": ["device_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_dns",
            "description": "Perform a DNS lookup for a domain and return the response code (NOERROR, SERVFAIL, NXDOMAIN) and resolved IP if successful.",
            "parameters": {
                "type": "object",
                "properties": {"domain": {"type": "string", "description": "Domain name to look up"}},
                "required": ["domain"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_dhcp_lease",
            "description": "Check the DHCP lease status for a client, identified by MAC address or hostname, including current pool utilization.",
            "parameters": {
                "type": "object",
                "properties": {"client_mac_or_hostname": {"type": "string", "description": "Client MAC address or hostname"}},
                "required": ["client_mac_or_hostname"]
            }
        }
    },
]