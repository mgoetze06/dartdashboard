import requests
import json

url = "http://192.168.0.214/update"
data = {'punkte0': '501', 'punkte1': '501', 'spieler': '0'}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
r = requests.post(url, data=json.dumps(data), headers=headers)
print(r)