import requests
import math

with open("key_sf.txt","r",encoding="utf-8")as f:
    sk_key = f.read().strip()


def cosine(a,b):
    dot = 0
    for i in range(len(a)):
        dot += a[i] * b[i]
    len_a = 0
    for x in a :
        len_a += x * x
    len_b = 0
    for x in b:
        len_b += x*x
    return dot / (math.sqrt(len_a)*math.sqrt(len_b))

def embed(text):
    response= requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers = {
            "Authorization":f"Bearer {sk_key}",
            "Content-type":"application/json",
        },
        json={"model":"BAAI/bge-m3","input":text},
        timeout=30
    )
    return response.json()["data"][0]["embedding"]


# v= embed("你好")
# print(type(v))
# print(len(v))
# print(v)

# result = requests.post(
#     "https://api.siliconflow.cn/v1/embeddings",
#     headers={
#         "Authorization": f"Bearer {sk_key}",
#         "Content-Type": "application/json",
#     },
#     json={
#         "model": "BAAI/bge-m3",
#         "input": ["第一段", "第二段", "第三段"],
#     },
#     timeout=30,
# )

# data = result.json()

# print("data 里有几条：", len(data["data"]))

# for item in data["data"]:
#     print(f"  index={item['index']}  向量长度={len(item['embedding'])}")



def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sk_key}",
            "Content-Type":"application/json",
        },
        json={"model":"BAAI/bge-m3","input":texts},
        timeout=30,
    )
    data = response.json()["data"]
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        i = item["index"]
        vectors[i] = item["embedding"]
    return vectors


texts = ["AAA","BBB","CCC"]
vectors = embed_batch(texts)
single = embed("BBB")
print(f"相似度：{cosine(single,vectors[1]):.8f}")