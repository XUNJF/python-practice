import requests
import os
import json

with open("key.txt","r",encoding="utf-8")as f:
    api_key = f.read().strip()

SYSTEM = """
你是一个Python助教，正在帮助一个从零学Python的人。

对方情况：
- 会基础语法（变量、循环、函数、列表、字典），但不熟练
- 目标是找AI应用开发的工作

回答要求：
1. 先给结论，再解释原因
2. 能用生活例子就用
3. 给代码必须加注释
4. 对方写错了直接指出，不用客气
5. 如果不确定，明说不知道，不要编
6. 如果对方只是打招呼或闲聊，简短回应即可，不要展开讲学习规划
"""


headers = {
    "Authorization":f"Bearer {api_key}",
    "Content-Type":"application/json",
}

if os.path.exists("history.json"):
    with open("history.json","r",encoding="utf-8")as f:
        messages = json.load(f)
else:
    messages=[{"role":"system","content":SYSTEM}]

    
while True:
    question = input("你：")
    if question == "退出":
        with open("history.json","w",encoding="utf-8")as f:
            json.dump(messages,f,ensure_ascii = False,indent = 2)       
        break
    messages.append({"role":"user","content":question})

    payload = {
        "model":"deepseek-chat",
        "messages":messages,
    }
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers = headers,
        json = payload,
        timeout = 30,
    )
    if response.status_code == 200:
        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        print(f"AI:{answer}")
        messages.append({"role":"assistant","content":answer})
    else:
        print(f"状态码：{response.status_code}")
        print(f"原始状态：{response.text}")
        

        

