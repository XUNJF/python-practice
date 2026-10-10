"""
给检索量个分 —— 15 道题，看答案能不能被捞出来
"""

import json
import math
import requests

INDEX_FILE = "index.json"
TOP_K = 5
with open("key_sf.txt",encoding="utf-8")as f:
    sf_key = f.read().strip()


TEST_CASES =[
    ("变量是什么",               "## 一、变量：给数据起名字"),
    ("input 怎么用",             "## 二、input：接收用户输入"),
    ("if 怎么写",                "## 三、if：做判断"),
    ("for 循环怎么写",           "## 四、循环：重复干活"),
    ("f-string 怎么用",          "## 六、f-string：更好用的输出方式（进阶但立刻有用）"),
    ("列表索引从几开始",          "## 二、索引：从 0 开始"),
    ("列表切片怎么写",            "## 六、列表切片（进阶，但很有用）"),
    ("字典怎么取值",              "## 二、取值：`[]` vs `get()`"),
    ("列表套字典是什么",          "## 五、列表套字典（重点！）"),
    ("return 和 print 的区别",    "## 四、⭐ 最重要的一节：`return` 和 `print` 的区别"),
    ("函数最多写多长",            "## 八、函数该多长？"),
    ("文件有哪几种打开模式",       "## 二、⚠️ 三种模式（最重要的一节）"),
    ("读文件为什么要写 encoding",  "## 四、⚠️ 中文必踩坑：`encoding=\"utf-8\"`"),
    ("怎么判断文件是否存在",       "## 八、判断文件是否存在"),
    ("虚拟环境是干什么的",         "## 一、为什么需要"),
]


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
    return dot / (math.sqrt(len_b) * math.sqrt(len_a))


with open(INDEX_FILE, encoding="utf-8")as f:
    _data = json.load(f)

CHUNKS = _data["chunks"]
VECTORS = _data["vectors"]    

def search(question, top_k = TOP_K):
    q_vec = embed_batch([question])[0]
    scores = []
    for i in range(len(CHUNKS)):
        scores.append((cosine(q_vec, VECTORS[i]), i))
    scores.sort(reverse=True)
    return [i for score, i in scores[:top_k]]


print(f"测试集：{len(TEST_CASES)}题，看top-{TOP_K}里有没有正确答案所在的那一节")
print()
print(f"  {'问题':<26} {'top1':>5}{'top3':>5}{'top5':>5}")
print(f"  {'-'*62}{'-'*5}{'-'*5}{'-'*5}")


hit1 = hit3 = hit5 = 0

for question, expect_title in TEST_CASES:
    got = search(question)

    rank = -1
    for n, idx in enumerate(got, 1):
        if CHUNKS[idx]["text"].startswith(expect_title):
            rank = n
            break
    if rank == 1:
        hit1 += 1
    if 0 < rank <= 3:
        hit3 += 1
    if 0 < rank <= 5:
        hit5 += 1

    m1 = "✓" if rank == 1 else " "
    m3 = "✓" if 0 < rank <= 3 else " "
    m5 = "✓" if 0 < rank <= 5 else "x"

    if rank > 0:
        print(f"  {question:<26} {m1:>5} {m3:>5} {m5:>5}   第{rank}名")
    else:
        print(f"  {question:<26} {'':>5} {'':>5} {m5:>5}   没找到")

n = len(TEST_CASES)
print()
print(f"  {'命中率':<26} {hit1/n:>4.0%} {hit3/n:>5.0%} {hit5/n:>5.0%}")