import urllib.request

url = 'http://127.0.0.1:3300/shadow-control'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8')
        print('HTTP Status:', resp.status)
        checks = [
            'Model A -- Frozen Baseline',
            'Model C -- Shadow Control',
            'Model B -- Drift-Adapted',
            'Paired Bootstrap Significance Analysis',
            'Not statistically distinguishable at production threshold T=0.70',
            'directional only -- not tested for statistical significance',
            'Evolved Rule Ensemble',
            'LightGBM Baseline',
            'Trade-off is interpretability and self-correction without retraining vs a raw-accuracy baseline'
        ]
        for check in checks:
            present = check in html
            print(f'Check: [{check}] -> {"FOUND" if present else "NOT FOUND IN INITIAL HTML"}')
except Exception as e:
    print('Error:', e)
