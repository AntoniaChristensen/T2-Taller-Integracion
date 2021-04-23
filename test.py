import requests

BASE = "http://127.0.0.1:5000/"
   
response = requests.post(BASE + "artists", {'name': "Michael Jackson", 'age': 21})
print(response.json())
input()
response = requests.post(BASE + "artists/TWljaGFlbCBKYWNrc29u/albums", {'name': "Off the Wall", 'genre':"Pop"})
print(response.json())
input()
response = requests.post(BASE + "albums/T2ZmIHRoZSBXYWxsOlRXbG/tracks", {'name': "Don't Stop 'Til You Get Enough", 'duration':4})
print(response.json())
response = requests.get(BASE + "tracks")
print(response.json())