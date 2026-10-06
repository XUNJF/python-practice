"""
Function Calling 最小示例

★ 核心：模型自己不执行任何函数。
   它只说「我想调用 get_time，参数是 {}」，
   真正干活的是我们这边的 Python 代码。
"""

import json
import datetime
import requests

with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add(a, b):
    return a+b

def word_count(text):
    return len(text)

TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"get_time",
            "description":"查询当前的日期时间。用户问现在几点，今天几号时用。",
            "parameters":{
                "type":"object",
                "properties":{}
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"add",
            "description":"把两个数相加。用户需要做加法时用。",
            "parameters":{
                "type":"object",
                "properties":{
                    "a":{"type":"number","description":"第一个数"},
                    "b":{"type":"number","description":"第二个数"},
                },
                "required":["a", "b"],
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"word_count",
            "description":"数一段文字有多少个字符。用户问某段对话时用。",
            "parameters":{
                "type":"object",
                "properties":{
                    "text":{"type":"string","description":"要数的文字"},
                },
                "required":["text"],
            },
        },
    },
]

FUNCS = {
    "get_time":get_time,
    "add":add,
    "word_count":word_count,
}


def call_model(messages):
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json = {
            "model":"deepseek-chat",
            "messages":messages,
            "tools":TOOLS,
        },
        timeout=60,
    )
    return response.json()["choices"][0]


messages = [
    {"role":"system","content":"你是一个助手。需要外部信息时，调用提供的工具。"},
    {"role":"user","content":"现在几点？顺便算一下 123+456，再数数这句话多长"},
]
print(f"用户：{messages[-1]['content']}")

n = 0
while True:
    n += 1
    print(f"--第{n}轮--")
    choice = call_model(messages)
    msg = choice["message"]
    reason = choice["finish_reason"]
    print(f"  finish_reason = {reason}")
    if reason != "tool_calls":
        print()
        print(f"AI:{msg['content']}")
        break
    print(f" 模型说：{msg.get('content')}")
    messages.append(msg)
    for tc in msg["tool_calls"]:
        name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])
        print(f" → 要调用{name},参数{args}")
        result = FUNCS[name](**args)
        print(f"  → 我们执行，得到 {result!r}")
        messages.append({
            "role":"tool",
            "tool_call_id":tc["id"],
            "content":str(result),
        })
        print(messages)

    print()