import requests
import os
import json
import re
import jieba

NOTES_DIR ="../../学习笔记"
INDEX_FILE = "index.json"
MIN_LEN = 50
BATCH_SIZE = 20

CODE_PATTERN = r"[a-zA-Z0-9_][a-zA-Z0-9_./\-]*"

with open("key_sf.txt", "r", encoding="utf-8")as f:
    sf_key = f.read().strip()

def cut_words(text):
    """分词：中文用 jieba，英文/代码整串保留"""
    codes = re.findall(CODE_PATTERN, text)
    rest = re.sub(CODE_PATTERN, " ", text)
    words = jieba.lcut(rest)
    words = [w for w in words if re.search(r"\w", w)]
    words.extend(codes)
    return words

def embed_batch(texts):
    """把一批文字转成向量，返回一批向量"""
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


def cut_into_chunks():
    """遍历笔记文件夹，按 ## 标题把每个 .md 切成小块"""
    chunks = []
    for filename in sorted(os.listdir(NOTES_DIR)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(NOTES_DIR,filename)
        with open(path, "r", encoding="utf-8")as f:
            content = f.read()

        parts = content.split("\n## ")
        for i, part in enumerate(parts):
            if i == 0:
                text = part
            else:
                text = "## " + part
            text == text.strip()
            if text.endswith("---"):
                text = text[:-3].strip()
            if len(text) < MIN_LEN:
                continue
            chunks.append({
                "text":text,
                "source":filename,
            })
    return chunks


def build_word_freq(chunks):
    """给所有块建词频表，供 BM25 用"""
    doc_words = []
    df = {}
    for chunk in chunks:
        words = cut_words(chunk["text"])
        doc_words.append(words)
        for word in set(words):
            df[word] = df.get(word, 0)+1
    avg_len = sum(len(w) for w in doc_words) / len(doc_words)
    return{
        "doc_words":doc_words,
        "df":df,
        "avg_len":avg_len,
    }


print("第 1 步：读笔记、切分……")
chunks = cut_into_chunks()
print(f"  切出 {len(chunks)} 块")
print()
print(f"第 2 步：转向量（每批 {BATCH_SIZE} 段）……")
all_texts = [c["text"] for c in chunks]
all_vectors = []

for start in range(0, len(all_texts),BATCH_SIZE):
    batch = all_texts[start : start + BATCH_SIZE]
    all_vectors.extend(embed_batch(batch))
    done = min(start + BATCH_SIZE, len(all_texts))
    print(f"  已完成 {done}/{len(all_texts)}")


print()
print("第 3 步：建词频表……")
bm25_data = build_word_freq(chunks)
print(f"  词表里 {len(bm25_data['df'])} 个不同的词")
print(f"  平均每块 {bm25_data['avg_len']:.0f} 个词")


print()
print(f"第 4 步：存进 {INDEX_FILE}……")
with open(INDEX_FILE, "w", encoding="utf-8")as f:
    json.dump({
        "chunks":chunks,
        "vectors":all_vectors,
        "bm25":bm25_data,
    },
    f,
    ensure_ascii=False,
    )

size = os.path.getsize(INDEX_FILE) / 1024 / 1024
print(f"  完成，文件大小 {size:.1f} MB")