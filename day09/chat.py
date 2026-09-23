import requests

with open("key.txt", "r", encoding="utf-8")as f:
    api_key = f.read().strip()

headers = {
    "Authorization" : f"Bearer {api_key}",
    "Content-Type" : "application/json", 
}

payload = {
    "model": "deepseek-chat",
    "messages":[
        {"role": "user",
         "content": "你好,请用一句话介绍你自己"
        }
    ]
}

response = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers = headers,
    json = payload,
    timeout = 30,
)



if response.status_code ==200:
    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    print(answer)
else:
    print(f"状态码：{response.status_code}")
    print(f"错误详情：{response.text}")
