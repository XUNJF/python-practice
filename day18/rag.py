import requests
import math

# ============================================================
# 读两个 key
#   key_sf.txt → 硅基流动（做 embedding）
#   key.txt    → DeepSeek（做对话）
# ============================================================
with open("key_sf.txt", encoding="utf-8") as f:
    sf_key = f.read().strip()

with open("key.txt", encoding="utf-8") as f:
    ds_key = f.read().strip()


# ============================================================
# 下面是第 17 天写的：检索
# ============================================================

def embed_batch(texts):
    """把一批文字转成向量"""
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization": f"Bearer {sf_key}",
            "Content-Type": "application/json",
        },
        json={"model": "BAAI/bge-m3", "input": texts},
        timeout=30,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors


def cosine(a, b):
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

    return dot / (math.sqrt(len_a) * math.sqrt(len_b))


# 这是我们的「知识库」
docs = [
    "退款政策：购买后30天内可申请全额退款。",
    "配送说明：全国包邮，偏远地区需加收运费。",
    "会员权益：会员可享受9折优惠和优先客服。",
    "服务器日志保留七天，超过期限自动清理。",
    "发票申请：订单完成后可在订单页申请电子发票。",
]

# 提前把所有文档转成向量（只做一次，后面反复用）
doc_vectors = embed_batch(docs)


def search(query, top_k=2):
    """检索：找出跟 query 最相关的 top_k 段文档"""
    # 把问题也转成向量（注意取 [0]，因为只传了一句）
    q_vec = embed_batch([query])[0]

    # 跟每篇文档算相似度，存成 (分数, 下标)
    scores = []
    for i in range(len(docs)):
        score = cosine(q_vec, doc_vectors[i])
        scores.append((score, i))

    # 从高到低排序
    scores.sort(reverse=True)

    # 取前 top_k 条，拼成 (分数, 文档内容)
    result = []
    for score, i in scores[:top_k]:
        result.append((score, docs[i]))

    return result


# ============================================================
# 下面是今天新写的：生成
# ============================================================

def ask(question):
    """先检索，把资料塞进 prompt，再让 AI 基于资料回答"""

    # ---------- 第 1 步：检索 ----------
    hits = search(question, top_k=3)

    # ---------- 第 2 步：把检索结果拼成一段文字 ----------
    # context 会长这样：
    #   1. 退款政策：购买后30天内可申请全额退款。
    #   2. 配送说明：全国包邮，偏远地区需加收运费。
    #   3. 会员权益：会员可享受9折优惠和优先客服。
    context = ""
    for i, (score, doc) in enumerate(hits):
        # i 从 0 开始，所以要 +1，这样编号是 1、2、3
        # \n 是换行，让每条资料占一行
        context += f"{i + 1}. {doc}\n"

    # ---------- 第 3 步：拼消息 ----------
    messages = [
        {
            "role": "system",
            # 这句话是 RAG 的关键：只许照资料答，资料里没有就说没有
            "content": (
                "你是一个客服助手。\n"
                "只根据下面提供的【资料】回答用户的问题。\n"
                "如果资料里没有相关信息，就直说「资料里没有提到这个问题」，"
                "不要凭自己的知识回答。"
            ),
        },
        {
            "role": "user",
            # 【资料】和【问题】分开标清楚，模型才分得清哪是哪
            "content": f"【资料】\n{context}\n【问题】\n{question}",
        },
    ]

    # ---------- 第 4 步：发给 DeepSeek ----------
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {ds_key}",
                "Content-Type": "application/json",
            },
            json={"model": "deepseek-chat", "messages": messages},
            timeout=30,
        )
    except requests.RequestException as e:
        return f"网络出问题了：{e}"

    if response.status_code != 200:
        return f"请求失败，状态码：{response.status_code}"

    # ---------- 第 5 步：取回答 ----------
    data = response.json()
    return data["choices"][0]["message"]["content"]


# ============================================================
# 测试
# ============================================================

print("=" * 50)
print("问题 1：资料里【有】答案的")
print("=" * 50)
print(ask("你们退款几天内可以"))

print()
print("=" * 50)
print("问题 2：资料里【没有】这个信息")
print("=" * 50)
print(ask("你们支持货到付款吗"))
