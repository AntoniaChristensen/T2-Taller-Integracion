import requests

BASE = "http://127.0.0.1:5000/"
   

response = requests.put(BASE + "artists/TWljaGFlbCBKYWNrc29u/albums/play")
print(response.json())
response = requests.get(BASE + "tracks")
print(response.json())
