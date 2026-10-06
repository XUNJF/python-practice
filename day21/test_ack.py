import json
import math
import requests
import re
import jieba

INDEX_FILE = "index.json"

COARSE_K = 20
FINAL_K = 5
K1 = 1.2
B = 0.75
RRF_K = 60

CODE_PATTERN = r"[a-zA-Z0-9_][a-zA-Z0-9_./\-]*"

with open("key_sf.txt",encoding="utf-8")as f:
    sk_key = f.read().strip()

with open("key.txt",encoding="utf-8")as f:
    ds_key = f.read().strip()

INDEX_FILE = "index.json"

def embed_batch(texts):
    """把一段文字转化成向量"""
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

def cosine(a,b):
    dot = 0
    for i in range(len(a)):
        dot += a[i]*b[i]
    len_a = 0
    for x in a:
        len_a += x * x  
    len_b = 0
    for x in b:
        len_b += x*x
    return dot/(math.sqrt(len_b)*(math.sqrt(len_a)))


def load_index():
    with open(INDEX_FILE,encoding="utf-8") as f:
        data = json.load(f)
    return data["chunks"], data["vectors"], data["bm25"]


def cut_words(text):
    codes = re.findall(CODE_PATTERN,text)
    rest = re.sub(CODE_PATTERN," ",text)
    words = jieba.lcut(rest)
    words = [w for w in words if re.search(r"\w", w)]
    words.extend(codes)
    return words

def coarse_search(question, chunks, vectors, top_k = COARSE_K):
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(chunks)):
        score = cosine(q_vec, vectors[i])
        scores.append((score,i))
    scores.sort(reverse=True)
    return scores[:top_k]

def bm25_score(query_words, doc_index, bm25, k1=K1, b=B):
    doc_words = bm25["doc_words"][doc_index] 
    df = bm25["df"]
    N = len(bm25["doc_words"])
    avg_len = bm25["avg_len"]
    doc_len = len(doc_words)
    score = 0
    for word in query_words:
        f = doc_words.count(word)
        if f ==0:
            continue
        n = df.get(word, 0)
        idf = math.log((N-n+0.5)/(n+0.5)+1)
        tf = (f*(k1+1))/(f+k1*(1-b+b*doc_len/avg_len))
        score += idf * tf
    return score

def bm25_search(question, chunks, bm25, top_k = COARSE_K):
    query_words = cut_words(question)
    scores = []
    for i in range(len(chunks)):
        score = bm25_score(query_words, i, bm25)
        scores.append((score, i))
    scores.sort(reverse=True)
    return scores[:top_k]

def rrf(result_lists, chunks, top_k = COARSE_K, k = RRF_K):
    total = {}
    for results in result_lists:
        for rank, (score,i) in enumerate(results, 1):
            total[i] = total.get(i,0)+1/(k+rank)
    pairs = []
    for i, s in total.items():
        pairs.append((s, i))
    pairs.sort(reverse=True)
    result = []
    for s, i in pairs[:top_k]:
        result.append((s, chunks[i]))
    return result


def rerank(question, candidates, top_n = FINAL_K):
    documents = [chunk["text"] for score, chunk in candidates] 
    response = requests.post(
        "https://api.siliconflow.cn/v1/rerank",
        headers={
            "Authorization":f"Bearer {sk_key}",
            "Content-Type":"application/json",
        },
        json={
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
    context = ""
    for score, chunk in hits:
        context += f"【来源:{chunk['source']}】\n{chunk['text']}\n\n"

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



chunks, vectors, bm25 = load_index()
print(f"已加载{len(chunks)}块笔记")
print()

question = "top_k是什么"


print("【第一轮】向量检索 top 5")
print("-"*62)
vec_hits = coarse_search(question, chunks,vectors)
for rank, (score,i) in enumerate(vec_hits[:5], 1):
    preview = chunks[i]["text"].replace("\n"," ")[:42]
    print(f"    {rank}.[{score:.4f}] {preview}")
print()

print("【第二轮】BM25检索 top 5")
print("-"*62)
bm_hits = bm25_search(question, chunks,bm25)
for rank, (score, i) in enumerate(bm_hits[:5], 1):
    preview = chunks[i]["text"].replace("\n", " ")[:42]
    print(f"    {rank}.[{score:.4f}] {preview}")
print()

print("【融合+精排】")
print("-"*62)
fused = rrf([vec_hits, bm_hits],chunks)
fine = rerank(question, fused, top_n=FINAL_K)
for rank, (score, chunk) in enumerate(fine,1):
    preview = chunk["text"].replace("\n"," ")[:42]
    print(f"   {rank}.[{score:.4f}] {preview}")
print()
print("-"*62)
print(ask(question,fine))