import requests

BASE = "http://127.0.0.1:5000/"
   

response = requests.post(BASE + "artists", json={"name": "123", "age": 35, "x": "w"})
print(response.json())
# input()
# response = requests.get(BASE + "artists")
# print(response.json())