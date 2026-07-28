import json
import urllib.request

url = 'http://127.0.0.1:5000/submit'
data = {
    'item_code': 'TESTCODE',
    'total_weight': 100.0,
    'pallet_weight': 10.0
}
req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req) as resp:
    print(resp.status)
    print(resp.read().decode())
