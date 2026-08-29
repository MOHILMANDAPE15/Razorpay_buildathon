import urllib.request

url = 'http://127.0.0.1:3300/'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8')
        print('HTTP Status:', resp.status)
        checks = [
            'How Aegis Evolved: Genesis to Production Proof',
            'Genesis Baseline',
            'The Concept Drift Shock',
            'Targeted Adaptation & Residual Mining',
            'Statistical Attribution Notice',
            'Held-Out Test Set Proof',
            'The Preventable Loss Pool vs. Realized Savings',
            'Why Aegis Outperforms Alternative Approaches',
            'Core Subsystem Modules'
        ]
        for c in checks:
            print(f'Check [{c}]: {"FOUND" if c in html else "NOT FOUND IN INITIAL HTML"}')
except Exception as e:
    print('Error:', e)
