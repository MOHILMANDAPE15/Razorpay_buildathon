import urllib.request
import json

def get_status():
    with urllib.request.urlopen('http://127.0.0.1:8080/api/v1/monitor/status') as res:
        d = json.loads(res.read().decode())
        print(f"Status: {d['status']} | Flag Rate: {d['current_flag_rate']*100:.1f}% | Z: {d['z_score']}s | CUSUM: {d['cusum_positive']} | Active Alerts: {len(d['active_alerts'])}")

print("1. Initial Baseline State:")
get_status()

print("\n2. Injecting 30 high fraud spike orders (55% flag rate):")
req = urllib.request.Request('http://127.0.0.1:8080/api/v1/monitor/simulate-traffic', data=json.dumps({'count': 30, 'spike_rate': 0.55}).encode(), headers={'Content-Type': 'application/json'})
urllib.request.urlopen(req)
get_status()

print("\n3. Injecting 50 normal baseline orders (8% flag rate) -> should recover to HEALTHY:")
req = urllib.request.Request('http://127.0.0.1:8080/api/v1/monitor/simulate-traffic', data=json.dumps({'count': 50, 'spike_rate': 0.08}).encode(), headers={'Content-Type': 'application/json'})
urllib.request.urlopen(req)
get_status()
