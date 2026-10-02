"""
只做检索，不调大模型。

用来查看「检索到了什么」—— RAG 出问题时，先看这里。
"""

import json
import math
import requests
INDEX_FILE = "index.json"

with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()

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
        data =json.load(f)
    return data["chunks"],data["vectors"] 

def peek(question,chunks,vectors,top_k=5):
    """只检索，把结果打出来，不调大模型"""
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(chunks)):
        score = cosine(q_vec,vectors[i])
        scores.append((score,i))
    scores.sort(reverse=True)

    print(f"问题：{question}")
    print("-"*62)
    for score, i in scores[:top_k]:
        chunk = chunks[i]
        preview = chunk["text"].replace("\n"," ")[:60]
        print(f"  [{score:.4f}] {chunk['source']}")
        print(f"        {preview}")
        print()
    print()


chunks, vectors = load_index()
print(f"已加载{len(chunks)} 块笔记")
print()
peek("RAG 是什么？为什么要用它？", chunks, vectors)
peek("异常处理怎么写？", chunks, vectors)
peek("怎么做红烧肉？", chunks, vectors)