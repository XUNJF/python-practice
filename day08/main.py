import requests
response = requests.get("https://v1.hitokoto.cn/")
data = response.json()
zhuangtai = response.status_code
print(zhuangtai)
print(data)