"""
Agent 雏形：让模型自己决定要不要查笔记

对比 hybrid_ask.py：
    hybrid_ask  →  每次都检索（无脑）
    agent_ask   →  模型自己判断：这个问题需要查笔记吗？
"""

import json
import math
import requests

INDEX_FILE = "index.json"
TOP_K = 5

with open("key_sf.txt",encoding="utf-8")as f:
    sk_key = f.read().strip()

with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sk_key}",
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
        text += f"【来源:{c['source']}】\n{c['text']}\n\n"
    return text

TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"search_notes",
            "description":(
                "在用户的学习笔记里检索"
                "当用户问到他笔记里学过的知识点使用"
                "（比如RAG、BM25、函数、异常处理、FastAPI等）"
                "如果只是打招呼，闲聊，不用调用。"
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
]


FUNCS = {"search_notes":search_notes}

def call_model(messages):
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json={"model":"deepseek-chat","messages":messages,"tools":TOOLS},
        timeout=60,
    )
    return response.json()["choices"][0]

def run(question):
    print("="*62)
    print(f"问：{question}")
    print("="*62)

    messages = [
        {
            "role":"system","content":"你是一个学习助手。需要查用户笔记时，调用 search_notes 工具。"
        },
        {
            "role":"user","content":question,
        },
    ]
    n = 0
    while True:
        n += 1
        choice = call_model(messages)
        msg = choice["message"]
        if choice["finish_reason"] !="tool_calls":
            print(f"   共{n}轮")
            print()
            print(msg["content"])
            print()
            return
        messages.append(msg)
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            print(f"  →调用{name}，参数{args.get('question')!r}")
            result = FUNCS[name](**args)
            messages.append({
                "role":"tool",
                "tool_call_id":tc["id"],
                "content":result,
            })


run("你好呀，你是谁")
run("RAG 是什么？")
run("帮我算一下 3 的平方")