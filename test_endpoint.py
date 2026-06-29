import urllib.request, json
data=json.dumps({'preferences':{'categories':['Travel', 'Dining'],'monthlySpend':3000,'region':'North America','balance':5000}}).encode()
req=urllib.request.Request('http://localhost:8000/api/recommend', data=data, headers={'Content-Type': 'application/json'})
r=urllib.request.urlopen(req)
d = json.loads(r.read().decode())
print(f"Returned {len(d.get('cards', []))} cards.")
