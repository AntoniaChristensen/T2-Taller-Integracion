import requests

BASE = "http://127.0.0.1:5000/"
   

response = requests.get(BASE + "artists/TWljaGFlbCBKYWNrc29u/tracks")
print(response.json())
