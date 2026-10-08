"""
多工具：让模型在几个工具之间自己选

跟 day23 的区别只有一处 —— TOOLS 里从一个变成了三个。
代码结构一模一样。
"""


import json
import requests
import math
import datetime

INDEX_FILE = "index.json"
TOP_K =5

with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()
with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=60,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors


def cosine(a, b):
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a:
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x * x
    return dot/(math.sqrt(len_b)*math.sqrt(len_a))

def load_index():
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
    return data["chunks"], data["vectors"]


CHUNKS, VECTORS = load_index()



def search_notes(question):
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(CHUNKS)):
        scores.append((cosine(q_vec, VECTORS[i]), i))
    scores.sort(reverse=True)
    text = ""
    for score, i in scores[:TOP_K]:
        c = CHUNKS[i]
        text += f"【来源：{c['source']}】\n{c['text']}\n\n" 
    return text


def calculate(a,b,operation):
    if operation == "+":
        return a+b
    if operation == "-":
        return a-b
    if operation == "*":
        return a*b
    if operation == "/":
        return a/b
    return "不支持的运算"


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:S")


TOOLS =[
    {
        "type":"function",
        "function":{
            "name":"search_notes",
            "description":(
                "在用户的学习笔记里检索。"
                "当用户问到他笔记里学过的知识点时使用"
                "（比如 RAG、BM25、函数、异常处理、FastAPI 等）。"
                "闲聊时不要调用。"
            ),
            "parameters":{
                "type":"object",
                "properties":{
                    "question":{
                        "type":"string",
                        "description":"要在笔记里检索的问题",
                    },
                },
                "required":["question"],
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"calculate",
            "description":"做四则运算。当用户需要算数时使用（加减乘除）。",
            "parameters":{
                "type":"object",
                "properties":{
                    "a":{"type":"number","description":"第一个数"},
                    "b":{"type":"number","description":"第二个数"},  
                    "operation":{
                        "type":"string",
                        "description":"运算符，只能是 + - * / 之一",
                    },
                },
                "required":["a","b","operation"],
            },
        },
    },
    {
        "type":"function",
        "function":{
            "name":"get_time",
            "description":"查询当前的日期和时间。当用户问现在几点、今天几号时使用。",
            "parameter":{
                "type":"object",
                "properties":{},
            },
        },
    },
]

FUNCS = {
    "search_notes":search_notes,
    "get_time":get_time,
    "calculate":calculate,
}


def call_model(messages):
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json={"model":"deepseek-chat","messages":messages, "tools":TOOLS},
        timeout=60,
    )
    return response.json()["choices"][0]



def run(question):
    print("="*62)
    print(f"问：{question}")
    print("="*62)
    messages = [
        {"role":"system","content":"你是一个助手。需要外部信息时调用工具。"},
        {"role":"user","content":question},
    ]
    used = []
    while True:
        choice = call_model(messages)
        msg = choice["message"]
        if choice["finish_reason"] != "tool_calls":
            if used:
                print(f"  ✓ 用了：{used}")
            else:
                print("  （没用工具）")
            print()
            print(msg["content"])
            print()
            return
        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            used.append(name)
            print(f"  → {name}({args})")
            result = FUNCS[name](**args)
            messages.append({
                "role":"tool",
                "tool_call_id":tc["id"],
                "content":str(result)
            })


run("你好呀")
run("RAG 是什么")
run("帮我算 1738 × 2947")
run("现在几点")
run("现在几点？顺便说说 BM25 是什么")