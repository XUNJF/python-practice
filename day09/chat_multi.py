import requests
messages = []
with open("key.txt","r",encoding="utf-8") as f:
    api_key = f.read().strip()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
while True:
    question = input("你：")
    if question =="退出":
        break
    messages.append({"role":"user","content":question})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
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
            print(f"AI：{answer}")
            messages.append({"role":"assistant","content":answer})
    else:
        print(f"状态码：{response.status_code}")
        print(f"错误详情：{response.text}")



