from agent.chat_loop import run_conversation

SCENARIOS = [
    {
        "name": "VPN - intermittent drops",
        "message": "My VPN keeps dropping every few minutes during video calls"
    },
    {
        "name": "VPN - gateway health + connectivity",
        "message": "VPN gateway vpn-gw-01 seems unstable — can you check if it's healthy and also test connectivity to it?"
    },
    {
        "name": "DNS - specific domain failure",
        "message": "Can you check why internal-api.company.com isn't resolving for some users?"
    },
    {
        "name": "DHCP - client can't get lease",
        "message": "A laptop with MAC address 00:1A:2B:3C:4D:5E isn't getting an IP address, can you check its lease status?"
    },
    {
        "name": "Firewall - device health",
        "message": "Is firewall-02 currently healthy? We've had reports of intermittent connectivity through it."
    },
    {
        "name": "Routing - slow connection between subnets",
        "message": "Users on the 10.0.4.0/24 subnet report slow connections to 10.0.8.50 — can you check what's going on?"
    },
]

if __name__ == "__main__":
    for scenario in SCENARIOS:
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario['name']}")
        print(f"MESSAGE: {scenario['message']}")
        print('='*70)

        answer = run_conversation(scenario["message"])

        print(f"\nFINAL ANSWER:\n{answer}\n")