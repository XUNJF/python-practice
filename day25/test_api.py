"""测试【带 tools】的请求 —— 直接从 file_agent.py 里把 TOOLS 拿过来用"""

import json
import requests

# 读 file_agent.py，但只执行到 def run 之前（避免跑主程序）
src = open("file_agent.py", encoding="utf-8").read()
head = src.split("def run(")[0]

ns = {}
exec(head, ns)

TOOLS = ns["TOOLS"]
ds_key = ns["ds_key"]

print(f"工具个数：{len(TOOLS)}")
print()

response = requests.post(
    "https://api.deepseek.com/chat/completions",
    headers={
        "Authorization": f"Bearer {ds_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}],
        "tools": TOOLS,
    },
    timeout=90,
)

print("HTTP 状态：", response.status_code)
print()
print("返回内容：")
print(response.text[:1500])