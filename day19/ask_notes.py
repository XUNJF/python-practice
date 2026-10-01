"""
读取建好的索引，回答关于笔记的问题

可以反复跑，很快——不用重新转向量。
"""

import json
import math
import requests

INDEX_FILE = "index.json"
TOP_K = 5

with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()
with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()


def embed_batch(texts):
    """把一批文字转成向量"""
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

def cosine(a,b):
    """算两个向量的相似度，越大越像"""
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a:
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x * x
    return dot/(math.sqrt(len_a)*math.sqrt(len_b))


def load_index():
    """读索引文件，返回（块列表，向量列表）"""
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
    return data["chunks"], data["vectors"]


def search(question,chunks,vectors,top_k=TOP_K):
    """找出跟问题最相关的 top_k 块"""
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(chunks)):
        score = cosine(q_vec,vectors[i])
        scores.append((score,i))
    scores.sort(reverse=True)
    result = []
    for score, i in scores[:top_k]:
        result.append((score,chunks[i]))
    return result

def ask(question,chunks,vectors):
    """检索 + 让 AI 基于检索结果回答"""
    hits = search(question,chunks,vectors,top_k=TOP_K)
    context = ""
    for score,chunk in hits:
        context += f"【来源：{chunk['source']}】\n{chunk['text']}\n\n"

    messages = [
        {
            "role":"system",
            "content":(
                "你是一个学习助手，帮助用户回忆他学过的内容。\n"
                "只根据下面提供的【资料】回答问题。\n"
                "如果资料里没有相关信息，就直说「资料里没有提到」。\n"
                "回答时请注明是根据哪份笔记。"
            ),
        },
        {
            "role":"user",
            "content":f"【资料】\n{context}\n【问题】\n{question}",
        },
    ]
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json={"model":"deepseek-chat","messages":messages},
        timeout=60,
    )
    return response.json()["choices"][0]["message"]["content"]

chunks, vectors = load_index()
print(f"已加载 {len(chunks)} 块笔记")
print()
questions = [
    "RAG 是什么？为什么要用它？",
    "异常处理怎么写？",
    "FastAPI 怎么启动？",
    "我笔记里讲过 embedding 吗？",
    "怎么做红烧肉？",        
]
for q in questions:
    print("="*62)
    print(f"问：{q}")
    print("="*62)
    print(ask(q,chunks,vectors))
    print()