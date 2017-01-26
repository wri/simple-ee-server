import requests

# or using cURL on windows
# curl -X POST -H "Content-Type: application/json" -d "{\"test\": \"data\"}" http://localhost:5000

geojson = {"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[-56.832275390625,-21.637005211106306],[-57.3651123046875,-22.715390019335942],[-56.4,-23.49347666096087],[-55.2504545454,-22.649502094242195],[-55.8599853515625,-21.058870866501525],[-56.832275390625,-21.637005211106306]]]}}]}

thresh = '30'
start = '2001'
end = '2010'

payload = {'geojson': geojson, 'thresh': thresh, 'start': start, 'end': end}

headers = {'Content-Type': 'application/json'}
url = r'http://localhost:5000/'

r = requests.post(url, headers=headers, json=payload)

print r.json()