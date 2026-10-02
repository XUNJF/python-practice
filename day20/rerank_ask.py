"""
在 ask_notes.py 基础上加了「重排」（rerank）

原来的流程：
    241 块 → 向量检索 top 5 → 给大模型

现在的流程：
    241 块 → 向量检索 top 20 → 重排选 top 5 → 给大模型
                              ↑ 新增的这一步
"""

import json
import math
import requests

INDEX_FILE = "../day19/index.json"
COARSE_K = 20
FINAL_K = 5

with open("../day19/key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()

with open("../day19/key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

def embed_batch(texts):
    response =requests.post(
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
    """算两个向量的相似度"""
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a:
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x * x
    return dot/(math.sqrt(len_a) * math.sqrt(len_b))


def load_index():
    """读索引"""
    with open(INDEX_FILE,encoding="utf-8")as f:
        data = json.load(f)
    return data["chunks"],data["vectors"]

def coarse_search(question, chunks, vectors, top_k=COARSE_K):
    """向量检索：从 241 块里粗粗挑出 top_k 块"""
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(chunks)):
        score = cosine(q_vec, vectors[i])
        scores.append((score, i))
    scores.sort(reverse=True)
    result = []
    for score, i in scores[:top_k]:
        result.append((score,chunks[i]))
    return result

def rerank(question,candidates,top_n=FINAL_K):
    """把粗筛出来的候选块做精排，返回最相关的 top_n 块

    candidates 是 coarse_search 的结果：[(分数, 块), ...]
    """
    documents = [chunk["text"] for score,chunk in candidates]
    response = requests.post(
        "https://api.siliconflow.cn/v1/rerank",
        headers = {
            "Authorization": f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json = {
            "model":"BAAI/bge-reranker-v2-m3",
            "query":question,
            "documents":documents,
            "top_n":top_n,
        },
        timeout=60,
    )
    result = []
    for item in response.json()["results"]:
        chunk = candidates[item["index"]][1]
        result.append((item["relevance_score"],chunk))
    return result



def ask(question, hits):
    """拿【已经检索好的块】拼 prompt，问大模型

    hits 是 [(分数, 块), ...]
    """
    context = ""
    for score, chunk in hits:
        context +=f"【来源：{chunk['source']}】\n{chunk['text']}\n\n"

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
            "content":f"【资料】\n{context}\n【问题】\n{question}"
        },
    ]
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers= {
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json={"model":"deepseek-chat","messages":messages},
        timeout=60,
    )
    return response.json()["choices"][0]["message"]["content"]



chunks, vectors = load_index()
print(f"已加载{len(chunks)}块笔记")
print()

question = "RAG 是什么？为什么要用它？"

print(f"【第一步】粗筛：向量检索 top{COARSE_K}")
print("-"*62)
coarse = coarse_search(question, chunks, vectors, top_k=COARSE_K)
for rank, (score,chunk) in enumerate(coarse,1):
    preview = chunk["text"].replace("\n"," ")[:42]
    print(f" {rank:2}.[{score:.4f}] {preview}")

print()

print(f"【第二步】精排：rerank 选 top {FINAL_K}")
print("-"*62)

fine = rerank(question,coarse,top_n=FINAL_K)
for rank, (score,chunk) in enumerate(fine, 1):
    preview = chunk["text"].replace("\n"," ")[:42]
    print(f" {rank:2}.[{score:.4f}] {preview}")

print()

print(f"【第三步】拿精排的 {FINAL_K} 块去问大模型")
print("="*62)
print(ask(question,fine))
