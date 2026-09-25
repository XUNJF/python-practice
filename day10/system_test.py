import requests

with open("key.txt", "r", encoding="utf-8")as f:
    api_key = f.read().strip()


headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model":"deepseek-chat",
    "messages":[{"role": "system", "content": "回答必须控制在20个字以内"},
                {"role": "user",   "content": "什么是变量？"}]
            
}

response = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers=headers,
    json=payload,
    timeout=30,
)

if response.status_code == 200:
    data = response.json()
    print(data["choices"][0]["message"]["content"])
else:
    print(f"状态码：{response.status_code}")
    print(f"原始返回：{response.text}")