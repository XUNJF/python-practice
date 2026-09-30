import requests
import math

with open("key_sf.txt","r",encoding="utf-8")as f:
    sf_key = f.read().strip()


with open("key.txt","r",encoding="utf-8")as f:
    ds_key = f.read().strip()

def embed_batch(texts):
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization":f"Bearer {sf_key}",
            "Content-Type":"application/json",
        },
        json = {"model":"BAAI/bge-m3","input":texts},
        timeout = 30,
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
    return dot/(math.sqrt(len_a)*math.sqrt(len_b))


docs = [
    "退款政策：购买后30天内可申请全额退款。",
    "配送说明：全国包邮，偏远地区需加收运费。",
    "会员权益：会员可享受9折优惠和优先客服。",
    "服务器日志保留七天，超过期限自动清理。",
    "发票申请：订单完成后可在订单页申请电子发票。",
]

doc_vectors = embed_batch(docs)

def search(query, top_k=2):
    q_vec = embed_batch([query])[0]
    scores = []
    for i in range(len(docs)):
        score = cosine(q_vec,doc_vectors[i])
        scores.append((score,i))
    scores.sort(reverse=True)
    result = []
    for score,i in scores[:top_k]:
        result.append((score,docs[i]))
    return result


def ask(question):
    hits = search(question, top_k=3)
    context = ""
    for i,(score,doc) in enumerate(hits):
        context += f"{i+1}.{doc}\n"
    messages = [
        {"role":"system","content":"你是一个客服助手。\n只根据【资料】回答如果资料里没有相关信息，就直说「资料里没有提到这个问题」，不要凭自己的知识回答。"},
        {"role":"user","content":f"【资料】\n{context}\n【问题】\n{question}"}
    ]
    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization":f"Bearer {ds_key}",
            "Content-Type":"application/json",
        },
        json = {"model":"deepseek-chat","messages":messages},
        timeout=30,
    )
    return response.json()["choices"][0]["message"]["content"]


print(ask("你们退款几天内可以"))
print(ask("你们支持货到付款吗"))