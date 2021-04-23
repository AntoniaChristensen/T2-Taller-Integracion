import requests

BASE = "http://127.0.0.1:5000/"
   
response = requests.post(BASE + "artists", {'name': "Michael Jackson", 'age': 21})
print(response.json())
input()
response = requests.get(BASE + "artists")
print(response.json())