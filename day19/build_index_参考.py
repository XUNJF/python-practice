"""
第一步：把学习笔记切分成小块，转成向量，存成 index.json

这个脚本只需要跑一次（或者笔记更新后再跑）。
建好的索引会被 ask_notes.py 直接读取，不用每次重新算。
"""

import os
import json
import requests
import math

# ============================================================
# 配置
# ============================================================

# 笔记文件夹的位置
# 这个脚本在 day19 里，笔记在 code/学习笔记，所以要往上走两层
NOTES_DIR = "../../学习笔记"

# 索引存到哪
INDEX_FILE = "index.json"

# 太短的块丢掉（比如只有个标题没有内容的）
MIN_LEN = 50

# 一次往接口送多少段（别太多，会被拒绝）
BATCH_SIZE = 20


# 读硅基流动的 key（做 embedding）
with open("key_sf.txt", encoding="utf-8") as f:
    sf_key = f.read().strip()


# ============================================================
# 基础函数
# ============================================================

def embed_batch(texts):
    """把一批文字转成向量，返回一批向量"""
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={
            "Authorization": f"Bearer {sf_key}",
            "Content-Type": "application/json",
        },
        json={"model": "BAAI/bge-m3", "input": texts},
        timeout=60,
    )
    vectors = [None] * len(texts)
    for item in response.json()["data"]:
        vectors[item["index"]] = item["embedding"]
    return vectors


def cut_into_chunks():
    """把笔记文件夹里所有 .md 文件，按 ## 标题切成小块"""

    chunks = []          # 每块是 {"text": 内容, "source": 来自哪个文件}

    # sorted 是为了每次跑的顺序都一样
    for filename in sorted(os.listdir(NOTES_DIR)):

        # 只要 .md 文件
        if not filename.endswith(".md"):
            continue

        path = os.path.join(NOTES_DIR, filename)
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # 按 "\n## " 切开
        #   "\n" 是为了只匹配行首的 ##，不会切到 ### 或正文里的 #
        parts = content.split("\n## ")

        for i, part in enumerate(parts):
            # 第 0 块是文件开头的标题和导言（## 之前的部分）
            # 其余的块，要把它自己的 "## " 补回去
            if i == 0:
                text = part
            else:
                text = "## " + part

            # 去掉首尾空白，以及结尾那根分隔线
            text = text.strip()
            if text.endswith("---"):
                text = text[:-3].strip()

            # 太短的不要
            if len(text) < MIN_LEN:
                continue

            chunks.append({
                "text": text,
                "source": filename,
            })

    return chunks


# ============================================================
# 主流程
# ============================================================

print("第 1 步：读笔记、切分……")
chunks = cut_into_chunks()
print(f"  切出 {len(chunks)} 块")

print()
print(f"第 2 步：转向量（分 {BATCH_SIZE} 段一批，可能要一会儿）……")

all_texts = [c["text"] for c in chunks]
all_vectors = []

# range(0, 总数, 每批大小) → 0, 20, 40, ...
for start in range(0, len(all_texts), BATCH_SIZE):

    # 切出一批（切片）
    batch = all_texts[start : start + BATCH_SIZE]

    # 转成向量，接到总表后面
    all_vectors.extend(embed_batch(batch))

    done = min(start + BATCH_SIZE, len(all_texts))
    print(f"  已完成 {done}/{len(all_texts)}")

print()
print(f"第 3 步：存进 {INDEX_FILE}……")

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(
        {"chunks": chunks, "vectors": all_vectors},
        f,
        ensure_ascii=False,
    )

size = os.path.getsize(INDEX_FILE) / 1024 / 1024
print(f"  完成，文件大小 {size:.1f} MB")
print()
print("以后直接用 ask_notes.py 提问就行，不用再跑这个脚本。")
