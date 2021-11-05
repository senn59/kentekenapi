import requests

url = "http://127.0.0.1:5000/scanner"
file = {"image": open("/home/senn/Programming/Projects/kenteken-API/images/real2.jpg", "rb")}
response = requests.post(url, files=file)
print(response.json())