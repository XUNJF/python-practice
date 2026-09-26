import requests
r = requests.post(
    "http://127.0.0.1:8000/chat",
    params = {"question":"什么是列表"}
)
print(r.status_code)
print(r.json())