import requests

BASE = "http://127.0.0.1:5000/"
   

response = requests.delete(BASE + "artists/TWljaGFlbCBKYWNrc29u")
print(response.json())
input()
response = requests.get(BASE + "tracks")
print(response.json())
